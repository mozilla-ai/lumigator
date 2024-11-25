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
        style="vertical-align: middle; text-align: right"
      >
        <template #body="{index}">
          {{ index+1 }}
        </template>
      </Column>

      <Column
        field="example"
        header="examples"
      >
        <template #body="slotProps">
          {{ slotProps.data.example }}
        </template>
      </Column>
      <Column
        field="ground_truth"
        header="Ground Truth"
      ></Column>
      <Column
        field="predictions"
        header="predictions"
      ></Column>
      <Column
        field="rouge.rouge1"
        header="rouge-1"
        sortable
      >
        <template #body="slotProps">
          {{ slotProps.data.rouge.rouge1.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="rouge.rouge2"
        header="rouge-2"
        sortable
      >
        <template #body="slotProps">
          {{ slotProps.data.rouge.rouge2.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="rouge.rougeL"
        header="Rouge-l"
        sortable
      >
        <template #body="slotProps">
          {{ slotProps.data.rouge.rougeL.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="meteor"
        header="meteor"
        sortable
      >
        <template #body="slotProps">
          {{ slotProps.data.meteor.meteor.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="bertscore"
        header="Bert P"
        sortable
      >
        <template #body="slotProps">
          {{ slotProps.data.bertscore.precision.toFixed(2) }}
        </template>
      </Column>
      <Column
        field="bertscore.f1"
        header="Bert f1"
        sortable
      >
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


onMounted(() => {
  tableData.value = props.results;
})
</script>
