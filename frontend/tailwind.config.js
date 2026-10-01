/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: { extend: {
    colors: { background: 'hsl(var(--background) / <alpha-value>)', surface: 'hsl(var(--surface) / <alpha-value>)', elevated: 'hsl(var(--elevated) / <alpha-value>)', border: 'hsl(var(--border) / <alpha-value>)', foreground: 'hsl(var(--foreground) / <alpha-value>)', muted: 'hsl(var(--muted) / <alpha-value>)', classical: 'hsl(var(--classical) / <alpha-value>)', quantum: 'hsl(var(--quantum) / <alpha-value>)', warning: 'hsl(var(--warning) / <alpha-value>)', danger: 'hsl(var(--danger) / <alpha-value>)', success: 'hsl(var(--success) / <alpha-value>)' },
    fontFamily: { heading: ['Sora', 'sans-serif'], body: ['IBM Plex Sans', 'sans-serif'], mono: ['JetBrains Mono', 'monospace'] },
    borderRadius: { card: '8px', input: '4px' },
  } },
  plugins: [],
};
