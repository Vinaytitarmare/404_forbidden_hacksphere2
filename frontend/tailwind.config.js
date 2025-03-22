/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      screens: {
        'mid-lg': '920px',
        'beech-lg': '1070px',
        'near-lg': '1300px', // Custom breakpoint between md and lg
      },
    },
  },
  plugins: [require("flowbite/plugin")], // ✅ Add Flowbite plugin
}

