<template>
  <div class="l-experiment-empty">
    <h2 class="l-experiment-empty__instructions">
      Experiments are a logical sequence of inference and evaluationtasks that
      run sequentially to evaluate an LLM.</h2>
    <p class="l-experiment-empty__instructions-text">

      <span>
        We evaluate Summarization tasks using ROUGE, METEOR, and BERT score,
        each focusing on different aspects of prediction-ground truth similarity. Learn more↗
        <a
          class="l-experiment-empty__-more"
        >Learn more</a>
      </span>
    </p>
    <Button
      rounded
      size="small"
      icon="pi pi-plus"
      label="Create experiment"
      class="l-experiment-empty__action-btn"
      @click="emit('l-add-experiment')"
    />
    <p class="l-experiment-empty__note">Currently only CSV files are supported.</p>
  </div>
</template>

<script setup>
import Button from 'primevue/button';
const emit  = defineEmits(['l-add-experiment'])
</script>

<style scoped lang="scss">
.l-experiment-empty {
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
