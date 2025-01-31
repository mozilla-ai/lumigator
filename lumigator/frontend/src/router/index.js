/**
 * This file sets up the Vue Router for the Lumigator frontend application.
 * It defines the routes and their respective components, as well as the router configuration.
 */

import {
  createRouter,
  createWebHistory,
} from 'vue-router';


/**
 * Lazy-loaded components for each route page.
 * @returns {Promise} A promise that resolves to the Datasets component.
 */
const LDatasetes = () => import('@/components/pages/LDatasets.vue')
const LExperiments = () => import('@/components/pages/LExperiments.vue')


/**
 * Array of route objects for the application.
 * @type {Array<Object>}
 * @property {string} path - The URL path for the route.
 * @property {string} name - The name of the route.
 * @property {boolean} disabled - Whether the route is disabled.
 * @property {Function} component - The component to be rendered for the route.
 * @property {string} icon - The icon associated with the route.
 */
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

/**
 * Creates and configures the Vue Router instance.
 * @returns {Router} The configured Vue Router instance.
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  /**
   * Scroll behavior function for the router.
   * @param {Route} to - The target Route Object being navigated to.
   * @param {Route} from - The current route being navigated away from.
   * @param {Object} savedPosition - The saved scroll position, if any.
   * @returns {Object} The scroll position to move to.
   */
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

export default router;
