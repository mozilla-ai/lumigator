import http from '@/services/http';
import { PATH_EXPERIMENTS_ROOT, PATH_EXPERIMENTS_EVALUATE } from './api';


async function fetchExperiments() {
  try {
    const response = await http.get(PATH_EXPERIMENTS_ROOT());
    return response.data.items;
  } catch (error) {
    console.error("Error fetching experiments:", error.message || error);
    return [];
  }
}

async function triggerExperiment(experimentPayload) {
  try {
    const response = await http.post(PATH_EXPERIMENTS_EVALUATE(), experimentPayload, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    console.log(response);
    return response.data
  } catch (error) {
    console.log('error while creating Experiment', error)
  }
}

export default {
  fetchExperiments,
  triggerExperiment
}
