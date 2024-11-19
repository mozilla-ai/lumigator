<template>
  <div class="l-dataset-empty">
    <h2 class="l-dataset-empty__instructions">Submit a dataset to start using Lumigator.</h2>
    <p class="l-dataset-empty__instructions">
      The dataset file should contain a header row with the following columns: 'examples', 'ground_truth'. <br> The 'ground_truth' column is optional since you can generate it using Lumigator. </br>
      <a
        class="l-dataset-empty__-more"
      >Learn more.</a>
    </p>
    <Button
      rounded
      size="small"
      icon="pi pi-plus"
      label="Provide Dataset"
      class="l-dataset-empty__action-btn"
      @click="emit('l-add-dataset')"
    />
    <p class="l-dataset-empty__note">Currently only CSV files are supported.</p>
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
