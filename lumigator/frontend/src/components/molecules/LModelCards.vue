<template>
  <div class="l-models-list">
    <div class="l-models-list__options-container">
      <div
        v-for="model in models"
        :key="model.name"
        class="l-models-list__options-container--option"
        @click="selectModel(model)"
      >
        <RadioButton
          v-model="selectedModel"
          :inputId="model.uri"
          name="dynamic"
          :value="model"
          @click.stop
        />
        <label :for="model.uri">{{ model.name }}</label>
        <Button
          as="a"
          icon="pi pi-external-link"
          severity="secondary"
          variant="text"
          rounded
          class="l-models__external-link"
          :href="model.website_url"
          target="_blank"
          @click.stop
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useModelStore } from '@/stores/models/store';
import RadioButton from 'primevue/radiobutton';
import Button from 'primevue/button';

const modelStore = useModelStore();
const { models } = storeToRefs(modelStore);
const selectedModel = ref('');

defineProps({
  modelLink: String
})

defineExpose({
  selectedModel
})

function selectModel(model) {
  selectedModel.value = model;
}
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
      border: 1px solid $l-gridlines-stroke;
      padding: $l-spacing-1;
      border-radius: $l-main-radius;
      cursor: pointer;
      align-items: CENTER;

      label {
        font-size: $l-font-size-sm;
      cursor: pointer;
        color: $l-grey-100;
      }

      &:hover {
        border-color: #52525b;
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
