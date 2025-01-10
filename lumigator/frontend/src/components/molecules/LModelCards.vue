<template>
  <div class="l-models-list">
    <div class="l-models-list__options-container">
      <div
        v-for="model in models"
        :key="model.name"
        class="l-models-list__options-container--option"
      >
        <RadioButton
          v-model="selectedModel"
          :inputId="model.uri"
          name="dynamic"
          :value="model"
        />
        <label :for="model.name">{{ model.name }}</label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { storeToRefs } from 'pinia'
import { useModelStore } from '@/stores/models/store';
import RadioButton from 'primevue/radiobutton';

const modelStore = useModelStore();
const { models } = storeToRefs(modelStore);
const selectedModel = ref('')

defineProps({
  modelLink: String
})

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
