/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./nuxt.config.{js,ts}",
    "./app.vue",
  ],
  theme: {
    extend: {
      colors: {
        primary: { // Teal color palette
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#06b6d4', // Main teal
          600: '#0891b2',
          700: '#0e7490',
          800: '#0f766e', // A bit darker, more greenish teal
          900: '#115e59',
        },
        // Optionally add a slate/gray for background as mentioned in gemini.md
        // bg-slate-50 is already a default tailwind color, so no explicit definition needed here
      },
    },
  },
  plugins: [],
}
