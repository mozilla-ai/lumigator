import { computed, ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { datasetsService } from '@/sdk/datasetsService'

import type { Dataset } from '@/types/Dataset'
import { jobsService } from '@/sdk/jobsService'
import type { Job } from '@/types/Job'
import { retrieveEntrypoint } from '@/helpers/retrieveEntrypoint'
import { WorkflowStatus } from '@/types/Workflow'
import { calculateDuration } from '@/helpers/calculateDuration'

export const useDatasetStore = defineStore('datasets', () => {
  const datasets: Ref<Dataset[]> = ref([])
  const selectedDataset: Ref<Dataset | undefined> = ref()

  const completedStatus = [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]

  const jobs: Ref<Job[]> = ref([])
  const inferenceJobs: Ref<Job[]> = ref([])

  const isPollingForJobStatus = ref(false)
  let jobStatusInterval: number | undefined = undefined

  async function fetchDatasets() {
    try {
      datasets.value = await datasetsService.fetchDatasets()
    } catch {
      datasets.value = []
    }
  }

  const setSelectedDataset = (dataset: Dataset | undefined): void => {
    selectedDataset.value = dataset
  }

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
      // NOTE: 'temporary fix' to prevent showing inference jobs that weren't created by the UI
      // to generate ground truth.
      .filter((job) => job.name.startsWith("Ground truth for "))
      .map((job) => parseJob(job))
  }

  const hasRunningInferenceJob = computed(() => {
    return inferenceJobs.value.some((job) => job.status === WorkflowStatus.RUNNING)
  })

  /**
   * TODO: move to a helper file, this shouldn't be in the store
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

  /* TODO: Move all below functions into `Datasets` component where the state can be shared across InferenceJobsTable and DatasetDetails */
  /**
   * The retrieved IDs will determine which experiment is still Running
   * @returns {string[]} IDs of stored experiments that have not completed
   */
  function getIncompleteJobIds() {
    return inferenceJobs.value
      .filter((job) => !completedStatus.includes(job.status))
      .map((job) => job.id)
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
        startPollingForAnnotationJobStatus(jobResponse.id) // Add polling for ground truth job
        return jobResponse
      }
      return
    } catch (error) {
      console.error('Failed to start ground truth generation:', error)
      return
    }
  }

  function startPollingForAnnotationJobStatus(jobId: string) {
    isPollingForJobStatus.value = true
    jobStatusInterval = setInterval(async () => {
      await updateJobStatus(jobId).then(() => {
        const job = inferenceJobs.value.find((job) => job.id === jobId)
        if (job && completedStatus.includes(job.status)) {
          stopPollingForAnnotationJobStatus() // Stop polling when the job is complete
        }
      })
    }, 3000) // Poll every 3 seconds
  }

  function stopPollingForAnnotationJobStatus() {
    if (isPollingForJobStatus.value) {
      isPollingForJobStatus.value = false
      clearInterval(jobStatusInterval)
      jobStatusInterval = undefined
    }
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
      const job = inferenceJobs.value.find((job) => job.id === id)
      if (job) {
        job.status = status
      }
    } catch (error) {
      console.error(`Failed to update status for job ${id} ${error}`)
    }
  }

  return {
    datasets,
    selectedDataset,
    jobs,
    inferenceJobs,
    hasRunningInferenceJob,
    fetchDatasets,
    setSelectedDataset,
    fetchAllJobs,
    updateStatusForIncompleteJobs,
    stopPollingForAnnotationJobStatus,
    startGroundTruthGeneration,
    parseJob,
  }
})
