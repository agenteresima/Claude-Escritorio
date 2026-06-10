import type { Metadata } from 'next'
import Link from 'next/link'
import {
  MessageSquare,
  Map,
  Layers,
  Target,
  Calculator,
  FileCheck,
  CheckCircle,
  ArrowRight,
  Search,
  Clock,
  Euro,
  Users,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Auditoría IA para Empresas | Diagnóstico de Procesos | Automatización Procesos IA',
  description:
    'Auditoría de inteligencia artificial para empresas: analizamos tus procesos, identificamos oportunidades de automatización y te entregamos un plan de acción con estimación de ahorro. Desde 790 €.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/auditoria-ia' },
  openGraph: {
    title: 'Auditoría IA para Empresas | Diagnóstico de Procesos | Automatización Procesos IA',
    description:
      'Diagnóstico profesional de IA para empresas. Mapa completo de automatizaciones, priorización y estimación de ahorro. Desde 790 €.',
    url: 'https://www.automatizacionprocesos.es/auditoria-ia',
  },
}

const auditSteps = [
  {
    icon: MessageSquare,
    step: '01',
    title: 'Entrevista inicial',
    duration: '90 min',
    description:
      'Sesión de trabajo con los responsables clave de la empresa. Entendemos el modelo de negocio, los departamentos, las herramientas actuales y los principales puntos de dolor. Ninguna pregunta técnica: solo conversación sobre cómo funciona tu empresa.',
  },
  {
    icon: Map,
    step: '02',
    title: 'Revisión de procesos',
    duration: '3-4 días',
    description:
      'Analizamos en profundidad los procesos operativos de cada departamento. Hablamos directamente con las personas que hacen el trabajo para entender dónde se pierden las horas y qué tareas se hacen de forma repetitiva.',
  },
  {
    icon: Layers,
    step: '03',
    title: 'Mapa de automatizaciones',
    duration: '2 días',
    description:
      'Creamos un mapa completo de todas las oportunidades de automatización identificadas: qué se puede automatizar, con qué herramientas y qué dependencias tiene cada automatización.',
  },
  {
    icon: Target,
    step: '04',
    title: 'Priorización impacto/esfuerzo',
    duration: '1 día',
    description:
      'Clasificamos cada automatización según su impacto esperado y el esfuerzo de implementación. El resultado es una matriz clara que indica por dónde empezar para obtener el mayor retorno lo antes posible.',
  },
  {
    icon: Calculator,
    step: '05',
    title: 'Estimación de ahorro',
    duration: '1 día',
    description:
      'Calculamos el ahorro estimado de cada automatización: horas semanales recuperadas, coste equivalente en euros, coste de implementación y período de retorno. Cifras conservadoras y metodología transparente.',
  },
  {
    icon: FileCheck,
    step: '06',
    title: 'Informe final + plan de acción',
    duration: '2 días',
    description:
      'Entregamos un informe ejecutivo completo y presentamos los resultados en una sesión de 60 minutos. El plan de acción incluye los primeros pasos concretos, ordenados por prioridad, con presupuesto orientativo para cada uno.',
  },
]

const deliverableItems = [
  'Mapa visual de todos los procesos analizados',
  'Inventario completo de oportunidades de automatización',
  'Matriz de priorización impacto/esfuerzo',
  'Estimación de ahorro en horas y euros por automatización',
  'Presupuesto orientativo de implementación por proyecto',
  'Recomendación de herramientas para cada caso',
  'Plan de acción con hitos a 3, 6 y 12 meses',
  'Sesión de presentación con espacio para preguntas',
]

const forWhom = [
  {
    profile: 'Director general o gerente',
    description:
      'Quieres saber exactamente cuánto puede ahorrar tu empresa con IA antes de comprometer presupuesto. Necesitas datos concretos, no promesas.',
  },
  {
    profile: 'Responsable de operaciones',
    description:
      'Identificas cuellos de botella en los procesos pero no tienes claro cuáles tienen solución técnica viable con IA y cuáles no.',
  },
  {
    profile: 'Empresa que ya usa ChatGPT pero no ve resultados',
    description:
      'Tu equipo usa herramientas de IA de forma dispersa y sin estrategia. Quieres ordenar el caos y orientar el uso hacia resultados medibles.',
  },
  {
    profile: 'Empresa que va a invertir en IA por primera vez',
    description:
      'Quieres empezar con buen pie: saber exactamente qué tiene sentido hacer antes de gastar un euro en herramientas o proveedores.',
  },
]

export default function AuditoriaIAPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Service',
            name: 'Auditoría IA para Empresas',
            description:
              'Diagnóstico profesional de inteligencia artificial para empresas. Mapa de automatizaciones, priorización y estimación de ahorro.',
            provider: { '@type': 'Organization', name: 'Automatización Procesos IA', url: 'https://www.automatizacionprocesos.es' },
            url: 'https://www.automatizacionprocesos.es/auditoria-ia',
            offers: {
              '@type': 'Offer',
              price: '790',
              priceCurrency: 'EUR',
              description: 'Desde 790 € (pago único)',
            },
          }),
        }}
      />

      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
              Auditoría IA
            </span>
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
              Auditoría de inteligencia artificial{' '}
              <span className="text-blue-400">para empresas</span>
            </h1>
            <p className="text-lg text-slate-300 mb-8 leading-relaxed">
              Antes de invertir en IA, necesitas saber exactamente qué puedes automatizar, cuánto
              ahorrarías y cuánto costaría. La auditoría es el diagnóstico profesional que te da
              ese mapa completo. El punto de partida correcto.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 mb-10">
              <Link
                href="/contacto"
                className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
              >
                Solicitar auditoría
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/diagnostico-gratuito"
                className="inline-flex items-center justify-center gap-2 border border-slate-600 hover:border-slate-400 text-slate-300 hover:text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
              >
                Diagnóstico gratuito primero
              </Link>
            </div>
            <div className="flex flex-col sm:flex-row gap-6">
              <div className="flex items-center gap-2 text-slate-300">
                <Euro className="h-5 w-5 text-blue-400" />
                <span className="font-semibold">Desde 790 € (pago único)</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <Clock className="h-5 w-5 text-blue-400" />
                <span>Plazo: 2-3 semanas</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* What is it */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-6">Qué es y para qué sirve</h2>
              <p className="text-slate-600 mb-4 leading-relaxed">
                La auditoría de IA es un análisis profesional de los procesos de tu empresa para
                identificar todas las oportunidades de automatización con inteligencia artificial.
                No es una consultoría genérica ni una presentación de herramientas: es un trabajo
                de campo real con tu equipo.
              </p>
              <p className="text-slate-600 mb-4 leading-relaxed">
                Al final del proceso tendrás una respuesta concreta a tres preguntas:{' '}
                <strong className="text-slate-900">qué puedes automatizar</strong>,{' '}
                <strong className="text-slate-900">cuánto ahorrarías</strong> y{' '}
                <strong className="text-slate-900">cuánto costaría</strong>. Con esos datos puedes
                tomar decisiones de inversión con criterio.
              </p>
              <p className="text-slate-600 leading-relaxed">
                El 80% de las empresas que contratan la auditoría descubren oportunidades de
                automatización que no habían considerado. Y el 100% llega con un plan de acción
                concreto para los próximos 12 meses.
              </p>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Search className="h-5 w-5 text-blue-600" />
                <h3 className="font-bold text-slate-900">Qué incluye el informe entregable</h3>
              </div>
              <ul className="space-y-3">
                {deliverableItems.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-sm text-slate-700">
                    <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Process */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">El proceso en 6 pasos</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Una metodología estructurada que garantiza que no se escapa ninguna oportunidad y
              que cada recomendación está respaldada por datos reales de tu empresa.
            </p>
          </div>
          <div className="space-y-4">
            {auditSteps.map((step) => {
              const Icon = step.icon
              return (
                <div
                  key={step.step}
                  className="bg-white border border-slate-200 rounded-2xl p-6 flex flex-col sm:flex-row gap-6"
                >
                  <div className="flex-shrink-0 flex items-start gap-4">
                    <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
                      <span className="text-white font-bold">{step.step}</span>
                    </div>
                  </div>
                  <div className="flex-grow">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
                      <h3 className="font-bold text-slate-900 text-lg">{step.title}</h3>
                      <span className="inline-flex items-center gap-1 text-xs text-blue-600 bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-full font-medium w-fit">
                        <Clock className="h-3 w-3" />
                        {step.duration}
                      </span>
                    </div>
                    <p className="text-slate-600 text-sm leading-relaxed">{step.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* For whom */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Para quién es la auditoría</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              La auditoría es especialmente útil en cuatro situaciones concretas.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 gap-6">
            {forWhom.map((item) => (
              <div key={item.profile} className="border border-slate-200 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-3">
                  <Users className="h-5 w-5 text-blue-600" />
                  <h3 className="font-semibold text-slate-900">{item.profile}</h3>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <div className="bg-white border-2 border-blue-500 rounded-2xl p-8 text-center">
            <span className="inline-block bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full mb-4">
              Precio fijo, sin sorpresas
            </span>
            <div className="text-5xl font-bold text-slate-900 mb-2">Desde 790 €</div>
            <p className="text-slate-500 mb-6">Pago único. Sin suscripciones ni costes adicionales.</p>
            <div className="grid sm:grid-cols-2 gap-4 mb-8 text-left">
              <div className="flex items-center gap-2 text-sm text-slate-700">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                Análisis completo de procesos
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-700">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                Informe ejecutivo detallado
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-700">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                Plan de acción a 12 meses
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-700">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                Sesión de presentación incluida
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-700">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                Estimación de ahorro en €
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-700">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                Plazo: 2-3 semanas
              </div>
            </div>
            <Link
              href="/contacto"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-bold px-8 py-3.5 rounded-xl transition-colors text-lg"
            >
              Solicitar auditoría
              <ArrowRight className="h-5 w-5" />
            </Link>
            <p className="text-slate-400 text-sm mt-4">
              ¿Tienes dudas? Empieza con el{' '}
              <Link href="/diagnostico-gratuito" className="text-blue-600 hover:underline">
                diagnóstico gratuito
              </Link>
              .
            </p>
          </div>
        </div>
      </section>
    </>
  )
}
