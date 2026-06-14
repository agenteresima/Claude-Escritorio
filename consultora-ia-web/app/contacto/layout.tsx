export const metadata = {
  title: 'Contacto Consultoría IA Valencia | Automatización Procesos',
  description:
    'Contacta con nuestra consultoría de IA en Valencia. Expertos en automatización de procesos para pymes. Respuesta en menos de 24 horas. Sin compromiso.',
  keywords: [
    'consultoría IA Valencia',
    'automatización procesos Valencia',
    'contacto consultor IA',
    'expertos IA España',
  ],
  openGraph: {
    title: 'Contacto Consultoría IA Valencia | Automatización Procesos',
    description:
      'Contacta con nuestra consultoría de IA en Valencia. Expertos en automatización de procesos para pymes. Respuesta en menos de 24 horas. Sin compromiso.',
    url: 'https://www.automatizacionprocesos.es/contacto',
    images: [
      {
        url: 'https://www.automatizacionprocesos.es/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Contacto Consultoría IA Valencia',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Contacto Consultoría IA Valencia | Automatización Procesos',
    description:
      'Contacta con nuestra consultoría de IA en Valencia. Expertos en automatización de procesos para pymes. Respuesta en menos de 24 horas.',
    images: ['https://www.automatizacionprocesos.es/og-image.jpg'],
  },
  alternates: { canonical: 'https://www.automatizacionprocesos.es/contacto' },
}

export default function ContactoLayout({ children }: { children: React.ReactNode }) {
  return children
}
