import { ref } from 'vue';
import { defineStore } from 'pinia'
import experimentService from "@/services/experiments/experimentService";
import { retrieveEntrypoint, calculateDuration } from '@/helpers/index'

export const useExperimentStore = defineStore('experiment', () => {
  const experiments = ref([]);
  const selectedExperiment = ref(null);
  const selectedExperimentRslts = ref(null);

  async function loadExperiments() {
    const experimentsList = await experimentService.fetchExperiments();
    experiments.value = experimentsList.map((job) => {
      return {
        ...retrieveEntrypoint(job),
        status: job.status,
        id: job.submission_id,
        useCase: `summarization`,
        created: job.start_time,
        runTime: job.end_time ? calculateDuration(job.start_time, job.end_time) : null
      }
    })
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
      runTime: details.end_time ? calculateDuration(details.start_time, details.end_time) : '-'
    }
  }

  async function loadResults(experiment_id) {
    const results = await experimentService.fetchResults(experiment_id);
    if (results?.id) {
      selectedExperiment.value = experiments.value
        .find((experiment) => experiment.id === results.id);
      selectedExperimentRslts.value = results.resultsData;
    }
    console.log(selectedExperimentRslts.value);
  }

  return {
    experiments,
    loadDetails,
    loadResults,
    selectedExperiment,
    loadExperiments,
    runExperiment
  }
})
