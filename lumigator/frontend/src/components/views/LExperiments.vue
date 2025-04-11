<template>
  <div class="l-experiments" :class="{ 'no-data': experiments.length === 0 }">
    <l-experiments-empty
      v-if="experiments.length === 0"
      @l-add-experiment="handleCreateExperimentClicked()"
    />
    <div v-if="experiments.length > 0" class="l-experiments__header-container">
      <l-page-header
        title="Experiments"
        :description="headerDescription"
        button-label="Create Experiment"
        :column="experiments.length === 0"
        @l-header-action="handleCreateExperimentClicked()"
      />
    </div>
    <div v-if="experiments.length > 0" class="l-experiments__table-container">
      <l-experiment-table
        :experiments="experiments"
        @l-experiment-selected="handleExperimentClicked($event)"
        @delete-option-clicked="handleDeleteButtonClicked"
        @view-experiment-results-clicked="onShowExperimentResults($event)"
      />
    </div>
    <l-experiments-drawer
      v-if="showDrawer"
      ref="experimentsDrawer"
      :header="getDrawerHeader()"
      :position="showLogs ? 'bottom' : 'full'"
      @l-drawer-closed="resetDrawerContent()"
    >
      <l-experiment-results
        v-if="showExpResults && selectedExperimentResults && selectedExperimentResults.length"
        :results="selectedExperimentResults"
      />
      <!-- <l-experiment-results
        v-if="selectedWorkflowResults && showJobResults"
        :results="selectedWorkflowResults"
      /> -->
      <!-- <l-experiment-logs :logs="workflowLogs" v-if="showLogs" /> -->
    </l-experiments-drawer>
    <CreateExperimentModal
      :selectedDataset="selectedDataset"
      @close="closeExperimentForm"
      v-if="isNewExperimentFormVisible"
    />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, type Ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasetsStore'
import { useModelStore } from '@/stores/modelsStore'
import LPageHeader from '@/components/layout/LPageHeader.vue'
import LExperimentTable from '@/components/experiments/LExperimentTable.vue'
import LExperimentsDrawer from '@/components/experiments/LExperimentsDrawer.vue'
import LExperimentResults from '@/components/experiments/LExperimentResults.vue'
import LExperimentsEmpty from '@/components/experiments/LExperimentsEmpty.vue'
import type { Experiment } from '@/types/Experiment'
import { experimentsService } from '@/sdk/experimentsService'
import {
  getExperimentResults,
  type TableDataForExperimentResults,
} from '@/helpers/getExperimentResults'
import { useConfirm, useToast } from 'primevue'
import { useRouter } from 'vue-router'
import CreateExperimentModal from '../experiments/CreateExperimentModal.vue'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { retrieveStatus } from '@/helpers/retrieveStatus'
import { getAxiosError } from '@/helpers/getAxiosError'

const datasetStore = useDatasetStore()
const modelStore = useModelStore()
const { selectedDataset } = storeToRefs(datasetStore)
const { models } = storeToRefs(modelStore)

const selectedExperimentResults: Ref<TableDataForExperimentResults[]> = ref([])

const selectedExperiment = ref<Experiment | undefined>()

const router = useRouter()
const showDrawer = ref(false)
const experimentsDrawer = ref()
const showLogs = ref()
const showExpResults = ref()
const showJobResults = ref()
const headerDescription = ref(`Experiments are a logical sequence of inference and
evaluation tasks that run sequentially to evaluate an LLM.`)

const isNewExperimentFormVisible = ref(false)

const closeExperimentForm = () => {
  isNewExperimentFormVisible.value = false
  datasetStore.setSelectedDataset(undefined)
}

const getDrawerHeader = () => {
  return showLogs.value ? 'Logs' : `Experiment: ${selectedExperiment.value?.name}`
}

const { data: experiments, refetch } = useQuery({
  queryKey: ['experiments'],
  queryFn: experimentsService.fetchExperiments,
  initialData: [],
  placeholderData: [],
  select: (data) =>
    data.map((experiment: Experiment) => {
      return {
        ...experiment,
        status: retrieveStatus(experiment) || 'empty',
      }
    }),
})

const queryClient = useQueryClient()

const handleCreateExperimentClicked = () => {
  selectedExperiment.value = undefined
  isNewExperimentFormVisible.value = true
}

const handleExperimentClicked = (experiment: Experiment) => {
  selectedExperiment.value = experiments.value.find((e: Experiment) => e.id === experiment.id)

  router.push(`/experiments/${experiment.id}`)
}

const onShowExperimentResults = async (experiment: Experiment) => {
  selectedExperimentResults.value = await getExperimentResults(experiment, models.value)
  selectedExperiment.value = experiment
  showExpResults.value = true
  showDrawer.value = true
}

const confirm = useConfirm()
const toast = useToast()

const deleteExperimentMutation = useMutation({
  mutationFn: experimentsService.deleteExperiment,
  onMutate: () => {
    toast.add({
      group: 'br',
      severity: 'info',
      summary: 'Deleting experiment',
      detail: 'Deleting experiment',
      life: 3000,
    })
  },
  onError: (error) => {
    toast.add({
      group: 'br',
      severity: 'error',
      summary: 'Error deleting experiment',
      detail: getAxiosError(error),
    })
  },
  onSuccess: () => {
    toast.add({
      group: 'br',
      severity: 'success',
      summary: 'Experiment deleted',
      detail: 'Experiment deleted',
      life: 3000,
    })
    router.push('/experiments')
  },
})

async function handleDeleteButtonClicked(selectedItem: Experiment) {
  const experiment = selectedItem || selectedExperiment.value
  if (!experiment) {
    return
  }

  confirm.require({
    message: `This will permanently delete the experiment and all its model runs.`,
    header: `Delete  Experiment?`,
    icon: 'pi pi-info-circle',
    rejectLabel: 'Cancel',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      // style: 'color: #fff; background-color: #363636; border: none; border-radius: 46px;',
      outlined: true,
    },
    acceptProps: {
      label: 'Delete Experiment',
      // style: 'color: #fff; background-color: #9F1A1C; border: none; border-radius: 46px; ',
      severity: 'danger',
    },
    accept: async () => {
      deleteExperimentMutation.mutate(experiment.id)
      // refetch experiments to remove it from the table
      await queryClient.invalidateQueries({
        queryKey: ['experiments'],
      })
    },
    reject: () => {},
  })
}
// function getJobRuntime(jobId: string) {
//   const job = jobs.value.find((job) => job.id === jobId)
//   return job ? job.runTime : undefined
// }

const resetDrawerContent = () => {
  showExpResults.value = false
  showJobResults.value = false
  showLogs.value = false
  showDrawer.value = false
}

onMounted(async () => {
  await Promise.all([modelStore.fetchModels(), refetch()])

  if (selectedDataset.value) {
    handleCreateExperimentClicked()
  }
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-experiments {
  $root: &;
  max-width: $l-main-width;
  width: 100%;
  margin: 0 auto;

  &__header-container {
    margin: auto;
    padding: $l-spacing-1;
    display: grid;
    place-items: center;
    width: 100%;
  }

  &__table-container {
    padding: $l-spacing-1;
    display: grid;
    width: 100%;
  }
  &.no-data {
    max-width: $l-main-width;
    padding: $l-spacing-1;
    display: grid;
    place-content: center;

    .l-experiments__header-container {
      margin-top: 120px;
    }
  }
}
</style>
