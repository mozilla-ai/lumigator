<template>
  <DataTable
    :value="tableData"
    dataKey="id"
    :showHeaders="false"
    :tableStyle="columnStyles"
    :pt="{ root: 'l-job-table', tableContainer: 'width-100' }"
    @row-click="handleRowClick"
  >
    <Column :style="columnStyles.expander"></Column>
    <Column :style="columnStyles.name">
      <template #body="slotProps">
        {{ shortenedModel(slotProps.data.model.path) }}
      </template>
    </Column>
    <Column field="created" header="created" :style="columnStyles.created" sortable>
      <template #body="slotProps">
        {{ formatDate(slotProps.data.created) }}
      </template>
    </Column>
    <Column field="status" header="status">
      <template #body="slotProps">
        <div>
          <Tag
            v-if="retrieveStatus(slotProps.data.id) === 'SUCCEEDED'"
            severity="success"
            rounded
            :value="retrieveStatus(slotProps.data.id)"
            :pt="{ root: 'l-job-table__tag' }"
          />
          <Tag
            v-else-if="retrieveStatus(slotProps.data.id) === 'FAILED'"
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
    <Column style="width: 6rem"></Column>
  </DataTable>
</template>

<script lang="ts" setup>
import DataTable, { type DataTableRowClickEvent } from 'primevue/datatable';
import Tag from 'primevue/tag';
import Column from 'primevue/column';
import { formatDate } from '@/helpers/index';
import { storeToRefs } from 'pinia';
import { useExperimentStore } from '@/stores/experiments/store';

const experimentStore = useExperimentStore()
const { jobs } = storeToRefs(experimentStore)
defineProps({
  tableData: {
    type: Array,
    required: true,
  },
  columnStyles: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['l-job-selected'])

const shortenedModel = (path: string) => (path.length <= 30 ? path : `${path.slice(0, 30)}...`);

function handleRowClick(event: DataTableRowClickEvent) {
  emit('l-job-selected', event.data);
}

function retrieveStatus(jobID: string) {
  const job = jobs.value.find((job) => job.id === jobID);
  return job ? job.status : undefined;
}
</script>

<style scoped lang="scss">
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

<style lang="scss">
.l-job-table {
  $root: &;
  width: 100%;
  display: flex;
  place-content: center;

  .p-datatable-table-container {
    border: none;
  }

  .p-datatable-table-container [class*='p-row-'] {
    background-color: $l-main-bg;
  }
}
</style>
