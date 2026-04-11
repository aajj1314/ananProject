import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/devices',
      component: () => import('@/views/DeviceList.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/map/:deviceId',
      component: () => import('@/views/MapView.vue'),
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      component: () => import('@/views/AdminDashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false
  const requiresAdmin = to.meta.requiresAdmin

  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录，重定向到登录页
    next('/login')
  } else if (requiresAdmin && !authStore.isAdmin) {
    // 需要管理员权限但不是管理员，重定向到设备列表页
    next('/devices')
  } else {
    // 其他情况，正常导航
    next()
  }
})
