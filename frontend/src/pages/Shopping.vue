<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <h1 class="text-2xl font-bold text-gray-900">购物清单</h1>
      <div class="flex items-center gap-2">
        <button @click="handleImport" class="inline-flex items-center gap-1 px-3 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors text-sm font-medium whitespace-nowrap">
          🍳 从餐食导入
        </button>
        <button v-if="checkedItems.length > 0" @click="handleClearChecked" class="inline-flex items-center gap-1 px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium whitespace-nowrap">
          清除已购 ({{ checkedItems.length }})
        </button>
        <button @click="showAddModal = true" class="inline-flex items-center gap-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium whitespace-nowrap">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          添加
        </button>
      </div>
    </div>

    <div v-if="shoppingStore.loading" class="text-center py-12 text-gray-400">加载中...</div>
    <template v-else>
      <!-- Unchecked items by category -->
      <div v-for="group in uncheckedGroups" :key="group.aisle" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-4 py-3 bg-gray-50 border-b border-gray-100">
          <h3 class="font-semibold text-gray-700 text-sm">{{ group.aisle }} <span class="text-gray-400 font-normal">({{ group.items.length }})</span></h3>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="item in group.items" :key="item.id" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors">
            <button @click="toggleItem(item)" class="w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-colors" :class="item.checked ? 'bg-green-500 border-green-500' : 'border-gray-300 hover:border-green-400'">
              <svg v-if="item.checked" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
            </button>
            <div class="flex-1 min-w-0">
              <span class="text-sm text-gray-900">{{ item.name }}</span>
              <span v-if="item.quantity" class="text-xs text-gray-400 ml-2">{{ item.quantity }}</span>
            </div>
            <button @click="deleteItem(item)" class="p-1 hover:bg-red-50 rounded transition-colors shrink-0">
              <svg class="w-4 h-4 text-gray-300 hover:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Checked items -->
      <div v-if="checkedItems.length > 0" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-4 py-3 bg-green-50 border-b border-green-100">
          <h3 class="font-semibold text-green-700 text-sm">已购买 <span class="text-green-400 font-normal">({{ checkedItems.length }})</span></h3>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="item in checkedItems" :key="item.id" class="flex items-center gap-3 px-4 py-3 opacity-50">
            <button @click="toggleItem(item)" class="w-5 h-5 rounded border-2 bg-green-500 border-green-500 flex items-center justify-center shrink-0">
              <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
            </button>
            <span class="text-sm text-gray-400 line-through flex-1">{{ item.name }}</span>
            <span v-if="item.quantity" class="text-xs text-gray-300">{{ item.quantity }}</span>
            <button @click="deleteItem(item)" class="p-1 hover:bg-red-50 rounded transition-colors shrink-0">
              <svg class="w-4 h-4 text-gray-300 hover:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </div>
      </div>

      <EmptyState v-if="shoppingStore.items.length === 0" icon="🛒" message="购物清单是空的，添加一些商品吧" />
    </template>

    <!-- Add Item Modal -->
    <Modal :show="showAddModal" title="添加购物项" @close="showAddModal = false">
      <form @submit.prevent="handleAdd" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">名称 *</label>
          <input v-model="form.name" type="text" required class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none" placeholder="商品名称" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
            <input v-model="form.aisle" type="text" list="aisle-list" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none" placeholder="如: 蔬菜" />
            <datalist id="aisle-list">
              <option v-for="a in commonAisles" :key="a" :value="a" />
            </datalist>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">数量</label>
            <input v-model="form.quantity" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none" placeholder="如: 1斤" />
          </div>
        </div>
        <button type="submit" :disabled="saving" class="w-full py-2.5 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition-colors">
          {{ saving ? '保存中...' : '添加' }}
        </button>
      </form>
    </Modal>

    <ConfirmDialog :show="showConfirm" :message="confirmMessage" @confirm="confirmAction" @cancel="showConfirm = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useShoppingStore } from '@/stores/shopping'
import { useMealsStore } from '@/stores/meals'
import Modal from '@/components/Modal.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import EmptyState from '@/components/EmptyState.vue'

const shoppingStore = useShoppingStore()
const mealsStore = useMealsStore()

const showAddModal = ref(false)
const saving = ref(false)
const showConfirm = ref(false)
const confirmMessage = ref('')
let pendingConfirmAction = null

const form = ref({ name: '', aisle: '', quantity: '' })

const commonAisles = ['蔬菜', '水果', '肉禽蛋', '水产', '乳制品', '主食', '调味品', '零食', '饮料', '日用品', '其他']

const checkedItems = computed(() => shoppingStore.items.filter((i) => i.checked))

const uncheckedGroups = computed(() => {
  const unchecked = shoppingStore.items.filter((i) => !i.checked)
  const groups = {}
  unchecked.forEach((item) => {
    const aisle = item.aisle || '未分类'
    if (!groups[aisle]) groups[aisle] = { aisle, items: [] }
    groups[aisle].items.push(item)
  })
  return Object.values(groups).sort((a, b) => a.aisle.localeCompare(b.aisle, 'zh'))
})

async function toggleItem(item) {
  try {
    await shoppingStore.toggleItem(item.id)
  } catch {
    // handled
  }
}

function deleteItem(item) {
  confirmMessage.value = `确定要删除「${item.name}」吗？`
  pendingConfirmAction = async () => {
    await shoppingStore.deleteItem(item.id)
  }
  showConfirm.value = true
}

function handleClearChecked() {
  confirmMessage.value = `确定要清除所有已购商品吗？`
  pendingConfirmAction = async () => {
    await shoppingStore.clearChecked()
  }
  showConfirm.value = true
}

async function handleAdd() {
  saving.value = true
  try {
    await shoppingStore.addItem({ ...form.value, checked: false })
    showAddModal.value = false
    form.value = { name: '', aisle: '', quantity: '' }
  } catch {
    // handled
  } finally {
    saving.value = false
  }
}

async function handleImport() {
  try {
    const today = new Date().toISOString().slice(0, 10)
    await mealsStore.exportToShopping(today)
    await shoppingStore.fetchItems()
  } catch {
    // handled
  }
}

async function confirmAction() {
  showConfirm.value = false
  if (pendingConfirmAction) {
    await pendingConfirmAction()
    pendingConfirmAction = null
  }
}

onMounted(() => {
  shoppingStore.fetchItems()
})
</script>
