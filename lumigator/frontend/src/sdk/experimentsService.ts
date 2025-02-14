import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'

import type { ExperimentNew } from '@/types/ExperimentNew'
import type { CreateWorkflowPayload, WorkflowResults } from '@/types/Workflow'

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

export type CreateExperimentPayload = {
  name: string
  description: string
  task: 'summarization'
}

// experiment_id and model are set by the inner function
export type createExperimentWithWorkflowsPayload = Omit<
  CreateExperimentPayload & CreateWorkflowPayload,
  'experiment_id' | 'model'
>

export async function createExperiment(
  experimentPayload: CreateExperimentPayload,
): Promise<ExperimentNew> {
  // first we create an experiment as a container for different workflows
  const response: { data: ExperimentNew } = await lumigatorApiAxiosInstance.post(
    'experiments/new',
    experimentPayload,
  )

  return response.data
}

export async function fetchExperimentResults(
  experimentId: string,
): Promise<unknown | { resultsData: WorkflowResults; id: string; download_url: string }> {
  const response = await lumigatorApiAxiosInstance.get(
    `experiments/${experimentId}/result/download`,
  )
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
