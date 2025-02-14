import { ref, watch, type Ref } from 'vue'
import { defineStore } from 'pinia'
import {
  experimentsService,
  type createExperimentWithWorkflowsPayload,
} from '@/sdk/experimentsService'

import type { EvaluationJobResults, ExperimentResults } from '@/types/Experiment'
import { downloadContent } from '@/helpers/downloadContent'
import type { Model } from '@/types/Model'
import { workflowsService } from '@/sdk/workflowsService'
import type { ExperimentNew } from '@/types/ExperimentNew'
import { WorkflowStatus, type Workflow, type WorkflowResults } from '@/types/Workflow'
import { jobsService } from '@/sdk/jobsService'
import axios from 'axios'

export const useExperimentStore = defineStore('experiments', () => {
  const experiments: Ref<ExperimentNew[]> = ref([])

  const selectedExperiment: Ref<ExperimentNew | undefined> = ref()
  const selectedWorkflow: Ref<Workflow | undefined> = ref()
  const selectedWorkflowResults: Ref<EvaluationJobResults[] | undefined> = ref()

  const selectedExperimentResults: Ref<ExperimentResults[]> = ref([])

  const isPolling = ref(false)
  let experimentInterval: number | undefined = undefined
  const workflowLogs: Ref<string[]> = ref([])
  const completedStatus = [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]

  async function fetchAllExperiments() {
    experiments.value = await experimentsService.fetchExperiments()
  }

  /**
   * The retrieved IDs will determine which experiment is still Running
   * @returns {string[]} IDs of stored experiments that have not completed
   */
  function getIncompleteExperimentIds() {
    return experiments.value
      .filter((experiment) => !completedStatus.includes(experiment.status))
      .map((experiment) => experiment.id)
  }

  /**
   *
   * @param {string} id - String (UUID) representing the experiment which should be updated with the latest status
   */
  async function updateExperimentStatus(id: string) {
    try {
      const status = await jobsService.fetchJobStatus(id)
      const experiment = experiments.value.find((experiment) => experiment.id === id)
      if (experiment) {
        experiment.status = status
      }
    } catch (error) {
      console.error(`Failed to update status for job ${id} ${error}`)
    }
  }

  /**
   * Updates the status for stored experiments that are not completed
   */
  async function updateStatusForIncompleteExperiments() {
    await Promise.all(getIncompleteExperimentIds().map((id) => updateExperimentStatus(id)))
  }

  /**
   * Runs an experiment with multiple models.
   * Each model triggers a respective evaluation job.
   *
   * @param {Object} experimentData - The data for the experiment to run.
   * @returns {Promise<Array>} The results of the experiment.
   */
  async function createExperimentWithWorkflows(
    experimentData: createExperimentWithWorkflowsPayload,
    models: Model[],
  ) {
    // first we create an experiment as a container
    const { id: experimentId } = await experimentsService.createExperiment(experimentData)

    // then we create a workflow for each model to be attached to the experiment
    return Promise.all(
      models.map((model: Model) =>
        workflowsService.createWorkflow({
          ...experimentData,
          experiment_id: experimentId,
          model: model.uri,
        }),
      ),
    )
  }

  function loadExperimentDetails(id: string) {
    selectedExperiment.value = experiments.value.find((experiment) => experiment.id === id)
  }

  async function fetchExperimentResultsFile(jobId: string) {
    const blob = await experimentsService.downloadResults(jobId)
    downloadContent(blob, `${selectedWorkflow.value?.name}_results`)
  }

  async function fetchExperimentResults(experiment: ExperimentNew) {
    for (const workflow of experiment.workflows) {
      //   console.log({experiment, workflow})
      if (workflow.artifacts_download_url) {
        const { data }: { data: WorkflowResults } = await axios.get(workflow.artifacts_download_url)
        console.log(data)

        const modelRow = {
          model: data.artifacts.model,
          meteor: data.metrics.meteor,
          bertscore: data.metrics.bertscore,
          rouge: data.metrics.rouge,
          runTime: undefined, //getJobRuntime(results.id),
          jobResults: transformJobResults(data),
        }
        selectedExperimentResults.value.push(modelRow)
      }
    }
  }

  // async function fetchJobResults(jobId: string) {
  //   const results = (await experimentsService.fetchExperimentResults(jobId)) as {
  //     resultsData: WorkflowResults
  //     id: string
  //     download_url: string
  //   }
  //   if (results?.id) {
  //     selectedJob.value = jobs.value.find((job) => job.id === results.id)
  //     selectedJobResults.value = transformJobResults(results.resultsData)
  //   }
  // }
  async function fetchWorkflowResults(workflow: Workflow) {
    const results = await workflowsService.fetchWorkflowResults(workflow)
    if (results) {
      selectedWorkflow.value = workflow
      selectedWorkflowResults.value = transformJobResults(
        results,
      )
    }
  }

  /**
   * Transforms results data into a format which accommodates the UI
   *
   * @param {Object} objectData .
   * @returns {Array} Transformed results array.
   */
  function transformJobResults(objectData: WorkflowResults): EvaluationJobResults[] {
    const transformedArray = objectData.artifacts.examples.map((example, index: number) => {
      return {
        example,
        bertscore: {
          f1: objectData.metrics.bertscore?.f1?.[index] ?? 0,
          f1_mean: objectData.metrics.bertscore?.f1_mean ?? 0,
          hashcode: objectData.metrics.bertscore?.hashcode ?? 0,
          precision: objectData.metrics.bertscore?.precision?.[index] ?? 0,
          precision_mean: objectData.metrics.bertscore?.precision_mean ?? 0,
          recall: objectData.metrics.bertscore?.recall?.[index] ?? 0,
          recall_mean: objectData.metrics.bertscore?.recall_mean ?? 0,
        },
        evaluation_time: objectData.artifacts.evaluation_time ?? 0,
        ground_truth: objectData.artifacts.ground_truth?.[index],
        meteor: {
          meteor: objectData.metrics.meteor?.meteor?.[index] ?? 0,
          meteor_mean: objectData.metrics.meteor?.meteor_mean ?? 0,
        },
        model: objectData.artifacts.model,
        predictions: objectData.artifacts.predictions?.[index],
        rouge: {
          rouge1: objectData.metrics.rouge?.rouge1?.[index] ?? 0,
          rouge1_mean: objectData.metrics.rouge?.rouge1_mean ?? 0,
          rouge2: objectData.metrics.rouge?.rouge2?.[index] ?? 0,
          rouge2_mean: objectData.metrics.rouge?.rouge2_mean ?? 0,
          rougeL: objectData.metrics.rouge?.rougeL?.[index] ?? 0,
          rougeL_mean: objectData.metrics.rouge?.rougeL_mean ?? 0,
          rougeLsum: objectData.metrics.rouge?.rougeLsum?.[index] ?? 0,
          rougeLsum_mean: objectData.metrics.rouge?.rougeLsum_mean ?? 0,
        },
        summarization_time: objectData.artifacts.summarization_time,
      } as unknown as EvaluationJobResults
    })
    return transformedArray
  }

  async function retrieveWorkflowLogs() {
    if (selectedWorkflow.value) {
      const logsData = await workflowsService.fetchLogs(selectedWorkflow.value?.id)
      const logs = splitByEscapeCharacter(logsData.logs)
      console.log({ logs })
      logs.forEach((log: string) => {
        const lastEntry = workflowLogs.value[workflowLogs.value.length - 1]
        if (workflowLogs.value.length === 0 || lastEntry !== log) {
          workflowLogs.value.push(log)
        }
      })
    }
  }

  function splitByEscapeCharacter(input: string) {
    const result = input.split('\n')
    return result
  }

  function startPollingForWorkflowLogs() {
    workflowLogs.value = []
    if (!isPolling.value) {
      isPolling.value = true
      retrieveWorkflowLogs()
      // Poll every 3 seconds
      experimentInterval = setInterval(retrieveWorkflowLogs, 3000)
    }
  }

  function stopPollingForWorkflowLogs() {
    if (isPolling.value) {
      isPolling.value = false
      clearInterval(experimentInterval)
      experimentInterval = undefined
    }
  }

  // function getJobRuntime(jobId: string) {
  //   const job = jobs.value.find((job) => job.id === jobId)
  //   return job ? job.runTime : undefined
  // }

  watch(
    selectedExperiment,
    (newValue) => {
      if (newValue?.workflows.some((workflow) => workflow.status === WorkflowStatus.RUNNING)) {
        startPollingForWorkflowLogs()
        return
      } else if (isPolling.value) {
        stopPollingForWorkflowLogs()
      }
    },
    { deep: true },
  )

  watch(
    selectedWorkflow,
    (newValue) => {
      workflowLogs.value = []
      if (newValue) {
        // switch to the experiment the job belongs
        const found = experiments.value.find((experiment) => {
          return experiment.workflows.some((workflow) => workflow.id === newValue.id)
        })
        selectedExperiment.value = found

        retrieveWorkflowLogs()
      }
      if (newValue?.status === WorkflowStatus.RUNNING) {
        startPollingForWorkflowLogs()
        return
      } else if (isPolling.value) {
        stopPollingForWorkflowLogs()
      }
    },
    { deep: true },
  )

  return {
    // state
    experiments,
    selectedExperiment,
    workflowLogs,
    selectedExperimentResults,
    selectedWorkflow,
    selectedWorkflowResults,
    isPolling,
    // computed
    // actions
    loadExperimentDetails,
    fetchExperimentResults,
    fetchExperimentResultsFile,
    createExperimentWithWorkflows,
    fetchAllExperiments,
    updateStatusForIncompleteExperiments,
    fetchWorkflowResults,
  }
})
