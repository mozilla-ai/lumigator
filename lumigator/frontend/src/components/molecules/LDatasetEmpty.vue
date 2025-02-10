<template>
  <div class="l-dataset-empty">
    <h2 class="l-dataset-empty__instructions">Submit a dataset to start using Lumigator.</h2>
    <p class="l-dataset-empty__instructions-text">
      <span>
        Use a dataset as the basis for your evaluation. It includes data for the model you'd like to
        evaluate and possibly a ground truth "answer".
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
      Your dataset should be a CSV file and include the following columns:
      <span class="l-dataset-empty__note-item">examples</span>,
      <span class="l-dataset-empty__note-item">ground_truth</span>.
    </p>
    <p class="l-dataset-empty__note">
      The
      <span class="l-dataset-empty__note-item">ground_truth</span>
      column is optional, as it can be generated using Lumigator.
      <a
        href="https://mozilla-ai.github.io/lumigator/"
        target="_blank"
        style="background-color: transparent"
        >Learn more <span class="pi pi-arrow-up-right"
      /></a>
    </p>
  </div>
</template>

<script lang="ts" setup>
import Button from 'primevue/button'
const emit = defineEmits(['l-add-dataset'])
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-dataset-empty {
  $root: &;
  max-width: 600px;
  margin: auto;

  h2 {
    margin-bottom: calc($l-spacing-1 / 2);
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
    margin-bottom: calc($l-spacing-1 / 2);
  }

  &__note {
    margin-bottom: 0;
    &-item {
      background: $black;
    }
  }
}
</style>
