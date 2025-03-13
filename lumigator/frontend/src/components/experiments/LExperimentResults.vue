<template>
  <div class="l-experiment-results">
    <TableView
      :data="tableData"
      :columns="Object.keys(tableData[0]).filter((key) => key !== 'subRows' && key !== 'rowNumber')"
      :downloadFileName="'results'"
      :isEditable="false"
      :showRowNumber="!isTableDataForExperimentResults(results)"
      :isSearchEnabled="false"
      ref="dataTable"
    />
  </div>
</template>

<script lang="ts" setup>
import { computed, ref, toRefs } from 'vue'
import { useModelStore } from '@/stores/modelsStore'
import { storeToRefs } from 'pinia'
import type { Model } from '@/types/Model'
import TableView from '../common/TableView.vue'
import type {
  TableDataForExperimentResults,
  TableDataForWorkflowResults,
} from '@/helpers/getExperimentResults'

const modelStore = useModelStore()
const { models } = storeToRefs(modelStore)
// const expandedRows = ref([])

const props = defineProps<{
  results: TableDataForExperimentResults[] | TableDataForWorkflowResults[]
}>()

const { results } = toRefs(props)

const tooltipColorsConfig = ref({
  root: {
    style: {
      background: `transparent`,
    },
  },
  text: {
    style: {
      background: `black`,
    },
  },
  arrow: {
    style: {
      ['border-bottom-color']: `black`,
    },
  },
})
const tooltips = ref({
  examples: {
    value: `Text which is passed as an input to the model, together
    with a task-dependent prompt.`,
    class: 'metric-tooltip',
    pt: tooltipColorsConfig.value,
  },
  ground_truth: {
    value: `Expected output we are comparing the model's predictions with
     - all metrics are results of such a comparison.`,
    class: 'metric-tooltip',
    pt: tooltipColorsConfig.value,
  },
  predictions: {
    value: `Answers provided by the model after being prompted with the input.`,
    class: 'metric-tooltip',
    pt: tooltipColorsConfig.value,
  },
  rouge1: {
    value: `Measures the overlap of individual words
     between the predicted and ground-truth summaries, focusing on basic word-level similarity.`,
    class: 'metric-tooltip',
    pt: tooltipColorsConfig.value,
  },
  rouge2: {
    value: `Calculates the overlap of two-word sequences (bigrams) capturing
    both word choices and their immediate order.`,
    class: 'metric-tooltip',
    pt: tooltipColorsConfig.value,
  },
  rougeL: {
    value: `Identifies the longest matching sequence of words (not necessarily consecutive),
    considering overall structure while allowing for gaps between words.`,
    class: 'metric-tooltip',
    pt: tooltipColorsConfig.value,
  },
  meteor: {
    value: `Evaluates predictions by comparing words, synonyms, and flexible word orders
     balancing precision and recall for semantic similarity.`,
    class: 'metric-tooltip',
    pt: tooltipColorsConfig.value,
  },
  bertPrecision: {
    value: `Measures the precision of predictions,
    calculated as the proportion of predicted tokens that are semantically
    similar to tokens in the ground truth.`,
    class: 'metric-tooltip',
    pt: tooltipColorsConfig.value,
  },
  bertF1: {
    value: `Harmonic mean of BERT Precision and BERT Recall, providing a balanced
    measure of how well the prediction aligns with the ground truth both in accuracy and coverage.`,
    class: 'metric-tooltip',
    pt: tooltipColorsConfig.value,
  },
})

const tableData = computed(() => {
  const isExperimentResults = isTableDataForExperimentResults(results.value)
  if (!isExperimentResults) {
    return results.value.map((result) => ({
      ...result,
      model: (
        models.value.find(
          (model: Model) =>
            model.model === (result as TableDataForExperimentResults).model ||
            model.display_name === (result as TableDataForExperimentResults).model,
        )! as Model
      )?.display_name,
    }))
  } else {
    return results.value
  }
})

function isTableDataForExperimentResults(
  data: TableDataForExperimentResults[] | TableDataForWorkflowResults[],
): data is TableDataForExperimentResults[] {
  return (data as TableDataForExperimentResults[])[0].hasOwnProperty('model')
}
</script>

<style scoped lang="scss"></style>
