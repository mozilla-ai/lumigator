import { ref, watch } from 'vue';
import { defineStore } from 'pinia'
import experimentService from "@/services/experiments/experimentService";
import { retrieveEntrypoint, calculateDuration, downloadContent } from '@/helpers/index'

export const useExperimentStore = defineStore('experiment', () => {
  const experiments = ref([]);
  const selectedExperiment = ref(null);
  const selectedExperimentRslts = ref([]);
  const isPolling = ref(false);
  let experimentInterval = null;
  const experimentLogs = ref([]);
  const completedStatus = ["SUCCEEDED", "FAILED"];

  async function loadExperiments() {
    const experimentsList = await experimentService.fetchExperiments();
    experiments.value = experimentsList.map(job => parseExperiment(job));
  }

  /**
   *
   * @param {*} job - the job data to parse
   * @returns job data parsed for display as an experiment
   */
  function parseExperiment(job) {
    return {
      ...retrieveEntrypoint(job),
      status: job.status.toUpperCase(),
      id: job.submission_id,
      useCase: `summarization`,
      created: job.start_time,
      runTime: job.end_time ? calculateDuration(job.start_time, job.end_time) : null
    };
  }

  /**
   *
   * @returns {string[]} IDs of stored experiments that have not completed
   */
  function getIncompleteExperimentIds() {
    return experiments.value
      .filter(experiment => !completedStatus.includes(experiment.status))
      .map(experiment => experiment.id);
  }

  /**
   *
   * @param {string} id - String (UUID) representing the experiment which should be updated with the latest status
   */
  async function updateExperimentStatus(id) {
    try {
      const status = await experimentService.fetchJobStatus(id);
      const experiment = experiments.value.find((experiment) => experiment.id === id);
      if (experiment) {
        experiment.status = status;
      }
    } catch (error) {
      console.error(`Failed to update status for experiment ${id} ${error}`);
    }
  }

  /**
   * Updates the status for stored experiments that are not completed
   */
  async function updateStatusForIncompleteExperiments() {
    await Promise.all(
      getIncompleteExperimentIds()
      .map(id => updateExperimentStatus(id)));
  }

  async function runExperiment(experimentData) {
    const modelArray = experimentData.models;
    const jobRequests = modelArray.map((singleModel) => {
      // trigger one job per model
      const jobPayload = {
        ...experimentData,
        model: singleModel.link,
      };
      return experimentService.triggerExperiment(jobPayload);
    });

    // Execute all requests in parallel
    // and wait for all of them to resolve or reject
    const results = await Promise.all(jobRequests);
    return results;
  }

  async function loadDetails(id) {
    const details = await experimentService.fetchExperimentDetails(id);
    selectedExperiment.value = parseExperiment(details);
    experimentLogs.value = [];
    retrieveLogs();
  }

  async function loadResultsFile(experiment_id) {
    const blob = await experimentService.downloadResults(experiment_id);
    downloadContent(blob, `${selectedExperiment.value.name}_results`)
  }

  async function loadResults(experiment_id) {
    const results = await experimentService.fetchResults(experiment_id);
    if (results?.id) {
      selectedExperiment.value = experiments.value
        .find((experiment) => experiment.id === results.id);
      selectedExperimentRslts.value = transformResultsArray(results.resultsData);
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

  async function retrieveLogs() {
    const logsData = await experimentService.fetchLogs(selectedExperiment.value.id);
    const logs = splitByEscapeCharacter(logsData.logs);
    logs.forEach(log => experimentLogs.value.push(log));
  }

  function splitByEscapeCharacter(input) {
    const result = input.split('\n');
    return result;
  }

  function startPolling() {
    experimentLogs.value = [];
    if (!isPolling.value) {
      isPolling.value = true;
      retrieveLogs();
      // Poll every 3 seconds
      experimentInterval = setInterval(retrieveLogs, 3000);
    }
  }

  function stopPolling() {
    if (isPolling.value) {
      isPolling.value = false;
      clearInterval(experimentInterval);
      experimentInterval = null;
    }
  }

  watch(selectedExperiment, (newValue) => {
    if (newValue?.status === 'RUNNING') {
      startPolling()
      return;
    } else if (isPolling.value) {
      stopPolling();
    }
  }, { deep: true });

  return {
    experiments,
    loadExperiments,
    updateStatusForIncompleteExperiments,
    loadDetails,
    loadResults,
    loadResultsFile,
    selectedExperiment,
    experimentLogs,
    selectedExperimentRslts,
    runExperiment
  }
})
