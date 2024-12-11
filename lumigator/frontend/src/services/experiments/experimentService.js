import http from '@/services/http';
import {
  PATH_EXPERIMENTS_ROOT,
  PATH_EXPERIMENTS_EVALUATE,
  PATH_EXPERIMENT_DETAILS,
  PATH_EXPERIMENT_RESULTS,
  PATH_EXPERIMENT_LOGS,
} from './api';


async function fetchExperiments() {
  try {
    const response = await http.get(PATH_EXPERIMENTS_ROOT());
    return response.data;
  } catch (error) {
    console.error("Error fetching experiments:", error.message || error);
    return [];
  }
}

async function fetchExperimentDetails(id) {
  const response = await http.get(PATH_EXPERIMENT_DETAILS(id));
  return response.data
}

async function triggerExperiment(experimentPayload) {
  try {
    const response = await http.post(PATH_EXPERIMENTS_EVALUATE(), experimentPayload, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data
  } catch (error) {
    console.log('error while creating Experiment', error);
    return error.message;
  }
}

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
      id
    }
  } catch (error) {
    console.error("Error fetching experiment results:", error.message || error);
    return error;
  }
}

async function fetchLogs(id) {
  try {
    const logsResponse = await http.get(PATH_EXPERIMENT_LOGS(id));
    return logsResponse.data
  } catch (error) {
    console.log(error);
  }
}

export default {
  fetchExperiments,
  fetchResults,
  fetchExperimentDetails,
  triggerExperiment,
  fetchLogs
};
