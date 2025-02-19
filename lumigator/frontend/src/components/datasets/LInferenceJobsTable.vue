<template>
  <DataTable
    v-model:selection="focusedItem"
    :value="tableData"
    selectionMode="single"
    dataKey="id"
    :tableStyle="tableStyle"
    sortField="created"
    :sortOrder="-1"
    scrollable
    scrollHeight="75vh"
    :pt="{ root: 'l-job-table', tableContainer: 'width-100' }"
    @row-click="handleRowClick"
  >
    <Column field="name" header="Filename">
      <template #body="slotProps">
        {{ slotProps.data.dataset.name }}
      </template>
    </Column>
    <Column field="created" header="created" sortable>
      <template #body="slotProps">
        {{ formatDate(slotProps.data.created_at) }}
      </template>
    </Column>
    <Column field="status" header="status">
      <template #body="slotProps">
        <div>
          <Tag
            v-if="retrieveStatus(slotProps.data.id) === WorkflowStatus.SUCCEEDED"
            severity="success"
            rounded
            :value="retrieveStatus(slotProps.data.id)"
            :pt="{ root: 'l-job-table__tag' }"
          />
          <Tag
            v-else-if="retrieveStatus(slotProps.data.id) === WorkflowStatus.FAILED"
            severity="danger"
            rounded
            :value="retrieveStatus(slotProps.data.id)"
            :pt="{ root: 'l-job-table__tag' }"
          />
          <Tag
            v-else
            severity="warn"
            rounded
            :value="retrieveStatus(slotProps.data.id)"
            :pt="{ root: 'l-job-table__tag' }"
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
        ></span>
      </template>
    </Column>
  </DataTable>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import DataTable, { type DataTableRowClickEvent } from 'primevue/datatable'
import Tag from 'primevue/tag'
import Column from 'primevue/column'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasetsStore'
import { useSlidePanel } from '@/composables/useSlidePanel'
import { formatDate } from '@/helpers/formatDate'
import { WorkflowStatus } from '@/types/Workflow'

const datasetStore = useDatasetStore()
const { inferenceJobs, hasRunningInferenceJob } = storeToRefs(datasetStore)
defineProps({
  tableData: {
    type: Array,
    required: true,
  },
  columnStyles: {
    type: Object,
    required: false,
  },
})

const emit = defineEmits(['l-inference-selected', 'l-inference-finished'])
const { showSlidingPanel } = useSlidePanel()
const isThrottled = ref(false)
const focusedItem = ref()

const tableStyle = computed(() => {
  return showSlidingPanel.value ? 'min-width: 40vw' : 'min-width: min(80vw, 1200px)'
})

function handleRowClick(event: DataTableRowClickEvent) {
  emit('l-inference-selected', event.data)
}

function retrieveStatus(jobId: string) {
  const jobStatus = inferenceJobs.value.find((job) => job.id === jobId)
  return jobStatus ? jobStatus.status : undefined
}

// Throttle ensures the function is invoked at most once every defined period.
async function throttledUpdateAllJobs() {
  if (isThrottled.value) {
    return
  } // Skip if throttle is active

  isThrottled.value = true
  await datasetStore.updateStatusForIncompleteJobs()
  setTimeout(() => {
    isThrottled.value = false // Release throttle after delay
  }, 5000) // 5 seconds throttle
}

// This is a temporary solution until 'jobs/' endpoint
// updates the status of each job
let pollingId: number | undefined
watch(hasRunningInferenceJob, async (newValue) => {
  if (newValue) {
    await datasetStore.updateStatusForIncompleteJobs()
    pollingId = setInterval(async () => {
      await throttledUpdateAllJobs()
    }, 1000)
  } else {
    clearInterval(pollingId)
    emit('l-inference-finished')
    datasetStore.fetchDatasets()
  }
})

onBeforeUnmount(() => {
  clearInterval(pollingId)
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;
.l-job-table {
  $root: &;
  width: 100%;
  display: flex;
  place-content: center;

  .p-datatable-table-container {
    [class*='p-row-'] {
      background-color: $l-main-bg;
    }
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
