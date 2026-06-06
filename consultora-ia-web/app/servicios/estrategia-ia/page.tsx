import type { Metadata } from 'next'
import Link from 'next/link'
import { Target, Map, BarChart3, Shield, Lightbulb, CheckCircle, ArrowRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Estrategia de IA para Empresas | Hoja de Ruta y Transformación Digital | AP Automatización IA',
  description:
    'Consultoría estratégica de inteligencia artificial para empresas. Definimos tu hoja de ruta de IA, priorizamos iniciativas y acompañamos la transformación digital con resultados medibles.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/servicios/estrategia-ia' },
  openGraph: {
    title: 'Estrategia de IA para Empresas | AP Automatización IA',
    description:
      'Consultoría estratégica de IA. Hoja de ruta, priorización de iniciativas y acompañamiento en la transformación digital de tu empresa.',
    url: 'https://www.automatizacionprocesos.es/servicios/estrategia-ia',
  },
}

const includes = [
  {
    icon: Target,
    title: 'Diagnóstico estratégico inicial',
    description:
      'Analizamos en profundidad tu modelo de negocio, procesos actuales, madurez digital y posición competitiva para identificar dónde la IA puede generar mayor impacto.',
  },
  {
    icon: Map,
    title: 'Hoja de ruta de IA personalizada',
    description:
      'Diseñamos un plan de implementación por fases con iniciativas priorizadas por impacto, esfuerzo y coste. Sabes exactamente qué hacer, cuándo y en qué orden.',
  },
  {
    icon: BarChart3,
    title: 'Business case y estimación de ROI',
    description:
      'Para cada iniciativa calculamos el retorno esperado, el coste de implementación y el tiempo de recuperación de la inversión. Decisiones basadas en datos, no en intuición.',
  },
  {
    icon: Shield,
    title: 'Gestión de riesgos y gobernanza',
    description:
      'Identificamos los riesgos de cada iniciativa e integramos principios de ética, privacidad y cumplimiento normativo desde el inicio del diseño estratégico.',
  },
  {
    icon: Lightbulb,
    title: 'Identificación de casos de uso',
    description:
      'Seleccionamos los casos de uso más relevantes para tu sector y tamaño de empresa, con ejemplos de empresas similares que ya los han implantado con éxito.',
  },
  {
    icon: CheckCircle,
    title: 'Acompañamiento en la ejecución',
    description:
      'La estrategia no queda en un documento. Te acompañamos en la implementación, validamos los avances y ajustamos el rumbo cuando el contexto cambia.',
  },
]

const benefits = [
  {
    title: 'Inversión enfocada donde realmente importa',
    description:
      'Sin una estrategia clara, las empresas malgastan recursos en herramientas de moda que no resuelven problemas reales. Con una hoja de ruta sólida, cada euro invertido tiene un propósito medible.',
    stat: '3x',
    label: 'mayor retorno de la inversión en IA',
  },
  {
    title: 'Ventaja competitiva sostenible',
    description:
      'Las empresas que implementan IA de forma estratégica y ordenada se distancian de la competencia de manera duradera. No se trata de adoptar tecnología, sino de rediseñar cómo compites.',
    stat: '2 años',
    label: 'de ventaja competitiva media',
  },
  {
    title: 'Reducción del riesgo de fracaso',
    description:
      'El 85% de los proyectos de IA fracasan por falta de estrategia, no por falta de tecnología. Un plan bien diseñado multiplica las probabilidades de éxito y reduce los costes de ensayo y error.',
    stat: '85%',
    label: 'de proyectos IA fallan sin estrategia',
  },
]

export default function EstrategiaIAPage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Estrategia e IA para empresas
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            La hoja de ruta de IA que necesita{' '}
            <span className="text-blue-400">tu empresa para crecer</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-10">
            Definimos juntos qué iniciativas de inteligencia artificial tienen más sentido para tu
            negocio, en qué orden implementarlas y cómo medir el impacto real. Estrategia concreta,
            no visión de futuro.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/diagnostico-gratuito"
              className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl font-semibold transition-colors"
            >
              Solicitar diagnóstico gratuito
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/contacto"
              className="inline-flex items-center justify-center gap-2 border border-slate-600 hover:border-slate-400 text-slate-300 hover:text-white px-8 py-4 rounded-xl font-semibold transition-colors"
            >
              Hablar con un consultor
            </Link>
          </div>
        </div>
      </section>

      {/* ¿Qué incluye? */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">¿Qué incluye el servicio?</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Un proceso estructurado que va desde el análisis de tu situación actual hasta una hoja
              de ruta ejecutable, con el acompañamiento necesario para que la estrategia se convierta
              en resultados reales.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {includes.map((item) => {
              const Icon = item.icon
              return (
                <div key={item.title} className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200">
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-50 rounded-xl mb-4">
                    <Icon className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">{item.title}</h3>
                  <p className="text-slate-600 text-sm leading-relaxed">{item.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Beneficios */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Beneficios concretos</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Por qué las empresas que trabajan con una estrategia de IA clara obtienen mejores
              resultados que las que improvisan.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {benefits.map((b) => (
              <div key={b.title} className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200">
                <div className="text-4xl font-bold text-blue-600 mb-1">{b.stat}</div>
                <div className="text-xs text-slate-500 mb-4 font-semibold uppercase tracking-wider">{b.label}</div>
                <h3 className="text-lg font-semibold text-slate-900 mb-3">{b.title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">{b.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section className="bg-slate-900 text-white py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            ¿Quieres una estrategia de IA clara para tu empresa?
          </h2>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto mb-8">
            En 45 minutos analizamos la situación actual de tu empresa y te damos una primera
            visión de por dónde empezar y qué impacto puedes esperar. Sin compromiso.
          </p>
          <Link
            href="/diagnostico-gratuito"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors text-lg"
          >
            Solicitar diagnóstico gratuito
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>
    </>
  )
}
