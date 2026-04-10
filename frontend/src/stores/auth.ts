import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface User {
  id: number
  phone: string
  nickname: string
  role: 'user' | 'admin'
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>('')
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const setToken = (value: string) => {
    token.value = value
  }

  const setUser = (value: User | null) => {
    user.value = value
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    setToken,
    setUser,
    logout,
  }
})
