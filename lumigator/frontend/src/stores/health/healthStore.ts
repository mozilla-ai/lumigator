import { ref } from 'vue'
import { defineStore } from 'pinia'
import { healthService } from '@/services/health/healthService'
import { getAxiosError } from '@/helpers/getAxiosError'
import type { AxiosError } from 'axios'

export const useHealthStore = defineStore('health-store', () => {
  const healthStatus = ref()

  async function fetchHealthStatus() {
    try {
      healthStatus.value = await healthService.fetchHealthStatus()
    } catch (error) {
      console.error(getAxiosError(error as Error | AxiosError))
    }
  }

  return {
    healthStatus,
    fetchHealthStatus,
  }
})
