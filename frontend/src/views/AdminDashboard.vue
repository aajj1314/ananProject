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

interface DeviceItem {
  device_id: string
  device_name: string
  user_id: number
  battery: number
  last_updated: string | null
}

interface AlarmItem {
  id: number
  device_id: string
  alarm_type: number
  message: string
  timestamp: string
}

const router = useRouter()
const authStore = useAuthStore()

const stats = ref<Stats | null>(null)
const users = ref<UserItem[]>([])
const devices = ref<DeviceItem[]>([])
const alarms = ref<AlarmItem[]>([])
const loading = ref(true)
const errorText = ref('')
const successText = ref('')
const activeTab = ref('users')

const loadData = async () => {
  loading.value = true
  errorText.value = ''
  successText.value = ''
  try {
    const [statsResponse, usersResponse, devicesResponse, alarmsResponse] = await Promise.all([
      apiClient.get('/admin/stats'),
      apiClient.get('/admin/users', { params: { limit: 20 } }),
      apiClient.get('/admin/devices'),
      apiClient.get('/admin/alarms', { params: { limit: 20 } }),
    ])
    stats.value = statsResponse.data.data
    users.value = usersResponse.data.data.items
    devices.value = devicesResponse.data.data
    alarms.value = alarmsResponse.data.data
  } catch (error: any) {
    errorText.value = error.message || '数据加载失败，请确认您有管理员权限'
  } finally {
    loading.value = false
  }
}

const updateUserRole = async (user: UserItem, newRole: 'user' | 'admin') => {
  try {
    await apiClient.put(`/admin/users/${user.id}/role?role=${newRole}`)
    user.role = newRole
    successText.value = `用户 ${user.nickname} 已${newRole === 'admin' ? '设为' : '取消'}管理员`
  } catch (error: any) {
    errorText.value = error.message || '角色更新失败'
  }
}

const deleteUser = async (user: UserItem) => {
  if (user.id === authStore.user?.id) {
    errorText.value = '不能删除自己的账号'
    return
  }
  
  const confirmed = window.confirm(`确认删除用户 ${user.nickname} 吗？`)
  if (!confirmed) {
    return
  }
  
  try {
    await apiClient.delete(`/admin/users/${user.id}`)
    users.value = users.value.filter(u => u.id !== user.id)
    successText.value = `用户 ${user.nickname} 已删除`
  } catch (error: any) {
    errorText.value = error.message || '用户删除失败'
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
    <header class="flex justify-between items-center mb-6">
      <div>
        <h1 class="hero-title">管理员仪表板</h1>
        <p class="muted">平台管理与监控中心</p>
      </div>
      <div class="flex gap-4">
        <button 
          class="button-primary" 
          type="button" 
          @click="loadData" 
          :disabled="loading"
        >
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
        <router-link class="button-secondary" to="/devices">
          返回设备管理
        </router-link>
      </div>
    </header>

    <div v-if="errorText" class="alert alert-danger mb-4">
      {{ errorText }}
    </div>
    
    <div v-if="successText" class="alert alert-success mb-4">
      {{ successText }}
    </div>

    <section v-if="stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-muted">用户总数</p>
            <h2 class="text-3xl font-bold">{{ stats.users.total }}</h2>
          </div>
          <div class="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-white">
            <span>👥</span>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-muted">设备总数</p>
            <h2 class="text-3xl font-bold">{{ stats.devices.total }}</h2>
          </div>
          <div class="w-12 h-12 rounded-full bg-info flex items-center justify-center text-white">
            <span>📱</span>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-muted">报警总数</p>
            <h2 class="text-3xl font-bold">{{ stats.alarms.total }}</h2>
          </div>
          <div class="w-12 h-12 rounded-full bg-danger flex items-center justify-center text-white">
            <span>🔔</span>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-muted">通知总数</p>
            <h2 class="text-3xl font-bold">{{ stats.notifications.total }}</h2>
          </div>
          <div class="w-12 h-12 rounded-full bg-success flex items-center justify-center text-white">
            <span>📢</span>
          </div>
        </div>
      </div>
    </section>

    <div class="card mb-6">
      <div class="flex border-b">
        <button 
          class="px-4 py-2 font-medium" 
          :class="{ 'border-b-2 border-accent text-accent': activeTab === 'users' }"
          @click="activeTab = 'users'"
        >
          用户管理
        </button>
        <button 
          class="px-4 py-2 font-medium" 
          :class="{ 'border-b-2 border-accent text-accent': activeTab === 'devices' }"
          @click="activeTab = 'devices'"
        >
          设备管理
        </button>
        <button 
          class="px-4 py-2 font-medium" 
          :class="{ 'border-b-2 border-accent text-accent': activeTab === 'alarms' }"
          @click="activeTab = 'alarms'"
        >
          报警记录
        </button>
      </div>
      
      <div class="p-4">
        <!-- 用户管理 -->
        <div v-if="activeTab === 'users'">
          <h3 class="text-lg font-semibold mb-4">用户列表</h3>
          
          <div v-if="loading" class="text-center py-8">
            <div class="flex justify-center">
              <svg class="animate-spin h-8 w-8 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p class="mt-2">加载中...</p>
          </div>
          
          <div v-else-if="users.length === 0" class="text-center py-8">
            <p class="text-muted">暂无用户</p>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="w-full border-collapse">
              <thead>
                <tr class="border-b">
                  <th class="text-left py-3 px-4 text-muted">ID</th>
                  <th class="text-left py-3 px-4 text-muted">手机号</th>
                  <th class="text-left py-3 px-4 text-muted">昵称</th>
                  <th class="text-left py-3 px-4 text-muted">角色</th>
                  <th class="text-left py-3 px-4 text-muted">注册时间</th>
                  <th class="text-left py-3 px-4 text-muted">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id" class="border-b hover:bg-gray-50">
                  <td class="py-3 px-4">{{ user.id }}</td>
                  <td class="py-3 px-4">{{ user.phone }}</td>
                  <td class="py-3 px-4">{{ user.nickname }}</td>
                  <td class="py-3 px-4">
                    <span :class="{
                      'px-2 py-1 rounded-full bg-danger text-white text-xs': user.role === 'admin',
                      'px-2 py-1 rounded-full bg-gray-200 text-gray-800 text-xs': user.role === 'user'
                    }">
                      {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                    </span>
                  </td>
                  <td class="py-3 px-4">{{ user.created_at }}</td>
                  <td class="py-3 px-4">
                    <div class="flex gap-2">
                      <button
                        v-if="user.role === 'user'"
                        class="button-primary text-sm px-3 py-1"
                        type="button"
                        @click="updateUserRole(user, 'admin')"
                      >
                        设为管理员
                      </button>
                      <button
                        v-else
                        class="button-secondary text-sm px-3 py-1"
                        type="button"
                        @click="updateUserRole(user, 'user')"
                      >
                        取消管理员
                      </button>
                      <button
                        class="button-danger text-sm px-3 py-1"
                        type="button"
                        @click="deleteUser(user)"
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- 设备管理 -->
        <div v-if="activeTab === 'devices'">
          <h3 class="text-lg font-semibold mb-4">设备列表</h3>
          
          <div v-if="loading" class="text-center py-8">
            <div class="flex justify-center">
              <svg class="animate-spin h-8 w-8 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p class="mt-2">加载中...</p>
          </div>
          
          <div v-else-if="devices.length === 0" class="text-center py-8">
            <p class="text-muted">暂无设备</p>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="w-full border-collapse">
              <thead>
                <tr class="border-b">
                  <th class="text-left py-3 px-4 text-muted">设备ID</th>
                  <th class="text-left py-3 px-4 text-muted">设备名称</th>
                  <th class="text-left py-3 px-4 text-muted">用户ID</th>
                  <th class="text-left py-3 px-4 text-muted">电量</th>
                  <th class="text-left py-3 px-4 text-muted">最后上报</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="device in devices" :key="device.device_id" class="border-b hover:bg-gray-50">
                  <td class="py-3 px-4">{{ device.device_id }}</td>
                  <td class="py-3 px-4">{{ device.device_name }}</td>
                  <td class="py-3 px-4">{{ device.user_id }}</td>
                  <td class="py-3 px-4">
                    <div class="flex items-center">
                      <div class="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          class="h-2 rounded-full" 
                          :class="{
                            'bg-success': device.battery > 30,
                            'bg-warning': device.battery <= 30 && device.battery > 10,
                            'bg-danger': device.battery <= 10
                          }"
                          :style="{ width: `${device.battery}%` }"
                        ></div>
                      </div>
                      <span>{{ device.battery }}%</span>
                    </div>
                  </td>
                  <td class="py-3 px-4">{{ device.last_updated || '暂无数据' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- 报警记录 -->
        <div v-if="activeTab === 'alarms'">
          <h3 class="text-lg font-semibold mb-4">报警记录</h3>
          
          <div v-if="loading" class="text-center py-8">
            <div class="flex justify-center">
              <svg class="animate-spin h-8 w-8 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p class="mt-2">加载中...</p>
          </div>
          
          <div v-else-if="alarms.length === 0" class="text-center py-8">
            <p class="text-muted">暂无报警记录</p>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="w-full border-collapse">
              <thead>
                <tr class="border-b">
                  <th class="text-left py-3 px-4 text-muted">ID</th>
                  <th class="text-left py-3 px-4 text-muted">设备ID</th>
                  <th class="text-left py-3 px-4 text-muted">报警类型</th>
                  <th class="text-left py-3 px-4 text-muted">报警信息</th>
                  <th class="text-left py-3 px-4 text-muted">报警时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="alarm in alarms" :key="alarm.id" class="border-b hover:bg-gray-50">
                  <td class="py-3 px-4">{{ alarm.id }}</td>
                  <td class="py-3 px-4">{{ alarm.device_id }}</td>
                  <td class="py-3 px-4">
                    <span class="px-2 py-1 rounded-full bg-danger text-white text-xs">
                      报警 {{ alarm.alarm_type }}
                    </span>
                  </td>
                  <td class="py-3 px-4">{{ alarm.message }}</td>
                  <td class="py-3 px-4">{{ alarm.timestamp }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
/* 添加加载动画 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .md\:grid-cols-2,
  .lg\:grid-cols-4 {
    grid-template-columns: 1fr;
  }
  
  .overflow-x-auto {
    overflow-x: auto;
  }
  
  table {
    min-width: 600px;
  }
}
</style>
