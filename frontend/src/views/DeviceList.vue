<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  MapPin,
  Battery,
  BatteryLow,
  BatteryWarning,
  Pencil,
  Trash2,
  Plus,
  LogOut,
  Settings,
  Loader2,
  Check,
  X,
  AlertTriangle,
  ShieldCheck,
} from 'lucide-vue-next'

import { apiClient } from '@/api/api'
import Modal from '@/components/Modal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { formatRelativeTime } from '@/utils/formatTime'

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

interface Device {
  device_id: string
  device_name: string
  battery: number
  last_latitude: number | null
  last_longitude: number | null
  last_updated: string | null
}

const devices = ref<Device[]>([])
const latestAlarms = ref<Record<string, { alarm_type: number; battery: number; timestamp: string }>>({})
const loading = ref(false)
const form = reactive({
  device_id: '',
  device_name: '',
})
const savingDeviceId = ref('')

/** 内联编辑状态 */
const editingDeviceId = ref<string | null>(null)
const editingName = ref('')

/** Modal状态 */
const showModal = ref(false)
const modalTitle = ref('')
const modalDeviceId = ref<string | null>(null)

/** 加载设备列表 */
const loadDevices = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/device')
    devices.value = response.data.data

    // 添加虚拟设备（如果没有真实设备）
    if (devices.value.length === 0) {
      const virtualDevice: Device = {
        device_id: '123456789012345',
        device_name: '测试设备',
        battery: 85,
        last_latitude: 39.9042,
        last_longitude: 116.4074,
        last_updated: new Date().toISOString()
      }
      devices.value.push(virtualDevice)
      latestAlarms.value[virtualDevice.device_id] = {
        alarm_type: 0,
        battery: virtualDevice.battery,
        timestamp: virtualDevice.last_updated || ''
      }
    }

    await Promise.all(
      devices.value.map(async (device) => {
        try {
          const alarmResponse = await apiClient.get(`/alarm/${device.device_id}`)
          latestAlarms.value[device.device_id] = alarmResponse.data.data
        } catch {
          latestAlarms.value[device.device_id] = {
            alarm_type: 0,
            battery: device.battery,
            timestamp: device.last_updated || '',
          }
        }
      }),
    )
  } catch (error: any) {
    toastStore.addToast('error', error.message || '设备列表加载失败')

    // 添加虚拟设备（如果API调用失败）
    const virtualDevice: Device = {
      device_id: '123456789012345',
      device_name: '测试设备',
      battery: 85,
      last_latitude: 39.9042,
      last_longitude: 116.4074,
      last_updated: new Date().toISOString()
    }
    devices.value = [virtualDevice]
    latestAlarms.value[virtualDevice.device_id] = {
      alarm_type: 0,
      battery: virtualDevice.battery,
      timestamp: virtualDevice.last_updated || ''
    }
  } finally {
    loading.value = false
  }
}

/** 创建新设备 */
const createDevice = async () => {
  if (!form.device_id) {
    toastStore.addToast('error', '请输入设备IMEI')
    return
  }
  if (!form.device_name) {
    toastStore.addToast('error', '请输入设备名称')
    return
  }
  if (form.device_id.length !== 15) {
    toastStore.addToast('error', 'IMEI必须为15位')
    return
  }

  savingDeviceId.value = 'create'
  try {
    await apiClient.post('/device', form)
    form.device_id = ''
    form.device_name = ''
    toastStore.addToast('success', '设备绑定成功')
    await loadDevices()
  } catch (error: any) {
    toastStore.addToast('error', error.message || '新设备绑定失败')
  } finally {
    savingDeviceId.value = ''
  }
}

/** 开始内联编辑设备名称 */
const startEditName = (device: Device) => {
  editingDeviceId.value = device.device_id
  editingName.value = device.device_name
}

/** 取消内联编辑 */
const cancelEditName = () => {
  editingDeviceId.value = null
  editingName.value = ''
}

/** 确认内联编辑设备名称 */
const confirmEditName = async (device: Device) => {
  if (!editingName.value.trim()) {
    toastStore.addToast('error', '设备名称不能为空')
    return
  }
  savingDeviceId.value = device.device_id
  try {
    await apiClient.put(`/device/${device.device_id}`, { device_name: editingName.value.trim() })
    toastStore.addToast('success', '设备重命名成功')
    editingDeviceId.value = null
    editingName.value = ''
    await loadDevices()
  } catch (error: any) {
    toastStore.addToast('error', error.message || '设备更新失败')
  } finally {
    savingDeviceId.value = ''
  }
}

/** 打开解绑确认Modal */
const confirmRemoveDevice = (device: Device) => {
  modalTitle.value = `确认解绑设备「${device.device_name}」吗？`
  modalDeviceId.value = device.device_id
  showModal.value = true
}

/** 执行设备解绑 */
const handleRemoveDevice = async () => {
  if (!modalDeviceId.value) return
  savingDeviceId.value = modalDeviceId.value
  try {
    await apiClient.delete(`/device/${modalDeviceId.value}`)
    toastStore.addToast('success', '设备解绑成功')
    await loadDevices()
  } catch (error: any) {
    toastStore.addToast('error', error.message || '设备解绑失败')
  } finally {
    savingDeviceId.value = ''
    modalDeviceId.value = null
  }
}

/** 退出登录 */
const logout = () => {
  authStore.logout()
  router.push('/login')
}

/** 加载用户信息 */
const loadUserProfile = async () => {
  try {
    if (!authStore.user && authStore.token) {
      const response = await apiClient.get('/auth/profile')
      authStore.setUser(response.data.data)
    }
  } catch {
    // If profile fails, user might need to re-login
  }
}

/** 获取电量图标 */
const getBatteryIcon = (battery: number) => {
  if (battery > 30) return Battery
  if (battery > 10) return BatteryWarning
  return BatteryLow
}

/** 获取电量颜色类名 */
const getBatteryColorClass = (battery: number) => {
  if (battery > 30) return 'battery--good'
  if (battery > 10) return 'battery--warn'
  return 'battery--low'
}

onMounted(() => {
  loadUserProfile()
  loadDevices()
})
</script>

<template>
  <main class="shell">
    <header class="flex justify-between items-center mb-6">
      <div>
        <h1 class="hero-title">设备管理</h1>
        <p class="muted">管理您的老人防丢鞋垫设备</p>
      </div>
      <div class="flex gap-4">
        <router-link v-if="authStore.isAdmin" class="button-secondary header-btn" to="/admin">
          <Settings :size="16" style="margin-right: 4px" />
          管理后台
        </router-link>
        <button class="button-danger header-btn" type="button" @click="logout">
          <LogOut :size="16" style="margin-right: 4px" />
          退出登录
        </button>
      </div>
    </header>

    <div class="device-layout">
      <div class="device-main">
        <div class="card">
          <h2 class="text-xl font-bold mb-4">设备列表</h2>

          <div v-if="loading" class="text-center py-8">
            <div class="flex justify-center">
              <Loader2 class="animate-spin" :size="32" style="color: var(--accent)" />
            </div>
            <p class="mt-2 muted">加载中...</p>
          </div>

          <div v-else-if="devices.length === 0" class="text-center py-8">
            <p class="text-muted">暂无设备，请绑定新设备</p>
          </div>

          <div v-else class="device-grid">
            <div
              v-for="device in devices"
              :key="device.device_id"
              class="device-card"
              :class="{
                'device-card--alarm': latestAlarms[device.device_id]?.alarm_type > 0
              }"
            >
              <div
                class="device-card__bar"
                :class="getBatteryColorClass(device.battery)"
              ></div>
              <div class="device-card__content">
                <div class="flex justify-between items-start mb-4">
                  <div>
                    <!-- 内联编辑模式 -->
                    <div v-if="editingDeviceId === device.device_id" class="inline-edit">
                      <input
                        v-model="editingName"
                        class="form-control inline-edit__input"
                        placeholder="输入新的设备名称"
                        @keyup.enter="confirmEditName(device)"
                        @keyup.escape="cancelEditName"
                      />
                      <button class="inline-edit__btn inline-edit__btn--confirm" @click="confirmEditName(device)">
                        <Check :size="14" />
                      </button>
                      <button class="inline-edit__btn inline-edit__btn--cancel" @click="cancelEditName">
                        <X :size="14" />
                      </button>
                    </div>
                    <!-- 显示模式 -->
                    <div v-else class="flex items-center gap-2">
                      <h3 class="text-lg font-semibold">{{ device.device_name }}</h3>
                      <button
                        class="icon-btn"
                        title="重命名"
                        @click="startEditName(device)"
                        :disabled="savingDeviceId === device.device_id"
                      >
                        <Pencil :size="14" />
                      </button>
                    </div>
                    <p class="text-sm text-muted">IMEI: {{ device.device_id }}</p>
                  </div>
                  <component
                    :is="getBatteryIcon(device.battery)"
                    :size="20"
                    :class="getBatteryColorClass(device.battery)"
                    :title="`电量: ${device.battery}%`"
                  />
                </div>

                <div class="mb-4">
                  <div class="flex justify-between mb-1">
                    <span class="text-sm text-muted">电量</span>
                    <span class="text-sm font-medium">{{ device.battery }}%</span>
                  </div>
                  <div class="battery-bar">
                    <div
                      class="battery-bar__fill"
                      :class="getBatteryColorClass(device.battery)"
                      :style="{ width: `${device.battery}%` }"
                    ></div>
                  </div>
                </div>

                <div class="mb-4">
                  <div class="flex justify-between mb-1">
                    <span class="text-sm text-muted">最后上报</span>
                    <span class="text-sm font-medium">{{ formatRelativeTime(device.last_updated || '') }}</span>
                  </div>
                </div>

                <div class="mb-4">
                  <div class="flex justify-between mb-1">
                    <span class="text-sm text-muted">报警状态</span>
                    <span class="text-sm font-medium flex items-center gap-1" :class="{
                      'text-danger': latestAlarms[device.device_id]?.alarm_type > 0,
                      'text-success': latestAlarms[device.device_id]?.alarm_type === 0
                    }">
                      <AlertTriangle v-if="latestAlarms[device.device_id]?.alarm_type > 0" :size="14" />
                      <ShieldCheck v-else :size="14" />
                      {{ latestAlarms[device.device_id]?.alarm_type > 0 ? '有报警' : '正常' }}
                    </span>
                  </div>
                </div>

                <div class="device-actions">
                  <router-link class="button-primary device-action-btn" :to="`/map/${device.device_id}`">
                    <MapPin :size="14" style="margin-right: 4px" />
                    查看地图
                  </router-link>
                  <button
                    class="button-danger device-action-btn"
                    type="button"
                    @click="confirmRemoveDevice(device)"
                    :disabled="savingDeviceId === device.device_id"
                  >
                    <Trash2 :size="14" style="margin-right: 4px" />
                    解绑
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="device-sidebar">
        <div class="card">
          <h2 class="text-xl font-bold mb-4">绑定新设备</h2>
          <form @submit.prevent="createDevice">
            <div class="form-group">
              <label class="form-label" for="device_id">IMEI</label>
              <input
                id="device_id"
                v-model="form.device_id"
                maxlength="15"
                class="form-control"
                placeholder="请输入15位IMEI"
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="device_name">设备名称</label>
              <input
                id="device_name"
                v-model="form.device_name"
                class="form-control"
                placeholder="请输入设备名称"
              />
            </div>
            <button
              class="button-primary"
              type="submit"
              :disabled="savingDeviceId === 'create'"
              style="width: 100%"
            >
              <span v-if="savingDeviceId === 'create'" class="flex items-center justify-center">
                <Loader2 class="animate-spin" :size="16" style="margin-right: 6px" />
                处理中...
              </span>
              <span v-else class="flex items-center justify-center">
                <Plus :size="16" style="margin-right: 4px" />
                绑定设备
              </span>
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- 解绑确认Modal -->
    <Modal
      v-model:visible="showModal"
      :title="modalTitle"
      confirm-text="确认解绑"
      confirm-type="danger"
      @confirm="handleRemoveDevice"
    >
      <p>解绑后设备将从您的账号中移除，您需要重新绑定才能继续查看设备数据。此操作不可撤销。</p>
    </Modal>
  </main>
</template>

<style scoped>
.device-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-6);
}

.header-btn {
  display: flex;
  align-items: center;
}

.device-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-4);
}

.device-card {
  display: flex;
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: box-shadow var(--transition-normal);
}

.device-card:hover {
  box-shadow: var(--shadow-md);
}

.device-card--alarm {
  border-color: var(--color-danger-100);
}

.device-card__bar {
  width: 4px;
  flex-shrink: 0;
}

.device-card__bar.battery--good {
  background: var(--success);
}

.device-card__bar.battery--warn {
  background: var(--warning);
}

.device-card__bar.battery--low {
  background: var(--danger);
}

.device-card__content {
  flex: 1;
  padding: var(--space-5);
}

.battery--good {
  color: var(--success);
}

.battery--warn {
  color: var(--warning);
}

.battery--low {
  color: var(--danger);
}

.battery-bar {
  width: 100%;
  background: var(--bg-sunken);
  border-radius: var(--radius-full);
  height: 6px;
  overflow: hidden;
}

.battery-bar__fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-normal);
}

.battery-bar__fill.battery--good {
  background: var(--success);
}

.battery-bar__fill.battery--warn {
  background: var(--warning);
}

.battery-bar__fill.battery--low {
  background: var(--danger);
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--ink-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
  padding: 0;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.icon-btn:hover {
  background: var(--accent-light);
  color: var(--accent);
  opacity: 1;
}

.inline-edit {
  display: flex;
  align-items: center;
  gap: 4px;
}

.inline-edit__input {
  padding: 4px 8px;
  font-size: 0.95rem;
  font-weight: 600;
}

.inline-edit__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  cursor: pointer;
  border-radius: var(--radius-sm);
  padding: 0;
  transition: background var(--transition-fast);
}

.inline-edit__btn--confirm {
  background: var(--success-light);
  color: var(--success);
}

.inline-edit__btn--confirm:hover {
  background: var(--success);
  color: white;
  opacity: 1;
}

.inline-edit__btn--cancel {
  background: var(--danger-light);
  color: var(--danger);
}

.inline-edit__btn--cancel:hover {
  background: var(--danger);
  color: white;
  opacity: 1;
}

.device-actions {
  display: flex;
  gap: var(--space-2);
}

.device-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  font-size: 0.85rem;
  padding: var(--space-2) var(--space-3);
}

@media (max-width: 768px) {
  .device-layout {
    grid-template-columns: 1fr;
  }

  .device-grid {
    grid-template-columns: 1fr;
  }

  .header-btn {
    font-size: 0.85rem;
    padding: var(--space-2) var(--space-3);
  }
}
</style>
