
<template>
  <div>
    <h1 class="logo">🐊 Lumigator</h1>
    <div class="l-main">
      <div class="upload-container">
        <l-upload @dataset-upload="getDatasets()" />
      </div>
      <l-datasets
        :datasets="datasets"
        @dataset-selected="getDatasetDetails($event)"
        @dataset-remove="deleteDataset($event)"
      />
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import LDatasets from './components/LDatasets.vue';
import LUpload from './components/LUpload.vue';
import http from '@/services/http/index.js';

const datasets = ref([]);

const getDatasets = async () => {
  const response = await http.get('datasets/');
  console.log(response.data.items);
  datasets.value = response.data.items;
};

const getDatasetDetails = async (id) => {
  const response = await http.get(`datasets/${id}`);
  console.log(response.data);
};

const deleteDataset = async (id) => {
  console.log(id);
  const response = await http.delete(`datasets/${id}`);
  console.log(response.data);
  setTimeout(() => {
    getDatasets();
  }, 1000);
};

onMounted(() => {
  getDatasets();
});
</script>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
  cursor: default;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.l-main {
  padding: 3rem;
  display: grid;
  grid-template-columns: minmax(150px, 25%) 1fr;
}
</style>
