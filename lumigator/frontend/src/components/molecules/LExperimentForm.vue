<template>
  <div class="l-experiment-form">
    <div class="l-experiment-form__header">
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
          :options="datasets"
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
        <InputText
          id="max_samples"
          v-model="maxSamples"
          variant="filled"
          disabled
        />
        <label
          for="max_samples"
          class="disabled"
        >Maximul samples (optional)</label>
      </FloatLabel>
    </div>
    <div class="l-experiment-form__model-container">
      <h3>Model Selection</h3>
      <h4>Hugging Face Model Hub & Mistral</h4>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasets/store'
import Button from 'primevue/button';
import FloatLabel from 'primevue/floatlabel';
import Select from 'primevue/select';
import Textarea from 'primevue/textarea';
import InputText from 'primevue/inputtext';

const emit = defineEmits([
  'l-close-form',
])

const datasetStore = useDatasetStore();
const { datasets } = storeToRefs(datasetStore);

const experimentTypeOptions = ref([{ useCase: 'Summarization' }])
const experimentType = experimentTypeOptions.value[0];
const dataset = ref(null);
const experimentTitle = ref('')
const experimentDescription = ref('')
const maxSamples = ref(null)
</script>

<style scoped lang="scss">
.l-experiment-form {
  $root: &;
  display: flex;
  flex-direction: column;

  &__header, &__model-container{
    color: $l-grey-100;
    padding-bottom: $l-spacing-1;
    display: flex;
    justify-content: space-between;

    h3 {
      font-weight: $l-font-weight-normal;
      font-size: $l-font-size-md;
    }

    button {
      margin: 0 2px;
      background-color: $l-main-bg;
      border: none;
      color: $l-grey-100;
    }
  }

  &__fields {
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

    .disabled {
      color: #4D4D4D;
      cursor: not-allowed!important;
    }
  }

  &__model-container {
    flex-direction: column;
    h4 {
      font-size: $l-font-size-sm;
      font-weight:$l-font-weight-bold ;
    }
  }

}
</style>

<style lang="scss"></style>
