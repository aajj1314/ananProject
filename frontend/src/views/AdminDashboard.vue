<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { apiClient } from '@/api/api'
import { useAuthStore } from '@/stores/auth'

interface Stats {
  users: { total: number }
  devices: { total: number }
  alarms: { total: number }
  notifications: { total: number }
  metrics: Record<string, unknown>
}

interface UserItem {
  id: number
  phone: string
  nickname: string
  role: 'user' | 'admin'
  created_at: string
}

const router = useRouter()
const authStore = useAuthStore()

const stats = ref<Stats | null>(null)
const users = ref<UserItem[]>([])
const loading = ref(true)
const errorText = ref('')

const loadData = async () => {
  loading.value = true
  errorText.value = ''
  try {
    const [statsResponse, usersResponse] = await Promise.all([
      apiClient.get('/admin/stats'),
      apiClient.get('/admin/users', { params: { limit: 10 } }),
    ])
    stats.value = statsResponse.data.data
    users.value = usersResponse.data.data.items
  } catch (error) {
    errorText.value = '数据加载失败，请确认您有管理员权限'
  } finally {
    loading.value = false
  }
}

const updateUserRole = async (user: UserItem, newRole: 'user' | 'admin') => {
  try {
    await apiClient.put(`/admin/users/${user.id}/role?role=${newRole}`)
    user.role = newRole
  } catch (error) {
    errorText.value = '角色更新失败'
  }
}

onMounted(() => {
  if (!authStore.isAdmin) {
    router.push('/devices')
    return
  }
  loadData()
})
</script>

<template>
  <main class="shell">
    <section class="panel" style="padding: 28px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <p class="muted">Admin Panel</p>
          <h1 class="hero-title" style="font-size: clamp(2rem, 5vw, 3.5rem);">平台管理仪表板</h1>
        </div>
        <button class="button-primary" type="button" @click="loadData" :disabled="loading">
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
      </div>
    </section>

    <p v-if="errorText" style="color:#8f1f1f;margin-top:20px;">{{ errorText }}</p>

    <section v-if="stats" class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-top: 20px;">
      <div class="panel" style="padding: 24px;">
        <p class="muted">用户总数</p>
        <h2 style="margin:0;font-size:2.8rem;">{{ stats.users.total }}</h2>
      </div>
      <div class="panel" style="padding: 24px;">
        <p class="muted">设备总数</p>
        <h2 style="margin:0;font-size:2.8rem;">{{ stats.devices.total }}</h2>
      </div>
      <div class="panel" style="padding: 24px;">
        <p class="muted">报警总数</p>
        <h2 style="margin:0;font-size:2.8rem;">{{ stats.alarms.total }}</h2>
      </div>
      <div class="panel" style="padding: 24px;">
        <p class="muted">通知总数</p>
        <h2 style="margin:0;font-size:2.8rem;">{{ stats.notifications.total }}</h2>
      </div>
    </section>

    <section v-if="users.length" class="panel" style="padding: 24px; margin-top: 20px;">
      <h2 style="margin-top:0;">最近注册用户</h2>
      <table style="width:100%;border-collapse:collapse;margin-top:16px;">
        <thead>
          <tr style="border-bottom:1px solid var(--line);">
            <th style="text-align:left;padding:12px 0;" class="muted">ID</th>
            <th style="text-align:left;padding:12px 0;" class="muted">手机号</th>
            <th style="text-align:left;padding:12px 0;" class="muted">昵称</th>
            <th style="text-align:left;padding:12px 0;" class="muted">角色</th>
            <th style="text-align:left;padding:12px 0;" class="muted">注册时间</th>
            <th style="text-align:left;padding:12px 0;" class="muted">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" style="border-bottom:1px solid var(--line);">
            <td style="padding:12px 0;">{{ user.id }}</td>
            <td style="padding:12px 0;">{{ user.phone }}</td>
            <td style="padding:12px 0;">{{ user.nickname }}</td>
            <td style="padding:12px 0;">
              <span :style="{ color: user.role === 'admin' ? '#b6542b' : 'inherit' }">
                {{ user.role === 'admin' ? '管理员' : '普通用户' }}
              </span>
            </td>
            <td style="padding:12px 0;">{{ user.created_at }}</td>
            <td style="padding:12px 0;">
              <button
                v-if="user.role === 'user'"
                class="button-primary"
                type="button"
                style="padding:0.5rem 0.8rem;font-size:0.9rem;"
                @click="updateUserRole(user, 'admin')"
              >
                设为管理员
              </button>
              <button
                v-else
                class="button-primary"
                type="button"
                style="padding:0.5rem 0.8rem;font-size:0.9rem;background:linear-gradient(135deg,#33514b,#1d2f2a);"
                @click="updateUserRole(user, 'user')"
              >
                取消管理员
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>
