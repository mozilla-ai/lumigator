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
        {{ shortenedModel(slotProps.data.model) }}
      </template>
    </Column>
    <Column field="created" header="created" :style="columnStyles.created" sortable>
      <template #body="slotProps">
        {{ formatDate(slotProps.data.created_at) }}
      </template>
    </Column>
    <Column field="status" header="status">
      <template #body="slotProps">
        <div>
          <Tag
            v-if="slotProps.data.status === WorkflowStatus.SUCCEEDED"
            severity="success"
            rounded
            :value="slotProps.data.status"
            :pt="{ root: 'l-job-table__tag' }"
          />
          <Tag
            v-else-if="slotProps.data.status === WorkflowStatus.FAILED"
            severity="danger"
            rounded
            :value="slotProps.data.status"
            :pt="{ root: 'l-job-table__tag' }"
          />
          <Tag
            v-else
            severity="warn"
            rounded
            :value="slotProps.data.status"
            :pt="{ root: 'l-job-table__tag' }"
          />
        </div>
      </template>
    </Column>
    <Column style="width: 6rem"></Column>
  </DataTable>
</template>

<script lang="ts" setup>
import DataTable, { type DataTableRowClickEvent } from 'primevue/datatable'
import Tag from 'primevue/tag'
import Column from 'primevue/column'
<<<<<<<< HEAD:lumigator/frontend/src/components/experiments/LJobsTable.vue
// import { storeToRefs } from 'pinia'
// import { useExperimentStore } from '@/stores/experimentsStore'
import { formatDate } from '@/helpers/formatDate'
import { WorkflowStatus, type Workflow } from '@/types/Workflow'
import type { PropType } from 'vue'
// import type { JobDetails } from '@/types/JobDetails'
========
import { storeToRefs } from 'pinia'
import { useExperimentStore } from '@/stores/experimentsStore'
import { formatDate } from '@/helpers/formatDate'
>>>>>>>> origin/new-workflow-api:lumigator/frontend/src/components/jobs/LJobsTable.vue

// const experimentStore = useExperimentStore()
// const { jobs } = storeToRefs(experimentStore)
defineProps({
  tableData: {
    type: Array as PropType<Workflow[]>,
    required: true,
  },
  columnStyles: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['l-job-selected'])

const shortenedModel = (path: string) => (path.length <= 30 ? path : `${path.slice(0, 30)}...`)

function handleRowClick(event: DataTableRowClickEvent) {
  emit('l-job-selected', event.data)
}
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

<style lang="scss">
@use '@/styles/variables' as *;

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
