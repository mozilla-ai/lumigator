<template>
  <Dialog modal v-model:visible="isVisible" @update:visible="handleIsVisibleChanged">
    <template #header>
      <div class="header">
        <h5 class="modal-title">Configure Model Run</h5>
        <p class="note">
          Note that model parameter configurations will override experiment parameters.
          <a
            href="https://mozilla-ai.github.io/lumigator/get-started/quickstart.html#trigger-the-workflows"
            rel="noopener"
            target="_blank"
            style="background-color: transparent"
            >Learn more <span class="pi pi-arrow-up-right"></span>
          </a>
        </p>
      </div>
    </template>
    <div class="tabs-wrapper">
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
                    :disabled="!isBYOM"
                    v-model="modelId"
                    variant="filled"
                    :placeholder="
                      via === 'Hugging Face' ? 'paste Model ID here' : 'paste Model ID here'
                    "
                  ></InputText>
                </div>

                <div variant="in" class="form-field">
                  <label for="provider" class="field-label">Provider</label>
                  <InputText
                    id="provider"
                    :disabled="!isBYOM"
                    v-model="provider"
                    placeholder="Model Provider"
                    variant="filled"
                  ></InputText>
                </div>

                <div variant="in" class="form-field">
                  <label for="run-title" class="field-label">run title</label>
                  <InputText
                    id="run-title"
                    v-model="runTitle"
                    variant="filled"
                    placeholder="Type run title here"
                  ></InputText>
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
                    <Slider
                      v-model="temperature"
                      name="temperature"
                      :step="0.01"
                      :min="0"
                      :max="1"
                    />
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
            </div>
          </TabPanel>
          <TabPanel value="json">
            <div class="json-panel">
              <!-- <pre>{{ workflowForm }}</pre> -->
              <JsonEditorVue
                class="jse-theme-dark"
                :debounce="300"
                :mode="mode"
                :ask-to-format="true"
                :onChange="handleJSONChanged"
                :main-menu-bar="false"
                :model-value="workflowForm"
              ></JsonEditorVue>
              <p class="json-note">
                Ensure the schema is configured correctly. Check all parameters and their values to
                ensure optimal performance. An incorrect configuration can result in a failed job or
                gibberish output.
              </p>
            </div>
          </TabPanel>
        </TabPanels>
      </Tabs>
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
  </Dialog>
</template>

<script setup lang="ts">
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
import { computed, ref, watch } from 'vue'
import type { WorkflowForm } from './AddWorkflowsTab.vue'
import JsonEditorVue from 'json-editor-vue'
import 'vanilla-jsoneditor/themes/jse-theme-dark.css'
import { Mode, type TextContent } from 'vanilla-jsoneditor'

const props = withDefaults(
  defineProps<{
    // isVisible: boolean
    workflow: WorkflowForm
    isBYOM: boolean
  }>(),
  {
    isBYOM: false,
  },
)

const emit = defineEmits<{
  save: [payload: WorkflowForm]
  close: []
}>()

const isVisible = ref(true)
const modelId = ref(props.workflow.model)
const runTitle = ref(props.workflow.name)
const prompt = ref(props.workflow.system_prompt)
const baseUrl = ref(props.workflow.base_url)
const temperature = ref(props.workflow.generation_config?.temperature)
const topP = ref(props.workflow.generation_config?.top_p)
const via = ref('Hugging Face')
const provider = ref(props.workflow.provider)
const mode = Mode.text
const handleJSONChanged = (change: TextContent) => {
  const string = change.text
  try {
    const val = JSON.parse(string)
    modelId.value = val.model
    runTitle.value = val.name
    prompt.value = val.system_prompt
    baseUrl.value = val.base_url
    temperature.value = val.generation_config?.temperature
    topP.value = val.generation_config?.top_p
  } catch (e) {
    console.error('Error parsing JSON', e)
  }
}

watch(via, (value) => {
  if (props.isBYOM) {
    if (value === 'Hugging Face') {
      provider.value = 'hf'
    } else if (value === 'Self-Hosted') {
      provider.value = 'self-hosted'
    }
  }
})

const handleIsVisibleChanged = (value: boolean) => {
  isVisible.value = value
  emit('close')
}

const workflowForm = computed(() => ({
  ...props.workflow,
  base_url: props.isBYOM ? baseUrl.value || props.workflow.base_url : props.workflow.base_url,
  model: modelId.value || props.workflow.model,
  name: runTitle.value || props.workflow.name,
  system_prompt: prompt.value || defaultPrompt.value,
  provider: provider.value,
  generation_config: {
    temperature: temperature.value,
    top_p: topP.value,
  },
}))
const defaultPrompt = computed(() => {
  const task = props.workflow.task_definition.task
  if (task === 'summarization') {
    return 'You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences.'
  } else {
    const { source_language: sourceLanguage, target_language: targetLanguage } =
      props.workflow.task_definition || {}
    return `translate ${sourceLanguage} to ${targetLanguage}:`
  }
})
const activeTab = ref('basic')

const handleCancelClicked = () => {
  emit('close')
}

const handleContinueClicked = () => {
  emit('save', workflowForm.value)
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

.tabs-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.json-note {
  color: var(--l-grey-100);
  @include mixins.caption;
}

.json-panel {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
