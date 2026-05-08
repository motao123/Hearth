import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useNotesStore = defineStore('notes', () => {
  const notes = ref([])
  const loading = ref(false)

  async function fetchNotes() {
    loading.value = true
    try {
      const { data } = await api.get('/api/notes')
      notes.value = Array.isArray(data) ? data : data.items || []
    } finally {
      loading.value = false
    }
  }

  async function createNote(data) {
    const { data: note } = await api.post('/api/notes', data)
    notes.value.push(note)
    return note
  }

  async function updateNote(id, data) {
    const { data: updated } = await api.patch(`/api/notes/${id}`, data)
    const idx = notes.value.findIndex((n) => n.id === id)
    if (idx !== -1) notes.value[idx] = updated
    return updated
  }

  async function deleteNote(id) {
    await api.delete(`/api/notes/${id}`)
    notes.value = notes.value.filter((n) => n.id !== id)
  }

  return { notes, loading, fetchNotes, createNote, updateNote, deleteNote }
})
