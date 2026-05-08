import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useShoppingStore = defineStore('shopping', () => {
  const items = ref([])
  const loading = ref(false)

  async function fetchItems() {
    loading.value = true
    try {
      const { data } = await api.get('/api/shopping')
      items.value = Array.isArray(data) ? data : data.items || []
    } finally {
      loading.value = false
    }
  }

  async function addItem(data) {
    const { data: item } = await api.post('/api/shopping', data)
    items.value.push(item)
    return item
  }

  async function toggleItem(id) {
    const item = items.value.find((i) => i.id === id)
    if (!item) return
    const { data: updated } = await api.patch(`/api/shopping/${id}`, { checked: !item.checked })
    const idx = items.value.findIndex((i) => i.id === id)
    if (idx !== -1) items.value[idx] = updated
    return updated
  }

  async function deleteItem(id) {
    await api.delete(`/api/shopping/${id}`)
    items.value = items.value.filter((i) => i.id !== id)
  }

  async function clearChecked() {
    await api.post('/api/shopping/clear-checked')
    items.value = items.value.filter((i) => !i.checked)
  }

  async function importFromMeal(ingredients) {
    const { data } = await api.post('/api/shopping/import', { ingredients })
    await fetchItems()
    return data
  }

  return { items, loading, fetchItems, addItem, toggleItem, deleteItem, clearChecked, importFromMeal }
})
