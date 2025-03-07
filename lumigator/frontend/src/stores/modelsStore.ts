import { ref } from 'vue'
import { defineStore } from 'pinia'
import { modelsService } from '@/sdk/modelsService'
import type { Model } from '@/types/Model'

export const useModelStore = defineStore('models', () => {
  const models = ref([])

  async function fetchModels() {
    models.value = await modelsService.fetchModels()
  }

  function filterModelsByUseCase(useCase: 'summarization' | 'translation') {
    return models.value.filter((model: Model) =>
      model.tasks.some((task) => {
        return task.hasOwnProperty(useCase)
      }),
    )
  }

  return {
    models,
    fetchModels,
    filterModelsByUseCase,
  }
})
