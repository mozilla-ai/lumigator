import http from '@/services/http';
import { PATH_DATASETS_ROOT, PATH_SINGLE_DATASET, PATH_DATASET_DOWNLOAD } from './api';

async function fetchDatasets() {
  try {
    const response = await http.get(PATH_DATASETS_ROOT());
    return response.data.items;
  } catch (error) {
    console.error("Error fetching datasets:", error.message || error);
    return [];
  }
}

async function fetchDatasetInfo(id) {
  try {
    const response = await http.get(PATH_SINGLE_DATASET(id));
    return response.data;
  } catch (error) {
    console.error("Error fetching dataset info:", error.message || error);
    return [];
  }
}

async function postDataset(formData) {
  try {
    const response = await http.post(PATH_DATASETS_ROOT(), formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data
  } catch (error) {
    return error
  }
}

async function downloadDataset(dataset_id) {
  try {
    const response = await http.get(PATH_DATASET_DOWNLOAD(dataset_id))
    const  download_url = response.data.download_urls[0];
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
    console.log(`Error dowloading dataset ${dataset_id}`, error)
  }
}

async function deleteDataset(id) {

  try {
    const response = await http.delete(PATH_SINGLE_DATASET(id));
    if (response.status === 200 || response.status === 204) {
      return response;
    } else {
      console.error("Unexpected response status: ", response.status);
    }
  } catch (error) {
    console.error("Error deleting dataset:", error);
  }
}

export default {
  fetchDatasets,
  fetchDatasetInfo,
  postDataset,
  downloadDataset,
  deleteDataset
}
