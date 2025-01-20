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
          icon="pi pi-download"
          severity="secondary"
          variant="text"
          rounded
          @click="emit('l-download-dataset')"
        />
        <Button
          severity="secondary"
          icon="pi pi-bin"
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
      <div
        class="l-dataset-details__content-item"
        @click="copyToClipboard(selectedDataset.id)"
      >
        <span class="l-dataset-details__content-label">dataset id</span>
        <span class="l-dataset-details__content-field">
          {{ selectedDataset.id }}
          <i
            v-tooltip="'Copy ID'"
            :class="isCopied ? 'pi pi-check' : 'pi pi-clone'"
            style="font-size: 14px;padding-left: 3px;cursor: pointer;"
          />
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
      <div class="l-dataset-details__actions">
        <Button
          rounded
          severity="secondary"
          size="small"
          icon="pi pi-microchip"
          label="Use in Experiment"
          class="l-dataset-empty__action-btn"
          :disabled="!selectedDataset.ground_truth"
          @click="emit('l-experiment', selectedDataset)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasets/store'
import { useSlidePanel } from '@/composables/SlidingPanel';
import { formatDate } from '@/helpers/index'
import Button from 'primevue/button';

const datasetStore = useDatasetStore();
const { selectedDataset } = storeToRefs(datasetStore);
const { showSlidingPanel } = useSlidePanel();
const isCopied = ref(false);

const emit = defineEmits([
  'l-delete-dataset',
  'l-download-dataset',
  'l-details-closed',
  'l-experiment'
])

const copyToClipboard = async (longString) => {
  isCopied.value = true;
  setTimeout(() => {
    isCopied.value = false;
  }, 3000);
  await navigator.clipboard.writeText(longString);
};

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
    align-items: center;

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

    &-actions {
      display: flex;
      align-items: center;

      > * {
        height: 14px;
      }
    }
  }

  &__content, &__content-item {
    display: flex;
    flex-direction: column;
    font-size: $l-menu-font-size;
    font-size: $l-table-font-size;

    &-label {
      color: $l-grey-200;
      text-transform: uppercase;
      font-weight: $l-font-weight-bold;
      font-size: $l-font-size-sm;
    }

    &-field {
      display: flex;
      justify-content: space-between;
    }

  }
   &__content-item {
    padding: $l-spacing-1/2 0;
   }

   &__actions {
    padding: $l-spacing-1 0;
    display: flex;
    justify-content: center;
   }

}
</style>
