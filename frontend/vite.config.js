import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath } from 'url'

export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  plugins: [
    tailwindcss(),
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Hearth',
        short_name: 'Hearth',
        description: '家庭生活管理中心',
        theme_color: '#E8590C',
        background_color: '#FFF5EB',
        display: 'standalone',
        // TODO: 替换为实际图标文件，放入 frontend/public/ 目录
        // icons: [
        //   { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
        //   { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
        // ],
      },
    }),
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8090',
    },
  },
})
