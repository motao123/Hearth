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

  async function addMember(data) {
    const { data: member } = await api.post('/api/family/members', data)
    members.value.push(member)
    return member
  }

  async function updateMember(id, data) {
    const { data: updated } = await api.patch(`/api/family/members/${id}`, data)
    const idx = members.value.findIndex((m) => m.id === id)
    if (idx !== -1) members.value[idx] = updated
    return updated
  }

  async function deleteMember(id) {
    await api.delete(`/api/family/members/${id}`)
    members.value = members.value.filter((m) => m.id !== id)
  }

  async function fetchPointsRanking() {
    const { data } = await api.get('/api/family/points')
    pointsRanking.value = Array.isArray(data) ? data : data.items || []
  }

  return { members, currentMember, pointsRanking, loading, loadMembers, fetchMembers, addMember, updateMember, deleteMember, fetchPointsRanking }
})
