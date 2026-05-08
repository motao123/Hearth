import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref([])
  const loading = ref(false)

  async function fetchTasks(status) {
    loading.value = true
    try {
      const params = {}
      if (status) params.status = status
      const { data } = await api.get('/api/tasks', { params })
      tasks.value = Array.isArray(data) ? data : data.items || []
    } finally {
      loading.value = false
    }
  }

  async function createTask(data) {
    const { data: task } = await api.post('/api/tasks', data)
    tasks.value.push(task)
    return task
  }

  async function updateTask(id, data) {
    const { data: updated } = await api.patch(`/api/tasks/${id}`, data)
    const idx = tasks.value.findIndex((t) => t.id === id)
    if (idx !== -1) tasks.value[idx] = updated
    return updated
  }

  async function deleteTask(id) {
    await api.delete(`/api/tasks/${id}`)
    tasks.value = tasks.value.filter((t) => t.id !== id)
  }

  async function completeTask(id) {
    const { data: updated } = await api.patch(`/api/tasks/${id}`, { status: 'done' })
    const idx = tasks.value.findIndex((t) => t.id === id)
    if (idx !== -1) tasks.value[idx] = updated
    return updated
  }

  return { tasks, loading, fetchTasks, createTask, updateTask, deleteTask, completeTask }
})
