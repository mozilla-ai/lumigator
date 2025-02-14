import type { Bertscore, Meteor, Rouge } from "./Experiment"

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

export type WorkflowResults = {
  artifacts: Artifacts
  metrics: MetricsResult
  parameters: Parameters
}

export type Artifacts = {
  examples: string[]
  ground_truth: string[]
  model: string
  predictions: string[]
}

export type MetricsResult = {
  bertscore: Bertscore,
  meteor: Meteor,
  rouge: Rouge
}

export type Parameters = {
  dataset: {
    path: string
  }
  evaluation: {
    max_samples: number
  }
  metrics: string[]
  return_input_data: boolean
  return_predictions: boolean
  storage_path: string
  hf_pipeline: HfPipeline
  inference_server?: unknown
  name: string
  job: {
    enable_tqdm: boolean
    max_samples: number
    output_field: string
    storage_path: string
  }
  params: unknown
}

export type HfPipeline = {
  accelerator: string
  max_new_tokens: number
  model_uri: string
  revision: string
  task: string
  torch_dtype: string
  truncation: boolean
  trust_remote_code: boolean
  use_fast: boolean
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
