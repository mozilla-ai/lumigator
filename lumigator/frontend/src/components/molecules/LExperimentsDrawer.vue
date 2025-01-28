<template>
  <div>
    <Drawer
      v-model:visible="drawerVisible"
      :header
      :position
      class="l-experiments-drawer"
      :class="[{'dark ': position === 'bottom'}]"
      @hide="emit('l-drawer-closed')"
    >
      <template
        v-if=" position === 'bottom'"
        #header
      >
        <div class="l-experiments-drawer__header">
          <span class="l-experiments-drawer__header-title">Experiment Logs</span>
          <!-- header actions here -->
        </div>
      </template>
      <slot />
    </Drawer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Drawer from 'primevue/drawer';

const emit = defineEmits(['l-drawer-closed'])
defineProps({
  header: {
    type: String,
    required: true,
    default: 'Results'
  },
  position: {
    type: String,
    required: false,
    default: 'full'
  }
})
const drawerVisible = ref(true);

</script>

<!-- Style here cannot be scoped because Drawer is attached to the DOM
after the LResultsDrawer is mounted -->
<style lang="scss">
.l-experiments-drawer {
  $root: &;

  .p-drawer-title {
    color: $l-grey-100;
    font-size: $l-font-size-md;
  }

  &__header {
    width: 90%;
    display: flex;
    justify-content: space-between;
    padding-top: $l-spacing-1 / 2;
    padding-bottom: 0;

    &-title {
      font-size: $l-menu-font-size;
    }

    &-actions {
      display: flex;
      gap: $l-spacing-1;

      span {
        cursor: pointer;
      }
    }
  }
}

.p-drawer.p-component.l-experiments-drawer {
  height: $l-bottom-drawer-height;
  &.dark {
    background-color: $l-logs-bg;
    border: none;

    .p-drawer-header {
      color: $l-grey-100;
      padding: 0.5rem 2rem;
    }
  }
}
</style>
