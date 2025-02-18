<template>
  <div class="l-experiment-details">
    <div class="l-experiment-details__header" style="position: sticky; top: 0; z-index: 100">
      <h3>{{ title }}</h3>
      <Button
        icon="pi pi-times"
        severity="secondary"
        rounded
        aria-label="Close"
        class="l-experiment-details__close"
        @click="emit('l-close-details')"
      >
      </Button>
    </div>
    <div class="l-experiment-details__content">
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">Title</div>
        <div class="l-experiment-details__content-field">
          {{ focusedItem?.name }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">description</div>
        <div class="l-experiment-details__content-field">
          {{ focusedItem?.description }}
        </div>
      </div>
      <div class="l-experiment-details__content-item row">
        <div class="l-experiment-details__content-label">status</div>
        <div class="l-experiment-details__content-field">
          <Tag
            :severity="tagSeverity"
            rounded
            :value="currentItemStatus"
            :pt="{ root: 'l-experiment-details__tag' }"
          ></Tag>
          <Button
            v-if="isWorkflowFocused"
            icon="pi pi-external-link"
            severity="secondary"
            size="small"
            label="Logs"
            aria-label="Logs"
            :disabled="currentItemStatus === WorkflowStatus.PENDING"
            style="padding: 0; background: transparent; border: none; font-weight: 400; gap: 4px"
            class="l-experiment-details__content-item-logs"
            iconClass="logs-btn"
            @click="emit('l-show-logs')"
          ></Button>
        </div>
      </div>
      <div
        v-if="isWorkflowFocused && selectedWorkflow"
        class="l-experiment-details__content-item"
        @click="copyToClipboard(selectedWorkflow.id)"
      >
        <div class="l-experiment-details__content-label">job id</div>
        <div
          class="l-experiment-details__content-field"
          style="display: flex; justify-content: space-between; cursor: pointer"
        >
          {{ selectedWorkflow?.id }}
          <i
            v-tooltip="'Copy ID'"
            :class="isCopied ? 'pi pi-check' : 'pi pi-clone'"
            style="font-size: 14px; padding-left: 3px"
          ></i>
        </div>
      </div>
      <div
        class="l-experiment-details__content-item"
        v-if="focusedItem && isExperiment(focusedItem)"
      >
        <div class="l-experiment-details__content-label">dataset</div>
        <div class="l-experiment-details__content-field">
          {{ focusedItem.dataset }}
        </div>
      </div>
      <div
        class="l-experiment-details__content-item"
        v-if="focusedItem && isExperiment(focusedItem)"
      >
        <div class="l-experiment-details__content-label">use-case</div>
        <div class="l-experiment-details__content-field">{{ focusedItem?.task }}</div>
      </div>
      <div v-if="!isWorkflowFocused" class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">Evaluated Models</div>
        <div class="l-experiment-details__content-field">
          <ul>
            <li v-for="workflow in selectedExperiment?.workflows" :key="workflow.id">
              · {{ workflow.model }}
            </li>
          </ul>
        </div>
      </div>
      <div v-if="isWorkflowFocused" class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">model</div>
        <div class="l-experiment-details__content-field">
          {{ (selectedWorkflow as any)?.model.path }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">created</div>
        <div class="l-experiment-details__content-field">
          {{ formatDate(focusedItem!.created_at) }}
        </div>
      </div>
      <!-- TODO: double check with design since this cant be shown now that we can lazily add workflows -->
      <!-- <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">run time</div>
        <div class="l-experiment-details__content-field">{{ focusedItemRunTime }}</div>
      </div> -->
      <div v-if="selectedExperiment" class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">samples limit</div>
        <div class="l-experiment-details__content-field">
          {{ selectedExperiment.max_samples }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">top-p</div>
        <div class="l-experiment-details__content-field">0.5</div>
      </div>
    </div>
    <!-- <div v-if="!isInference" class="l-experiment-details__actions"> -->
    <div class="l-experiment-details__actions">
      <Button
        rounded
        severity="secondary"
        size="small"
        icon="pi pi-external-link"
        label="View Results"
        :disabled="currentItemStatus !== WorkflowStatus.SUCCEEDED"
        @click="showResults"
      ></Button>
      <Button
        v-if="isWorkflowFocused"
        rounded
        severity="secondary"
        size="small"
        icon="pi pi-download"
        label="Download Results"
        :disabled="currentItemStatus !== WorkflowStatus.SUCCEEDED"
        @click="emit('l-download-results', selectedWorkflow)"
      ></Button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref, type ComputedRef } from 'vue'
import { storeToRefs } from 'pinia'
import { useExperimentStore } from '@/stores/experimentsStore'

import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { formatDate } from '@/helpers/formatDate'
import { WorkflowStatus, type Workflow } from '@/types/Workflow'
import type { ExperimentNew } from '@/types/ExperimentNew'

const emit = defineEmits([
  'l-close-details',
  'l-experiment-results',
  'l-job-results',
  'l-show-logs',
  'l-download-results',
])

defineProps({
  title: {
    type: String,
    required: true,
  },
})
const experimentStore = useExperimentStore()
const { experiments, selectedExperiment, selectedWorkflow } = storeToRefs(experimentStore)
const isCopied = ref(false)

const copyToClipboard = async (longString: string) => {
  isCopied.value = true
  setTimeout(() => {
    isCopied.value = false
  }, 3000)
  await navigator.clipboard.writeText(longString)
}

const isWorkflowFocused = computed(() => Boolean(selectedWorkflow.value))
// const allJobs = computed(() => [...jobs.value, ...inferenceJobs.value])

// TODO: this needs refactor when the backend provides experiment id
const currentItemStatus = computed(() => {
  if (isWorkflowFocused.value) {
    return selectedWorkflow.value?.status
  }
  const selected = experiments.value.find(
    (experiment) => experiment.id === selectedExperiment.value?.id,
  )
  return selected ? selected.status : selectedExperiment.value?.status
})

// const isInference = computed(() => {
//   return isWorkflowFocused.value && inferenceJobs.value.some((job) => job.id === selectedWorkflow.value?.id)
// })

const focusedItem: ComputedRef<Workflow | ExperimentNew | undefined> = computed(() => {
  if (selectedWorkflow.value) {
    return selectedWorkflow.value
  }
  const selected = experiments.value.find(
    (experiment) => experiment.id === selectedExperiment.value?.id,
  )
  return selected ? selected : selectedExperiment.value
})

const tagSeverity = computed(() => {
  const status = currentItemStatus.value
  switch (status) {
    case WorkflowStatus.SUCCEEDED:
      return 'success'
    case WorkflowStatus.FAILED:
      return 'danger'
    case WorkflowStatus.INCOMPLETE:
      return 'info'
    default:
      return 'warn'
  }
})

// const focusedItemRunTime = computed(() => {
//   if (isWorkflowFocused.value) {
//     return selectedWorkflow.value?.runTime ? selectedWorkflow.value?.runTime : '-'
//   }

//   if (
//     currentItemStatus.value !== WorkflowStatus.RUNNING &&
//     currentItemStatus.value !== WorkflowStatus.PENDING
//   ) {
//     const endTimes = selectedExperiment.value?.workflows.map((workflow) => workflow.end_time) || []
//     const lastEndTime = endTimes.reduce((latest, current) => {
//       return new Date(latest) > new Date(current) ? latest : current
//     })
//     if (lastEndTime && selectedExperiment.value) {
//       return calculateDuration(selectedExperiment.value?.created_at, lastEndTime)
//     }
//   }
//   return '-'
// })

const showResults = () => {
  if (isWorkflowFocused.value) {
    emit('l-job-results', selectedWorkflow.value)
    return
  }
  emit('l-experiment-results', selectedExperiment.value)
}

function isExperiment(item: ExperimentNew | Workflow): item is ExperimentNew {
  return 'workflows' in item
}

// function _isJob(item: ExperimentNew | JobDetails): item is JobDetails {
//   return 'entrypoint' in item
// }
</script>

<style lang="scss">
@use '@/styles/variables' as *;
.l-experiment-details {
  $root: &;
  display: flex;
  flex-direction: column;

  &__header {
    padding-bottom: $l-spacing-1;
    display: flex;
    justify-content: space-between;
    background-color: $l-main-bg;

    h3 {
      font-weight: $l-font-weight-normal;
      font-size: $l-font-size-md;
      color: $l-grey-100;
    }

    button {
      margin: 0 2px;
      background-color: $l-main-bg;
      border: none;
      color: $l-grey-100;
    }
  }

  &__content,
  &__content-item {
    display: flex;
    flex-direction: column;
    font-size: $l-table-font-size;
    &.row {
      flex-direction: row;
      justify-content: space-between;
    }

    &-label {
      color: $l-grey-200;
      text-transform: uppercase;
      font-weight: $l-font-weight-bold;
      font-size: $l-font-size-sm;
    }

    &-logs {
      font-size: $l-font-size-sm;
      padding: 0;

      span {
        color: $l-grey-100;
      }
      .logs-btn {
        font-size: 12px !important;
      }
    }

    &-field {
      display: flex;
      gap: 9px;
    }
    li {
      color: $white;
      font-weight: $l-font-weight-semibold;
    }
  }

  &__content-item {
    padding: calc($l-spacing-1 / 2) 0;

    .p-tag-label {
      font-size: $l-font-size-sm;
      color: $l-grey-100;
      line-height: 1;
      font-weight: $l-font-weight-normal;
    }
  }

  &__actions {
    padding: $l-spacing-1 0;
    display: flex;
    gap: $l-spacing-1;
  }

  &__tag {
    text-transform: uppercase;
  }
}
</style>
