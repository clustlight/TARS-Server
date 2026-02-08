import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  const backendUrl = env.VITE_BACKEND_URL || 'http://localhost:3880'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/recordings': backendUrl,
        '/subscriptions': backendUrl,
        '/users': backendUrl
      }
    }
  }
})
