import http from '@/services/http';
import { PATH_DATASETS_ROOT } from './api';

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

export default {
   fetchDatasets,
  postDataset
}