<template>
  <div class="l-experiment-empty">
    <h2 class="l-experiment-empty__instructions">
      {{ t('experiments.header.description') }}
    </h2>
    <p class="l-experiment-empty__instructions-text">


    </p>
    <Button
      rounded
      size="small"
      icon="pi pi-plus"
      :label="t('experiments.header.createExperiment')"
      class="l-experiment-empty__action-btn"
      @click="emit('l-add-experiment')"
    />
    <p class="l-experiment-empty__note">
      <span>
        {{ t('experiments.emptyExperiments.note') }}
        <a href="https://mozilla-ai.github.io/lumigator/"
           target="_blank"
           style="background-color: transparent;"
        >{{ t('experiments.emptyExperiments.learnMore') }}
          <span class="pi pi-arrow-up-right" /></a>
      </span></p>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import Button from 'primevue/button';

const { t } = useI18n();
const emit  = defineEmits(['l-add-experiment'])
</script>

<style scoped lang="scss">
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
    padding-top: $l-spacing-1/2;
    font-size: $l-font-size-sm;
    color: $l-grey-100;
  }

  &__action-btn {
    font-weight: $l-font-weight-normal;
    margin-top: $l-spacing-1;
    margin-bottom: $l-spacing-1/2;
  }

  p {
    margin-bottom: $l-spacing-1;
  }

}
</style>
