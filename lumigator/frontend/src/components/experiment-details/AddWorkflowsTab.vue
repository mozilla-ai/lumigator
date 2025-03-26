<template>
  <div class="workflows-tab-container">
    <div class="left-container">
      <div class="info-wrapper">
        <div class="hint">
          <i class="pi pi-lightbulb message-icon"></i>
          <p class="caption">
            You can configure the parameters for each model run within your experiment. You can also
            add models from Hugging Face or your own environment, and you can always add additional
            runs later.
            <!-- <i class="close-icon pi pi-times"></i> -->
          </p>
        </div>
      </div>
      <div class="header-wrapper">
        <h4 class="header">Suggested Models</h4>
        <div class="header-actions">
          <Button
            severity="secondary"
            rounded
            label="Add Model"
            icon="pi pi-plus"
            @click="handleAddModelClicked"
          ></Button>
          <Button
            severity="secondary"
            rounded
            label="Run"
            disabled
            icon="pi pi-play"
            @click="handleRunClicked"
          ></Button>
        </div>
      </div>
      <div class="models-container">
        <div class="models-wrapper">
          <h5 class="caption-caps">via hugging face</h5>
          <div class="models-grid">
            <article class="model-card">
              <div class="model-field">
                <Checkbox binary input-id="card-input"></Checkbox>
                <label for="card-input" class="model-label">Model 1</label>
              </div>
              <div class="model-actions">
                <Button
                  icon="pi pi-heart"
                  severity="help"
                  variant="text"
                  rounded
                  aria-label="Favorite"
                ></Button>
                <Button
                  icon="pi pi-times"
                  severity="danger"
                  variant="text"
                  rounded
                  aria-label="Cancel"
                ></Button>
                <Button
                  icon="pi pi-star"
                  severity="contrast"
                  variant="text"
                  rounded
                  aria-label="Star"
                ></Button>
              </div>
            </article>
          </div>
        </div>
        <div class="models-wrapper">
          <h5 class="caption-caps">via apis</h5>
          <div class="models-grid">
            <article class="model-card">
              <div class="model-field">
                <Checkbox binary input-id="card-input"></Checkbox>
                <label for="card-input" class="model-label">Model 1</label>
              </div>
              <div class="model-actions">
                <Button
                  icon="pi pi-heart"
                  severity="help"
                  variant="text"
                  rounded
                  aria-label="Favorite"
                ></Button>
                <Button
                  icon="pi pi-times"
                  severity="danger"
                  variant="text"
                  rounded
                  aria-label="Cancel"
                ></Button>
                <Button
                  icon="pi pi-star"
                  severity="contrast"
                  variant="text"
                  rounded
                  aria-label="Star"
                ></Button>
              </div>
            </article>
          </div>
        </div>
      </div>
    </div>
    <div class="right-container">
      <div class="prompt-field">
        <label for="prompt" class="caption-caps">Default use-case prompt</label>
        <Textarea
          id="prompt"
          :model-value="experimentPrompt || defaultPrompt"
          @update:model-value="(value) => (experimentPrompt = value || defaultPrompt)"
          autoResize
          fluid
        ></Textarea>
      </div>
      <div class="parameters-wrapper">
        <h5 class="caption-caps">Default parameters</h5>
        <div class="parameters">
          <div class="parameter-field">
            <div class="field-label">
              <label for="temperature" class="parameter-label">Temperature</label>
              <InputNumber v-model="temperature" />
            </div>
            <Slider v-model="temperature" name="temperature" :step="0.1" :min="0" :max="1" />
          </div>
          <div class="parameter-field">
            <div class="field-label">
              <label for="topP" class="parameter-label">Top-P</label>
              <InputNumber v-model="topP" />
            </div>
            <Slider v-model="topP" name="top-p" :step="0.1" :min="0" :max="1" />
          </div>
        </div>
      </div>

      <div></div>
    </div>
  </div>
</template>

<script setup lang="ts">
// import { useModelStore } from '@/stores/modelsStore'
import { Button, Checkbox, InputNumber, Slider, Textarea } from 'primevue'
import { computed, ref } from 'vue'

// const modelStore = useModelStore()

const experimentPrompt = ref('')
const defaultPrompt = computed(() => {
  // if (useCase.value === 'summarization') {
  return 'You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences.'
  // }
  // return `translate ${sourceLanguage.value} to ${targetLanguage.value}:`
})
const topP = ref(0.55)
const temperature = ref(0.55)

// const models = computed(() => modelStore.filterModelsByUseCase(props.useCase))

// const modelsByRequirement = (requirementKey: string, isRequired: boolean): Model[] => {
//   return models.value.filter((model: Model) => {
//     const isKeyPresent = model.requirements?.includes(requirementKey)
//     return isRequired ? isKeyPresent : !isKeyPresent
//   })
// }

// const modelsRequiringAPIKey = computed(() => modelsByRequirement('api_key', true))

// const modelsRequiringNoAPIKey = computed(() => modelsByRequirement('api_key', false))

const handleAddModelClicked = () => {}

const handleRunClicked = () => {}
</script>

<style scoped lang="scss">
@use '@/styles/mixins.scss';

.workflows-tab-container {
  display: flex;
  justify-content: space-between;
  gap: 5rem;
}

.caption {
  color: var(--l-grey-200);
  position: relative;
  @include mixins.caption;
}

.close-icon {
  position: absolute;
  top: 0;
  right: 0;
}

.prompt-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.model-label {
  color: var(--l-grey-100);
  font-family: Inter;
  font-size: 0.75rem;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  letter-spacing: -0.015rem;
}

.models-grid {
  display: grid;
  grid-template-columns: auto auto;
  column-gap: 0.5rem;
  row-gap: 0.5rem;
}

article {
  border: solid 1px var(--border-stroke);
}

.hint {
  display: flex;
  padding: 0.75rem;
  align-items: center;
  gap: 0.5rem;

  border-radius: 0.5rem;
  border: 0.5px solid var(--border-stroke);
  background: var(--l-grey-500);
}

.message-icon {
  color: var(--l-primary-color);
}

.caption-caps {
  color: var(--l-grey-100);
  @include mixins.captions-caps;
}

.left-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header-wrapper {
  display: flex;
  justify-content: space-between;
}

.parameters-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.parameters {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.parameter-field {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.parameter-label {
  color: var(--l-grey-100);
  @include mixins.paragraph;
}

.field-label {
  display: flex;
  justify-content: space-between;
}

.header {
  color: var(--l-grey-100);

  @include mixins.paragraph-2;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.models-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.models-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.right-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.model-card {
  display: flex;
  padding: 0rem 0.5rem 0rem 0.75rem;
  max-width: 19.875rem;
  // flex: 1 0 0;
  min-height: 3.625rem;
  justify-content: space-between;
  align-items: center;
  border-radius: 0.5rem;
  background: var(--l-grey-300);
}

.model-field {
  display: flex;
  gap: 0.5rem;
}
</style>
