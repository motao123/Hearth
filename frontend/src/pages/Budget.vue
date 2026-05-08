<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <h1 class="text-2xl font-bold text-gray-900">预算管理</h1>
      <div class="flex items-center gap-2">
        <button @click="prevMonth" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <span class="text-sm font-medium text-gray-700 min-w-[100px] text-center">{{ monthLabel }}</span>
        <button @click="nextMonth" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </button>
        <button @click="goCurrentMonth" class="px-3 py-2 text-sm text-orange-600 hover:bg-orange-50 rounded-lg transition-colors font-medium">本月</button>
        <button @click="showAddModal = true" class="inline-flex items-center gap-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium whitespace-nowrap">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          添加记录
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex bg-gray-100 rounded-lg p-1 max-w-xs">
      <button @click="activeTab = 'all'" :class="activeTab === 'all' ? 'bg-white shadow text-gray-900' : 'text-gray-500'" class="flex-1 py-2 rounded-md text-sm font-medium transition-all">
        全部
      </button>
      <button @click="activeTab = 'hongbao'" :class="activeTab === 'hongbao' ? 'bg-white shadow text-gray-900' : 'text-gray-500'" class="flex-1 py-2 rounded-md text-sm font-medium transition-all">
        人情往来
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-3 gap-4">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div class="text-xs text-gray-500 mb-1">收入</div>
        <div class="text-xl font-bold text-green-600">¥{{ (budgetStore.summary.income || 0).toLocaleString() }}</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div class="text-xs text-gray-500 mb-1">支出</div>
        <div class="text-xl font-bold text-red-600">¥{{ (budgetStore.summary.expense || 0).toLocaleString() }}</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div class="text-xs text-gray-500 mb-1">结余</div>
        <div class="text-xl font-bold" :class="(budgetStore.summary.balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'">
          ¥{{ (budgetStore.summary.balance || 0).toLocaleString() }}
        </div>
      </div>
    </div>

    <!-- Monthly Trend Chart -->
    <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
      <h3 class="text-sm font-semibold text-gray-700 mb-4">近6月趋势</h3>
      <div class="flex items-end gap-2 h-32">
        <div v-for="(bar, idx) in trendBars" :key="idx" class="flex-1 flex flex-col items-center gap-1">
          <div class="w-full flex flex-col items-center gap-0.5" :style="{ height: bar.height + '%' }">
            <div class="w-full bg-red-200 rounded-t" :style="{ flex: bar.expenseRatio }"></div>
            <div class="w-full bg-green-200 rounded-b" :style="{ flex: bar.incomeRatio }"></div>
          </div>
          <span class="text-xs text-gray-400">{{ bar.label }}</span>
        </div>
      </div>
      <div class="flex items-center justify-center gap-4 mt-3 text-xs">
        <span class="flex items-center gap-1"><span class="w-3 h-3 bg-green-200 rounded"></span> 收入</span>
        <span class="flex items-center gap-1"><span class="w-3 h-3 bg-red-200 rounded"></span> 支出</span>
      </div>
    </div>

    <!-- Entry List -->
    <div v-if="budgetStore.loading" class="text-center py-12 text-gray-400">加载中...</div>
    <div v-else-if="displayEntries.length === 0">
      <EmptyState icon="💰" message="暂无记录，添加一笔吧" />
    </div>
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="divide-y divide-gray-50">
        <div v-for="entry in displayEntries" :key="entry.id" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors group">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center text-sm shrink-0" :class="entry.type === 'income' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'">
            {{ entry.type === 'income' ? '↓' : '↑' }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-gray-900">{{ entry.description || categoryLabel(entry.category) }}</span>
              <span class="px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-500">{{ categoryLabel(entry.category) }}</span>
              <span v-if="entry.is_hongbao" class="px-1.5 py-0.5 rounded text-xs bg-red-50 text-red-500">人情</span>
            </div>
            <div class="text-xs text-gray-400 mt-0.5">{{ formatDate(entry.date) }}</div>
          </div>
          <div class="text-sm font-semibold shrink-0" :class="entry.type === 'income' ? 'text-green-600' : 'text-red-600'">
            {{ entry.type === 'income' ? '+' : '-' }}¥{{ (entry.amount || 0).toLocaleString() }}
          </div>
          <button @click="openEdit(entry)" class="p-1.5 hover:bg-gray-100 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity shrink-0" title="编辑">
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
          </button>
          <button @click="handleDelete(entry)" class="p-1.5 hover:bg-red-50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity shrink-0" title="删除">
            <svg class="w-4 h-4 text-gray-400 hover:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Entry Modal -->
    <Modal :show="showModal" :title="editingEntry ? '编辑记录' : '添加记录'" @close="closeModal">
      <form @submit.prevent="handleSave" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">类型</label>
          <div class="flex gap-2">
            <label class="flex-1 flex items-center justify-center gap-2 p-2.5 border rounded-lg cursor-pointer transition-colors" :class="form.type === 'expense' ? 'bg-red-50 border-red-300 text-red-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'">
              <input type="radio" value="expense" v-model="form.type" class="sr-only" />
              <span class="text-sm font-medium">支出</span>
            </label>
            <label class="flex-1 flex items-center justify-center gap-2 p-2.5 border rounded-lg cursor-pointer transition-colors" :class="form.type === 'income' ? 'bg-green-50 border-green-300 text-green-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'">
              <input type="radio" value="income" v-model="form.type" class="sr-only" />
              <span class="text-sm font-medium">收入</span>
            </label>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">金额 *</label>
          <input v-model.number="form.amount" type="number" step="0.01" min="0.01" required class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="0.00" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
          <select v-model="form.category" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none">
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
          <input v-model="form.description" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="备注说明" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">日期</label>
          <input v-model="form.date" type="date" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" />
        </div>
        <div class="flex items-center gap-2">
          <input type="checkbox" v-model="form.is_hongbao" id="hk-hongbao" class="w-4 h-4 rounded border-gray-300 text-red-500 focus:ring-red-500" />
          <label for="hk-hongbao" class="text-sm text-gray-700">标记为人情往来</label>
        </div>
        <div class="flex gap-3">
          <button type="submit" :disabled="saving" class="flex-1 py-2.5 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 transition-colors">
            {{ saving ? '保存中...' : (editingEntry ? '保存修改' : '添加') }}
          </button>
          <button v-if="editingEntry" type="button" @click="confirmDelete" class="px-4 py-2.5 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors">删除</button>
        </div>
      </form>
    </Modal>

    <ConfirmDialog :show="showConfirm" :message="confirmMessage" @confirm="confirmAction" @cancel="showConfirm = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { useBudgetStore } from '@/stores/budget'
import Modal from '@/components/Modal.vue'
import EmptyState from '@/components/EmptyState.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const budgetStore = useBudgetStore()

const currentMonth = ref(dayjs())
const activeTab = ref('all')
const showModal = ref(false)
const editingEntry = ref(null)
const saving = ref(false)
const showConfirm = ref(false)
const confirmMessage = ref('')
let pendingConfirmAction = null
const hongbaoEntries = ref([])

const form = ref({
  type: 'expense',
  amount: null,
  category: 'food',
  description: '',
  date: dayjs().format('YYYY-MM-DD'),
  is_hongbao: false,
})

const categories = [
  { value: 'food', label: '餐饮' },
  { value: 'transport', label: '交通' },
  { value: 'shopping', label: '购物' },
  { value: 'housing', label: '住房' },
  { value: 'entertainment', label: '娱乐' },
  { value: 'medical', label: '医疗' },
  { value: 'education', label: '教育' },
  { value: 'salary', label: '工资' },
  { value: 'investment', label: '投资' },
  { value: 'gift', label: '礼金' },
  { value: 'other', label: '其他' },
]

const monthLabel = computed(() => currentMonth.value.format('YYYY年M月'))

const displayEntries = computed(() => {
  if (activeTab.value === 'hongbao') {
    return hongbaoEntries.value
  }
  return budgetStore.entries
})

const trendBars = computed(() => {
  const bars = []
  for (let i = 5; i >= 0; i--) {
    const m = dayjs().subtract(i, 'month')
    const label = m.format('M月')
    // Use summary data if available, otherwise show placeholder
    const income = i === 0 ? (budgetStore.summary.income || 0) : 0
    const expense = i === 0 ? (budgetStore.summary.expense || 0) : 0
    const max = Math.max(income, expense, 1)
    const total = income + expense
    bars.push({
      label,
      height: total > 0 ? Math.max((total / max) * 80, 10) : 10,
      incomeRatio: total > 0 ? income / total : 0.5,
      expenseRatio: total > 0 ? expense / total : 0.5,
    })
  }
  return bars
})

function categoryLabel(cat) {
  const found = categories.find((c) => c.value === cat)
  return found ? found.label : cat
}

function formatDate(date) {
  if (!date) return ''
  return dayjs(date).format('M月D日')
}

function prevMonth() {
  currentMonth.value = currentMonth.value.subtract(1, 'month')
  loadData()
}

function nextMonth() {
  currentMonth.value = currentMonth.value.add(1, 'month')
  loadData()
}

function goCurrentMonth() {
  currentMonth.value = dayjs()
  loadData()
}

async function handleSave() {
  saving.value = true
  try {
    if (editingEntry.value) {
      await budgetStore.updateEntry(editingEntry.value.id, {
        type: form.value.type,
        amount: form.value.amount,
        category: form.value.category,
        description: form.value.description,
        date: form.value.date,
        is_hongbao: form.value.is_hongbao,
      })
    } else {
      await budgetStore.addEntry({
        type: form.value.type,
        amount: form.value.amount,
        category: form.value.category,
        description: form.value.description,
        date: form.value.date,
        is_hongbao: form.value.is_hongbao,
      })
    }
    closeModal()
    await loadData()
  } catch {
    // handled
  } finally {
    saving.value = false
  }
}

function openEdit(entry) {
  editingEntry.value = entry
  form.value = {
    type: entry.type,
    amount: entry.amount,
    category: entry.category,
    description: entry.description || '',
    date: entry.date,
    is_hongbao: entry.is_hongbao || false,
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingEntry.value = null
  form.value = { type: 'expense', amount: null, category: 'food', description: '', date: dayjs().format('YYYY-MM-DD'), is_hongbao: false }
}

function handleDelete(entry) {
  confirmMessage.value = `确定删除「${entry.description || categoryLabel(entry.category)}」¥${entry.amount} 吗？`
  pendingConfirmAction = async () => {
    await budgetStore.deleteEntry(entry.id)
    await loadData()
  }
  showConfirm.value = true
}

function confirmDelete() {
  handleDelete(editingEntry.value)
  closeModal()
}

async function confirmAction() {
  showConfirm.value = false
  if (pendingConfirmAction) {
    await pendingConfirmAction()
    pendingConfirmAction = null
  }
}

async function loadData() {
  const y = currentMonth.value.year()
  const m = currentMonth.value.month() + 1
  await Promise.allSettled([
    budgetStore.fetchEntries(y, m),
    budgetStore.fetchSummary(y, m),
    loadHongbao(),
  ])
}

async function loadHongbao() {
  try {
    const data = await budgetStore.fetchHongbao()
    hongbaoEntries.value = Array.isArray(data) ? data : data.items || []
  } catch {
    hongbaoEntries.value = []
  }
}

onMounted(() => {
  loadData()
})
</script>
