import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { experimentsService } from '@/sdk/experimentsService'

import { workflowsService } from '@/sdk/workflowsService'
import type { Experiment } from '@/types/Experiment'
import { WorkflowStatus } from '@/types/Workflow'

export const useExperimentStore = defineStore('experiments', () => {
  const experiments: Ref<Experiment[]> = ref([])

  const completedStatus = [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]

  async function fetchAllExperiments() {
    experiments.value = (await experimentsService.fetchExperiments()).map((experiment) => {
      return {
        ...experiment,
        status: retrieveStatus(experiment),
      }
    })
  }

  // aggregates the experiment's status based on its workflows statuses
  function retrieveStatus(experiment: Experiment): WorkflowStatus {
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

  /**
   * The retrieved IDs will determine which experiment is still Running
   * @returns {string[]} IDs of stored experiments that have not completed
   */
  function getIncompleteExperiments(): Experiment[] {
    return experiments.value.filter((experiment) => !completedStatus.includes(experiment.status))
  }

  /**
   *
   * @param {string} id - String (UUID) representing the experiment which should be updated with the latest status
   */
  async function updateExperimentStatus(experiment: Experiment): Promise<void> {
    try {
      const incompleteWorkflows = experiment.workflows.filter(
        (workflow) => !completedStatus.includes(workflow.status),
      )

      const incompleteWorkflowDetails = await Promise.all(
        incompleteWorkflows.map((workflow) => workflowsService.fetchWorkflowDetails(workflow.id)),
      )

      incompleteWorkflowDetails.forEach((workflow) => {
        const existingWorkflow = experiment.workflows.find((w) => w.id === workflow.id)
        if (existingWorkflow) {
          existingWorkflow.status = workflow.status
        }
      })

      const status = incompleteWorkflowDetails.every((workflow) =>
        completedStatus.includes(workflow.status),
      )
        ? WorkflowStatus.SUCCEEDED
        : retrieveStatus(experiment)

      // const e = experiments.value.find((exp) => exp.id === experiment.id)
      // if (e) {
      // e.status = status
      experiment.status = status
      // }
    } catch (error) {
      console.error(`Failed to update status for exp ${experiment} ${error}`)
    }
  }

  /**
   * Updates the status for stored experiments that are not completed
   */
  async function updateStatusForIncompleteExperiments() {
    await Promise.all(
      getIncompleteExperiments().map((experiment) => updateExperimentStatus(experiment)),
    )
  }

  return {
    // state
    experiments,
    fetchAllExperiments,
    updateStatusForIncompleteExperiments,
  }
})
