import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
import type { Experiment } from '@/types/Experiment'
import type { WorkflowResults } from '@/types/Metrics'
import type { Model } from '@/types/Model'

import type { CreateWorkflowPayload } from '@/types/Workflow'
import { workflowsService } from './workflowsService'

export async function fetchExperiments(): Promise<Experiment[]> {
  const response = await lumigatorApiAxiosInstance.get('/experiments')
  return response.data.items
}

export async function fetchExperiment(id: string): Promise<Experiment> {
  const response = await lumigatorApiAxiosInstance.get(`experiments/${id}`)
  return response.data
}

export async function deleteExperiment(id: string) {
  const response = await lumigatorApiAxiosInstance.delete(`experiments/${id}`)
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
  'experiment_id' | 'model' | 'provider'
>

export async function createExperiment(
  experimentPayload: CreateExperimentPayload,
): Promise<Experiment> {
  // first we create an experiment as a container for different workflows
  const response: { data: Experiment } = await lumigatorApiAxiosInstance.post(
    '/experiments',
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

/**
 * Runs an experiment with multiple models.
 * Each model triggers a respective evaluation job.
 *
 * @param {Object} experimentData - The data for the experiment to run.
 * @returns {Promise<Array>} The results of the experiment.
 */
export async function createExperimentWithWorkflows(
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
        model: model.model,
        provider: model.provider,
        base_url: model.base_url,
      }),
    ),
  )
}

export const experimentsService = {
  fetchExperiments,
  fetchExperiment,
  createExperimentWithWorkflows,
  fetchExperimentResults,
  downloadResults,
  createExperiment,
  deleteExperiment,
}
