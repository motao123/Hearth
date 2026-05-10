<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <h1 class="text-2xl font-bold text-gray-900">日历</h1>
      <div class="flex items-center gap-2">
        <button @click="prevMonth" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <span class="text-sm font-medium text-gray-700 min-w-[100px] text-center">{{ monthLabel }}</span>
        <button @click="nextMonth" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </button>
        <button @click="goToday" class="px-3 py-2 text-sm text-orange-600 hover:bg-orange-50 rounded-lg transition-colors font-medium">今天</button>
        <button @click="openAddEvent(todayStr)" class="inline-flex items-center gap-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium whitespace-nowrap">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          添加事件
        </button>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <!-- Weekday Headers -->
      <div class="grid grid-cols-7 border-b border-gray-100">
        <div v-for="day in weekdays" :key="day" class="p-2 text-center text-xs font-medium text-gray-500 border-r border-gray-50 last:border-r-0">
          {{ day }}
        </div>
      </div>

      <!-- Day Cells -->
      <div class="grid grid-cols-7">
        <div
          v-for="(cell, idx) in calendarCells"
          :key="idx"
          class="min-h-[80px] sm:min-h-[100px] p-1.5 border-b border-r border-gray-50 last:border-r-0 cursor-pointer hover:bg-gray-50 transition-colors"
          :class="{ 'bg-gray-50/50': !cell.currentMonth }"
          @click="openAddEvent(cell.date)"
        >
          <div class="flex items-center justify-between mb-1">
            <span
              class="text-sm w-7 h-7 flex items-center justify-center rounded-full"
              :class="{
                'bg-orange-600 text-white': cell.isToday,
                'text-gray-900 font-semibold': cell.currentMonth && !cell.isToday,
                'text-gray-300': !cell.currentMonth,
              }"
            >
              {{ cell.day }}
            </span>
            <span v-if="cell.lunar" class="text-xs text-gray-400 hidden sm:block">{{ cell.lunar }}</span>
          </div>
          <!-- Holiday -->
          <div v-if="cell.holiday" class="text-xs text-red-500 font-medium mb-0.5 truncate">{{ cell.holiday }}</div>
          <!-- Events -->
          <div class="space-y-0.5">
            <div
              v-for="event in getEventsForDate(cell.date)"
              :key="event.id"
              class="text-xs px-1.5 py-0.5 rounded truncate cursor-pointer"
              :class="event.color === 'holiday' ? 'bg-red-50 text-red-600' : 'bg-orange-50 text-orange-700'"
              @click.stop="openEventDetail(event)"
            >
              {{ event.title }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Event Modal -->
    <Modal :show="showAddModal" :title="editingEvent ? '编辑事件' : '添加事件'" @close="closeModal">
      <form @submit.prevent="handleSave" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">标题 *</label>
          <input v-model="form.title" type="text" required class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="事件标题" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">日期 *</label>
            <input v-model="form.date" type="date" required class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">时间</label>
            <input v-model="form.time" type="time" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
          <textarea v-model="form.description" rows="2" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="事件描述"></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">颜色</label>
          <div class="flex gap-2">
            <button v-for="c in colorOptions" :key="c.value" type="button" @click="form.color = c.value" class="w-8 h-8 rounded-full border-2 transition-all" :class="form.color === c.value ? 'border-gray-900 scale-110' : 'border-transparent'" :style="{ backgroundColor: c.bg }" :title="c.label"></button>
          </div>
        </div>
        <div class="flex gap-3">
          <button type="submit" :disabled="saving" class="flex-1 py-2.5 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 transition-colors">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <button v-if="editingEvent" type="button" @click="handleDelete" class="px-4 py-2.5 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors">
            删除
          </button>
        </div>
      </form>
    </Modal>

    <!-- Event Detail Modal -->
    <Modal :show="showDetailModal" :title="detailEvent?.title || ''" @close="showDetailModal = false">
      <div v-if="detailEvent" class="space-y-3">
        <div class="flex items-center gap-2 text-sm text-gray-600">
          <span>📅</span>
          <span>{{ formatDate(detailEvent.start_time || detailEvent.date) }}</span>
          <span v-if="detailEvent.time || (detailEvent.start_time && detailEvent.start_time.length >= 16)">{{ detailEvent.time || detailEvent.start_time.substring(11, 16) }}</span>
        </div>
        <div v-if="detailEvent.description" class="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">{{ detailEvent.description }}</div>
        <div class="flex gap-3 pt-2">
          <button @click="openEditFromDetail" class="flex-1 py-2 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 transition-colors text-sm">编辑</button>
          <button @click="deleteFromDetail" class="px-4 py-2 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors text-sm">删除</button>
        </div>
      </div>
    </Modal>

    <ConfirmDialog :show="showConfirm" :message="confirmMessage" @confirm="confirmAction" @cancel="showConfirm = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { useCalendarStore } from '@/stores/calendar'
import Modal from '@/components/Modal.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { Solar } from 'lunar-javascript'

const calendarStore = useCalendarStore()

const currentMonth = ref(dayjs())
const showAddModal = ref(false)
const showDetailModal = ref(false)
const showConfirm = ref(false)
const confirmMessage = ref('')
const editingEvent = ref(null)
const detailEvent = ref(null)
const saving = ref(false)
const holidays = ref({})
let pendingConfirmAction = null

const todayStr = dayjs().format('YYYY-MM-DD')
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const colorOptions = [
  { value: 'default', label: '默认', bg: '#FED7AA' },
  { value: 'blue', label: '蓝色', bg: '#BFDBFE' },
  { value: 'green', label: '绿色', bg: '#BBF7D0' },
  { value: 'purple', label: '紫色', bg: '#DDD6FE' },
  { value: 'red', label: '红色', bg: '#FECACA' },
]

const form = ref({ title: '', date: '', time: '', description: '', color: 'default' })

const monthLabel = computed(() => currentMonth.value.format('YYYY年M月'))

const calendarCells = computed(() => {
  const start = currentMonth.value.startOf('month')
  const startDay = start.day() === 0 ? 6 : start.day() - 1 // Monday as first day
  const daysInMonth = currentMonth.value.daysInMonth()
  const today = dayjs().format('YYYY-MM-DD')
  const cells = []

  // Previous month days
  for (let i = startDay - 1; i >= 0; i--) {
    const d = start.subtract(i + 1, 'day')
    cells.push({ date: d.format('YYYY-MM-DD'), day: d.format('D'), currentMonth: false, isToday: false, lunar: '', holiday: '' })
  }

  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    const d = currentMonth.value.date(i)
    const dateStr = d.format('YYYY-MM-DD')
    cells.push({
      date: dateStr,
      day: String(i),
      currentMonth: true,
      isToday: dateStr === today,
      lunar: getLunarDate(d),
      holiday: holidays.value[dateStr] || '',
    })
  }

  // Next month days to fill grid
  const remaining = 42 - cells.length
  for (let i = 1; i <= remaining; i++) {
    const d = currentMonth.value.add(1, 'month').date(i)
    cells.push({ date: d.format('YYYY-MM-DD'), day: String(i), currentMonth: false, isToday: false, lunar: '', holiday: '' })
  }

  return cells
})

function getLunarDate(d) {
  try {
    const solar = Solar.fromDate(d.toDate())
    const lunar = solar.getLunar()
    const lunarDay = lunar.getDayInChinese()
    const lunarMonth = lunar.getMonthInChinese()
    // Show month name on day 1, otherwise show day
    if (lunar.getDay() === 1) {
      return lunarMonth + '月'
    }
    return lunarDay
  } catch {
    return ''
  }
}

function getEventsForDate(date) {
  return calendarStore.events.filter((e) => e.date === date || (e.start_time && e.start_time.startsWith(date)))
}

function formatDate(date) {
  if (!date) return ''
  return dayjs(date).format('YYYY年M月D日')
}

function prevMonth() {
  currentMonth.value = currentMonth.value.subtract(1, 'month')
  loadData()
}

function nextMonth() {
  currentMonth.value = currentMonth.value.add(1, 'month')
  loadData()
}

function goToday() {
  currentMonth.value = dayjs()
  loadData()
}

function openAddEvent(date) {
  editingEvent.value = null
  form.value = { title: '', date, time: '', description: '', color: 'default' }
  showAddModal.value = true
}

function openEventDetail(event) {
  detailEvent.value = event
  showDetailModal.value = true
}

function openEditFromDetail() {
  if (!detailEvent.value) return
  editingEvent.value = detailEvent.value
  const st = detailEvent.value.start_time || ''
  const datePart = detailEvent.value.date || (st ? st.substring(0, 10) : '')
  const timePart = detailEvent.value.time || (st.length >= 16 ? st.substring(11, 16) : '')
  form.value = {
    title: detailEvent.value.title,
    date: datePart,
    time: timePart,
    description: detailEvent.value.description || '',
    color: detailEvent.value.color || 'default',
  }
  showDetailModal.value = false
  showAddModal.value = true
}

function deleteFromDetail() {
  if (!detailEvent.value) return
  confirmMessage.value = `确定要删除事件「${detailEvent.value.title}」吗？`
  pendingConfirmAction = async () => {
    await calendarStore.deleteEvent(detailEvent.value.id)
    showDetailModal.value = false
  }
  showConfirm.value = true
}

function closeModal() {
  showAddModal.value = false
  editingEvent.value = null
  form.value = { title: '', date: '', time: '', description: '', color: 'default' }
}

async function handleSave() {
  saving.value = true
  try {
    if (editingEvent.value) {
      await calendarStore.updateEvent(editingEvent.value.id, form.value)
    } else {
      await calendarStore.createEvent(form.value)
    }
    closeModal()
  } catch {
    // handled
  } finally {
    saving.value = false
  }
}

function handleDelete() {
  if (!editingEvent.value) return
  confirmMessage.value = `确定要删除事件「${editingEvent.value.title}」吗？`
  pendingConfirmAction = async () => {
    await calendarStore.deleteEvent(editingEvent.value.id)
    closeModal()
  }
  showConfirm.value = true
}

async function confirmAction() {
  showConfirm.value = false
  if (pendingConfirmAction) {
    await pendingConfirmAction()
    pendingConfirmAction = null
  }
}

async function loadHolidays() {
  try {
    const data = await calendarStore.fetchHolidays(currentMonth.value.year())
    if (data && typeof data === 'object') {
      holidays.value = data
    }
  } catch {
    // holidays not critical
  }
}

async function loadData() {
  const start = currentMonth.value.startOf('month').subtract(7, 'day').format('YYYY-MM-DD')
  const end = currentMonth.value.endOf('month').add(7, 'day').format('YYYY-MM-DD')
  await Promise.allSettled([calendarStore.fetchEvents(start, end), loadHolidays()])
}

onMounted(() => {
  loadData()
})
</script>
