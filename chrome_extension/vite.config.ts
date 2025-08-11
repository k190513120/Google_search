import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { copyFileSync, mkdirSync, existsSync } from 'fs'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'copy-manifest',
      writeBundle() {
        // 复制 manifest.json
        copyFileSync('manifest.json', 'dist/manifest.json')
        
        // 复制 icons 目录
        if (!existsSync('dist/icons')) {
          mkdirSync('dist/icons', { recursive: true })
        }
        copyFileSync('public/icons/icon16.png', 'dist/icons/icon16.png')
        copyFileSync('public/icons/icon48.png', 'dist/icons/icon48.png')
        copyFileSync('public/icons/icon128.png', 'dist/icons/icon128.png')
      }
    }
  ],
  build: {
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'popup.html'),
        background: resolve(__dirname, 'src/background.ts'),
        content: resolve(__dirname, 'src/content.ts')
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  }
})