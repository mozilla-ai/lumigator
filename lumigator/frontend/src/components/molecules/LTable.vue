<template>
	<div class="l-table">
		<DataTable v-if="entityType === 'datasets'" :value="tableData" size="medium" tableStyle="min-width: 70rem">
			<Column field="filename" header="Filename" />
			<Column field="id" header="dataset id">
				<template #body="slotProps">
					{{ shortenedID(slotProps.data.id) }}
				</template>
			</Column>
			<Column field="created_at" header="submitted">
				<template #body="slotProps">
					{{ formatDate(slotProps.data.created_at) }}
				</template>
			</Column>
			<Column field="size" header="size">
				<template #body="slotProps">
					{{ Math.floor(slotProps.data.size / 1000) }} KB
				</template>
			</Column>
			<Column field="ground_truth" header="GroundTruth">
				<template #body="slotProps">
					<span v-text="slotProps.data.ground_truth" class="capitalize" />
				</template>
			</Column>
			<Column header="options">
				<template #body>
					<span class="pi pi-fw pi-ellipsis-h l-table__options-trigger" @click="togglePopover"
						aria-controls="optionsMenu" />
				</template>
			</Column>
		</DataTable>
		<Menu ref="optionsMenu" id="options_menu" :model="options" :popup="true"
			:pt="{ list: 'l-table__options-menu', itemLink: 'l-table__menu-option', itemIcon: 'l-table__menu-option-icon', separator: 'separator' }" />
	</div>
</template>

<script setup>
import { ref } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Menu from 'primevue/menu';


defineProps({
	tableData: {
		type: Array,
		required: true,
	},
	entityType: {
		type: String,
		required: false,
	}

})

const optionsMenu = ref()
const options = ref([
	{
		label: 'Use in Experiment',
		icon: 'pi pi-microchip',
	},
	{
		separator: true,
	},
	{
		label: 'View',
		icon: 'pi pi-external-link'
	},
	{
		label: 'Download',
		icon: 'pi pi-download'
	},
	{
		label: 'Delete',
		icon: 'pi pi-trash'
	},
])

const shortenedID = (id) =>
	id.length <= 20 ? id : `${id.slice(0, 20)}...`;

const formatDate = (dateString) => {
	const date = new Date(dateString);
	return new Intl.DateTimeFormat('en-GB', {
		day: '2-digit',
		month: 'short',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
		hour12: false,
	}).format(date).replace(/(\d{4})(\s)/, '$1,$2');
};

const togglePopover = (event) => {
	optionsMenu.value.toggle(event);
}

</script>

<style scoped lang="scss">
.l-table {
	$root: &;
	width: 100%;
	display: flex;
	place-content: center;

	&__options-trigger {
		padding: 0;
		margin-left: 20% !important;
	}

}
</style>

<style lang="scss">
.l-table__options-menu {
	padding: 0 $l-spacing-1;
}

.l-table__menu-option {
	color: $l-grey-100;
	padding: $l-spacing-1 $l-spacing-1 $l-spacing-1 0 $l-spacing-1;
	font-size: $l-menu-font-size;

	&:hover {
		color: white;
	}
}

.separator {
	padding: $l-spacing-1/2 0;
}

.l-table__options-menu> :first-child .l-table__menu-option {
	padding-bottom: 1rem;
	padding-top: 0rem;
}
</style>