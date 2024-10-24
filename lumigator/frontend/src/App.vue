<script setup>
 import LDatasets from './components/LDatasets.vue'
	import http from '@/services/http/index.js';


	const getDatasetDetails = async (id) => {
		const response = await http.get(`datasets/${id}`);
  	console.log(response.data);
	}
</script>
<template>
  <div>
    <h1 class="logo">🐊 Lumigator</h1>
		<l-datasets
			@dataset-selected="getDatasetDetails($event)"
		/>
  </div>
</template>

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
</style>
