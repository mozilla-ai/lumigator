<template>
  <div class="l-dataset-table">
    <transition
      name="transition-fade"
      mode="out-in"
    >
      <DataTable
        v-if="tableVisible"
        v-model:selection="focusedItem"
        selectionMode="single"
        dataKey="id"
        :value="tableData"
        :tableStyle="style"
        columnResizeMode="expand"
        scrollable
        :pt="{table:'table-root'}"
        @row-click="emit('l-dataset-selected', $event.data)"
        @row-unselect="showSlidingPanel = false"
      >
        <Column
          field="filename"
          header="Filename"
        />
        <Column
          field="id"
          header="dataset id"
        >
          <template #body="slotProps">
            {{ shortenedID(slotProps.data.id) }}
          </template>
        </Column>
        <Column
          field="created_at"
          header="submitted"
        >
          <template #body="slotProps">
            {{ formatDate(slotProps.data.created_at) }}
          </template>
        </Column>
        <Column
          field="size"
          header="size"
        >
          <template #body="slotProps">
            {{ Math.floor(slotProps.data.size / 1000) }} KB
          </template>
        </Column>
        <Column
          field="ground_truth"
          header="Ground Truth"
        >
          <template #body="slotProps">
            <span class="capitalize"
                  v-text="slotProps.data.ground_truth"
            />
          </template>
        </Column>
        <Column header="options">
          <template #body="slotProps">
            <span class="pi pi-fw pi-ellipsis-h l-dataset-table__options-trigger"
                  aria-controls="optionsMenu"
                  @click.stop="togglePopover($event, slotProps.data)"
            />
          </template>
        </Column>
      </DataTable>
    </transition>

    <Menu
      id="options_menu"
      ref="optionsMenu"
      :model="options"
      :popup="true"
      :pt="ptConfigOptionsMenu"
    >
    </Menu>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Menu from 'primevue/menu';
import { useSlidePanel } from '@/composables/SlidingPanel';
import { formatDate } from '@/helpers/index'

defineProps({
	tableData: {
		type: Array,
		required: true,
	}
})

const emit = defineEmits(['l-delete-dataset', 'l-dataset-selected', 'l-experiment'])

const { showSlidingPanel  } = useSlidePanel();
const style = computed(() => {
  return showSlidingPanel.value ?
    'min-width: 40vw' : 'min-width: min(80vw, 1200px)'
})

const focusedItem = ref(null);
const tableVisible = ref(true)
const optionsMenu = ref();
const options = ref([
	{
		label: 'Use in Experiment',
    icon: 'pi pi-microchip',
    disabled: false,
     command: () => {
      emit('l-experiment', focusedItem.value)
    }
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
    icon: 'pi pi-trash',
    command: () => {
      emit('l-delete-dataset', focusedItem.value)
    }
	},
])

const ptConfigOptionsMenu = ref({
  list: 'l-dataset-table__options-menu',
  itemLink: 'l-dataset-table__menu-option',
  itemIcon: 'l-dataset-table__menu-option-icon',
  separator: 'separator'
});

const shortenedID = (id) =>
	id.length <= 20 ? id : `${id.slice(0, 20)}...`;


const togglePopover = (event, dataset) => {
  focusedItem.value = dataset;
  const experimentOption = options.value.find(option => option.label === 'Use in Experiment');
  if (experimentOption) {
    experimentOption.disabled = !dataset.ground_truth;
  }
	optionsMenu.value.toggle(event);
}

watch(showSlidingPanel, (newValue) => {
  tableVisible.value = false;
  focusedItem.value = newValue ? focusedItem.value : null;
  setTimeout(() => {
    tableVisible.value = true;
  }, 100);
});

</script>

<style scoped lang="scss">
.l-dataset-table {
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
//  In order to have effect the following
// css rules must not be "scoped" because
// the popup-menu is attached to the DOM after the
// parent component is mounted
.l-dataset-table__options-menu {
	padding: 0 $l-spacing-1;
}

.l-dataset-table__menu-option {
	color: $l-grey-100;
	padding: $l-spacing-1 $l-spacing-1 $l-spacing-1 0 $l-spacing-1;
	font-size: $l-menu-font-size;

	&:hover {
		color: white;
    text-shadow: 0 0 1px white;
	}
}

.separator {
	padding: $l-spacing-1/2 0;
}

.l-dataset-table__options-menu> :first-child .l-dataset-table__menu-option {
	padding-bottom: 1rem;
	padding-top: 0rem;
}
</style>
