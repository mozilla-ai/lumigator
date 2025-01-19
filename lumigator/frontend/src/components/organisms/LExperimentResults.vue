<template>
  <div class="experiment-results">
    <h1>Experiment Results</h1>
    <pre>{{ tableData }}</pre>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useExperimentStore } from "@/stores/experiments/store.js";
import { useModelStore } from "@/stores/models/store.js";
import { storeToRefs } from 'pinia';

// const tableData = ref([]);
const experimentStore = useExperimentStore();
const modelStore = useModelStore();
const { selectedExperimentRslts } = storeToRefs(experimentStore);
const { models } = storeToRefs(modelStore);

const tableData = computed(() => {
  const modelsMap = new Map(models.value.map(model => [model.uri, model]));
  return selectedExperimentRslts.value.map(job => ({
    ...job,
    model: modelsMap.get(job.model),
  }));
});

</script>

<style scoped lang="scss">
</style>
