import react from "@vitejs/plugin-react-swc"
import path from "node:path"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from "vite"
import { viteSingleFile } from "vite-plugin-singlefile"

const REPORT_DIR = "octobot_script/resources/report"

export default defineConfig({
  root: REPORT_DIR,
  plugins: [tailwindcss(), react(), viteSingleFile()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, REPORT_DIR, "src"),
    },
  },
  build: {
    outDir: path.resolve(__dirname, REPORT_DIR, "dist"),
    emptyOutDir: true,
    chunkSizeWarningLimit: 10000,
  },
})
