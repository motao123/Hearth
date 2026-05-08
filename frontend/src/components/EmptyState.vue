<template>
  <div class="flex flex-col items-center justify-center py-12 text-gray-400">
    <span class="text-5xl mb-4">{{ icon }}</span>
    <p class="text-base">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📭' },
  message: { type: String, default: '暂无数据' },
})
</script>
