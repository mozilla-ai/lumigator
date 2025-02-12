import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
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

export const workflowsService = {
  createWorkflow,
  fetchLogs,
}
