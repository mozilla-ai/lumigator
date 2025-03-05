import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'
import type { Model } from '@/types/Model'

export async function fetchModels(tasks: string[] = ['summarization']) {
  const response = await lumigatorApiAxiosInstance.get('/models', {
    params: {
      tasks: tasks.join(','),
    },
  })

  return response.data.items
}

export const modelsService = {
  fetchModels,
}
