<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Users,
  Smartphone,
  Bell,
  Megaphone,
  RefreshCw,
  ArrowLeft,
  Loader2,
  Shield,
  ShieldOff,
  Trash2,
  AlertTriangle,
} from 'lucide-vue-next'

import { apiClient } from '@/api/api'
import Modal from '@/components/Modal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { formatRelativeTime } from '@/utils/formatTime'

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
const toastStore = useToastStore()

const stats = ref<Stats | null>(null)
const users = ref<UserItem[]>([])
const devices = ref<DeviceItem[]>([])
const alarms = ref<AlarmItem[]>([])
const loading = ref(true)
const activeTab = ref('users')

/** 跟踪各标签页数据是否已加载，避免重复请求 */
const loadedTabs = ref<Set<string>>(new Set())

/** Modal状态 */
const showModal = ref(false)
const modalTitle = ref('')
const modalUserId = ref<number | null>(null)

/** 加载统计数据（轻量，始终加载） */
const loadStats = async () => {
  try {
    const statsResponse = await apiClient.get('/admin/stats')
    stats.value = statsResponse.data.data
  } catch (error: any) {
    toastStore.addToast('error', error.message || '统计数据加载失败')
  }
}

/** 按标签页加载数据，避免一次性请求所有数据 */
const loadTabData = async (tab: string) => {
  if (loadedTabs.value.has(tab)) return

  try {
    switch (tab) {
      case 'users': {
        const response = await apiClient.get('/admin/users', { params: { limit: 20 } })
        users.value = response.data.data.items
        break
      }
      case 'devices': {
        const response = await apiClient.get('/admin/devices')
        devices.value = response.data.data
        break
      }
      case 'alarms': {
        const response = await apiClient.get('/admin/alarms', { params: { limit: 20 } })
        alarms.value = response.data.data
        break
      }
    }
    loadedTabs.value.add(tab)
  } catch (error: any) {
    toastStore.addToast('error', error.message || '数据加载失败')
  }
}

/** 加载所有数据（用于刷新按钮） */
const loadData = async () => {
  loading.value = true
  loadedTabs.value.clear()
  try {
    await loadStats()
    await loadTabData(activeTab.value)
  } finally {
    loading.value = false
  }
}

/** 监听标签页切换，按需加载数据 */
const handleTabChange = async (tab: string) => {
  activeTab.value = tab
  await loadTabData(tab)
}

/** 更新用户角色 */
const updateUserRole = async (user: UserItem, newRole: 'user' | 'admin') => {
  try {
    await apiClient.put(`/admin/users/${user.id}/role?role=${newRole}`)
    user.role = newRole
    toastStore.addToast('success', `用户 ${user.nickname} 已${newRole === 'admin' ? '设为' : '取消'}管理员`)
  } catch (error: any) {
    toastStore.addToast('error', error.message || '角色更新失败')
  }
}

/** 打开删除用户确认Modal */
const confirmDeleteUser = (user: UserItem) => {
  if (user.id === authStore.user?.id) {
    toastStore.addToast('error', '不能删除自己的账号')
    return
  }
  modalTitle.value = `确认删除用户「${user.nickname}」吗？`
  modalUserId.value = user.id
  showModal.value = true
}

/** 执行删除用户 */
const handleDeleteUser = async () => {
  if (!modalUserId.value) return
  try {
    await apiClient.delete(`/admin/users/${modalUserId.value}`)
    const deletedUser = users.value.find(u => u.id === modalUserId.value)
    users.value = users.value.filter(u => u.id !== modalUserId.value)
    toastStore.addToast('success', `用户 ${deletedUser?.nickname || ''} 已删除`)
  } catch (error: any) {
    toastStore.addToast('error', error.message || '用户删除失败')
  } finally {
    modalUserId.value = null
  }
}

/** 获取电量颜色类名 */
const getBatteryColorClass = (battery: number) => {
  if (battery > 30) return 'battery--good'
  if (battery > 10) return 'battery--warn'
  return 'battery--low'
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
          class="button-primary header-btn"
          type="button"
          @click="loadData"
          :disabled="loading"
        >
          <RefreshCw :size="14" style="margin-right: 4px" :class="{ 'animate-spin': loading }" />
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
        <router-link class="button-secondary header-btn" to="/devices">
          <ArrowLeft :size="14" style="margin-right: 4px" />
          返回设备管理
        </router-link>
      </div>
    </header>

    <section v-if="stats" class="stats-grid">
      <div class="card stat-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-muted">用户总数</p>
            <h2 class="text-3xl font-bold">{{ stats.users.total }}</h2>
          </div>
          <div class="stat-icon stat-icon--accent">
            <Users :size="22" />
          </div>
        </div>
      </div>
      <div class="card stat-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-muted">设备总数</p>
            <h2 class="text-3xl font-bold">{{ stats.devices.total }}</h2>
          </div>
          <div class="stat-icon stat-icon--info">
            <Smartphone :size="22" />
          </div>
        </div>
      </div>
      <div class="card stat-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-muted">报警总数</p>
            <h2 class="text-3xl font-bold">{{ stats.alarms.total }}</h2>
          </div>
          <div class="stat-icon stat-icon--danger">
            <Bell :size="22" />
          </div>
        </div>
      </div>
      <div class="card stat-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-muted">通知总数</p>
            <h2 class="text-3xl font-bold">{{ stats.notifications.total }}</h2>
          </div>
          <div class="stat-icon stat-icon--success">
            <Megaphone :size="22" />
          </div>
        </div>
      </div>
    </section>

    <div class="card mb-6">
      <div class="tab-bar">
        <button
          class="tab-btn"
          :class="{ 'tab-btn--active': activeTab === 'users' }"
          @click="handleTabChange('users')"
        >
          <Users :size="16" style="margin-right: 4px" />
          用户管理
        </button>
        <button
          class="tab-btn"
          :class="{ 'tab-btn--active': activeTab === 'devices' }"
          @click="handleTabChange('devices')"
        >
          <Smartphone :size="16" style="margin-right: 4px" />
          设备管理
        </button>
        <button
          class="tab-btn"
          :class="{ 'tab-btn--active': activeTab === 'alarms' }"
          @click="handleTabChange('alarms')"
        >
          <AlertTriangle :size="16" style="margin-right: 4px" />
          报警记录
        </button>
      </div>

      <div class="tab-content">
        <!-- 用户管理 -->
        <div v-if="activeTab === 'users'">
          <h3 class="text-lg font-semibold mb-4">用户列表</h3>

          <div v-if="loading" class="text-center py-8">
            <div class="flex justify-center">
              <Loader2 class="animate-spin" :size="28" style="color: var(--accent)" />
            </div>
            <p class="mt-2 muted">加载中...</p>
          </div>

          <div v-else-if="users.length === 0" class="text-center py-8">
            <p class="text-muted">暂无用户</p>
          </div>

          <div v-else class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>手机号</th>
                  <th>昵称</th>
                  <th>角色</th>
                  <th>注册时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.phone }}</td>
                  <td>{{ user.nickname }}</td>
                  <td>
                    <span class="role-badge" :class="{
                      'role-badge--admin': user.role === 'admin',
                      'role-badge--user': user.role === 'user'
                    }">
                      {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                    </span>
                  </td>
                  <td>{{ formatRelativeTime(user.created_at) }}</td>
                  <td>
                    <div class="flex gap-2">
                      <button
                        v-if="user.role === 'user'"
                        class="button-primary table-btn"
                        type="button"
                        @click="updateUserRole(user, 'admin')"
                      >
                        <Shield :size="12" style="margin-right: 2px" />
                        设为管理员
                      </button>
                      <button
                        v-else
                        class="button-secondary table-btn"
                        type="button"
                        @click="updateUserRole(user, 'user')"
                      >
                        <ShieldOff :size="12" style="margin-right: 2px" />
                        取消管理员
                      </button>
                      <button
                        class="button-danger table-btn"
                        type="button"
                        @click="confirmDeleteUser(user)"
                      >
                        <Trash2 :size="12" style="margin-right: 2px" />
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
              <Loader2 class="animate-spin" :size="28" style="color: var(--accent)" />
            </div>
            <p class="mt-2 muted">加载中...</p>
          </div>

          <div v-else-if="devices.length === 0" class="text-center py-8">
            <p class="text-muted">暂无设备</p>
          </div>

          <div v-else class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>设备ID</th>
                  <th>设备名称</th>
                  <th>用户ID</th>
                  <th>电量</th>
                  <th>最后上报</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="device in devices" :key="device.device_id">
                  <td>{{ device.device_id }}</td>
                  <td>{{ device.device_name }}</td>
                  <td>{{ device.user_id }}</td>
                  <td>
                    <div class="flex items-center">
                      <div class="battery-bar-sm">
                        <div
                          class="battery-bar-sm__fill"
                          :class="getBatteryColorClass(device.battery)"
                          :style="{ width: `${device.battery}%` }"
                        ></div>
                      </div>
                      <span style="margin-left: 8px">{{ device.battery }}%</span>
                    </div>
                  </td>
                  <td>{{ formatRelativeTime(device.last_updated || '') }}</td>
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
              <Loader2 class="animate-spin" :size="28" style="color: var(--accent)" />
            </div>
            <p class="mt-2 muted">加载中...</p>
          </div>

          <div v-else-if="alarms.length === 0" class="text-center py-8">
            <p class="text-muted">暂无报警记录</p>
          </div>

          <div v-else class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>设备ID</th>
                  <th>报警类型</th>
                  <th>报警信息</th>
                  <th>报警时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="alarm in alarms" :key="alarm.id">
                  <td>{{ alarm.id }}</td>
                  <td>{{ alarm.device_id }}</td>
                  <td>
                    <span class="role-badge role-badge--danger">
                      报警 {{ alarm.alarm_type }}
                    </span>
                  </td>
                  <td>{{ alarm.message }}</td>
                  <td>{{ formatRelativeTime(alarm.timestamp) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除用户确认Modal -->
    <Modal
      v-model:visible="showModal"
      :title="modalTitle"
      confirm-text="确认删除"
      confirm-type="danger"
      @confirm="handleDeleteUser"
    >
      <p>删除用户后，该用户的所有数据将被永久移除。此操作不可撤销。</p>
    </Modal>
  </main>
</template>

<style scoped>
.header-btn {
  display: flex;
  align-items: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  margin-bottom: 0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-icon--accent {
  background: var(--accent);
}

.stat-icon--info {
  background: var(--info);
}

.stat-icon--danger {
  background: var(--danger);
}

.stat-icon--success {
  background: var(--success);
}

.tab-bar {
  display: flex;
  border-bottom: 1px solid var(--line);
}

.tab-btn {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  font-weight: 500;
  border: none;
  background: transparent;
  color: var(--ink-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color var(--transition-fast), border-color var(--transition-fast);
}

.tab-btn:hover {
  color: var(--accent);
  opacity: 1;
}

.tab-btn--active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.tab-content {
  padding: var(--space-4);
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  color: var(--ink-secondary);
  font-weight: 500;
  font-size: 0.85rem;
  border-bottom: 1px solid var(--line);
}

.data-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--line);
}

.data-table tbody tr:hover {
  background: var(--bg-sunken);
}

.role-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
}

.role-badge--admin {
  background: var(--accent-subtle);
  color: var(--accent);
}

.role-badge--user {
  background: var(--bg-sunken);
  color: var(--ink-secondary);
}

.role-badge--danger {
  background: var(--danger-light);
  color: var(--danger);
}

.table-btn {
  display: inline-flex;
  align-items: center;
  font-size: 0.8rem;
  padding: 4px 10px;
}

.battery-bar-sm {
  width: 80px;
  background: var(--bg-sunken);
  border-radius: var(--radius-full);
  height: 4px;
  overflow: hidden;
}

.battery-bar-sm__fill {
  height: 100%;
  border-radius: var(--radius-full);
}

.battery--good {
  background: var(--success);
}

.battery--warn {
  background: var(--warning);
}

.battery--low {
  background: var(--danger);
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .header-btn {
    font-size: 0.85rem;
    padding: var(--space-2) var(--space-3);
  }

  .table-wrapper {
    overflow-x: auto;
  }

  .data-table {
    min-width: 600px;
  }
}
</style>
