import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  clearScreen: false,
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
  },
  build: {
    rollupOptions: {
      // Prevents Vite/Rollup from failing if w.ts or w.js is resolved at runtime
      external: ["w.ts", "w.js"],
    },
  },
});