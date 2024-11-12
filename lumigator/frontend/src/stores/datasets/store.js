import { ref } from 'vue';
import { defineStore } from 'pinia'
import datasetsService from "@/services/datasets/datasetsService";

export const useDatasetStore = defineStore('dataset', () => {
  const datasets = ref([]);


  async function loadDatasets() {
    datasets.value = await datasetsService.fetchDatasets();
  }

  async function uploadDataset(datasetFile) {
    if (!datasetFile) { return }
    // Create a new FormData object and append the selected file and the required format
    const formData = new FormData();
    formData.append('dataset', datasetFile); // Attach the file
    formData.append('format', 'job'); // Specification @localhost:8000/docs
    const uploadConfirm = await datasetsService.postDataset(formData)
    console.log('uploadConfirm', uploadConfirm)
    if (uploadConfirm.status) {
      console.log('⚠️ Error', uploadConfirm.message);
    }
    await loadDatasets();
  }
  return {
    datasets,
    loadDatasets,
    uploadDataset
  }
})