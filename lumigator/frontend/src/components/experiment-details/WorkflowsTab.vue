<template>
  <div class="wrapper">
    <div class="header">
      <div class="header-actions">
        <Button
          severity="secondary"
          rounded
          :disabled="isViewResultsDisabled"
          label="View All Results"
          @click="handleViewAllResultsClicked"
        ></Button>
        <!-- <Button
          severity="secondary"
          rounded
          label="Add Model"
          icon="pi pi-plus"
          @click="handleAddModelClicked"
        ></Button> -->
      </div>
    </div>
    <div :class="{ 'no-data': experiment.workflows.length === 0 }">
      <l-experiments-empty
        v-if="experiment.workflows.length === 0"
        instructions="Model runs are a logical sequence of inference and evaluation jobs that run sequentially to evaluate an LLM with a given set of parameters."
        :button-text="'Add Model Run'"
        @l-add-experiment="handleAddModelClicked"
      />
    </div>
    <TableView
      v-if="experiment.workflows.length > 0"
      :columns="columns"
      :data="tableData"
      :columnStyles="columnStyles"
      @row-click="onWorkflowClicked"
      :is-search-enabled="false"
      :has-column-toggle="false"
    >
      <template #options="slotProps">
        <Button
          icon="pi pi-trash"
          @click="handleDeleteWorkflowClicked(slotProps.data)"
          v-tooltip.bottom="'Delete'"
          severity="secondary"
          variant="text"
          rounded
          aria-label="Delete"
        ></Button>
        <Button
          icon="pi pi-file"
          @click="handleViewLogsClicked(slotProps.data)"
          v-tooltip.bottom="'Logs'"
          severity="secondary"
          variant="text"
          rounded
          aria-label="View logs"
        ></Button>
        <Button
          icon="pi pi-download"
          @click="handleDownloadResultsClicked(slotProps.data)"
          v-tooltip.bottom="'Download results'"
          severity="secondary"
          variant="text"
          :disabled="slotProps.data.status !== WorkflowStatus.SUCCEEDED"
          rounded
          aria-label="Download results"
        ></Button>
      </template>
    </TableView>
    <l-experiments-drawer
      v-if="showDrawer"
      ref="experimentsDrawer"
      :header="getDrawerHeader()"
      :position="showLogs ? 'bottom' : 'full'"
      @l-drawer-closed="handleDrawerClosed"
    >
      <l-experiment-results
        v-if="showExpResults && experimentResults && experimentResults.length"
        :results="experimentResults"
      />
      <l-experiment-logs :logs="clickedWorkflowLogs" v-if="showLogs" />
    </l-experiments-drawer>
  </div>
</template>

<script setup lang="ts">
import { WorkflowStatus, type Workflow } from '@/types/Workflow'
import type { Experiment } from '@/types/Experiment'
import { computed, ref, type Ref } from 'vue'
import TableView from '../common/TableView.vue'
import { Button, useConfirm, useToast, type DataTableRowClickEvent } from 'primevue'
import LExperimentsDrawer from '../experiments/LExperimentsDrawer.vue'
import LExperimentResults from '../experiments/LExperimentResults.vue'
import {
  getExperimentResults,
  type TableDataForExperimentResults,
} from '@/helpers/getExperimentResults'
import { useModelStore } from '@/stores/modelsStore'
import { storeToRefs } from 'pinia'
import LExperimentLogs from '../experiments/LExperimentLogs.vue'
import { useMutation, useQuery } from '@tanstack/vue-query'
import { workflowsService } from '@/sdk/workflowsService'
import { getAxiosError } from '@/helpers/getAxiosError'
import { downloadContent } from '@/helpers/downloadContent'
import LExperimentsEmpty from '../experiments/LExperimentsEmpty.vue'

const props = defineProps<{
  experiment: Experiment
}>()
const emit = defineEmits(['add-model-run-clicked'])

const showDrawer = ref(false)
const showLogs = ref(false)
const showExpResults = ref(false)
const getDrawerHeader = () => {
  return showLogs.value ? 'Logs' : `Experiment: ${props.experiment.name}`
}

const handleDrawerClosed = () => {
  showDrawer.value = false
  showLogs.value = false
  showExpResults.value = false
}
const toast = useToast()
const confirm = useConfirm()

const modelsStore = useModelStore()
const { models } = storeToRefs(modelsStore)
const logsItem = ref()

const workflowId = computed(() => logsItem.value?.id)
const workflowLogsQuery = useQuery({
  queryKey: computed(() => ['workflowLogs', workflowId]),
  placeholderData: [],
  initialData: [],
  queryFn: async () => {
    if (!logsItem.value) return null
    return workflowsService.fetchLogs(logsItem.value.id)
  },
  refetchInterval: 3000,
  enabled: computed(() => !!logsItem.value),
  select: (data) => data.logs.split('\n'),
})

const clickedWorkflowLogs = computed(() => workflowLogsQuery.data.value || [])

const deleteWorkflowMutation = useMutation({
  mutationFn: workflowsService.deleteWorkflow,
  onMutate: () => {
    toast.add({
      group: 'br',
      life: 3000,
      severity: 'info',
      summary: 'Deleting workflow',
      detail: 'Deleting workflow...',
    })
  },
  onError: (error) => {
    toast.add({
      group: 'br',
      severity: 'error',
      summary: 'Error',
      detail: getAxiosError(error),
    })
  },
  onSuccess: () => {
    toast.add({
      group: 'br',
      life: 3000,
      severity: 'success',
      summary: 'Success',
      detail: 'Workflow deleted successfully',
    })
  },
})

const onWorkflowClicked = (item: DataTableRowClickEvent) => {
  if (item.data.status === WorkflowStatus.SUCCEEDED) {
    handleViewAllResultsClicked()
  }
}

const columns = ['model', 'run title', 'prompt', 'created_at', 'status', 'options']
const tableData = computed(() => {
  return props.experiment.workflows.map((workflow: Workflow) => {
    return {
      // id: workflow.id,
      // name: workflow.name,
      ...workflow,
      model: workflow.model,
      created_at: workflow.created_at,
      'run title': workflow.name,
      prompt: workflow.system_prompt,

      // name: workflow.name,
      status: workflow.status,
      options: 'options',
    }
  })
})
const experimentResults: Ref<TableDataForExperimentResults[]> = ref([])
const columnStyles = computed(() => {
  return {
  }
})

const handleDeleteWorkflowClicked = (workflow: (typeof tableData.value)[0]) => {
  confirm.require({
    message: `This will permanently delete this model run from your experiment.`,
    header: `Delete Model Run?`,
    icon: 'pi pi-info-circle',
    rejectLabel: 'Cancel',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',

      outlined: true,
    },
    acceptProps: {
      label: 'Delete Model Run',
      severity: 'danger',
    },
    accept: async () => {
      deleteWorkflowMutation.mutate(workflow.id)
    },
    reject: () => {},
  })
}

const isViewResultsDisabled = computed(
  () =>
    !props.experiment.workflows.some((workflow) => workflow.status === WorkflowStatus.SUCCEEDED),
)
const handleViewLogsClicked = async (workflow: (typeof tableData.value)[0]) => {
  logsItem.value = workflow
  showLogs.value = true
  showDrawer.value = true
}

const handleDownloadResultsClicked = async (workflow: (typeof tableData.value)[0]) => {
  const blob = await workflowsService.downloadResults(workflow.id)
  downloadContent(blob, `${workflow.name}_results.json`)
}

const handleAddModelClicked = () => {
  emit('add-model-run-clicked')
}

const handleViewAllResultsClicked = async () => {
  experimentResults.value = await getExperimentResults(props.experiment, models.value)

  logsItem.value = undefined
  showExpResults.value = true
  showLogs.value = false
  showDrawer.value = true
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

.no-data {
  display: grid;
  place-content: center;
  margin-top: 5rem;
}
</style>
