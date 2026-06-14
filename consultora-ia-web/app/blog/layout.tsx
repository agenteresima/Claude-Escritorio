import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Blog IA para Empresas | Guías y Casos Reales | Automatización Procesos IA',
  description:
    'Guías prácticas y casos reales sobre inteligencia artificial para empresas. Aprende a automatizar procesos con IA, implementar agentes y transformar tu pyme con resultados medibles.',
  keywords: ['blog IA empresas', 'guías automatización IA', 'inteligencia artificial pymes', 'casos reales IA empresa'],
  openGraph: {
    title: 'Blog IA para Empresas | Automatización Procesos IA',
    description: 'Guías prácticas sobre IA para empresas: automatización de procesos, agentes IA, estrategia y formación.',
    url: 'https://www.automatizacionprocesos.es/blog',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Blog IA para empresas' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Blog IA para Empresas | Automatización Procesos IA',
    description: 'Guías prácticas y casos reales sobre IA empresarial.',
    images: ['/og-image.png'],
  },
  alternates: { canonical: 'https://www.automatizacionprocesos.es/blog' },
}

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return children
}
