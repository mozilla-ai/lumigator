import http from '@/services/http';
import {
  PATH_EXPERIMENTS_ROOT,
  PATH_EXPERIMENTS_EVALUATE,
  PATH_EXPERIMENT_DETAILS,
  PATH_EXPERIMENT_RESULTS
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
    // console.log(response);
    return response.data
  } catch (error) {
    console.log('error while creating Experiment', error)
  }
}

async function fetchResults(id) {
  try {
    const response = await http.get(PATH_EXPERIMENT_RESULTS(id));
    const downloadUrl = response.data.download_url;
    // console.log('service', results);
    const jsonRes = jsonFetch(downloadUrl);
    console.log(jsonRes);
    // window.open(downloadUrl, "_blank");

    return response.data;
  } catch (error) {
    console.error("Error fetching experiments:", error.message || error);
    return [];
  }
}

async function jsonFetch(url) {
  console.log(url)
  const res = await fetch(url);
  const jsonData = await res.json;
  console.log(jsonData)
  return res;
}

export default {
  fetchExperiments,
  fetchResults,
  fetchExperimentDetails,
  triggerExperiment
}
