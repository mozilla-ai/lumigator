<template>
  <Drawer
    v-model:visible="isVisible"
    :header="title"
    :position="'full'"
    @hide="$emit('close', $event)"
  >
    <template #header>
      <h3>{{ title }}</h3>
      <PrimeVueButton
        type="button"
        text
        icon="pi pi-download"
        rounded
        severity="secondary"
        style="margin-left: auto"
        aria-label="download"
        @click="handleDownloadClicked"
      ></PrimeVueButton>
    </template>
    <DataTable
      :value="data"
      :reorderableColumns="true"
      ref="dataTable"
      removableSort
      scrollable
      scrollHeight="flex"
      :virtualScrollerOptions="{ itemSize: 46 }"
      :resizableColumns="false"
      columnResizeMode="fit"
      showGridlines
      stripedRows
    >
      <Column v-for="col in columns" sortable :key="col" :field="col" :header="col"></Column>
    </DataTable>
  </Drawer>
</template>

<script lang="ts">
import { Button, Column, DataTable, Drawer, type DataTableProps } from 'primevue'
import { defineComponent, ref, type PropType } from 'vue'

export default defineComponent({
  name: 'DatasetViewer',
  components: {
    DataTable,
    Drawer,
    Column,
    PrimeVueButton: Button,
  },
  emits: ['close'],
  props: {
    data: {
      type: Array as PropType<DataTableProps['value']>,
      required: true,
    },
    columns: {
      type: Array as PropType<string[]>,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const isVisible = ref(true)
    const dataTable = ref()

    const handleDownloadClicked = () => {
      dataTable.value.exportCSV()
    }
    return { isVisible, dataTable, handleDownloadClicked, ...props }
  },
})
</script>

<style scoped></style>
