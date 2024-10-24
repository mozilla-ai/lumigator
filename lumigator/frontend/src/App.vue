<script setup>
	import Actions from './components/Actions.vue'
</script>
<template>
  <div>
    <h1 class="logo">🐊 Lumigator</h1>
		<Actions />
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
