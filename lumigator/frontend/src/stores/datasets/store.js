import { ref } from 'vue';
import { defineStore } from 'pinia'
import datasetsService from "@/services/datasets/datasetsService";

export const useDatasetStore = defineStore('dataset', () => {
  const datasets = ref([]);
  const selectedDataset = ref(null);


  async function loadDatasets() {
    datasets.value = await datasetsService.fetchDatasets();
  }

  async function loadDatasetInfo(datasetID) {
    selectedDataset.value = await datasetsService.fetchDatasetInfo(datasetID);
  }

  function resetSelection() {
    selectedDataset.value = null;
  }

  async function uploadDataset(datasetFile) {
    if (!datasetFile) { return }
    // Create a new FormData object and append the selected file and the required format
    const formData = new FormData();
    formData.append('dataset', datasetFile); // Attach the file
    formData.append('format', 'job'); // Specification @localhost:8000/docs
    const uploadConfirm = await datasetsService.postDataset(formData)
    if (uploadConfirm.status) {
      console.log('⚠️ Error', uploadConfirm.message);
    }
    await loadDatasets();
  }

  async function deleteDataset(id) {
    if (!id) { return };
    if (selectedDataset.value?.id === id) {
      resetSelection();
    }
    await datasetsService.deleteDataset(id);
    await loadDatasets();
  }

  return {
    datasets,
    loadDatasets,
    selectedDataset,
    loadDatasetInfo,
    resetSelection,
    uploadDataset,
    deleteDataset
  }
})
