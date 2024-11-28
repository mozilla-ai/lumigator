<template>
  <Tabs
    value="0"
    class="l-experiment-tabs"
  >
    <TabList class="l-experiment-tabs__list">
      <Tab value="0">Experiment Details</Tab>
      <Tab value="1">Logs</Tab>
      <Button
        icon="pi pi-times"
        severity="secondary"
        rounded
        aria-label="Close"
        style="margin-left: auto;"
        class="l-experiment-form__close"
        @click="emit('l-close-details')"
      />
    </TabList>
    <TabPanels>
      <TabPanel value="0">
        <slot name="experiment-details" />
      </TabPanel>
      <TabPanel value="1">
        <slot name="logs" />
      </TabPanel>
    </TabPanels>
  </Tabs>
</template>

<script setup>
import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';
import Button from 'primevue/button';

const emit = defineEmits(['l-close-details']);



</script>

<style scoped lang="scss">
.l-experiment-tabs {
  $root: &;

  &__list {
    position: sticky; top: 0;z-index:100;
    padding-bottom: $l-spacing-1;
    //  style="position: sticky; top: 0;z-index:100"
  }
}
</style>
