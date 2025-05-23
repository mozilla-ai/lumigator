<template>
  <div class="l-dataset-empty">
    <h2 class="l-dataset-empty__instructions">
      Use a dataset as the basis for your evaluation. It includes data for the model you'd like to
      evaluate and possibly a ground truth "answer".
    </h2>
    <p class="l-dataset-empty__instructions-text">
      <span>
        If you don't have your dataset yet, you can use our
        <a
          href="https://github.com/mozilla-ai/lumigator/tree/main/lumigator/sample_data"
          target="_blank"
          style="background-color: transparent"
        >
          <span class="underline">sample datasets</span> <span class="pi pi-arrow-up-right"></span
        ></a>
      </span>
    </p>
    <Button
      rounded
      size="small"
      icon="pi pi-plus"
      label="Provide Dataset"
      class="l-dataset-empty__action-btn"
      @click="emit('l-add-dataset')"
    >
    </Button>
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
        href="https://mozilla-ai.github.io/lumigator/get-started/quickstart.html#upload-a-dataset"
        target="_blank"
        style="background-color: transparent"
        >Learn more <span class="pi pi-arrow-up-right"></span
      ></a>
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
