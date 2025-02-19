import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { experimentsService } from '@/sdk/experimentsService'

import type { Experiment } from '@/types/Experiment'
import { WorkflowStatus } from '@/types/Workflow'

export const useExperimentStore = defineStore('experiments', () => {
  const experiments: Ref<Experiment[]> = ref([])
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

  return {
    // state
    experiments,
    fetchAllExperiments,
  }
})
