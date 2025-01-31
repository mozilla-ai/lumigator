/**
 * This file contains services related to experiments & jobs
 */

// TODO: Refactor into two services one for experiments one for jobs, when Backend can provide an experiment ID.

import http from '@/services/http';
import {
  PATH_JOBS_ROOT,
  PATH_EXPERIMENTS_EVALUATE,
  PATH_JOB_DETAILS,
  PATH_EXPERIMENT_RESULTS,
  PATH_EXPERIMENT_LOGS,
  PATHS_EXPERIMENTS_ANNOTATE,
} from './api';

/**
 *
 * @returns {array} of all jobs, regardless the experiment
 */
async function fetchJobs() {
  try {
    const response = await http.get(PATH_JOBS_ROOT());
    return response.data.items.map(p => ({
      ...p,
      status: p.status.toUpperCase(),
    }));
  } catch (error) {
    console.error("Error fetching experiments", error.message || error);
    return [];
  }
}

/**
 * Fetches details of a specific job by ID.
 * @param {string} id - The ID of the job.
 */

// TODO: Remame fetchJobDetails and refactor accodingly
async function fetchExperimentDetails(id) {
  try {
    const response = await http.get(PATH_JOB_DETAILS(id));
    if (response?.data?.status) {
      // Ensure that we transform status at the point the API returns it.
      response.data.status = response.data.status.toUpperCase();
    }
    return response.data;
  } catch (error) {
    console.error("Error fetching experiment details", error.message || error);
    return null;
  }
}

/**
 * Fetches the status of a specific job.
 * @param {string} id .
 */
async function fetchJobStatus(id) {
  const job = await fetchExperimentDetails(id);
  return job?.status;
}

/**
 * Triggers a new experiment with the given payload, due API limitations at the time.
 * In fact this funcition triggers an evaluation job.
 * @param {Object} experimentPayload - The payload for the experiment.
 *  The schema of experimentPayload can be found @ api/v1/experiments/
 */
 // TODO: For experiments with multiple models this function is called recursively for every model selected from the form.
 // Check ExperimentForm.vue
async function triggerExperiment(experimentPayload) {
  try {
    const response = await http.post(PATH_EXPERIMENTS_EVALUATE(), experimentPayload, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data
  } catch (error) {
    console.error('Error while creating experiment', error);
    return error.message;
  }
}

/**
 * Triggers a new annotation job with the given payload.
 * @param {Object} groundTruthPayload - The payload for the ground truth job.
 * @returns {Promise<Object|null>} A promise that resolves to the response data or null if an error occurs.
 */
async function triggerAnnotationJob(groundTruthPayload) {
  try {
    const response = await http.post(PATHS_EXPERIMENTS_ANNOTATE(), groundTruthPayload, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error while creating ground truth job', error);
    return null;
  }
}

/**
 * Fetches the results of a specific job.
 * @param {string} job_id
 */
async function fetchResults(job_id) {
  try {
    const response = await http.get(PATH_EXPERIMENT_RESULTS(job_id));
    const { download_url, id } = response.data;
    if (!download_url) {
      console.error("No download_url found in the response.");
      return;
    }
    const jsonData = await http.get(download_url)
    return {
      resultsData: jsonData.data,
      id,
      download_url
    }
  } catch (error) {
    console.error("Error fetching experiment results", error.message || error);
    return error;
  }
}

/**
 * Downloads the results of a specific experiment by ID.
 * @param {string} experiment_id .
 * @returns {Promise<Blob|Error>} A promise that resolves to a Blob containing the file data.
 */
async function downloadResults(experiment_id) {
  try {
    const response = await http.get(PATH_EXPERIMENT_RESULTS(experiment_id));
    const { download_url } = response.data;
    if (!download_url) {
      console.error("No download_url found in the response.");
      return;
    }
    const fileResponse = await http.get(download_url, {
      responseType: 'blob', // Important: Receive the file as a binary blob
    })
    const blob = fileResponse.data;
    return blob;
  } catch (error) {
    console.error("Error downloading experiment results", error.message || error);
    return error;
  }
}

/**
 * Fetches the logs of a specific job by ID.
 * @param {string} id .
 */
async function fetchLogs(id) {
  try {
    const logsResponse = await http.get(PATH_EXPERIMENT_LOGS(id));
    return logsResponse.data
  } catch (error) {
    console.error('Error fetching logs for job', id, error);
  }
}

export default {
  fetchJobs,
  fetchJobStatus,
  fetchResults,
  downloadResults,
  fetchExperimentDetails,
  triggerExperiment,
  triggerAnnotationJob,
  fetchLogs
};
