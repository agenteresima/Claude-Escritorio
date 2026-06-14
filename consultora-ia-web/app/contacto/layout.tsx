import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Contacto | Consultoría IA Valencia | Automatización Procesos IA',
  description:
    'Contacta con nuestra consultoría de IA en Valencia. Automatización de procesos, agentes IA y formación para empresas. Respondemos en menos de 24 horas.',
  keywords: ['consultoría IA Valencia', 'automatización procesos Valencia', 'contacto consultor IA', 'agentes IA Valencia'],
  openGraph: {
    title: 'Contacto | Consultoría IA Valencia',
    description: 'Contacta con Automatización Procesos IA. Expertos en IA para empresas en Valencia y toda España.',
    url: 'https://www.automatizacionprocesos.es/contacto',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Contacto consultoría IA Valencia' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Contacto | Consultoría IA Valencia',
    description: 'Contacta con nuestra consultoría IA en Valencia. Respondemos en menos de 24h.',
    images: ['/og-image.png'],
  },
  alternates: { canonical: 'https://www.automatizacionprocesos.es/contacto' },
}

export default function ContactoLayout({ children }: { children: React.ReactNode }) {
  return children
}
