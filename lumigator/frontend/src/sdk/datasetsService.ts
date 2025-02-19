import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
import type { Dataset } from '@/types/Dataset'

export async function fetchDatasets(): Promise<Dataset[]> {
  const response = await lumigatorApiAxiosInstance.get('datasets/')
  return response.data.items
}

export async function fetchDatasetInfo(id: string): Promise<Dataset> {
  const response = await lumigatorApiAxiosInstance.get(`datasets/${id}`)
  return response.data
}

export async function postDataset(formData: FormData): Promise<Dataset> {
  const response = await lumigatorApiAxiosInstance.post('datasets/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export async function deleteDataset(id: string): Promise<void> {
  const response = await lumigatorApiAxiosInstance.delete(`datasets/${id}`)
  if (response.status === 200 || response.status === 204) {
    return
  } else {
    console.error('Unexpected response status: ', response.status)
  }
}

export async function downloadDataset(id: string): Promise<Blob> {
  const response = await lumigatorApiAxiosInstance.get(`datasets/${id}/download?extension=csv`)

  const { download_urls } = response.data
  if (!download_urls) {
    console.error('No download URLs found in the response: ', response.data)
    throw new Error('No download URLs found in the response.')
  } else if (download_urls.length > 1) {
    console.error('Expected a single dataset CSV URL: ', download_urls)
    throw new Error('Expected a single dataset CSV URL.')
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
