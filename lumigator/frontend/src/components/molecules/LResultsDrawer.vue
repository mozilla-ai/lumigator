<template>
  <div class="card flex justify-center">
    <Drawer
      v-model:visible="drawerVisible"
      header="Drawer"
      position="full"
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

const drawerVisible = ref(true);

</script>

<style scoped lang="scss">
.l-results-drawer {
  $root: &;
}
</style>
