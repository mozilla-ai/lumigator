<template>
  <div class="l-dataset-empty">
    <h2 class="l-dataset-empty__instructions">
      {{ t('datasets.emptyDataset.title') }}
    </h2>
    <p class="l-dataset-empty__instructions-text">
      <span>
        {{ t('datasets.header.description') }}
      </span>
    </p>
    <Button
      rounded
      size="small"
      icon="pi pi-plus"
      label="Provide Dataset"
      class="l-dataset-empty__action-btn"
      @click="emit('l-add-dataset')"
    />
    <p class="l-dataset-empty__note">
      {{ t('datasets.emptyDataset.note') }}
      <span  class="l-dataset-empty__note-item"> {{ t('datasets.emptyDataset.examples') }}</span>,
      <span  class="l-dataset-empty__note-item">
        {{ t('datasets.emptyDataset.ground_truth') }}
      </span>.
    </p>
    <p class="l-dataset-empty__note">
      {{ t('datasets.emptyDataset.the') }}
      <span  class="l-dataset-empty__note-item">{{ t('datasets.emptyDataset.ground_truth') }}</span>
      {{ t('datasets.emptyDataset.columnOptional') }}
      <a href="https://mozilla-ai.github.io/lumigator/"
         target="_blank"
         style="background-color: transparent;"
      >{{ t('datasets.emptyDataset.learnMore') }} <span class="pi pi-arrow-up-right" /></a>
    </p>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import Button from 'primevue/button';

const { t } = useI18n();
const emit  = defineEmits(['l-add-dataset'])
</script>

<style scoped lang="scss">
.l-dataset-empty {
  $root: &;
  max-width: 600px;
  margin: auto;

  h2 {
    margin-bottom: $l-spacing-1/2;
  }

  &__instructions {
    color: $l-grey-100;
    font-size: $l-font-size;
    font-weight: $l-font-weight-normal;
    &-text {
      display: grid;
      place-items: center;
      color: $l-grey-100;
      font-size: $l-font-size;
      font-weight: $l-font-weight-normal;
      margin-bottom: $l-spacing-1;
    }
  }

  &__note {
    font-size: $l-font-size-sm;
    color: $l-grey-100;
  }

  &__action-btn {
    font-weight: $l-font-weight-normal;
    margin-top: $l-spacing-1;
    margin-bottom: $l-spacing-1/2;

  }

  &__note {
    margin-bottom: 0;
    &-item {
      background: $black;
    }
  }

}
</style>
