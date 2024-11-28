<template>
  <div class="l-experiment-details">
    <div
      class="l-experiment-details__header"
    >
      <h3>{{ selectedExperiment.name }}</h3>
      <p v-if="selectedExperiment.description">{{ selectedExperiment.description }}</p>
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
      <div
        class="l-experiment-details__content-item"
        @click="copyToClipboard(selectedExperiment.id)"
      >
        <div class="l-experiment-details__content-label">experiment id</div>
        <div
          class="l-experiment-details__content-field"
          style="display: flex; justify-content: space-between;cursor:pointer"
        >
          {{ selectedExperiment.id }}
          <i
            v-tooltip="'Copy ID'"
            class="pi pi-clone"
            style="font-size: 12px;"
          />
        </div>
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
        :disabled="!(selectedExperiment.status === 'SUCCEEDED'
          || selectedExperiment.status === 'FAILED')"
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
    .filter((job) => job.id === selectedExperiment.value.id)[0]
  return selected ? selected.status : selectedExperiment.value.status;
})

const copyToClipboard = async (longString) => {
    await navigator.clipboard.writeText(longString);

};

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
    flex-direction: column;
    gap: 10px;
    background-color: $l-main-bg;

    h3 {
      font-weight: $l-font-weight-normal;
      font-size: $l-font-size-md;
      color: $l-grey-150;
    }

    p {
      color: $l-grey-150;
      font-size: $l-menu-font-size;
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
