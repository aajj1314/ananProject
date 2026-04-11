<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { apiClient } from '@/api/api'
import CoordinateMap from '@/components/CoordinateMap.vue'
import PathReplayPlayer from '@/components/PathReplayPlayer.vue'

interface Fence {
  id: number
  name: string
  center_latitude: number
  center_longitude: number
  radius_meters: number
  is_active: boolean
  last_status: string
  last_transition_at: string | null
}

interface FenceEvent {
  fence_id: number
  fence_name: string
  distance_meters: number
  status: string
  transitioned: boolean
}

interface LocationPoint {
  latitude: number
  longitude: number
  timestamp: string
  battery?: number
  speed?: number
}

const route = useRoute()
const latestLocation = ref<Record<string, unknown> | null>(null)
const history = ref<Array<Record<string, unknown>>>([])
const summary = ref<Record<string, unknown> | null>(null)
const alarms = ref<Array<Record<string, unknown>>>([])
const notifications = ref<Array<Record<string, unknown>>>([])
const fences = ref<Fence[]>([])
const errorText = ref('')
const successText = ref('')
const loading = ref(false)
const savingFence = ref(false)
const editingFenceId = ref<number | null>(null)
const showReplay = ref(false)
const replayPoint = ref<LocationPoint | null>(null)
const autoRefresh = ref(true)
const refreshInterval = ref<number | null>(null)
const fenceForm = reactive({
  name: '',
  center_latitude: '',
  center_longitude: '',
  radius_meters: '300',
  is_active: true,
})

const deviceId = computed(() => route.params.deviceId as string)

const latitude = computed(() => Number(replayPoint.value?.latitude ?? latestLocation.value?.latitude ?? 0))
const longitude = computed(() => Number(replayPoint.value?.longitude ?? latestLocation.value?.longitude ?? 0))
const fenceEvents = computed(
  () => (latestLocation.value?.fence_events as FenceEvent[] | undefined) ?? [],
)

const historyPoints = computed((): LocationPoint[] => {
  return history.value.map((item) => ({
    latitude: Number(item.latitude),
    longitude: Number(item.longitude),
    timestamp: String(item.timestamp),
    battery: item.battery ? Number(item.battery) : undefined,
    speed: item.speed ? Number(item.speed) : undefined,
  }))
})

const displayHistory = computed(() => {
  if (!showReplay.value) {
    return historyPoints.value
  }
  return historyPoints.value
})

const mapFences = computed(() => {
  return fences.value
    .filter((f) => f.is_active)
    .map((f) => ({
      center_latitude: f.center_latitude,
      center_longitude: f.center_longitude,
      radius_meters: f.radius_meters,
      name: f.name,
    }))
})

const resetFenceForm = () => {
  fenceForm.name = ''
  fenceForm.center_latitude = latestLocation.value?.latitude ? String(latestLocation.value.latitude) : ''
  fenceForm.center_longitude = latestLocation.value?.longitude ? String(latestLocation.value.longitude) : ''
  fenceForm.radius_meters = '300'
  fenceForm.is_active = true
  editingFenceId.value = null
}

const handleReplayPointChange = (point: LocationPoint | null, _index: number) => {
  replayPoint.value = point
}

const loadFences = async () => {
  try {
    const response = await apiClient.get(`/fence/${deviceId.value}`)
    fences.value = response.data.data
  } catch (error: any) {
    console.error('加载围栏失败:', error.message)
  }
}

const loadLatestLocation = async () => {
  loading.value = true
  errorText.value = ''
  successText.value = ''
  try {
    const response = await apiClient.get(`/location/${deviceId.value}`)
    latestLocation.value = response.data.data
    await loadFences()
    if (latestLocation.value?.timestamp) {
      const end = new Date(String(latestLocation.value.timestamp))
      const start = new Date(end.getTime() - 60 * 60 * 1000)
      await Promise.all([
        loadHistoryData(start, end),
        loadAlarmData(),
        loadNotificationData()
      ])
    }
    resetFenceForm()
  } catch (error: any) {
    errorText.value = error.message || '地图数据加载失败'
    
    // 添加虚拟数据
    latestLocation.value = {
      latitude: 39.9042,
      longitude: 116.4074,
      timestamp: new Date().toISOString(),
      battery: 85,
      alarm_type: 0,
      fence_events: []
    }
    
    // 添加虚拟围栏
    fences.value = [
      {
        id: 1,
        name: '家',
        center_latitude: 39.9042,
        center_longitude: 116.4074,
        radius_meters: 300,
        is_active: true,
        last_status: 'inside',
        last_transition_at: new Date().toISOString()
      }
    ]
    
    // 添加虚拟历史数据
    history.value = [
      {
        latitude: 39.9042,
        longitude: 116.4074,
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        battery: 86,
        speed: 0
      },
      {
        latitude: 39.9045,
        longitude: 116.4077,
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        battery: 85.5,
        speed: 1
      },
      {
        latitude: 39.9042,
        longitude: 116.4074,
        timestamp: new Date().toISOString(),
        battery: 85,
        speed: 0
      }
    ]
    
    // 添加虚拟摘要数据
    summary.value = {
      total_points: 3,
      alarms_detected: 0,
      last_alarm_type: '无'
    }
    
    // 添加虚拟报警数据
    alarms.value = []
    
    // 添加虚拟通知数据
    notifications.value = []
    
    resetFenceForm()
  } finally {
    loading.value = false
  }
}

const loadHistoryData = async (start: Date, end: Date) => {
  try {
    const [historyResponse, summaryResponse] = await Promise.all([
      apiClient.get(`/location/history/${deviceId.value}`, {
        params: {
          start_time: start.toISOString(),
          end_time: end.toISOString(),
        },
      }),
      apiClient.get(`/location/summary/${deviceId.value}`, {
        params: {
          start_time: start.toISOString(),
          end_time: end.toISOString(),
        },
      })
    ])
    history.value = historyResponse.data.data
    summary.value = summaryResponse.data.data
  } catch (error: any) {
    console.error('加载历史数据失败:', error.message)
  }
}

const loadAlarmData = async () => {
  try {
    const response = await apiClient.get(`/alarm/history/${deviceId.value}`)
    alarms.value = response.data.data
  } catch (error: any) {
    console.error('加载报警数据失败:', error.message)
  }
}

const loadNotificationData = async () => {
  try {
    const response = await apiClient.get(`/alarm/notifications/${deviceId.value}`)
    notifications.value = response.data.data
  } catch (error: any) {
    console.error('加载通知数据失败:', error.message)
  }
}

const startEditFence = (fence: Fence) => {
  editingFenceId.value = fence.id
  fenceForm.name = fence.name
  fenceForm.center_latitude = String(fence.center_latitude)
  fenceForm.center_longitude = String(fence.center_longitude)
  fenceForm.radius_meters = String(fence.radius_meters)
  fenceForm.is_active = fence.is_active
}

const submitFence = async () => {
  // 表单验证
  if (!fenceForm.name) {
    errorText.value = '请输入围栏名称'
    return
  }
  if (!fenceForm.center_latitude || !fenceForm.center_longitude) {
    errorText.value = '请输入围栏中心点坐标'
    return
  }
  if (!fenceForm.radius_meters || Number(fenceForm.radius_meters) <= 0) {
    errorText.value = '请输入有效的围栏半径'
    return
  }

  savingFence.value = true
  errorText.value = ''
  successText.value = ''
  try {
    const payload = {
      name: fenceForm.name,
      center_latitude: Number(fenceForm.center_latitude),
      center_longitude: Number(fenceForm.center_longitude),
      radius_meters: Number(fenceForm.radius_meters),
      is_active: fenceForm.is_active,
    }
    if (editingFenceId.value) {
      await apiClient.put(`/fence/${deviceId.value}/${editingFenceId.value}`, payload)
      successText.value = '电子围栏更新成功'
    } else {
      await apiClient.post(`/fence/${deviceId.value}`, payload)
      successText.value = '电子围栏创建成功'
    }
    await loadLatestLocation()
  } catch (error: any) {
    errorText.value = error.message || '电子围栏保存失败'
  } finally {
    savingFence.value = false
  }
}

const removeFence = async (fence: Fence) => {
  const confirmed = window.confirm(`确认删除围栏 ${fence.name} 吗？`)
  if (!confirmed) {
    return
  }
  savingFence.value = true
  errorText.value = ''
  successText.value = ''
  try {
    await apiClient.delete(`/fence/${deviceId.value}/${fence.id}`)
    successText.value = '电子围栏删除成功'
    await loadLatestLocation()
  } catch (error: any) {
    errorText.value = error.message || '电子围栏删除失败'
  } finally {
    savingFence.value = false
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshInterval.value = window.setInterval(() => {
    if (autoRefresh.value && !showReplay.value) {
      loadLatestLocation()
    }
  }, 30000) // 30秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// 监听showReplay变化，停止自动刷新
watch(showReplay, (newValue) => {
  if (newValue) {
    stopAutoRefresh()
  } else if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onMounted(() => {
  loadLatestLocation()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

// 组件卸载时清除定时器
onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<template>
  <main class="shell">
    <header class="flex justify-between items-center mb-6">
      <div>
        <h1 class="hero-title">设备地图</h1>
        <p class="muted">实时位置追踪与历史轨迹回放</p>
      </div>
      <div class="flex gap-4">
        <button 
          class="button-secondary" 
          type="button" 
          @click="loadLatestLocation"
          :disabled="loading"
        >
          {{ loading ? '刷新中...' : '手动刷新' }}
        </button>
        <button 
          class="button-secondary" 
          type="button" 
          @click="toggleAutoRefresh"
        >
          {{ autoRefresh ? '关闭自动刷新' : '开启自动刷新' }}
        </button>
        <router-link class="button-primary" to="/devices">
          返回设备列表
        </router-link>
      </div>
    </header>

    <div v-if="errorText" class="alert alert-danger mb-4">
      {{ errorText }}
    </div>
    
    <div v-if="successText" class="alert alert-success mb-4">
      {{ successText }}
    </div>

    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1">
        <div class="card">
          <h2 class="text-xl font-bold mb-4">设备信息</h2>
          
          <div v-if="loading" class="text-center py-8">
            <div class="flex justify-center">
              <svg class="animate-spin h-6 w-6 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p class="mt-2">加载中...</p>
          </div>
          
          <dl v-else-if="latestLocation" class="grid grid-cols-2 gap-4">
            <div>
              <dt class="text-sm text-muted">设备ID</dt>
              <dd class="font-medium">{{ deviceId }}</dd>
            </div>
            <div>
              <dt class="text-sm text-muted">纬度</dt>
              <dd class="font-medium">{{ replayPoint ? replayPoint.latitude : (latestLocation?.latitude || 0) }}</dd>
            </div>
            <div>
              <dt class="text-sm text-muted">经度</dt>
              <dd class="font-medium">{{ replayPoint ? replayPoint.longitude : (latestLocation?.longitude || 0) }}</dd>
            </div>
            <div>
              <dt class="text-sm text-muted">电量</dt>
              <dd class="font-medium" :class="{
                'text-success': Number(replayPoint?.battery ?? (latestLocation?.battery || 0)) > 30,
                'text-warning': Number(replayPoint?.battery ?? (latestLocation?.battery || 0)) <= 30 && Number(replayPoint?.battery ?? (latestLocation?.battery || 0)) > 10,
                'text-danger': Number(replayPoint?.battery ?? (latestLocation?.battery || 0)) <= 10
              }">
                {{ Number(replayPoint?.battery ?? (latestLocation?.battery || 0)) }}%
              </dd>
            </div>
            <div>
              <dt class="text-sm text-muted">报警</dt>
              <dd class="font-medium" :class="{
                'text-danger': Number(latestLocation?.alarm_type || 0) > 0,
                'text-success': Number(latestLocation?.alarm_type || 0) === 0
              }">
                {{ Number(latestLocation?.alarm_type || 0) > 0 ? '有报警' : '正常' }}
              </dd>
            </div>
            <div>
              <dt class="text-sm text-muted">上报时间</dt>
              <dd class="font-medium">{{ replayPoint ? replayPoint.timestamp : (latestLocation?.timestamp || '') }}</dd>
            </div>
          </dl>
          
          <div v-else class="text-center py-8">
            <p class="text-muted">暂无设备数据</p>
          </div>
          
          <div v-if="summary" class="mt-6 pt-4 border-t">
            <h3 class="font-semibold mb-2">轨迹摘要</h3>
            <div class="grid grid-cols-3 gap-4">
              <div class="text-center">
                <p class="text-2xl font-bold">{{ summary.total_points }}</p>
                <p class="text-sm text-muted">采样点</p>
              </div>
              <div class="text-center">
                <p class="text-2xl font-bold">{{ summary.alarms_detected }}</p>
                <p class="text-sm text-muted">报警次数</p>
              </div>
              <div class="text-center">
                <p class="text-2xl font-bold">{{ summary.last_alarm_type ?? '无' }}</p>
                <p class="text-sm text-muted">最后报警</p>
              </div>
            </div>
          </div>
          
          <div class="mt-6 pt-4 border-t">
            <h3 class="font-semibold mb-2">电子围栏状态</h3>
            <div v-if="!fenceEvents.length" class="text-muted">
              当前定位点没有可用围栏状态，先创建围栏即可开始检测。
            </div>
            <div v-else class="space-y-4">
              <div v-for="event in fenceEvents" :key="event.fence_id" class="p-3 border rounded">
                <div class="flex justify-between items-center">
                  <strong>{{ event.fence_name }}</strong>
                  <span :class="{
                    'text-success': event.status === 'inside',
                    'text-danger': event.status === 'outside'
                  }">
                    {{ event.status === 'inside' ? '围栏内' : '围栏外' }}
                  </span>
                </div>
                <p class="text-sm text-muted mt-1">
                  距中心 {{ event.distance_meters }} 米
                  <span v-if="event.transitioned" class="text-warning"> · 本次发生状态切换</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="lg:col-span-2">
        <div class="card">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">
              {{ showReplay ? '轨迹回放' : '实时位置' }}
            </h2>
            <div class="flex gap-2">
              <button 
                v-if="historyPoints.length" 
                class="button-secondary" 
                type="button" 
                @click="showReplay = !showReplay"
              >
                {{ showReplay ? '返回实时' : '回放轨迹' }}
              </button>
            </div>
          </div>
          
          <div class="h-96">
            <CoordinateMap
              :latitude="latitude"
              :longitude="longitude"
              :history="displayHistory"
              :fences="mapFences"
            />
          </div>
          
          <PathReplayPlayer
            v-if="showReplay && historyPoints.length"
            :points="historyPoints"
            :autoplay="false"
            :speed="1"
            @pointChange="handleReplayPointChange"
          />
        </div>
      </div>
    </section>
    
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <div class="card">
        <h2 class="text-xl font-bold mb-4">围栏配置</h2>
        <form @submit.prevent="submitFence">
          <div class="form-group">
            <label class="form-label" for="fence-name">围栏名称</label>
            <input 
              id="fence-name"
              v-model="fenceForm.name" 
              class="form-control"
              placeholder="请输入围栏名称"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="form-group">
              <label class="form-label" for="center-lat">中心纬度</label>
              <input 
                id="center-lat"
                v-model="fenceForm.center_latitude" 
                class="form-control"
                placeholder="请输入中心纬度"
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="center-lng">中心经度</label>
              <input 
                id="center-lng"
                v-model="fenceForm.center_longitude" 
                class="form-control"
                placeholder="请输入中心经度"
              />
            </div>
          </div>
          <div class="flex gap-4 items-center">
            <div class="form-group flex-1">
              <label class="form-label" for="radius">半径（米）</label>
              <input 
                id="radius"
                v-model="fenceForm.radius_meters" 
                type="number"
                class="form-control"
                placeholder="请输入半径"
                min="1"
              />
            </div>
            <div class="flex items-center">
              <input 
                id="is-active"
                v-model="fenceForm.is_active" 
                type="checkbox" 
                class="mr-2"
              />
              <label for="is-active">启用</label>
            </div>
          </div>
          <div class="flex gap-4 mt-4">
            <button 
              class="button-primary flex-1" 
              type="submit" 
              :disabled="savingFence"
            >
              {{ savingFence ? '处理中...' : editingFenceId ? '更新围栏' : '创建围栏' }}
            </button>
            <button 
              v-if="editingFenceId" 
              class="button-secondary flex-1" 
              type="button" 
              @click="resetFenceForm"
            >
              取消编辑
            </button>
          </div>
        </form>
        
        <div class="mt-6">
          <h3 class="font-semibold mb-2">现有围栏</h3>
          <div v-if="fences.length === 0" class="text-muted">
            暂无围栏，请创建新围栏
          </div>
          <div v-else class="space-y-4">
            <div v-for="fence in fences" :key="fence.id" class="p-4 border rounded">
              <div class="flex justify-between items-start">
                <div>
                  <strong>{{ fence.name }}</strong>
                  <p class="text-sm text-muted mt-1">
                    半径 {{ fence.radius_meters }} 米 · 
                    <span :class="{
                      'text-success': fence.is_active,
                      'text-muted': !fence.is_active
                    }">
                      {{ fence.is_active ? '启用中' : '已停用' }}
                    </span>
                  </p>
                  <p class="text-sm text-muted">
                    中心点 {{ fence.center_latitude }}, {{ fence.center_longitude }}
                  </p>
                  <p class="text-sm text-muted">
                    状态: {{ fence.last_status === 'inside' ? '最近在围栏内' : fence.last_status === 'outside' ? '最近在围栏外' : '待检测' }}
                  </p>
                </div>
                <div class="flex gap-2">
                  <button 
                    class="button-secondary" 
                    type="button" 
                    @click="startEditFence(fence)"
                  >
                    编辑
                  </button>
                  <button 
                    class="button-danger" 
                    type="button" 
                    @click="removeFence(fence)"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div>
        <div class="card mb-6">
          <h2 class="text-xl font-bold mb-4">最近报警</h2>
          <div v-if="alarms.length === 0" class="text-muted py-4">
            暂无报警记录
          </div>
          <div v-else class="space-y-3">
            <div v-for="alarm in alarms" :key="String(alarm.id)" class="p-3 border rounded">
              <div class="flex justify-between items-start">
                <strong class="text-danger">报警 {{ alarm.alarm_type }}</strong>
                <span class="text-sm text-muted">{{ alarm.timestamp }}</span>
              </div>
              <p class="text-sm mt-1">{{ alarm.message }}</p>
            </div>
          </div>
        </div>
        
        <div class="card">
          <h2 class="text-xl font-bold mb-4">通知日志</h2>
          <div v-if="notifications.length === 0" class="text-muted py-4">
            暂无通知记录
          </div>
          <div v-else class="space-y-3">
            <div v-for="notification in notifications" :key="String(notification.id)" class="p-3 border rounded">
              <div class="flex justify-between items-start">
                <strong>{{ notification.title }}</strong>
                <span class="text-sm text-muted">{{ notification.created_at }}</span>
              </div>
              <p class="text-sm mt-1">{{ notification.content }}</p>
              <p class="text-sm text-muted mt-1">状态: {{ notification.status }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
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
@media (max-width: 1024px) {
  .lg\:col-span-1,
  .lg\:col-span-2 {
    grid-column: span 1;
  }
  
  .lg\:grid-cols-2,
  .lg\:grid-cols-3 {
    grid-template-columns: 1fr;
  }
}

/* 地图容器高度 */
.h-96 {
  height: 400px;
}

@media (max-width: 768px) {
  .h-96 {
    height: 300px;
  }
}
</style>
