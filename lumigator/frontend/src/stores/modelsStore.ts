import { defineStore } from 'pinia'
import { modelsService } from '@/sdk/modelsService'
import type { Model } from '@/types/Model'
import { useQuery } from '@tanstack/vue-query'

export const useModelStore = defineStore('models', () => {
  const { data: models, refetch } = useQuery({
    queryKey: ['models'],
    queryFn: () => modelsService.fetchModels(),
    placeholderData: [],
    initialData: [],
  })

  async function fetchModels() {
    refetch()
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
