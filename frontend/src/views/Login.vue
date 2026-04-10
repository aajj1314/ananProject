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
  } catch (error) {
    errorText.value = isRegisterMode.value ? '注册失败，请重试' : '登录失败，请检查手机号和密码'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="shell">
    <section class="panel grid" style="padding: 28px; grid-template-columns: 1.15fr 0.85fr;">
      <div>
        <p class="muted">Elderly Insole Platform</p>
        <h1 class="hero-title">老人防丢鞋垫 管理中枢</h1>
        <p class="muted">以设备、轨迹与报警为核心的陪护平台。当前阶段先交付稳定、清晰、可继续迭代的业务壳。</p>
      </div>
      <form class="panel" style="padding: 24px;" @submit.prevent="submit">
        <h2>{{ isRegisterMode ? '注册' : '登录' }}</h2>
        <label>
          <span>手机号</span>
          <input v-model="form.phone" maxlength="11" style="display:block;width:100%;margin-top:8px;padding:12px;border-radius:14px;border:1px solid var(--line);" />
        </label>
        <label v-if="isRegisterMode" style="display:block;margin-top:12px;">
          <span>昵称</span>
          <input v-model="form.nickname" style="display:block;width:100%;margin-top:8px;padding:12px;border-radius:14px;border:1px solid var(--line);" />
        </label>
        <label style="display:block;margin-top:12px;">
          <span>密码</span>
          <input v-model="form.password" type="password" style="display:block;width:100%;margin-top:8px;padding:12px;border-radius:14px;border:1px solid var(--line);" />
        </label>
        <p v-if="errorText" style="color:#8f1f1f;">{{ errorText }}</p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:16px;">
          <button class="button-primary" type="submit" :disabled="loading">
            {{ loading ? '处理中...' : isRegisterMode ? '注册' : '进入平台' }}
          </button>
          <button class="button-primary" type="button" style="background:linear-gradient(135deg,#33514b,#1d2f2a);" @click="isRegisterMode = !isRegisterMode">
            {{ isRegisterMode ? '返回登录' : '注册账号' }}
          </button>
        </div>
      </form>
    </section>
  </main>
</template>
