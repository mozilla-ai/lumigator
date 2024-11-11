<template>
  <div class="l-datasets">
    <div class="l-datasets__table-container">
      <l-dataset-table :table-data="datasets" />
    </div>
  </div>
</template>

<script setup>
import { onMounted} from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasets/store'
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

  &__table-container {
		padding: $l-spacing-1;
    display: grid;
  }
}
</style>
