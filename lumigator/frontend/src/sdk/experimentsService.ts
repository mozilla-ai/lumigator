import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
import type { Dataset } from '@/types/Dataset'
import type { Job, ObjectData } from '@/types/Experiment'
import type { ExperimentNew } from '@/types/ExperimentNew'

export async function fetchExperiments(): Promise<ExperimentNew[]> {
  const response = await lumigatorApiAxiosInstance.get('/experiments/new/all')
  return response.data.items
}

export async function fetchExperiment(id: string): Promise<ExperimentNew> {
  const response = await lumigatorApiAxiosInstance.get(`experiments/new/${id}`)
  return response.data
}

export async function deleteExperiment(id: string) {
  const response = await lumigatorApiAxiosInstance.delete(`experiments/new/${id}`)
  return response.data
}

export type ExperimentPayload = {
  name: string
  description: string
  model?: string
  dataset: string
  max_samples: number
  model_url?: string
  system_prompt?: string
  inference_output_field?: string
  config_template?: string
}

export async function createExperiment(
  experimentPayload: ExperimentPayload,
): Promise<ExperimentNew> {
  // first we create an experiment as a container for different workflows
  const response: { data: ExperimentNew } = await lumigatorApiAxiosInstance.post(
    'experiments/new',
    experimentPayload,
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
  const response = await lumigatorApiAxiosInstance.get(`experiments/${job_id}/result/download`)
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
  const response = await lumigatorApiAxiosInstance.get(
    `experiments/${experiment_id}/result/download`,
  )
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

export const experimentsService = {
  fetchExperiments,
  fetchExperiment,
  // triggerExperiment,
  fetchExperimentResults,
  downloadResults,
  createExperiment,
}
