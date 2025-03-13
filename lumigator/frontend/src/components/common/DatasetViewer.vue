<template>
  <Drawer v-model:visible="isVisible" :position="'full'" @hide="$emit('close', $event)">
    <template #header>
      <div class="title-slot"><slot name="title"></slot></div>
      <PrimeVueButton
        type="button"
        icon="pi pi-download"
        size="small"
        label="Download"
        rounded
        severity="secondary"
        :variant="'text'"
        class="table-download-button"
        aria-label="download"
        @click="handleDownloadClicked"
      ></PrimeVueButton>
    </template>
    <TableView
      :data="data"
      :columns="columns"
      :downloadFileName="downloadFileName"
      :isEditable="isEditable"
      :showRowNumber="showRowNumber"
      :isSearchEnabled="isSearchEnabled"
      ref="dataTable"
    />
  </Drawer>
</template>

<script lang="ts">
import { Button, Drawer, type DataTableProps } from 'primevue'
import { defineComponent, ref, type PropType } from 'vue'
import TableView from './TableView.vue'

export default defineComponent({
  name: 'DatasetViewer',
  components: {
    TableView,
    Drawer,
    PrimeVueButton: Button,
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
    const handleDownloadClicked = () => {
      dataTable.value.exportCSV()
    }
    return {
      isVisible,
      handleDownloadClicked,
      dataTable,
      ...props,
    }
  },
})
</script>

<style lang="scss" scoped>
@use '@/styles/mixins';
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
