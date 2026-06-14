import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Blog IA para Empresas | Automatización Procesos IA',
  description: 'Guías prácticas, casos reales y estrategias de IA para empresas. Automatización de procesos, agentes IA y herramientas para directivos y responsables de empresa.',
  keywords: ['blog ia empresas', 'automatización procesos blog', 'agentes ia articulos', 'consultoría ia blog'],
  alternates: { canonical: 'https://www.automatizacionprocesos.es/blog' },
  openGraph: {
    title: 'Blog IA para Empresas | Automatización Procesos IA',
    description: 'Guías prácticas y casos reales de IA para empresas. Estrategia, automatización y herramientas.',
    url: 'https://www.automatizacionprocesos.es/blog',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Blog IA para Empresas' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Blog IA para Empresas | Automatización Procesos IA',
    description: 'Guías prácticas de IA para empresas. Automatización, agentes IA y estrategia.',
    images: ['/og-image.png'],
  },
}

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return children
}
