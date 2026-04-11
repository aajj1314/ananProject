<script setup lang="ts">
import { CheckCircle, XCircle, Info, X } from 'lucide-vue-next'

import { useToastStore, type ToastType } from '@/stores/toast'

const toastStore = useToastStore()

/** 根据Toast类型获取对应的图标组件 */
const iconMap: Record<ToastType, typeof CheckCircle> = {
  success: CheckCircle,
  error: XCircle,
  info: Info,
}

/** 根据Toast类型获取对应的CSS类名 */
const typeClassMap: Record<ToastType, string> = {
  success: 'toast--success',
  error: 'toast--error',
  info: 'toast--info',
}
</script>

<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          class="toast"
          :class="typeClassMap[toast.type]"
        >
          <component :is="iconMap[toast.type]" class="toast-icon" :size="18" />
          <span class="toast-message">{{ toast.message }}</span>
          <button class="toast-close" @click="toastStore.removeToast(toast.id)">
            <X :size="14" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  min-width: 280px;
  max-width: 420px;
  pointer-events: auto;
  font-size: 0.9rem;
  line-height: 1.4;
}

.toast--success {
  background: var(--bg-elevated);
  border: 1px solid var(--color-success-100);
  color: var(--success);
}

.toast--error {
  background: var(--bg-elevated);
  border: 1px solid var(--color-danger-100);
  color: var(--danger);
}

.toast--info {
  background: var(--bg-elevated);
  border: 1px solid var(--color-info-100);
  color: var(--info);
}

.toast-icon {
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  color: var(--ink);
}

.toast-close {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--ink-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
  padding: 0;
  transition: background var(--transition-fast);
}

.toast-close:hover {
  background: var(--bg-sunken);
  opacity: 1;
}

/* Toast进入/离开动画 */
.toast-enter-active {
  transition: all var(--transition-spring);
}

.toast-leave-active {
  transition: all var(--transition-fast);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform var(--transition-normal);
}

@media (max-width: 480px) {
  .toast-container {
    left: 12px;
    right: 12px;
  }

  .toast {
    min-width: auto;
    max-width: none;
  }
}
</style>
