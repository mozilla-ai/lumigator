import { ref } from 'vue';
import { defineStore } from 'pinia'
import experimentService from "@/services/experiments/experimentService";
import { retrieveEntrypoint, calculateDuration } from '@/helpers/index'

export const useExperimentStore = defineStore('experiment', () => {
  const experiments = ref([]);
  const selectedExperiment = ref(null);
  const selectedExperimentRslts = ref([]);

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
      id: details.submission_id,
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
      selectedExperimentRslts.value = transformResultsArray(results.resultsData);
     ;
    }
  }

  function transformResultsArray(objectData) {
    const transformedArray = objectData.examples.map((example, index) => {
      return {
        example,
        bertscore: {
          f1: objectData.bertscore.f1[index],
          f1_mean: objectData.bertscore.f1_mean,
          hashcode: objectData.bertscore.hashcode,
          precision: objectData.bertscore.precision[index],
          precision_mean: objectData.bertscore.precision_mean,
          recall: objectData.bertscore.recall[index],
          recall_mean: objectData.bertscore.recall_mean,
        },
        evaluation_time: objectData.evaluation_time,
        ground_truth: objectData.ground_truth[index],
        meteor: {
          meteor: objectData.meteor.meteor[index],
          meteor_mean: objectData.meteor.meteor_mean,
        },
        model: objectData.model,
        predictions: objectData.predictions[index],
        rouge: {
          rouge1: objectData.rouge.rouge1[index],
          rouge1_mean: objectData.rouge.rouge1_mean,
          rouge2: objectData.rouge.rouge2[index],
          rouge2_mean: objectData.rouge.rouge2_mean,
          rougeL: objectData.rouge.rougeL[index],
          rougeL_mean: objectData.rouge.rougeL_mean,
          rougeLsum: objectData.rouge.rougeLsum[index],
          rougeLsum_mean: objectData.rouge.rougeLsum_mean,
        },
        summarization_time: objectData.summarization_time,
        }
    });
    return transformedArray
  }

  return {
    experiments,
    loadDetails,
    loadResults,
    selectedExperiment,
    selectedExperimentRslts,
    loadExperiments,
    runExperiment
  }
})
