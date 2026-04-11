<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { MapPin, Shield, Bell, Eye, EyeOff, Loader2 } from 'lucide-vue-next'

import { apiClient } from '@/api/api'
import { useAuthStore, type User } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const isRegisterMode = ref(false)
const showPassword = ref(false)
const form = reactive({
  phone: '',
  password: '',
  nickname: '',
})

/** 表单验证错误信息 */
const phoneError = computed(() => {
  if (!form.phone) return ''
  if (!/^1\d{10}$/.test(form.phone)) return '请输入有效的11位手机号'
  return ''
})

const passwordError = computed(() => {
  if (!form.password) return ''
  if (form.password.length < 6) return '密码至少6位'
  return ''
})

const nicknameError = computed(() => {
  if (!isRegisterMode.value) return ''
  if (form.nickname && form.nickname.length > 20) return '昵称最多20个字符'
  return ''
})

/** 是否有表单验证错误 */
const hasValidationError = computed(() => {
  if (isRegisterMode.value) {
    return !form.phone || !form.password || !form.nickname || !!phoneError.value || !!passwordError.value || !!nicknameError.value
  }
  return !form.phone || !form.password || !!phoneError.value || !!passwordError.value
})

const submit = async () => {
  // 表单验证
  if (!form.phone) {
    return
  }
  if (!form.password) {
    return
  }
  if (isRegisterMode.value && !form.nickname) {
    return
  }
  if (hasValidationError.value) {
    return
  }

  loading.value = true
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
    // 错误通过表单内联显示，不再使用alert
    console.error(isRegisterMode.value ? '注册失败' : '登录失败', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="shell">
    <section class="login-layout">
      <div class="login-hero">
        <h1 class="hero-title">老人防丢鞋垫 管理系统</h1>
        <p class="muted mb-6">以设备、轨迹与报警为核心的陪护平台，为老人安全保驾护航</p>
        <div class="flex flex-col gap-4 mt-8">
          <div class="feature-item">
            <div class="feature-icon feature-icon--success">
              <MapPin :size="20" />
            </div>
            <span>实时位置追踪</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon feature-icon--warning">
              <Shield :size="20" />
            </div>
            <span>电子围栏保护</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon feature-icon--danger">
              <Bell :size="20" />
            </div>
            <span>多渠道报警通知</span>
          </div>
        </div>
      </div>
      <div class="card login-card">
        <h2 class="text-center text-2xl font-bold mb-6">{{ isRegisterMode ? '注册账号' : '用户登录' }}</h2>

        <form @submit.prevent="submit">
          <div class="form-group">
            <label class="form-label" for="phone">手机号</label>
            <input
              id="phone"
              v-model="form.phone"
              type="tel"
              maxlength="11"
              class="form-control"
              :class="{ 'is-error': phoneError }"
              placeholder="请输入手机号码"
            />
            <p v-if="phoneError" class="form-error">{{ phoneError }}</p>
          </div>

          <div v-if="isRegisterMode" class="form-group">
            <label class="form-label" for="nickname">昵称</label>
            <input
              id="nickname"
              v-model="form.nickname"
              class="form-control"
              :class="{ 'is-error': nicknameError }"
              placeholder="请输入昵称"
            />
            <p v-if="nicknameError" class="form-error">{{ nicknameError }}</p>
          </div>

          <div class="form-group">
            <label class="form-label" for="password">密码</label>
            <div class="password-wrapper">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="form-control password-input"
                :class="{ 'is-error': passwordError }"
                placeholder="请输入密码"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
                aria-label="切换密码可见性"
              >
                <EyeOff v-if="showPassword" :size="18" />
                <Eye v-else :size="18" />
              </button>
            </div>
            <p v-if="passwordError" class="form-error">{{ passwordError }}</p>
          </div>

          <button
            class="button-primary w-full"
            type="submit"
            :disabled="loading || hasValidationError"
            style="width: 100%"
          >
            <span v-if="loading" class="flex items-center justify-center">
              <Loader2 class="animate-spin" :size="18" style="margin-right: 8px" />
              处理中...
            </span>
            <span v-else>{{ isRegisterMode ? '注册' : '登录' }}</span>
          </button>
        </form>

        <div class="login-switch">
          <span class="muted">{{ isRegisterMode ? '已有账号？' : '还没有账号？' }}</span>
          <a href="#" @click.prevent="isRegisterMode = !isRegisterMode">
            {{ isRegisterMode ? '返回登录' : '注册账号' }}
          </a>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.login-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
  min-height: 80vh;
}

.login-hero {
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.feature-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.feature-icon--success {
  background: var(--success);
}

.feature-icon--warning {
  background: var(--warning);
}

.feature-icon--danger {
  background: var(--danger);
}

.login-card {
  max-width: 420px;
  margin: 0 auto;
}

.password-wrapper {
  position: relative;
}

.password-input {
  padding-right: 44px;
}

.password-toggle {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--ink-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
  padding: 0;
  transition: color var(--transition-fast);
}

.password-toggle:hover {
  color: var(--ink);
  opacity: 1;
}

.login-switch {
  text-align: center;
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px solid var(--line);
}

.w-full {
  width: 100%;
}

@media (max-width: 768px) {
  .login-layout {
    grid-template-columns: 1fr;
    min-height: auto;
    gap: 24px;
  }

  .login-hero {
    text-align: center;
  }
}
</style>
