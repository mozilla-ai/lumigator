<template>
  <div class="l-experiment-results">
    <TableView
      :data="results"
      :hasCursorPointer="false"
      :columns="Object.keys(results[0]).filter((key) => key !== 'subRows' && key !== 'rowNumber')"
      :downloadFileName="'results'"
      :isEditable="false"
      :showRowNumber="!isTableDataForExperimentResults(results)"
      :isSearchEnabled="!isTableDataForExperimentResults(results)"
      ref="dataTable"
    />
  </div>
</template>

<script lang="ts" setup>
import TableView from '../common/TableView.vue'
import type {
  TableDataForExperimentResults,
  TableDataForWorkflowResults,
} from '@/helpers/getExperimentResults'

// const expandedRows = ref([])

defineProps<{
  results: TableDataForExperimentResults[] | TableDataForWorkflowResults[]
}>()

function isTableDataForExperimentResults(
  data: TableDataForExperimentResults[] | TableDataForWorkflowResults[],
): data is TableDataForExperimentResults[] {
  return (data as TableDataForExperimentResults[])[0].hasOwnProperty('model')
}
</script>

<style scoped lang="scss"></style>
