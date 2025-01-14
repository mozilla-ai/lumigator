<template>
  <div class="l-experiment-table">
    <transition
      name="transition-fade"
      mode="out-in"
    >
      <DataTable
        v-if="tableVisible"
        v-model:selection="focusedItem"
        v-model:expandedRows="expandedRows"
        selectionMode="single"
        dataKey="id"
        :value="tableData"
        :tableStyle="style"
        columnResizeMode="expand"
        sortField="created"
        :sortOrder="-1"
        scrollable
        scrollHeight="80vh"
        :pt="{table:'table-root'}"
        @row-unselect="showSlidingPanel = false"
      >
        <Column
          expander
          :style="columnStyles.expander"
        />
        <Column
          field="name"
          :style="columnStyles.name"
          header="experiment title"
        />
        <Column
          field="created"
          header="created"
          sortable
          :style="columnStyles.created"
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
                :pt="{root:'l-experiment-table__tag'}"
              />
              <Tag
                v-else-if="retrieveStatus(slotProps.data.id) === 'FAILED' "
                severity="danger"
                rounded
                :value="retrieveStatus(slotProps.data.id)"
                :pt="{root:'l-experiment-table__tag'}"
              />
              <Tag
                v-else
                severity="warn"
                rounded
                :value="retrieveStatus(slotProps.data.id)"
                :pt="{root:'l-experiment-table__tag'}"
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
            />
          </template>
        </Column>
        <template #expansion="slotProps">
          <div class="l-experiment-table__jobs-table-container">
            <l-jobs-table
              :column-styles="columnStyles"
              :table-data="slotProps.data.jobs"
            />
          </div>
        </template>
      </DataTable>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { formatDate } from '@/helpers/index'
import { useSlidePanel } from '@/composables/SlidingPanel';
import Tag from 'primevue/tag';
import LJobsTable from '@/components/molecules/LJobsTable.vue';
import {useExperimentStore} from "@/stores/experiments/store.js";

const props = defineProps({
  tableData: {
    type: Array,
    required: true,
  }
});
const emit = defineEmits(['l-experiment-selected'])


const isThrottled = ref(false);
const { showSlidingPanel } = useSlidePanel();
const experimentStore = useExperimentStore();
const { experiments } = storeToRefs(experimentStore);
const tableVisible = ref(true);
const focusedItem = ref();
const expandedRows = ref({});

const style = computed(() => {
  return showSlidingPanel.value ?
    'table-layout: fixed; width: 100%;' : 'min-width: min(80vw, 1200px)'
})

const columnStyles = {
  expander: "width: 4rem",
  name: "width: 24rem",
  created: "width: 12rem",
}

function retrieveStatus(jobID) {
  const job = experiments.value.find(job => job.id === jobID);
  return job ? job.status : null;
}

// Throttle ensures the function is invoked at most once every defined period.
async function throttledUpdateAllJobs() {
  if (isThrottled.value) { return }; // Skip if throttle is active

  isThrottled.value = true;
  await experimentStore.updateStatusForIncompleteExperiments();
  setTimeout(() => {
    isThrottled.value = false; // Release throttle after delay
  }, 5000); // 5 seconds throttle
}

// This is a temporary solution until 'experiments/' endpoint
// updates the status of each experiment
let pollingId;
onMounted(async () => {
  await experimentStore.updateStatusForIncompleteExperiments();
  pollingId = setInterval(async () => {
    await throttledUpdateAllJobs();
  }, 1000)}
); // Check every second, throttled to execute every 5 seconds

onUnmounted(() => {
  clearInterval(pollingId);
});

watch(showSlidingPanel, (newValue) => {
  tableVisible.value = false;
  focusedItem.value = newValue ? focusedItem.value : null;
  setTimeout(() => {
    tableVisible.value = true;
  }, 100);
});

watch(() => props.tableData.length, async () => {
  await experimentStore.updateStatusForIncompleteExperiments();
});
</script>

<style scoped lang="scss">
.l-experiment-table {
	$root: &;
  	width: 100%;
    display: flex;
    place-content: center;

    &__options-trigger {
		padding: 0;
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
