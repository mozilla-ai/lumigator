import { ref } from 'vue';
import { defineStore } from 'pinia'
import resultsService from '@/services/results/resultsService';


export const useResultsStore = defineStore('results', () => {
  const results = ref([]);

  async function loadResults(jobId) {
    results.value = async resultsService.fetchResults(jobId);
  }


})
