import type { Metadata } from 'next'
import Link from 'next/link'
import { Zap, GitBranch, Clock, CheckCircle, BarChart3, Settings, ArrowRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Automatización de Procesos con IA | n8n, Zapier, Make | AP Automatización IA',
  description:
    'Automatizamos tus procesos empresariales repetitivos con n8n, Zapier y Make. Elimina tareas manuales, reduce errores y libera a tu equipo para lo que importa. Resultados medibles.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/servicios/automatizacion-procesos' },
  openGraph: {
    title: 'Automatización de Procesos con IA | AP Automatización IA',
    description:
      'Automatizamos tus procesos empresariales repetitivos con n8n, Zapier y Make. Elimina tareas manuales y libera a tu equipo.',
    url: 'https://www.automatizacionprocesos.es/servicios/automatizacion-procesos',
  },
}

const includes = [
  {
    icon: Zap,
    title: 'Automatización end-to-end',
    description:
      'Conectamos todas tus aplicaciones y construimos flujos que se ejecutan solos, desde el disparo hasta el resultado final.',
  },
  {
    icon: GitBranch,
    title: 'Flujos con lógica condicional',
    description:
      'Tus procesos no son lineales y los nuestros tampoco. Ramificaciones, bucles y condiciones según el contexto real.',
  },
  {
    icon: Clock,
    title: 'Ejecución programada o en tiempo real',
    description:
      'Automatizaciones que arrancan a una hora fija o al instante cuando ocurre un evento en cualquier sistema.',
  },
  {
    icon: CheckCircle,
    title: 'Validación y control de errores',
    description:
      'Cada flujo incluye manejo de excepciones y alertas para que sepas de inmediato si algo no funciona como debe.',
  },
  {
    icon: BarChart3,
    title: 'Métricas y seguimiento',
    description:
      'Panel de control con el estado de cada automatización, tiempo ahorrado y volumen de tareas ejecutadas.',
  },
  {
    icon: Settings,
    title: 'Mantenimiento y evolución',
    description:
      'Te dejamos la plataforma documentada y formamos a tu equipo para que puedas modificar y ampliar los flujos tú mismo.',
  },
]

const benefits = [
  {
    title: 'Hasta 80% menos tiempo en tareas manuales',
    description:
      'Facturas, informes, emails, actualizaciones de CRM… todo lo que hacéis a mano hoy puede ejecutarse solo. Tus empleados dejan de ser copistas y pasan a tomar decisiones.',
    stat: '80%',
    label: 'reducción de trabajo manual',
  },
  {
    title: 'Cero errores por descuido humano',
    description:
      'Los procesos automatizados ejecutan siempre igual: sin olvidar pasos, sin copiar mal un dato, sin que nadie se vaya de vacaciones. La consistencia es el nuevo estándar.',
    stat: '0',
    label: 'errores por fatiga o despiste',
  },
  {
    title: 'ROI positivo en menos de 3 meses',
    description:
      'Calculamos el ahorro real antes de empezar. En la mayoría de proyectos el coste de la automatización se recupera en el primer trimestre y genera ahorro neto a partir del cuarto mes.',
    stat: '<3m',
    label: 'para recuperar la inversión',
  },
]

export default function AutomatizacionProcesosPage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Automatización de procesos
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Elimina las tareas repetitivas{' '}
            <span className="text-blue-400">de tu empresa para siempre</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-10">
            Con n8n, Zapier y Make conectamos todos tus sistemas y construimos automatizaciones que
            trabajan 24 horas al día, 7 días a la semana, sin errores y sin supervisión constante.
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
              No vendemos herramientas. Construimos soluciones completas, documentadas y listas para
              que tu equipo las mantenga y amplíe sin depender de nosotros.
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
              Resultados reales que nuestros clientes han conseguido con automatizaciones de procesos.
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
            ¿Listo para dejar de hacer trabajo manual?
          </h2>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto mb-8">
            En una videollamada de 45 minutos identificamos qué procesos de tu empresa se pueden
            automatizar y te damos una estimación del ahorro real. Sin coste y sin compromiso.
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
