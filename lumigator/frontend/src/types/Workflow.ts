export type Workflow = {
  id: string
  experiment_id: string
  model: string
  name: string
  description: string
  status: WorkflowStatus
  created_at: string
  updated_at: string
  metrics?: Metrics
  parameters?: Record<string, unknown>
  artifacts_download_url?: string
  jobs?: JobResult[]
}

export type JobResult = {
  id: string
  metrics?: Metrics
  parameters?: Record<string, unknown>
  metric_url: string
  artifact_url: string
}

export type Metrics = {
  meteor_mean: number
  rouge1_mean: number
  bertscore_precision_mean: number
  bertscore_f1_mean: number
  bertscore_recall_mean: number
  rougeL_mean: number
  rougeLsum_mean: number
  rouge2_mean: number
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
