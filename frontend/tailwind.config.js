/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#F7F8FA',
        surface: '#FFFFFF',
        'surface-subtle': '#F2F4F7',
        navy: {
          DEFAULT: '#102A43',
          dark: '#0A1C2E',
          soft: '#243B53',
        },
        slate: {
          muted: '#526174',
          subtle: '#829AB1',
          border: '#DCE3EA',
          line: '#E7ECF0',
        },
        blue: {
          primary: '#0070E0',
          hover: '#005CB9',
          soft: '#EAF3FC',
          border: '#BFDCF8',
          dark: '#004C99',
        },
        accent: {
          forest: '#1E4D2B',
          'forest-bg': '#EEF4EF',
          'forest-border': '#C9DEC9',
          amber: '#8A5B10',
          'amber-bg': '#FAF4EB',
          'amber-border': '#ECDBC3',
          crimson: '#8C2522',
          'crimson-bg': '#FBF0F0',
          'crimson-border': '#EFC9C8',
        },
      },
      fontFamily: {
        serif: ['"DM Serif Display"', 'Playfair Display', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      boxShadow: {
        xs: '0 1px 2px 0 rgba(16, 42, 67, 0.05)',
      },
    },
  },
  plugins: [],
}
