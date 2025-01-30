/**
 * Health store module.
 * State management for interacting with the /health/ endpoint
 * @module stores/health/store
 */

import { ref } from 'vue';
import { defineStore } from 'pinia'
import healthService from "@/services/health/healthService";

/**
 * Defines the health store.
 * @function useHealthStore
 * @returns {Object} The health store with state and actions.
 */
export const useHealthStore = defineStore('health', () => {
  const healthStatus = ref(null);

  /**
   * Loads the health status from the health service.
   * @async
   * @function loadHealthStatus
   * @returns {Promise<void>} A promise that resolves when the health status is loaded.
   */
  async function loadHealthStatus() {
    healthStatus.value = await healthService.fetchHealthStatus();
  }

  return {
    healthStatus,
    loadHealthStatus
  }
})
