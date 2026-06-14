import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Diagnóstico Gratuito IA para tu Empresa | Consultor IA Valencia',
  description:
    'Diagnóstico gratuito IA en 30 minutos para tu empresa. Nuestro consultor IA en Valencia analiza tus procesos e identifica dónde la inteligencia artificial te ahorra tiempo y dinero.',
  keywords: [
    'diagnóstico gratuito IA empresa',
    'consultor IA Valencia',
    'diagnóstico inteligencia artificial',
    'consultoría IA gratuita',
    'análisis procesos IA',
  ],
  alternates: { canonical: 'https://www.automatizacionprocesos.es/diagnostico-gratuito' },
  openGraph: {
    title: 'Diagnóstico Gratuito IA para tu Empresa | Consultor IA Valencia',
    description: 'Diagnóstico gratuito IA en 30 minutos. Identifica dónde la inteligencia artificial puede ahorrar tiempo y dinero en tu empresa.',
    url: 'https://www.automatizacionprocesos.es/diagnostico-gratuito',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Diagnóstico gratuito de IA' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Diagnóstico Gratuito IA para tu Empresa | Consultor IA Valencia',
    description: 'Diagnóstico gratuito IA en 30 minutos. Sin compromiso.',
    images: ['/og-image.png'],
  },
}

export default function DiagnosticoLayout({ children }: { children: React.ReactNode }) {
  return children
}
