import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
import type { Dataset } from '@/types/Dataset'
import type { Job } from '@/types/Experiment'

/**
 * Fetches the logs of a specific job by ID.
 * @param {string} id .
 */
export async function fetchLogs(id: string) {
  const logsResponse = await lumigatorApiAxiosInstance.get(`jobs/${id}/logs`)
  return logsResponse.data
}

/**
 *
 * @returns {array} of all jobs, regardless the experiment
 */
export async function fetchJobs(): Promise<Job[]> {
  const response = await lumigatorApiAxiosInstance.get('/jobs')
  return response.data.items
}

/**
 * Fetches details of a specific job by ID.
 * @param {string} id - The ID of the job.
 */
export async function fetchJobDetails(id: string) {
  const response = await lumigatorApiAxiosInstance.get(`jobs/${id}`)
  return response.data
}

export async function fetchJobStatus(id: string) {
  const job = await fetchJobDetails(id)
  return job?.status
}

/*
  An annotation job is a special type of inference job used to generate ground truth for a dataset
*/
export async function triggerAnnotationJob(dataset: Dataset) {
  const groundTruthPayload = {
    name: `Ground truth for ${dataset.filename}`,
    description: `Ground truth generation for dataset ${dataset.id}`,
    dataset: dataset.id,
    max_samples: -1,
    task: 'summarization',
    job_config: {
      job_type: 'annotate',
    },
  }

  const response = await lumigatorApiAxiosInstance.post('jobs/annotate/', groundTruthPayload)
  return response.data
}

export const jobsService = {
  fetchLogs,
  fetchJobs,
  fetchJobDetails,
  fetchJobStatus,
  triggerAnnotationJob,
}
