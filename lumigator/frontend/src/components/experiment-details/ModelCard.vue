<template>
  <article class="model-card">
    <div class="model-field">
      <Checkbox
        :input-id="workflow.id"
        :name="workflow.id"
        :value="workflow.id"
        binary
        :model-value="isSelected"
        @update:model-value="emit('checkboxToggled', workflow)"
      ></Checkbox>
      <label :for="workflow.model" class="model-label">{{ workflow.name }}</label>
      <!-- <Button
                    as="a"
                    icon="pi pi-external-link"
                    severity="secondary"
                    variant="text"
                    rounded
                    class="l-models__external-link"
                    :href="model.website_url"
                    target="_blank"
                    @click.stop
                  ></Button> -->
    </div>
    <div class="model-actions">
      <Button
        v-if="isDeletable"
        icon="pi pi-trash"
        severity="secondary"
        @click="emit('deleteClicked', workflow)"
        variant="text"
        rounded
        aria-label="Delete"
      ></Button>
      <Button
        icon="pi pi-clone"
        severity="secondary"
        @click="emit('cloneClicked', workflow)"
        variant="text"
        rounded
        aria-label="Clone"
      ></Button>
      <Button
        icon="pi pi-sliders-v"
        :severity="isCustom ? 'primary' : 'secondary'"
        @click="emit('customizeClicked', workflow)"
        variant="text"
        rounded
        aria-label="Customize"
      ></Button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { Button, Checkbox } from 'primevue'
import type { WorkflowForm } from './AddWorkflowsTab.vue'

const { isSelected, isCustom, isDeletable } = defineProps<{
  workflow: WorkflowForm
  isSelected: boolean
  isCustom: boolean
  isDeletable: boolean
}>()
const emit = defineEmits<{
  checkboxToggled: [payload: WorkflowForm]
  deleteClicked: [payload: WorkflowForm]
  cloneClicked: [payload: WorkflowForm]
  customizeClicked: [payload: WorkflowForm]
}>()
</script>

<style scoped lang="scss">
.model-card {
  display: flex;
  padding: 0rem 0.5rem 0rem 0.75rem;
  min-width: 19.875rem;
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

.model-label {
  color: var(--l-grey-100);
  font-family: Inter;
  font-size: 0.75rem;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  letter-spacing: -0.015rem;
}
</style>
