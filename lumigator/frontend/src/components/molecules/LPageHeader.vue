<template>
  <div
    class="l-page-header"
    :class="{'column': column}"
  >
    <div class="l-page-header__text-content">
      <h3>{{ title }} </h3>
      <p class="l-page-header__text-content-description">{{ description }}</p>
      <!-- <p>{{ subtitle }}</p> -->
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
  title: {
    type: String,
    default: '',
    required: false
  },
  subtitle: {
    type: String,
    default: '',
    required: false
  },
  description: {
    type: String,
    default: '',
    required: false
  },
  buttonLabel: {
    type: String,
    default: '',
    required: false
  },
  column: {
    type: Boolean,
    default: false,
    required: false
  }
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
  gap: 2 * $l-spacing-1;

  &__text-content {
    color: $l-grey-100;
    display: flex;
    align-items: start;
    flex-direction: column;

    h3 {
      font-size: $l-font-size;
      font-weight: $l-font-weight-semibold;
    }

    p {
      font-size: $l-font-size-sm;
    }

    &-description {
      padding-top: $l-spacing-1/2;
      max-width: 400px;
      text-align: left;
    }
  }

  &__action-btn {
    font-weight: $l-font-weight-normal;
    &:hover {
      color:$white;
    }
  }

  &.column{
   width: 100%;
   flex-direction: column;
  }

}
</style>
