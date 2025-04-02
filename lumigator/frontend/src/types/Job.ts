export enum JobStatus {
  CREATED = 'created',
  PENDING = 'pending',
  RUNNING = 'running',
  FAILED = 'failed',
  SUCCEEDED = 'succeeded',
  STOPPED = 'stopped',
  UNRECOVERABLE = 'unrecoverable',
}

export type Job = {
  type: string
  submission_id: string
  driver_info?: unknown
  status: JobStatus
  config: {
    name: string
    max_samples: number
    model_name_or_path?: string
    system_prompt: string
    dataset: {
      id: string
      name: string
    }
    hf_pipeline: {
      model_name_or_path: string
      revision: string
      use_fast: boolean
      trust_remote_code: boolean
      torch_dtype: string
      accelerator: string
      truncation: boolean
      task: string
    }
    generation_config: {
      max_new_tokens: number
      frequency_penalty: number
      temperature: number
      top_p: number
    }
  }
  message: string
  error_type?: unknown
  start_time: string
  end_time: string
  metadata: {
    job_type: string
  }
  runtime_env: {
    working_dir: string
    pip: {
      packages: string[]
      pip_check: boolean
    }
    env_vars: Record<string, string>
    _ray_commit: string
  }
  driver_agent_http_address: string
  driver_node_id: string
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
  experiment_id?: string
  driver_exit_code: number
}
