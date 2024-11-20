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

const onSelectExperiment = (experiment) => {
  experimentStore.loadDetails(experiment.id);
}

onMounted(async () => {
  await experimentStore.loadExperiments();
})
</script>

<style scoped lang="scss">
.l-experiments {
  $root: &;
  max-width: $l-main-width;
  margin: 0 auto;

  &__header-container {
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
    display: grid;
    place-items: center;
  }
}
</style>
