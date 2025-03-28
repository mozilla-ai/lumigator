<template>
  <Dialog
    v-model:visible="isVisible"
    modal
    :closable="true"
    close-icon=""
    @update:visible="handleIsVisibleChanged"
  >
    <template #header>
      <div class="header">Create Experiment</div>
    </template>
    <div class="form-body">
      <FloatLabel variant="in" class="form-field">
        <InputText id="title" v-model="experimentTitle" variant="filled" />
        <label for="title">Title</label>
      </FloatLabel>
      <FloatLabel variant="in" class="form-field">
        <Textarea
          id="description_input"
          v-model="experimentDescription"
          rows="2"
          style="resize: none"
        ></Textarea>
        <label for="description_input">Description for your own reference</label>
      </FloatLabel>

      <FloatLabel variant="in" class="form-field">
        <Select
          v-model="dataset"
          label-id="dataset"
          :options="filteredDatasets"
          optionLabel="filename"
          variant="filled"
        ></Select>
        <label for="dataset">Dataset</label>
      </FloatLabel>

      <FloatLabel variant="in" class="form-field">
        <InputNumber
          input-id="max_samples"
          v-model="maxSamples"
          variant="filled"
          class="number-input"
        />
        <label for="max_samples">Maximum samples (optional)</label>
      </FloatLabel>
      <p class="caption">Limit how many rows of your dataset to use for this experiment.</p>

      <FloatLabel variant="in" size="small" class="form-field">
        <Select
          v-model="useCase"
          label-id="usecase"
          :options="useCaseOptions"
          optionLabel="label"
          optionValue="value"
          variant="filled"
          :disabled="false"
        >
        </Select>
        <label for="usecase">Use-case</label>
      </FloatLabel>
      <p class="caption">Summarization experiments are evaluated with ROUGE, METEOR, and BERT.</p>

      <div v-if="useCase === 'translation'" class="languages form-field">
        <FloatLabel variant="in" class="form-field form-field--inline">
          <Select
            label-id="sourceLanguage"
            v-model="sourceLanguage"
            variant="filled"
            :options="sourceLanguageOptions"
            optionLabel="label"
            optionValue="value"
          ></Select>
          <label for="sourceLanguage">Source Language</label>
        </FloatLabel>
        <span>to</span>
        <FloatLabel variant="in" class="form-field form-field--inline">
          <Select
            v-model="targetLanguage"
            variant="filled"
            label-id="targetLanguage"
            :options="targetLanguageOptions"
            optionLabel="label"
            optionValue="value"
          ></Select>
          <label for="targetLanguage">Target Language</label>
        </FloatLabel>
      </div>
      <div v-if="useCase === 'summarization'" class="g-eval-field">
        <Checkbox disabled v-model="includeGEval" inputId="g-eval" name="g-eval" binary />
        <label for="g-eval"> Include G-Eval scores using LLM as a Judge </label>
      </div>
    </div>
    <template #footer>
      <div class="actions">
        <Button
          type="button"
          label="Cancel"
          rounded
          severity="secondary"
          @click="handleCancelClicked"
        ></Button>
        <Button
          type="button"
          rounded
          :loading="createExperimentMutation.isPending.value"
          label="Continue"
          :disabled="isFormInvalid || createExperimentMutation.isPending.value"
          @click="handleContinueClicked"
        ></Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { getAxiosError } from '@/helpers/getAxiosError'
import { experimentsService } from '@/sdk/experimentsService'
import { useDatasetStore } from '@/stores/datasetsStore'
import type { Dataset } from '@/types/Dataset'
import type { CreateExperimentPayload } from '@/types/Experiment'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { storeToRefs } from 'pinia'
import {
  Button,
  Checkbox,
  Dialog,
  FloatLabel,
  InputNumber,
  InputText,
  Select,
  Textarea,
  useToast,
} from 'primevue'
import { computed, ref, type Ref } from 'vue'
import { useRouter } from 'vue-router'

const { selectedDataset } = defineProps<{
  selectedDataset?: Dataset
}>()

const isVisible = ref(true)
const datasetStore = useDatasetStore()
const { datasets } = storeToRefs(datasetStore)

const filteredDatasets = computed(() =>
  datasets.value.filter((dataset) => dataset.ground_truth === true),
)
const dataset: Ref<Dataset | undefined> = ref(selectedDataset)
const includeGEval = ref(false)

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

const handleIsVisibleChanged = (value: boolean) => {
  isVisible.value = value
  emit('close')
}

const experimentTitle = ref('')
const experimentDescription = ref('')
const maxSamples = ref()
const toast = useToast()
const sourceLanguage = ref('')
const targetLanguage = ref('')

toast.add({
  severity: 'info',
  summary: 'Creating Experiment',
  detail: 'Please wait...',
  life: 3000,
})

const isFormInvalid = computed(
  () =>
    !experimentTitle.value ||
    !experimentDescription.value ||
    !dataset.value ||
    !useCase.value ||
    (useCase.value === 'translation' && (!sourceLanguage.value || !targetLanguage.value)),
)

const queryClient = useQueryClient()

const router = useRouter()
const createExperimentMutation = useMutation({
  mutationFn: experimentsService.createExperiment,
  onMutate: () => {
    toast.add({
      severity: 'info',
      summary: 'Creating Experiment',
      group: 'br',
      detail: 'Please wait...',
      life: 3000,
    })
  },
  onError: (error) => {
    const errorMessage = getAxiosError(error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      group: 'br',
      life: 3000,
    })
  },
  onSuccess: async (data) => {
    toast.add({
      severity: 'success',
      summary: 'Experiment Created',
      detail: 'Experiment has been created successfully.',
      life: 3000,
      group: 'br',
    })

    queryClient.invalidateQueries({
      queryKey: ['experiments'],
    })
    router.push(`/experiments/${data.id}`)
  },
})

async function handleContinueClicked() {
  const taskDefinition =
    useCase.value === 'translation'
      ? {
          task: useCase.value,
          source_language: sourceLanguage.value,
          target_language: targetLanguage.value,
        }
      : { task: useCase.value }

  const experimentPayload: CreateExperimentPayload = {
    name: experimentTitle.value,
    description: experimentDescription.value,
    dataset: dataset.value!.id,
    max_samples: maxSamples.value ? maxSamples.value : -1,
    task_definition: taskDefinition,
  }

  createExperimentMutation.mutate(experimentPayload)
}

const emit = defineEmits(['close'])

function handleCancelClicked() {
  isVisible.value = false
  // resetForm()
  emit('close')
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss';
@use '@/styles/mixins.scss';

.header {
  text-align: center;
  width: 100%;
  @include mixins.heading-2;
}

// .form {
//   display: flex;
//   flex-direction: column;
//   gap: 1.5rem;
//   width: 100%;
// }

.form-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.caption {
  color: var(--l-grey-100, #bbb);

  @include mixins.caption;
}

.g-eval-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.languages {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.form-field {
  > div,
  > input {
    width: 100%;
    font-size: var(--l-font-size-sm);
    height: var(--l-input-height);
  }

  textarea {
    width: 100%;
    font-size: var(--l-font-size-sm);
  }

  .number-input {
    width: 100%;
  }

  &--inline {
    flex: 1;
    margin-bottom: 0;
  }
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  width: 100%;
}
</style>
