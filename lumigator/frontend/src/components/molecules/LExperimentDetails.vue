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
          {{ focusedItem.name }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">description</div>
        <div class="l-experiment-details__content-field">
          {{ focusedItem.description }}
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
          />
          <Button
            v-if="isJobFocused"
            icon="pi pi-external-link"
            severity="secondary"
            size="small"
            label="Logs"
            aria-label="Logs"
            :disabled="currentItemStatus === 'PENDING'"
            style="padding: 0; background: transparent; border: none; font-weight: 400; gap: 4px"
            class="l-experiment-details__content-item-logs"
            iconClass="logs-btn"
            @click="emit('l-show-logs')"
          />
        </div>
      </div>
      <div
        v-if="isJobFocused"
        class="l-experiment-details__content-item"
        @click="copyToClipboard(selectedJob.id)"
      >
        <div class="l-experiment-details__content-label">job id</div>
        <div
          class="l-experiment-details__content-field"
          style="display: flex; justify-content: space-between; cursor: pointer"
        >
          {{ selectedJob.id }}
          <i
            v-tooltip="'Copy ID'"
            :class="isCopied ? 'pi pi-check' : 'pi pi-clone'"
            style="font-size: 14px; padding-left: 3px"
          />
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">dataset</div>
        <div class="l-experiment-details__content-field">
          {{ focusedItem.dataset.name }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">use-case</div>
        <div class="l-experiment-details__content-field">{{ focusedItem.useCase }}</div>
      </div>
      <div v-if="!isJobFocused" class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">Evaluated Models</div>
        <div class="l-experiment-details__content-field">
          <ul>
            <li v-for="job in selectedExperiment.jobs" :key="job.id">· {{ job.model.path }}</li>
          </ul>
        </div>
      </div>
      <div v-if="isJobFocused" class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">model</div>
        <div class="l-experiment-details__content-field">{{ selectedJob.model.path }}</div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">created</div>
        <div class="l-experiment-details__content-field">
          {{ formatDate(focusedItem.created) }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">run time</div>
        <div class="l-experiment-details__content-field">{{ focusedItemRunTime }}</div>
      </div>
      <div v-if="selectedExperiment" class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">samples limit</div>
        <div class="l-experiment-details__content-field">
          {{ selectedExperiment.samples }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">top-p</div>
        <div class="l-experiment-details__content-field">0.5</div>
      </div>
    </div>
    <div v-if="!isInference" class="l-experiment-details__actions">
      <Button
        rounded
        severity="secondary"
        size="small"
        icon="pi pi-external-link"
        label="View Results"
        :disabled="currentItemStatus !== 'SUCCEEDED'"
        @click="showResults"
      />
      <Button
        v-if="isJobFocused"
        rounded
        severity="secondary"
        size="small"
        icon="pi pi-download"
        label="Download Results"
        :disabled="currentItemStatus !== 'SUCCEEDED'"
        @click="emit('l-dnld-results', selectedJob)"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useExperimentStore } from '@/stores/experiments/store'
import { formatDate, calculateDuration } from '@/helpers/index'
import Button from 'primevue/button'
import Tag from 'primevue/tag'

const emit = defineEmits([
  'l-close-details',
  'l-experiment-results',
  'l-job-results',
  'l-show-logs',
  'l-dnld-results',
])

defineProps({
  title: {
    type: String,
    required: true,
  },
})
const experimentStore = useExperimentStore()
const { experiments, selectedExperiment, jobs, inferenceJobs, selectedJob } =
  storeToRefs(experimentStore)
const isCopied = ref(false)

const copyToClipboard = async (longString) => {
  isCopied.value = true
  setTimeout(() => {
    isCopied.value = false
  }, 3000)
  await navigator.clipboard.writeText(longString)
}

const isJobFocused = computed(() => selectedJob.value !== null)
const allJobs = computed(() => [...jobs.value, ...inferenceJobs.value])

// TODO: this needs refactor when the backend provides experiment id
const currentItemStatus = computed(() => {
  if (isJobFocused.value) {
    const selected = allJobs.value.filter((job) => job.id === selectedJob.value.id)[0]
    return selected ? selected.status : selectedJob.value.status
  }
  const selected = experiments.value.filter(
    (experiment) => experiment.id === selectedExperiment.value.id,
  )[0]
  return selected ? selected.status : selectedExperiment.value.status
})

const isInference = computed(() => {
  return isJobFocused.value && inferenceJobs.value.some((job) => job.id === selectedJob.value.id)
})

const focusedItem = computed(() => {
  if (selectedJob.value) {
    return selectedJob.value
  }
  const selected = experiments.value.filter(
    (experiment) => experiment.id === selectedExperiment.value.id,
  )[0]
  return selected ? selected : selectedExperiment.value
})

const tagSeverity = computed(() => {
  const status = currentItemStatus.value
  switch (status) {
    case 'SUCCEEDED':
      return 'success'
    case 'FAILED':
      return 'danger'
    case 'INCOMPLETE':
      return 'info'
    default:
      return 'warn'
  }
})

const focusedItemRunTime = computed(() => {
  if (isJobFocused.value) {
    return selectedJob.value.runTime ? selectedJob.value.runTime : '-'
  }

  if (currentItemStatus.value !== 'RUNNING' && currentItemStatus.value !== 'PENDING') {
    const endTimes = selectedExperiment.value.jobs.map((job) => job.end_time)
    const lastEndTime = endTimes.reduce((latest, current) => {
      return new Date(latest) > new Date(current) ? latest : current
    })
    if (lastEndTime) {
      return calculateDuration(selectedExperiment.value.created, lastEndTime)
    }
  }
  return '-'
})

const showResults = () => {
  if (isJobFocused.value) {
    emit('l-job-results', selectedJob.value)
    return
  }
  emit('l-experiment-results', selectedExperiment.value)
}
</script>

<style lang="scss">
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
    font-size: $l-menu-font-size;
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
    padding: $l-spacing-1/2 0;

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
