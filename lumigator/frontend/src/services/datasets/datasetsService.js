import http from '@/services/http';
import { PATH_DATASETS_ROOT, PATH_SINGLE_DATASET } from './api';

async function fetchDatasets() {
  try {
    const response = await http.get(PATH_DATASETS_ROOT());
    return response.data.items;
  } catch (error) {
    console.error("Error fetching datasets:", error.message || error);
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
  postDataset,
  deleteDataset
}