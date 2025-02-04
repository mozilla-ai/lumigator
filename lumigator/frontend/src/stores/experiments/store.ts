import { ref, watch, computed } from 'vue';
import { defineStore } from 'pinia';
import experimentService from '@/services/experiments/experimentService';
import { retrieveEntrypoint, calculateDuration, downloadContent } from '@/helpers/index';

export const useExperimentStore = defineStore('experiment', () => {
  const experiments = ref([]);
  const jobs = ref([]);
  const inferenceJobs = ref([]);
  const selectedExperiment = ref(null);
  const selectedJob = ref(null);
  const selectedJobRslts = ref([]);
  const selectedExperimentRslts = ref([]);
  const isPolling = ref(false);
  let experimentInterval = null;
  const experimentLogs = ref([]);
  const completedStatus = ['SUCCEEDED', 'FAILED'];

  const hasRunningInferenceJob = computed(() => {
    return inferenceJobs.value.some((job) => job.status === 'RUNNING');
  });

  async function loadExperiments() {
    const allJobs = await experimentService.fetchJobs();
    inferenceJobs.value = allJobs
      .filter((job) => job.metadata.job_type === 'inference')
      .map((job) => parseJobDetails(job));
    jobs.value = allJobs
      .filter((job) => job.metadata.job_type === 'evaluate')
      .map((job) => parseJobDetails(job));
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
          name: job.name,
          experimentStart: job.experimentStart,
          jobs: [],
          useCase: job.useCase,
          runTime: '',
          samples: job.max_samples,
          models: [],
          status: 'SUCCEEDED',
        };
      }
      acc[key].jobs.push(job);
      acc[key].models = acc[key].jobs.map((singleJob) => singleJob.model);
      return acc;
    }, {});

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
      runTime: job.end_time ? calculateDuration(job.start_time, job.end_time) : null,
    };
  }

  /**
   *
   * @returns {string[]} IDs of stored experiments that have not completed
   */
  function getIncompleteJobIds() {
    return jobs.value.filter((job) => !completedStatus.includes(job.status)).map((job) => job.id);
  }

  /**
   *
   * @param {string} id - String (UUID) representing the experiment which should be updated with the latest status
   */
  // TODO: Refactor for each kind of job OR gather all jobs into one array for internal use
  async function updateJobStatus(id) {
    try {
      const status = await experimentService.fetchJobStatus(id);
      const inferenceJob = inferenceJobs.value.find((job) => job.id === id);
      if (inferenceJob) {
        inferenceJob.status = status;
      }
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
    await Promise.all(getIncompleteJobIds().map((id) => updateJobStatus(id)));
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
    selectedExperiment.value = experiments.value.find((experiment) => experiment.id === id);
  }

  async function loadJobDetails(id) {
    const jobData = await experimentService.fetchExperimentDetails(id);
    selectedJob.value = parseJobDetails(jobData);
  }

  async function loadResultsFile(jobId) {
    const blob = await experimentService.downloadResults(jobId);
    downloadContent(blob, `${selectedJob.value.name}_results`);
  }

  async function loadExperimentResults(experiment) {
    for (const job of experiment.jobs) {
      const results = await experimentService.fetchResults(job.id);
      if (results?.id) {
        const modelRow = {
          model: results.resultsData.model,
          meteor: results.resultsData.meteor,
          bertscore: results.resultsData.bertscore,
          rouge: results.resultsData.rouge,
          runTime: getJobRuntime(results.id),
          jobResults: transformResultsArray(results.resultsData),
        };
        selectedExperimentRslts.value.push(modelRow);
      }
    }
  }

  async function loadJobResults(jobId) {
    const results = await experimentService.fetchResults(jobId);
    if (results?.id) {
      selectedJob.value = jobs.value.find((job) => job.id === results.id);
      selectedJobRslts.value = transformResultsArray(results.resultsData);
    }
  }

  function transformResultsArray(objectData) {
    const transformedArray = objectData.examples.map((example, index) => {
      return {
        example,
        bertscore: {
          f1: objectData.bertscore?.f1?.[index] ?? 0,
          f1_mean: objectData.bertscore?.f1_mean ?? 0,
          hashcode: objectData.bertscore?.hashcode ?? 0,
          precision: objectData.bertscore?.precision?.[index] ?? 0,
          precision_mean: objectData.bertscore?.precision_mean ?? 0,
          recall: objectData.bertscore?.recall?.[index] ?? 0,
          recall_mean: objectData.bertscore?.recall_mean ?? 0,
        },
        evaluation_time: objectData.evaluation_time ?? 0,
        ground_truth: objectData.ground_truth?.[index],
        meteor: {
          meteor: objectData.meteor?.meteor?.[index] ?? 0,
          meteor_mean: objectData.meteor?.meteor_mean ?? 0,
        },
        model: objectData.model,
        predictions: objectData.predictions?.[index],
        rouge: {
          rouge1: objectData.rouge?.rouge1?.[index] ?? 0,
          rouge1_mean: objectData.rouge?.rouge1_mean ?? 0,
          rouge2: objectData.rouge?.rouge2?.[index] ?? 0,
          rouge2_mean: objectData.rouge?.rouge2_mean ?? 0,
          rougeL: objectData.rouge?.rougeL?.[index] ?? 0,
          rougeL_mean: objectData.rouge?.rougeL_mean ?? 0,
          rougeLsum: objectData.rouge?.rougeLsum?.[index] ?? 0,
          rougeLsum_mean: objectData.rouge?.rougeLsum_mean ?? 0,
        },
        summarization_time: objectData.summarization_time,
      };
    });
    return transformedArray;
  }

  async function retrieveLogs() {
    const logsData = await experimentService.fetchLogs(selectedJob.value.id);
    const logs = splitByEscapeCharacter(logsData.logs);
    logs.forEach((log) => {
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

  async function startGroundTruthGeneration(groundTruthPayload) {
    try {
      const jobResponse = await experimentService.triggerAnnotationJob(groundTruthPayload);
      if (jobResponse) {
        // Start polling to monitor the job status
        await updateJobStatus(jobResponse.id); // Ensure initial update
        startPollingForJob(jobResponse.id); // Add polling for ground truth job
        return jobResponse;
      }
      return null;
    } catch (error) {
      console.error('Failed to start ground truth generation:', error);
      return null;
    }
  }

  function startPollingForJob(jobId) {
    isPolling.value = true;
    experimentInterval = setInterval(() => {
      updateJobStatus(jobId).then(() => {
        const job = experiments.value.find((experiment) => experiment.id === jobId);
        if (completedStatus.includes(job?.status)) {
          stopPolling(); // Stop polling when the job is complete
        }
      });
    }, 3000); // Poll every 3 seconds
  }

  function getJobRuntime(jobId) {
    const job = jobs.value.find((job) => job.id === jobId);
    return job ? job.runTime : null;
  }

  watch(
    selectedExperiment,
    (newValue) => {
      if (newValue?.status === 'RUNNING') {
        // startPolling()
        return;
      } else if (isPolling.value) {
        stopPolling();
      }
    },
    { deep: true },
  );

  watch(
    selectedJob,
    (newValue) => {
      experimentLogs.value = [];
      if (newValue) {
        const isEvaluationJob = jobs.value.some((job) => job?.id === newValue.id);
        if (isEvaluationJob) {
          // switch to the experiment the job belongs
          const selectedExperimentId = `${newValue.name}-${newValue.experimentStart}`;
          selectedExperiment.value = experiments.value.find(
            (exp) => exp.id === selectedExperimentId,
          );
        }
        retrieveLogs();
      }
      if (newValue?.status === 'RUNNING') {
        startPolling();
        return;
      } else if (isPolling.value) {
        stopPolling();
      }
    },
    { deep: true },
  );

  return {
    // state
    experiments,
    jobs,
    inferenceJobs,
    selectedExperiment,
    selectedJob,
    experimentLogs,
    selectedExperimentRslts,
    selectedJobRslts,
    isPolling,
    // computed
    hasRunningInferenceJob,
    // actions
    loadExperiments,
    updateStatusForIncompleteJobs,
    loadExperimentDetails,
    loadJobDetails,
    loadExperimentResults,
    loadJobResults,
    loadResultsFile,
    startGroundTruthGeneration,
    runExperiment,
  };
});
