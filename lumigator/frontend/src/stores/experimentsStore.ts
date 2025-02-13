import { ref, watch, computed, type Ref } from 'vue'
import { defineStore } from 'pinia'
import {
  experimentsService,
  type createExperimentWithWorkflowsPayload,
} from '@/sdk/experimentsService'

import type { EvaluationJobResults, ExperimentResults, ObjectData } from '@/types/Experiment'
import { retrieveEntrypoint } from '@/helpers/retrieveEntrypoint'
import { downloadContent } from '@/helpers/downloadContent'
import type { Dataset } from '@/types/Dataset'
import type { Model } from '@/types/Model'
import { workflowsService } from '@/sdk/workflowsService'
import type { ExperimentNew } from '@/types/ExperimentNew'
import { WorkflowStatus } from '@/types/Workflow'
import { jobsService } from '@/sdk/jobsService'
import { calculateDuration } from '@/helpers/calculateDuration'
import type { JobDetails } from '@/types/JobDetails'

export const useExperimentStore = defineStore('experiments', () => {
  const experiments: Ref<ExperimentNew[]> = ref([])

  const jobs: Ref<JobDetails[]> = ref([])
  const inferenceJobs: Ref<ExperimentNew[]> = ref([])

  const selectedExperiment: Ref<ExperimentNew | undefined> = ref()
  const selectedJob: Ref<JobDetails | undefined> = ref()

  const selectedJobResults: Ref<EvaluationJobResults[]> = ref([])
  const selectedExperimentResults: Ref<ExperimentResults[]> = ref([])

  const isPolling = ref(false)
  let experimentInterval: number | undefined = undefined
  const experimentLogs: Ref<unknown[]> = ref([])
  const completedStatus = [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]

  const hasRunningInferenceJob = computed(() => {
    return inferenceJobs.value.some((job) => job.status === WorkflowStatus.RUNNING)
  })

  /**
   * Loads all experiments and jobs.
   */
  async function fetchAllJobs() {
    let allJobs: JobDetails[]
    try {
      allJobs = await jobsService.fetchJobs()
    } catch {
      allJobs = []
    }
    inferenceJobs.value = allJobs
      .filter((job) => job.metadata.job_type === 'inference')
      .map((job) => parseJobDetails(job))
    jobs.value = allJobs
      .filter((job) => job.metadata.job_type === 'evaluate')
      .map((job) => parseJobDetails(job))

    experiments.value = await experimentsService.fetchExperiments()
  }

  /**
   *
   * @param {*} job - the job data to parse
   * @returns job data parsed for display as an experiment
   */
  function parseJobDetails(job: JobDetails) {
    const { entrypoint: _entrypoint, ...rest} = job
    return {
      ...rest,
      ...retrieveEntrypoint(job),
      runTime: job.end_time ? calculateDuration(job.start_time, job.end_time) : undefined,
    }
  }

  /**
   * The retrieved IDs will determine which experiment is still Running
   * @returns {string[]} IDs of stored experiments that have not completed
   */
  function getIncompleteJobIds() {
    return jobs.value.filter((job) => !completedStatus.includes(job.status)).map((job) => job.id)
  }

  /**
   *
   * @param {string} id - String (UUID) representing the experiment which should be updated with the latest status
   */
  // TODO: Refactor for each kind of job OR gather all jobs into one array for internal use
  async function updateJobStatus(id: string) {
    try {
      const status = await jobsService.fetchJobStatus(id)
      const inferenceJob = inferenceJobs.value.find((job) => job.id === id)
      if (inferenceJob) {
        inferenceJob.status = status
      }
      const job = jobs.value.find((job) => job.id === id)
      if (job) {
        job.status = status
      }
    } catch (error) {
      console.error(`Failed to update status for job ${id} ${error}`)
    }
  }

  /**
   * Updates the status for stored experiments that are not completed
   */
  async function updateStatusForIncompleteJobs() {
    await Promise.all(getIncompleteJobIds().map((id) => updateJobStatus(id)))
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

  async function fetchJobDetails(id: string) {
    const jobData = await jobsService.fetchJobDetails(id)
    selectedJob.value = parseJobDetails(jobData)
  }

  async function fetchExperimentResultsFile(jobId: string) {
    const blob = await experimentsService.downloadResults(jobId)
    downloadContent(blob, `${selectedJob.value?.name}_results`)
  }

  async function fetchExperimentResults(experiment: ExperimentNew) {
    for (const workflow of experiment.workflows) {
      const results = (await experimentsService.fetchExperimentResults(workflow.id)) as {
        resultsData: ObjectData
        id: string
        download_url: string
      }
      if (results?.id) {
        const modelRow = {
          model: results.resultsData.artifacts.model,
          meteor: results.resultsData.metrics.meteor,
          bertscore: results.resultsData.metrics.bertscore,
          rouge: results.resultsData.metrics.rouge,
          // runTime: getJobRuntime(results.id),
          jobResults: transformJobResults(results.resultsData),
        } as unknown as ExperimentResults
        selectedExperimentResults.value.push(modelRow)
      }
    }
  }

  async function fetchJobResults(jobId: string) {
    const results = (await experimentsService.fetchExperimentResults(jobId)) as {
      resultsData: ObjectData
      id: string
      download_url: string
    }
    if (results?.id) {
      selectedJob.value = jobs.value.find((job) => job.id === results.id)
      selectedJobResults.value = transformJobResults(results.resultsData)
    }
  }

  /**
   * Transforms results data into a format which accommodates the UI
   *
   * @param {Object} objectData .
   * @returns {Array} Transformed results array.
   */
  function transformJobResults(objectData: ObjectData): EvaluationJobResults[] {
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
        evaluation_time: objectData.metrics.evaluation_time ?? 0,
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
        summarization_time: objectData.metrics.summarization_time,
      } as unknown as EvaluationJobResults
    })
    return transformedArray
  }

  async function retrieveLogs() {
    if (selectedJob.value) {
      const logsData = await jobsService.fetchLogs(selectedJob.value?.id)
      const logs = splitByEscapeCharacter(logsData.logs)
      logs.forEach((log: string) => {
        const lastEntry = experimentLogs.value[experimentLogs.value.length - 1]
        if (experimentLogs.value.length === 0 || lastEntry !== log) {
          experimentLogs.value.push(log)
        }
      })
    }
  }

  function splitByEscapeCharacter(input: string) {
    const result = input.split('\n')
    return result
  }

  function startPolling() {
    experimentLogs.value = []
    if (!isPolling.value) {
      isPolling.value = true
      retrieveLogs()
      // Poll every 3 seconds
      experimentInterval = setInterval(retrieveLogs, 3000)
    }
  }

  function stopPolling() {
    if (isPolling.value) {
      isPolling.value = false
      clearInterval(experimentInterval)
      experimentInterval = undefined
    }
  }

  /**
   * Starts ground truth generation aka an inference job.
   *
   * @param {Object} groundTruthPayload - The payload for ground truth generation.
   * @returns {Promise<Object|null>} The response from the annotation job or null if it fails.
   */
  async function startGroundTruthGeneration(dataset: Dataset) {
    try {
      const jobResponse = await jobsService.triggerAnnotationJob(dataset)
      if (jobResponse) {
        // Start polling to monitor the job status
        await updateJobStatus(jobResponse.id) // Ensure initial update
        startPollingForAnnotationJob(jobResponse.id) // Add polling for ground truth job
        return jobResponse
      }
      return
    } catch (error) {
      console.error('Failed to start ground truth generation:', error)
      return
    }
  }

  function startPollingForAnnotationJob(jobId: string) {
    isPolling.value = true
    experimentInterval = setInterval(() => {
      updateJobStatus(jobId).then(() => {
        const job = jobs.value.find((job) => job.id === jobId)
        if (job && completedStatus.includes(job.status)) {
          stopPolling() // Stop polling when the job is complete
        }
      })
    }, 3000) // Poll every 3 seconds
  }

  // function getJobRuntime(jobId: string) {
  //   const job = jobs.value.find((job) => job.id === jobId)
  //   return job ? job.runTime : undefined
  // }

  watch(
    selectedExperiment,
    (newValue) => {
      if (newValue?.workflows.some((workflow) => workflow.status === WorkflowStatus.RUNNING)) {
        // startPolling()
        return
      } else if (isPolling.value) {
        stopPolling()
      }
    },
    { deep: true },
  )

  watch(
    selectedJob,
    (newValue) => {
      experimentLogs.value = []
      if (newValue) {
        // const isEvaluationJob = jobs.value.some((job) => job?.id === newValue.id)
        // if (isEvaluationJob) {
        // switch to the experiment the job belongs
        // const selectedExperimentId = experiments.value.find(experiment => {
        //   return experiment.workflows.some(workflow => workflow.id === newValue.id)
        // })
        selectedExperiment.value = experiments.value.find((exp) => exp.id === newValue.id)
        // }
        retrieveLogs()
      }
      if (newValue?.status === WorkflowStatus.RUNNING) {
        startPolling()
        return
      } else if (isPolling.value) {
        stopPolling()
      }
    },
    { deep: true },
  )

  return {
    // state
    experiments,
    jobs,
    inferenceJobs,
    selectedExperiment,
    selectedJob,
    experimentLogs,
    selectedExperimentResults,
    selectedJobResults,
    isPolling,
    // computed
    hasRunningInferenceJob,
    // actions
    fetchAllJobs,
    updateStatusForIncompleteJobs,
    loadExperimentDetails,
    fetchJobDetails,
    fetchExperimentResults,
    fetchJobResults,
    fetchExperimentResultsFile,
    startGroundTruthGeneration,
    createExperimentWithWorkflows,
  }
})
