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
import { ref, computed, type PropType } from 'vue'
import { storeToRefs } from 'pinia'
import { type DataTableRowClickEvent } from 'primevue/datatable'

import { formatDate } from '@/helpers/formatDate'
import { WorkflowStatus } from '@/types/Workflow'
import type { Experiment } from '@/types/Experiment'
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
  'delete-option-clicked',
  'view-experiment-results-clicked',
])

const tableVisible = ref(true)

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
