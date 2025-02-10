import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { datasetsService } from '@/sdk/datasetsService'

import { useToast } from 'primevue/usetoast'
import type { ToastMessageOptions } from 'primevue'
import type { Dataset } from '@/types/Dataset'
import { getAxiosError } from '@/helpers/getAxiosError'
import type { AxiosError } from 'axios'
import { downloadContent } from '@/helpers/downloadContent'

export const useDatasetStore = defineStore('datasets', () => {
  const datasets: Ref<Dataset[]> = ref([])
  const selectedDataset: Ref<Dataset | undefined> = ref()
  const toast = useToast()

  async function fetchDatasets() {
    try {
      datasets.value = await datasetsService.fetchDatasets()
    } catch {
      datasets.value = []
    }
  }

  async function fetchDatasetDetails(datasetID: string) {
    try {
      selectedDataset.value = await datasetsService.fetchDatasetInfo(datasetID)
    } catch {
      selectedDataset.value = undefined
    }
  }

  function resetSelection() {
    selectedDataset.value = undefined
  }

  async function uploadDataset(datasetFile: File) {
    if (!datasetFile) {
      return
    }
    // Create a new FormData object and append the selected file and the required format
    const formData = new FormData()
    formData.append('dataset', datasetFile) // Attach the file
    formData.append('format', 'job') // Specification @localhost:8000/docs
    try {
      const uploadConfirm = await datasetsService.postDataset(formData)
      if (uploadConfirm.status) {
        toast.add({
          severity: 'error',
          summary: `${uploadConfirm.data.detail}`,
          messageicon: 'pi pi-exclamation-triangle',
          group: 'br',
        } as ToastMessageOptions & { messageicon: string })
      }
    } catch (error) {
      const errorMessage = getAxiosError(error as Error | AxiosError)
      toast.add({
        severity: 'error',
        summary: `${errorMessage}`,
        messageicon: 'pi pi-exclamation-triangle',
        group: 'br',
      } as ToastMessageOptions & { messageicon: string })
    }
    await fetchDatasets()
  }

  async function deleteDataset(id: string) {
    if (!id) {
      return
    }
    if (selectedDataset.value?.id === id) {
      resetSelection()
    }
    await datasetsService.deleteDataset(id)
    await fetchDatasets()
  }

  // TODO: this shouldnt depend on refs/state, it can be a util function
  async function downloadDatasetFile() {
    if (selectedDataset.value) {
      const blob = await datasetsService.downloadDataset(selectedDataset.value?.id)
      downloadContent(blob, selectedDataset.value?.filename)
    }
  }

  return {
    datasets,
    fetchDatasets,
    selectedDataset,
    fetchDatasetDetails,
    resetSelection,
    uploadDataset,
    deleteDataset,
    downloadDatasetFile,
  }
})
