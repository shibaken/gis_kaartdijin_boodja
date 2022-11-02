import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

var port = 9072;
if (process.env.PORT) {
    port = process.env.PORT;
}
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
    port: port,
    strictPort: true,
  }
})

