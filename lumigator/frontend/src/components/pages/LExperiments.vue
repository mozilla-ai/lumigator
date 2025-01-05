<template>
  <div
    class="l-experiments"
    :class="{'no-data':experiments.length === 0}"
  >
    <l-experiments-empty
      v-if="experiments.length === 0"
      @l-add-experiment="onCreateExperiment()"
    />
    <div
      v-if="experiments.length > 0"
      class="l-experiments__header-container"
    >
      <l-page-header
        :title="t('experiments.header.title')"
        :description="t('experiments.header.description')"
        :button-label="t('experiments.header.createExperiment')"
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
      <transition name="transition-fade">
        <l-experiment-form
          v-if="showSlidingPanel && selectedExperiment === null"
          @l-close-form="onDismissForm"
        />
      </transition>
      <transition name="transition-fade">
        <l-experiment-details
          v-if="selectedExperiment !== null"
          @l-results="onShowResults($event)"
          @l-dnld-results="onDnldResults($event)"
          @l-show-logs="onShowLogs"
          @l-close-details="onCloseDetails"
        />
      </transition>
    </Teleport>
    <l-experiments-drawer
      v-if="showDrawer"
      ref="experimentsDrawer"
      :header="getDrawerHeader()"
      :position="showLogs ? 'bottom' : 'full'"
      @l-drawer-closed="resetDrawerContent()"
    >
      <l-experiment-results
        v-if="selectedExperimentRslts.length"
        :results="selectedExperimentRslts"
      />
      <l-experiment-logs
        v-if="selectedExperimentRslts.length === 0"
      />

    </l-experiments-drawer>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import { onMounted, watch, ref } from 'vue'
import { storeToRefs } from 'pinia';
import { useExperimentStore } from '@/stores/experiments/store'
import { useDatasetStore } from '@/stores/datasets/store'
import { useSlidePanel } from '@/composables/SlidingPanel';
import LPageHeader from '@/components/molecules/LPageHeader.vue';
import LExperimentTable from '@/components/molecules/LExperimentTable.vue';
import LExperimentForm from '@/components/molecules/LExperimentForm.vue';
import LExperimentDetails from '@/components/molecules/LExperimentDetails.vue';
import LExperimentsDrawer from '@/components/molecules/LExperimentsDrawer.vue';
import LExperimentResults from '@/components/molecules/LExperimentResults.vue';
import LExperimentLogs from '@/components/molecules/LExperimentLogs.vue';
import LExperimentsEmpty from '@/components/molecules/LExperimentsEmpty.vue'

const { t } = useI18n();
const { showSlidingPanel } = useSlidePanel();
const experimentStore = useExperimentStore();
const datasetStore = useDatasetStore();
const { selectedDataset } = storeToRefs(datasetStore);
const {
  experiments,
  selectedExperiment,
  selectedExperimentRslts
} = storeToRefs(experimentStore);

const showDrawer = ref(false);
const experimentsDrawer = ref(null);
const showLogs = ref(null);

const getDrawerHeader = () => {
  return showLogs.value ? 'Experiment Logs' : selectedExperiment.value.name;
};

const onCreateExperiment = () => {
  showSlidingPanel.value = true;
  selectedExperiment.value = null;
}

const onSelectExperiment = (experiment) => {
  experimentStore.loadDetails(experiment.id);
  showSlidingPanel.value = true;
}

const onShowResults = (experiment) => {
  experimentStore.loadResults(experiment.id);
  showDrawer.value = true;
}

const onDnldResults = (experiment) => {
  experimentStore.loadResultsFile(experiment.id);
}

const onShowLogs = () => {
  showLogs.value = true;
  showDrawer.value = true;
}

const onDismissForm = () => {
  selectedDataset.value = null;
  showSlidingPanel.value = false;
}

const onCloseDetails = () => {
  showSlidingPanel.value = false;
}

const resetDrawerContent = () => {
  selectedExperimentRslts.value = [];
  showLogs.value = false;
  showDrawer.value = false;
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
    place-content: center;

    .l-experiments__header-container {
      margin-top: 120px;
    }
  }
}
</style>
