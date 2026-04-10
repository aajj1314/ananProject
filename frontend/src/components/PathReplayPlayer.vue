<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'

interface LocationPoint {
  latitude: number
  longitude: number
  timestamp: string
  battery?: number
  speed?: number
}

interface Props {
  points: LocationPoint[]
  autoplay?: boolean
  speed?: number
}

const props = withDefaults(defineProps<Props>(), {
  autoplay: false,
  speed: 1,
})

const emit = defineEmits<{
  (e: 'pointChange', point: LocationPoint | null, index: number): void
  (e: 'playStateChange', playing: boolean): void
}>()

const currentIndex = ref(-1)
const isPlaying = ref(false)
const playbackSpeed = ref(props.speed)
let animationFrameId: number | null = null
let lastTimestamp = 0

const progress = computed(() => {
  if (props.points.length === 0) return 0
  return Math.max(0, Math.min(100, ((currentIndex.value + 1) / props.points.length) * 100))
})

const currentPoint = computed(() => {
  if (currentIndex.value < 0 || currentIndex.value >= props.points.length) {
    return null
  }
  return props.points[currentIndex.value]
})

const displayPoints = computed(() => {
  if (currentIndex.value < 0) return []
  return props.points.slice(0, currentIndex.value + 1)
})

const play = () => {
  if (props.points.length === 0) return
  if (currentIndex.value >= props.points.length - 1) {
    currentIndex.value = -1
  }
  isPlaying.value = true
  emit('playStateChange', true)
  lastTimestamp = performance.now()
  tick()
}

const pause = () => {
  isPlaying.value = false
  emit('playStateChange', false)
  if (animationFrameId !== null) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}

const reset = () => {
  pause()
  currentIndex.value = -1
  emit('pointChange', null, -1)
}

const seek = (index: number) => {
  currentIndex.value = Math.max(-1, Math.min(props.points.length - 1, index))
  if (currentIndex.value >= 0) {
    emit('pointChange', props.points[currentIndex.value], currentIndex.value)
  }
}

const tick = () => {
  if (!isPlaying.value) return

  const now = performance.now()
  const delta = now - lastTimestamp
  lastTimestamp = now

  const advance = Math.max(1, Math.round((delta / 1000) * 10 * playbackSpeed.value))
  const nextIndex = currentIndex.value + advance

  if (nextIndex >= props.points.length) {
    currentIndex.value = props.points.length - 1
    emit('pointChange', props.points[currentIndex.value], currentIndex.value)
    isPlaying.value = false
    emit('playStateChange', false)
    return
  }

  currentIndex.value = nextIndex
  emit('pointChange', props.points[currentIndex.value], currentIndex.value)

  animationFrameId = requestAnimationFrame(tick)
}

watch(
  () => props.autoplay,
  (val) => {
    if (val && !isPlaying.value) {
      play()
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  pause()
})
</script>

<template>
  <div class="replay-player">
    <div class="progress-bar">
      <div class="progress-track" @click.stop>
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        <input
          class="progress-input"
          type="range"
          min="-1"
          :max="points.length - 1"
          :value="currentIndex"
          @input="seek(Number((<HTMLInputElement>$event.target).value))"
        />
      </div>
    </div>
    <div class="controls">
      <div class="stats">
        <span v-if="currentPoint">
          {{ currentPoint.timestamp }} · 电量 {{ currentPoint.battery ?? 'N/A' }}%
        </span>
        <span v-else>等待回放...</span>
      </div>
      <div class="buttons">
        <button class="control-button" type="button" @click="reset" :disabled="points.length === 0">
          重置
        </button>
        <button v-if="!isPlaying" class="control-button primary" type="button" @click="play" :disabled="points.length === 0">
          播放
        </button>
        <button v-else class="control-button primary" type="button" @click="pause">
          暂停
        </button>
        <select class="speed-select" :value="playbackSpeed" @change="playbackSpeed = Number((<HTMLSelectElement>$event.target).value)">
          <option :value="0.5">0.5x</option>
          <option :value="1">1x</option>
          <option :value="2">2x</option>
          <option :value="5">5x</option>
        </select>
      </div>
    </div>
  </div>
</template>

<style scoped>
.replay-player {
  padding: 16px 0;
}

.progress-bar {
  position: relative;
  margin-bottom: 12px;
}

.progress-track {
  position: relative;
  height: 12px;
  background: rgba(27, 25, 22, 0.08);
  border-radius: 999px;
  overflow: visible;
}

.progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
  border-radius: 999px;
  transition: width 60ms linear;
}

.progress-input {
  position: absolute;
  top: -4px;
  left: 0;
  width: 100%;
  height: 20px;
  opacity: 0;
  cursor: pointer;
  margin: 0;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.stats {
  font-size: 0.95rem;
  color: var(--muted);
}

.buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.control-button {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 252, 247, 0.6);
  color: var(--ink);
  padding: 0.6rem 1rem;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background 150ms ease;
}

.control-button:hover:not(:disabled) {
  background: rgba(255, 252, 247, 0.9);
}

.control-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-button.primary {
  border: 0;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
  color: #fff8f2;
}

.speed-select {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 252, 247, 0.6);
  color: var(--ink);
  padding: 0.55rem 0.9rem;
  font-size: 0.9rem;
  cursor: pointer;
}
</style>
