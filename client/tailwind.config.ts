import type { Config } from 'tailwindcss';

export default {
    darkMode: 'class',
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            colors: {
                civic: {
                    900: '#1e293b', // Dark sidebar
                    800: '#334155',
                    teal: '#14b8a6', // Primary accent
                    tealDark: '#0f766e',
                    light: '#f8fafc',
                }
            }
        }
    },
    plugins: [],
} satisfies Config;
