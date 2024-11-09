<template>
	<div class="l-table">
		<DataTable :value="tableData" size="medium">
			<Column v-for="(column, idx) in columns" :key="idx" :field="column.field" :header="column.header" />
		</DataTable>
	</div>
</template>

<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

defineProps({
	columns: {
		type: Array,
		required: true,
		validator: (value) => {
			return value.every(item => 'field' in item && 'header' in item);
		}
	},
	tableData: {
		type: Array,
		required: true,
	}

})


</script>

<style scoped lang="scss">
	.l-table {
		width: 100%;
		display: flex;
		place-content: center;
	}
</style>