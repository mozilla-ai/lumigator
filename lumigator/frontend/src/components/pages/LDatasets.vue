<template>
  <div
    class="l-datasets"
    :class="{'is-empty': datasets.length === 0 || !datasets}"
  >
    <div
      v-if="datasets.length > 0"
      class="l-datasets__header-container"
    >
      <l-page-header
        title="Datasets"
        :description="headerDescription"
        subtitle="Only CSV files are currently supported."
        button-label="Provide Dataset"
        @l-header-action="onDatasetAdded()"
      />
    </div>
    <l-dataset-empty
      v-else
      @l-add-dataset="onDatasetAdded()"
    />
    <div
      v-if="datasets.length > 0"
      class="l-datasets__table-container"
    >
      <l-dataset-table
        :table-data="datasets"
        @l-dataset-selected="onDatasetSelected($event)"
        @l-experiment="onExperimentDataset($event)"
        @l-delete-dataset="deleteConfirmation($event)"
      />
    </div>
    <l-file-upload
      ref="datasetInput"
      entity="dataset"
      @l-file-upload="onDatasetUpload($event)"
    />
    <Teleport
      to=".sliding-panel"
    >
      <l-dataset-details
        v-if="selectedDataset"
        @l-experiment="onExperimentDataset($event)"
        @l-details-closed="onClearSelection()"
        @l-delete-dataset="deleteConfirmation($event)"
        @l-download-dataset="onDownloadDataset()"
      />
    </Teleport>
  </div>
</template>

<script setup>
import { onMounted, ref} from 'vue'
import { storeToRefs } from 'pinia'
import { useDatasetStore } from '@/stores/datasets/store'
import { useSlidePanel } from '@/composables/SlidingPanel';
import { useRouter, useRoute } from 'vue-router';
import LPageHeader from '@/components/molecules/LPageHeader.vue';
import LDatasetTable from '@/components/molecules/LDatasetTable.vue';
import LFileUpload from '@/components/molecules/LFileUpload.vue';
import LDatasetEmpty from '@/components/molecules/LDatasetEmpty.vue';
import LDatasetDetails from '@/components/organisms/LDatasetDetails.vue';
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import datasetsService from "@/services/datasets/datasetsService.js";
import {downloadContent} from "@/helpers/index.js";

const datasetStore = useDatasetStore();
const { datasets, selectedDataset } = storeToRefs(datasetStore);
const { showSlidingPanel  } = useSlidePanel();
const toast = useToast();
const datasetInput = ref(null);
const confirm = useConfirm();
const router = useRouter();
const route = useRoute();

const headerDescription = ref(`Use a dataset as the basis for your evaluation.
It includes data for the model you'd like to evaluate and possibly a ground truth "answer".`)

function deleteConfirmation(dataset) {
  confirm.require({
    message: `${dataset.filename}`,
    header: 'Delete  dataset?',
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
      onDeleteDataset(dataset.id)
      if (!selectedDataset.value && showSlidingPanel.value) {
        showSlidingPanel.value = false
      }
      toast.add({
        severity: 'secondary',
        summary: `Dataset removed`,
        messageicon: 'pi pi-trash',
        detail: `${dataset.filename}`,
        group: 'br',
        life: 3000
      })
    },
    reject: () => {}
  });
}

function onDownloadDataset() {
  datasetStore.loadDatasetFile();
}

const onDatasetAdded = () => { datasetInput.value.input.click() }

const onDatasetUpload = (datasetFile) => {
  datasetStore.uploadDataset(datasetFile);
}

const onDeleteDataset = (datasetID) => {
  datasetStore.deleteDataset(datasetID);
}

const onDatasetSelected = (dataset) => {
  datasetStore.loadDatasetInfo(dataset.id);
  showSlidingPanel.value = true;
}

const onClearSelection = () => {
  datasetStore.resetSelection();
}

const onExperimentDataset = (dataset) => {
  router.push('experiments')
  selectedDataset.value = dataset;
  datasetStore.loadDatasetInfo(dataset.id);
}

onMounted(async () => {
  if (route.query.dataset) {
    const selection = datasets.value.filter((dataset) => dataset.id === route.query.dataset)[0];
    onDatasetSelected(selection);
  }
})

</script>

<style scoped lang="scss">
.l-datasets {
  $root: &;
  max-width: $l-main-width;
  margin: 0 auto;

  &__header-container {
    padding: $l-spacing-1;
    display: grid;
    place-items: center;
    width: 100%;
  }

  &__table-container {
		padding: $l-spacing-1;
    display: grid;
    width: 100%;
  }
}

.is-empty {
  display: grid;
  place-content: center;
}
</style>
