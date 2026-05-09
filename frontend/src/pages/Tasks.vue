<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <h1 class="text-2xl font-bold text-gray-900">任务管理</h1>
      <div class="flex items-center gap-2">
        <!-- Filters -->
        <select v-model="filterPriority" class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none">
          <option value="">全部优先级</option>
          <option value="high">高优先级</option>
          <option value="medium">中优先级</option>
          <option value="low">低优先级</option>
        </select>
        <select v-model="filterAssignee" class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none">
          <option value="">全部成员</option>
          <option v-for="m in familyStore.members" :key="m.id" :value="m.id">{{ m.name }}</option>
        </select>
        <button @click="showAddModal = true" class="inline-flex items-center gap-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium whitespace-nowrap">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          添加任务
        </button>
      </div>
    </div>

    <!-- Kanban Board -->
    <div v-if="tasksStore.loading" class="text-center py-12 text-gray-400">加载中...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Todo Column -->
      <div class="bg-gray-50 rounded-xl p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-700 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-blue-500"></span>
            待办
            <span class="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">{{ todoTasks.length }}</span>
          </h3>
        </div>
        <div class="space-y-3 min-h-[100px]">
          <div v-for="task in todoTasks" :key="task.id" class="bg-white rounded-lg p-3 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer" @click="openEdit(task)">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0 flex-1">
                <div class="font-medium text-gray-900 text-sm">{{ task.title }}</div>
                <div v-if="task.description" class="text-xs text-gray-500 mt-1 line-clamp-2">{{ task.description }}</div>
              </div>
              <span :class="priorityBadge(task.priority)" class="px-1.5 py-0.5 rounded text-xs font-medium shrink-0">
                {{ priorityLabel(task.priority) }}
              </span>
            </div>
            <div class="flex items-center justify-between mt-2 text-xs text-gray-400">
              <div class="flex items-center gap-2">
                <span v-if="task.assignee_name">{{ task.assignee_name }}</span>
                <span v-if="task.due_date">{{ formatDate(task.due_date) }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span v-if="task.points" class="text-amber-500">+{{ task.points }}分</span>
                <button @click.stop="moveTask(task, 'in_progress')" class="p-1 hover:bg-gray-100 rounded transition-colors" title="开始">
                  <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </button>
              </div>
            </div>
          </div>
          <div v-if="todoTasks.length === 0" class="text-center text-gray-400 text-sm py-4">暂无待办任务</div>
        </div>
      </div>

      <!-- In Progress Column -->
      <div class="bg-gray-50 rounded-xl p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-700 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-yellow-500"></span>
            进行中
            <span class="text-xs bg-yellow-100 text-yellow-600 px-2 py-0.5 rounded-full">{{ inProgressTasks.length }}</span>
          </h3>
        </div>
        <div class="space-y-3 min-h-[100px]">
          <div v-for="task in inProgressTasks" :key="task.id" class="bg-white rounded-lg p-3 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer" @click="openEdit(task)">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0 flex-1">
                <div class="font-medium text-gray-900 text-sm">{{ task.title }}</div>
                <div v-if="task.description" class="text-xs text-gray-500 mt-1 line-clamp-2">{{ task.description }}</div>
              </div>
              <span :class="priorityBadge(task.priority)" class="px-1.5 py-0.5 rounded text-xs font-medium shrink-0">
                {{ priorityLabel(task.priority) }}
              </span>
            </div>
            <div class="flex items-center justify-between mt-2 text-xs text-gray-400">
              <div class="flex items-center gap-2">
                <span v-if="task.assignee_name">{{ task.assignee_name }}</span>
                <span v-if="task.due_date">{{ formatDate(task.due_date) }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span v-if="task.points" class="text-amber-500">+{{ task.points }}分</span>
                <button @click.stop="moveTask(task, 'todo')" class="p-1 hover:bg-gray-100 rounded transition-colors" title="退回待办">
                  <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
                </button>
                <button @click.stop="moveTask(task, 'done')" class="p-1 hover:bg-gray-100 rounded transition-colors" title="完成">
                  <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                </button>
              </div>
            </div>
          </div>
          <div v-if="inProgressTasks.length === 0" class="text-center text-gray-400 text-sm py-4">暂无进行中任务</div>
        </div>
      </div>

      <!-- Done Column -->
      <div class="bg-gray-50 rounded-xl p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-700 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-green-500"></span>
            已完成
            <span class="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded-full">{{ doneTasks.length }}</span>
          </h3>
        </div>
        <div class="space-y-3 min-h-[100px]">
          <div v-for="task in doneTasks" :key="task.id" class="bg-white rounded-lg p-3 shadow-sm border border-gray-100 opacity-75">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0 flex-1">
                <div class="font-medium text-gray-500 text-sm line-through">{{ task.title }}</div>
              </div>
              <span v-if="task.points" class="text-amber-500 bg-amber-50 px-1.5 py-0.5 rounded text-xs font-medium shrink-0">
                +{{ task.points }}分
              </span>
            </div>
            <div class="flex items-center justify-between mt-2 text-xs text-gray-400">
              <span v-if="task.assignee_name">{{ task.assignee_name }}</span>
              <button @click="deleteTask(task)" class="p-1 hover:bg-red-50 rounded transition-colors" title="删除">
                <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            </div>
          </div>
          <div v-if="doneTasks.length === 0" class="text-center text-gray-400 text-sm py-4">暂无已完成任务</div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Task Modal -->
    <Modal :show="showAddModal || !!editingTask" :title="editingTask ? '编辑任务' : '添加任务'" @close="closeModal">
      <form @submit.prevent="handleSave" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">标题 *</label>
          <input v-model="form.title" type="text" required class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="任务标题" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
          <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="任务描述"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">优先级</label>
            <select v-model="form.priority" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none">
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">指派给</label>
            <select v-model="form.assignee_id" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none">
              <option value="">未指派</option>
              <option v-for="m in familyStore.members" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">截止日期</label>
            <input v-model="form.due_date" type="date" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">积分</label>
            <input v-model.number="form.points" type="number" min="0" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="0" />
          </div>
        </div>
        <div class="flex gap-3">
          <button type="submit" :disabled="saving" class="flex-1 py-2.5 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 transition-colors">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <button v-if="editingTask" type="button" @click="handleDelete" class="px-4 py-2.5 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors">
            删除
          </button>
        </div>
      </form>
    </Modal>

    <ConfirmDialog :show="showConfirm" :message="confirmMessage" @confirm="confirmAction" @cancel="showConfirm = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { useTasksStore } from '@/stores/tasks'
import { useFamilyStore } from '@/stores/family'
import Modal from '@/components/Modal.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const tasksStore = useTasksStore()
const familyStore = useFamilyStore()

const showAddModal = ref(false)
const editingTask = ref(null)
const saving = ref(false)
const filterPriority = ref('')
const filterAssignee = ref('')
const showConfirm = ref(false)
const confirmMessage = ref('')
let pendingConfirmAction = null

const form = ref({
  title: '',
  description: '',
  priority: 'normal',
  assignee_id: null,
  due_date: '',
  points: 0,
})

const filteredTasks = computed(() => {
  let result = tasksStore.tasks
  if (filterPriority.value) result = result.filter((t) => t.priority === filterPriority.value)
  if (filterAssignee.value) result = result.filter((t) => t.assignee_id === filterAssignee.value)
  return result
})

const todoTasks = computed(() => filteredTasks.value.filter((t) => t.status === 'todo'))
const inProgressTasks = computed(() => filteredTasks.value.filter((t) => t.status === 'in_progress'))
const doneTasks = computed(() => filteredTasks.value.filter((t) => t.status === 'done'))

function formatDate(date) {
  if (!date) return ''
  return dayjs(date).format('M/D')
}

function priorityLabel(p) {
  return { low: '低', medium: '中', high: '高' }[p] || '中'
}

function priorityBadge(p) {
  return {
    low: 'bg-blue-50 text-blue-600',
    medium: 'bg-yellow-50 text-yellow-600',
    high: 'bg-red-50 text-red-600',
  }[p] || 'bg-yellow-50 text-yellow-600'
}

async function moveTask(task, newStatus) {
  try {
    if (newStatus === 'done') {
      await tasksStore.completeTask(task.id)
    } else {
      await tasksStore.updateTask(task.id, { ...task, status: newStatus })
    }
  } catch {
    // handled by store
  }
}

function openEdit(task) {
  editingTask.value = task
  form.value = {
    title: task.title,
    description: task.description || '',
    priority: task.priority || 'medium',
    assignee_id: task.assignee_id || '',
    due_date: task.due_date || '',
    points: task.points || 0,
  }
}

function closeModal() {
  showAddModal.value = false
  editingTask.value = null
  form.value = { title: '', description: '', priority: 'normal', assignee_id: null, due_date: '', points: 0 }
}

async function handleSave() {
  saving.value = true
  try {
    if (editingTask.value) {
      await tasksStore.updateTask(editingTask.value.id, form.value)
    } else {
      await tasksStore.createTask({ ...form.value, status: 'todo' })
    }
    closeModal()
  } catch {
    // handled by store
  } finally {
    saving.value = false
  }
}

function deleteTask(task) {
  confirmMessage.value = `确定要删除任务「${task.title}」吗？`
  pendingConfirmAction = async () => {
    await tasksStore.deleteTask(task.id)
  }
  showConfirm.value = true
}

function handleDelete() {
  if (!editingTask.value) return
  confirmMessage.value = `确定要删除任务「${editingTask.value.title}」吗？`
  pendingConfirmAction = async () => {
    await tasksStore.deleteTask(editingTask.value.id)
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

onMounted(async () => {
  await Promise.allSettled([tasksStore.fetchTasks(), familyStore.loadMembers()])
})
</script>
