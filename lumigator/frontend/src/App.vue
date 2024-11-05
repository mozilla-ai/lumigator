<template>
	<div id="app">
		<div class="header"></div>
		<div class="l-menu-container">
			<l-menu />
		</div>
		<div class="l-main-container">
			<router-view v-slot="{ Component }">
				<transition name="transition-fade">
					<component :is="Component" @s-disable-scroll="disableScroll = $event" />
				</transition>
			</router-view>
		</div>
	</div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import http from '@/services/http/index.js';
import LMenu from '@/components/LMenu.vue'

const datasets = ref([]);

const getDatasets = async () => {
  const response = await http.get('datasets/');
  console.log(response.data.items);
  datasets.value = response.data.items;
};

const getDatasetDetails = async (id) => {
	const response = await http.get(`datasets/${id}`);
	// this will fetch further information for the selected dataset
	// when endpoint is ready
  console.log(response.data);
};

const deleteDataset = async (id) => {
  try {
    const response = await http.delete(`datasets/${id}`);

    if (response.status === 200 || response.status === 204) {
      setTimeout(() => {
        getDatasets();
      }, 1000);
    } else {
      console.error("Unexpected response status: ", response.status);
    }
  } catch (error) {
    console.error("Error deleting dataset:", error);
  }
};

onMounted(() => {
  getDatasets();
});
</script>

<style scoped lang="scss">
// .logo {
//   height: 6em;
//   padding: 1.5em;
//   will-change: filter;
//   transition: filter 300ms;
//   cursor: default;
// }
// .logo:hover {
//   filter: drop-shadow(0 0 2em #646cffaa);
// }

#app {
	height: 100vh;
  padding: $l-spacing-1;
	margin: auto;
	background-color: $l-main-bg;
	display: grid;
	grid-template-columns: minmax(150px, 20%) 1fr;
	grid-template-rows: auto 1fr;
	max-width: $l-app-width;
	text-align: center;

	.header {
		// border: 2px solid red;
		background-color: $l-main-bg;
		grid-column: 1/-1;
		grid-row: 1;
	}

	.l-menu-container{
		background-color: $l-main-bg;
		// border: 2px solid blue;
		grid-row: 2;
	}

	.l-main-container {
		background-color: $l-card-bg;
		border-radius: $l-main-radius;
		grid-row: 2;
	}
}
</style>
