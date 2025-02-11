<template>
  <div class="l-datasets" :class="{ 'is-empty': datasets.length === 0 || !datasets }">
    <div v-if="datasets.length > 0" class="l-datasets__header-container">
      <l-page-header
        title="Datasets"
        :description="headerDescription"
        subtitle="Only CSV files are currently supported."
        button-label="Provide Dataset"
        @l-header-action="onDatasetAdded()"
      />
    </div>
    <l-dataset-empty v-else @l-add-dataset="onDatasetAdded()" />
    <div v-if="datasets.length > 0" class="l-datasets__table-container">
      <Tabs v-model:value="currentTab" @update:value="showSlidingPanel = false">
        <TabList>
          <Tab value="0">All Datasets</Tab>
          <Tab value="1">
            <div :class="{ 'is-running': hasRunningInferenceJob }">
              <span>Groundtruth Jobs</span>
            </div>
          </Tab>
        </TabList>
        <TabPanels>
          <TabPanel value="0">
            <l-dataset-table
              v-if="datasets.length"
              ref="refDatasetTable"
              :table-data="datasets"
              @l-dataset-selected="onDatasetSelected($event)"
              @l-experiment="onExperimentDataset($event)"
              @l-download-dataset="onDownloadDataset($event)"
              @l-delete-dataset="deleteConfirmation($event)"
            />
          </TabPanel>
          <TabPanel value="1">
            <l-inference-jobs-table
              :table-data="inferenceJobs"
              @l-inference-selected="onJobInferenceSelected($event)"
              @l-inference-finished="reloadDatasetTable"
            />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>
    <l-file-upload ref="datasetInput" entity="dataset" @l-file-upload="onDatasetUpload($event)" />
    <Teleport to=".sliding-panel">
      <l-dataset-details
        v-if="selectedDataset"
        @l-experiment="onExperimentDataset($event)"
        @l-generate-gt="onGenerateGT()"
        @l-details-closed="onClearSelection()"
        @l-delete-dataset="deleteConfirmation($event)"
        @l-download-dataset="onDownloadDataset($event)"
      />
      <l-experiment-details
        v-if="showSlidingPanel && selectedJob"
        title="Job Details"
        @l-close-details="onCloseJobDetails"
        @l-show-logs="onShowLogs"
      />
    </Teleport>
    <l-experiments-drawer
      v-if="showLogs"
      ref="experimentsDrawer"
      header="Logs"
      :position="'bottom'"
      @l-drawer-closed="showLogs = false"
    >
      <l-experiment-logs v-if="showLogs" />
    </l-experiments-drawer>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasetsStore'
import { useExperimentStore } from '@/stores/experimentsStore'
import { useSlidePanel } from '@/composables/useSlidePanel'
import { useRouter } from 'vue-router'
import LPageHeader from '@/components/layout/LPageHeader.vue'
import LDatasetTable from '@/components/datasets/LDatasetTable.vue'
import LFileUpload from '@/components/common/LFileUpload.vue'
import LDatasetEmpty from '@/components/datasets/LDatasetEmpty.vue'
import LDatasetDetails from '@/components/datasets/LDatasetDetails.vue'
import LInferenceJobsTable from '@/components/datasets/LInferenceJobsTable.vue'
import LExperimentDetails from '@/components/experiments/LExperimentDetails.vue'
import LExperimentsDrawer from '@/components/experiments/LExperimentsDrawer.vue'
import LExperimentLogs from '@/components/experiments/LExperimentLogs.vue'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'

import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import type { ToastMessageOptions } from 'primevue'
import type { Dataset } from '@/types/Dataset'
import type { Job } from '@/types/Experiment'

const datasetStore = useDatasetStore()
const { datasets, selectedDataset } = storeToRefs(datasetStore)
const experimentStore = useExperimentStore()
const { inferenceJobs, selectedJob, hasRunningInferenceJob } = storeToRefs(experimentStore)
const { showSlidingPanel } = useSlidePanel()
const toast = useToast()
const datasetInput = ref()
const confirm = useConfirm()
const router = useRouter()
const currentTab = ref('0')
const showLogs = ref(false)
const refDatasetTable = ref()

onMounted(async () => {
  await datasetStore.fetchDatasets()
})

const headerDescription = ref(`Use a dataset as the basis for your evaluation.
It includes data for the model you'd like to evaluate and possibly a ground truth "answer".`)

function deleteConfirmation(dataset: Dataset) {
  confirm.require({
    message: `${dataset.filename}`,
    header: 'Delete  dataset?',
    icon: 'pi pi-info-circle',
    rejectLabel: 'Cancel',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true,
    },
    acceptProps: {
      label: 'Delete',
      severity: 'danger',
    },
    accept: () => {
      onDeleteDataset(dataset.id)
      if (!selectedDataset.value && showSlidingPanel.value) {
        showSlidingPanel.value = false
      }
      toast.add({
        severity: 'secondary',
        summary: `Dataset removed`,
        messageicon: 'pi pi-trash',
        detail: `${dataset.filename}`,
        group: 'br',
        life: 3000,
      } as ToastMessageOptions & { messageicon: string })
    },
    reject: () => {},
  })
}

function onDownloadDataset(dataset: Dataset) {
  selectedDataset.value = dataset
  datasetStore.downloadDatasetFile()
}

const onDatasetAdded = () => {
  datasetInput.value.input.click()
}

const reloadDatasetTable = () => {
  datasetStore.fetchDatasets()
  refDatasetTable.value.loading = true
  setTimeout(async () => {
    await datasetStore.fetchDatasets()
    refDatasetTable.value.loading = false
  }, 1500)
}

const onDatasetUpload = (datasetFile: File) => {
  datasetStore.uploadDataset(datasetFile)
}

const onDeleteDataset = (datasetID: string) => {
  datasetStore.deleteDataset(datasetID)
}

const onDatasetSelected = (dataset: Dataset) => {
  selectedJob.value = undefined
  datasetStore.fetchDatasetDetails(dataset.id)
  showSlidingPanel.value = true
}

const onClearSelection = () => {
  datasetStore.resetSelection()
}

const onExperimentDataset = (dataset: Dataset) => {
  router.push('experiments')
  selectedDataset.value = dataset
  datasetStore.fetchDatasetDetails(dataset.id)
}

const onJobInferenceSelected = (job: Job) => {
  selectedDataset.value = undefined
  experimentStore.fetchJobDetails(job.id)
  showSlidingPanel.value = true
}

const onCloseJobDetails = () => {
  showSlidingPanel.value = false
  selectedJob.value = undefined
}

const onShowLogs = () => {
  showLogs.value = true
}

const onGenerateGT = () => {
  showSlidingPanel.value = false
  currentTab.value = '1'
}
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-datasets {
  $root: &;
  max-width: $l-main-width;
  width: 100%;
  margin: 0 auto;

  &__header-container {
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
}

.is-empty {
  display: grid;
  place-content: center;
}
</style>

<style lang="scss">
@use '@/styles/variables' as *;

.l-datasets .p-tabs {
  $root: &;

  & .p-tablist {
    margin-bottom: $l-spacing-1;
  }

  & .p-tablist-tab-list {
    background: $l-card-bg !important;
    border-color: $l-main-bg;

    & .p-tab {
      padding-left: $l-spacing-1;
      padding-right: $l-spacing-1;
      border-color: $l-main-bg;

      &:hover {
        border-color: $l-main-bg;
      }
    }
  }

  .is-running::after {
    content: '';
    display: inline-block;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background-color: $l-primary-color;
    margin-left: 8px;
    margin-bottom: 2px;
    animation: pulse-dot 1.5s infinite ease-in-out;
  }
  @keyframes pulse-dot {
    0% {
      transform: scale(1);
      /* Start with no glow */
      color: rgba(255, 255, 0, 0.7);
    }
    50% {
      /* Dot grows in size slightly */
      transform: scale(1.2);
      /* Box-shadow expands outward for the glow effect */
      color: rgba(255, 255, 0, 0.7);
    }
    100% {
      transform: scale(1);
      /* Return to no glow */
      color: rgba(255, 255, 0, 0.7);
    }
  }
}
</style>
