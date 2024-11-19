
<template>
  <div class="l-models-list">
    <div class="l-models-list__options-container">
      <div
        v-for="model in modelOptions"
        :key="model.name"
        class="l-models-list__options-container--option"
      >
        <RadioButton
          v-model="selectedModel"
          :inputId="model.link"
          name="dynamic"
          :value="model"
        />
        <label :for="model.link">{{ model.link }}</label>
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
import RadioButton from 'primevue/radiobutton';

const selectedModel = ref('')

defineProps({
  modelLink: String
})

const modelOptions = ref([
  { id: '1', link: 'hf://facebook/bart-large-cnn', externalLink: '' },
  { id: '2', link: 'mikeadimech/longformer-qmsum-meeting-summarization', externalLink: '' },
  { id: '3', link: 'mrm8488/t5-base-finetuned-summarize-news', externalLink: '' },
  { id: '4', link: 'mrm8488/t5-base-finetuned-summarize-news', externalLink: '' }
]);


defineExpose({
  selectedModel
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
        color: $l-grey-150;
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
