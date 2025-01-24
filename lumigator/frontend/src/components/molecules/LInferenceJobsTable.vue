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
    :pt="{root:'l-job-table', tableContainer:'width-100'}"
    @row-click="handleRowClick"
  >
    <Column
      field="name"
      header="Filename"
    >
      <template #body="slotProps">
        {{ slotProps.data.dataset.name }}
      </template>
    </Column>
    <Column
      field="created"
      header="created"
      sortable
    >
      <template #body="slotProps">
        {{ formatDate(slotProps.data.created) }}
      </template>
    </Column>
    <Column
      field="status"
      header="status"
    >

      <template #body="slotProps">
        <div>
          <Tag
            v-if="retrieveStatus(slotProps.data.id) === 'SUCCEEDED' "
            severity="success"
            rounded
            :value="retrieveStatus(slotProps.data.id)"
            :pt="{root:'l-job-table__tag'}"
          />
          <Tag
            v-else-if="retrieveStatus(slotProps.data.id) === 'FAILED' "
            severity="danger"
            rounded
            :value="retrieveStatus(slotProps.data.id)"
            :pt="{root:'l-job-table__tag'}"
          />
          <Tag
            v-else
            severity="warn"
            rounded
            :value="retrieveStatus(slotProps.data.id)"
            :pt="{root:'l-job-table__tag'}"
          />
        </div>
      </template>
    </Column>
    <Column
      header="options"
    >
      <template #body>
        <span
          class="pi pi-fw pi-ellipsis-h l-experiment-table__options-trigger"
          style="cursor: not-allowed; pointer-events: all"
          aria-controls="optionsMenu"
        />
      </template>
    </Column>
  </DataTable>
</template>

<script setup>
import {ref, computed, onMounted, onUnmounted } from 'vue';
import DataTable from 'primevue/datatable';
import Tag from 'primevue/tag';
import Column from 'primevue/column';
import { formatDate } from '@/helpers/index'
import { storeToRefs } from 'pinia';
import { useExperimentStore } from "@/stores/experiments/store.js";
import { useSlidePanel } from '@/composables/SlidingPanel';


const experimentStore = useExperimentStore();
const { inferenceJobs } = storeToRefs(experimentStore);
defineProps({
  tableData: {
    type: Array,
    required: true,
  },
  columnStyles: {
    type: Object,
    required: false
  },
});

const emit = defineEmits(['l-inference-selected'])
const { showSlidingPanel  } = useSlidePanel();
const isThrottled = ref(false);
const focusedItem = ref(null);

const tableStyle = computed(() => {
  return showSlidingPanel.value ?
    'min-width: 40vw' : 'min-width: min(80vw, 1200px)'
});


function handleRowClick(event) {
  emit('l-inference-selected', event.data)
}

function retrieveStatus(jobId) {
  const jobStatus = inferenceJobs.value.find((job) => job.id === jobId);
  return jobStatus ? jobStatus.status : null;
}

// Throttle ensures the function is invoked at most once every defined period.
async function throttledUpdateAllJobs() {
  if (isThrottled.value) { return }; // Skip if throttle is active

  isThrottled.value = true;
  await experimentStore.updateStatusForIncompleteJobs();
  setTimeout(() => {
    isThrottled.value = false; // Release throttle after delay
  }, 5000); // 5 seconds throttle
}


// This is a temporary solution until 'experiments/' endpoint
// updates the status of each experiment
let pollingId;
onMounted(async () => {
  await experimentStore.updateStatusForIncompleteJobs();
  pollingId = setInterval(async () => {
    await throttledUpdateAllJobs();
  }, 1000)}
);

onUnmounted(() => {
  clearInterval(pollingId);
});

</script>

<style scoped lang="scss">
.l-job-table {
	$root: &;
  	width: 100%;
    display: flex;
    place-content: center;

    .p-datatable-table-container {
      [class*=p-row-] {
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
