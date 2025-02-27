<template>
  <Drawer v-model:visible="isVisible" :position="'full'" @hide="$emit('close', $event)">
    <template #header>
      <slot name="title"></slot>
      <PrimeVueButton
        type="button"
        icon="pi pi-download"
        label="Downlaod"
        rounded
        severity="secondary"
        :variant="'text'"
        style="margin-left: auto"
        aria-label="download"
        @click="handleDownloadClicked"
      ></PrimeVueButton>
    </template>
    <DataTable
      :value="data"
      :reorderableColumns="true"
      ref="dataTable"
      :removableSort="true"
      :scrollable="true"
      scrollHeight="flex"
      :resizableColumns="false"
      :columnResizeMode="'fit'"
      :showGridlines="true"
      :stripedRows="false"
      :exportFilename="downloadFileName"
      :editMode="isEditable ? 'cell' : undefined"
      @cell-edit-complete="onCellEditComplete"
      @cell-edit-cancel="onCellEditCancel"
    >
      <Column
        v-for="col in columns"
        sortable
        :key="col"
        :field="col"
        :header="col"
        :style="`width: ${(1 / columns.length) * 100}%`"
      >
        <template #editor="{ data, field }">
          <PrimeVueTextarea v-model="data[field]" autoResize autofocus fluid></PrimeVueTextarea>
        </template>
      </Column>
    </DataTable>
  </Drawer>
</template>

<script lang="ts">
import {
  Button,
  Column,
  DataTable,
  Drawer,
  Textarea,
  type DataTableCellEditCancelEvent,
  type DataTableCellEditCompleteEvent,
  type DataTableProps,
} from 'primevue'
import { defineComponent, ref, type PropType } from 'vue'

export default defineComponent({
  name: 'DatasetViewer',
  components: {
    DataTable,
    Drawer,
    Column,
    PrimeVueButton: Button,
    PrimeVueTextarea: Textarea,
  },
  emits: ['close'],
  props: {
    downloadFileName: {
      type: String,
      required: true,
    },
    isEditable: {
      type: Boolean,
      default: false,
    },
    data: {
      type: Array as PropType<DataTableProps['value']>,
      required: true,
    },
    columns: {
      type: Array as PropType<string[]>,
      required: true,
    },
  },
  setup(props) {
    const isVisible = ref(true)
    const dataTable = ref()

    const handleDownloadClicked = () => {
      dataTable.value.exportCSV()
    }

    const onCellEditComplete = (event: DataTableCellEditCompleteEvent) => {
      const { data, newValue, field } = event

      data[field] = newValue
    }

    const onCellEditCancel = (event: DataTableCellEditCancelEvent) => {
      // prevent esc key from closing the whole modal
      event.originalEvent.stopPropagation()
    }

    return {
      isVisible,
      dataTable,
      handleDownloadClicked,
      onCellEditComplete,
      onCellEditCancel,
      ...props,
    }
  },
})
</script>

<style scoped></style>
