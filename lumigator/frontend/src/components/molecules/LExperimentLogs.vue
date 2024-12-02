<template>
  <div
    class="l-experiment-logs"
  >
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
  height: 100%;

  &__container {
    height: calc($l-bottom-drawer-height * 0.8);
    min-height: 100%;
    overflow-y: auto;
    background-color: $l-card-bg;
    color: $l-grey-100;
    font-family: monospace;
    font-size: $l-font-size-sm;
    line-height: 1.9;
    padding: 10px $l-spacing-1;
    border-radius: $l-main-radius;

    &-log-entry {
      margin-bottom: $l-spacing-1 *2;
      word-wrap: break-word;
    }

  }
}
</style>
