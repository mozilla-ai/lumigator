import { ref } from 'vue';
import { defineStore } from 'pinia'
import experimentService from "@/services/experiments/experimentService";
import { retrieveEntrypoint } from '@/helpers/index'

export const useExperimentStore = defineStore('experiment', () => {
  const experiments = ref([]);
  const selectedExperiment = ref()

  async function loadExperiments() {
    experiments.value = await experimentService.fetchExperiments();
  }

  async function runExperiment(experimentData) {
    const experimentResponse = await experimentService.triggerExperiment(experimentData);
    if (experimentResponse) {
      return experimentResponse.name
    }
  }

  async function loadDetails(id) {
    const details = await experimentService.fetchExperimentDetails(id);
    selectedExperiment.value = {
      ...retrieveEntrypoint(details),
      status: details.status,
      jobId: details.submission_id,
      useCase: `summarization`,
      created: details.start_time,
    }
  }

  return {
    experiments,
    loadDetails,
    loadExperiments,
    runExperiment
  }
})
