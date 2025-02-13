import type { Workflow, WorkflowStatus } from './Workflow'

export type ExperimentNew = {
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
  workflows: Workflow[]
  task: 'summarization'
  dataset: string
  max_samples: number

  // added by the frontend, TODO: refactor
  status: WorkflowStatus
}
