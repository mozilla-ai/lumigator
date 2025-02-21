<template>
  <DataTable
    :value="tableData"
    dataKey="id"
    :showHeaders="false"
    :tableStyle="columnStyles"
    :pt="{ root: 'l-job-table', tableContainer: 'width-100' }"
    @row-click="handleRowClick"
  >
    <Column :style="columnStyles.expander"></Column>
    <Column :style="columnStyles.name">
      <template #body="slotProps">
        {{ shortenedModel(slotProps.data.model) }}
      </template>
    </Column>
    <Column field="created" header="created" :style="columnStyles.created" sortable>
      <template #body="slotProps">
        {{ formatDate(slotProps.data.created_at) }}
      </template>
    </Column>
    <Column field="status" header="status">
      <template #body="slotProps">
        <div>
          <Tag
            v-if="slotProps.data.status === WorkflowStatus.SUCCEEDED"
            severity="success"
            rounded
            :value="slotProps.data.status"
            :pt="{ root: 'l-job-table__tag' }"
          />
          <Tag
            v-else-if="slotProps.data.status === WorkflowStatus.FAILED"
            severity="danger"
            rounded
            :value="slotProps.data.status"
            :pt="{ root: 'l-job-table__tag' }"
          />
          <Tag
            v-else
            severity="warn"
            rounded
            :value="slotProps.data.status"
            :pt="{ root: 'l-job-table__tag' }"
          />
        </div>
      </template>
    </Column>
    <Column header="options">
      <template #body="slotProps">
        <span
          class="pi pi-fw pi-ellipsis-h l-experiment-table__options-trigger"
          style="pointer-events: all"
          aria-haspopup="true"
          aria-controls="optionsMenu"
          @click.stop="toggleOptionsMenu($event, slotProps.data)"
        >
        </span>
      </template>
    </Column>
    <Menu id="options_menu" ref="optionsMenu" :model="options" :popup="true"> </Menu>
  </DataTable>
</template>

<script lang="ts" setup>
import DataTable, { type DataTableRowClickEvent } from 'primevue/datatable'
import Tag from 'primevue/tag'
import Column from 'primevue/column'
// import { storeToRefs } from 'pinia'
// import { useExperimentStore } from '@/stores/experimentsStore'
import { formatDate } from '@/helpers/formatDate'
import { WorkflowStatus, type Workflow } from '@/types/Workflow'
import { ref, type PropType } from 'vue'
import type { MenuItem, MenuItemCommandEvent } from 'primevue/menuitem'
import { Menu } from 'primevue'
// import type { Job } from '@/types/Job'
// const experimentStore = useExperimentStore()
// const { jobs } = storeToRefs(experimentStore)
defineProps({
  tableData: {
    type: Array as PropType<Workflow[]>,
    required: true,
  },
  columnStyles: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['l-job-selected', 'delete-workflow-clicked'])
const clickedItem = ref<Workflow>()
const shortenedModel = (path: string) => (path.length <= 30 ? path : `${path.slice(0, 30)}...`)

const optionsMenu = ref()
const options = ref<MenuItem[]>([
  {
    label: 'View Results',
    icon: 'pi pi-chart-bar',
    disabled: false,
    command: () => {
      // emit('l-experiment-selected', focusedItem.value)
    },
  },
  {
    label: 'Download Results',
    icon: 'pi pi-download',
    disabled: false,
    command: () => {
      // emit('l-download-experiment', focusedItem.value)
    },
  },
  {
    label: 'Delete Model Run',
    icon: 'pi pi-trash',
    style: 'color: red;',
    disabled: false,
    command: (e: MenuItemCommandEvent) => {
      emit('delete-workflow-clicked', clickedItem.value)
    },
  },
])

const toggleOptionsMenu = (event: MouseEvent, selectedItem: Workflow) => {
  clickedItem.value = selectedItem
  optionsMenu.value.toggle(event, selectedItem)
}

function handleRowClick(event: DataTableRowClickEvent) {
  clickedItem.value = event.data
  emit('l-job-selected', event.data)
}
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-job-table {
  $root: &;
  width: 100%;
  display: flex;
  place-content: center;

  .p-datatable-table-container {
    [class*='p-row-'] {
      background-color: $l-main-bg;
    }
  }

  &__tag {
    color: $l-grey-100;
    font-size: $l-font-size-sm;
    line-height: 1;
    font-weight: $l-font-weight-normal;
    text-transform: uppercase;
  }
}
</style>

<style lang="scss">
@use '@/styles/variables' as *;

.l-job-table {
  $root: &;
  width: 100%;
  display: flex;
  place-content: center;

  .p-datatable-table-container {
    border: none;
  }

  .p-datatable-table-container [class*='p-row-'] {
    background-color: $l-main-bg;
  }
}
</style>
