import { lumigatorApiAxiosInstance } from '@/helpers/lumigator-axios-instance'
import type { Job, ObjectData } from '@/types/Experiment'

export const PATH_JOBS_ROOT = () => `jobs/`
export const PATH_JOB_DETAILS = (experiment_id: string) => `jobs/${experiment_id}`
export const PATH_EXPERIMENT_LOGS = (id: string) => `jobs/${id}/logs`
export const PATH_EXPERIMENT_RESULTS = (job_id: string) => `experiments/${job_id}/result/download`
export const PATH_EXPERIMENTS_EVALUATE = () => `experiments`
export const PATHS_EXPERIMENTS_ANNOTATE = () => 'jobs/annotate/'

/**
 *
 * @returns {array} of all jobs, regardless the experiment
 */
export async function fetchJobs(): Promise<Job[]> {
  const response = await lumigatorApiAxiosInstance.get(PATH_JOBS_ROOT())
  return response.data.items.map((job: Job) => ({
    ...job,
    status: job.status.toUpperCase(),
  }))
}

/**
 * Fetches details of a specific job by ID.
 * @param {string} id - The ID of the job.
 */
export async function fetchJobDetails(id: string) {
  const response = await lumigatorApiAxiosInstance.get(PATH_JOB_DETAILS(id))
  if (response.data?.status) {
    // Ensure that we transform status at the point the API returns it.
    response.data.status = response.data.status.toUpperCase()
  }
  return response.data
}

export async function fetchJobStatus(id: string) {
  const job = await fetchJobDetails(id)
  return job?.status
}

/**
 * Triggers a new experiment with the given payload, due API limitations at the time.
 * In fact this funcition triggers an evaluation job.
 * @param {Object} experimentPayload - The payload for the experiment.
 *  The schema of experimentPayload can be found @ api/v1/experiments/
 */
// TODO: For experiments with multiple models this function is called recursively for every model selected from the form.
// Check ExperimentForm.vue
export async function triggerExperiment(experimentPayload: unknown) {
  const response = await lumigatorApiAxiosInstance.post(
    PATH_EXPERIMENTS_EVALUATE(),
    experimentPayload,
    {
      headers: {
        'Content-Type': 'application/json',
      },
    },
  )
  return response.data
}

export async function triggerAnnotationJob(groundTruthPayload: unknown) {
  const response = await lumigatorApiAxiosInstance.post(
    PATHS_EXPERIMENTS_ANNOTATE(),
    groundTruthPayload,
    {
      headers: {
        'Content-Type': 'application/json',
      },
    },
  )
  return response.data
}

/**
 * Fetches the results of a specific job.
 * @param {string} job_id
 */
export async function fetchExperimentResults(
  job_id: string,
): Promise<unknown | { resultsData: ObjectData; id: string; download_url: string }> {
  const response = await lumigatorApiAxiosInstance.get(PATH_EXPERIMENT_RESULTS(job_id))
  const { download_url, id } = response.data
  if (!download_url) {
    console.error('No download_url found in the response.')
    return
  }
  const jsonData = await lumigatorApiAxiosInstance.get(download_url)
  return {
    resultsData: jsonData.data,
    id,
    download_url,
  }
}

/**
 * Downloads the results of a specific experiment by ID.
 * @param {string} experiment_id .
 * @returns {Promise<Blob|Error>} A promise that resolves to a Blob containing the file data.
 */
export async function downloadResults(experiment_id: string) {
  const response = await lumigatorApiAxiosInstance.get(PATH_EXPERIMENT_RESULTS(experiment_id))
  const { download_url } = response.data
  if (!download_url) {
    console.error('No download_url found in the response.')
    return
  }
  const fileResponse = await lumigatorApiAxiosInstance.get(download_url, {
    responseType: 'blob', // Important: Receive the file as a binary blob
  })
  const blob = fileResponse.data
  return blob
}

/**
 * Fetches the logs of a specific job by ID.
 * @param {string} id .
 */
export async function fetchLogs(id: string) {
  const logsResponse = await lumigatorApiAxiosInstance.get(PATH_EXPERIMENT_LOGS(id))
  return logsResponse.data
}

export const experimentsService = {
  fetchJobs,
  fetchJobDetails,
  fetchJobStatus,
  triggerExperiment,
  fetchExperimentResults,
  downloadResults,
  fetchLogs,
  triggerAnnotationJob,
}
