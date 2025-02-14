import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const LDatasetes = () => import('@/components/views/LDatasets.vue')
const LExperiments = () => import('@/components/views/LExperiments.vue')

export const routes: Array<RouteRecordRaw & { icon?: string }> = [
  {
    path: '/datasets',
    name: 'datasets',
    component: LDatasetes,
    icon: 'pi pi-dataset',
  },
  {
    path: '/experiments',
    name: 'experiments',
    component: LExperiments,
    icon: 'pi pi-experiments',
  },
  {
    path: '/:pathMatch(.*)*', // Catch-all route for undefined paths
    redirect: { name: 'datasets' }, // Redirect to the datasets route
  },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})
