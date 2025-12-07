/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#3b82f6',
                secondary: '#10b981',
                surface: '#18181b', // Zinc-900
                // Ethereal Theme
                void: '#050505', // Almost Black
                glass: 'rgba(255, 255, 255, 0.05)',
                'neon-blue': '#3b82f6',
                'neon-green': '#10b981',
                'neon-pink': '#ec4899',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['Space Mono', 'monospace'],
            },
            animation: {
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
            },
            keyframes: {
                glow: {
                    '0%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)' },
                    '100%': { boxShadow: '0 0 40px rgba(59, 130, 246, 0.8), 0 0 80px rgba(59, 130, 246, 0.4)' },
                }
            }
        },
    },
    plugins: [],
}
