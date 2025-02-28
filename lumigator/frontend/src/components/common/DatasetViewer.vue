<template>
  <Drawer v-model:visible="isVisible" :position="'full'" @hide="$emit('close', $event)">
    <template #header>
      <div class="title-slot"><slot name="title"></slot></div>
      <PrimeVueButton
        type="button"
        icon="pi pi-download"
        size="small"
        label="Downlaod"
        rounded
        severity="secondary"
        :variant="'text'"
        class="table-download-button"
        aria-label="download"
        @click="handleDownloadClicked"
      ></PrimeVueButton>
    </template>
    <DataTable
      class="gridlines"
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
      :globalFilterFields="columns"
      v-model:filters="filters"
      :editMode="isEditable ? 'cell' : undefined"
      @cell-edit-complete="onCellEditComplete"
      @cell-edit-cancel="onCellEditCancel"
    >
      <template #header v-if="isSearchEnabled">
        <div>
          <IconField>
            <InputIcon>
              <i class="pi pi-search"></i>
            </InputIcon>
            <InputText v-model="filters['global'].value" placeholder="Keyword Search" />
          </IconField>
        </div>
      </template>
      <template #empty> No items found. </template>
      <Column v-if="showRowNumber" key="rowNumber" field="rowNumber" header="" sortable></Column>
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
  IconField,
  InputIcon,
  InputText,
  Textarea,
  type DataTableCellEditCancelEvent,
  type DataTableCellEditCompleteEvent,
  type DataTableProps,
} from 'primevue'
import { FilterMatchMode } from '@primevue/core/api'
import { defineComponent, ref, type PropType } from 'vue'

export default defineComponent({
  name: 'DatasetViewer',
  components: {
    DataTable,
    Drawer,
    Column,
    PrimeVueButton: Button,
    PrimeVueTextarea: Textarea,
    IconField,
    InputIcon,
    InputText,
  },
  emits: ['close'],
  props: {
    isSearchEnabled: {
      type: Boolean,
      default: true,
    },
    showRowNumber: {
      type: Boolean,
      default: false,
    },
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
    const filters = ref({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    })
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
      filters,
      ...props,
    }
  },
})
</script>

<style lang="scss" scoped>
@use '@/styles/mixins';

/* make the sort icon smaller */
::v-deep(.p-datatable-sort-icon) {
  width: 10px;
  height: 10px;
}

.title-slot {
  @include mixins.paragraph;
}

.table-download-button {
  @include mixins.caption;
  margin-left: auto;
  margin-right: 1.5rem;
  gap: 0.125rem;
}
</style>
