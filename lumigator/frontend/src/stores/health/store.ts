import { ref } from 'vue'
import { defineStore } from 'pinia'
import healthService from '@/services/health/healthService'

export const useHealthStore = defineStore('health', () => {
  const healthStatus = ref(null)

  async function loadHealthStatus() {
    healthStatus.value = await healthService.fetchHealthStatus()
  }

  return {
    healthStatus,
    loadHealthStatus,
  }
})
