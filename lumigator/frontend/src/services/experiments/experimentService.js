import http from '@/services/http';
import {
  PATH_EXPERIMENTS_ROOT,
  PATH_EXPERIMENTS_EVALUATE,
  PATH_EXPERIMENT_DETAILS
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
    console.log('error while creating Experiment', error)
  }
}

export default {
  fetchExperiments,
  fetchExperimentDetails,
  triggerExperiment
}
