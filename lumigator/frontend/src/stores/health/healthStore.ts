import { ref } from 'vue'
import { defineStore } from 'pinia'
import { healthService } from '@/services/health/healthService'

export const useHealthStore = defineStore('health-store', () => {
  const healthStatus = ref()

  async function fetchHealthStatus() {
    healthStatus.value = await healthService.fetchHealthStatus()
  }

  return {
    healthStatus,
    fetchHealthStatus,
  }
})
