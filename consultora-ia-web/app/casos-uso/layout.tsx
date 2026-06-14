import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Casos de Uso de IA para Empresas | Automatización Procesos IA',
  description:
    'Descubre cómo empresas como la tuya aplican inteligencia artificial: automatización de pedidos, atención al cliente 24/7, análisis de datos y más. Casos reales con resultados medibles.',
  keywords: [
    'casos de uso inteligencia artificial',
    'IA empresas ejemplos',
    'automatización casos reales',
    'chatbot empresa',
    'agentes IA casos uso',
    'ejemplos automatización pymes',
  ],
  openGraph: {
    title: 'Casos de Uso de IA para Empresas | Automatización Procesos IA',
    description:
      'Casos reales de empresas que ya usan IA: ahorro de tiempo, reducción de errores y más ventas. Descubre qué puedes automatizar tú también.',
    url: 'https://www.automatizacionprocesos.es/casos-uso',
    type: 'website',
    locale: 'es_ES',
    siteName: 'Automatización Procesos IA',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Casos de uso IA para empresas' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Casos de Uso de IA para Empresas',
    description: 'Casos reales de IA aplicada en empresas: automatización, agentes IA y chatbots con resultados medibles.',
    images: ['/og-image.png'],
  },
  alternates: {
    canonical: 'https://www.automatizacionprocesos.es/casos-uso',
  },
}

export default function CasosUsoLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
