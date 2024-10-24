<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { ref, onMounted } from 'vue';
import http from '@/services/http/index.js';

const datasets = ref([]);

const emit = defineEmits(['dataset-selected'])

const formatDate = (dateString) => {
  const date = new Date(dateString);

  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // getMonth() returns 0-11
  const year = String(date.getFullYear()).slice(-2); // Get last two digits of year
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${day}/${month}/${year} - ${hours}:${minutes}`;
}

const onDatasetSelect = (id) => {
	emit('dataset-selected', id)
}

const getDatasets = async () => {
  const response = await http.get('datasets/');
  console.log(response.data.items);
  datasets.value = response.data.items;
};

onMounted(() => {
  getDatasets();
});
</script>

<template>
  <div class="l-datasets">
    <div class="l-datasets__list-container">
      <ul class="l-datasets__list">
        <li v-for="dataset in datasets" :key="dataset.id">
          <div
						class="l-datasets__list-card"
						@click="onDatasetSelect(dataset.id)"
					>
            <span> {{ formatDate(dataset.created_at) }}</span>
            <span>File name: {{ dataset.filename }}</span>
            <span>Ground truth: {{ dataset.ground_truth ? '✅ ' : ' ❌' }}</span>
            <span>Size: {{ dataset.size }}</span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped lang="scss">
.l-datasets {
  $root: &;

  &__list-container {
    display: grid;
  }

  &__list {
    display: flex;
		flex-direction: column;
    flex-wrap: wrap;
    list-style-type: none;
    &-card {
			cursor: pointer;
      margin: 1rem;
			padding: 1rem;
      box-shadow: 2px 4px 15px rgba(252, 228, 228, 0.401);
      border-radius: 12px;
      overflow: hidden;
      transition: all 0.2s linear;
      display: flex;
      flex-direction: column;
			max-width: 250px;

      &:hover {
        box-shadow: 2px 8px 45px rgba(0, 0, 0, 0.15);
        transform: translate3D(0, -2px, 0);
      }
    }
  }
}
</style>
