import { defineStore } from 'pinia'
import { ref } from 'vue'

/** Toast通知类型 */
export type ToastType = 'success' | 'error' | 'info'

/** Toast通知项 */
export interface ToastItem {
  id: number
  type: ToastType
  message: string
}

let nextId = 0

/**
 * Toast通知状态管理Store
 * 管理全局Toast通知的添加和移除
 */
export const useToastStore = defineStore('toast', () => {
  const toasts = ref<ToastItem[]>([])

  /**
   * 添加一条Toast通知
   * @param type - 通知类型: success/error/info
   * @param message - 通知消息内容
   */
  const addToast = (type: ToastType, message: string) => {
    const id = nextId++
    toasts.value.push({ id, type, message })
    setTimeout(() => {
      removeToast(id)
    }, 3000)
  }

  /**
   * 移除指定ID的Toast通知
   * @param id - Toast通知ID
   */
  const removeToast = (id: number) => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return {
    toasts,
    addToast,
    removeToast,
  }
})
