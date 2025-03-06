<template>
  <div class="l-experiment-results">
    <DataTable
      v-model:expandedRows="expandedRows"
      class="gridlines"
      :value="tableData"
      scrollable
      scrollHeight="90vh"
      tableStyle="min-width: 50rem;min-width:70vw"
    >
      <Column expander />
      <Column field="model" bodyStyle="width: 300px">
        <template #header>
          <span class="p-datatable-column-title">Model </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.model.display_name }}
        </template>
      </Column>
      <Column field="meteor.meteor_mean" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.meteor" class="p-datatable-column-title">Meteor </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.meteor.meteor_mean.toFixed(2) }}
        </template>
      </Column>
      <Column field="bertscore" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.bertPrecision" class="p-datatable-column-title"
            >BERT P
          </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.bertscore.precision_mean.toFixed(2) }}
        </template>
      </Column>
      <Column field="bertscore" sortable>
        <template #header>
          <span class="p-datatable-column-title">BERT R </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.bertscore.recall_mean.toFixed(2) }}
        </template>
      </Column>
      <Column field="bertscore.f1" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.bertF1" class="p-datatable-column-title">BERT F1 </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.bertscore.f1_mean.toFixed(2) }}
        </template>
      </Column>
      <Column field="rouge.rouge1" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.rouge1" class="p-datatable-column-title">ROUGE-1 </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.rouge.rouge1_mean.toFixed(2) }}
        </template>
      </Column>
      <Column field="rouge.rouge2" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.rouge2" class="p-datatable-column-title">ROUGe-2 </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.rouge.rouge2_mean.toFixed(2) }}
        </template>
      </Column>
      <Column field="rouge.rougeL" sortable>
        <template #header>
          <span v-tooltip.bottom="tooltips.rougeL" class="p-datatable-column-title">ROUGE-L </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.rouge.rougeL_mean.toFixed(2) }}
        </template>
      </Column>
      <Column field="model.info.model_size" sortable>
        <template #header>
          <span class="p-datatable-column-title">model size </span>
        </template>
        <template #body="slotProps">
          {{
            slotProps.data.model.info?.model_size.replace(/(\d+(?:\.\d+)?)([a-zA-Z]+)/g, '$1 $2')
          }}
        </template>
      </Column>
      <Column field="model.info.parameter_count" sortable>
        <template #header>
          <span class="p-datatable-column-title">parameters </span>
        </template>
        <template #body="slotProps">
          {{
            slotProps.data.model.info?.parameter_count.replace(
              /(\d+(?:\.\d+)?)([a-zA-Z]+)/g,
              '$1 $2',
            )
          }}
        </template>
      </Column>
      <Column field="runTime" sortable>
        <template #header>
          <span class="p-datatable-column-title">Run Time </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.runTime }}
        </template>
      </Column>
      <template #expansion="slotProps">
        <div>
          <l-job-results :results="slotProps.data.jobResults" :no-radius="true" />
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref, toRefs, type ComputedRef } from 'vue'
import { useModelStore } from '@/stores/modelsStore'
import { storeToRefs } from 'pinia'
import LJobResults from '@/components/experiments/LJobResults.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type { Model } from '@/types/Model'
import type { ExperimentResults } from '@/types/Experiment'

const modelStore = useModelStore()
const { models } = storeToRefs(modelStore)
const expandedRows = ref([])

const props = defineProps<{
  results: ExperimentResults[]
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

const tableData: ComputedRef<Array<ExperimentResults & { model: Model }>> = computed(() => {
  const data = results.value.map((result) => ({
    ...result,
    model: models.value.find(
      (model: Model) => model.model === result.model || model.display_name === result.model,
    )!,
  }))

  console.log('data', data)

  return data
})
</script>

<style scoped lang="scss"></style>
