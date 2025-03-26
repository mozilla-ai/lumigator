<template>
   <TableView :columns="columns" :data="workflows" :columnStyles="columnStyles" @row-clicked="onWorkflowSelected"
   :is-search-enabled="false"
   :has-column-toggle="false"
   >
    </TableView>
</template>

<script setup lang="ts">
import type { Workflow } from '@/types/Workflow';
import LJobsTable from '../experiments/LJobsTable.vue';
import type { Experiment } from '@/types/Experiment';
import { computed } from 'vue';
import { useSlidePanel } from '@/composables/useSlidePanel';
import TableView from '../common/TableView.vue';

const onWorkflowSelected = (workflow: any) => {
    console.log('workflow selected', workflow);

};

const columns = ['model' ,'name', 'status', 'options'];
const { showSlidingPanel } = useSlidePanel();
const columnStyles = computed(() => {
  return {
    // expander: 'width: 4rem',
    // name: showSlidingPanel.value ? 'width: 20rem' : 'width: 26rem',
    // created: 'width: 12rem',
    // status: 'width: 12rem',
    // useCase: 'width: 8rem',
  }
})
const props = defineProps<{
  workflows: Workflow[];
  experiment: Experiment
}>();

</script>

<style scoped></style>
