<template>
  <div class="l-experiments">
    <div class="l-experiments__header-container">
      <l-page-header
        title="Experiments"
        button-label="Create Experiment"
        @l-header-action="onCreateExperiment()"
      />
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
import { useSlidePanel } from '@/composables/SlidingPanel';
import LPageHeader from '@/components/molecules/LPageHeader.vue';
import LExperimentForm from '@/components/molecules/LExperimentForm.vue';
import { useDatasetStore } from '@/stores/datasets/store'


const { showSlidingPanel } = useSlidePanel();
const datasetStore = useDatasetStore();

const onCreateExperiment = () => {
  showSlidingPanel.value = true;
}
onMounted(async () => {
  await datasetStore.loadDatasets();

})
</script>

<style scoped>
.l-experiments {
	display: grid;
	place-items: center;
}
</style>
