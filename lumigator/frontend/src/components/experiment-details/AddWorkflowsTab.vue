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
            rounded
            label="Run"
            :disabled="selectedModels.length === 0 || createWorkflowMutation.isPending.value"
            icon="pi pi-play"
            @click="handleRunClicked"
          ></Button>
        </div>
      </div>
      <div class="models-container">
        <div class="models-wrapper">
          <h5 class="caption-caps">via hugging face</h5>
          <div class="models-grid">
            <ModelCard
              v-for="model in modelsRequiringNoAPIKey"
              :key="model.model"
              :model="model"
              :is-selected="selectedModels.includes(model.model)"
              :is-custom="customWorkflows.some((workflow) => workflow.model === model.model)"
              @checkbox-toggled="handleCheckboxToggled"
              @clone-clicked="handleCloneClicked"
              @customize-clicked="handleCustomizeClicked"
              @delete-clicked="handleDeleteClicked"
            />
          </div>
        </div>
        <div class="models-wrapper">
          <h5 class="caption-caps">via apis</h5>
          <div class="models-grid">
            <ModelCard
              v-for="model in modelsRequiringAPIKey"
              :key="model.model"
              :model="model"
              :is-selected="selectedModels.includes(model.model)"
              :is-custom="customWorkflows.some((workflow) => workflow.model === model.model)"
              @checkbox-toggled="handleCheckboxToggled"
              @clone-clicked="handleCloneClicked"
              @customize-clicked="handleCustomizeClicked"
              @delete-clicked="handleDeleteClicked"
            />
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
              <InputNumber v-model="temperature" :step="0.1" />
            </div>
            <Slider v-model="temperature" name="temperature" :step="0.01" :min="0" :max="1" />
          </div>
          <div class="parameter-field">
            <div class="field-label">
              <label for="topP" class="parameter-label">Top-P</label>
              <InputNumber v-model="topP" :step="0.1" />
            </div>
            <Slider v-model="topP" name="top-p" :step="0.01" :min="0" :max="1" />
          </div>
        </div>
      </div>

      <div></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useModelStore } from '@/stores/modelsStore'
import type { Experiment } from '@/types/Experiment'
import type { Model } from '@/types/Model'
import { Button, InputNumber, Slider, Textarea, useToast } from 'primevue'
import { computed, ref } from 'vue'
import ModelCard from './ModelCard.vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { workflowsService } from '@/sdk/workflowsService'
import type { CreateWorkflowPayload } from '@/types/Workflow'
import { getAxiosError } from '@/helpers/getAxiosError'

const props = defineProps<{ experiment: Experiment }>()
const modelStore = useModelStore()
const toast = useToast()
const selectedModels = ref<Model['model'][]>([])
const customWorkflows = ref<CreateWorkflowPayload[]>([])
const queryClient = useQueryClient()
const emit = defineEmits(['workflowCreated'])

const experimentPrompt = ref('')
const defaultPrompt = computed(() => {
  const task = props.experiment.task_definition.task
  if (task === 'summarization') {
    return 'You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences.'
  } else {
    const { source_language: sourceLanguage, target_language: targetLanguage } =
      props.experiment.task_definition
    return `translate ${sourceLanguage} to ${targetLanguage}:`
  }
})
const topP = ref(0.55)
const temperature = ref(0.55)
const createWorkflowMutation = useMutation({
  mutationFn: workflowsService.createWorkflow,
  onError: (error) => {
    toast.add({
      group: 'br',
      closable: true,
      severity: 'error',
      summary: 'Error',
      detail: getAxiosError(error),
    })
  },
  onSuccess: async () => {
    toast.add({
      group: 'br',
      life: 3000,
      severity: 'success',
      summary: 'Success',
      detail: 'Model Run created successfully',
    })
    queryClient.invalidateQueries({
      queryKey: ['experiment', props.experiment.id],
    })
    emit('workflowCreated')
  },
  onMutate: () => {
    toast.add({
      group: 'br',
      life: 3000,
      severity: 'info',
      summary: 'Creating Model Run',
      detail: 'Please wait...',
    })
  },
})

const models = computed(() =>
  modelStore.filterModelsByUseCase(props.experiment.task_definition.task),
)
const modelsByRequirement = (requirementKey: string, isRequired: boolean): Model[] => {
  return models.value.filter((model: Model) => {
    const isKeyPresent = model.requirements?.includes(requirementKey)
    return isRequired ? isKeyPresent : !isKeyPresent
  })
}
const modelsRequiringAPIKey = computed(() => modelsByRequirement('api_key', true))
const modelsRequiringNoAPIKey = computed(() => modelsByRequirement('api_key', false))

const handleAddModelClicked = () => {}

const handleRunClicked = () => {
  selectedModels.value.forEach((selectedModel) => {
    const model = models.value.find((m: Model) => m.model === selectedModel)
    const workflowPayload: CreateWorkflowPayload = {
      dataset: props.experiment.dataset,
      experiment_id: props.experiment.id,
      task_definition: props.experiment.task_definition,
      system_prompt: experimentPrompt.value || defaultPrompt.value,
      description: props.experiment.description,
      max_samples: props.experiment.max_samples,
      name: `${props.experiment.name}/${model.model}`,
      model: model.model,
      provider: model.provider,
      secret_key_name: model.requirements.includes('api_key')
        ? `${model.provider}_api_key`
        : undefined,
      base_url: model.base_url,
      generation_config: {
        temperature: temperature.value,
        top_p: topP.value,
        // max_new_tokens: 1024,
        // frequency_penalty: 0
      },
    }

    createWorkflowMutation.mutate(workflowPayload)

    selectedModels.value = []
  })
}

const handleCheckboxToggled = (model: Model) => {
  selectedModels.value = selectedModels.value.includes(model.model)
    ? selectedModels.value.filter((selectedModel) => selectedModel !== model.model)
    : [...selectedModels.value, model.model]
}

const handleCloneClicked = (model: Model) => {
  console.log('clone clicked', model)
}

const handleCustomizeClicked = (model: Model) => {
  console.log('customize clicked', model)
  if (customWorkflows.value.some((workflow) => workflow.model === model.model)) {
    customWorkflows.value = customWorkflows.value.filter(
      (workflow) => workflow.model !== model.model,
    )
  } else {
    customWorkflows.value.push({
      dataset: props.experiment.dataset,
      experiment_id: props.experiment.id,
      task_definition: props.experiment.task_definition,
      system_prompt: experimentPrompt.value || defaultPrompt.value,
      description: props.experiment.description,
      max_samples: props.experiment.max_samples,
      name: `${props.experiment.name}/${model.model}`,
      model: model.model,
      provider: model.provider,
      secret_key_name: model.requirements.includes('api_key')
        ? `${model.provider}_api_key`
        : undefined,
      base_url: model.base_url,
      generation_config: {
        temperature: temperature.value,
        top_p: topP.value,
      },
    })
  }
}

const handleDeleteClicked = (model: Model) => {
  console.log('delete clicked', model)
}
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
</style>
