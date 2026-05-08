<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shrink-0 z-30">
      <div class="flex items-center gap-3">
        <button @click="sidebarOpen = !sidebarOpen" class="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
        <div class="flex items-center gap-2">
          <span class="text-xl">🏠</span>
          <span class="text-lg font-bold text-gray-900">Hearth</span>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <div v-if="authStore.user" class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center text-sm font-medium text-orange-600">
            {{ authStore.user.name?.charAt(0) || '?' }}
          </div>
          <span class="text-sm text-gray-700 hidden sm:block">{{ authStore.user.name }}</span>
        </div>
        <button @click="handleLogout" class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="退出登录">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
        </button>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar Overlay (mobile) -->
      <Transition name="fade">
        <div v-if="sidebarOpen" class="fixed inset-0 bg-black/50 z-20 lg:hidden" @click="sidebarOpen = false"></div>
      </Transition>

      <!-- Sidebar -->
      <nav
        :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
        class="fixed lg:static inset-y-0 left-0 z-20 w-60 bg-[#1A1A2E] text-white flex flex-col transition-transform duration-200 ease-in-out lg:transition-none pt-16 lg:pt-0"
      >
        <div class="p-4 border-b border-white/10 lg:hidden">
          <span class="text-xl">🏠</span>
          <span class="text-lg font-bold ml-2">Hearth</span>
        </div>
        <div class="flex-1 py-2 overflow-y-auto">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-4 py-3 text-sm transition-colors hover:bg-white/10"
            :class="isActive(item.path) ? 'bg-white/15 text-white font-medium border-r-3 border-orange-500' : 'text-gray-300'"
            @click="sidebarOpen = false"
          >
            <span class="text-lg w-6 text-center">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </router-link>
        </div>
        <div class="p-4 border-t border-white/10">
          <div class="text-xs text-gray-400 text-center">Hearth v0.1</div>
        </div>
      </nav>

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 pb-20 lg:pb-6">
        <router-view />
      </main>
    </div>

    <!-- Mobile Bottom Navigation -->
    <nav class="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-30 safe-area-bottom">
      <div class="flex items-center justify-around py-1">
        <router-link
          v-for="item in bottomNavItems"
          :key="item.path"
          :to="item.path"
          class="flex flex-col items-center py-1.5 px-3 text-xs transition-colors"
          :class="isActive(item.path) ? 'text-orange-600' : 'text-gray-400'"
        >
          <span class="text-lg">{{ item.icon }}</span>
          <span class="mt-0.5">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFamilyStore } from '@/stores/family'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const familyStore = useFamilyStore()

const sidebarOpen = ref(false)

const navItems = [
  { path: '/', icon: '📊', label: '总览' },
  { path: '/tasks', icon: '✅', label: '任务' },
  { path: '/shopping', icon: '🛒', label: '购物' },
  { path: '/meals', icon: '🍳', label: '餐食' },
  { path: '/budget', icon: '💰', label: '预算' },
  { path: '/calendar', icon: '📅', label: '日历' },
  { path: '/notes', icon: '📝', label: '便签' },
  { path: '/family', icon: '👨‍👩‍👧‍👦', label: '家庭' },
]

const bottomNavItems = [
  { path: '/', icon: '📊', label: '总览' },
  { path: '/tasks', icon: '✅', label: '任务' },
  { path: '/shopping', icon: '🛒', label: '购物' },
  { path: '/meals', icon: '🍳', label: '餐食' },
  { path: '/budget', icon: '💰', label: '预算' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  await Promise.allSettled([authStore.fetchMe(), familyStore.loadMembers()])
})
</script>

<style scoped>
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom, 0);
}
.border-r-3 {
  border-right-width: 3px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
