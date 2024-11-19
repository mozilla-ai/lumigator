<template>
  <div class="l-health-status">
    <p>Health: {{ healthStatus }}</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useHealthStore } from '@/stores/health/store';

const healthStore = useHealthStore();
const { healthStatus } = storeToRefs(healthStore);

onMounted(async () => {
  await healthStore.loadHealthStatus();
})
</script>

<style scoped lang="scss">
.l-health-status {
  font-size: $l-font-size-sm;
  display: flex;
  justify-content: flex-end;
  padding: $l-spacing-1/2;
  color: $l-grey-100;
}
</style>