import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Diagnóstico Gratuito IA para tu Empresa | Consultor IA Valencia',
  description:
    'Solicita tu diagnóstico gratuito de IA en Valencia. Videollamada de 30 min: analizamos tu empresa, identificamos oportunidades de automatización y te damos una hoja de ruta sin coste.',
  keywords: ['diagnóstico gratuito IA empresa', 'consultor IA Valencia', 'auditoría IA gratis', 'automatización procesos Valencia'],
  openGraph: {
    title: 'Diagnóstico Gratuito de IA para tu Empresa',
    description: 'Videollamada de 30 min gratuita: identificamos las mejores oportunidades de automatización IA para tu empresa. Sin coste. Sin compromiso.',
    url: 'https://www.automatizacionprocesos.es/diagnostico-gratuito',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Diagnóstico gratuito IA' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Diagnóstico Gratuito de IA para tu Empresa',
    description: 'Videollamada gratuita de 30 min para identificar oportunidades de automatización IA en tu empresa.',
    images: ['/og-image.png'],
  },
  alternates: { canonical: 'https://www.automatizacionprocesos.es/diagnostico-gratuito' },
}

export default function DiagnosticoLayout({ children }: { children: React.ReactNode }) {
  return children
}
