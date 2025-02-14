import type { WorkflowStatus } from './Workflow'

export type JobDetails = {
  type: string
  submission_id: string
  driver_info?: unknown
  status: WorkflowStatus
  entrypoint: string
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
  dataset: {
    id: string
    name: string
  }
}
