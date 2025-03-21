<template>
  <div class="l-datasets" :class="{ 'is-empty': !datasets || datasets.length === 0 }">
    <div v-if="datasets.length > 0" class="l-datasets__header-container">
      <l-page-header
        title="Datasets"
        :description="headerDescription"
        subtitle="Only CSV files are currently supported."
        button-label="Provide Dataset"
        @l-header-action="handleAddDatasetClicked()"
      />
    </div>
    <l-dataset-empty v-else @l-add-dataset="handleAddDatasetClicked()" />
    <div v-if="datasets.length > 0" class="l-datasets__table-container">
      <Tabs v-model:value="currentTab" @update:value="showSlidingPanel = false">
        <TabList>
          <Tab value="0">All Datasets</Tab>
          <Tab value="1">
            <div :class="{ 'is-running': hasRunningInferenceJob }">
              <span>Ground Truth Jobs</span>
            </div>
          </Tab>
        </TabList>
        <TabPanels>
          <TabPanel value="0">
            <LDatasetTable
              v-if="datasets.length"
              :isLoading="isDatasetsLoading || isDatasetsFetching"
              :table-data="datasets"
              @l-dataset-selected="onDatasetSelected($event)"
              @use-in-experiment-clicked="handleUseInExperimentClicked($event)"
              @l-download-dataset="handleDownloadDatasetClicked($event)"
              @l-delete-dataset="handleDeleteDatasetClicked($event)"
              @view-dataset-clicked="handleViewDatasetClicked"
            />
          </TabPanel>
          <TabPanel value="1">
            <l-inference-jobs-table
              :table-data="inferenceJobs"
              @l-inference-selected="onInferenceJobSelected($event)"
              @l-inference-finished="reloadDatasetTable"
            />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>
    <l-file-upload ref="datasetInput" entity="dataset" @l-file-upload="uploadDataset($event)" />
    <DatasetViewer
      v-if="isDatasetViewerVisible"
      :downloadFileName="selectedDataset?.filename.split('.')[0] || 'download'"
      :data="datasetFileContent"
      :isEditable="false"
      :isSearchEnabled="true"
      :showRowNumber="true"
      :columns="datasetColumns"
      @close="isDatasetViewerVisible = false"
    >
      <template #title>
        <h3 class="dataset-title">
          <span style="color: #888888">Dataset:</span> {{ selectedDataset?.filename }}
        </h3>
      </template>
    </DatasetViewer>
    <Teleport to=".sliding-panel">
      <l-dataset-details
        v-if="selectedDataset"
        @use-in-experiment-clicked="handleUseInExperimentClicked($event)"
        @l-generate-gt="onGenerateGT()"
        @l-details-closed="onClearSelection()"
        @l-delete-dataset="handleDeleteDatasetClicked($event)"
        @l-download-dataset="handleDownloadDatasetClicked($event)"
        @view-dataset-clicked="handleViewDatasetClicked"
      />
      <l-job-details
        v-if="showSlidingPanel && selectedJob"
        title="Job Details"
        :selectedJob="selectedJob"
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
      <l-experiment-logs v-if="showLogs" :logs="jobLogs" />
    </l-experiments-drawer>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, type Ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasetsStore'
import { useSlidePanel } from '@/composables/useSlidePanel'
import { useRouter } from 'vue-router'
import LPageHeader from '@/components/layout/LPageHeader.vue'
import LDatasetTable from '@/components/datasets/LDatasetTable.vue'
import LFileUpload from '@/components/common/LFileUpload.vue'
import LDatasetEmpty from '@/components/datasets/LDatasetEmpty.vue'
import LDatasetDetails from '@/components/datasets/LDatasetDetails.vue'
import LInferenceJobsTable from '@/components/datasets/LInferenceJobsTable.vue'
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
import LJobDetails from '../datasets/LJobDetails.vue'
import type { Job } from '@/types/Job'
import { jobsService } from '@/sdk/jobsService'
import { WorkflowStatus } from '@/types/Workflow'
import { datasetsService } from '@/sdk/datasetsService'
import { getAxiosError } from '@/helpers/getAxiosError'
import type { AxiosError } from 'axios'
import { downloadContent } from '@/helpers/downloadContent'
import Papa from 'papaparse'
import DatasetViewer from '../common/DatasetViewer.vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'

const datasetStore = useDatasetStore()
const {
  datasets,
  selectedDataset,
  inferenceJobs,
  hasRunningInferenceJob,
  isDatasetsLoading,
  isDatasetsFetching,
} = storeToRefs(datasetStore)
const selectedJob: Ref<Job | undefined> = ref()
const { showSlidingPanel } = useSlidePanel()
const toast = useToast()
const datasetInput = ref()
const confirm = useConfirm()
const router = useRouter()
const currentTab = ref('0')
const showLogs = ref(false)
const jobLogs: Ref<string[]> = ref([])
const isPollingForJobLogs = ref(false)
let jobLogsInterval: number | undefined = undefined
const datasetFileContent = ref()
const datasetColumns = ref()
const isDatasetViewerVisible = ref(false)

console.log({ isDatasetsFetching, isDatasetsLoading })
const queryClient = useQueryClient()

const uploadDatasetMutation = useMutation({
  mutationFn: datasetsService.postDataset,
  onMutate: () => {
    toast.add({
      severity: 'info',
      summary: 'Uploading dataset...',
      messageicon: 'pi pi-upload',
      group: 'br',
      life: 3000,
    } as ToastMessageOptions & { messageicon: string })
  },
  onError: (error) => {
    const errorMessage = getAxiosError(error as Error | AxiosError)
    toast.add({
      severity: 'error',
      summary: `${errorMessage}`,
      messageicon: 'pi pi-exclamation-triangle',
      group: 'br',
    } as ToastMessageOptions & { messageicon: string })
  },
  onSuccess: async () => {
    toast.add({
      severity: 'success',
      summary: 'Dataset uploaded',
      messageicon: 'pi pi-check',
      life: 3000,
      group: 'br',
    } as ToastMessageOptions & { messageicon: string })
    await queryClient.invalidateQueries({
      queryKey: ['datasets'],
    })
  },
})

const deleteDatasetMutation = useMutation({
  mutationFn: datasetsService.deleteDataset,
  onMutate: () => {
    toast.add({
      severity: 'info',
      summary: 'Deleting dataset...',
      messageicon: 'pi pi-trash',
      group: 'br',
      life: 3000,
    } as ToastMessageOptions & { messageicon: string })
  },
  onError: (error) => {
    const errorMessage = getAxiosError(error as Error | AxiosError)
    toast.add({
      severity: 'error',
      summary: `${errorMessage}`,
      messageicon: 'pi pi-exclamation-triangle',
      group: 'br',
    } as ToastMessageOptions & { messageicon: string })
  },
  onSuccess: async () => {
    toast.add({
      severity: 'success',
      summary: 'Dataset deleted',
      messageicon: 'pi pi-check',
      group: 'br',
      life: 3000,
    } as ToastMessageOptions & { messageicon: string })
    await queryClient.invalidateQueries({
      queryKey: ['datasets'],
    })
  },
})

const downloadDatasetMutation = useMutation({
  mutationFn: (dataset: Dataset) => datasetsService.downloadDataset(dataset.id),
  onMutate: () => {
    toast.add({
      severity: 'info',
      summary: 'Downloading dataset...',
      messageicon: 'pi pi-download',
      group: 'br',
      life: 3000,
    } as ToastMessageOptions & { messageicon: string })
  },

  onError: (error) => {
    const errorMessage = getAxiosError(error as Error | AxiosError)
    toast.add({
      severity: 'error',
      summary: `${errorMessage}`,
      messageicon: 'pi pi-exclamation-triangle',
      group: 'br',
    } as ToastMessageOptions & { messageicon: string })
  },
  onSuccess: async (blob: Blob) => {
    if (selectedDataset.value) {
      downloadContent(blob, selectedDataset.value?.filename)
    }
  },
})

onMounted(async () => {
  await reloadDatasetTable()
})

const headerDescription = ref(`Use a dataset as the basis for your evaluation.
It includes data for the model you'd like to evaluate and possibly a ground truth "answer".`)

function handleDeleteDatasetClicked(dataset: Dataset) {
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
    accept: async () => {
      if (!dataset.id) {
        return
      }
      if (selectedDataset.value?.id === dataset.id) {
        datasetStore.setSelectedDataset(undefined)
      }
      await deleteDatasetMutation.mutate(dataset.id)
      if (!selectedDataset.value && showSlidingPanel.value) {
        showSlidingPanel.value = false
      }
    },
    reject: () => {},
  })
}

function startPollingForAnnotationJobLogs() {
  jobLogs.value = []
  if (!isPollingForJobLogs.value) {
    isPollingForJobLogs.value = true
    retrieveJobLogs()
    // Poll every 3 seconds
    jobLogsInterval = setInterval(retrieveJobLogs, 3000)
  }
}

async function retrieveJobLogs() {
  if (selectedJob.value) {
    const logsData = await jobsService.fetchLogs(selectedJob.value?.id)
    const logs = logsData.logs.split('\n')
    jobLogs.value = logs
  }
}

// start/stop polling for selected job (if its running) as the user clicks through them
watch(
  selectedJob,
  (newValue) => {
    jobLogs.value = []
    if (newValue) {
      retrieveJobLogs()
    }
    if (newValue?.status === WorkflowStatus.RUNNING) {
      startPollingForAnnotationJobLogs()
    } else if (isPollingForJobLogs.value) {
      stopPollingForAnnotationJobLogs()
    }
  },
  { deep: true },
)

function stopPollingForAnnotationJobLogs() {
  if (isPollingForJobLogs.value) {
    isPollingForJobLogs.value = false
    clearInterval(jobLogsInterval)
    jobLogsInterval = undefined
  }
}

async function handleViewDatasetClicked(dataset: Dataset) {
  datasetStore.setSelectedDataset(dataset)
  const blob = await datasetsService.downloadDataset(dataset.id)
  const text = await blob.text()

  // parse csv string into an array of arrays
  const data = Papa.parse(text, { skipEmptyLines: true }).data
  const columns: string[] = data[0]

  // transform parsed csv into DataTable props
  datasetColumns.value = columns
  datasetFileContent.value = data.slice(1, data.length).map((row: string[], rowIndex: number) => {
    return row.reduce((accum, value, index) => {
      return {
        ...accum,
        [columns[index]]: value,
        rowNumber: rowIndex + 1,
      }
    }, {})
  })

  isDatasetViewerVisible.value = true
}

async function handleDownloadDatasetClicked(dataset: Dataset) {
  datasetStore.setSelectedDataset(dataset)
  if (selectedDataset.value) {
    await downloadDatasetMutation.mutate(dataset)
  }
}

const handleAddDatasetClicked = () => {
  datasetInput.value.input.click()
}

const reloadDatasetTable = async () => {
  await datasetStore.fetchDatasets()
}

const uploadDataset = async (datasetFile: File) => {
  if (!datasetFile) {
    return
  }
  // Create a new FormData object and append the selected file and the required format
  const formData = new FormData()
  formData.append('dataset', datasetFile) // Attach the file
  formData.append('format', 'job') // Specification @localhost:8000/docs

  uploadDatasetMutation.mutate(formData, {})
  // refetch datasets after create
  await reloadDatasetTable()
}

async function fetchDatasetDetails(datasetID: string) {
  try {
    selectedDataset.value = await datasetsService.fetchDatasetInfo(datasetID)
  } catch {
    selectedDataset.value = undefined
  }
}

const onDatasetSelected = (dataset: Dataset) => {
  selectedJob.value = undefined
  fetchDatasetDetails(dataset.id)
  showSlidingPanel.value = true
}

const onClearSelection = () => {
  datasetStore.setSelectedDataset(undefined)
}

const handleUseInExperimentClicked = (dataset: Dataset) => {
  showSlidingPanel.value = false
  router.push('experiments')
  datasetStore.setSelectedDataset(dataset)
  fetchDatasetDetails(dataset.id)
}

const onInferenceJobSelected = (job: Job) => {
  datasetStore.setSelectedDataset(undefined)
  fetchJob(job.id)
  showSlidingPanel.value = true
}

async function fetchJob(id: string) {
  const jobData = await jobsService.fetchJob(id)
  selectedJob.value = datasetStore.parseJob(jobData)
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

<style lang="scss" scoped>
@use '@/styles/variables' as *;
@use '@/styles/mixins';

.l-datasets {
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

.dataset-title {
  @include mixins.paragraph;
  gap: 0.125rem;
  display: flex;
}
</style>
