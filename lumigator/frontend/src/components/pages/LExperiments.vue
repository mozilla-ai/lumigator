<template>
  <div
    class="l-experiments"
    :class="{'no-data':experiments.length === 0}"
  >
    <div class="l-experiments__header-container">
      <l-page-header
        title="Experiments"
        button-label="Create Experiment"
        :column="experiments.length === 0"
        @l-header-action="onCreateExperiment()"
      />
    </div>
    <div
      v-if="experiments.length > 0"
      class="l-experiments__table-container"
    >
      <l-experiment-table
        :table-data="experiments"
        @l-experiment-selected="onSelectExperiment($event)"
      />
    </div>
    <Teleport to=".sliding-panel">
      <transition name="transtion-fade">
        <l-experiment-form
          v-if="showSlidingPanel && selectedExperiment === null"
          @l-close-form="onDismissForm"
        />
      </transition>
      <transition name="transtion-fade">
        <l-experiment-details
          v-if="showSlidingPanel && selectedExperiment !== null"
          @l-close-details="onCloseDetails"
        />
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia';
import { useExperimentStore } from '@/stores/experiments/store'
import { useDatasetStore } from '@/stores/datasets/store'
import { useSlidePanel } from '@/composables/SlidingPanel';
import LPageHeader from '@/components/molecules/LPageHeader.vue';
import LExperimentTable from '@/components/molecules/LExperimentTable.vue';
import LExperimentForm from '@/components/molecules/LExperimentForm.vue';
import LExperimentDetails from '@/components/molecules/LExperimentDetails.vue';

const { showSlidingPanel } = useSlidePanel();
const experimentStore = useExperimentStore();
const datasetStore = useDatasetStore();
const { selectedDataset } = storeToRefs(datasetStore);
const { experiments, selectedExperiment } = storeToRefs(experimentStore);

const onCreateExperiment = () => {
  showSlidingPanel.value = true;
  selectedExperiment.value = null;
}

const onSelectExperiment = (experiment) => {
  experimentStore.loadDetails(experiment.id);
  showSlidingPanel.value = true;
}

const onDismissForm = () => {
  selectedDataset.value = null;
  showSlidingPanel.value = false;
}

const onCloseDetails = () => {
  showSlidingPanel.value = false;
}

onMounted(async () => {
   if (selectedDataset.value) {
     onCreateExperiment();
  }
})

watch(showSlidingPanel, () => {
  selectedExperiment.value = null;
});
</script>

<style scoped lang="scss">
.l-experiments {
  $root: &;
  max-width: $l-main-width;
  margin: 0 auto;

  &__header-container {
    margin: auto;
    padding:$l-spacing-1;
    display: grid;
    place-items: center;
    width: 100%;
  }

  &__table-container {
		padding: $l-spacing-1;
    display: grid;
    width: 100%;
  }
  &.no-data {
    max-width: $l-main-width;
    padding: $l-spacing-1;
    display: grid;
    place-items: start;

    .l-experiments__header-container {
      margin-top: 120px;
    }
  }
}
</style>
