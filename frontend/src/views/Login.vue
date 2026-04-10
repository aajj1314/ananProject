<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { apiClient } from '@/api/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const errorText = ref('')
const form = reactive({
  phone: '',
  password: '',
})

const submit = async () => {
  loading.value = true
  errorText.value = ''
  try {
    const response = await apiClient.post('/auth/login', form)
    const token = response.data.data.access_token
    authStore.setToken(token)
    localStorage.setItem('access_token', token)
    await router.push('/devices')
  } catch (error) {
    errorText.value = '登录失败，请检查手机号和密码'
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
        <h2>登录</h2>
        <label>
          <span>手机号</span>
          <input v-model="form.phone" maxlength="11" style="display:block;width:100%;margin-top:8px;padding:12px;border-radius:14px;border:1px solid var(--line);" />
        </label>
        <label style="display:block;margin-top:16px;">
          <span>密码</span>
          <input v-model="form.password" type="password" style="display:block;width:100%;margin-top:8px;padding:12px;border-radius:14px;border:1px solid var(--line);" />
        </label>
        <p v-if="errorText" style="color:#8f1f1f;">{{ errorText }}</p>
        <button class="button-primary" type="submit" :disabled="loading">{{ loading ? '登录中...' : '进入平台' }}</button>
      </form>
    </section>
  </main>
</template>
