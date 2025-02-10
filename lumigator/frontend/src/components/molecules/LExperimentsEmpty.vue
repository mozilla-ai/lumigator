<template>
  <div class="l-experiment-empty">
    <h2 class="l-experiment-empty__instructions">
      Experiments are a logical sequence of inference and evaluation tasks that run sequentially to
      evaluate an LLM.
    </h2>
    <p class="l-experiment-empty__instructions-text"></p>
    <Button
      rounded
      size="small"
      icon="pi pi-plus"
      label="Create Experiment"
      class="l-experiment-empty__action-btn"
      @click="emit('l-add-experiment')"
    />
    <p class="l-experiment-empty__note">
      <span>
        We evaluate Summarization tasks using ROUGE, METEOR, and BERT score, each focusing on
        different aspects of prediction-ground truth similarity.
        <a
          href="https://mozilla-ai.github.io/lumigator/"
          target="_blank"
          style="background-color: transparent"
          >Learn more <span class="pi pi-arrow-up-right"
        /></a>
      </span>
    </p>
  </div>
</template>

<script lang="ts" setup>
import Button from 'primevue/button'
const emit = defineEmits(['l-add-experiment'])
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.l-experiment-empty {
  $root: &;
  margin: auto;
  max-width: 500px;

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
    padding-top: calc($l-spacing-1 / 2);
    font-size: $l-font-size-sm;
    color: $l-grey-100;
  }

  &__action-btn {
    font-weight: $l-font-weight-normal;
    margin-top: $l-spacing-1;
    margin-bottom: calc($l-spacing-1 / 2);
  }

  p {
    margin-bottom: $l-spacing-1;
  }
}
</style>
