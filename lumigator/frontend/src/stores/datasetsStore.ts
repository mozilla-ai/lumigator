import { computed, ref, watch, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { datasetsService } from '@/sdk/datasetsService'

import { useToast } from 'primevue/usetoast'
import type { ToastMessageOptions } from 'primevue'
import type { Dataset } from '@/types/Dataset'
import { getAxiosError } from '@/helpers/getAxiosError'
import type { AxiosError } from 'axios'
import { downloadContent } from '@/helpers/downloadContent'
import { jobsService } from '@/sdk/jobsService'
import type { Job } from '@/types/Job'
import { retrieveEntrypoint } from '@/helpers/retrieveEntrypoint'
import type { EvaluationJobResults } from '@/types/Experiment'
import { WorkflowStatus } from '@/types/Workflow'
import { calculateDuration } from '@/helpers/calculateDuration'

export const useDatasetStore = defineStore('datasets', () => {
  const datasets: Ref<Dataset[]> = ref([])
  const selectedDataset: Ref<Dataset | undefined> = ref()
  const selectedJob: Ref<Job | undefined> = ref()
  const completedStatus = [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]

  const selectedJobResults: Ref<EvaluationJobResults[]> = ref([])
  const jobs: Ref<Job[]> = ref([])
  const inferenceJobs: Ref<Job[]> = ref([])
  const jobLogs: Ref<string[]> = ref([])
  const isPolling = ref(false)
  let jobLogsInterval: number | undefined = undefined

  const toast = useToast()

  async function fetchDatasets() {
    try {
      datasets.value = await datasetsService.fetchDatasets()
    } catch {
      datasets.value = []
    }
  }

  const hasRunningInferenceJob = computed(() => {
    return inferenceJobs.value.some((job) => job.status === WorkflowStatus.RUNNING)
  })

  /**
   * Loads all experiments and jobs.
   */
  async function fetchAllJobs() {
    let allJobs: Job[]
    try {
      allJobs = await jobsService.fetchJobs()
    } catch {
      allJobs = []
    }
    inferenceJobs.value = allJobs
      .filter((job) => job.metadata.job_type === 'inference')
      .map((job) => parseJob(job))
    jobs.value = allJobs
      .filter((job) => job.metadata.job_type === 'evaluate')
      .map((job) => parseJob(job))
  }

  /**
   *
   * @param {*} job - the job data to parse
   * @returns job data parsed for display as an experiment
   */
  function parseJob(job: Job) {
    return {
      ...job,
      entrypoint: undefined,
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

  async function fetchJob(id: string) {
    const jobData = await jobsService.fetchJob(id)
    selectedJob.value = parseJob(jobData)
  }

  async function retrieveJobLogs() {
    if (selectedJob.value) {
      const logsData = await jobsService.fetchLogs(selectedJob.value?.id)
      const logs = splitByEscapeCharacter(logsData.logs)
      logs.forEach((log: string) => {
        const lastEntry = jobLogs.value[jobLogs.value.length - 1]
        if (jobLogs.value.length === 0 || lastEntry !== log) {
          jobLogs.value.push(log)
        }
      })
    }
  }

  function startPolling() {
    jobLogs.value = []
    if (!isPolling.value) {
      isPolling.value = true
      retrieveJobLogs()
      // Poll every 3 seconds
      jobLogsInterval = setInterval(retrieveJobLogs, 3000)
    }
  }

  watch(
    selectedJob,
    (newValue) => {
      jobLogs.value = []
      if (newValue) {
        // const isEvaluationJob = jobs.value.some((job) => job?.id === newValue.id)
        // if (isEvaluationJob) {
        // switch to the experiment the job belongs
        // const selectedExperimentId = experiments.value.find(experiment => {
        //   return experiment.workflows.some(workflow => workflow.id === newValue.id)
        // })
        // selectedExperiment.value = experiments.value.find((exp) => exp.id === newValue.id)
        // }
        retrieveJobLogs()
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

  function stopPolling() {
    if (isPolling.value) {
      isPolling.value = false
      clearInterval(jobLogsInterval)
      jobLogsInterval = undefined
    }
  }

  function splitByEscapeCharacter(input: string) {
    const result = input.split('\n')
    return result
  }

  /**
   * Updates the status for stored experiments that are not completed
   */
  async function updateStatusForIncompleteJobs() {
    await Promise.all(getIncompleteJobIds().map((id) => updateJobStatus(id)))
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
    jobLogsInterval = setInterval(() => {
      updateJobStatus(jobId).then(() => {
        const job = jobs.value.find((job) => job.id === jobId)
        if (job && completedStatus.includes(job.status)) {
          stopPolling() // Stop polling when the job is complete
        }
      })
    }, 3000) // Poll every 3 seconds
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

  async function fetchDatasetDetails(datasetID: string) {
    try {
      selectedDataset.value = await datasetsService.fetchDatasetInfo(datasetID)
    } catch {
      selectedDataset.value = undefined
    }
  }

  function resetSelection() {
    selectedDataset.value = undefined
  }

  async function uploadDataset(datasetFile: File) {
    if (!datasetFile) {
      return
    }
    // Create a new FormData object and append the selected file and the required format
    const formData = new FormData()
    formData.append('dataset', datasetFile) // Attach the file
    formData.append('format', 'job') // Specification @localhost:8000/docs
    try {
      await datasetsService.postDataset(formData)
    } catch (error) {
      const errorMessage = getAxiosError(error as Error | AxiosError)
      toast.add({
        severity: 'error',
        summary: `${errorMessage}`,
        messageicon: 'pi pi-exclamation-triangle',
        group: 'br',
      } as ToastMessageOptions & { messageicon: string })
    }
    await fetchDatasets()
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

  async function deleteDataset(id: string) {
    if (!id) {
      return
    }
    if (selectedDataset.value?.id === id) {
      resetSelection()
    }
    await datasetsService.deleteDataset(id)
    await fetchDatasets()
  }

  // TODO: this shouldn't depend on refs/state, it can be a util function
  async function downloadDatasetFile() {
    if (selectedDataset.value) {
      const blob = await datasetsService.downloadDataset(selectedDataset.value?.id)
      downloadContent(blob, selectedDataset.value?.filename)
    }
  }

  return {
    datasets,
    fetchDatasets,
    selectedDataset,
    fetchDatasetDetails,
    jobLogs,
    resetSelection,
    uploadDataset,
    deleteDataset,
    downloadDatasetFile,
    jobs,
    inferenceJobs,
    selectedJob,
    selectedJobResults,
    hasRunningInferenceJob,
    fetchAllJobs,
    updateStatusForIncompleteJobs,
    fetchJob,
    // fetchJobResults,
    startGroundTruthGeneration,
    parseJob,
  }
})
