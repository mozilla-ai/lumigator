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
        <Column field="status" header="status" :style="columnStyles.status">
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
          <template #body="slotProps">
            <span
              class="pi pi-fw pi-ellipsis-h l-experiment-table__options-trigger"
              style="pointer-events: all"
              aria-haspopup="true"
              aria-controls="optionsMenu"
              @click.stop="toggleOptionsMenu($event, slotProps.data)"
            >
            </span>
          </template>
        </Column>
        <Menu id="options_menu" ref="optionsMenu" :model="options" :popup="true"> </Menu>
        <template #expansion="slotProps">
          <div class="l-experiment-table__jobs-table-container">
            <l-jobs-table
              :column-styles="columnStyles"
              :table-data="slotProps.data.workflows"
              @l-job-selected="onWorkflowSelected($event, slotProps.data)"
              @view-workflow-results-clicked="$emit('view-workflow-results-clicked', $event)"
              @delete-workflow-clicked="$emit('delete-option-clicked', $event)"
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
import { retrieveStatus } from '@/helpers/retrieveStatus'
import type { MenuItem, MenuItemCommandEvent } from 'primevue/menuitem'
import { Menu } from 'primevue'
const props = defineProps({
  tableData: {
    type: Array as PropType<Experiment[]>,
    required: true,
  },
})

const emit = defineEmits(['l-experiment-selected', 'l-workflow-selected', 'delete-option-clicked', 'view-experiment-results-clicked', 'view-workflow-results-clicked'])

const isThrottled = ref(false)
const { showSlidingPanel } = useSlidePanel()
const experimentStore = useExperimentStore()
const { experiments } = storeToRefs(experimentStore)
const tableVisible = ref(true)
const focusedItem = ref()
const expandedRows = ref([])
const completedStatus = [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]

const optionsMenu = ref()
const options = ref<MenuItem[]>([
  {
    label: 'View Results',
    icon: 'pi pi-external-link',
    disabled: false,
    visible: () => {
      return focusedItem.value.status === WorkflowStatus.SUCCEEDED
    },
    command: () => {
      emit('view-experiment-results-clicked', focusedItem.value)
    },
  },
  {
    label: 'Download Results',
    icon: 'pi pi-download',
    disabled: false,
    visible: false,
    command: () => {
      // emit('l-download-experiment', focusedItem.value)
    },
  },
  {
    label: () => {
      return 'Delete Experiment'
    },
    icon: 'pi pi-trash',
    style: 'color: red; --l-menu-item-icon-color: red; --l-menu-item-icon-focus-color: red;',
    disabled: false,
    command: (e: MenuItemCommandEvent) => {
      emit('delete-option-clicked', focusedItem.value)
    },
  },
])

const style = computed(() => {
  return showSlidingPanel.value ? 'width: 100%;' : 'min-width: min(80vw, 1200px);max-width:1300px'
})

const toggleOptionsMenu = (event: MouseEvent, selectedItem: Workflow | Experiment) => {
  focusedItem.value = selectedItem
  optionsMenu.value.toggle(event)
}

const columnStyles = computed(() => {
  return {
    expander: 'width: 4rem',
    name: showSlidingPanel.value ? 'width: 20rem' : 'width: 26rem',
    created: 'width: 12rem',
    status: 'width: 24rem',
  }
})

function handleRowClick(event: DataTableRowClickEvent) {
  if (
    (event.originalEvent.target as HTMLElement)?.closest('svg.p-icon.p-datatable-row-toggle-icon')
  ) {
    // preventing experiment selection on row expansion
    return
  }
  emit('l-experiment-selected', event.data)
}

async function onWorkflowSelected(workflow: Workflow, experiment: Experiment) {
  // fetching job details from BE instead of filtering
  // because job might be still running
  // const inferenceJob = workflow.jobs.find((job: JobResult) => job.metrics?.length > 0)
  if (workflow.jobs) {
    emit('l-workflow-selected', workflow)
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
      // TODO: immutability would be nice
      const existingWorkflow = experiment.workflows.find((w) => w.id === workflow.id)
      if (existingWorkflow) {
        existingWorkflow.status = workflow.status
        existingWorkflow.artifacts_download_url = workflow.artifacts_download_url
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

  &__tag {
    color: $l-grey-100;
    font-size: $l-font-size-sm;
    line-height: 1;
    font-weight: $l-font-weight-normal;
    text-transform: uppercase;
  }
}
</style>
