import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  preview: {
    allowedHosts: ['app-dev-front-chatbot-finsa-hhcgfwf9e0axf8ek.westeurope-01.azurewebsites.net']
  }
})
