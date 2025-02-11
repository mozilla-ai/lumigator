import type { Workflow, WorkflowStatus } from './Workflow'

export type ExperimentNew = {
  id: string
  name: string
  description: string
  created_at: string
  workflows: Workflow[]

  // added by the frontend, TODO: refactor
  status: WorkflowStatus
}
