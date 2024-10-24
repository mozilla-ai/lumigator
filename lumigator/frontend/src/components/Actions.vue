<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { onMounted } from 'vue';
import http from '@/services/http/index.js';
// const getDataset =

onMounted(async () => {
	const response = await http.get('datasets/');
	console.log(response.data)
})


</script>

<template>
  <div>
		this Actions
	</div>
</template>
