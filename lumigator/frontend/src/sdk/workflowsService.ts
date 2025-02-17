import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
import type { CreateWorkflowPayload, Workflow, WorkflowResults } from '@/types/Workflow'

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

export const workflowsService = {
  createWorkflow,
  fetchLogs,
  fetchWorkflowResults,
  fetchWorkflowDetails,
}
