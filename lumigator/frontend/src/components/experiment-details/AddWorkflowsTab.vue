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
            :disabled="selectedWorkflowIds.length === 0 || createWorkflowMutation.isPending.value"
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
              v-for="workflow in workflowsRequiringNoApiKey"
              :key="workflow.id"
              :workflow="workflow"
              :is-selected="selectedWorkflowIds.includes(workflow.id)"
              :is-custom="configuredWorkflowIds.includes(workflow.id)"
              :is-deletable="deletableWorkflowIds.includes(workflow.id)"
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
              v-for="workflow in workflowsRequiringApiKey"
              :key="workflow.id"
              :workflow="workflow"
              :is-selected="selectedWorkflowIds.includes(workflow.id)"
              :is-custom="configuredWorkflowIds.includes(workflow.id)"
              :is-deletable="deletableWorkflowIds.includes(workflow.id)"
              @checkbox-toggled="handleCheckboxToggled"
              @clone-clicked="handleCloneClicked"
              @customize-clicked="handleCustomizeClicked"
              @delete-clicked="handleDeleteClicked"
            />
          </div>
        </div>
        <!-- <div class="models-wrapper" v-if="customModels.length">
          <h5 class="caption-caps">Custom</h5>
          <div class="models-grid">
            <ModelCard
              v-for="model in customModels"
              :key="model.model"
              :model="model"
              :is-selected="selectedWorkflowIds.includes(model.model)"
              :is-custom="configuredWorkflowIds.some((workflowId) => workflow.model === modelIodel)"
              :is-deletable="deletableWorkflowIds.includes(workflow.id)"
              @checkbox-toggled="handleCheckboxToggled"
              @clone-clicked="handleCloneClicked"
              @customize-clicked="handleCustomizeClicked"
              @delete-clicked="handleDeleteClicked"
            />
          </div>
        </div> -->
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
              <InputNumber
                v-model="temperature"
                :step="0.1"
                :min="0"
                :max="1"
                fluid
                style="max-width: 3.5rem"
              />
            </div>
            <Slider v-model="temperature" name="temperature" :step="0.01" :min="0" :max="1" />
          </div>
          <div class="parameter-field">
            <div class="field-label">
              <label for="topP" class="parameter-label">Top-P</label>
              <InputNumber
                v-model="topP"
                :step="0.1"
                :min="0"
                :max="1"
                fluid
                style="max-width: 3.5rem"
              />
            </div>
            <Slider v-model="topP" name="top-p" :step="0.01" :min="0" :max="1" />
          </div>
        </div>
      </div>

      <ConfigureWorkflowModal
        v-if="isCustomWorkflowModalVisible && workflowBeingConfigured"
        :workflow="workflowBeingConfigured"
        :isBYOM="isBYOM"
        @save="saveModelConfiguration"
        @close="handleConfigureWorkflowModalClosed"
      ></ConfigureWorkflowModal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useModelStore } from '@/stores/modelsStore'
import type { Experiment } from '@/types/Experiment'
import type { Model } from '@/types/Model'
import { Button, InputNumber, Slider, Textarea, useToast } from 'primevue'
import { computed, ref, type Ref } from 'vue'
import ModelCard from './ModelCard.vue'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { workflowsService } from '@/sdk/workflowsService'
import type { CreateWorkflowPayload } from '@/types/Workflow'
import { getAxiosError } from '@/helpers/getAxiosError'
import ConfigureWorkflowModal from './ConfigureWorkflowModal.vue'
import { storeToRefs } from 'pinia'
const { models } = storeToRefs(useModelStore())
const props = defineProps<{ experiment: Experiment }>()
const modelStore = useModelStore()
const toast = useToast()
const selectedWorkflowIds = ref<string[]>([])
const configuredWorkflowIds = ref<WorkflowForm['id'][]>([])
const deletableWorkflowIds = ref<WorkflowForm['id'][]>([])
const queryClient = useQueryClient()
const emit = defineEmits(['workflowCreated'])
const isCustomWorkflowModalVisible = ref(false)
const workflowBeingConfigured = ref<WorkflowForm>()
const isBYOM = ref(false)

const handleConfigureWorkflowModalClosed = () => {
  workflowBeingConfigured.value = undefined
  isCustomWorkflowModalVisible.value = false
  isBYOM.value = false
}

export type WorkflowForm = CreateWorkflowPayload & {
  id: string
}

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
  mutationFn: (workflowForm: WorkflowForm) => {
    const { id: _id, ...rest } = workflowForm
    return workflowsService.createWorkflow(rest)
  },
  onError: (error) => {
    toast.add({
      group: 'br',
      closable: true,
      severity: 'error',
      summary: 'Error',
      detail: getAxiosError(error),
    })
  },
  onSuccess: async (context, variables) => {
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
    if (configuredWorkflowIds.value.some((workflowId) => workflowId === variables.id)) {
      // remove the workflow from the configured workflows list so it doesn't show up as active
      configuredWorkflowIds.value = configuredWorkflowIds.value.filter(
        (workflowId) => workflowId !== variables.id,
      )
    }
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

const transformModelToWorkflowForm = (model: Model): WorkflowForm => {
  return {
    id: model.model.concat(Math.floor(Math.random() * 1000000).toString(16)),
    dataset: props.experiment.dataset,
    experiment_id: props.experiment.id,
    task_definition: props.experiment.task_definition,
    system_prompt: experimentPrompt.value || defaultPrompt.value,
    description: props.experiment.description,
    max_samples: props.experiment.max_samples,
    name: `${model.model}`,
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
  }
}

const allWorkflows: Ref<WorkflowForm[]> = ref([
  ...modelStore
    .filterModelsByUseCase(props.experiment.task_definition.task)
    .map(transformModelToWorkflowForm), // system models that can do this task
])

const workflowsByRequirement = (requirementKey: string, isRequired: boolean): WorkflowForm[] => {
  return allWorkflows.value.filter((workflow: WorkflowForm) => {
    const model = models.value.find((model: Model) => model.model === workflow.model)
    if (!model) return !isRequired
    const isKeyPresent = model.requirements.includes(requirementKey)
    return isRequired ? isKeyPresent : !isKeyPresent
  })
}
const workflowsRequiringApiKey = computed(() => workflowsByRequirement('api_key', true))
const workflowsRequiringNoApiKey = computed(() => workflowsByRequirement('api_key', false))

const handleAddModelClicked = () => {
  isBYOM.value = true
  isCustomWorkflowModalVisible.value = true
  workflowBeingConfigured.value = {
    id: Math.floor(Math.random() * 1000000).toString(16),
    dataset: props.experiment.dataset,
    experiment_id: props.experiment.id,
    task_definition: props.experiment.task_definition,
    system_prompt: experimentPrompt.value || defaultPrompt.value,
    description: props.experiment.description,
    max_samples: props.experiment.max_samples,
    name: '',
    model: '',
    provider: '',
    secret_key_name: undefined,
    base_url: undefined,
    generation_config: {
      temperature: temperature.value,
      top_p: topP.value,
    },
  }
}

const handleRunClicked = () => {
  selectedWorkflowIds.value.forEach((selectedWorkflowId) => {
    // const workflow = allWorkflows.value.find((workflowForm: WorkflowForm) => workflowForm.id === selectedWorkflowId)!
    // const model = models.value.find((model: Model) => model.model === workflow.model)
    const foundCustomWorkflow = allWorkflows.value.find(
      (workflow) => workflow.id === selectedWorkflowId,
    )!
    const workflowPayload: WorkflowForm = foundCustomWorkflow
    createWorkflowMutation.mutate(workflowPayload)
    selectedWorkflowIds.value = []
  })
}

const handleCheckboxToggled = (workflow: WorkflowForm) => {
  selectedWorkflowIds.value = selectedWorkflowIds.value.includes(workflow.id)
    ? selectedWorkflowIds.value.filter((selectedWorkflowId) => selectedWorkflowId !== workflow.id)
    : [...selectedWorkflowIds.value, workflow.id]
}

const handleCloneClicked = (workflow: WorkflowForm) => {
  console.log('clone clicked', workflow)
  configuredWorkflowIds.value.push(workflow.id)
  const id = Math.floor(Math.random() * 1000000).toString(16)
  allWorkflows.value.push({
    ...workflow,
    id: id,
  })
  deletableWorkflowIds.value.push(id)
  // customModels.value.push({
  //   ...model,
  //   model: `${model.model}`,
  //   display_name: `${model.display_name}-copy`,
  // })
}

const handleCustomizeClicked = (workflow: WorkflowForm) => {
  console.log('customize clicked', workflow)
  workflowBeingConfigured.value = workflow
  isCustomWorkflowModalVisible.value = true
}

const saveModelConfiguration = (payload: WorkflowForm) => {
  const existingWorkflow = allWorkflows.value.find(
    (workflowForm: WorkflowForm) => workflowForm.id === payload.id,
  )
  if (!existingWorkflow) {
    // incase of BYOM
    allWorkflows.value.push({
      ...payload,
    })
    deletableWorkflowIds.value.push(payload.id)
  } else {
    // incase of configuring existing workflow
    allWorkflows.value = allWorkflows.value.map((workflowForm: WorkflowForm) => {
      if (workflowForm.id === payload.id) {
        return {
          ...workflowForm,
          ...payload,
        }
      }
      return workflowForm
    })
  }
  if (!configuredWorkflowIds.value.includes(payload.id)) {
    configuredWorkflowIds.value.push(payload.id)
  }
  if (!selectedWorkflowIds.value.includes(payload.id)) {
    selectedWorkflowIds.value.push(payload.id)
  }

  isBYOM.value = false
  workflowBeingConfigured.value = undefined
  isCustomWorkflowModalVisible.value = false
}

const handleDeleteClicked = (workflow: WorkflowForm) => {
  allWorkflows.value = allWorkflows.value.filter(
    (workflowForm: WorkflowForm) => workflowForm.id !== workflow.id,
  )
  configuredWorkflowIds.value = configuredWorkflowIds.value.filter(
    (configuredWorkflowId) => configuredWorkflowId !== workflow.id,
  )
  selectedWorkflowIds.value = selectedWorkflowIds.value.filter(
    (selectedWorkflowId) => selectedWorkflowId !== workflow.id,
  )
  deletableWorkflowIds.value = deletableWorkflowIds.value.filter(
    (deletableWorkflowId) => deletableWorkflowId !== workflow.id,
  )
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
