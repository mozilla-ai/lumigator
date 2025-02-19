<template>
  <div class="l-models-list">
    <div class="l-models-list__options-container">
      <div class="l-models-list__options-container-section">
        <p>VIA HUGGING FACE</p>
        <span
          >Ensure you have sufficient compute resources available before running models in your
          environment.
        </span>
      </div>
      <div
        v-for="model in modelsRequiringNoAPIKey"
        :key="model.name"
        class="l-models-list__options-container--option"
        @click="toggleModel(model)"
      >
        <Checkbox
          v-model="selectedModels"
          :value="model"
          :inputId="model.id"
          name="model"
          @click.stop
        />
        <label :for="model.id">{{ model.name }}</label>

        <!-- Keep @click.stop on external link so it doesn't toggle selection -->
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
        >
        </Button>
      </div>
      <!-- TODO: this is copy pasted and can be extracted into a component -->
      <div v-if="modelsRequiringAPIKey.length" class="l-models-list__options-container-section">
        <p>VIA APIs</p>
        <span
          >Ensure your API keys are added to your environment variables (.env) file before using
          API-based models.
        </span>
      </div>
      <div
        v-for="model in modelsRequiringAPIKey"
        :key="model.name"
        class="l-models-list__options-container--option"
        @click="toggleModel(model)"
      >
        <Checkbox
          v-model="selectedModels"
          :value="model"
          :inputId="model.id"
          name="model"
          @click.stop
        />
        <label :for="model.id">{{ model.name }}</label>

        <!-- Keep @click.stop on external link so it doesn't toggle selection -->
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

<script lang="ts" setup>
import { ref, computed, type Ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useModelStore } from '@/stores/modelsStore'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import type { Model } from '@/types/Model'

const modelStore = useModelStore()
const { models } = storeToRefs(modelStore)
const selectedModels: Ref<Model[]> = ref([])

defineProps({
  modelLink: String,
})

defineExpose({
  selectedModels,
})

const modelsByRequirement = (requirementKey: string, isRequired: boolean): Model[] => {
  return models.value.filter((model: Model) => {
    const isKeyPresent = model.requirements?.includes(requirementKey)
    return isRequired ? isKeyPresent : !isKeyPresent
  })
}

const modelsRequiringAPIKey = computed(() => modelsByRequirement('api_key', true))

const modelsRequiringNoAPIKey = computed(() => modelsByRequirement('api_key', false))

function toggleModel(model: Model) {
  const index = selectedModels.value.findIndex(
    (selectedModel: Model) => selectedModel.name === model.name,
  )

  if (index === -1) {
    selectedModels.value.push(model)
  } else {
    selectedModels.value.splice(index, 1)
  }
}
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-models-list {
  width: 100%;

  &__options-container {
    display: flex;
    flex-direction: column;
    padding-top: $l-spacing-1;
    gap: $l-spacing-1;

    &-section {
      color: $l-grey-100;
      font-size: $l-font-size-sm;
      p {
        margin-bottom: 5px;
      }
      span {
        display: block;
        line-height: 1.2;
      }
    }
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
