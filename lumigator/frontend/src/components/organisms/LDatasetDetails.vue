<template>
  <div class="l-dataset-details">
    <Button
      icon="pi pi-times"
      severity="secondary"
      rounded
      aria-label="Close"
      class="l-dataset-details__close"
      @click="onCloseDetails"
    />
    <div class="l-dataset-details__header">
      <h3>Dataset Details</h3>
      <span class="l-dataset-details__header-actions">
        <Button
          icon="pi pi-external-link"
          severity="secondary"
          variant="text"
          rounded
        />
        <Button
          icon="pi pi-download"
          severity="secondary"
          variant="text"
          rounded
        />
        <Button
          severity="secondary"
          icon="pi pi-trash"
          variant="text"
          rounded
          @click="emit('l-delete-dataset', selectedDataset)"
        />
      </span>
    </div>
    <div class="l-dataset-details__content">
      <div class="l-dataset-details__content-item">
        <span class="l-dataset-details__content-label">filename</span>
        <span class="l-dataset-details__content-field">
          {{ selectedDataset.filename }}
        </span>
      </div>
      <div class="l-dataset-details__content-item">
        <span class="l-dataset-details__content-label">dataset id</span>
        <span class="l-dataset-details__content-field">
          {{ selectedDataset.id }}
        </span>
      </div>
      <div class="l-dataset-details__content-item">
        <span class="l-dataset-details__content-label">submitted</span>
        <span class="l-dataset-details__content-field">
          {{ formatDate(selectedDataset.created_at) }}
        </span>
      </div>
      <div class="l-dataset-details__content-item">
        <span class="l-dataset-details__content-label">file size</span>
        <span class="l-dataset-details__content-field">
          {{ Math.floor(selectedDataset.size / 1000) }} KB
        </span>
      </div>
      <div class="l-dataset-details__content-item">
        <span class="l-dataset-details__content-label">ground truth</span>
        <span class="l-dataset-details__content-field">{{ selectedDataset.ground_truth }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasets/store'
import { useSlidePanel } from '@/composables/SlidingPanel';
import { formatDate } from '@/helpers/index'
import Button from 'primevue/button';

const datasetStore = useDatasetStore();
const { selectedDataset } = storeToRefs(datasetStore);
const { showSlidingPanel } = useSlidePanel();

const emit = defineEmits(['l-delete-dataset', 'l-details-closed'])

function onCloseDetails() {
  showSlidingPanel.value = false;
  emit('l-details-closed')
}

</script>

<style lang="scss" scoped>
.l-dataset-details {
  $root: &;
  display: flex;
  flex-direction: column;

  &__close {
    margin-left: auto;
  }

  &__header {
    color: $l-grey-100;
    display: flex;
    padding: $l-spacing-1 0;
    justify-content: space-between;

    h3 {
      font-weight: $l-font-weight-normal;
      font-size: $l-font-size-md;
    }

    button {
      margin: 0 2px;
      background-color: $l-main-bg;
      border: none;
      color: $l-grey-100;
    }
  }

  &__content, &__content-item {
    display: flex;
    flex-direction: column;
    font-size: $l-menu-font-size;
    font-size:$l-font-size-sm;

    &-label {
      color: $l-grey-200;
      text-transform: uppercase;
    }

  }
   &__content-item {
    padding: $l-spacing-1/2 0;
   }

}
</style>
