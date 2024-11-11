import { ref } from 'vue';
import { defineStore } from 'pinia'
import datasetsService from "@/services/datasets/datasetsService";

export const useDatasetStrore = defineStore('dataset', () => {
	const datasets = ref([]);


	async function loadDatasets() {
		if (datasets.value.length > 0) {return;}
		datasets.value = await datasetsService.fetchDatasets();
	}
	return {
		datasets,
		loadDatasets
	}
})