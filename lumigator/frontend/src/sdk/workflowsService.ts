import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
import type { WorkflowResults } from '@/types/Metrics'
import type { CreateWorkflowPayload, Workflow } from '@/types/Workflow'

async function createWorkflow(experimentPayload: CreateWorkflowPayload): Promise<Workflow> {
  const response = await lumigatorApiAxiosInstance.post('workflows', experimentPayload, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
  return response.data
}

/**
 * Fetches the logs of a specific job by ID.
 * @param {string} id .
 */
export async function fetchLogs(id: string) {
  const logsResponse = await lumigatorApiAxiosInstance.get(`workflows/${id}/logs`)
  return logsResponse.data
}

export async function fetchWorkflowResults(workflow: Workflow): Promise<WorkflowResults> {
  const response = await lumigatorApiAxiosInstance.get(workflow.artifacts_download_url!)
  return response.data
}

export async function fetchWorkflowDetails(id: string): Promise<Workflow> {
  const response = await lumigatorApiAxiosInstance.get(`workflows/${id}`)
  return response.data
}

export async function deleteWorkflow(id: string) {
  const response = await lumigatorApiAxiosInstance.delete(`workflows/${id}`)
  return response.data
}

/**
 * Downloads the results of a specific workflow by ID.
 * @param {string} workflow_id .
 * @returns {Promise<Blob|Error>} A promise that resolves to a Blob containing the file data.
 */
export async function downloadResults(workflow_id: string) {
  const response = await lumigatorApiAxiosInstance.get(
    `workflows/${workflow_id}/result/download`,
  )
  if (!response.data) {
    console.error('No URL found in the response.')
    return
  }
  const fileResponse = await lumigatorApiAxiosInstance.get(response.data, {
    responseType: 'blob', // Important: Receive the file as a binary blob
  })
  const blob = fileResponse.data
  return blob
}


export const workflowsService = {
  createWorkflow,
  fetchLogs,
  fetchWorkflowResults,
  fetchWorkflowDetails,
  deleteWorkflow,
  downloadResults,
}
