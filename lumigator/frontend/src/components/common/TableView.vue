<template>
  <DataTable
    :class="showGridlines ? '' : 'gridlines'"
    :value="reactiveData"
    ref="dataTable"
    :reorderableColumns="true"
    :removableSort="true"
    :scrollable="true"
    scrollHeight="flex"
    :loading="isLoading"
    :sort-field="sortField"
    :sort-order="sortOrder"
    :resizableColumns="false"
    :columnResizeMode="'fit'"
    :showGridlines="showGridlines"
    :stripedRows="false"
    :exportFilename="downloadFileName"
    :globalFilterFields="columns"
    v-model:filters="filters"
    :editMode="isEditable ? 'cell' : undefined"
    v-model:expandedRows="expandedRows"
    @rowExpand="onRowExpand"
    @rowCollapse="onRowCollapse"
    @row-click="$emit('row-click', $event)"
    @cell-edit-complete="onCellEditComplete"
    @cell-edit-cancel="onCellEditCancel"
  >
    <template #header v-if="hasColumnToggle || isSearchEnabled">
      <div style="display: flex; gap: 2rem; justify-content: flex-end">
        <MultiSelect
          v-if="hasColumnToggle"
          :modelValue="selectedColumns"
          :options="columns"
          :size="'small'"
          :selectedItemsLabel="`${selectedColumns.length} Columns Selected`"
          :max-selected-labels="0"
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
          <InputText v-model="filters['global'].value" placeholder="Search" />
        </IconField>
      </div>
    </template>
    <template #empty v-if="isSearchEnabled"> No items found. </template>
    <Column expander style="width: 10" v-if="hasSubRows" />
    <Column
      v-if="showRowNumber && selectedColumns.length"
      key="rowNumber"
      field="rowNumber"
      header=""
      sortable
    ></Column>
    <Column
      v-for="col in selectedColumns"
      :sortable="col !== 'options'"
      :key="col"
      :field="col"
      :header="col"
      :style="
        hasEqualColumnSizes
          ? `width: ${selectedColumns.length > 0 ? (1 / selectedColumns.length) * 100 : 100}% `
          : undefined
      "
    >
      <template #body="slotProps" v-if="col === 'status' || col === 'options'">
        <Tag
          v-if="col === 'status'"
          :severity="
            slotProps.data.status === WorkflowStatus.SUCCEEDED
              ? 'success'
              : slotProps.data.status === WorkflowStatus.FAILED
                ? 'danger'
                : 'warn'
          "
          rounded
          :value="slotProps.data.status"
          class="tag"
        >
          {{ slotProps.data.status }}
        </Tag>
        <div class="options" v-if="col === 'options'">
          <slot name="options" :data="slotProps.data"></slot>
        </div>
      </template>
      <template #editor="{ data, field }" v-if="isEditable">
        <PrimeVueTextarea v-model="data[field]" autoResize autofocus fluid></PrimeVueTextarea>
      </template>
    </Column>
    <template #expansion="slotProps">
      <TableView
        :data="slotProps.data.subRows"
        :isSearchEnabled="true"
        :hasColumnToggle="false"
        :showRowNumber="true"
        :downloadFileName="downloadFileName"
        :isEditable="isEditable"
        ref="subTable"
        :columns="
          Object.keys(slotProps.data.subRows[0]).filter(
            (key) => key !== 'subRows' && key !== 'rowNumber',
          )
        "
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
  Tag,
  Textarea,
  type DataTableCellEditCancelEvent,
  type DataTableCellEditCompleteEvent,
} from 'primevue'
import { FilterMatchMode } from '@primevue/core/api'
import { defineComponent, ref, toRef, type PropType } from 'vue'
import { WorkflowStatus } from '@/types/Workflow'

export default defineComponent({
  name: 'TableView',
  components: {
    DataTable,
    Column,
    Tag,
    // PrimeVueButton: Button,
    PrimeVueTextarea: Textarea,
    IconField,
    InputIcon,
    InputText,
    MultiSelect,
  },
  props: {
    sortField: {
      type: String,
      default: undefined,
    },
    sortOrder: {
      type: Number,
      default: undefined,
    },
    isLoading: {
      type: Boolean,
      default: false,
    },
    showGridlines: {
      type: Boolean,
      default: true,
    },
    hasEqualColumnSizes: {
      type: Boolean,
      default: false,
    },
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
      type: Array as PropType<Record<string, unknown>[]>,
      required: true,
    },
    columns: {
      type: Array as PropType<string[]>,
      required: true,
    },
  },
  exposes: ['exportCSV'],
  emits: ['row-click'],
  setup(props) {
    const reactiveData = toRef(props, 'data')
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
      WorkflowStatus,
      onCellEditCancel,
      filters,
      // allColumns,
      selectedColumns,
      onToggle,
      expandedRows,
      onRowExpand,
      onRowCollapse,
      expandAll,
      collapseAll,
      exportCSV,
      reactiveData,
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

::v-deep(.p-datatable-header) {
  padding-right: 0;
  border: none;
}

.options {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.tag {
  color: var(--l-grey-100);
  font-size: var(--l-font-size-sm);
  line-height: 1;
  font-weight: var(--l-font-weight-normal);
  text-transform: uppercase;
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
