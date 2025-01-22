<template>
  <DataTable
    :value="tableData"
    selectionMode="single"
    dataKey="id"
    :tableStyle="tableStyle"
    sortField="created"
    :sortOrder="-1"
    scrollable
    :pt="{root:'l-job-table', tableContainer:'width-100'}"
    @row-click="handleRowClick"
  >
    <Column
      field="name"
      header="File Name"
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
import { computed } from 'vue';
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

const tableStyle = computed(() => {
  return showSlidingPanel.value ?
    'min-width: 40vw' : 'min-width: min(80vw, 1200px)'
});


function handleRowClick(event) {
  emit('l-inference-selected', event.data)
}

function retrieveStatus(jobID) {
  const job = inferenceJobs.value.find(job => job.id === jobID);
  return job ? job.status : null;
}

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

<style lang="scss">
.l-job-table {
	$root: &;
  	width: 100%;
    max-width: 1300px;
    display: flex;
    place-content: center;
}
</style>
