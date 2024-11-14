<template>
  <div class="l-dataset-table">
    <transition name="transition-fade">

      <DataTable
        v-if="tableVisible"
        :value="tableData"
        :tableStyle="style"
        columnResizeMode="expand"
        scrollable
        :pt="{table:'table-root'}"
        @row-click="emit('l-dataset-selected', $event.data)"
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
          header="GroundTruth"
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
      <ConfirmDialog></ConfirmDialog>
    </Menu>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Menu from 'primevue/menu';
import ConfirmDialog from 'primevue/confirmdialog';
import { useConfirm } from "primevue/useconfirm";
import { useSlidePanel } from '@/composables/SlidingPanel';

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

const { showSlidingPanel  } = useSlidePanel();
const style = computed(() => {
  return showSlidingPanel.value ?
    'min-width: min(40vw, 1200px)' : 'min-width: min(80vw, 1200px)'
})

const emit = defineEmits(['l-delete-dataset', 'l-dataset-selected'])

const confirm = useConfirm();
const focusedDataset = ref(null);
const tableVisible = ref(true)
const optionsMenu = ref();
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
    icon: 'pi pi-trash',
    command: () => {
      deleteConfirmation()
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

const togglePopover = (event, dataset) => {
  focusedDataset.value = dataset;
	optionsMenu.value.toggle(event);
}

function deleteConfirmation() {
  confirm.require({
    message: `${focusedDataset.value.filename}`,
    header: 'Delete  dataset ?',
    icon: 'pi pi-info-circle',
    rejectLabel: 'Cancel',
    rejectProps: {
      label: 'Cancel',
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: 'Delete',
      severity: 'danger'
    },
    accept: () => {
      emit('l-delete-dataset', focusedDataset.value.id);
      focusedDataset.value = null;
    },
    reject: () => {
      focusedDataset.value = null;
    }
  });
}

watch(showSlidingPanel, () => {
  tableVisible.value = false;
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
// component is mounted
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
