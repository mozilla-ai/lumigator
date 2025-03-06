import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { experimentsService } from '@/sdk/experimentsService'

import type { Experiment } from '@/types/Experiment'
import { retrieveStatus } from '@/helpers/retrieveStatus'

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

  return {
    // state
    experiments,
    fetchAllExperiments,
  }
})
