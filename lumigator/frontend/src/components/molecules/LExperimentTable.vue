<template>
  <div class="l-experiment-table">
    <transition
      name="transition-fade"
      mode="out-in"
    >
      <DataTable
        v-if="tableVisible"
        v-model:selection="focusedItem"
        selectionMode="single"
        dataKey="id"
        :value="tableData"
        :tableStyle="style"
        columnResizeMode="expand"
        scrollable
        :pt="{table:'table-root'}"
        @row-click="emit('l-experiment-selected', $event.data)"
        @row-unselect="showSlidingPanel = false"
      >
        <Column
          field="name"
          header="experiment title"
        />
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
import { useHealthStore } from '@/stores/health/store';
import Tag from 'primevue/tag';

const props = defineProps({
  tableData: {
    type: Array,
    required: true,
  }
});
const emit = defineEmits(['l-experiment-selected'])


const isThrottled = ref(false);
const { showSlidingPanel } = useSlidePanel();
const healthStore = useHealthStore();
const { runningJobs } = storeToRefs(healthStore);
const tableVisible = ref(true);
const focusedItem = ref();

const style = computed(() => {
  return showSlidingPanel.value ?
    'min-width: min(60vw, 1200px)' : 'min-width: min(80vw, 1200px)'
})

function retrieveStatus(jobID) {
 const job = runningJobs.value.find(job => job.id === jobID);
  return job ? job.status : null;
}


function updateJobStatuses() {
  runningJobs.value =  props.tableData.map(experiment => ({
    id: experiment.id,
    status: experiment.status
  }));
}

// Throttle ensures the function is invoked at most once every defined period.
async function throttledUpdateAllJobs() {
  if (isThrottled.value) { return }; // Skip if throttle is active

  isThrottled.value = true;
  await healthStore.updateAllJobs();
  setTimeout(() => {
    isThrottled.value = false; // Release throttle after delay
  }, 5000); // 5 seconds throttle
}

// This is a temporary solution until 'experiments/' endpoint
// updates the status of each experiment
let pollingId;
onMounted(() => {
  updateJobStatuses();
  pollingId = setInterval(() => {
    throttledUpdateAllJobs();
  }, 1000); // Check every second, throttled to execute every 5 seconds
})

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

watch(() => props.tableData.length, () => {
  updateJobStatuses();
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
    color: $l-grey-150;
    font-size: $l-font-size-sm;
    line-height: 1;
    font-weight: $l-font-weight-normal;
  }
}
</style>
