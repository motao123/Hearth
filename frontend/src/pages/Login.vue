<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900">🏠 Hearth</h1>
        <p class="text-gray-500 mt-2">你的家庭生活管理中心</p>
      </div>

      <div class="bg-white rounded-2xl shadow-lg p-6">
        <!-- Tab Switch -->
        <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button
            @click="mode = 'login'"
            :class="mode === 'login' ? 'bg-white shadow text-gray-900' : 'text-gray-500'"
            class="flex-1 py-2 rounded-md text-sm font-medium transition-all"
          >
            登录
          </button>
          <button
            @click="mode = 'register'"
            :class="mode === 'register' ? 'bg-white shadow text-gray-900' : 'text-gray-500'"
            class="flex-1 py-2 rounded-md text-sm font-medium transition-all"
          >
            注册
          </button>
        </div>

        <!-- Login Form -->
        <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              v-model="loginForm.username"
              type="text"
              required
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入用户名"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              v-model="loginForm.password"
              type="password"
              required
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入密码"
            />
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-2.5 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="loading">登录中...</span>
            <span v-else>登录</span>
          </button>
        </form>

        <!-- Register Form -->
        <form v-else @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓名</label>
            <input
              v-model="registerForm.name"
              type="text"
              required
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入姓名"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              v-model="registerForm.username"
              type="text"
              required
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入用户名"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              v-model="registerForm.password"
              type="password"
              required
              minlength="8"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all"
              placeholder="请输入密码（至少8位，含字母和数字）"
            />
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-2.5 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="loading">注册中...</span>
            <span v-else>注册</span>
          </button>
        </form>

        <!-- Error Message -->
        <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg text-center">
          {{ error }}
        </div>

        <!-- Success Message -->
        <div v-if="success" class="mt-4 p-3 bg-green-50 text-green-600 text-sm rounded-lg text-center">
          {{ success }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

if (authStore.isAuthenticated) {
  router.push('/')
}

const mode = ref('login')
const loading = ref(false)
const error = ref('')
const success = ref('')

const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', name: '' })

async function handleLogin() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await authStore.login(loginForm.value.username, loginForm.value.password)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await authStore.register(registerForm.value.username, registerForm.value.password, registerForm.value.name)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
