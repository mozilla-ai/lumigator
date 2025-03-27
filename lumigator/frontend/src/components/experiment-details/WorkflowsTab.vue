<template>
  <div class="wrapper">
    <div class="header">
      <div class="header-actions">
        <Button
          severity="secondary"
          rounded
          label="View All Results"
          @click="handleViewAllResultsClicked"
        ></Button>
        <Button
          severity="secondary"
          rounded
          label="Add Model"
          icon="pi pi-plus"
          @click="handleAddModelClicked"
        ></Button>
      </div>
    </div>
    <TableView
      v-if="workflows.length > 0"
      :columns="columns"
      :data="tableData"
      :columnStyles="columnStyles"
      @row-clicked="onWorkflowSelected"
      :is-search-enabled="false"
      :has-column-toggle="false"
    >
      <template #options="slotProps">
        <Button
          icon="pi pi-trash"
          @click="handleDeleteWorkflowClicked(slotProps.data)"
          severity="secondary"
          variant="text"
          rounded
          aria-label="Delete"
        ></Button>
        <Button
          icon="pi pi-table"
          @click="handleViewResultsClicked(slotProps.data)"
          severity="secondary"
          variant="text"
          rounded
          aria-label="View results"
          :disabled="slotProps.data.status !== WorkflowStatus.SUCCEEDED"
        ></Button>
        <Button
          icon="pi pi-download"
          @click="handleDownloadResultsClicked(slotProps.data)"
          severity="secondary"
          variant="text"
          :disabled="slotProps.data.status !== WorkflowStatus.SUCCEEDED"
          rounded
          aria-label="Download results"
        ></Button>
      </template>
    </TableView>
  </div>
</template>

<script setup lang="ts">
import { WorkflowStatus, type Workflow } from '@/types/Workflow'
import type { Experiment } from '@/types/Experiment'
import { computed } from 'vue'
import { useSlidePanel } from '@/composables/useSlidePanel'
import TableView from '../common/TableView.vue'
import { Button } from 'primevue'
import { useRouter } from 'vue-router'

const onWorkflowSelected = (workflow: Workflow) => {
  console.log('workflow selected', workflow)
}

const props = defineProps<{
  workflows: Workflow[]
  experiment: Experiment
}>()
const emit = defineEmits(['add-model-run-clicked'])

const columns = ['model', 'created_at', 'status', 'options']
const tableData = computed(() => {
  return props.workflows.map((workflow: Workflow) => {
    return {
      model: workflow.model,
      created_at: workflow.created_at,
      // name: workflow.name,
      status: workflow.status,
      options: 'options',
    }
  })
})
const { showSlidingPanel } = useSlidePanel()
const columnStyles = computed(() => {
  return {
    // expander: 'width: 4rem',
    // name: showSlidingPanel.value ? 'width: 20rem' : 'width: 26rem',
    // created: 'width: 12rem',
    // status: 'width: 12rem',
    // useCase: 'width: 8rem',
  }
})

const handleDeleteWorkflowClicked = (workflow: Workflow) => {
  console.log('delete workflow clicked', workflow)
}

const handleViewResultsClicked = (workflow: Workflow) => {
  console.log('view results clicked', workflow)
}

const handleDownloadResultsClicked = (workflow: Workflow) => {
  console.log('download results clicked', workflow)
}

const handleAddModelClicked = () => {
  console.log('add model clicked')
  emit('add-model-run-clicked')
}

const handleViewAllResultsClicked = () => {
  console.log('view all results clicked')
}
</script>

<style scoped lang="scss">
.header {
  display: flex;
  justify-content: flex-end;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.wrapper {
  display: flex;
  gap: 1rem;
  flex-direction: column;
}
</style>
