export const metadata = {
  title: 'Blog IA para Empresas | Automatización Procesos IA',
  description:
    'Blog de inteligencia artificial para empresas: automatización de procesos, agentes IA, estrategia IA para pymes. Guías prácticas y casos de uso reales con resultados medibles.',
  keywords: [
    'blog IA empresas',
    'automatización procesos IA',
    'agentes IA pymes',
    'inteligencia artificial para empresas',
    'guías IA práctica',
    'casos uso IA',
  ],
  openGraph: {
    title: 'Blog IA para Empresas | Automatización Procesos IA',
    description:
      'Blog de inteligencia artificial para empresas: automatización de procesos, agentes IA, estrategia IA para pymes. Guías prácticas y casos de uso reales con resultados medibles.',
    url: 'https://www.automatizacionprocesos.es/blog',
    images: [
      {
        url: 'https://www.automatizacionprocesos.es/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Blog IA para Empresas',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Blog IA para Empresas | Automatización Procesos IA',
    description:
      'Blog de inteligencia artificial para empresas: automatización de procesos, agentes IA, estrategia IA para pymes. Guías prácticas y casos reales.',
    images: ['https://www.automatizacionprocesos.es/og-image.png'],
  },
  alternates: { canonical: 'https://www.automatizacionprocesos.es/blog' },
}

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return children
}
