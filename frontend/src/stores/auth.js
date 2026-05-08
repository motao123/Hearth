import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('hearth_token') || '')
  const user = ref(null)
  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    const { data } = await api.post('/api/auth/login', { username, password })
    token.value = data.token
    localStorage.setItem('hearth_token', data.token)
    user.value = data.user || null
  }

  async function register(username, password, name) {
    const { data } = await api.post('/api/auth/register', { username, password, name })
    token.value = data.token
    localStorage.setItem('hearth_token', data.token)
    user.value = data.user || null
  }

  async function logout() {
    try {
      await api.post('/api/auth/logout')
    } catch {
      // ignore
    }
    token.value = ''
    user.value = null
    localStorage.removeItem('hearth_token')
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const { data } = await api.get('/api/auth/me')
      user.value = data
    } catch {
      token.value = ''
      user.value = null
      localStorage.removeItem('hearth_token')
    }
  }

  return { token, user, isAuthenticated, login, register, logout, fetchMe }
})
