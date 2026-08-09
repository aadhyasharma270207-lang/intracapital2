/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#020617',
        cardBg: 'rgba(15, 23, 42, 0.65)',
        accentBlue: '#2563eb',
        accentCyan: '#0891b2',
        accentPurple: '#7c3aed',
      }
    },
  },
  plugins: [],
}
