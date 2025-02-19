<template>
  <div class="l-results-table">
    <DataTable
      class="gridlines"
      :value="tableData"
      scrollable
      scrollHeight="90vh"
      tableStyle="min-width: 50rem;min-width:70vw"
      :class="{ 'no-radius': noRadius }"
    >
      <Column style="vertical-align: middle; text-align: left; padding-right: 0">
        <template #body="{ index }">
          {{ index + 1 }}
        </template>
      </Column>

      <Column field="example" bodyStyle="max-width: 300px">
        <template #header>
          <span v-tooltip.bottom="tooltips.examples" class="p-datatable-column-title"
            >Examples
          </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.example }}
        </template>
      </Column>
      <Column field="ground_truth" bodyStyle="max-width: 300px">
        <template #header>
          <span v-tooltip.bottom="tooltips.ground_truth" class="p-datatable-column-title"
            >Ground Truth
          </span>
        </template>
      </Column>
      <Column field="predictions" bodyStyle="max-width: 300px">
        <template #header>
          <span v-tooltip.bottom="tooltips.predictions" class="p-datatable-column-title"
            >Predictions
          </span>
        </template>
      </Column>
      <Column field="rouge.rouge1" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.rouge1" class="p-datatable-column-title">ROUGE-1 </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.rouge.rouge1.toFixed(2) }}
        </template>
      </Column>
      <Column field="rouge.rouge2" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.rouge2" class="p-datatable-column-title">ROUGe-2 </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.rouge.rouge2.toFixed(2) }}
        </template>
      </Column>
      <Column field="rouge.rougeL" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.rougeL" class="p-datatable-column-title">ROUGE-L </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.rouge.rougeL.toFixed(2) }}
        </template>
      </Column>
      <Column field="meteor" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.meteor" class="p-datatable-column-title">meteor </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.meteor.meteor.toFixed(2) }}
        </template>
      </Column>
      <Column field="bertscore" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.bertPrecision" class="p-datatable-column-title"
            >BERT P
          </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.bertscore.precision.toFixed(2) }}
        </template>
      </Column>
      <Column field="bertscore.f1" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.bertF1" class="p-datatable-column-title">BERT F1 </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.bertscore.f1.toFixed(2) }}
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, type Ref, type PropType } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type { EvaluationJobResults } from '@/types/Experiment'

const props = defineProps({
  results: {
    type: Array as PropType<EvaluationJobResults[]>,
    required: true,
  },
  noRadius: {
    type: Boolean,
    required: false,
    default: false,
  },
})

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

const tableData: Ref<EvaluationJobResults[]> = ref([])
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

onMounted(() => {
  tableData.value = props.results
})
</script>

<style lang="scss">
.l-results-table {
  .p-datatable-column-title {
    cursor: pointer;
  }

  .no-radius {
    .p-datatable-table-container {
      border-radius: 0 !important;
    }
  }
}
</style>
