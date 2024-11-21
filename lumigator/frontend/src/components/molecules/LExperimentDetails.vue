<template>
  <div class="l-experiment-details">
    <div
      class="l-experiment-details__header"
      style="position: sticky; top: 0;z-index:100"
    >
      <h3>Experiment Details</h3>
      <Button
        icon="pi pi-times"
        severity="secondary"
        rounded
        aria-label="Close"
        class="l-experiment-form__close"
        @click="emit('l-close-details')"
      />
    </div>
    <div class="l-experiment-details__content">
      <div class="l-experiment-details__content-item row">
        <div class="l-experiment-details__content-label">status</div>
        <div class="l-experiment-details__content-field">
          <Tag
            v-if="selectedExperiment.status === 'SUCCEEDED' "
            severity="success"
            rounded
            :value="selectedExperiment.status"
            :pt="{root:'l-experiment-details__tag'}"
          />
          <Tag
            v-else-if="selectedExperiment.status === 'FAILED' "
            severity="danger"
            rounded
            :value="selectedExperiment.status"
            :pt="{root:'l-experiment-details__tag'}"
          />
          <Tag
            v-else
            severity="warn"
            rounded
            :value="selectedExperiment.status"
            :pt="{root:'l-experiment-details__tag'}"
          />

        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">experiment id</div>
        <div class="l-experiment-details__content-field">{{ selectedExperiment.jobId }}</div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">dataset</div>
        <div class="l-experiment-details__content-field">
          {{ selectedExperiment.dataset.name }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">use-case</div>
        <div class="l-experiment-details__content-field">{{ selectedExperiment.useCase }}</div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">model</div>
        <div class="l-experiment-details__content-field">{{ selectedExperiment.model.path }}</div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">created</div>
        <div class="l-experiment-details__content-field">
          {{ formatDate(selectedExperiment.created) }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">run time</div>
        <div class="l-experiment-details__content-field">{{ selectedExperiment.runTime }}</div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">samples limit</div>
        <div class="l-experiment-details__content-field">
          {{ selectedExperiment.evaluation.max_samples }}
        </div>
      </div>
      <div class="l-experiment-details__content-item">
        <div class="l-experiment-details__content-label">top-p</div>
        <div class="l-experiment-details__content-field">0.5</div>
      </div>
    </div>
    <div class="l-experiment-details__actions">
      <Button
        rounded
        severity="secondary"
        size="small"
        icon="pi pi-external-link"
        label="View Results"
        class="l-dataset-empty__action-btn"
        @click="emit('l-results', selectedExperiment)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useExperimentStore } from '@/stores/experiments/store'
import { useHealthStore } from '@/stores/health/store'
import { formatDate, calculateDuration } from '@/helpers/index'
import Button from 'primevue/button';
import Tag from 'primevue/tag';

const emit = defineEmits(['l-close-details', 'l-results']);

const experimentStore = useExperimentStore();
const { selectedExperiment } = storeToRefs(experimentStore);
const healthStore = useHealthStore();
const { runningJobs } = storeToRefs(healthStore);

const experimentStatus = computed(() => {
  const selected = runningJobs.value
    .filter((job) => job.id === selectedExperiment.value.jobId)[0]
  return selected ? selected.status : selectedExperiment.value.status;
})

watch(experimentStatus, (newStatus) => {
  selectedExperiment.value.status = newStatus;
  if (selectedExperiment.value.end_time) {
    selectedExperiment.value.runTime =
      calculateDuration(selectedExperiment.value.start_time, selectedExperiment.value.end_time);
    }
});
</script>

<style scoped lang="scss">
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
      color: $l-grey-150;
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
    font-size: $l-font-size-sm;
    &.row {
      flex-direction: row;
      justify-content: space-between;
    }

    &-label {
      color: $l-grey-200;
      text-transform: uppercase;
      font-weight: $l-font-weight-bold;
    }

  }

  &__content-item {
    padding: $l-spacing-1/2 0;
  }

  &__tag {
    font-size: $l-font-size-sm;
    color: $l-grey-150;
    line-height: 1;
    font-weight: $l-font-weight-normal;
  }
  &__actions {
    padding: $l-spacing-1 0;
  }
}
</style>
