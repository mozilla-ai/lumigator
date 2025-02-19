import type { Experiment } from '@/types/Experiment'
import { WorkflowStatus } from '@/types/Workflow'

// aggregates the experiment's status based on its workflows statuses
export function retrieveStatus(experiment: Experiment): WorkflowStatus {
  const workflowStatuses = experiment.workflows.map((workflow) => workflow.status)
  const uniqueStatuses = new Set(workflowStatuses)

  if (uniqueStatuses.has(WorkflowStatus.RUNNING)) {
    return WorkflowStatus.RUNNING
  } else if (
    uniqueStatuses.has(WorkflowStatus.FAILED) &&
    uniqueStatuses.has(WorkflowStatus.SUCCEEDED)
  ) {
    return WorkflowStatus.INCOMPLETE
  } else {
    // if none of its workflows are running, or if some failed and others succeeded, then it probably means they all have the same status so just return it
    return [...uniqueStatuses][0]
  }
}
