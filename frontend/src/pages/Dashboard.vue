<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">欢迎回家 🏠</h1>
        <p class="text-gray-500 mt-1">{{ todayFormatted }}</p>
      </div>
    </div>

    <!-- Stat Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center text-lg">📋</div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ pendingTasks }}</div>
            <div class="text-xs text-gray-500">待办任务</div>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center text-lg">🛒</div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ uncheckedItems }}</div>
            <div class="text-xs text-gray-500">购物清单</div>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center text-lg">💰</div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ monthlySpent }}</div>
            <div class="text-xs text-gray-500">本月支出</div>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center text-lg">🍳</div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ todayMeals }}</div>
            <div class="text-xs text-gray-500">今日餐食</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="flex flex-wrap gap-3">
      <button @click="showAddTask = true" class="inline-flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        添加任务
      </button>
      <button @click="showAddItem = true" class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        添加购物项
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Upcoming Events -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>📅</span> 近期日程
        </h2>
        <div v-if="upcomingEvents.length === 0" class="text-gray-400 text-sm text-center py-6">暂无近期日程</div>
        <div v-else class="space-y-3">
          <div v-for="event in upcomingEvents" :key="event.id" class="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
            <div class="w-2 h-2 rounded-full bg-orange-500 mt-2 shrink-0"></div>
            <div class="min-w-0 flex-1">
              <div class="font-medium text-gray-900 text-sm truncate">{{ event.title }}</div>
              <div class="text-xs text-gray-500 mt-0.5">{{ formatDate(event.start_time || event.date) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity / Pending Tasks -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>✅</span> 待办任务
        </h2>
        <div v-if="recentTasks.length === 0" class="text-gray-400 text-sm text-center py-6">暂无待办任务</div>
        <div v-else class="space-y-3">
          <div v-for="task in recentTasks" :key="task.id" class="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
            <span :class="priorityBadge(task.priority)" class="px-2 py-0.5 rounded-full text-xs font-medium">
              {{ priorityLabel(task.priority) }}
            </span>
            <div class="min-w-0 flex-1">
              <div class="font-medium text-gray-900 text-sm truncate">{{ task.title }}</div>
              <div v-if="task.due_date" class="text-xs text-gray-500 mt-0.5">截止: {{ formatDate(task.due_date) }}</div>
            </div>
            <span v-if="task.points" class="text-xs text-amber-600 font-medium bg-amber-50 px-2 py-0.5 rounded-full">
              +{{ task.points }}分
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Task Modal -->
    <Modal :show="showAddTask" title="添加任务" @close="showAddTask = false">
      <form @submit.prevent="handleAddTask" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
          <input v-model="taskForm.title" type="text" required class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="任务标题" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
          <textarea v-model="taskForm.description" rows="2" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="任务描述（可选）"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">优先级</label>
            <select v-model="taskForm.priority" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none">
              <option value="low">低</option>
              <option value="normal">中</option>
              <option value="high">高</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">积分</label>
            <input v-model.number="taskForm.points" type="number" min="0" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="0" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">截止日期</label>
          <input v-model="taskForm.due_date" type="date" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" />
        </div>
        <button type="submit" :disabled="taskSaving" class="w-full py-2.5 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 transition-colors">
          {{ taskSaving ? '保存中...' : '添加' }}
        </button>
      </form>
    </Modal>

    <!-- Add Shopping Item Modal -->
    <Modal :show="showAddItem" title="添加购物项" @close="showAddItem = false">
      <form @submit.prevent="handleAddItem" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">名称</label>
          <input v-model="itemForm.name" type="text" required class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none" placeholder="商品名称" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
            <input v-model="itemForm.aisle" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none" placeholder="如: 蔬菜" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">数量</label>
            <input v-model="itemForm.quantity" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none" placeholder="如: 1斤" />
          </div>
        </div>
        <button type="submit" :disabled="itemSaving" class="w-full py-2.5 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition-colors">
          {{ itemSaving ? '保存中...' : '添加' }}
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { useTasksStore } from '@/stores/tasks'
import { useShoppingStore } from '@/stores/shopping'
import { useBudgetStore } from '@/stores/budget'
import { useMealsStore } from '@/stores/meals'
import { useCalendarStore } from '@/stores/calendar'
import Modal from '@/components/Modal.vue'

const tasksStore = useTasksStore()
const shoppingStore = useShoppingStore()
const budgetStore = useBudgetStore()
const mealsStore = useMealsStore()
const calendarStore = useCalendarStore()

const todayFormatted = dayjs().format('YYYY年M月D日 dddd')

const showAddTask = ref(false)
const showAddItem = ref(false)
const taskSaving = ref(false)
const itemSaving = ref(false)

const taskForm = ref({ title: '', description: '', priority: 'normal', points: 0, due_date: '' })
const itemForm = ref({ name: '', aisle: '', quantity: '' })

const pendingTasks = computed(() => tasksStore.tasks.filter((t) => t.status !== 'done').length)
const uncheckedItems = computed(() => shoppingStore.items.filter((i) => !i.checked).length)
const monthlySpent = computed(() => {
  const val = budgetStore.summary.expense || 0
  return '¥' + val.toLocaleString()
})
const todayMeals = computed(() => {
  const today = dayjs().format('YYYY-MM-DD')
  const plan = mealsStore.mealPlan
  let count = 0
  if (plan[today]) {
    count = Object.values(plan[today]).filter((v) => v).length
  }
  return count
})

const recentTasks = computed(() => tasksStore.tasks.filter((t) => t.status !== 'done').slice(0, 5))
const upcomingEvents = computed(() => {
  const now = dayjs().format('YYYY-MM-DD')
  return calendarStore.events
    .filter((e) => (e.start_time || e.date) >= now)
    .sort((a, b) => (a.start_time || a.date).localeCompare(b.start_time || b.date))
    .slice(0, 5)
})

function formatDate(date) {
  if (!date) return ''
  return dayjs(date).format('M月D日')
}

function priorityLabel(p) {
  return { low: '低', normal: '中', high: '高' }[p] || '中'
}

function priorityBadge(p) {
  return {
    low: 'bg-blue-50 text-blue-600',
    normal: 'bg-yellow-50 text-yellow-600',
    high: 'bg-red-50 text-red-600',
  }[p] || 'bg-yellow-50 text-yellow-600'
}

async function handleAddTask() {
  taskSaving.value = true
  try {
    await tasksStore.createTask({ ...taskForm.value, status: 'todo' })
    showAddTask.value = false
    taskForm.value = { title: '', description: '', priority: 'normal', points: 0, due_date: '' }
  } catch {
    // error handled by store
  } finally {
    taskSaving.value = false
  }
}

async function handleAddItem() {
  itemSaving.value = true
  try {
    await shoppingStore.addItem({ ...itemForm.value, checked: false })
    showAddItem.value = false
    itemForm.value = { name: '', aisle: '', quantity: '' }
  } catch {
    // error handled by store
  } finally {
    itemSaving.value = false
  }
}

onMounted(async () => {
  const now = dayjs()
  const promises = [
    tasksStore.fetchTasks(),
    shoppingStore.fetchItems(),
    budgetStore.fetchSummary(now.year(), now.month() + 1),
    budgetStore.fetchEntries(now.year(), now.month() + 1),
    mealsStore.fetchMealPlan(now.startOf('week').format('YYYY-MM-DD'), now.endOf('week').format('YYYY-MM-DD')),
    calendarStore.fetchEvents(now.startOf('month').format('YYYY-MM-DD'), now.endOf('month').add(7, 'day').format('YYYY-MM-DD')),
  ]
  await Promise.allSettled(promises)
})
</script>
