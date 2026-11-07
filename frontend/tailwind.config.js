/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          900: '#0B0F17',
          800: '#111827',
          700: '#1F2937',
          600: '#374151',
          500: '#4B5563',
          accent: '#0284C7',
          glow: '#38BDF8',
          success: '#10B981',
          warning: '#F59E0B',
          critical: '#EF4444'
        }
      }
    },
  },
  plugins: [],
}
