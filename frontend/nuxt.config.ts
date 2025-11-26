// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  compatibilityDate: '2025-07-15',
  devtools: { enabled: process.env.NODE_ENV !== 'production' },

  app: {
    pageTransition: { name: 'page', mode: 'out-in' }
  },

  // Add runtime config for API endpoint
  runtimeConfig: {
    public: {
      apiBase: '', // API calls are now proxied by Vite, so this should be empty
    }
  },

  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n',
    '@vite-pwa/nuxt'
  ],

  pwa: {
    manifest: {
      name: 'Dormitory Check',
      short_name: 'DormCheck',
      description: 'Dormitory Inspection and Reporting System',
      theme_color: '#009696',
      icons: [
        {
          src: 'pwa-192x192.png',
          sizes: '192x192',
          type: 'image/png',
        },
        {
          src: 'pwa-512x512.png',
          sizes: '512x512',
          type: 'image/png',
        },
        {
          src: 'pwa-512x512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'any maskable',
        },
      ],
    },
    workbox: {
      globPatterns: ['**/*.{js,css,html,png,svg,ico}'],
    },
    devOptions: {
      enabled: true,
      type: 'module',
    },
  },

  i18n: {
    locales: [
      {
        code: 'en',
        file: 'en.json',
        name: 'English'
      },
      {
        code: 'zh',
        file: 'zh.json',
        name: '繁體中文'
      }
    ],
    lazy: false,
    langDir: 'locales',
    strategy: 'prefix_except_default',
    defaultLocale: 'zh',
    detectBrowserLanguage: false,

    // ✨ 防止 unplugin-vue-i18n 將 email1@example.com 誤判為 linked message
    compilation: {
      strictMessage: false
    }
  },

  css: ['~/assets/css/tailwind.css'],

  vite: {
    server: {
      proxy: {
        // Proxy /api/** requests to our backend server
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        }
      }
    },
    esbuild: {
      drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
    }
  },
})
