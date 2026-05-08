import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useBudgetStore = defineStore('budget', () => {
  const entries = ref([])
  const summary = ref({ income: 0, expense: 0, balance: 0 })
  const loading = ref(false)

  async function fetchEntries(year, month) {
    loading.value = true
    try {
      const { data } = await api.get('/api/budget/entries', { params: { year, month } })
      entries.value = Array.isArray(data) ? data : data.items || []
    } finally {
      loading.value = false
    }
  }

  async function addEntry(data) {
    const { data: entry } = await api.post('/api/budget/entries', data)
    entries.value.push(entry)
    return entry
  }

  async function fetchSummary(year, month) {
    const { data } = await api.get('/api/budget/summary', { params: { year, month } })
    summary.value = data
  }

  async function fetchHongbao() {
    const { data } = await api.get('/api/budget/hongbao')
    return data
  }

  return { entries, summary, loading, fetchEntries, addEntry, fetchSummary, fetchHongbao }
})
