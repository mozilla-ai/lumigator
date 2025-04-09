<template>
  <Dialog modal :closable="true" close-icon="''" :visible="true">
    <template #header>
      <div class="header">
        <h5 class="modal-title">Configure Model Run</h5>
        <p class="note">
          Note that model parameter configurations will override experiment parameters.
          <a href="#" rel="noopener" target="_blank">Learn more↗</a>
        </p>
      </div>
    </template>
    <Tabs :value="activeTab" @update:value="activeTab = String($event)">
      <TabList>
        <Tab value="basic">Basic </Tab>
        <Tab value="json"> JSON </Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="basic">
          <div class="basic-panel">
            <div class="form-fields">
              <div variant="in" class="form-field" v-if="isBYOM">
                <label for="via" class="field-label">Via</label>
                <Select
                  v-model="via"
                  label-id="via"
                  :options="['Hugging Face', 'Self-Hosted']"
                  variant="filled"
                ></Select>
              </div>

              <!-- <div variant="in" class="form-field" v-if="via== 'Hugging Face'">
                <label for="hugging-face-model-id" class="field-label">Hugging Face Model id</label>
                <InputText id="hugging-face-model-id" v-model="huggingFaceModelId" variant="filled" placeholder="Paste your model title or link here"></InputText>
              </div> -->

              <div variant="in" class="form-field" v-if="via == 'Self-Hosted'">
                <label for="base-url" class="field-label">Base Url</label>
                <InputText
                  id="base-url"
                  v-model="baseUrl"
                  variant="filled"
                  placeholder="Paste URL link here"
                ></InputText>
              </div>

              <div variant="in" class="form-field">
                <label for="model-id" class="field-label">{{
                  via === 'Hugging Face' ? 'Hugging Face Model id' : 'model id'
                }}</label>
                <InputText
                  id="model-id"
                  v-model="modelId"
                  variant="filled"
                  :placeholder="via === 'Hugging Face' ? 'Paste your model title or link here' : ''"
                ></InputText>
              </div>

              <div variant="in" class="form-field">
                <label for="run-title" class="field-label">run title</label>
                <InputText id="run-title" v-model="runTitle" variant="filled"></InputText>
              </div>

              <div class="prompt-field">
                <label for="prompt" class="field-label">Model Prompt</label>
                <Textarea
                  id="prompt"
                  :model-value="prompt || defaultPrompt"
                  @update:model-value="(value) => (prompt = value || defaultPrompt)"
                  autoResize
                  fluid
                ></Textarea>
              </div>
            </div>

            <div class="parameters-wrapper">
              <h6 class="parameters-header">Model parameters</h6>
              <div class="parameters">
                <div class="parameter-field">
                  <div class="inline-parameter-field">
                    <label for="temperature" class="parameter-label">Temperature</label>
                    <InputNumber
                      :max="1"
                      :min="0"
                      v-model="temperature"
                      :step="0.1"
                      size="small"
                      class="input-number"
                      fluid
                    />
                  </div>
                  <Slider v-model="temperature" name="temperature" :step="0.01" :min="0" :max="1" />
                </div>
                <div class="parameter-field">
                  <div class="inline-parameter-field">
                    <label for="topP" class="parameter-label">Top-P</label>
                    <InputNumber
                      :max="1"
                      :min="0"
                      v-model="topP"
                      :step="0.1"
                      size="small"
                      class="input-number"
                      fluid
                    />
                  </div>
                  <Slider v-model="topP" name="top-p" :step="0.01" :min="0" :max="1" />
                </div>
              </div>
            </div>
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
                :loading="isLoading"
                label="Done"
                :disabled="isFormInvalid"
                @click="handleContinueClicked"
              ></Button>
            </div>
          </div>
        </TabPanel>
        <TabPanel value="json"> Json tab </TabPanel>
      </TabPanels>
    </Tabs>
  </Dialog>
</template>

<script setup lang="ts">
import type { CreateWorkflowPayload } from '@/types/Workflow'

import {
  Button,
  Dialog,
  InputNumber,
  InputText,
  Select,
  Slider,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Textarea,
} from 'primevue'
import { computed, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    // isVisible: boolean
    model: CreateWorkflowPayload | undefined
    isBYOM: boolean
  }>(),
  {
    isBYOM: false,
  },
)

const emit = defineEmits<{
  save: [payload: CreateWorkflowPayload]
  close: []
}>()

const modelId = ref(props.model?.model)
const runTitle = ref(props.model?.name)
const prompt = ref(props.model?.system_prompt)
const baseUrl = ref(props.model?.base_url)
const temperature = ref(props.model?.generation_config?.temperature)
const topP = ref(props.model?.generation_config?.top_p)
const via = ref()
// const huggingFaceModelId = ref()

const defaultPrompt = computed(() => {
  const task = props.model?.task_definition.task
  if (task === 'summarization') {
    return 'You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences.'
  } else {
    const { source_language: sourceLanguage, target_language: targetLanguage } =
      props.model?.task_definition || {}
    return `translate ${sourceLanguage} to ${targetLanguage}:`
  }
})
const activeTab = ref('basic')

const handleCancelClicked = () => {
  emit('close')
}

const handleContinueClicked = () => {
  emit('save', {
    ...props.model,
    base_url: baseUrl.value || props.model?.base_url,
    model: modelId.value || props.model?.model,
    name: runTitle.value || props.model?.name,
    system_prompt: prompt.value || defaultPrompt.value,
    provider: via.value === 'Hugging Face' ? 'hf' : 'self-hosted',
    generation_config: {
      temperature: temperature.value,
      top_p: topP.value,
    },
  } as CreateWorkflowPayload)
}

const isLoading = ref(false)
const isFormInvalid = computed(() => {
  return (
    !modelId.value ||
    !runTitle.value ||
    !prompt.value ||
    (via.value === 'Self-Hosted' && !baseUrl.value)
  )
})
</script>

<style scoped lang="scss">
@use '@/styles/mixins.scss';

.header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.modal-title {
  text-align: center;
  @include mixins.heading-2;
}
.note {
  @include mixins.caption;
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

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.field-label {
  color: var(--l-grey-100);
  @include mixins.captions-caps;
}

.basic-panel {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.parameters-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.parameters-header {
  color: var(--l-grey-100);
  @include mixins.captions-caps;
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

.inline-parameter-field {
  display: flex;
  justify-content: space-between;
  // max-width: 1rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  width: 100%;
}

.input-number {
  max-width: 2.5rem;
}
</style>
