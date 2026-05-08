<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <h1 class="text-2xl font-bold text-gray-900">餐食计划</h1>
      <div class="flex items-center gap-2">
        <button @click="prevWeek" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <span class="text-sm font-medium text-gray-700 min-w-[140px] text-center">{{ weekLabel }}</span>
        <button @click="nextWeek" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </button>
        <button @click="goToday" class="px-3 py-2 text-sm text-orange-600 hover:bg-orange-50 rounded-lg transition-colors font-medium">今天</button>
        <button @click="handleExportShopping" class="inline-flex items-center gap-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium whitespace-nowrap">
          🛒 导出购物单
        </button>
      </div>
    </div>

    <div v-if="mealsStore.loading" class="text-center py-12 text-gray-400">加载中...</div>
    <template v-else>
      <!-- Weekly Grid -->
      <div class="overflow-x-auto">
        <div class="min-w-[700px]">
          <!-- Header -->
          <div class="grid grid-cols-8 gap-1 mb-1">
            <div class="p-2 text-xs text-gray-400 font-medium"></div>
            <div v-for="day in weekDays" :key="day.date" class="p-2 text-center rounded-lg" :class="day.isToday ? 'bg-orange-50' : ''">
              <div class="text-xs font-medium" :class="day.isToday ? 'text-orange-600' : 'text-gray-500'">{{ day.weekday }}</div>
              <div class="text-sm font-bold" :class="day.isToday ? 'text-orange-700' : 'text-gray-700'">{{ day.day }}</div>
            </div>
          </div>

          <!-- Meal Rows -->
          <div v-for="meal in mealTypes" :key="meal.key" class="grid grid-cols-8 gap-1 mb-1">
            <div class="p-2 flex items-center">
              <span class="text-sm font-medium text-gray-600">{{ meal.label }}</span>
            </div>
            <div
              v-for="day in weekDays"
              :key="day.date"
              class="p-2 min-h-[60px] rounded-lg border border-gray-100 hover:border-orange-200 hover:bg-orange-50/30 cursor-pointer transition-colors flex items-center justify-center"
              @click="openMealAssign(day.date, meal.key)"
            >
              <div v-if="getMealPlan(day.date, meal.key)" class="text-center w-full">
                <div class="text-xs font-medium text-gray-800 truncate">{{ getMealPlan(day.date, meal.key).recipe_name || getMealPlan(day.date, meal.key).name || '已安排' }}</div>
                <button @click.stop="clearMeal(day.date, meal.key)" class="text-xs text-red-400 hover:text-red-600 mt-1">清除</button>
              </div>
              <div v-else class="text-gray-300 text-lg">+</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recipe Sidebar (toggled) -->
      <div v-if="showRecipePanel" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-900">食谱库</h3>
          <div class="flex items-center gap-2">
            <button @click="showAddRecipe = true" class="text-sm text-orange-600 hover:text-orange-700 font-medium">+ 添加食谱</button>
            <button @click="showRecipePanel = false" class="p-1 hover:bg-gray-100 rounded-lg">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        </div>
        <div class="mb-3">
          <input v-model="recipeSearch" type="text" placeholder="搜索食谱..." class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" />
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[300px] overflow-y-auto">
          <div
            v-for="recipe in filteredRecipes"
            :key="recipe.id"
            class="p-3 border border-gray-100 rounded-lg hover:border-orange-200 hover:bg-orange-50/30 transition-colors group"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1 min-w-0 cursor-pointer" @click="assignRecipe(recipe)">
                <div class="font-medium text-sm text-gray-900">{{ recipe.name }}</div>
                <div v-if="recipe.ingredients" class="text-xs text-gray-400 mt-1 line-clamp-2">{{ recipe.ingredients }}</div>
              </div>
              <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                <button @click="openEditRecipe(recipe)" class="p-1 hover:bg-gray-100 rounded" title="编辑">
                  <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                </button>
                <button @click="handleDeleteRecipe(recipe)" class="p-1 hover:bg-red-50 rounded" title="删除">
                  <svg class="w-3.5 h-3.5 text-gray-400 hover:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
        <EmptyState v-if="filteredRecipes.length === 0" icon="🍳" message="暂无食谱" />
      </div>
    </template>

    <!-- Add/Edit Recipe Modal -->
    <Modal :show="showRecipeModal" :title="editingRecipe ? '编辑食谱' : '添加食谱'" @close="closeRecipeModal">
      <form @submit.prevent="handleSaveRecipe" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">食谱名称 *</label>
          <input v-model="recipeForm.name" type="text" required class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="如: 番茄炒蛋" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">食材清单</label>
          <textarea v-model="recipeForm.ingredients" rows="3" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="每行一种食材，如:&#10;番茄 2个&#10;鸡蛋 3个"></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">做法</label>
          <textarea v-model="recipeForm.instructions" rows="4" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="烹饪步骤..."></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用餐类型</label>
          <div class="flex gap-2">
            <label v-for="mt in mealTypes" :key="mt.key" class="flex items-center gap-1.5 px-3 py-1.5 border border-gray-200 rounded-lg cursor-pointer hover:border-orange-300 transition-colors" :class="recipeForm.meal_type === mt.key ? 'bg-orange-50 border-orange-300' : ''">
              <input type="radio" :value="mt.key" v-model="recipeForm.meal_type" class="sr-only" />
              <span class="text-sm">{{ mt.label }}</span>
            </label>
          </div>
        </div>
        <div class="flex gap-3">
          <button type="submit" :disabled="saving" class="flex-1 py-2.5 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 transition-colors">
            {{ saving ? '保存中...' : (editingRecipe ? '保存修改' : '添加食谱') }}
          </button>
          <button v-if="editingRecipe" type="button" @click="handleDeleteRecipe(editingRecipe)" class="px-4 py-2.5 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors">删除</button>
        </div>
      </form>
    </Modal>

    <ConfirmDialog :show="showConfirm" :message="confirmMessage" @confirm="confirmAction" @cancel="showConfirm = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import isoWeek from 'dayjs/plugin/isoWeek'
import { useMealsStore } from '@/stores/meals'
import { useShoppingStore } from '@/stores/shopping'
import Modal from '@/components/Modal.vue'
import EmptyState from '@/components/EmptyState.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

dayjs.extend(isoWeek)

const mealsStore = useMealsStore()
const shoppingStore = useShoppingStore()

const weekStart = ref(dayjs().startOf('isoWeek'))
const showRecipePanel = ref(false)
const showRecipeModal = ref(false)
const editingRecipe = ref(null)
const saving = ref(false)
const recipeSearch = ref('')
const showConfirm = ref(false)
const confirmMessage = ref('')
let pendingConfirmAction = null

const selectedSlot = ref({ date: '', meal: '' })

const mealTypes = [
  { key: 'breakfast', label: '早餐' },
  { key: 'lunch', label: '午餐' },
  { key: 'dinner', label: '晚餐' },
]

const recipeForm = ref({ name: '', ingredients: '', instructions: '', meal_type: 'lunch' })

const weekLabel = computed(() => {
  const start = weekStart.value
  const end = start.add(6, 'day')
  return `${start.format('M月D日')} - ${end.format('M月D日')}`
})

const weekDays = computed(() => {
  const days = []
  const today = dayjs().format('YYYY-MM-DD')
  for (let i = 0; i < 7; i++) {
    const d = weekStart.value.add(i, 'day')
    days.push({
      date: d.format('YYYY-MM-DD'),
      weekday: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][i],
      day: d.format('D'),
      isToday: d.format('YYYY-MM-DD') === today,
    })
  }
  return days
})

const filteredRecipes = computed(() => {
  let result = mealsStore.recipes
  if (recipeSearch.value) {
    const q = recipeSearch.value.toLowerCase()
    result = result.filter((r) => r.name.toLowerCase().includes(q) || (r.ingredients && r.ingredients.toLowerCase().includes(q)))
  }
  return result
})

function getMealPlan(date, mealType) {
  const plan = mealsStore.mealPlan
  if (plan[date] && plan[date][mealType]) return plan[date][mealType]
  return null
}

function prevWeek() {
  weekStart.value = weekStart.value.subtract(7, 'day')
  loadMealPlan()
}

function nextWeek() {
  weekStart.value = weekStart.value.add(7, 'day')
  loadMealPlan()
}

function goToday() {
  weekStart.value = dayjs().startOf('isoWeek')
  loadMealPlan()
}

function openMealAssign(date, mealType) {
  selectedSlot.value = { date, meal: mealType }
  showRecipePanel.value = true
}

async function assignRecipe(recipe) {
  try {
    await mealsStore.setMealPlan({
      date: selectedSlot.value.date,
      meal_type: selectedSlot.value.meal,
      recipe_id: recipe.id,
      recipe_name: recipe.name,
    })
    await loadMealPlan()
  } catch {
    // handled
  }
}

async function clearMeal(date, mealType) {
  try {
    await mealsStore.setMealPlan({ date, meal_type: mealType, recipe_id: null, recipe_name: '' })
    await loadMealPlan()
  } catch {
    // handled
  }
}

async function handleSaveRecipe() {
  saving.value = true
  try {
    if (editingRecipe.value) {
      await mealsStore.updateRecipe(editingRecipe.value.id, recipeForm.value)
    } else {
      await mealsStore.createRecipe(recipeForm.value)
    }
    closeRecipeModal()
    await mealsStore.fetchRecipes()
  } catch {
    // handled
  } finally {
    saving.value = false
  }
}

function openEditRecipe(recipe) {
  editingRecipe.value = recipe
  recipeForm.value = {
    name: recipe.name || '',
    ingredients: recipe.ingredients || '',
    instructions: recipe.instructions || '',
    meal_type: recipe.meal_type || 'lunch',
  }
  showRecipeModal.value = true
}

function closeRecipeModal() {
  showRecipeModal.value = false
  editingRecipe.value = null
  recipeForm.value = { name: '', ingredients: '', instructions: '', meal_type: 'lunch' }
}

function handleDeleteRecipe(recipe) {
  confirmMessage.value = `确定删除食谱「${recipe.name}」吗？`
  pendingConfirmAction = async () => {
    await mealsStore.deleteRecipe(recipe.id)
    await mealsStore.fetchRecipes()
    closeRecipeModal()
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

async function handleExportShopping() {
  try {
    const start = weekStart.value.format('YYYY-MM-DD')
    const end = weekStart.value.add(6, 'day').format('YYYY-MM-DD')
    await mealsStore.exportToShopping(start)
    await shoppingStore.fetchItems()
  } catch {
    // handled
  }
}

async function loadMealPlan() {
  const start = weekStart.value.format('YYYY-MM-DD')
  const end = weekStart.value.add(6, 'day').format('YYYY-MM-DD')
  await mealsStore.fetchMealPlan(start, end)
}

onMounted(async () => {
  await Promise.allSettled([loadMealPlan(), mealsStore.fetchRecipes()])
})
</script>
