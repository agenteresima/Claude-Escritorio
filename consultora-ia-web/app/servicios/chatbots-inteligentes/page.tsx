import type { Metadata } from 'next'
import Link from 'next/link'
import { MessageSquare, Users, Clock, Globe, Star, BarChart3, ArrowRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Chatbots Inteligentes con IA para Empresas | AP Automatización IA',
  description:
    'Chatbots con inteligencia artificial para atención al cliente, captación de leads y soporte interno. Disponibles 24/7, integrados en tu web, WhatsApp o app. Respuestas precisas y naturales.',
  alternates: { canonical: 'https://automatizacionprocesos.es/servicios/chatbots-inteligentes' },
  openGraph: {
    title: 'Chatbots Inteligentes con IA para Empresas | AP Automatización IA',
    description:
      'Chatbots con IA para atención al cliente 24/7. Integrados en web, WhatsApp y más. Respuestas naturales y precisas.',
    url: 'https://automatizacionprocesos.es/servicios/chatbots-inteligentes',
  },
}

const includes = [
  {
    icon: MessageSquare,
    title: 'Chatbot entrenado con tu información',
    description:
      'Lo alimentamos con tus FAQs, catálogo, políticas y documentos. Responde como si fuera un experto de tu empresa.',
  },
  {
    icon: Users,
    title: 'Escalado a agente humano',
    description:
      'Cuando la consulta lo requiere, el chatbot transfiere la conversación a un agente humano con todo el contexto ya cargado.',
  },
  {
    icon: Clock,
    title: 'Atención 24/7 sin coste adicional',
    description:
      'Tu negocio atiende clientes a las 3 de la mañana sin horas extra ni turnos de noche. El chatbot nunca se cansa.',
  },
  {
    icon: Globe,
    title: 'Multicanal y multilingüe',
    description:
      'Desplegamos el chatbot en tu web, WhatsApp Business, Telegram o app. Responde en el idioma del usuario automáticamente.',
  },
  {
    icon: Star,
    title: 'Personalidad de marca',
    description:
      'El chatbot adopta el tono, vocabulario y valores de tu marca. No parece un bot genérico, parece parte de tu equipo.',
  },
  {
    icon: BarChart3,
    title: 'Analítica y mejora continua',
    description:
      'Dashboard con conversaciones, tasas de resolución, preguntas sin respuesta y satisfacción del usuario para mejora constante.',
  },
]

const benefits = [
  {
    title: 'Resuelve el 70% de las consultas sin intervención humana',
    description:
      'La mayoría de las preguntas de clientes son repetitivas. El chatbot las responde de forma instantánea, liberando a tu equipo para casos complejos.',
  },
  {
    title: 'Captura leads fuera del horario comercial',
    description:
      'El chatbot cualifica visitantes, recoge datos de contacto y agenda reuniones mientras tu equipo duerme. Sin oportunidades perdidas.',
  },
  {
    title: 'Satisfacción del cliente medible y mejorable',
    description:
      'Medimos la satisfacción en cada conversación y ajustamos el chatbot para que mejore mes a mes. Siempre hay margen de mejora.',
  },
]

export default function ChatbotsInteligentesPage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 py-24 text-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Chatbots inteligentes
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Atención al cliente con IA{' '}
            <span className="text-blue-400">disponible las 24 horas</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-10">
            Chatbots entrenados con la información de tu empresa que responden preguntas, capturan
            leads y resuelven incidencias de forma natural. Integrados donde están tus clientes.
          </p>
          <Link
            href="/diagnostico-gratuito"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-4 rounded-xl transition-colors text-lg"
          >
            Solicitar diagnóstico gratuito
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* ¿Qué incluye? */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">¿Qué incluye el servicio?</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Un chatbot inteligente completo, entrenado, desplegado y optimizado continuamente para
              tu negocio.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {includes.map((item) => {
              const Icon = item.icon
              return (
                <div
                  key={item.title}
                  className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all"
                >
                  <div className="bg-blue-50 w-12 h-12 rounded-xl flex items-center justify-center mb-5">
                    <Icon className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-slate-900 text-lg mb-2">{item.title}</h3>
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
              Lo que cambia en tu negocio cuando implementas un chatbot inteligente.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {benefits.map((benefit) => (
              <div
                key={benefit.title}
                className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200"
              >
                <h3 className="font-bold text-slate-900 text-xl mb-3">{benefit.title}</h3>
                <p className="text-slate-600 leading-relaxed">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section className="bg-slate-900 text-white py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            ¿Quieres un chatbot inteligente para tu empresa?
          </h2>
          <p className="text-slate-300 text-lg mb-8 max-w-2xl mx-auto">
            En una llamada gratuita de 45 minutos analizamos tu caso, definimos el alcance del
            chatbot y te presentamos una propuesta clara con precio y plazos.
          </p>
          <Link
            href="/diagnostico-gratuito"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors"
          >
            Solicitar diagnóstico gratuito
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>
    </>
  )
}
