import { ref, watch } from 'vue';
import { defineStore } from 'pinia'
import experimentService from "@/services/experiments/experimentService";
import { retrieveEntrypoint, calculateDuration, downloadContent } from '@/helpers/index'

export const useExperimentStore = defineStore('experiment', () => {
  const experiments = ref([]);
  const jobs = ref([]);
  const selectedExperiment = ref(null);
  const selectedJob = ref(null);
  const selectedJobRslts = ref([]);
  const selectedExperimentRslts = ref([]);
  const isPolling = ref(false);
  let experimentInterval = null;
  const experimentLogs = ref([]);
  const completedStatus = ["SUCCEEDED", "FAILED"];

  async function loadExperiments() {
    const allJobs = await experimentService.fetchJobs();
    jobs.value = allJobs.map(job => parseJobDetails(job));
    experiments.value = getJobsPerExperiement();
  }

  function getJobsPerExperiement() {
    const experimentMap = jobs.value.reduce((acc, job) => {
      const key = `${job.name}-${job.experimentStart}`;
      // initialize a grouping object
      if (!acc[key]) {
        acc[key] = {
          id: key, // temporary key until BE provides one
          created: job.created,
          dataset: job.dataset,
          description: job.description,
          name: job.name, experimentStart: job.experimentStart,
          jobs: [],
          useCase: job.useCase,
          runTime: '',
          samples: job.evaluation.max_samples,
          models: [],
          status: 'SUCCEEDED'
        };
      }
      acc[key].jobs.push(job);
      acc[key].models = acc[key].jobs.map((singleJob) => singleJob.model);
      return acc;

    }, {})

    return Object.values(experimentMap);
  }

  /**
   *
   * @param {*} job - the job data to parse
   * @returns job data parsed for display as an experiment
   */
  function parseJobDetails(job) {
    return {
      ...retrieveEntrypoint(job),
      status: job.status.toUpperCase(),
      id: job.submission_id,
      useCase: `summarization`,
      created: job.start_time,
      description: job.description,
      experimentStart: job.start_time.slice(0, 16),
      end_time: job.end_time,
      runTime: job.end_time ? calculateDuration(job.start_time, job.end_time) : null
    };
  }

  /**
   *
   * @returns {string[]} IDs of stored experiments that have not completed
   */
  function getIncompleteJobIds() {
    return jobs.value
      .filter(job => !completedStatus.includes(job.status))
      .map(job => job.id);
  }

  /**
   *
   * @param {string} id - String (UUID) representing the experiment which should be updated with the latest status
   */
  async function updateJobStatus(id) {
    try {
      const status = await experimentService.fetchJobStatus(id);
      const job = jobs.value.find((job) => job.id === id);
      if (job) {
        job.status = status;
      }
    } catch (error) {
      console.error(`Failed to update status for job ${id} ${error}`);
    }
  }

  /**
   * Updates the status for stored experiments that are not completed
   */
  async function updateStatusForIncompleteJobs() {
    await Promise.all(
      getIncompleteJobIds()
        .map(id => updateJobStatus(id)));
  }

  async function runExperiment(experimentData) {
    const modelArray = experimentData.models;
    const jobRequests = modelArray.map((singleModel) => {
      // trigger one job per model
      const jobPayload = {
        ...experimentData,
        model: singleModel.uri,
      };
      return experimentService.triggerExperiment(jobPayload);
    });

    // Execute all requests in parallel
    // and wait for all of them to resolve or reject
    const results = await Promise.all(jobRequests);
    return results;
  }

  function loadExperimentDetails(id) {
    selectedExperiment.value = experiments.value.find(experiment => experiment.id === id);
  }

  async function loadJobDetails(id) {
    const jobData = await experimentService.fetchExperimentDetails(id);
    selectedJob.value = parseJobDetails(jobData);
  }

  async function loadResultsFile(jobId) {
    const blob = await experimentService.downloadResults(jobId);
    downloadContent(blob, `${selectedJob.value.name}_results`)
  }

  async function loadResults(experiment_id) {
    const results = await experimentService.fetchResults(experiment_id);
    if (results?.id) {
      selectedExperiment.value = experiments.value
        .find((experiment) => experiment.id === results.id);
      selectedExperimentRslts.value = transformResultsArray(results.resultsData);
    }
  }

  async function loadJobResults(jobId) {
    const results = await experimentService.fetchResults(jobId);
    if (results?.id) {
      selectedJob.value = jobs.value
        .find((job) => job.id === results.id);
      selectedJobRslts.value = transformResultsArray(results.resultsData);
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
    const logsData = await experimentService.fetchLogs(selectedJob.value.id);
    const logs = splitByEscapeCharacter(logsData.logs);
    logs.forEach(log => {
      const lastEntry = experimentLogs.value[experimentLogs.value.length - 1];
      if (experimentLogs.value.length === 0 || lastEntry !== log) {
      experimentLogs.value.push(log);
      }
    });
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
      // startPolling()
      return;
    } else if (isPolling.value) {
      stopPolling();
    }
  }, { deep: true });

  watch(selectedJob, (newValue) => {
    experimentLogs.value = [];
    // switch to the experiment the job belongs
    if (newValue) {
      const selectedExperimentId = `${newValue.name}-${newValue.experimentStart}`
      selectedExperiment.value = experiments.value.find((exp) => exp.id === selectedExperimentId)
      retrieveLogs();
    }
    if (newValue?.status === 'RUNNING') {
      startPolling()
      return;
    } else if (isPolling.value) {
      stopPolling();
    }
  }, { deep: true });
  return {
    experiments,
    jobs,
    loadExperiments,
    updateStatusForIncompleteJobs,
    loadExperimentDetails,
    loadJobDetails,
    loadResults,
    loadJobResults,
    loadResultsFile,
    selectedExperiment,
    selectedJob,
    experimentLogs,
    selectedExperimentRslts,
    selectedJobRslts,
    runExperiment
  }
})
