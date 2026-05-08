import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useFamilyStore = defineStore('family', () => {
  const members = ref([])
  const currentMember = ref(null)
  const pointsRanking = ref([])
  const loading = ref(false)

  async function loadMembers() {
    loading.value = true
    try {
      const { data } = await api.get('/api/family/members')
      members.value = Array.isArray(data) ? data : data.items || []
    } finally {
      loading.value = false
    }
  }

  async function fetchMembers() {
    return loadMembers()
  }

  async function updateMember(id, data) {
    const { data: updated } = await api.patch(`/api/family/members/${id}`, data)
    const idx = members.value.findIndex((m) => m.id === id)
    if (idx !== -1) members.value[idx] = updated
    return updated
  }

  async function fetchPointsRanking() {
    const { data } = await api.get('/api/family/points')
    pointsRanking.value = Array.isArray(data) ? data : data.items || []
  }

  return { members, currentMember, pointsRanking, loading, loadMembers, fetchMembers, updateMember, fetchPointsRanking }
})
