<template>
  <div
    class="l-experiment-logs"
  >
    <div class="header">
      <h3>Ray logs</h3>
      <p>Lumigator uses Ray as its orchestrator for running LLM workloads.</p>
    </div>
    <div
      ref="logContainer"
      class="l-experiment-logs__container"
    >
      <div
        v-for="(log, index) in experimentLogs"
        :key="index"
        class="l-experiment-logs__container-log-entry"
      >
        {{ log }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue';
import { storeToRefs } from 'pinia';
import { useExperimentStore } from '@/stores/experiments/store'
const experimentStore = useExperimentStore();
const { experimentLogs } = storeToRefs(experimentStore);
const logContainer = ref(null);
const logsLength = computed(() => experimentLogs.value.length)

const scrollToBottom = async () => {
  if (logContainer.value) {
    await nextTick();
    logContainer.value.scrollTop = logContainer.value.scrollHeight;
  }
};


watch(logsLength, () => scrollToBottom())
</script>

<style scoped lang="scss">
.l-experiment-logs {
  $root: &;
  border-radius: $l-main-radius;

  h3 {
    font-weight: $l-font-weight-normal;
    font-size: $l-font-size-md;
    color: $l-grey-150;
  }

  p {
    color: $l-grey-150;
    font-size: $l-menu-font-size;
  }
  &__container {
    height: 77vh;
    overflow-y: auto;
    background-color: #000;
    color: $l-grey-100;
    font-family: monospace;
    font-size: $l-font-size-sm;
    padding: 10px;
    border-radius: $l-main-radius;
    margin-top: $l-spacing-1;

    &-log-entry {
      margin-bottom: $l-spacing-1 *2;
      word-wrap: break-word;
    }

  }
}
</style>
