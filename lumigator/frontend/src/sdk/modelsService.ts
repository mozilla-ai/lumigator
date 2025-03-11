import { lumigatorApiAxiosInstance } from '@/helpers/lumigatorAxiosInstance'

export async function fetchModels(tasks: string[] = ['summarization', 'translation']) {
  const params = new URLSearchParams()
  tasks.forEach((task) => {
    params.append('tasks', task)
  })

  const response = await lumigatorApiAxiosInstance.get('/models', {
    params,
  })

  return response.data.items
}

export const modelsService = {
  fetchModels,
}
