<template>
  <div>
    <Drawer
      v-model:visible="drawerVisible"
      :header
      position="full"
      class="l-results-drawer"
      @hide="emit('l-close-results')"
    >
      <slot />
    </Drawer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Drawer from 'primevue/drawer';

const emit = defineEmits(['l-close-results'])
defineProps({
  header: {
    type: String,
    required: true,
    default: 'Results'
  }
})
const drawerVisible = ref(true);

</script>

<!-- Style here cannot be scoped because Drawer is attached to the DOM
after the LResultsDrawer is mounted -->
<style lang="scss">
.l-results-drawer {
  $root: &;
  .p-drawer-title {
    color: $l-grey-150;
    font-size: $l-font-size-md;
  }
}
</style>
