import { ref } from 'vue'
import { defineStore } from 'pinia'
import { modelsService } from '@/services/models/modelsService'
import { getAxiosError } from '@/helpers/getAxiosError'
import type { AxiosError } from 'axios'

export const useModelStore = defineStore('models', () => {
  const models = ref([])

  async function fetchModels() {
    try {
      models.value = await modelsService.fetchModels()
    } catch (error) {
      console.error(getAxiosError(error as Error | AxiosError))
    }
  }

  return {
    models,
    fetchModels,
  }
})
