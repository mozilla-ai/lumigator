<template>
  <div class="l-experiment-form">
    <div class="l-experiment-form__header" style="position: sticky; top: 0; z-index: 100">
      <h3>Create Experiment</h3>
      <Button
        icon="pi pi-times"
        severity="secondary"
        rounded
        aria-label="Close"
        class="l-experiment-form__close"
        @click="emit('l-close-form')"
      >
      </Button>
    </div>
    <div class="l-experiment-form__fields">
      <FloatLabel variant="in" size="small" class="l-experiment-form__field">
        <Select
          v-model="experimentType"
          inputId="use_case"
          optionLabel="useCase"
          :options="experimentTypeOptions"
          variant="filled"
          disabled
        >
        </Select>
        <label for="use_case">Use case</label>
      </FloatLabel>

      <p>
        Summarization jobs are evaluated with ROUGE, METEOR, and BERT score, each focusing on
        different aspects of prediction-ground truth similarity.
        <a href="https://mozilla-ai.github.io/lumigator/" target="_blank"
          >Learn more <span class="pi pi-arrow-up-right"></span>
        </a>
      </p>
      <FloatLabel variant="in" class="l-experiment-form__field">
        <Select
          v-model="dataset"
          inputId="dataset"
          optionLabel="filename"
          :options="filteredDatasets"
          variant="filled"
          size="small"
        ></Select>
        <label for="dataset">Select Dataset</label>
      </FloatLabel>
      <FloatLabel variant="in" class="l-experiment-form__field">
        <InputText id="title" v-model="experimentTitle" variant="filled" />
        <label for="title">Experiment Title</label>
      </FloatLabel>
      <FloatLabel variant="in" class="l-experiment-form__field">
        <Textarea
          id="description_input"
          v-model="experimentDescription"
          rows="2"
          style="resize: none"
        ></Textarea>
        <label for="description_input">Experiment description</label>
      </FloatLabel>
      <FloatLabel variant="in" class="l-experiment-form__field">
        <InputNumber id="max_samples" v-model="maxSamples" variant="filled" class="number-input" />
        <label for="max_samples">Maximum samples (optional)</label>
      </FloatLabel>
    </div>
    <div class="l-experiment-form__models-container">
      <h3>Model Selection</h3>
      <div class="l-experiment-form__models">
        <l-model-cards ref="modelSelection" />
      </div>
    </div>
    <div class="l-experiment-form__submit-container">
      <Button
        rounded
        size="small"
        label="Run experiment"
        class="l-page-header__action-btn"
        :disabled="isInvalid"
        @click="triggerExperiment"
      ></Button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, type Ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasetsStore'
import { useExperimentStore } from '@/stores/experimentsStore'
import Button from 'primevue/button'
import FloatLabel from 'primevue/floatlabel'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import LModelCards from '@/components/experiments/LModelCards.vue'
import { useToast } from 'primevue/usetoast'
import type { ToastMessageOptions } from 'primevue'
import type { Dataset } from '@/types/Dataset'
import type { createExperimentWithWorkflowsPayload } from '@/sdk/experimentsService'

const emit = defineEmits(['l-close-form'])

const datasetStore = useDatasetStore()
const experimentStore = useExperimentStore()
const { datasets, selectedDataset } = storeToRefs(datasetStore)

const experimentTypeOptions = ref([{ useCase: 'Summarization' }])
const experimentType = experimentTypeOptions.value[0]
const dataset: Ref<Dataset | undefined> = ref()
const experimentTitle = ref('')
const experimentDescription = ref('')
const maxSamples = ref()
const modelSelection = ref()
const toast = useToast()

const isInvalid = computed(
  () =>
    !experimentTitle.value ||
    !experimentDescription.value ||
    !dataset.value ||
    !modelSelection.value?.selectedModels?.length,
)

const filteredDatasets = computed(() =>
  datasets.value.filter((dataset) => dataset.ground_truth === true),
)

async function triggerExperiment() {
  const experimentPayload: createExperimentWithWorkflowsPayload = {
    name: experimentTitle.value,
    description: experimentDescription.value,
    dataset: dataset.value!.id,
    max_samples: maxSamples.value ? maxSamples.value : 0,
    task: 'summarization',
  }
  const workflows = await experimentStore.createExperimentWithWorkflows(
    experimentPayload,
    modelSelection.value.selectedModels,
  )
  if (workflows.length) {
    // refetch after creating an experiment to update the table
    await experimentStore.fetchAllExperiments()
    emit('l-close-form')
    resetForm()
    toast.add({
      severity: 'secondary',
      summary: `${workflows[0].name} Started`,
      messageicon: 'pi pi-verified',
      group: 'br',
      life: 3000,
    } as ToastMessageOptions & { messageicon: string })
    return
  }
  toast.add({
    severity: 'error',
    summary: `Experiment failed to start`,
    messageicon: 'pi pi-exclamation-triangle',
    group: 'br',
  } as ToastMessageOptions & { messageicon: string })
}

function resetForm() {
  experimentTitle.value = ''
  experimentDescription.value = ''
  dataset.value = undefined
  modelSelection.value.selectedModels = []
  maxSamples.value = undefined
}

onMounted(async () => {
  if (datasets.value?.length === 0) {
    await datasetStore.fetchDatasets()
  }
  if (selectedDataset.value) {
    dataset.value = selectedDataset.value
  }
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-experiment-form {
  $root: &;
  display: flex;
  flex-direction: column;

  p {
    font-size: $l-font-size-sm;
    color: $l-grey-100;
    padding: 0 $l-spacing-sm $l-spacing-1 $l-spacing-sm;
  }

  &__header,
  &__models-container {
    padding-bottom: $l-spacing-1;
    display: flex;
    justify-content: space-between;
    background-color: $l-main-bg;

    h3 {
      font-weight: $l-font-weight-normal;
      font-size: $l-font-size-md;
      color: $l-grey-100;
    }

    button {
      margin: 0 2px;
      background-color: $l-main-bg;
      border: none;
      color: $l-grey-100;
    }
  }

  &__fields {
    z-index: 1;
    display: flex;
    flex-direction: column;
  }

  &__field {
    margin-bottom: $l-spacing-1;

    & > div,
    & > input {
      width: 100%;
      font-size: $l-font-size-sm;
      height: $l-input-height;
    }

    textarea {
      background-color: $l-card-bg;
      width: 100%;
      font-size: $l-font-size-sm;
    }

    .number-input {
      background-color: $l-card-bg;
      width: 100%;
    }
  }

  &__models-container {
    flex-direction: column;
    h4 {
      font-size: $l-font-size-sm;
      color: $l-grey-100;
      font-weight: $l-font-weight-bold;
    }
  }

  &__submit-container {
    display: flex;
    justify-content: center;
  }
}
</style>
