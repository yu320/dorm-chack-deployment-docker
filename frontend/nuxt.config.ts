// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  app: {
    pageTransition: { name: 'page', mode: 'out-in' }
  },

  // Security Headers
  routeRules: {
    '/**': {
      headers: {
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' https://api.iconify.design http://localhost:8000 ws://localhost:3000;",
        'X-Frame-Options': 'SAMEORIGIN',
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
      }
    }
  },

  // Add runtime config for API endpoint
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000', // Point directly to backend instead of using proxy
    }
  },

  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n',
    '@vite-pwa/nuxt',
    '@nuxt/icon'
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
