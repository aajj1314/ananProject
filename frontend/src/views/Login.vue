<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { apiClient } from '@/api/api'
import { useAuthStore, type User } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const errorText = ref('')
const isRegisterMode = ref(false)
const form = reactive({
  phone: '',
  password: '',
  nickname: '',
})

const submit = async () => {
  // 表单验证
  if (!form.phone) {
    errorText.value = '请输入手机号'
    return
  }
  if (!form.password) {
    errorText.value = '请输入密码'
    return
  }
  if (isRegisterMode.value && !form.nickname) {
    errorText.value = '请输入昵称'
    return
  }

  loading.value = true
  errorText.value = ''
  try {
    let response
    if (isRegisterMode.value) {
      response = await apiClient.post('/auth/register', {
        phone: form.phone,
        password: form.password,
        nickname: form.nickname || '用户',
      })
    } else {
      response = await apiClient.post('/auth/login', {
        phone: form.phone,
        password: form.password,
      })
    }

    const token = response.data.data.access_token
    authStore.setToken(token)
    localStorage.setItem('access_token', token)

    // Fetch user profile
    const profileResponse = await apiClient.get('/auth/profile')
    authStore.setUser(profileResponse.data.data as User)

    // Redirect to admin if admin, else devices
    if (authStore.isAdmin) {
      await router.push('/admin')
    } else {
      await router.push('/devices')
    }
  } catch (error: any) {
    errorText.value = isRegisterMode.value 
      ? error.response?.data?.message || '注册失败，请重试' 
      : '登录失败，请检查手机号和密码'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="shell">
    <section class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center min-h-[80vh]">
      <div class="text-center md:text-left">
        <h1 class="hero-title">老人防丢鞋垫 管理系统</h1>
        <p class="muted mb-6">以设备、轨迹与报警为核心的陪护平台，为老人安全保驾护航</p>
        <div class="flex flex-col gap-4 mt-8">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-success flex items-center justify-center text-white">
              <span>📱</span>
            </div>
            <span>实时位置追踪</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-warning flex items-center justify-center text-white">
              <span>🚧</span>
            </div>
            <span>电子围栏保护</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-danger flex items-center justify-center text-white">
              <span>🔔</span>
            </div>
            <span>多渠道报警通知</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-info flex items-center justify-center text-white">
              <span>🎛️</span>
            </div>
            <span>智能管理仪表板</span>
          </div>
        </div>
      </div>
      <div class="card">
        <h2 class="text-center text-2xl font-bold mb-6">{{ isRegisterMode ? '注册账号' : '用户登录' }}</h2>
        
        <div v-if="errorText" class="alert alert-danger mb-4">
          {{ errorText }}
        </div>
        
        <form @submit.prevent="submit">
          <div class="form-group">
            <label class="form-label" for="phone">手机号</label>
            <input 
              id="phone" 
              v-model="form.phone" 
              type="tel" 
              maxlength="11" 
              class="form-control"
              placeholder="请输入手机号码"
            />
          </div>
          
          <div v-if="isRegisterMode" class="form-group">
            <label class="form-label" for="nickname">昵称</label>
            <input 
              id="nickname" 
              v-model="form.nickname" 
              class="form-control"
              placeholder="请输入昵称"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label" for="password">密码</label>
            <input 
              id="password" 
              v-model="form.password" 
              type="password" 
              class="form-control"
              placeholder="请输入密码"
            />
          </div>
          
          <div class="flex gap-4 mt-6">
            <button 
              class="button-primary flex-1" 
              type="submit" 
              :disabled="loading"
            >
              <span v-if="loading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                处理中...
              </span>
              <span v-else>{{ isRegisterMode ? '注册' : '登录' }}</span>
            </button>
            <button 
              class="button-secondary flex-1" 
              type="button" 
              @click="isRegisterMode = !isRegisterMode"
            >
              {{ isRegisterMode ? '返回登录' : '注册账号' }}
            </button>
          </div>
        </form>
      </div>
    </section>
  </main>
</template>

<style scoped>
/* 添加响应式设计 */
@media (max-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  .min-h-\[80vh\] {
    min-height: auto;
  }
}

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
</style>
