<template>
  <div id="app">
    <div class="header">
      <l-health-status />
    </div>
    <div class="content-wrapper">
      <div class="l-menu-container">
        <l-menu />
      </div>
      <div class="l-main-container">
        <router-view v-slot="{ Component }">
          <transition name="transition-fade" mode="out-in">
            <component
              :is="Component"
              @s-disable-scroll="disableScroll = $event"
            />
          </transition>
        </router-view>
      </div>
      <div class="sliding-panel"
           :class="{ open: showSlidingPanel }"
      >
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import LMenu from '@/components/organisms/LMenu.vue';
import LHealthStatus from '@/components/molecules/LHealthStatus.vue';
import { useDatasetStore } from '@/stores/datasets/store'
import { useExperimentStore } from '@/stores/experiments/store'
import { useSlidePanel } from '@/composables/SlidingPanel';

const datasetStore = useDatasetStore();
const experimentStore = useExperimentStore();

const { showSlidingPanel } = useSlidePanel();
onMounted(async () => {
  await experimentStore.loadExperiments();
  await datasetStore.loadDatasets();
})
</script>

<style scoped lang="scss">
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: $l-main-bg;
  padding: $l-spacing-1;

  .header {
    background-color: $l-main-bg;
  }

  .content-wrapper {
    display: flex;
    gap: 1rem;
    flex: 1;
    overflow: hidden;
  }

  .l-menu-container {
    height: 90vh;
    width: minmax(200px, 15%);
    background-color: $l-main-bg;
  }

  .l-main-container {
    flex: 1;
    background-color: $l-card-bg;
    transition: margin-right 0.3s ease-in-out;
    background-color: $l-card-bg;
    border-radius: $l-main-radius;
    display: grid;
    text-align: center;
  }

  .sliding-panel {
    width: 0;
    background-color: $l-main-bg;
    transition: width 0.3s ease-in-out;
    overflow: hidden;
  }

  .sliding-panel.open {
    width: $l-sliding-panel-size;
    overflow-y: auto;
  }

  .l-main-container {
    transition: flex-grow 0.3s, margin-right 0.3s;
  }

  .sliding-panel.open+.l-main-container {
    margin-right: 0;
  }
}
</style>
