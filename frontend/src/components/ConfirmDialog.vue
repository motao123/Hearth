<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="$emit('cancel')"></div>
        <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-sm z-10 p-6">
          <p class="text-gray-800 text-center mb-6">{{ message }}</p>
          <div class="flex gap-3 justify-center">
            <button @click="$emit('cancel')" class="px-5 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors">
              取消
            </button>
            <button @click="$emit('confirm')" class="px-5 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors">
              确认
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  message: { type: String, default: '确定要执行此操作吗？' },
})
defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.25s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
