/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable dark mode by default/class strategy
  theme: {
    extend: {
      colors: {
        background: '#0F172A', // Deep space dark
        surface: '#1E293B',    // Slate surface
        primary: '#6366F1',    // Indigo/electric blue
        accent: '#A855F7',     // Purple startup vibe
        textMain: '#F8FAFC',
        textMuted: '#94A3B8'
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
