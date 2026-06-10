import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Paleta principal Automatización Procesos IA
        navy: {
          950: '#060D1A',
          900: '#0F172A',
          800: '#1E293B',
          700: '#27374D',
          600: '#334155',
        },
        brand: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        surface: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
        },
        success: {
          400: '#34D399',
          500: '#10B981',
          600: '#059669',
        },
        accent: {
          purple: '#7C3AED',
          cyan: '#06B6D4',
          amber: '#F59E0B',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'hero-pattern':
          "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%232563EB' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        'mesh-gradient':
          'linear-gradient(135deg, #0F172A 0%, #1E293B 40%, #0F172A 100%)',
      },
      boxShadow: {
        'brand-sm': '0 2px 8px rgba(37, 99, 235, 0.15)',
        brand: '0 4px 20px rgba(37, 99, 235, 0.25)',
        'brand-lg': '0 8px 40px rgba(37, 99, 235, 0.35)',
        'card': '0 1px 3px rgba(0,0,0,0.05), 0 4px 16px rgba(0,0,0,0.08)',
        'card-hover': '0 4px 8px rgba(0,0,0,0.06), 0 12px 32px rgba(0,0,0,0.12)',
        'glow': '0 0 40px rgba(37, 99, 235, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'slide-in-right': 'slideInRight 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'gradient': 'gradient 8s ease infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '88': '22rem',
        '104': '26rem',
        '112': '28rem',
        '128': '32rem',
      },
      transitionDuration: {
        '400': '400ms',
      },
    },
  },
  plugins: [],
}

export default config
