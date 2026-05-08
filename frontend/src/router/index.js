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

router.beforeEach((to) => {
  const token = localStorage.getItem('hearth_token')
  if (to.name !== 'Login' && !token) return { name: 'Login' }
})

export default router
