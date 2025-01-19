<template>
  <div class="experiment-results">
    <h1>Experiment Results</h1>
    <pre>{{ selectedExperiment }}</pre>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import {useExperimentStore} from "@/stores/experiments/store.js";
import { storeToRefs } from 'pinia';

const experimentStore = useExperimentStore();
const { selectedExperiment } = storeToRefs(experimentStore);

onMounted(() => {
  console.log('🧪', selectedExperiment.value)
})
</script>

<style scoped lang="scss">
</style>
