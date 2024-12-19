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
  const runningJobs = ref([])

  async function loadExperiments() {
    const experimentsList = await experimentService.fetchExperiments();
    experiments.value = experimentsList.map((job) => {
      return {
        ...retrieveEntrypoint(job),
        status: job.status.toUpperCase(),
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
      return experimentResponse;
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

  async function updateJobStatus(jobId) {
    try {
      const status = await experimentService.fetchJobStatus(jobId);
      const job = runningJobs.value.find((job) => job.id === jobId);
      if (job) {
        job.status = status.toUpperCase();
      }
    } catch (error) {
      console.error(`Failed to update status for job ${jobId} ${error}`);
    }
  }

  async function updateAllJobs() {
    const promises = runningJobs.value
      .filter((job) => job.status !== 'SUCCEEDED' &&
        job.status !== 'FAILED') // Exclude complete or failed jobs
      .map((job) => updateJobStatus(job.id));
    await Promise.all(promises);
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
    loadDetails,
    loadResults,
    loadResultsFile,
    selectedExperiment,
    experimentLogs,
    selectedExperimentRslts,
    updateAllJobs,
    loadExperiments,
    runExperiment,
    runningJobs,
  }
})
