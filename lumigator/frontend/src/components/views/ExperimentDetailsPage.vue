<template>
  <div class="experiment-details-page">
    <div class="breadcrumbs">
      <i class="pi pi-arrow-left back-button" @click="handleBackButtonClicked"></i>
      <Breadcrumb :model="items">
        <template #separator>
          /
        </template>
      </Breadcrumb>
    </div>

    <Tabs value="model-runs">
        <div class="experiment-container">
      <div class="experiment-details-header">
        <h3 class="experiment-title"> <i class="pi pi-experiments"></i>{{ experiment?.name }}</h3>
        <TabList>
          <Tab value="model-runs">Model Runs</Tab>
          <Tab value="add-model-run">Trigger Model Run</Tab>
          <Tab value="details">Details</Tab>
        </TabList>
      </div>
      <div class="experiment-details-tab-content">
        <TabPanels>
          <TabPanel value="model-runs">
            <p>Model Runs</p>
          </TabPanel>
          <TabPanel value="add-model-run">
            <p>Trigger Model Run</p>
          </TabPanel>
          <TabPanel value="details">
            <p>Details</p>
          </TabPanel>
        </TabPanels>

      </div>
    </div>
      </Tabs>
  </div>
</template>

<script setup lang="ts">
import { useExperimentStore } from '@/stores/experimentsStore';
import { storeToRefs } from 'pinia';
import Breadcrumb from 'primevue/breadcrumb'
import {type MenuItem } from 'primevue/menuitem';
import { computed, ref, type ComputedRef, type Ref } from 'vue'
import { useRouter } from 'vue-router';
import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';

const { id } = defineProps<{
  id: string
}>()
const router = useRouter()
const experimentsStore = useExperimentStore()
const {experiments} = storeToRefs(experimentsStore)
const experiment = computed(() => experiments.value.find((exp) => exp.id === id))

const items: ComputedRef<MenuItem[]> = computed(() =>([
  {
    label: 'Experiments',
    command: (e) => {
      e.originalEvent.preventDefault()
      router.push('/experiments')
    },
    items: [],
    key: 'experiments'
  },
  {
    label: experiment.value?.name,
    command: (e) => {
      e.originalEvent.preventDefault()
      router.push(`/experiments/${id}`)
    },
    key: 'experiment-details'
  }
]))

const handleBackButtonClicked = () => {
  history.back();
}
</script>

<style scoped lang="scss">
@use "@/styles/mixins";

/* reset global css from _resetcss.scss */
:deep(a,li) {
  background-color: unset;
}

.back-button {
  cursor: pointer;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--l-grey-200);

  @include mixins.caption;
}

.experiment-details-page {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  text-align: left;
  padding: 0 1.88rem;
}

.experiment-title {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--l-grey-100);
  @include mixins.heading-2;
}

.experiment-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.experiment-details-header {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.experiment-details-tab-content {

}
</style>
