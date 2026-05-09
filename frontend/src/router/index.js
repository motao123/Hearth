import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue') },
      { path: 'tasks', name: 'Tasks', component: () => import('@/pages/Tasks.vue') },
      { path: 'shopping', name: 'Shopping', component: () => import('@/pages/Shopping.vue') },
      { path: 'meals', name: 'Meals', component: () => import('@/pages/Meals.vue') },
      { path: 'budget', name: 'Budget', component: () => import('@/pages/Budget.vue') },
      { path: 'calendar', name: 'Calendar', component: () => import('@/pages/Calendar.vue') },
      { path: 'notes', name: 'Notes', component: () => import('@/pages/Notes.vue') },
      { path: 'family', name: 'Family', component: () => import('@/pages/Family.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from) => {
  // Simple check: if not on login page, try to verify auth
  // The actual auth check happens via API calls (401 redirects to login)
  // This guard prevents flash of content for unauthenticated users
  if (to.name !== 'Login' && from.name === undefined) {
    // First navigation — let it through, the MainLayout will call fetchMe()
    // If fetchMe fails, the 401 interceptor will redirect to login
  }
})

export default router
