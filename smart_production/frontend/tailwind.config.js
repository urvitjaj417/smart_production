/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Same industrial palette used in the HTML prototype's light theme
        bg0: '#f4f6f7',
        bg1: '#ffffff',
        bg2: '#f9fafb',
        bg3: '#f1f3f4',
        line: '#e2e6e8',
        line2: '#d1d7da',
        acc: '#2ec4b6',
        green: '#15803d',
        orange: '#b45309',
        red: '#c53a34',
        purp: '#6d28d9',
        teal: '#0d7a6b',
        t0: '#1a2226',
        t1: '#3f484d',
        t2: '#5c666b',
      },
    },
  },
  plugins: [],
};
