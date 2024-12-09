import {
  createRouter,
  createWebHistory,
} from 'vue-router';

const LDatasetes = () => import('@/components/pages/LDatasets.vue')
const LExperiments = () => import('@/components/pages/LExperiments.vue')

export const routes = [
	{
		path: '/datasets',
		name: 'datasets',
		disabled: false,
		component: LDatasetes,
		icon: 'pi pi-dataset'
	},
	{
		path: '/experiments',
		name: 'experiments',
		disabled: false,
		component: LExperiments,
		icon: 'pi pi-experiments'
  },
  {
    path: '/:pathMatch(.*)*', // Catch-all route for undefined paths
    redirect: { name: 'datasets' } // Redirect to the datasets route
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});
export default router;
