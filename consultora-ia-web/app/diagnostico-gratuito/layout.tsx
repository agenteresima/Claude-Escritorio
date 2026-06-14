export const metadata = {
  title: 'Diagnóstico Gratuito IA para Empresas | Consultor IA Valencia',
  description:
    'Solicita tu diagnóstico gratuito de IA. Consultor IA en Valencia analiza tu empresa e identifica las mejores oportunidades de automatización. Sin compromiso en 30 minutos.',
  keywords: [
    'diagnóstico gratuito IA empresa',
    'consultor IA Valencia',
    'auditoría IA gratuita',
    'consultoría IA pymes gratis',
  ],
  openGraph: {
    title: 'Diagnóstico Gratuito IA para Empresas | Consultor IA Valencia',
    description:
      'Solicita tu diagnóstico gratuito de IA. Consultor IA en Valencia analiza tu empresa e identifica las mejores oportunidades de automatización. Sin compromiso en 30 minutos.',
    url: 'https://www.automatizacionprocesos.es/diagnostico-gratuito',
    images: [
      {
        url: 'https://www.automatizacionprocesos.es/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Diagnóstico Gratuito IA para Empresas',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Diagnóstico Gratuito IA para Empresas | Consultor IA Valencia',
    description:
      'Solicita tu diagnóstico gratuito de IA. Consultor IA en Valencia analiza tu empresa. Sin compromiso en 30 minutos.',
    images: ['https://www.automatizacionprocesos.es/og-image.jpg'],
  },
  alternates: { canonical: 'https://www.automatizacionprocesos.es/diagnostico-gratuito' },
}

const localBusinessSchema = {
  '@context': 'https://schema.org',
  '@type': 'LocalBusiness',
  name: 'Automatización Procesos IA',
  description: 'Consultoría de inteligencia artificial para pymes en Valencia y toda España.',
  url: 'https://www.automatizacionprocesos.es',
  address: {
    '@type': 'PostalAddress',
    addressLocality: 'Valencia',
    addressRegion: 'Comunitat Valenciana',
    addressCountry: 'ES',
  },
  areaServed: {
    '@type': 'Country',
    name: 'España',
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
