import type { Bertscore, Meteor, Rouge } from './Metrics'
import type { Workflow, WorkflowStatus } from './Workflow'

export type Experiment = {
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

export type ExperimentResults = {
  model: string
  meteor: Meteor
  bertscore: Bertscore
  rouge: Rouge
  runTime: string | undefined
  jobResults: EvaluationJobResults[]
}

export type EvaluationJobResults = {
  example: string
  bertscore: Bertscore
  evaluation_time: number
  ground_truth?: string
  meteor: Meteor
  model: string
  predictions?: string
  rouge: Rouge
  inference_time: number
}
