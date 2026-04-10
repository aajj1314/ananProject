<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { apiClient } from '@/api/api'

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
const savingDeviceId = ref('')
const form = reactive({
  device_id: '',
  device_name: '',
})

const loadDevices = async () => {
  try {
    const response = await apiClient.get('/device')
    devices.value = response.data.data
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
  } catch (error) {
    errorText.value = '设备列表加载失败'
  }
}

const createDevice = async () => {
  savingDeviceId.value = 'create'
  errorText.value = ''
  try {
    await apiClient.post('/device', form)
    form.device_id = ''
    form.device_name = ''
    await loadDevices()
  } catch (error) {
    errorText.value = '新设备绑定失败'
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
  try {
    await apiClient.put(`/device/${device.device_id}`, { device_name: nextName })
    await loadDevices()
  } catch (error) {
    errorText.value = '设备更新失败'
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
  try {
    await apiClient.delete(`/device/${device.device_id}`)
    await loadDevices()
  } catch (error) {
    errorText.value = '设备解绑失败'
  } finally {
    savingDeviceId.value = ''
  }
}

onMounted(() => {
  loadDevices()
})
</script>

<template>
  <main class="shell">
    <section class="grid" style="grid-template-columns: 1.2fr 0.8fr; align-items:start;">
      <div class="panel" style="padding: 28px;">
        <p class="muted">Device Center</p>
        <h1 class="hero-title" style="font-size: clamp(2.4rem, 6vw, 4.6rem);">设备与轨迹概览</h1>
        <p class="muted">第四阶段已开始接入电子围栏能力。设备列表继续负责绑定管理，围栏与轨迹详情统一放在地图页处理。</p>
      </div>
      <div class="panel" style="padding: 24px;">
        <h2>绑定新设备</h2>
        <form @submit.prevent="createDevice">
          <input v-model="form.device_id" maxlength="15" placeholder="15位 IMEI" style="display:block;width:100%;margin-top:8px;padding:12px;border-radius:14px;border:1px solid var(--line);" />
          <input v-model="form.device_name" placeholder="设备名称" style="display:block;width:100%;margin-top:12px;padding:12px;border-radius:14px;border:1px solid var(--line);" />
          <button class="button-primary" type="submit" style="margin-top:14px;" :disabled="savingDeviceId === 'create'">
            {{ savingDeviceId === 'create' ? '处理中...' : '绑定设备' }}
          </button>
        </form>
      </div>
    </section>
    <section style="margin-top: 20px;">
      <p v-if="errorText" style="color:#8f1f1f;">{{ errorText }}</p>
      <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));">
        <article v-for="device in devices" :key="device.device_id" class="panel" style="padding: 22px;">
          <p class="muted">IMEI {{ device.device_id }}</p>
          <h3>{{ device.device_name }}</h3>
          <p>电量 {{ device.battery }}%</p>
          <p>报警 {{ latestAlarms[device.device_id]?.alarm_type ?? 0 }}</p>
          <p class="muted">最后上报 {{ device.last_updated || '暂无数据' }}</p>
          <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <router-link class="button-primary" :to="`/map/${device.device_id}`">查看地图</router-link>
            <button class="button-primary" type="button" @click="renameDevice(device)" :disabled="savingDeviceId === device.device_id">重命名</button>
            <button class="button-primary" type="button" @click="removeDevice(device)" :disabled="savingDeviceId === device.device_id" style="background:linear-gradient(135deg,#6f2d20,#3c120d);">解绑</button>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>
