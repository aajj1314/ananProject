import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 8081,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },
  build: {
    /** 代码分割策略：将第三方库拆分为独立chunk，利用浏览器缓存 */
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'lucide-icons': ['lucide-vue-next'],
          'axios-vendor': ['axios'],
        },
      },
    },
    /** 单个chunk大小警告阈值（KB） */
    chunkSizeWarningLimit: 500,
    /** 启用CSS代码分割，按组件懒加载CSS */
    cssCodeSplit: true,
    /** 生产环境移除console和debugger */
    minify: 'esbuild',
    /** 构建目标为现代浏览器，生成更小的产物 */
    target: 'es2020',
    /** 启用Rollup的模块预加载，优化首屏加载 */
    modulePreload: {
      polyfill: false,
    },
  },
})
