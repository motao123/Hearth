import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useCalendarStore = defineStore('calendar', () => {
  const events = ref([])
  const loading = ref(false)

  async function fetchEvents(start, end) {
    loading.value = true
    try {
      const { data } = await api.get('/api/calendar/events', { params: { start, end } })
      events.value = Array.isArray(data) ? data : data.items || []
    } finally {
      loading.value = false
    }
  }

  function _mapColor(c) {
    const m = { default: null, blue: '#3B82F6', green: '#22C55E', purple: '#8B5CF6', red: '#EF4444' }
    return m[c] ?? c
  }
  function _toPayload(data) {
    const start = data.date && data.time ? `${data.date}T${data.time}:00` : data.start_time || data.date
    return { ...data, start_time: start, color: _mapColor(data.color) }
  }

  async function createEvent(data) {
    const { data: event } = await api.post('/api/calendar/events', _toPayload(data))
    events.value.push(event)
    return event
  }

  async function updateEvent(id, data) {
    const { data: updated } = await api.patch(`/api/calendar/events/${id}`, _toPayload(data))
    const idx = events.value.findIndex((e) => e.id === id)
    if (idx !== -1) events.value[idx] = updated
    return updated
  }

  async function deleteEvent(id) {
    await api.delete(`/api/calendar/events/${id}`)
    events.value = events.value.filter((e) => e.id !== id)
  }

  async function fetchHolidays(year) {
    const { data } = await api.get('/api/calendar/holidays/cn', { params: { year } })
    return data
  }

  return { events, loading, fetchEvents, createEvent, updateEvent, deleteEvent, fetchHolidays }
})
