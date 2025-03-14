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
          v-model="useCase"
          inputId="use_case"
          :options="useCaseOptions"
          optionLabel="label"
          optionValue="value"
          variant="filled"
          :disabled="false"
        >
        </Select>
        <label for="use_case">Use-case</label>
      </FloatLabel>

      <FloatLabel variant="in" class="l-experiment-form__field">
        <Select
          v-model="dataset"
          inputId="dataset"
          :options="filteredDatasets"
          optionLabel="filename"
          variant="filled"
          size="small"
        ></Select>
        <label for="dataset">Dataset</label>
      </FloatLabel>

      <div v-if="useCase === 'translation'" class="languages l-experiment-form__field">
        <FloatLabel variant="in" class="l-experiment-form__field l-experiment-form__field--inline">
          <Select
            id="sourceLanguage"
            v-model="sourceLanguage"
            variant="filled"
            inputId="source_language"
            :options="sourceLanguageOptions"
            optionLabel="label"
            optionValue="value"
          ></Select>
          <label for="sourceLanguage">Source Language</label>
        </FloatLabel>
        <span>to</span>
        <FloatLabel variant="in" class="l-experiment-form__field l-experiment-form__field--inline">
          <Select
            id="targetLanguage"
            v-model="targetLanguage"
            variant="filled"
            inputId="target_language"
            :options="targetLanguageOptions"
            optionLabel="label"
            optionValue="value"
          ></Select>
          <label for="targetLanguage">Target Language</label>
        </FloatLabel>
      </div>

      <FloatLabel variant="in" class="l-experiment-form__field">
        <Textarea
          id="prompt"
          :model-value="experimentPrompt || defaultPrompt"
          @update:model-value="(value) => (experimentPrompt = value || defaultPrompt)"
          autoResize
          fluid
          variant="filled"
        ></Textarea>
        <label for="prompt">Experiment Prompt</label>
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
      <p>
        Limit how many rows of your dataset to use for this experiment. Useful for when working with
        large datasets.
      </p>
    </div>
    <div class="l-experiment-form__models-container">
      <h3>Model Selection</h3>
      <div class="l-experiment-form__models">
        <l-model-cards ref="modelSelection" :useCase="useCase" />
      </div>
    </div>
    <div class="l-experiment-form__submit-container">
      <Button
        rounded
        size="small"
        label="Run experiment"
        class="l-page-header__action-btn"
        :disabled="isInvalid"
        @click="handleRunExperimentClicked"
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
import {
  experimentsService,
  type createExperimentWithWorkflowsPayload,
} from '@/sdk/experimentsService'
import { getAxiosError } from '@/helpers/getAxiosError'

const emit = defineEmits(['l-close-form'])

const datasetStore = useDatasetStore()
const experimentStore = useExperimentStore()
const { datasets, selectedDataset } = storeToRefs(datasetStore)

const useCaseOptions = ref([
  { label: 'Summarization', value: 'summarization' },
  { label: 'Translation', value: 'translation' },
])

const languageOptions = ref([
  {
    label: 'English',
    value: 'en',
  },
  {
    label: 'French',
    value: 'fr',
  },
  {
    label: 'German',
    value: 'de',
  },
  {
    label: 'Spanish',
    value: 'es',
  },
  {
    label: 'Arabic',
    value: 'ar',
  },
])

const sourceLanguageOptions = computed(() =>
  languageOptions.value.filter((language) => language.value !== targetLanguage.value),
)

const targetLanguageOptions = computed(() =>
  languageOptions.value.filter((language) => language.value !== sourceLanguage.value),
)

const useCase: Ref<'summarization' | 'translation'> = ref(
  useCaseOptions.value[0].value as 'summarization' | 'translation',
)
const dataset: Ref<Dataset | undefined> = ref()
const experimentTitle = ref('')
const experimentDescription = ref('')
const maxSamples = ref()
const modelSelection = ref()
const toast = useToast()
const sourceLanguage = ref('')
const targetLanguage = ref('')
const experimentPrompt = ref('')
const defaultPrompt = computed(() => {
  if (useCase.value === 'summarization') {
    return 'You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences.'
  }
  return `translate ${sourceLanguage.value} to ${targetLanguage.value}:`
})

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

async function handleRunExperimentClicked() {
  const taskDefinition =
    useCase.value === 'translation'
      ? {
          task: useCase.value,
          source_language: sourceLanguage.value,
          target_language: targetLanguage.value,
        }
      : { task: useCase.value }

  const experimentPayload: createExperimentWithWorkflowsPayload = {
    name: experimentTitle.value,
    description: experimentDescription.value,
    dataset: dataset.value!.id,
    max_samples: maxSamples.value ? maxSamples.value : -1,
    task_definition: taskDefinition,
    system_prompt: experimentPrompt.value || defaultPrompt.value,
  }

  const [experimentId, createWorkflowResponses] =
    await experimentsService.createExperimentWithWorkflows(
      experimentPayload,
      modelSelection.value.selectedModels,
    )
  // Separate successful workflows and errors
  const successfulResponses = createWorkflowResponses
    .filter((promise) => promise.status === 'fulfilled')
    .map((promise) => promise.value)
  const failedResponses = createWorkflowResponses
    .filter((promiseResult) => promiseResult.status === 'rejected')
    .map((promiseResult) => {
      const errorMessage = getAxiosError(promiseResult.reason)
      try {
        // if its a parseable JSON string, that means it returned `response.data`
        const responseBody = JSON.parse(errorMessage)
        return responseBody.detail
      } catch {
        // otherwise its just an error message/string
        return errorMessage
      }
    })

  failedResponses.forEach((msg: string) => {
    toast.add({
      severity: 'error',
      summary: `Workflow failed to start`,
      detail: `${msg}`,
      messageicon: 'pi pi-exclamation-triangle',
      group: 'br',
      life: 6000,
    } as ToastMessageOptions & { messageicon: string })
  })

  if (successfulResponses.length) {
    // re-fetch after creating an experiment to update the table
    await experimentStore.fetchAllExperiments()
    emit('l-close-form')
    resetForm()
    toast.add({
      severity: 'secondary',
      summary: `${experimentPayload.name} Started`,
      messageicon: 'pi pi-verified',
      group: 'br',
      life: 6000,
    } as ToastMessageOptions & { messageicon: string })
  } else {
    // delete the experiment if no workflows were created
    await experimentsService.deleteExperiment(experimentId)
    toast.add({
      severity: 'error',
      summary: `Experiment failed to start`,
      messageicon: 'pi pi-exclamation-triangle',
      group: 'br',
      life: 10000,
    } as ToastMessageOptions & { messageicon: string })
  }
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

.languages {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.l-experiment-form {
  $root: &;
  display: flex;
  flex-direction: column;

  p {
    font-size: $l-font-size-sm;
    color: $l-grey-100;
    margin-bottom: $l-spacing-1;
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

    &--inline {
      flex: 1;
      margin-bottom: 0;
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
