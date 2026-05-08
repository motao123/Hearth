<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">家庭成员</h1>
      <button @click="showAddModal = true" class="inline-flex items-center gap-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium whitespace-nowrap">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        添加成员
      </button>
    </div>

    <!-- Member Cards -->
    <div v-if="familyStore.loading" class="text-center py-12 text-gray-400">加载中...</div>
    <template v-else>
      <div v-if="familyStore.members.length === 0">
        <EmptyState icon="👨‍👩‍👧‍👦" message="暂无家庭成员，添加第一位成员吧" />
      </div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="member in familyStore.members" :key="member.id" class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div class="flex items-start gap-4">
            <div class="w-14 h-14 rounded-full flex items-center justify-center text-2xl shrink-0" :class="avatarBg(member.role)">
              {{ member.avatar || member.name?.charAt(0) || '?' }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <h3 class="font-semibold text-gray-900 text-lg">{{ member.name }}</h3>
                <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="roleBadge(member.role)">{{ roleLabel(member.role) }}</span>
              </div>
              <div v-if="member.points !== undefined && member.points !== null" class="text-sm text-amber-600 mt-1">积分: {{ member.points }}</div>
              <div v-if="member.email" class="text-sm text-gray-400 mt-1 truncate">{{ member.email }}</div>
            </div>
            <button @click="openEdit(member)" class="p-2 hover:bg-gray-100 rounded-lg transition-colors shrink-0" title="编辑">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
            </button>
            <button @click="handleDelete(member)" class="p-2 hover:bg-red-50 rounded-lg transition-colors shrink-0" title="删除">
              <svg class="w-4 h-4 text-gray-400 hover:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Points Ranking -->
    <div v-if="familyStore.pointsRanking.length > 0" class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
      <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <span>🏆</span> 积分排行
      </h2>
      <div class="space-y-3">
        <div v-for="(member, idx) in familyStore.pointsRanking" :key="member.id" class="flex items-center gap-3">
          <span class="text-lg w-8 text-center" :class="idx < 3 ? '' : 'opacity-50'">
            {{ ['🥇', '🥈', '🥉'][idx] || `${idx + 1}` }}
          </span>
          <div class="flex-1 min-w-0">
            <span class="font-medium text-gray-900 text-sm">{{ member.name }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="h-2 rounded-full bg-amber-100" :style="{ width: barWidth(member.points) + 'px' }"></div>
            <span class="text-sm font-semibold text-amber-600 min-w-[40px] text-right">{{ member.points }}分</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Member Modal -->
    <Modal :show="showAddModal || !!editingMember" :title="editingMember ? '编辑成员' : '添加成员'" @close="closeModal">
      <form @submit.prevent="handleSave" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">姓名 *</label>
          <input v-model="form.name" type="text" required class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="成员姓名" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">角色</label>
          <select v-model="form.role" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none">
            <option value="parent">家长</option>
            <option value="child">孩子</option>
            <option value="other">其他</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">头像文字</label>
          <input v-model="form.avatar" type="text" maxlength="2" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="如: 😊 或 名字首字" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
          <input v-model="form.email" type="email" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="example@email.com" />
        </div>
        <div class="flex gap-3">
          <button type="submit" :disabled="saving" class="flex-1 py-2.5 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 transition-colors">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <button v-if="editingMember" type="button" @click="handleDelete(editingMember)" class="px-4 py-2.5 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors">删除</button>
        </div>
      </form>
    </Modal>

    <ConfirmDialog :show="showConfirm" :message="confirmMessage" @confirm="confirmAction" @cancel="showConfirm = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFamilyStore } from '@/stores/family'
import Modal from '@/components/Modal.vue'
import EmptyState from '@/components/EmptyState.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const familyStore = useFamilyStore()

const showAddModal = ref(false)
const editingMember = ref(null)
const saving = ref(false)
const showConfirm = ref(false)
const confirmMessage = ref('')
let pendingConfirmAction = null

const form = ref({ name: '', role: 'parent', avatar: '', email: '' })

function avatarBg(role) {
  return {
    parent: 'bg-blue-100 text-blue-600',
    child: 'bg-green-100 text-green-600',
    other: 'bg-gray-100 text-gray-600',
  }[role] || 'bg-gray-100 text-gray-600'
}

function roleLabel(role) {
  return { parent: '家长', child: '孩子', other: '其他' }[role] || '成员'
}

function roleBadge(role) {
  return {
    parent: 'bg-blue-50 text-blue-600',
    child: 'bg-green-50 text-green-600',
    other: 'bg-gray-100 text-gray-600',
  }[role] || 'bg-gray-100 text-gray-600'
}

function barWidth(points) {
  const maxPoints = Math.max(...familyStore.pointsRanking.map((m) => m.points || 0), 1)
  return Math.max(((points || 0) / maxPoints) * 120, 4)
}

function openEdit(member) {
  editingMember.value = member
  form.value = {
    name: member.name || '',
    role: member.role || 'parent',
    avatar: member.avatar || '',
    email: member.email || '',
  }
}

function closeModal() {
  showAddModal.value = false
  editingMember.value = null
  form.value = { name: '', role: 'parent', avatar: '', email: '' }
}

async function handleSave() {
  saving.value = true
  try {
    if (editingMember.value) {
      await familyStore.updateMember(editingMember.value.id, form.value)
    } else {
      await familyStore.addMember(form.value)
    }
    closeModal()
    await loadData()
  } catch {
    // handled
  } finally {
    saving.value = false
  }
}

function handleDelete(member) {
  confirmMessage.value = `确定删除成员「${member.name}」吗？所有相关数据将被移除。`
  pendingConfirmAction = async () => {
    await familyStore.deleteMember(member.id)
    await loadData()
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
  await Promise.allSettled([familyStore.loadMembers(), familyStore.fetchPointsRanking()])
})
</script>
