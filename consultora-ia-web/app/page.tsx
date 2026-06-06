import type { Metadata } from 'next'
import Hero from '@/components/home/Hero'
import Problems from '@/components/home/Problems'
import Solutions from '@/components/home/Solutions'
import ServicesGrid from '@/components/home/ServicesGrid'
import HowWeWork from '@/components/home/HowWeWork'
import UseCases from '@/components/home/UseCases'
import Benefits from '@/components/home/Benefits'
import ExternalConsultant from '@/components/home/ExternalConsultant'
import Testimonials from '@/components/home/Testimonials'
import FAQ from '@/components/home/FAQ'
import CTAFinal from '@/components/home/CTAFinal'

export const metadata: Metadata = {
  title: 'AP Automatización IA | Consultoría de Inteligencia Artificial para Empresas | IA Práctica para Pymes',
  description:
    'AP Automatización IA ayuda a empresas y pymes a implementar inteligencia artificial de forma práctica: automatización de procesos, agentes IA, auditoría IA y formación. Sin tecnicismos, con resultados medibles.',
  keywords: [
    'consultoría IA',
    'inteligencia artificial para empresas',
    'automatización procesos IA',
    'agentes IA pymes',
    'consultor IA externo',
    'auditoría IA',
    'formación inteligencia artificial',
    'IA para pymes España',
  ],
  openGraph: {
    title: 'AP Automatización IA | Consultoría de Inteligencia Artificial para Empresas',
    description:
      'El experto en IA que tu empresa todavía no tiene en plantilla. Ayudamos a pymes a implementar IA de forma práctica y con resultados medibles.',
    type: 'website',
    locale: 'es_ES',
  },
  alternates: {
    canonical: 'https://www.automatizacionprocesos.es',
  },
}

const jsonLdProfessionalService = {
  '@context': 'https://schema.org',
  '@type': 'ProfessionalService',
  name: 'AP Automatización IA',
  description:
    'Consultoría de Inteligencia Artificial para empresas y pymes. Automatización de procesos, agentes IA, auditoría IA y formación.',
  url: 'https://www.automatizacionprocesos.es',
  telephone: '+34 900 000 000',
  areaServed: {
    '@type': 'Country',
    name: 'España',
  },
  hasOfferCatalog: {
    '@type': 'OfferCatalog',
    name: 'Servicios de Consultoría IA',
    itemListElement: [
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Consultoría IA',
          description: 'Estrategia y asesoramiento experto en inteligencia artificial para empresas.',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Automatización de Procesos',
          description: 'Automatización de tareas repetitivas mediante IA y herramientas de RPA.',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Agentes IA',
          description: 'Desarrollo de agentes inteligentes personalizados para empresas.',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Auditoría IA',
          description: 'Análisis de procesos y detección de oportunidades de mejora con IA.',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Formación IA',
          description: 'Programas formativos en inteligencia artificial para equipos empresariales.',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Consultor IA Externo',
          description: 'Servicio mensual de acompañamiento como consultor IA externo sin coste de plantilla.',
        },
      },
    ],
  },
}

const jsonLdFAQ = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: '¿Necesito conocimientos técnicos para trabajar con AP Automatización IA?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'En absoluto. Nos adaptamos a vuestro lenguaje y explicamos todo sin tecnicismos. Vosotros nos contáis vuestros problemas de negocio y nosotros nos encargamos de la parte técnica.',
      },
    },
    {
      '@type': 'Question',
      name: '¿Cuánto tiempo lleva ver resultados con la IA?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'En la mayoría de los casos los primeros resultados se ven en 4 a 8 semanas desde el inicio de la implementación. Las automatizaciones sencillas pueden estar operativas en días.',
      },
    },
    {
      '@type': 'Question',
      name: '¿Trabajáis solo con grandes empresas?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'No. La mayoría de nuestros clientes son pymes de entre 5 y 100 empleados. Adaptamos nuestras soluciones y precios al tamaño real de tu empresa.',
      },
    },
    {
      '@type': 'Question',
      name: '¿Cuánto cuesta una consultoría IA?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'El diagnóstico inicial es gratuito. Una auditoría básica empieza desde 1.500€. Los proyectos de automatización o agentes IA suelen estar entre 3.000€ y 15.000€ según complejidad.',
      },
    },
    {
      '@type': 'Question',
      name: '¿Cómo funciona el servicio de Consultor IA externo?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Es un servicio de acompañamiento mensual que incluye reunión mensual, soporte continuo, supervisión de automatizaciones e identificación de nuevas oportunidades. Sin permanencia mínima.',
      },
    },
  ],
}

export default function HomePage() {
  return (
    <>
      {/* Schema.org structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdProfessionalService) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdFAQ) }}
      />

      <main>
        <Hero />
        <Problems />
        <Solutions />
        <ServicesGrid />
        <HowWeWork />
        <UseCases />
        <Benefits />
        <ExternalConsultant />
        <Testimonials />
        <FAQ />
        <CTAFinal />
      </main>
    </>
  )
}
