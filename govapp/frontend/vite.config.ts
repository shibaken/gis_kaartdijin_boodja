import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom'
  },
  build: {
	outDir: "../",
	emptyOutDir: false,
	manifest: false,
	sourcemap: false,
        rollupOptions: {
          output: {
            entryFileNames: `static/webapp/assets/[name].js`,
            chunkFileNames: `static/webapp/assets/[name].js`,
            assetFileNames: `static/webapp/assets/[name].[ext]`
          }
        }
  },
  server: {
    host: true,
    port: 9072,
    strictPort: true,
    proxy: {
      '/api': {
        target: `http://localhost:9071`,
        changeOrigin: true,
      },
     }
  }
})

