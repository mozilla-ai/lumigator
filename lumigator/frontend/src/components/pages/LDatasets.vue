<template>
  <div
    class="l-datasets"
    :class="{'is-empty': datasets.length === 0 || !datasets}"
  >
    <div
      v-if="datasets.length > 0"
      class="l-datasets__header-container"
    >
      <l-page-header
        title="Datasets"
        subtitle="Excepteur sint  occaecat cupidatat non proident, sunt in culpa qui iest."
        button-label="Provide Dataset"
        @l-header-action="onDatasetAdded()"
      />
    </div>
    <l-dataset-empty
      v-else
      @l-add-dataset="onDatasetAdded()"
    />
    <div
      v-if="datasets.length > 0"
      class="l-datasets__table-container"
    >
      <l-dataset-table
        :table-data="datasets"
        @l-delete-dataset="onDeleteDataset($event)"
      />
    </div>
    <l-file-upload
      ref="datasetInput"
      entity="dataset"
      @l-file-upload="onDatasetUpload($event)"
    />
  </div>
</template>

<script setup>
import { onMounted, ref} from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasets/store'
import LPageHeader from '@/components/molecules/LPageHeader.vue';
import LDatasetTable from '@/components/molecules/LDatasetTable.vue';
import LFileUpload from '@/components/molecules/LFileUpload.vue';
import LDatasetEmpty from '@/components/molecules/LDatasetEmpty.vue';

const datasetStore = useDatasetStore()
const { datasets } = storeToRefs(datasetStore);
const datasetInput = ref(null);

const onDatasetAdded = () => { datasetInput.value.input.click() }

const onDatasetUpload = (datasetFile) => {
  datasetStore.uploadDataset(datasetFile);
}

const onDeleteDataset = (datasetID) => {
  datasetStore.deleteDataset(datasetID);
}

onMounted(async () => {
	await datasetStore.loadDatasets()
})
</script>

<style scoped lang="scss">
.l-datasets {
  $root: &;
  max-width: $l-main-width;
  margin: 0 auto;

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

.is-empty {
  display: grid;
  place-items: center;
}
</style>