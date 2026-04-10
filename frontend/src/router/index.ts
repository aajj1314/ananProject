import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/devices',
    },
    {
      path: '/login',
      component: () => import('@/views/Login.vue'),
    },
    {
      path: '/devices',
      component: () => import('@/views/DeviceList.vue'),
    },
    {
      path: '/map/:deviceId',
      component: () => import('@/views/MapView.vue'),
      props: true,
    },
    {
      path: '/admin',
      component: () => import('@/views/AdminDashboard.vue'),
      meta: { requiresAdmin: true },
    },
  ],
})
