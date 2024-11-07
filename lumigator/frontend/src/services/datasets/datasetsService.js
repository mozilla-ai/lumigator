import http from '@/services/http';
import { PATH_GET_ALL_DATASETS } from './api';

async function fetchDatasets() {
  try {
    const response = await http.get(PATH_GET_ALL_DATASETS());
    return response.data.items;
  } catch (error) {
    console.error("Error fetching datasets:", error.message || error);
    return [];
  }
}


export default {
	fetchDatasets
}