import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'

export const PATH_DATASETS_ROOT = () => `datasets/`
export const PATH_SINGLE_DATASET = (id: string) => `datasets/${id}`
export const PATH_SINGLE_DATASET_DOWNLOAD = (id: string) => `datasets/${id}/download`

export async function fetchDatasets() {
  const response = await lumigatorApiAxiosInstance.get(PATH_DATASETS_ROOT())
  return response.data.items
}

export async function fetchDatasetInfo(id: string) {
  const response = await lumigatorApiAxiosInstance.get(PATH_SINGLE_DATASET(id))
  return response.data
}

export async function postDataset(formData: FormData) {
  const response = await lumigatorApiAxiosInstance.post(PATH_DATASETS_ROOT(), formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export async function deleteDataset(id: string) {
  const response = await lumigatorApiAxiosInstance.delete(PATH_SINGLE_DATASET(id))
  if (response.status === 200 || response.status === 204) {
    return response
  } else {
    console.error('Unexpected response status: ', response.status)
  }
}

export async function downloadDataset(id: string) {
  const url = `${PATH_SINGLE_DATASET_DOWNLOAD(id)}?extension=csv`
  const response = await lumigatorApiAxiosInstance.get(url)

  const { download_urls } = response.data
  if (!download_urls) {
    console.error('No download URLs found in the response: ', response.data)
    return
  } else if (download_urls.length > 1) {
    console.error('Expected a single dataset CSV URL: ', download_urls)
    return
  }

  const fileResponse = await lumigatorApiAxiosInstance.get(download_urls[0], {
    responseType: 'blob', // Important: Receive the file as a binary blob
  })
  return fileResponse.data
}

export const datasetsService = {
  fetchDatasets,
  fetchDatasetInfo,
  postDataset,
  deleteDataset,
  downloadDataset,
}
