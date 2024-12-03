<template>
  <div class="l-dataset-empty">
    <h2 class="l-dataset-empty__instructions">Submit a dataset to start using Lumigator.</h2>
    <p class="l-dataset-empty__instructions-text">
      <span>
        The dataset file should contain a
        header row with the following columns: 'examples', 'ground_truth'.
      </span>
      <span>
        The 'ground_truth' column is optional since you can generate it using Lumigator.
        <a href="https://mozilla-ai.github.io/lumigator/"
           target="_blank"
        >Learn more <span class="pi pi-arrow-up-right" /></a>
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
      <span  class="l-dataset-empty__note-item">examples</span>,
      <span  class="l-dataset-empty__note-item">ground_truth</span>.
    </p>
    <p class="l-dataset-empty__note">
      The
      <span  class="l-dataset-empty__note-item">ground_truth</span>
      column is optional, as it can be generated using Lumigator.
    </p>
  </div>
</template>

<script setup>
import Button from 'primevue/button';
const emit  = defineEmits(['l-add-dataset'])
</script>

<style scoped lang="scss">
.l-dataset-empty {
  $root: &;
  margin: auto;

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

    &:hover {
      color: $white;
    }
  }
  p {
    margin-bottom: $l-spacing-1;
  }

  a {
    background-color: $l-card-bg;
    color: $l-primary-color;
  }

}
</style>
