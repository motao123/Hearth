import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)

  async function login(username, password) {
    const { data } = await api.post('/api/auth/login', { username, password })
    user.value = { is_admin: data.is_admin }
    // Fetch full user info after login
    await fetchMe()
  }

  async function register(username, password, name) {
    const { data } = await api.post('/api/auth/register', { username, password, name })
    user.value = { is_admin: data.is_admin }
    await fetchMe()
  }

  async function logout() {
    try {
      await api.post('/api/auth/logout')
    } catch {
      // ignore
    }
    user.value = null
  }

  async function fetchMe() {
    try {
      const { data } = await api.get('/api/auth/me')
      user.value = data
    } catch {
      user.value = null
    }
  }

  return { user, isAuthenticated, login, register, logout, fetchMe }
})
