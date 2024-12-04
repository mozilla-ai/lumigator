<template>
  <div class="l-results-table">
    <DataTable
      class="gridlines"
      :value="tableData"
      scrollable
      scrollHeight="90vh"
      tableStyle="min-width: 50rem;min-width:70vw"
    >
      <Column
        style="vertical-align: middle; text-align: left;padding-right:0"
      >
        <template #body="{index}">
          {{ index+1 }}
        </template>
      </Column>

      <Column
        field="example"
        header="examples"
        bodyStyle="max-width: 300px"
      >
        <template #body="slotProps">
          {{ slotProps.data.example }}
        </template>
      </Column>
      <Column
        field="ground_truth"
        header="Ground Truth"
        bodyStyle="max-width: 300px"
      ></Column>
      <Column
        field="predictions"
        header="predictions"
        bodyStyle="max-width: 300px"
      ></Column>
      <Column
        field="rouge.rouge1"
        sortable
      >
        <template #header>
          <span
            v-tooltip.bottom="tooltips.rouge1"
            class="p-datatable-column-title"
          >ROUGE-1
          </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.rouge.rouge1.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="rouge.rouge2"
        sortable
      >
        <template #header>
          <span
            v-tooltip.bottom="tooltips.rouge2"
            class="p-datatable-column-title"
          >ROUGe-2
          </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.rouge.rouge2.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="rouge.rougeL"
        sortable
      >
        <template #header>
          <span
            v-tooltip.bottom="tooltips.rougeL"
            class="p-datatable-column-title"
          >ROUGE-L
          </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.rouge.rougeL.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="meteor"
        sortable
      >
        <template #header>
          <span
            v-tooltip.bottom="tooltips.meteor"
            class="p-datatable-column-title"
          >meteor
          </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.meteor.meteor.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="bertscore"
        sortable
      >
        <template #header>
          <span
            v-tooltip.bottom="tooltips.bertPrecision"
            class="p-datatable-column-title"
          >BERT P
          </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.bertscore.precision.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="bertscore.f1"
        sortable
      >
        <template #header>
          <span
            v-tooltip.bottom="tooltips.bertF1"
            class="p-datatable-column-title"
          >Bert f1
          </span>
        </template>
        <template #body="slotProps">
          {{ slotProps.data.bertscore.f1.toFixed(2) }}
        </template>
      </Column>

    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const props = defineProps({
  results: {
    type: Object,
    required: true,
  }
})

const tableData = ref([]);
const tooltips = ref({
  rouge1: {
    value: `Measures the overlap of individual words
     between the predicted and ground-truth summaries, focusing on basic word-level similarity.`,
    class: 'metric-tooltip',
    pt: { text: 'tooltip-content' }
  },
  rouge2: {
    value: `Calculates the overlap of two-word sequences (bigrams) capturing
    both word choices and their immediate order.`,
    class: 'metric-tooltip',
    pt: { text: 'tooltip-content' }
  },
  rougeL: {
    value: `Identifies the longest matching sequence of words (not necessarily consecutive),
    considering overall structure while allowing for gaps between words.`,
    class: 'metric-tooltip',
    pt: { text: 'tooltip-content' }
  },
  meteor: {
    value: `Evaluates predictions by comparing words, synonyms, and flexible word orders
     balancing precision and recall for semantic similarity.`,
    class: 'metric-tooltip',
    pt: { text: 'tooltip-content' }
  },
  bertPrecision: {
    value: `Measures the precision of predictions,
    calculated as the proportion of predicted tokens that are semantically
    similar to tokens in the ground truth.`,
    class: 'metric-tooltip',
    pt: { text: 'tooltip-content' }
  },
  bertF1: {
    value: `Harmonic mean of BERT Precision and BERT Recall, providing a balanced
    measure of how well the prediction aligns with the ground truth both in accuracy and coverage.`,
    class: 'metric-tooltip',
    pt: { text: 'tooltip-content' }
  },
})


onMounted(() => {
  tableData.value = props.results;
})
</script>

<style lang="scss">
.metric-tooltip {
  border-radius: $l-border-radius;

  .tooltip-content {
    background-color: #000;
  }
}
</style>
