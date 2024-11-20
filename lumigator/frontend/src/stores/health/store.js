import { ref } from 'vue';
import { defineStore } from 'pinia'
import healthService from "@/services/health/healthService";

export const useHealthStore = defineStore('health', () => {
  const healthStatus = ref(null);
  const runningJobs = ref([])

  async function loadHealthStatus() {
    healthStatus.value = await healthService.fetchHealthStatus();
  }

  async function updateJobStatus(jobId) {
    try {
      const status = await healthService.fetchJobStatus(jobId);
      const job = runningJobs.value.find((job) => job.id === jobId);
      if (job) {
        job.status = status;
      }
    } catch (error) {
      console.error(`Failed to update status for job ${jobId} ${error}`);
    }
  }

  async function updateAllJobs() {
    const promises = runningJobs.value
      .filter((job) => job.status !== 'SUCCEEDED' && job.status !== 'FAILED') // Exclude complete or failed jobs
      .map((job) => updateJobStatus(job.id));
    await Promise.all(promises);
  }

  return {
    healthStatus,
    updateAllJobs,
    runningJobs,
    loadHealthStatus
  }

})
