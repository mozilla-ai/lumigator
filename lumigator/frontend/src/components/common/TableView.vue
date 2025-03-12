<template>
  <DataTable
    class="gridlines"
    :value="data"
    ref="dataTable"
    :reorderableColumns="true"
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
    v-model:expandedRows="expandedRows"
    @rowExpand="onRowExpand"
    @rowCollapse="onRowCollapse"
    @cell-edit-complete="onCellEditComplete"
    @cell-edit-cancel="onCellEditCancel"
  >
    <template #header>
      <div style="display: flex; gap: 2rem; justify-content: space-between">
        <MultiSelect
          v-if="hasColumnToggle"
          :modelValue="selectedColumns"
          :options="columns"
          @update:modelValue="onToggle"
          display="chip"
          placeholder="Select Columns"
        >
        </MultiSelect>

        <!-- <PrimeVueButton text icon="pi pi-plus" label="Expand All" @click="expandAll" />
           <PrimeVueButton text icon="pi pi-minus" label="Collapse All" @click="collapseAll" /> -->

        <IconField v-if="isSearchEnabled">
          <InputIcon>
            <i class="pi pi-search"></i>
          </InputIcon>
          <InputText v-model="filters['global'].value" placeholder="Keyword Search" />
        </IconField>
      </div>
    </template>
    <template #empty v-if="isSearchEnabled"> No items found. </template>
    <Column expander style="width: 10" v-if="hasSubRows" />
    <Column v-if="showRowNumber" key="rowNumber" field="rowNumber" header="" sortable></Column>
    <Column
      v-for="col in selectedColumns"
      sortable
      :key="col"
      :field="col"
      :header="col"
      :style="`width: ${(1 / selectedColumns.length) * 100}%`"
    >
      <template #editor="{ data, field }" v-if="isEditable">
        <PrimeVueTextarea v-model="data[field]" autoResize autofocus fluid></PrimeVueTextarea>
      </template>
    </Column>
    <template #expansion="slotProps">
      <TableView
        :data="slotProps.data.subRows"
        :isSearchEnabled="false"
        :hasColumnToggle="false"
        :showRowNumber="false"
        :downloadFileName="downloadFileName"
        :isEditable="isEditable"
        :columns="Object.keys(slotProps.data.subRows[0]).filter((key) => key !== 'subRows')"
      />
    </template>
  </DataTable>
</template>
<script lang="ts">
import {
  // Button,
  Column,
  DataTable,
  IconField,
  InputIcon,
  InputText,
  MultiSelect,
  Textarea,
  type DataTableCellEditCancelEvent,
  type DataTableCellEditCompleteEvent,
  type DataTableProps,
} from 'primevue'
import { FilterMatchMode } from '@primevue/core/api'
import { defineComponent, ref, type PropType } from 'vue'

export default defineComponent({
  name: 'TableView',
  components: {
    DataTable,
    Column,
    // PrimeVueButton: Button,
    PrimeVueTextarea: Textarea,
    IconField,
    InputIcon,
    InputText,
    MultiSelect,
  },
  props: {
    isSearchEnabled: {
      type: Boolean,
      default: true,
    },
    hasColumnToggle: {
      type: Boolean,
      default: true,
    },
    showRowNumber: {
      type: Boolean,
      default: false,
    },
    downloadFileName: {
      type: String,
      default: 'download',
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
  exposes: ['exportCSV'],
  setup(props) {
    const isVisible = ref(true)
    const dataTable = ref()
    const selectedColumns = ref(props.columns)
    const filters = ref({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    })
    const handleDownloadClicked = () => {
      dataTable.value.exportCSV()
    }
    const expandedRows = ref()

    const exportCSV = () => {
      dataTable.value.exportCSV()
    }

    const hasSubRows = props.data!.some((item) => item.subRows)

    const onCellEditComplete = (event: DataTableCellEditCompleteEvent) => {
      const { data, newValue, field } = event

      data[field] = newValue
    }

    const onCellEditCancel = (event: DataTableCellEditCancelEvent) => {
      // prevent esc key from closing the whole modal
      event.originalEvent.stopPropagation()
    }

    const onToggle = (selected: string[]) => {
      selectedColumns.value = props.columns.filter((col) => selected.includes(col))
    }

    const onRowExpand = () => {
      // toast.add({ severity: 'info', summary: 'Product Expanded', detail: event.data.name, life: 3000 });
    }
    const onRowCollapse = () => {
      // toast.add({ severity: 'success', summary: 'Product Collapsed', detail: event.data.name, life: 3000 });
    }
    const expandAll = () => {
      expandedRows.value = (props.data || []).reduce(
        (acc, item, index) => (acc[index] = true) && acc,
        {},
      )
    }
    const collapseAll = () => {
      expandedRows.value = undefined
    }

    return {
      isVisible,
      hasSubRows,
      dataTable,
      handleDownloadClicked,
      onCellEditComplete,
      onCellEditCancel,
      filters,
      selectedColumns,
      onToggle,
      expandedRows,
      onRowExpand,
      onRowCollapse,
      expandAll,
      collapseAll,
      exportCSV,
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

// global css overrides the cursor to be pointer, reset it back
:deep(.p-datatable-table-container) {
  [class*='p-row-'] {
    cursor: unset;
  }
}
</style>
