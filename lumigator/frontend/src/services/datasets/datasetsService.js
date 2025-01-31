/**
 *  This file contains CRUD operations for datasets through the API
 *  More information @http://localhost:8000/docs
 */

import http from '@/services/http';
import {PATH_DATASETS_ROOT, PATH_SINGLE_DATASET, PATH_SINGLE_DATASET_DOWNLOAD} from './api';

/**
 * @returns {Promise<Array>} A promise that resolves to an array of datasets.
 */
async function fetchDatasets() {
  try {
    const response = await http.get(PATH_DATASETS_ROOT());
    return response.data.items;
  } catch (error) {
    console.error("Error fetching datasets:", error.message || error);
    return [];
  }
}

/**
 * Fetches information about a specific dataset.
 * @param {string} id - The ID of the dataset.
 */
async function fetchDatasetInfo(id) {
  try {
    const response = await http.get(PATH_SINGLE_DATASET(id));
    return response.data;
  } catch (error) {
    console.error("Error fetching dataset info:", error.message || error);
    return [];
  }
}

/**
 * Upload a new dataset to the BE.
 * @param {FormData} formData - The form data containing the dataset information.
 *  Proper schema for FormData can be found @ [POST] /api/v1/datasets/
 */
async function postDataset(formData) {
  try {
    const response = await http.post(PATH_DATASETS_ROOT(), formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data
  } catch (error) {
    return error.response
  }
}

/**
 * Deletes a specific dataset.
 * @param {string} id - The ID of the dataset to delete.
 */
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

/**
 * Downloads a specific dataset as a CSV file.
 * @param {string} id - The ID of the dataset to download.
 */
async function downloadDataset(id) {
  try {
    const url = `${PATH_SINGLE_DATASET_DOWNLOAD(id)}?extension=csv`;
    const response = await http.get(url);
    if (response.status !== 200) {
      console.error("Error getting dataset download URLs: ", response.status);
      return;
    }

    const { download_urls } = response.data;
    if (!download_urls) {
      console.error("No download URLs found in the response: ", response.data);
      return;
    } else if (download_urls.length > 1) {
      console.error("Expected a single dataset CSV URL: ", download_urls);
      return;
    }

    const fileResponse = await http.get(download_urls[0], {
      responseType: 'blob', // Important: Receive the file as a binary blob
    });
    return fileResponse.data;

  } catch (error) {
    console.error("Error downloading dataset: ", error.message || error);
  }
}

export default {
  fetchDatasets,
  fetchDatasetInfo,
  postDataset,
  deleteDataset,
  downloadDataset
}
