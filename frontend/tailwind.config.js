/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        telecom: {
          dark: '#0a0d14',
          panel: '#121722',
          border: '#1f293d',
          accent: '#00f0ff',
          neon: '#7000ff',
          danger: '#ff2a5f',
          warning: '#ffb800',
          success: '#00e676'
        }
      }
    },
  },
  plugins: [],
}
