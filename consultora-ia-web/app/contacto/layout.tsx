import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Consultoría IA Valencia | Contacto Automatización Procesos IA',
  description:
    'Contacta con nuestra consultoría IA en Valencia. Resolvemos tus dudas sobre automatización de procesos, agentes IA y transformación digital para empresas. Respuesta en 24h.',
  keywords: [
    'consultoría IA Valencia',
    'automatización procesos Valencia',
    'contacto consultor IA',
    'contacto automatización IA',
    'expertos IA Valencia',
  ],
  alternates: { canonical: 'https://www.automatizacionprocesos.es/contacto' },
  openGraph: {
    title: 'Consultoría IA Valencia | Contacto Automatización Procesos IA',
    description: 'Contacta con nuestra consultoría IA en Valencia. Respondemos en menos de 24 horas.',
    url: 'https://www.automatizacionprocesos.es/contacto',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Contacto Automatización Procesos IA' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Consultoría IA Valencia | Contacto',
    description: 'Contacta con nuestra consultoría IA en Valencia. Respondemos en 24h.',
    images: ['/og-image.png'],
  },
}

export default function ContactoLayout({ children }: { children: React.ReactNode }) {
  return children
}
