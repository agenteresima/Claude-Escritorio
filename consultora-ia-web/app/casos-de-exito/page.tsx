import type { Metadata } from 'next'
import Link from 'next/link'
import {
  Factory,
  Stethoscope,
  Megaphone,
  ShoppingCart,
  FileText,
  Hotel,
  ArrowRight,
  TrendingUp,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Casos de éxito — AP Automatización IA',
  description:
    'Descubre cómo empresas de sectores muy diferentes han implementado inteligencia artificial con AP Automatización IA y han obtenido resultados reales y medibles.',
  keywords: [
    'casos de éxito IA empresas',
    'automatización IA resultados',
    'ejemplos inteligencia artificial pymes',
    'IA aplicada sectores',
  ],
  openGraph: {
    title: 'Casos de éxito — AP Automatización IA',
    description:
      'Empresas reales, resultados reales. Descubre cómo la IA ya está transformando sectores como industria, salud, marketing, e-commerce y hostelería.',
    type: 'website',
    locale: 'es_ES',
  },
  alternates: {
    canonical: 'https://www.automatizacionprocesos.es/casos-de-exito',
  },
}

const casos = [
  {
    icon: Factory,
    sector: 'Industria',
    empresa: 'Fabricante de componentes metálicos',
    titulo: 'Automatización integral de gestión de pedidos',
    resultado: '−70%',
    resultadoLabel: 'tiempo de gestión',
    descripcion:
      'Implantamos un agente IA que lee los pedidos entrantes por email, los valida contra el ERP, genera albaranes y notifica al equipo de producción. Sin intervención manual en el 85% de los casos.',
    tag: 'Agente IA · ERP',
  },
  {
    icon: Stethoscope,
    sector: 'Salud',
    empresa: 'Red de clínicas dentales (5 centros)',
    titulo: 'Chatbot de atención al paciente 24/7',
    resultado: '800',
    resultadoLabel: 'consultas/mes sin intervención',
    descripcion:
      'Desplegamos un chatbot entrenado sobre los protocolos de la clínica que resuelve dudas, gestiona citas y recuerda revisiones. El equipo de recepción redujo su carga de llamadas un 60%.',
    tag: 'Chatbot · Citas online',
  },
  {
    icon: Megaphone,
    sector: 'Marketing',
    empresa: 'Agencia de marketing digital (18 personas)',
    titulo: 'Generación automática de informes de campaña',
    resultado: '12h',
    resultadoLabel: 'semanales recuperadas por analista',
    descripcion:
      'Construimos un pipeline que extrae datos de Google Ads, Meta y Analytics, los cruza y genera informes en PDF listos para enviar al cliente. Cada analista recuperó medio día de trabajo a la semana.',
    tag: 'Automatización · Reporting',
  },
  {
    icon: ShoppingCart,
    sector: 'E-commerce',
    empresa: 'Tienda online de moda sostenible',
    titulo: 'Optimización de conversión con IA',
    resultado: '+35%',
    resultadoLabel: 'incremento en conversión',
    descripcion:
      'Implementamos un sistema de análisis de comportamiento que personaliza el orden de productos, ajusta los textos de fichas y activa descuentos dinámicos según el perfil de cada visitante.',
    tag: 'Personalización · Analítica',
  },
  {
    icon: FileText,
    sector: 'Servicios profesionales',
    empresa: 'Gestoría con 2.000 clientes activos',
    titulo: 'Clasificación y extracción de documentos fiscales',
    resultado: '−90%',
    resultadoLabel: 'tiempo de clasificación documental',
    descripcion:
      'El equipo recibía cientos de documentos al mes sin etiquetar. Ahora un modelo de IA los clasifica, extrae los datos clave y los vincula al expediente del cliente en segundos.',
    tag: 'OCR · IA documental',
  },
  {
    icon: Hotel,
    sector: 'Hostelería',
    empresa: 'Hotel boutique en Madrid',
    titulo: 'Asistente virtual multilingüe para huéspedes',
    resultado: '24/7',
    resultadoLabel: 'respuesta en 3 idiomas sin coste extra',
    descripcion:
      'Desarrollamos un asistente que responde en español, inglés y francés sobre servicios del hotel, restauración, excursiones y check-in/out. La satisfacción en Booking subió 0,4 puntos en 3 meses.',
    tag: 'Asistente IA · Multilingüe',
  },
]

export default function CasosDeExitoPage() {
  return (
    <main className="bg-surface-50 min-h-screen">
      {/* Hero */}
      <section className="bg-gradient-to-br from-navy-900 via-navy-800 to-navy-700 py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-brand-400 text-sm font-semibold uppercase tracking-widest mb-4">
            Casos de éxito
          </p>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
            Empresas que ya{' '}
            <span className="text-brand-400">trabajan con IA</span>
          </h1>
          <p className="text-lg md:text-xl text-navy-300 max-w-2xl mx-auto leading-relaxed">
            Resultados reales de proyectos completados en sectores muy diferentes. Cada caso
            demuestra que la IA no es ciencia ficción: es una herramienta que ya está generando
            valor en empresas como la tuya.
          </p>
        </div>
      </section>

      {/* Indicadores rápidos */}
      <section className="bg-white border-b border-surface-200 py-10 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {[
              { valor: '6', label: 'sectores representados' },
              { valor: '+50', label: 'proyectos completados' },
              { valor: '100%', label: 'clientes satisfechos' },
              { valor: '<3 meses', label: 'tiempo medio de ROI' },
            ].map((stat) => (
              <div key={stat.label}>
                <p className="text-3xl font-extrabold text-brand-600 mb-1">{stat.valor}</p>
                <p className="text-sm text-navy-500 font-medium">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Grid de casos */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {casos.map((caso) => {
              const Icon = caso.icon
              return (
                <article
                  key={caso.titulo}
                  className="bg-white rounded-2xl border border-surface-200 hover:border-brand-400 hover:shadow-xl transition-all duration-300 overflow-hidden flex flex-col group"
                >
                  {/* Header tarjeta */}
                  <div className="bg-gradient-to-br from-navy-900 to-navy-800 p-6 flex items-start justify-between">
                    <div>
                      <span className="inline-block bg-brand-500/20 text-brand-400 text-xs font-semibold px-3 py-1 rounded-full mb-3">
                        {caso.sector}
                      </span>
                      <p className="text-navy-300 text-sm leading-snug">{caso.empresa}</p>
                    </div>
                    <div className="w-11 h-11 bg-brand-500/15 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:bg-brand-500 transition-colors duration-300">
                      <Icon className="w-5 h-5 text-brand-400 group-hover:text-white transition-colors duration-300" />
                    </div>
                  </div>

                  {/* Resultado destacado */}
                  <div className="px-6 py-5 border-b border-surface-100 flex items-center gap-4">
                    <div>
                      <p className="text-4xl font-extrabold text-brand-600 leading-none">
                        {caso.resultado}
                      </p>
                      <p className="text-xs text-navy-500 font-medium mt-1">{caso.resultadoLabel}</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-success-500 flex-shrink-0 ml-auto opacity-70" />
                  </div>

                  {/* Contenido */}
                  <div className="px-6 py-5 flex flex-col flex-1">
                    <h3 className="text-base font-bold text-navy-900 mb-3 leading-snug">
                      {caso.titulo}
                    </h3>
                    <p className="text-navy-600 text-sm leading-relaxed flex-1">{caso.descripcion}</p>
                    <div className="mt-5">
                      <span className="inline-block bg-surface-100 text-navy-500 text-xs font-medium px-3 py-1 rounded-full">
                        {caso.tag}
                      </span>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-navy-900">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-brand-400 text-sm font-semibold uppercase tracking-widest mb-4">
            Tu empresa puede ser la siguiente
          </p>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-5 leading-tight">
            ¿Quieres ser el siguiente caso de éxito?
          </h2>
          <p className="text-navy-300 text-lg mb-10 leading-relaxed">
            Empieza con un diagnóstico gratuito de 30 minutos. Identificamos junto a ti qué
            procesos son automatizables y cuánto tiempo y dinero podrías recuperar.
          </p>
          <Link
            href="/diagnostico-gratuito"
            className="inline-flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-600 text-white font-bold px-10 py-4 rounded-xl transition-colors duration-200 text-lg"
          >
            Solicitar diagnóstico gratuito
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </main>
  )
}
