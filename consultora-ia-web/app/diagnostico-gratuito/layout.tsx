import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Diagnóstico Gratuito IA para Empresas | Consultor IA Valencia',
  description:
    'Diagnóstico gratuito de IA para tu empresa en Valencia. Videollamada de 30 min: analizamos tus procesos, detectamos oportunidades de automatización y te damos una hoja de ruta. Sin coste ni compromiso.',
  keywords: [
    'diagnóstico gratuito IA empresa',
    'consultor IA Valencia',
    'auditoría IA gratis',
    'automatización procesos Valencia',
    'consultoría IA gratuita',
    'asesoramiento IA pymes',
    'diagnóstico inteligencia artificial',
  ],
  openGraph: {
    title: 'Diagnóstico Gratuito de IA para tu Empresa | Consultor IA Valencia',
    description:
      'Videollamada gratuita de 30 min: identificamos las mejores oportunidades de automatización IA para tu empresa. Sin coste. Sin compromiso.',
    url: 'https://www.automatizacionprocesos.es/diagnostico-gratuito',
    type: 'website',
    locale: 'es_ES',
    siteName: 'Automatización Procesos IA',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Diagnóstico gratuito IA para empresas' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Diagnóstico Gratuito de IA para tu Empresa',
    description:
      'Videollamada gratuita de 30 min para identificar oportunidades de automatización IA en tu empresa en Valencia.',
    images: ['/og-image.png'],
  },
  alternates: { canonical: 'https://www.automatizacionprocesos.es/diagnostico-gratuito' },
}

const localBusinessSchema = {
  '@context': 'https://schema.org',
  '@type': 'LocalBusiness',
  name: 'Automatización Procesos IA',
  description: 'Consultoría de Inteligencia Artificial para empresas y pymes en Valencia, España.',
  url: 'https://www.automatizacionprocesos.es',
  telephone: '+34-963-000-000',
  email: 'admin@automatizacionprocesos.es',
  address: {
    '@type': 'PostalAddress',
    addressLocality: 'Valencia',
    addressRegion: 'Valencia',
    postalCode: '46001',
    addressCountry: 'ES',
  },
  geo: {
    '@type': 'GeoCoordinates',
    latitude: '39.4699',
    longitude: '-0.3763',
  },
  openingHoursSpecification: [
    {
      '@type': 'OpeningHoursSpecification',
      dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      opens: '09:00',
      closes: '18:00',
    },
  ],
  priceRange: '€€',
  areaServed: { '@type': 'Country', name: 'España' },
  hasOfferCatalog: {
    '@type': 'OfferCatalog',
    name: 'Diagnóstico Gratuito IA',
    itemListElement: [
      {
        '@type': 'Offer',
        name: 'Diagnóstico gratuito de automatización IA',
        description:
          'Videollamada gratuita de 30 minutos para identificar oportunidades de automatización con IA en tu empresa.',
        price: '0',
        priceCurrency: 'EUR',
      },
    ],
  },
}

export default function DiagnosticoLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(localBusinessSchema) }}
      />
      {children}
    </>
  )
}
