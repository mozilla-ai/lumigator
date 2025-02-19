<template>
  <div class="l-experiment-table">
    <transition name="transition-fade" mode="out-in">
      <DataTable
        v-if="tableVisible"
        v-model:selection="focusedItem"
        v-model:expandedRows="expandedRows"
        selectionMode="single"
        data-key="id"
        :value="tableData"
        :tableStyle="style"
        columnResizeMode="expand"
        sortField="created"
        :sortOrder="-1"
        scrollable
        scrollHeight="80vh"
        :pt="{ table: 'table-root' }"
        @row-click="handleRowClick"
      >
        <Column expander :style="columnStyles.expander" />
        <Column field="name" :style="columnStyles.name" header="experiment title" />
        <Column field="created" header="created" sortable :style="columnStyles.created">
          <template #body="slotProps">
            {{ formatDate(slotProps.data.created_at) }}
          </template>
        </Column>
        <Column field="status" header="status">
          <template #body="slotProps">
            <div>
              <Tag
                v-if="retrieveStatus(slotProps.data) === WorkflowStatus.SUCCEEDED"
                severity="success"
                rounded
                :value="retrieveStatus(slotProps.data)"
                :pt="{ root: 'l-experiment-table__tag' }"
              />
              <Tag
                v-else-if="retrieveStatus(slotProps.data) === WorkflowStatus.FAILED"
                severity="danger"
                rounded
                :value="retrieveStatus(slotProps.data)"
                :pt="{ root: 'l-experiment-table__tag' }"
              />
              <Tag
                v-else-if="retrieveStatus(slotProps.data) === WorkflowStatus.INCOMPLETE"
                severity="info"
                rounded
                :value="retrieveStatus(slotProps.data)"
                :pt="{ root: 'l-experiment-table__tag' }"
              />
              <Tag
                v-else
                severity="warn"
                rounded
                :value="retrieveStatus(slotProps.data)"
                :pt="{ root: 'l-experiment-table__tag' }"
              />
            </div>
          </template>
        </Column>
        <Column header="options">
          <template #body>
            <span
              class="pi pi-fw pi-ellipsis-h l-experiment-table__options-trigger"
              style="cursor: not-allowed; pointer-events: all"
              aria-controls="optionsMenu"
            >
            </span>
          </template>
        </Column>
        <template #expansion="slotProps">
          <div class="l-experiment-table__jobs-table-container">
            <l-jobs-table
              :column-styles="columnStyles"
              :table-data="slotProps.data.workflows"
              @l-job-selected="onWorkflowSelected($event, slotProps.data)"
            />
          </div>
        </template>
      </DataTable>
    </transition>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onMounted, type PropType, onBeforeUnmount } from 'vue'
import { storeToRefs } from 'pinia'
import DataTable, { type DataTableRowClickEvent } from 'primevue/datatable'
import Column from 'primevue/column'

import { useSlidePanel } from '@/composables/useSlidePanel'
import Tag from 'primevue/tag'
import LJobsTable from '@/components/experiments/LJobsTable.vue'
import { useExperimentStore } from '@/stores/experimentsStore'
import { formatDate } from '@/helpers/formatDate'
import { WorkflowStatus, type Workflow } from '@/types/Workflow'
import type { Experiment } from '@/types/Experiment'
import { workflowsService } from '@/sdk/workflowsService'
const props = defineProps({
  tableData: {
    type: Array as PropType<Experiment[]>,
    required: true,
  },
})
const emit = defineEmits(['l-experiment-selected', 'l-workflow-selected'])

const isThrottled = ref(false)
const { showSlidingPanel } = useSlidePanel()
const experimentStore = useExperimentStore()
const { experiments } = storeToRefs(experimentStore)
const tableVisible = ref(true)
const focusedItem = ref()
const expandedRows = ref([])
const completedStatus = [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]

const style = computed(() => {
  return showSlidingPanel.value ? 'width: 100%;' : 'min-width: min(80vw, 1200px);max-width:1300px'
})

const columnStyles = computed(() => {
  return {
    expander: 'width: 4rem',
    name: showSlidingPanel.value ? 'width: 20rem' : 'width: 26rem',
    created: 'width: 12rem',
  }
})

function handleRowClick(event: DataTableRowClickEvent) {
  if (
    (event.originalEvent.target as HTMLElement)?.closest('svg.p-icon.p-datatable-row-toggle-icon')
  ) {
    // preventing experiment selection on row expansion
    return
  }
  // user selected an experiment, clear selected job
  emit('l-workflow-selected', undefined)
  emit('l-experiment-selected', event.data)
}

function onWorkflowSelected(workflow: Workflow, experiment: Experiment) {
  // fetching job details from BE instead of filtering
  // because job might be still running
  // const inferenceJob = workflow.jobs.find((job: JobResult) => job.metrics?.length > 0)
  if (workflow.jobs) {
    workflowsService.fetchWorkflowDetails(workflow.id)
    emit('l-workflow-selected', workflow)
  }
  // select the experiment that job belongs to
  emit('l-experiment-selected', experiment)
}

// aggregates the experiment's status based on its workflows statuses
function retrieveStatus(experiment: Experiment): WorkflowStatus {
  const workflowStatuses = experiment.workflows.map((workflow) => workflow.status)
  const uniqueStatuses = new Set(workflowStatuses)

  if (uniqueStatuses.has(WorkflowStatus.RUNNING)) {
    return WorkflowStatus.RUNNING
  } else if (
    uniqueStatuses.has(WorkflowStatus.FAILED) &&
    uniqueStatuses.has(WorkflowStatus.SUCCEEDED)
  ) {
    return WorkflowStatus.INCOMPLETE
  } else {
    // if none of its workflows are running, or if some failed and others succeeded, then it probably means they all have the same status so just return it
    return [...uniqueStatuses][0]
  }
}

/**
 * The retrieved IDs will determine which experiment is still Running
 * @returns {string[]} IDs of stored experiments that have not completed
 */
function getIncompleteExperiments(): Experiment[] {
  return experiments.value.filter(
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
      const existingWorkflow = experiment.workflows.find((w) => w.id === workflow.id)
      if (existingWorkflow) {
        existingWorkflow.status = workflow.status
      }
    })

    const status = incompleteWorkflowDetails.every((workflow) =>
      completedStatus.includes(workflow.status),
    )
      ? WorkflowStatus.SUCCEEDED
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

watch(showSlidingPanel, (newValue) => {
  focusedItem.value = newValue ? focusedItem.value : undefined
})

watch(
  () => props.tableData.length,
  async () => {
    await updateStatusForIncompleteExperiments()
  },
)
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-experiment-table {
  $root: &;
  width: 100%;
  display: flex;
  place-content: center;

  &__options-trigger {
    padding-left: $l-spacing-1;
    margin-left: 10% !important;
  }

  &__tag {
    color: $l-grey-100;
    font-size: $l-font-size-sm;
    line-height: 1;
    font-weight: $l-font-weight-normal;
    text-transform: uppercase;
  }
}
</style>
