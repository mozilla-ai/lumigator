export type Workflow = {
  id: string
  experiment_id: string
  model: string
  name: string
  description: string
  status: WorkflowStatus
  created_at: string
  updated_at: string
  metrics?: Record<string, unknown>
  parameters?: Record<string, unknown>
  artifacts_download_url?: string
  jobs?: JobResult[]
}

export type JobResult = {
  id: string
  metrics?: Record<string, unknown>
  parameters?: Record<string, unknown>
  metric_url: string
  artifact_url: string
}

export enum WorkflowStatus {
  CREATED = 'created',
  RUNNING = 'running',
  FAILED = 'failed',
  SUCCEEDED = 'succeeded',

  // Added by frontend
  INCOMPLETE = 'incomplete',
  PENDING = 'pending',
}

export type CreateWorkflowPayload = {
  name: string
  description: string
  experiment_id: string
  model: string
  dataset: string
  max_samples: number
  model_url?: string
  system_prompt?: string
  inference_output_field?: string
  config_template?: string
}
