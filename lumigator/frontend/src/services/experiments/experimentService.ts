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
    return response.data.items.map((p) => ({
      ...p,
      status: p.status.toUpperCase(),
    }));
  } catch (error) {
    console.error('Error fetching experiments', error.message || error);
    return [];
  }
}

async function fetchExperimentDetails(id) {
  try {
    const response = await http.get(PATH_JOB_DETAILS(id));
    if (response?.data?.status) {
      // Ensure that we transform status at the point the API returns it.
      response.data.status = response.data.status.toUpperCase();
    }
    return response.data;
  } catch (error) {
    console.error('Error fetching experiment details', error.message || error);
    return null;
  }
}

async function fetchJobStatus(id) {
  const job = await fetchExperimentDetails(id);
  return job?.status;
}

async function triggerExperiment(experimentPayload) {
  try {
    const response = await http.post(PATH_EXPERIMENTS_EVALUATE(), experimentPayload, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error while creating experiment', error);
    return error.message;
  }
}

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
export { triggerAnnotationJob };

async function fetchResults(job_id) {
  try {
    const response = await http.get(PATH_EXPERIMENT_RESULTS(job_id));
    const { download_url, id } = response.data;
    if (!download_url) {
      console.error('No download_url found in the response.');
      return;
    }
    const jsonData = await http.get(download_url);
    return {
      resultsData: jsonData.data,
      id,
      download_url,
    };
  } catch (error) {
    console.error('Error fetching experiment results', error.message || error);
    return error;
  }
}

async function downloadResults(experiment_id) {
  try {
    const response = await http.get(PATH_EXPERIMENT_RESULTS(experiment_id));
    const { download_url } = response.data;
    if (!download_url) {
      console.error('No download_url found in the response.');
      return;
    }
    const fileResponse = await http.get(download_url, {
      responseType: 'blob', // Important: Receive the file as a binary blob
    });
    const blob = fileResponse.data;
    return blob;
  } catch (error) {
    console.error('Error downloading experiment results', error.message || error);
    return error;
  }
}

async function fetchLogs(id) {
  try {
    const logsResponse = await http.get(PATH_EXPERIMENT_LOGS(id));
    return logsResponse.data;
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
  fetchLogs,
};
