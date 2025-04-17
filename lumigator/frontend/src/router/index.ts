import LDatasets from '@/components/views/LDatasets.vue'
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

export const routes: Array<RouteRecordRaw> = [
  {
    path: '/datasets',
    name: 'datasets',
    component: LDatasets,
  },
  {
    path: '/experiments',
    name: 'experiments',
    component: () => import('@/components/views/LExperiments.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/components/views/SettingsPage.vue'),
  },
  {
    path: '/experiments/:id',
    name: 'ExperimentDetails',
    props: true,
    component: () => import('@/components/views/ExperimentDetailsPage.vue'),
    children: [],
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
