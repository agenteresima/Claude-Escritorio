import type { Metadata } from 'next'
import Link from 'next/link'
import { Bot, Brain, MessageSquare, Zap, Shield, TrendingUp, ArrowRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Agentes IA Autónomos para Empresas | LLMs Personalizados | Automatización Procesos IA',
  description:
    'Desarrollamos agentes de inteligencia artificial autónomos con LLMs para tu empresa. Agentes comerciales, de atención al cliente y administrativos que trabajan 24/7 sin errores.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/servicios/agentes-ia' },
  openGraph: {
    title: 'Agentes IA Autónomos para Empresas | Automatización Procesos IA',
    description:
      'Agentes de inteligencia artificial personalizados que trabajan 24/7 en tu nombre. Comercial, atención al cliente, administración.',
    url: 'https://www.automatizacionprocesos.es/servicios/agentes-ia',
  },
}

const includes = [
  {
    icon: Bot,
    title: 'Agente diseñado a medida',
    description:
      'Cada agente se construye específicamente para tu empresa: tus datos, tus procesos, tu tono de comunicación y tus reglas de negocio.',
  },
  {
    icon: Brain,
    title: 'Modelos de lenguaje avanzados',
    description:
      'Utilizamos GPT-4, Claude y otros LLMs de última generación combinados con herramientas y bases de conocimiento propias.',
  },
  {
    icon: MessageSquare,
    title: 'Integración multicanal',
    description:
      'El agente puede operar en email, WhatsApp, Slack, Teams, tu web o cualquier otra plataforma donde trabaje tu equipo.',
  },
  {
    icon: Zap,
    title: 'Ejecución de acciones reales',
    description:
      'No solo responde: actúa. Actualiza el CRM, crea tareas, envía emails, genera documentos y toma decisiones dentro de los límites que definas.',
  },
  {
    icon: Shield,
    title: 'Control y supervisión humana',
    description:
      'Definimos qué decisiones puede tomar el agente solo y cuáles requieren aprobación humana. Tú siempre tienes el control.',
  },
  {
    icon: TrendingUp,
    title: 'Mejora continua con datos reales',
    description:
      'El agente aprende de las interacciones. Revisamos periódicamente su rendimiento y ajustamos su comportamiento para que mejore con el tiempo.',
  },
]

const benefits = [
  {
    title: 'Disponibilidad total sin coste adicional',
    description:
      'Un agente IA trabaja los 365 días del año, a cualquier hora, sin vacaciones ni bajas. Atiende a tus clientes o gestiona tareas internas mientras tu equipo duerme.',
    stat: '24/7',
    label: 'disponibilidad garantizada',
  },
  {
    title: 'Escalabilidad instantánea',
    description:
      'Donde un humano solo puede gestionar una conversación a la vez, un agente IA maneja miles simultáneamente sin perder calidad. Escala en segundos ante picos de demanda.',
    stat: '∞',
    label: 'conversaciones simultáneas',
  },
  {
    title: 'Conocimiento siempre actualizado',
    description:
      'El agente accede en tiempo real a tu base de datos, catálogo, precios y políticas. Nunca da información desactualizada y siempre responde con precisión.',
    stat: '100%',
    label: 'información actualizada',
  },
]

export default function AgentesIAPage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Agentes IA autónomos
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Empleados digitales que trabajan{' '}
            <span className="text-blue-400">24 horas, 7 días a la semana</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-10">
            Desarrollamos agentes de inteligencia artificial personalizados con los LLMs más
            avanzados. Se integran en tus sistemas, conocen tu negocio y actúan en tu nombre sin
            errores y sin descanso.
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
              Cada agente se diseña, construye e implanta de forma personalizada. No son chatbots
              genéricos: son asistentes inteligentes entrenados con el conocimiento de tu empresa.
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
              Lo que consiguen nuestros clientes al implantar agentes IA en su operativa diaria.
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
            ¿Quieres un agente IA trabajando para tu empresa?
          </h2>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto mb-8">
            Cuéntanos qué tarea quieres automatizar y te explicamos en 45 minutos cómo lo
            construiríamos, qué resultados puedes esperar y cuánto costaría. Sin compromiso.
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
