<script setup lang="ts">
import { computed, watch } from 'vue'

/**
 * 坐标投影视图组件
 * 用于在没有真实地图SDK的情况下，通过SVG显示设备位置和历史轨迹
 */

interface Props {
  /** 设备当前纬度 */
  latitude: number
  /** 设备当前经度 */
  longitude: number
  /** 历史轨迹点数组 */
  history?: Array<{ latitude: number; longitude: number }>
  /** 电子围栏数组 */
  fences?: Array<{
    center_latitude: number
    center_longitude: number
    radius_meters: number
    name: string
  }>
}

const props = defineProps<Props>()

const plotPoint = computed(() => {
  const x = ((props.longitude + 180) / 360) * 100
  const y = ((90 - props.latitude) / 180) * 100
  return { x, y }
})

const historyPoints = computed(() => {
  if (!props.history || props.history.length === 0) return ''
  return props.history
    .map((item) => `${((item.longitude + 180) / 360) * 100},${((90 - item.latitude) / 180) * 100}`)
    .join(' ')
})

const fenceCircles = computed(() => {
  if (!props.fences) return []
  return props.fences.map((fence) => {
    const cx = ((fence.center_longitude + 180) / 360) * 100
    const cy = ((90 - fence.center_latitude) / 180) * 100
    const r = Math.min(fence.radius_meters / 1000, 15)
    return { cx, cy, r, name: fence.name }
  })
})
</script>

<template>
  <div class="coordinate-map">
    <svg viewBox="0 0 100 100" class="map-svg">
      <defs>
        <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
          <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(27,25,22,0.08)" stroke-width="0.5" />
        </pattern>
      </defs>
      <rect width="100" height="100" fill="url(#grid)" />
      <line x1="0" y1="50" x2="100" y2="50" stroke="rgba(27,25,22,0.18)" />
      <line x1="50" y1="0" x2="50" y2="100" stroke="rgba(27,25,22,0.18)" />

      <circle
        v-for="(fence, index) in fenceCircles"
        :key="index"
        :cx="fence.cx"
        :cy="fence.cy"
        :r="fence.r"
        fill="rgba(182, 84, 43, 0.12)"
        stroke="rgba(182, 84, 43, 0.5)"
        stroke-width="0.6"
      />

      <polyline
        v-if="historyPoints"
        :points="historyPoints"
        fill="none"
        stroke="#7a2a10"
        stroke-width="1.4"
        stroke-linecap="round"
        stroke-linejoin="round"
      />

      <circle :cx="plotPoint.x" :cy="plotPoint.y" r="2.6" fill="#b6542b" />
      <circle :cx="plotPoint.x" :cy="plotPoint.y" r="5" fill="none" stroke="#b6542b" stroke-width="0.6" opacity="0.5" />
    </svg>
    <p class="hint">坐标投影视图 · 接入真实地图 SDK 后将显示完整地图</p>
  </div>
</template>

<style scoped>
.coordinate-map {
  width: 100%;
}

.map-svg {
  width: 100%;
  border-radius: 22px;
  background: rgba(255, 252, 247, 0.7);
  border: 1px solid var(--line);
}

.hint {
  margin: 12px 0 0;
  font-size: 0.92rem;
  color: var(--muted);
}
</style>
