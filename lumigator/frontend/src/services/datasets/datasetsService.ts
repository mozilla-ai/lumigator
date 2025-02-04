import http from '@/services/http';
import { PATH_DATASETS_ROOT, PATH_SINGLE_DATASET, PATH_SINGLE_DATASET_DOWNLOAD } from './api';
import { AxiosError } from 'axios';

async function fetchDatasets() {
  try {
    const response = await http.get(PATH_DATASETS_ROOT())
    return response.data.items
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error fetching datasets:', error.message || error);
    } else if (error instanceof AxiosError) {
      console.error('Error fetching datasets:', error.response?.data || error);
    }
    return [];
  }
}

async function fetchDatasetInfo(id: string) {
  try {
    const response = await http.get(PATH_SINGLE_DATASET(id))
    return response.data
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error fetching dataset info:', error.message || error);
    } else if (error instanceof AxiosError) {
      console.error('Error fetching dataset info:', error.response?.data || error);
    }
    return [];
  }
}

async function postDataset(formData: FormData) {
  try {
    const response = await http.post(PATH_DATASETS_ROOT(), formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    if (error instanceof Error) {
      return error;
    } else if (error instanceof AxiosError) {
      return error.response;
    }
  }
}

async function deleteDataset(id: string) {
  try {
    const response = await http.delete(PATH_SINGLE_DATASET(id))
    if (response.status === 200 || response.status === 204) {
      return response
    } else {
      console.error('Unexpected response status: ', response.status)
    }
  } catch (error) {
    console.error('Error deleting dataset:', error)
  }
}

async function downloadDataset(id: string) {
  try {
    const url = `${PATH_SINGLE_DATASET_DOWNLOAD(id)}?extension=csv`
    const response = await http.get(url)
    if (response.status !== 200) {
      console.error('Error getting dataset download URLs: ', response.status)
      return
    }

    const { download_urls } = response.data
    if (!download_urls) {
      console.error('No download URLs found in the response: ', response.data)
      return
    } else if (download_urls.length > 1) {
      console.error('Expected a single dataset CSV URL: ', download_urls)
      return
    }

    const fileResponse = await http.get(download_urls[0], {
      responseType: 'blob', // Important: Receive the file as a binary blob
    })
    return fileResponse.data
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error downloading dataset: ', error.message || error);
    } else if (error instanceof AxiosError) {
      console.error('Error downloading dataset: ', error.response?.data || error);
    }
  }
}

export default {
  fetchDatasets,
  fetchDatasetInfo,
  postDataset,
  deleteDataset,
  downloadDataset,
}
