import { ref } from 'vue';
import { defineStore } from 'pinia';
import modelsService from '@/services/models/modelsService';

export const useModelStore = defineStore('models', () => {
  const models = ref([])


  async function loadModels() {
    models.value = await modelsService.fetchModels();
  }

  return {
    models,
    loadModels
  }
});
