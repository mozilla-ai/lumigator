import { ref } from 'vue'
import { defineStore } from 'pinia'
import { modelsService } from '@/sdk/modelsService'

export const useModelStore = defineStore('models', () => {
  const models = ref([])

  async function fetchModels() {
    models.value = await modelsService.fetchModels()
  }

  return {
    models,
    fetchModels,
  }
})
