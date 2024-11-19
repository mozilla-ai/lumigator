import { ref } from 'vue';
import { defineStore } from 'pinia'
import experimentService from "@/services/experiments/experimentService";

export const useExperimentStore = defineStore('experiment', () => {
  const experiments = ref([]);

  async function runExperiment(experimentData) {
    const experimentResponse = await experimentService.triggerExperiment(experimentData);
    if (experimentResponse) {
      console.log('🎉 Expriment created succsessfully ', experimentResponse)
      return experimentResponse.name
    }
  }

  return {
    experiments,
    runExperiment
  }
})
