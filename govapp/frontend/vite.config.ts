/// <reference types="vitest" />
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const port = process.env.PORT ? parseInt(process.env.PORT) : 9072;

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue({
    reactivityTransform: true
  })],
  test: {
    globals: true,
    environment: "happy-dom"
  },
  build: {
	outDir: "../",
	emptyOutDir: false,
	manifest: false,
	sourcemap: false,
        rollupOptions: {
          output: {
            entryFileNames: "static/webapp/assets/[name].js",
            chunkFileNames: "static/webapp/assets/[name].js",
            assetFileNames: "static/webapp/assets/[name].[ext]"
          }
        }
  },
  server: {
    host: true,
    port,
    strictPort: true
  }
});

