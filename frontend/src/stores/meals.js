import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useMealsStore = defineStore('meals', () => {
  const mealPlan = ref({})
  const recipes = ref([])
  const loading = ref(false)

  async function fetchMealPlan(startDate, endDate) {
    loading.value = true
    try {
      const { data } = await api.get('/api/meals/plan', { params: { start_date: startDate, end_date: endDate } })
      mealPlan.value = data
    } finally {
      loading.value = false
    }
  }

  async function setMealPlan(data) {
    const { data: result } = await api.put('/api/meals/plan', data)
    return result
  }

  async function fetchRecipes() {
    loading.value = true
    try {
      const { data } = await api.get('/api/meals/recipes')
      recipes.value = Array.isArray(data) ? data : data.items || []
    } finally {
      loading.value = false
    }
  }

  function _toRecipePayload(data) {
    return {
      name: data.name,
      ingredients: typeof data.ingredients === 'string' ? data.ingredients.split('\n').filter(Boolean) : data.ingredients,
      steps: typeof data.instructions === 'string' ? data.instructions.split('\n').filter(Boolean) : data.steps || [],
    }
  }

  async function createRecipe(data) {
    const { data: recipe } = await api.post('/api/meals/recipes', _toRecipePayload(data))
    recipes.value.push(recipe)
    return recipe
  }

  async function updateRecipe(id, data) {
    const { data: updated } = await api.patch(`/api/meals/recipes/${id}`, _toRecipePayload(data))
    const idx = recipes.value.findIndex((r) => r.id === id)
    if (idx !== -1) recipes.value[idx] = updated
    return updated
  }

  async function deleteRecipe(id) {
    await api.delete(`/api/meals/recipes/${id}`)
    recipes.value = recipes.value.filter((r) => r.id !== id)
  }

  async function exportToShopping(date) {
    const { data } = await api.post('/api/meals/export-to-shopping', { start_date: date, end_date: date })
    return data
  }

  return { mealPlan, recipes, loading, fetchMealPlan, setMealPlan, fetchRecipes, createRecipe, updateRecipe, deleteRecipe, exportToShopping }
})
