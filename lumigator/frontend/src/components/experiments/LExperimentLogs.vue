<template>
  <div class="l-experiment-logs">
    <div ref="logContainer" class="l-experiment-logs__container" @scroll.passive="onScroll">
      <div v-for="(log, index) in logs" :key="index" class="l-experiment-logs__container-log-entry">
        {{ log }}
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, computed, nextTick, type Ref, toRefs, onMounted } from 'vue'

const props = defineProps<{ logs: string[] }>()

const { logs } = toRefs(props)

const logContainer: Ref<HTMLElement | undefined> = ref()

const logsLength = computed(() => logs.value.length)
const isAutoScrollEnabled = ref(true)

const scrollToBottom = async () => {
  if (logContainer.value && isAutoScrollEnabled.value) {
    // wait for view to update the DOM with new logs
    await nextTick()

    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

const onScroll = () => {
  if (logContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = logContainer.value
    const isAtBottom = scrollHeight - scrollTop <= clientHeight + 5

    // resume autoscrolling only if at the bottom
    isAutoScrollEnabled.value = isAtBottom
  }
}
onMounted(() => {
  scrollToBottom()
})

watch(logsLength, scrollToBottom)
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

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
      margin-bottom: $l-spacing-1;
      word-wrap: break-word;
    }
  }
}
</style>
