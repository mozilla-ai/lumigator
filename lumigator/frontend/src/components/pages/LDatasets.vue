<template>
	<div class="l-datasets">
		<div class="l-datasets__list-container">
			<l-table :columns="datasetColumns" :table-data="datasets" entity-type="datasets" />
		</div>
	</div>
</template>
<script setup>
import { onMounted} from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStrore } from '@/stores/datasets/store'
import LTable from '@/components/molecules/LTable.vue';

const emit = defineEmits(['dataset-selected', 'remove']);

const datasetStore = useDatasetStrore()
const { datasets } = storeToRefs(datasetStore);

const onDatasetSelect = (id) => {
  emit('dataset-selected', id);
};

const onRemoveDataset = (id) => {
  emit('dataset-remove', id);
};

onMounted(async () => {
	await datasetStore.loadDatasets()
})
</script>

<style scoped lang="scss">
.l-datasets {
  $root: &;

  &__list-container {
		padding: $l-spacing-1;
    display: grid;
  }
}
</style>
