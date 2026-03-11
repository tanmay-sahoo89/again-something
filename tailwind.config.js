/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2A0800',
        secondary: '#775144',
        accent: '#C09891',
        light: '#BEA8A7',
        background: '#FADBD8',
        darkBg: '#0F0F0F',
        risk: {
          low: '#10B981',
          medium: '#F59E0B',
          high: '#F97316',
          critical: '#DC2626',
        }
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
