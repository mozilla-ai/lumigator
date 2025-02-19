<template>
  <div class="l-experiments" :class="{ 'no-data': experiments.length === 0 }">
    <l-experiments-empty v-if="experiments.length === 0" @l-add-experiment="onCreateExperiment()" />
    <div v-if="experiments.length > 0" class="l-experiments__header-container">
      <l-page-header
        title="Experiments"
        :description="headerDescription"
        button-label="Create Experiment"
        :column="experiments.length === 0"
        @l-header-action="onCreateExperiment()"
      />
    </div>
    <div v-if="experiments.length > 0" class="l-experiments__table-container">
      <l-experiment-table
        :table-data="experiments"
        @l-experiment-selected="onSelectExperiment($event)"
      />
    </div>
    <Teleport to=".sliding-panel">
      <transition name="transition-fade">
        <l-experiment-form v-if="isFormVisible" @l-close-form="onDismissForm" />
      </transition>
      <transition name="transition-fade">
        <l-experiment-details
          v-if="selectedExperiment"
          title="Experiment Details"
          @l-experiment-results="onShowExperimentResults($event)"
          @l-job-results="onShowJobResults($event)"
          @l-download-results="onDownloadResults($event)"
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
      <l-experiment-results v-if="showExpResults" />
      <l-job-results
        v-if="selectedWorkflowResults && showJobResults && selectedWorkflowResults.length"
        :results="selectedWorkflowResults"
      />
      <l-experiment-logs :logs="workflowLogs" v-if="showLogs" />
    </l-experiments-drawer>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, watch, ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useExperimentStore } from '@/stores/experimentsStore'
import { useDatasetStore } from '@/stores/datasetsStore'
import { useModelStore } from '@/stores/modelsStore'
import { useSlidePanel } from '@/composables/useSlidePanel'
import LPageHeader from '@/components/layout/LPageHeader.vue'
import LExperimentTable from '@/components/experiments/LExperimentTable.vue'
import LExperimentForm from '@/components/experiments/LExperimentForm.vue'
import LExperimentDetails from '@/components/experiments/LExperimentDetails.vue'
import LExperimentsDrawer from '@/components/experiments/LExperimentsDrawer.vue'
import LExperimentResults from '@/components/experiments/LExperimentResults.vue'
import LJobResults from '@/components/experiments/LJobResults.vue'
import LExperimentLogs from '@/components/experiments/LExperimentLogs.vue'
import LExperimentsEmpty from '@/components/experiments/LExperimentsEmpty.vue'
import type { Experiment } from '@/types/Experiment'
import type { Workflow } from '@/types/Workflow'

const { showSlidingPanel } = useSlidePanel()
const experimentStore = useExperimentStore()
const datasetStore = useDatasetStore()
const modelStore = useModelStore()
const { selectedDataset } = storeToRefs(datasetStore)
const { experiments, selectedExperiment, selectedWorkflow, selectedWorkflowResults, workflowLogs } =
  storeToRefs(experimentStore)

const showDrawer = ref(false)
const experimentsDrawer = ref()
const showLogs = ref()
const showExpResults = ref()
const showJobResults = ref()
const headerDescription = ref(`Experiments are a logical sequence of inference and
evaluation tasks that run sequentially to evaluate an LLM.`)

const isFormVisible = computed(() => showSlidingPanel.value && !selectedExperiment.value)

const getDrawerHeader = () => {
  return showLogs.value ? 'Logs' : selectedExperiment.value?.name
}

const onCreateExperiment = () => {
  showSlidingPanel.value = true
  selectedExperiment.value = undefined
}

const onSelectExperiment = (experiment: Experiment) => {
  experimentStore.loadExperimentDetails(experiment.id)
  showSlidingPanel.value = true
}

const onShowExperimentResults = (experiment: Experiment) => {
  experimentStore.fetchExperimentResults(experiment)
  showExpResults.value = true
  showDrawer.value = true
}

const onShowJobResults = (workflow: Workflow) => {
  experimentStore.fetchWorkflowResults(workflow)
  showDrawer.value = true
  showJobResults.value = true
}

const onDownloadResults = (workflow: Workflow | Experiment) => {
  experimentStore.fetchExperimentResultsFile(workflow.id)
}

const onShowLogs = () => {
  showLogs.value = true
  showDrawer.value = true
}

const onDismissForm = () => {
  datasetStore.setSelectedDataset(undefined)
  showSlidingPanel.value = false
}

const onCloseDetails = () => {
  showSlidingPanel.value = false
}

const resetDrawerContent = () => {
  selectedWorkflowResults.value = []
  showExpResults.value = false
  showJobResults.value = false
  showLogs.value = false
  showDrawer.value = false
}

onMounted(async () => {
  await Promise.all([experimentStore.fetchAllExperiments(), modelStore.fetchModels()])

  if (selectedDataset.value) {
    onCreateExperiment()
  }
})

watch(showSlidingPanel, (newValue) => {
  if (!newValue) {
    selectedExperiment.value = undefined
    selectedWorkflow.value = undefined
  }
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-experiments {
  $root: &;
  max-width: $l-main-width;
  margin: 0 auto;

  &__header-container {
    margin: auto;
    padding: $l-spacing-1;
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
