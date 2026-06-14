import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Contacto | Consultoría IA Valencia | Automatización Procesos IA',
  description:
    'Contacta con nuestra consultoría de IA en Valencia. Automatización de procesos, agentes IA y formación para empresas en España. Respondemos en menos de 24 horas laborables.',
  keywords: [
    'consultoría IA Valencia',
    'automatización procesos Valencia',
    'contacto consultor IA',
    'agentes IA Valencia',
    'consultor inteligencia artificial España',
    'contacto automatización procesos',
  ],
  openGraph: {
    title: 'Contacto | Consultoría IA Valencia | Automatización Procesos IA',
    description:
      'Contacta con Automatización Procesos IA. Expertos en IA para empresas en Valencia y toda España. Respondemos en menos de 24 horas.',
    url: 'https://www.automatizacionprocesos.es/contacto',
    type: 'website',
    locale: 'es_ES',
    siteName: 'Automatización Procesos IA',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Contacto consultoría IA Valencia' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Contacto | Consultoría IA Valencia',
    description:
      'Contacta con nuestra consultoría IA en Valencia. Automatización de procesos e inteligencia artificial para empresas.',
    images: ['/og-image.png'],
  },
  alternates: { canonical: 'https://www.automatizacionprocesos.es/contacto' },
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
  sameAs: [
    'https://www.linkedin.com/company/apautomatizacion',
    'https://twitter.com/apautomatizacion_es',
  ],
}

export default function ContactoLayout({ children }: { children: React.ReactNode }) {
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
