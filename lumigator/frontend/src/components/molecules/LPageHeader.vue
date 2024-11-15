<template>
  <div class="l-page-header">
    <div class="l-page-header__text-content">
      <h3>{{ title }}</h3>
      <p>{{ subtitle }}</p>
    </div>
    <Button
      rounded
      size="small"
      icon="pi pi-plus"
      :label="buttonLabel"
      class="l-page-header__action-btn"
      @click="handleAction"
    />
  </div>
</template>

<script setup>
import Button from 'primevue/button';

 defineProps({
  title: String,
  subtitle: String,
  buttonLabel: String
});

const emit = defineEmits(['l-header-action']);

const handleAction = () => {
  emit('l-header-action')
};
</script>

<style scoped lang="scss">
.l-page-header {
  $root: &;
  display: flex;
  width: 100%;
  justify-content: space-between;
  align-items: center;

  &__text-content {
    color: $l-grey-200;
    display: flex;
    align-items: start;
    flex-direction: column;

    h3 {
      font-size: $l-font-size;
    }

    p {
      font-size: $l-font-size-sm;
    }
  }

  &__action-btn {
    font-weight: $l-font-weight-normal;
    &:hover {
      color:$white;
    }
  }

}
</style>
