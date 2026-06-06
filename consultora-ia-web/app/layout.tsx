import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Script from 'next/script'
import './globals.css'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import ChatBot from '@/components/bot/ChatBot'
import CookieBanner from '@/components/ui/CookieBanner'

const GA_ID = 'G-50KP99T5BP'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  metadataBase: new URL('https://www.automatizacionprocesos.es'),
  title: {
    default: 'AP Automatización IA | Consultoría de IA para Empresas',
    template: '%s | AP Automatización IA',
  },
  description:
    'AP Automatización IA es la consultoría de inteligencia artificial que tu empresa necesita. Automatizamos procesos, implantamos agentes IA y formamos a tus equipos. El experto en IA que todavía no tienes en plantilla.',
  keywords: [
    'consultoría inteligencia artificial',
    'IA para empresas',
    'automatización con IA',
    'agentes de inteligencia artificial',
    'transformación digital',
    'ChatGPT empresas',
    'machine learning empresas',
    'automatización procesos',
    'IA España',
    'consultoría IA España',
    'implementación IA',
    'estrategia de IA',
    'AP Automatización IA',
  ],
  authors: [{ name: 'AP Automatización IA', url: 'https://www.automatizacionprocesos.es' }],
  creator: 'AP Automatización IA',
  publisher: 'AP Automatización IA',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'es_ES',
    url: 'https://www.automatizacionprocesos.es',
    siteName: 'AP Automatización IA',
    title: 'AP Automatización IA | Consultoría de Inteligencia Artificial para Empresas',
    description:
      'El experto en IA que tu empresa todavía no tiene en plantilla. Automatizamos procesos, implantamos agentes IA y formamos a tus equipos.',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'AP Automatización IA — Consultoría de Inteligencia Artificial para Empresas',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AP Automatización IA | Consultoría de Inteligencia Artificial para Empresas',
    description:
      'El experto en IA que tu empresa todavía no tiene en plantilla. Automatizamos, implantamos y formamos.',
    images: ['/og-image.jpg'],
    creator: '@apautomatizacion_es',
    site: '@apautomatizacion_es',
  },
  alternates: {
    canonical: 'https://www.automatizacionprocesos.es',
    languages: {
      'es-ES': 'https://www.automatizacionprocesos.es',
    },
  },
  verification: {
    google: 'google-site-verification-token',
  },
  category: 'technology',
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': ['ProfessionalService', 'LocalBusiness'],
  name: 'AP Automatización IA',
  description:
    'Consultoría de Inteligencia Artificial para empresas. Automatización de procesos, agentes IA, formación y estrategia de IA.',
  slogan: 'El experto en IA que tu empresa todavía no tiene en plantilla',
  url: 'https://www.automatizacionprocesos.es',
  logo: 'https://www.automatizacionprocesos.es/logo.png',
  image: 'https://www.automatizacionprocesos.es/og-image.jpg',
  email: 'hola@automatizacionprocesos.es',
  telephone: '+34-900-000-000',
  address: {
    '@type': 'PostalAddress',
    addressCountry: 'ES',
    addressLocality: 'Madrid',
    addressRegion: 'Madrid',
    postalCode: '28001',
  },
  geo: {
    '@type': 'GeoCoordinates',
    latitude: '40.4168',
    longitude: '-3.7038',
  },
  areaServed: {
    '@type': 'Country',
    name: 'España',
  },
  priceRange: '€€€',
  openingHoursSpecification: [
    {
      '@type': 'OpeningHoursSpecification',
      dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      opens: '09:00',
      closes: '18:00',
    },
  ],
  sameAs: [
    'https://www.linkedin.com/company/apautomatizacion',
    'https://twitter.com/apautomatizacion_es',
  ],
  hasOfferCatalog: {
    '@type': 'OfferCatalog',
    name: 'Servicios de IA',
    itemListElement: [
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Automatización de procesos con IA',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Agentes de Inteligencia Artificial',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Formación en IA para equipos',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Estrategia e implantación de IA',
        },
      },
    ],
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className={inter.variable}>
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#0F172A" />
      </head>
      <body className="font-sans antialiased">
        <Script
          src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${GA_ID}');
          `}
        </Script>
        <Header />
        <main>{children}</main>
        <Footer />
        <ChatBot />
        <CookieBanner />
      </body>
    </html>
  )
}
