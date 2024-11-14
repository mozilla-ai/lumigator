import {
  createRouter,
  createWebHistory,
} from 'vue-router';

const LDatasetes = () => import('@/components/pages/LDatasets.vue')
const LExperiments = () => import('@/components/pages/LExperiments.vue')

export const routes = [
	{
		path: '/',
		name: 'datasets',
		disabled: false,
		component: LDatasetes,
		icon: 'pi pi-fw pi-database'
	},
	{
		path: '/experiments',
		name: 'experiments',
		disabled: false,
		component: LExperiments,
		icon: 'pi pi-fw pi-database'
	}
]

const router = createRouter({
  routes,
  history: createWebHistory(import.meta.env.BASE_URL),
});
export default router;
