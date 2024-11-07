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
import LMenu from '@/components/organisms/LMenu.vue'

</script>

<style scoped lang="scss">
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
		background-color: $l-main-bg;
		grid-column: 1/-1;
		grid-row: 1;
	}

	.l-menu-container {
		background-color: $l-main-bg;
		grid-row: 2;
	}

	.l-main-container {
		background-color: $l-card-bg;
		border-radius: $l-main-radius;
		grid-row: 2;
		display: grid;
		place-items: center;
	}
}
</style>
