<template>
  <Drawer
    v-model:visible="isVisible"
    :header="title"
    :position="'full'"
    @hide="$emit('close', $event)"
  >
    <DataTable
      :value="data"
      :reorderableColumns="true"
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
import { Column, DataTable, Drawer, type DataTableProps } from 'primevue'
import { defineComponent, ref, type PropType } from 'vue'

export default defineComponent({
  components: {
    DataTable,
    Drawer,
    Column,
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
  setup() {
    const isVisible = ref(true)
    return { isVisible }
  },
})
</script>

<style scoped></style>
