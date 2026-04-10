<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
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
const savingFence = ref(false)
const editingFenceId = ref<number | null>(null)
const showReplay = ref(false)
const replayPoint = ref<LocationPoint | null>(null)
const fenceForm = reactive({
  name: '',
  center_latitude: '',
  center_longitude: '',
  radius_meters: '300',
  is_active: true,
})

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
  const response = await apiClient.get(`/fence/${route.params.deviceId}`)
  fences.value = response.data.data
}

const loadLatestLocation = async () => {
  try {
    const response = await apiClient.get(`/location/${route.params.deviceId}`)
    latestLocation.value = response.data.data
    await loadFences()
    if (latestLocation.value?.timestamp) {
      const end = new Date(String(latestLocation.value.timestamp))
      const start = new Date(end.getTime() - 60 * 60 * 1000)
      const historyResponse = await apiClient.get(`/location/history/${route.params.deviceId}`, {
        params: {
          start_time: start.toISOString(),
          end_time: end.toISOString(),
        },
      })
      history.value = historyResponse.data.data
      const summaryResponse = await apiClient.get(`/location/summary/${route.params.deviceId}`, {
        params: {
          start_time: start.toISOString(),
          end_time: end.toISOString(),
        },
      })
      summary.value = summaryResponse.data.data
      const alarmResponse = await apiClient.get(`/alarm/history/${route.params.deviceId}`)
      alarms.value = alarmResponse.data.data
      const notificationResponse = await apiClient.get(`/alarm/notifications/${route.params.deviceId}`)
      notifications.value = notificationResponse.data.data
    }
    resetFenceForm()
  } catch (error) {
    errorText.value = '地图数据加载失败'
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
  savingFence.value = true
  errorText.value = ''
  try {
    const payload = {
      name: fenceForm.name,
      center_latitude: Number(fenceForm.center_latitude),
      center_longitude: Number(fenceForm.center_longitude),
      radius_meters: Number(fenceForm.radius_meters),
      is_active: fenceForm.is_active,
    }
    if (editingFenceId.value) {
      await apiClient.put(`/fence/${route.params.deviceId}/${editingFenceId.value}`, payload)
    } else {
      await apiClient.post(`/fence/${route.params.deviceId}`, payload)
    }
    await loadLatestLocation()
  } catch (error) {
    errorText.value = '电子围栏保存失败'
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
  try {
    await apiClient.delete(`/fence/${route.params.deviceId}/${fence.id}`)
    await loadLatestLocation()
  } catch (error) {
    errorText.value = '电子围栏删除失败'
  } finally {
    savingFence.value = false
  }
}

onMounted(() => {
  loadLatestLocation()
})
</script>

<template>
  <main class="shell">
    <section class="grid" style="grid-template-columns: 0.95fr 1.05fr;">
      <div class="panel" style="padding: 24px;">
        <p class="muted">Map Phase</p>
        <h1 style="margin-top:0;">设备 {{ route.params.deviceId }}</h1>
        <p class="muted">坐标映射视图 + 轨迹回放模式。真实地图 SDK 可通过 VITE_MAP_PROVIDER 配置接入。</p>
        <p v-if="errorText" style="color:#8f1f1f;">{{ errorText }}</p>
        <dl v-if="latestLocation" style="display:grid;grid-template-columns:max-content 1fr;gap:10px 14px;">
          <dt class="muted">纬度</dt>
          <dd>{{ replayPoint ? replayPoint.latitude : latestLocation.latitude }}</dd>
          <dt class="muted">经度</dt>
          <dd>{{ replayPoint ? replayPoint.longitude : latestLocation.longitude }}</dd>
          <dt class="muted">电量</dt>
          <dd>{{ (replayPoint?.battery ?? latestLocation.battery) }}%</dd>
          <dt class="muted">报警</dt>
          <dd>{{ latestLocation.alarm_type }}</dd>
          <dt class="muted">上报时间</dt>
          <dd>{{ replayPoint ? replayPoint.timestamp : latestLocation.timestamp }}</dd>
        </dl>
        <div v-if="summary" style="margin-top:18px;padding-top:16px;border-top:1px solid var(--line);">
          <h3>轨迹摘要</h3>
          <p>采样点 {{ summary.total_points }}</p>
          <p>报警次数 {{ summary.alarms_detected }}</p>
          <p>最后报警 {{ summary.last_alarm_type ?? '无' }}</p>
        </div>
        <div style="margin-top:18px;padding-top:16px;border-top:1px solid var(--line);">
          <h3>电子围栏状态</h3>
          <p v-if="!fenceEvents.length" class="muted">当前定位点没有可用围栏状态，先创建围栏即可开始检测。</p>
          <article v-for="event in fenceEvents" :key="event.fence_id" style="padding:10px 0;border-top:1px solid var(--line);">
            <strong>{{ event.fence_name }}</strong>
            <p class="muted">
              {{ event.status === 'inside' ? '围栏内' : '围栏外' }} · 距中心 {{ event.distance_meters }} 米
              <span v-if="event.transitioned"> · 本次发生状态切换</span>
            </p>
          </article>
        </div>
      </div>
      <div class="panel" style="min-height: 480px; padding: 24px;">
        <div style="width:100%;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <h2 style="margin:0;">
              {{ showReplay ? '轨迹回放' : '实时位置' }}
            </h2>
            <button v-if="historyPoints.length" class="button-primary" type="button" @click="showReplay = !showReplay">
              {{ showReplay ? '返回实时' : '回放轨迹' }}
            </button>
          </div>
          <CoordinateMap
            :latitude="latitude"
            :longitude="longitude"
            :history="displayHistory"
            :fences="mapFences"
          />
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
    <section class="grid" style="grid-template-columns: 1fr 1fr; margin-top:20px;">
      <div class="panel" style="padding:24px;">
        <h2 style="margin-top:0;">围栏配置</h2>
        <form @submit.prevent="submitFence">
          <input v-model="fenceForm.name" placeholder="围栏名称" style="display:block;width:100%;margin-top:8px;padding:12px;border-radius:14px;border:1px solid var(--line);" />
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px;">
            <input v-model="fenceForm.center_latitude" placeholder="中心纬度" style="padding:12px;border-radius:14px;border:1px solid var(--line);" />
            <input v-model="fenceForm.center_longitude" placeholder="中心经度" style="padding:12px;border-radius:14px;border:1px solid var(--line);" />
          </div>
          <div style="display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center;margin-top:12px;">
            <input v-model="fenceForm.radius_meters" placeholder="半径（米）" style="padding:12px;border-radius:14px;border:1px solid var(--line);" />
            <label class="muted" style="display:flex;gap:8px;align-items:center;">
              <input v-model="fenceForm.is_active" type="checkbox" />
              启用
            </label>
          </div>
          <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:14px;">
            <button class="button-primary" type="submit" :disabled="savingFence">
              {{ savingFence ? '处理中...' : editingFenceId ? '更新围栏' : '创建围栏' }}
            </button>
            <button v-if="editingFenceId" class="button-primary" type="button" style="background:linear-gradient(135deg,#33514b,#1d2f2a);" @click="resetFenceForm">
              取消编辑
            </button>
          </div>
        </form>
        <article v-for="fence in fences" :key="fence.id" style="padding:14px 0;border-top:1px solid var(--line);margin-top:14px;">
          <strong>{{ fence.name }}</strong>
          <p class="muted">
            半径 {{ fence.radius_meters }} 米 · {{ fence.is_active ? '启用中' : '已停用' }} ·
            {{ fence.last_status === 'inside' ? '最近在围栏内' : fence.last_status === 'outside' ? '最近在围栏外' : '待检测' }}
          </p>
          <p class="muted">中心点 {{ fence.center_latitude }}, {{ fence.center_longitude }}</p>
          <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <button class="button-primary" type="button" @click="startEditFence(fence)">编辑</button>
            <button class="button-primary" type="button" style="background:linear-gradient(135deg,#6f2d20,#3c120d);" @click="removeFence(fence)">删除</button>
          </div>
        </article>
      </div>
      <div class="panel" style="padding:24px;">
        <h2 style="margin-top:0;">最近报警</h2>
        <p v-if="!alarms.length" class="muted">暂无报警记录</p>
        <article v-for="alarm in alarms" :key="String(alarm.id)" style="padding:12px 0;border-top:1px solid var(--line);">
          <strong>报警 {{ alarm.alarm_type }}</strong>
          <p class="muted">{{ alarm.message }}</p>
          <p class="muted">{{ alarm.timestamp }}</p>
        </article>
      </div>
      <div class="panel" style="padding:24px;">
        <h2 style="margin-top:0;">通知日志</h2>
        <p v-if="!notifications.length" class="muted">暂无通知记录</p>
        <article v-for="notification in notifications" :key="String(notification.id)" style="padding:12px 0;border-top:1px solid var(--line);">
          <strong>{{ notification.title }}</strong>
          <p class="muted">{{ notification.content }}</p>
          <p class="muted">{{ notification.created_at }} · {{ notification.status }}</p>
        </article>
      </div>
    </section>
  </main>
</template>
