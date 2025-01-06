<template>
  <div class="l-models-list">
    <div class="l-models-list__options-container">
      <div
        v-for="model in modelOptions"
        :key="model.name"
        class="l-models-list__options-container--option"
      >
        <Checkbox
          v-model="selectedModels"
          :inputId="model.id"
          name="model"
          :value="model"
        />
        <label :for="model.link">{{ model.label }}</label>
        <Button
          as="a"
          icon="pi pi-external-link"
          severity="secondary"
          variant="text"
          rounded
          class="l-models__external-link"
          :href="model.externalLink"
          target="_blank"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';

const selectedModels = ref()

defineProps({
  modelLink: String
})

const modelOptions = ref([
  {
    id: '1',
    link: 'hf://facebook/bart-large-cnn',
    externalLink: 'https://huggingface.co/facebook/bart-large-cnn',
    label: 'facebook/bart-large-cnn'
  },

  {
    id: '2',
    link: 'hf://mikeadimech/longformer-qmsum-meeting-summarization',
    externalLink: 'https://huggingface.co/mikeadimech/longformer-qmsum-meeting-summarization',
    label: 'mikeadimech/longformer-qmsum-meeting-summarization'
  },

  {
    id: '3',
    link: 'hf://mrm8488/t5-base-finetuned-summarize-news',
    externalLink: 'https://huggingface.co/mrm8488/t5-base-finetuned-summarize-news',
    label: 'mrm8488/t5-base-finetuned-summarize-news'
  },
  {
    id: '4',
    link: 'hf://falconsai/text_summarization',
    externalLink: 'https://huggingface.co/Falconsai/text_summarization',
    label: 'falconsai/text_summarization'
  },
]);


defineExpose({
  selectedModels
})
</script>

<style scoped lang="scss">
.l-models-list {
  width: 100%;

  &__options-container {
    display: flex;
    flex-direction: column;
    padding-top: $l-spacing-1;
    gap: $l-spacing-1;


    &--option {
      display: grid;
      grid-template-columns: 30px 80% 1fr;
      grid-gap: 5px;
      background-color: $l-grey-300;
      padding: $l-spacing-1;
      border-radius: $l-main-radius;

      label {
        font-size: $l-font-size-sm;
        color: $l-grey-100;
      }
    }

    &__external-link,
    a {
      background-color: $l-grey-300 !important;
      border: none;
    }
  }
}
</style>
