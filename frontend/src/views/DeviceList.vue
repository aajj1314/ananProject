<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { apiClient } from '@/api/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

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
const errorText = ref('')
const successText = ref('')
const savingDeviceId = ref('')
const loading = ref(false)
const form = reactive({
  device_id: '',
  device_name: '',
})

const loadDevices = async () => {
  loading.value = true
  errorText.value = ''
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
        } catch (error) {
          latestAlarms.value[device.device_id] = {
            alarm_type: 0,
            battery: device.battery,
            timestamp: device.last_updated || '',
          }
        }
      }),
    )
  } catch (error: any) {
    errorText.value = error.message || '设备列表加载失败'
    
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

const createDevice = async () => {
  // 表单验证
  if (!form.device_id) {
    errorText.value = '请输入设备IMEI'
    return
  }
  if (!form.device_name) {
    errorText.value = '请输入设备名称'
    return
  }
  if (form.device_id.length !== 15) {
    errorText.value = 'IMEI必须为15位'
    return
  }

  savingDeviceId.value = 'create'
  errorText.value = ''
  successText.value = ''
  try {
    await apiClient.post('/device', form)
    form.device_id = ''
    form.device_name = ''
    successText.value = '设备绑定成功'
    await loadDevices()
  } catch (error: any) {
    errorText.value = error.message || '新设备绑定失败'
  } finally {
    savingDeviceId.value = ''
  }
}

const renameDevice = async (device: Device) => {
  const nextName = window.prompt('输入新的设备名称', device.device_name)
  if (!nextName) {
    return
  }
  savingDeviceId.value = device.device_id
  errorText.value = ''
  successText.value = ''
  try {
    await apiClient.put(`/device/${device.device_id}`, { device_name: nextName })
    successText.value = '设备重命名成功'
    await loadDevices()
  } catch (error: any) {
    errorText.value = error.message || '设备更新失败'
  } finally {
    savingDeviceId.value = ''
  }
}

const removeDevice = async (device: Device) => {
  const confirmed = window.confirm(`确认解绑设备 ${device.device_name} 吗？`)
  if (!confirmed) {
    return
  }
  savingDeviceId.value = device.device_id
  errorText.value = ''
  successText.value = ''
  try {
    await apiClient.delete(`/device/${device.device_id}`)
    successText.value = '设备解绑成功'
    await loadDevices()
  } catch (error: any) {
    errorText.value = error.message || '设备解绑失败'
  } finally {
    savingDeviceId.value = ''
  }
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const loadUserProfile = async () => {
  try {
    if (!authStore.user && authStore.token) {
      const response = await apiClient.get('/auth/profile')
      authStore.setUser(response.data.data)
    }
  } catch (error) {
    // If profile fails, user might need to re-login
  }
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
        <router-link v-if="authStore.isAdmin" class="button-secondary" to="/admin">
          管理后台
        </router-link>
        <button class="button-danger" type="button" @click="logout">
          退出登录
        </button>
      </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="md:col-span-2">
        <div class="card">
          <h2 class="text-xl font-bold mb-4">设备列表</h2>
          
          <div v-if="errorText" class="alert alert-danger mb-4">
            {{ errorText }}
          </div>
          
          <div v-if="successText" class="alert alert-success mb-4">
            {{ successText }}
          </div>
          
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
            <p class="text-muted">暂无设备，请绑定新设备</p>
          </div>
          
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="device in devices" :key="device.device_id" class="card">
              <div class="flex justify-between items-start mb-4">
                <div>
                  <h3 class="text-lg font-semibold">{{ device.device_name }}</h3>
                  <p class="text-sm text-muted">IMEI: {{ device.device_id }}</p>
                </div>
                <div :class="{
                  'w-3 h-3 rounded-full bg-success': device.battery > 30,
                  'w-3 h-3 rounded-full bg-warning': device.battery <= 30 && device.battery > 10,
                  'w-3 h-3 rounded-full bg-danger': device.battery <= 10
                }" :title="`电量: ${device.battery}%`"></div>
              </div>
              
              <div class="mb-4">
                <div class="flex justify-between mb-1">
                  <span class="text-sm text-muted">电量</span>
                  <span class="text-sm font-medium">{{ device.battery }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
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
              </div>
              
              <div class="mb-4">
                <div class="flex justify-between mb-1">
                  <span class="text-sm text-muted">最后上报</span>
                  <span class="text-sm font-medium">{{ device.last_updated || '暂无数据' }}</span>
                </div>
              </div>
              
              <div class="mb-4">
                <div class="flex justify-between mb-1">
                  <span class="text-sm text-muted">报警状态</span>
                  <span class="text-sm font-medium" :class="{
                    'text-danger': latestAlarms[device.device_id]?.alarm_type > 0,
                    'text-success': latestAlarms[device.device_id]?.alarm_type === 0
                  }">
                    {{ latestAlarms[device.device_id]?.alarm_type > 0 ? '有报警' : '正常' }}
                  </span>
                </div>
              </div>
              
              <div class="flex gap-2">
                <router-link class="button-primary flex-1" :to="`/map/${device.device_id}`">
                  查看地图
                </router-link>
                <button 
                  class="button-secondary flex-1" 
                  type="button" 
                  @click="renameDevice(device)" 
                  :disabled="savingDeviceId === device.device_id"
                >
                  重命名
                </button>
                <button 
                  class="button-danger" 
                  type="button" 
                  @click="removeDevice(device)" 
                  :disabled="savingDeviceId === device.device_id"
                >
                  解绑
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div>
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
              class="button-primary w-full" 
              type="submit" 
              :disabled="savingDeviceId === 'create'"
            >
              {{ savingDeviceId === 'create' ? '处理中...' : '绑定设备' }}
            </button>
          </form>
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
  .md\:col-span-2 {
    grid-column: span 1;
  }
  
  .md\:grid-cols-2,
  .lg\:grid-cols-3 {
    grid-template-columns: 1fr;
  }
}
</style>
