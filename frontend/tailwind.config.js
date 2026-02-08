/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      keyframes: {
        'ping-pause': {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '30%': { transform: 'scale(2)', opacity: '0' },
          '100%': { transform: 'scale(2)', opacity: '0' },
        },
      },
      animation: {
        'ping-slow': 'ping-pause 3s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
    },
  },
  plugins: [],
}
