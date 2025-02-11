import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
import type { Workflow } from '@/types/Workflow'

type ExperimentPayload = {
  name: string
  description: string
  model: string
  dataset: string
  experiment_id: string
  max_samples: number
}

async function createWorkflow(experimentPayload: ExperimentPayload): Promise<Workflow> {
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
