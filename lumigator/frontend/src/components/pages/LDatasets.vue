<template>
	<div class="l-datasets">
		<div class="l-datasets__list-container">
			<ul class="l-datasets__list" v-if="datasets.length">
				<li v-for="dataset in datasets" :key="dataset.id">
					<div class="l-datasets__list-card" @click="onDatasetSelect(dataset.id)">
						<span> {{ formatDate(dataset.created_at) }}</span>
						<span>File name: {{ dataset.filename }}</span>
						<span>Ground truth: {{ dataset.ground_truth ? '✅ ' : ' ❌' }}</span>
						<span>Size: {{ dataset.size }} kb</span>
					</div>
					<span class="l-datasets__list-remove" @click="onRemoveDataset(dataset.id)">🗑️</span>
				</li>
			</ul>
		</div>
	</div>
</template>
<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStrore } from '@/stores/datasets/store.js'

const emit = defineEmits(['dataset-selected', 'remove']);

const datasetStore = useDatasetStrore()
const { datasets } = storeToRefs(datasetStore);

const formatDate = (dateString) => {
  const date = new Date(dateString);
	console.log(dateString)
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = String(date.getFullYear()).slice(-2);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${day}/${month}/${year} - ${hours}:${minutes}`;
};

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
    display: grid;
  }

  &__list {
    display: flex;
    flex-wrap: wrap;
    list-style-type: none;
		padding: 1rem;

    li {
      display: flex;
		padding: 1rem;
      align-items: center;
    }

    &-card {
      cursor: pointer;
      margin: 1rem;
      padding: 1rem;
      box-shadow: 2px 8px 45px rgba(0, 0, 0, 0.15);
      border-radius: 12px;
      overflow: hidden;
      transition: all 0.2s linear;
      display: flex;
      flex-direction: column;
      width: 300px;

      &:hover {
        box-shadow: 2px 4px 15px rgba(252, 228, 228, 0.401);
        transform: translate3D(0, -2px, 0);
      }
    }
    &-remove {
      cursor: pointer;
    }
  }
}
</style>
