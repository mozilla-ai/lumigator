<template>
  <div class="l-experiments">
    <div class="l-experiments__header-container">
      <l-page-header
        title="Experiments"
        button-label="Create Experiment"
        @l-header-action="onCreateExperiment()"
      />
    </div>
    <div
      v-if="experiments.length > 0"
      class="l-experiments__table-container"
    >
      <l-experiment-table :table-data="experiments" />
    </div>
    <Teleport to=".sliding-panel">
      <transition name="transtion-fade">
        <l-experiment-form
          v-if="showSlidingPanel"
          @l-close-form="showSlidingPanel= false"
        />
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia';
import { useSlidePanel } from '@/composables/SlidingPanel';
import LPageHeader from '@/components/molecules/LPageHeader.vue';
import LExperimentTable from '@/components/molecules/LExperimentTable.vue';
import LExperimentForm from '@/components/molecules/LExperimentForm.vue';
import { useExperimentStore } from '@/stores/experiments/store'

const { showSlidingPanel } = useSlidePanel();
const experimentStore = useExperimentStore();
const { experiments } = storeToRefs(experimentStore);

const onCreateExperiment = () => {
  showSlidingPanel.value = true;
}
onMounted(async () => {
  await experimentStore.loadExperiments();
})
</script>

<style scoped>
.l-experiments {
	display: grid;
	place-items: center;
}
</style>
