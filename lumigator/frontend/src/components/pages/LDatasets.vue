<template>
  <div class="l-datasets">
    <div class="l-datasets__header-container">
      <l-page-header
        title="Datasets"
        subtitle="Excepteur sint  occaecat cupidatat non proident, sunt in culpa qui iest."
        button-label="Provide Dataset"
      />
    </div>
    <div
      v-if="true"
      class="l-datasets__table-container"
    >
      <l-dataset-table :table-data="datasets" />
    </div>
  </div>
</template>

<script setup>
import { onMounted} from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasets/store'
import LPageHeader from '@/components/molecules/LPageHeader.vue';
import LDatasetTable from '@/components/molecules/LDatasetTable.vue';

const datasetStore = useDatasetStore()
const { datasets } = storeToRefs(datasetStore);


onMounted(async () => {
	await datasetStore.loadDatasets()
})
</script>

<style scoped lang="scss">
.l-datasets {
  $root: &;
  max-width: $l-main-width;

  &__header-container {
    padding: $l-spacing-1;
    display: grid;
    place-items: center;
    width: 100%;
  }

  &__table-container {
		padding: $l-spacing-1;
    display: grid;
    width: 100%;
  }
}
</style>
