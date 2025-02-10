import { lumigatorApiAxiosInstance } from '@/helpers/lumigator-axios-instance'

const PATH_MODELS_ROOT = (task_name: string) => `models/${task_name}`

export async function fetchModels(task_name = 'summarization') {
  const response = await lumigatorApiAxiosInstance.get(PATH_MODELS_ROOT(task_name))

  return response.data.items
}

export const modelsService = {
  fetchModels,
}
