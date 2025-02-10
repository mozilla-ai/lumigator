import { lumigatorApiAxiosInstance } from '@/helpers/lumigator-axios-instance'

const PATH_HEALTH_ROOT = () => `health/`

export async function fetchHealthStatus() {
  const response = await lumigatorApiAxiosInstance.get(PATH_HEALTH_ROOT())
  return response.data.status
}

export const healthService = {
  fetchHealthStatus,
}
