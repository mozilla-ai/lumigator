<template>
  <div class="l-experiment-form">
    <div
      class="l-experiment-form__header"
      style="position: sticky; top: 0;z-index:100"
    >
      <h3>Create Experiment</h3>
      <Button
        icon="pi pi-times"
        severity="secondary"
        rounded
        aria-label="Close"
        class="l-experiment-form__close"
        @click="emit('l-close-form')"
      />
    </div>
    <div class="l-experiment-form__fields">
      <FloatLabel
        variant="in"
        size="small"
        class="l-experiment-form__field"
      >
        <Select
          v-model="experimentType"
          inputId="use_case"
          optionLabel="useCase"
          :options="experimentTypeOptions"
          variant="filled"
          disabled
        />
        <label for="use_case">Use case</label>
      </FloatLabel>
      <FloatLabel
        variant="in"
        class="l-experiment-form__field"
      >
        <Select
          v-model="dataset"
          inputId="dataset"
          optionLabel="filename"
          :options="filteredDatasets"
          variant="filled"
          size="small"
        />
        <label for="dataset">Select Dataset</label>
      </FloatLabel>
      <FloatLabel
        variant="in"
        class="l-experiment-form__field"
      >
        <InputText
          id="title"
          v-model="experimentTitle"
          variant="filled"
        />
        <label for="title">Experiment Title</label>
      </FloatLabel>
      <FloatLabel
        variant="in"
        class="l-experiment-form__field"
      >
        <Textarea
          id="description_input"
          v-model="experimentDescription"
          rows="3"
          style="resize: none"
        />
        <label for="description_input">Experiment description</label>
      </FloatLabel>
      <FloatLabel
        variant="in"
        class="l-experiment-form__field"
      >
        <InputNumber
          id="max_samples"
          v-model="maxSamples"
          variant="filled"
          class="number-input"
        />
        <label for="max_samples">Maximum samples (optional)</label>
      </FloatLabel>
    </div>
    <div class="l-experiment-form__models-container">
      <h3>Model Selection</h3>
      <h4>Hugging Face Model Hub & Mistral</h4>
      <div class="l-experiment-form__models">
        <l-model-cards  ref="modelSelection"/>
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
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasets/store';
import { useExperimentStore } from '@/stores/experiments/store';
import Button from 'primevue/button';
import FloatLabel from 'primevue/floatlabel';
import Select from 'primevue/select';
import Textarea from 'primevue/textarea';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import LModelCards from '@/components/molecules/LModelCards.vue';
import { useToast } from "primevue/usetoast";

const emit = defineEmits([
  'l-close-form',
])

const datasetStore = useDatasetStore();
const experimentStore = useExperimentStore();
const { datasets, selectedDataset } = storeToRefs(datasetStore);

const experimentTypeOptions = ref([{ useCase: 'Summarization' }])
const experimentType = experimentTypeOptions.value[0];
const dataset = ref(null);
const experimentTitle = ref('');
const experimentDescription = ref('');
const maxSamples = ref();
const modelSelection = ref(null);
const toast = useToast();

const isInvalid = computed(() =>
  !experimentTitle.value ||
  !experimentDescription.value ||
  !dataset.value ||
  !modelSelection.value?.selectedModel
);

const filteredDatasets = computed(() =>
  datasets.value.filter((dataset) => dataset.ground_truth === true))

async function triggerExperiment() {
  const experimentPayload = {
    name: experimentTitle.value,
    description: experimentDescription.value,
    model: modelSelection.value.selectedModel.link,
    dataset: dataset.value.id,
    max_samples: maxSamples.value ? maxSamples.value : 0,
  }
  const success = await experimentStore.runExperiment(experimentPayload);
  if (success.name === experimentTitle.value) {
    await experimentStore.loadExperiments();
    emit('l-close-form');
    resetForm();
    toast.add({
      severity: 'secondary',
      summary: `${success.name } Started`,
      messageicon: 'pi pi-verified',
      group: 'br',
      life: 3000
    })
    return;
  }
    toast.add({
    severity: 'error',
    summary: `Experiment failed to start`,
    messageicon: 'pi pi-exclamation-triangle',
    group: 'br',
  })
}

function resetForm() {
  experimentTitle.value = '';
  experimentDescription.value = '';
  dataset.value = null;
  modelSelection.value.selectedModel = null;
  maxSamples.value = null;
}

onMounted(async () => {
  if (datasets.value?.length === 0) {
    await datasetStore.loadDatasets();
  }
  if (selectedDataset.value) {
    dataset.value = selectedDataset.value;
  }
})
</script>

<style scoped lang="scss">
.l-experiment-form {
  $root: &;
  display: flex;
  flex-direction: column;

  &__header, &__models-container{
    padding-bottom: $l-spacing-1;
    display: flex;
    justify-content: space-between;
    background-color: $l-main-bg;

    h3 {
      font-weight: $l-font-weight-normal;
      font-size: $l-font-size-md;
      color: $l-grey-150;
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

    &>div, &>input {
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
      color: $l-grey-150;
      font-weight:$l-font-weight-bold ;
    }
  }

  &__submit-container {
    display: flex;
    justify-content: center;
  }

}
</style>
