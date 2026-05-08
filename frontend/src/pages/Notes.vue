<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">便签</h1>
      <button @click="openAdd" class="inline-flex items-center gap-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium whitespace-nowrap">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        新建便签
      </button>
    </div>

    <div v-if="notesStore.loading" class="text-center py-12 text-gray-400">加载中...</div>
    <template v-else>
      <!-- Pinned notes -->
      <div v-if="pinnedNotes.length > 0">
        <h3 class="text-sm font-semibold text-gray-500 mb-3 flex items-center gap-1">📌 已置顶</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="note in pinnedNotes"
            :key="note.id"
            class="rounded-xl p-4 shadow-sm border cursor-pointer hover:shadow-md transition-all min-h-[120px] flex flex-col"
            :style="{ backgroundColor: noteColor(note.color), borderColor: noteColor(note.color) }"
            @click="openEdit(note)"
          >
            <div class="flex items-start justify-between gap-2">
              <h4 class="font-semibold text-gray-900 text-sm">{{ note.title || '无标题' }}</h4>
              <button @click.stop="togglePin(note)" class="p-1 hover:bg-white/50 rounded transition-colors" :title="note.pinned ? '取消置顶' : '置顶'">
                <span class="text-sm">📌</span>
              </button>
            </div>
            <div class="flex-1 mt-2 text-sm text-gray-700 line-clamp-4 overflow-hidden" v-html="renderMarkdown(note.content)"></div>
            <div class="text-xs text-gray-400 mt-3">{{ formatDate(note.updated_at || note.created_at) }}</div>
          </div>
        </div>
      </div>

      <!-- Regular notes -->
      <div v-if="regularNotes.length > 0">
        <h3 v-if="pinnedNotes.length > 0" class="text-sm font-semibold text-gray-500 mb-3">便签</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="note in regularNotes"
            :key="note.id"
            class="rounded-xl p-4 shadow-sm border cursor-pointer hover:shadow-md transition-all min-h-[120px] flex flex-col"
            :style="{ backgroundColor: noteColor(note.color), borderColor: noteColor(note.color) }"
            @click="openEdit(note)"
          >
            <div class="flex items-start justify-between gap-2">
              <h4 class="font-semibold text-gray-900 text-sm">{{ note.title || '无标题' }}</h4>
              <button @click.stop="togglePin(note)" class="p-1 hover:bg-white/50 rounded transition-colors" title="置顶">
                <span class="text-sm opacity-30">📌</span>
              </button>
            </div>
            <div class="flex-1 mt-2 text-sm text-gray-700 line-clamp-4 overflow-hidden" v-html="renderMarkdown(note.content)"></div>
            <div class="text-xs text-gray-400 mt-3">{{ formatDate(note.updated_at || note.created_at) }}</div>
          </div>
        </div>
      </div>

      <EmptyState v-if="notesStore.notes.length === 0" icon="📝" message="暂无便签，写一条吧" />
    </template>

    <!-- Add/Edit Note Modal -->
    <Modal :show="showModal" :title="editingNote ? '编辑便签' : '新建便签'" @close="closeModal">
      <form @submit.prevent="handleSave" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
          <input v-model="form.title" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none" placeholder="便签标题" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">内容（支持 Markdown）</label>
          <div class="border border-gray-200 rounded-lg overflow-hidden">
            <div class="flex bg-gray-50 border-b border-gray-200">
              <button type="button" @click="editMode = 'edit'" :class="editMode === 'edit' ? 'bg-white text-gray-900 border-b-2 border-orange-500' : 'text-gray-500'" class="px-4 py-2 text-sm font-medium transition-colors">
                编辑
              </button>
              <button type="button" @click="editMode = 'preview'" :class="editMode === 'preview' ? 'bg-white text-gray-900 border-b-2 border-orange-500' : 'text-gray-500'" class="px-4 py-2 text-sm font-medium transition-colors">
                预览
              </button>
            </div>
            <div v-if="editMode === 'edit'" class="p-2">
              <textarea v-model="form.content" rows="8" class="w-full px-2 py-1 outline-none resize-none text-sm font-mono" placeholder="在这里写内容..."></textarea>
            </div>
            <div v-else class="p-4 min-h-[200px] prose prose-sm max-w-none" v-html="renderMarkdown(form.content)"></div>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">颜色</label>
          <div class="flex gap-2">
            <button v-for="c in noteColors" :key="c.value" type="button" @click="form.color = c.value" class="w-8 h-8 rounded-full border-2 transition-all" :class="form.color === c.value ? 'border-gray-900 scale-110' : 'border-transparent'" :style="{ backgroundColor: c.bg }" :title="c.label"></button>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <input type="checkbox" v-model="form.pinned" id="note-pin" class="w-4 h-4 rounded border-gray-300 text-orange-500 focus:ring-orange-500" />
          <label for="note-pin" class="text-sm text-gray-700">置顶</label>
        </div>
        <div class="flex gap-3">
          <button type="submit" :disabled="saving" class="flex-1 py-2.5 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 transition-colors">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <button v-if="editingNote" type="button" @click="handleDelete" class="px-4 py-2.5 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors">
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
import { useNotesStore } from '@/stores/notes'
import Modal from '@/components/Modal.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import EmptyState from '@/components/EmptyState.vue'

const notesStore = useNotesStore()

const showModal = ref(false)
const showConfirm = ref(false)
const confirmMessage = ref('')
const editingNote = ref(null)
const saving = ref(false)
const editMode = ref('edit')
let pendingConfirmAction = null

const form = ref({ title: '', content: '', color: 'yellow', pinned: false })

const noteColors = [
  { value: 'yellow', label: '黄色', bg: '#FEF3C7' },
  { value: 'green', label: '绿色', bg: '#D1FAE5' },
  { value: 'blue', label: '蓝色', bg: '#DBEAFE' },
  { value: 'pink', label: '粉色', bg: '#FCE7F3' },
  { value: 'purple', label: '紫色', bg: '#EDE9FE' },
  { value: 'orange', label: '橙色', bg: '#FED7AA' },
]

const noteColorMap = {
  yellow: '#FEF3C7',
  green: '#D1FAE5',
  blue: '#DBEAFE',
  pink: '#FCE7F3',
  purple: '#EDE9FE',
  orange: '#FED7AA',
}

function noteColor(c) {
  return noteColorMap[c] || noteColorMap.yellow
}

const pinnedNotes = computed(() => notesStore.notes.filter((n) => n.pinned).sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)))
const regularNotes = computed(() => notesStore.notes.filter((n) => !n.pinned).sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)))

function formatDate(date) {
  if (!date) return ''
  return dayjs(date).format('M月D日 HH:mm')
}

function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Headers
    .replace(/^### (.*$)/gm, '<h4 class="text-base font-bold mt-2 mb-1">$1</h4>')
    .replace(/^## (.*$)/gm, '<h3 class="text-lg font-bold mt-2 mb-1">$1</h3>')
    .replace(/^# (.*$)/gm, '<h2 class="text-xl font-bold mt-2 mb-1">$1</h2>')
    // Lists
    .replace(/^- (.*$)/gm, '<li class="ml-4">$1</li>')
    // Line breaks
    .replace(/\n/g, '<br>')
  return html
}

function openAdd() {
  editingNote.value = null
  form.value = { title: '', content: '', color: 'yellow', pinned: false }
  editMode.value = 'edit'
  showModal.value = true
}

function openEdit(note) {
  editingNote.value = note
  form.value = {
    title: note.title || '',
    content: note.content || '',
    color: note.color || 'yellow',
    pinned: note.pinned || false,
  }
  editMode.value = 'edit'
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingNote.value = null
  form.value = { title: '', content: '', color: 'yellow', pinned: false }
}

async function handleSave() {
  saving.value = true
  try {
    if (editingNote.value) {
      await notesStore.updateNote(editingNote.value.id, form.value)
    } else {
      await notesStore.createNote(form.value)
    }
    closeModal()
  } catch {
    // handled
  } finally {
    saving.value = false
  }
}

function handleDelete() {
  if (!editingNote.value) return
  confirmMessage.value = `确定要删除便签「${editingNote.value.title || '无标题'}」吗？`
  pendingConfirmAction = async () => {
    await notesStore.deleteNote(editingNote.value.id)
    closeModal()
  }
  showConfirm.value = true
}

async function togglePin(note) {
  try {
    await notesStore.updateNote(note.id, { ...note, pinned: !note.pinned })
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
  notesStore.fetchNotes()
})
</script>
