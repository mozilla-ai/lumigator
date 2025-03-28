<template>
  <div class="l-experiment-table">
    <transition name="transition-fade" mode="out-in">
      <TableView
        style="width: 100%"
        v-if="tableVisible"
        :sortOrder="-1"
        :isLoading="isLoading"
        :sortField="'created_at'"
        :columns="columns"
        :data="tableData"
        @row-click="handleRowClick"
        :is-search-enabled="false"
        :has-column-toggle="false"
      >
        <template #options="slotProps">
          <Button
            icon="pi pi-trash"
            @click="handleDeleteExperimentClicked(slotProps.data)"
            severity="secondary"
            variant="text"
            rounded
            aria-label="Delete"
          ></Button>
          <Button
            icon="pi pi-download"
            @click="handleDownloadResultsClicked(slotProps.data)"
            severity="secondary"
            variant="text"
            rounded
            disabled
            aria-label="Download Results"
          ></Button>
          <Button
            icon="pi pi-chart-bar"
            @click="handleViewResultsClicked(slotProps.data)"
            severity="secondary"
            variant="text"
            :disabled="
              slotProps.data.status !== WorkflowStatus.INCOMPLETE &&
              slotProps.data.status !== WorkflowStatus.SUCCEEDED
            "
            rounded
            aria-label="View results"
          ></Button>
        </template>
      </TableView>
    </transition>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onMounted, type PropType, onBeforeUnmount } from 'vue'
import { storeToRefs } from 'pinia'
import { type DataTableRowClickEvent } from 'primevue/datatable'

import { useExperimentStore } from '@/stores/experimentsStore'
import { formatDate } from '@/helpers/formatDate'
import { WorkflowStatus } from '@/types/Workflow'
import type { Experiment } from '@/types/Experiment'
import { workflowsService } from '@/sdk/workflowsService'
import { retrieveStatus } from '@/helpers/retrieveStatus'
import { Button } from 'primevue'
import TableView from '../common/TableView.vue'
import { useDatasetStore } from '@/stores/datasetsStore'
const props = defineProps({
  experiments: {
    type: Array as PropType<Experiment[]>,
    required: true,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
})

const datasetStore = useDatasetStore()
const { datasets } = storeToRefs(datasetStore)

const tableData = computed(() => {
  return props.experiments.map((experiment) => {
    return {
      ...experiment,
      dataset:
        datasets.value.find((dataset) => dataset.id === experiment.dataset)?.filename ||
        experiment.dataset,
      created_at: formatDate(experiment.created_at),
      use_case: experiment.task_definition.task,
    }
  })
})

const columns = ['name', 'dataset', 'use_case', 'created_at', 'status', 'options']

const emit = defineEmits([
  'l-experiment-selected',
  'l-workflow-selected',
  'delete-option-clicked',
  'view-experiment-results-clicked',
  'view-workflow-results-clicked',
])

const isThrottled = ref(false)
const experimentStore = useExperimentStore()
const { experiments: allExperiments } = storeToRefs(experimentStore)
const tableVisible = ref(true)
const completedStatus = [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]

const handleDeleteExperimentClicked = (experiment: Experiment) => {
  emit('delete-option-clicked', experiment)
}
const handleDownloadResultsClicked = (experiment: Experiment) => {
  console.log('Download results clicked', experiment)
}
const handleViewResultsClicked = (experiment: Experiment) => {
  emit('view-experiment-results-clicked', experiment)
}

function handleRowClick(event: DataTableRowClickEvent) {
  emit('l-experiment-selected', event.data)
}

/**
 * The retrieved IDs will determine which experiment is still Running
 * @returns {string[]} IDs of stored experiments that have not completed
 */
function getIncompleteExperiments(): Experiment[] {
  return allExperiments.value.filter(
    (experiment: Experiment) => !completedStatus.includes(experiment.status),
  )
}

/**
 *
 * @param {string} id - String (UUID) representing the experiment which should be updated with the latest status
 */
async function updateExperimentStatus(experiment: Experiment): Promise<void> {
  try {
    const incompleteWorkflows = experiment.workflows.filter(
      (workflow) => !completedStatus.includes(workflow.status),
    )

    const incompleteWorkflowDetails = await Promise.all(
      incompleteWorkflows.map((workflow) => workflowsService.fetchWorkflowDetails(workflow.id)),
    )

    incompleteWorkflowDetails.forEach((workflow) => {
      // TODO: immutability would be nice
      const existingWorkflow = experiment.workflows.find((w) => w.id === workflow.id)
      if (existingWorkflow) {
        existingWorkflow.status = workflow.status
        existingWorkflow.artifacts_download_url = workflow.artifacts_download_url
      }
    })

    const status =
      incompleteWorkflowDetails.length &&
      incompleteWorkflowDetails.every((workflow) => completedStatus.includes(workflow.status))
        ? incompleteWorkflowDetails[0].status
        : retrieveStatus(experiment)

    // const e = experiments.value.find((exp) => exp.id === experiment.id)
    // if (e) {
    // e.status = status
    experiment.status = status
    // }
  } catch (error) {
    console.error(`Failed to update status for exp ${experiment} ${error}`)
  }
}

/**
 * Updates the status for stored experiments that are not completed
 */
async function updateStatusForIncompleteExperiments() {
  await Promise.all(
    getIncompleteExperiments().map((experiment) => updateExperimentStatus(experiment)),
  )
}

// Throttle ensures the function is invoked at most once every defined period.
async function throttledUpdateAllWorkflows() {
  if (isThrottled.value) {
    return
  } // Skip if throttle is active

  isThrottled.value = true
  await updateStatusForIncompleteExperiments()
  setTimeout(() => {
    isThrottled.value = false // Release throttle after delay
  }, 5000) // 5 seconds throttle
}

// This is a temporary solution until 'experiments/' endpoint
// updates the status of each experiment
let pollingId: number | undefined
onMounted(async () => {
  await updateStatusForIncompleteExperiments()
  pollingId = setInterval(async () => {
    await throttledUpdateAllWorkflows()
  }, 1000)
}) // Check every second, throttled to execute every 5 seconds

onBeforeUnmount(() => {
  clearInterval(pollingId)
})

watch(
  () => props.experiments.length,
  async () => {
    await updateStatusForIncompleteExperiments()
  },
)
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-experiment-table {
  width: 100%;
  display: flex;
  // place-content: center;

  &__tag {
    color: $l-grey-100;
    font-size: $l-font-size-sm;
    line-height: 1;
    font-weight: $l-font-weight-normal;
    text-transform: uppercase;
  }
}
</style>
