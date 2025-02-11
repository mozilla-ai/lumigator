export type Workflow = {
  created_at: string
  description: string
  experiment_id: string
  id: string
  name: string
  status: WorkflowStatus
  updated_at: string
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
