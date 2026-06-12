import type { Metadata } from 'next'
import Link from 'next/link'
import { MessageSquare, Users, Clock, Globe, Star, BarChart3, ArrowRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Chatbots Inteligentes con IA para Atención al Cliente | Automatización Procesos IA',
  description:
    'Chatbots con inteligencia artificial para atención al cliente en tu web, WhatsApp y redes sociales. Respuestas precisas, disponibilidad 24/7 y escala sin límite.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/servicios/chatbots-inteligentes' },
  openGraph: {
    title: 'Chatbots Inteligentes con IA para Atención al Cliente | Automatización Procesos IA',
    description:
      'Chatbots con IA que atienden a tus clientes 24/7 con respuestas precisas. Integración en web, WhatsApp y redes sociales.',
    url: 'https://www.automatizacionprocesos.es/servicios/chatbots-inteligentes',
  },
}

const includes = [
  {
    icon: MessageSquare,
    title: 'Entrenado con tu conocimiento',
    description:
      'El chatbot aprende de tus FAQs, catálogo, políticas y documentación interna. Responde con la información exacta de tu empresa, no con respuestas genéricas.',
  },
  {
    icon: Users,
    title: 'Transferencia a agente humano',
    description:
      'Cuando la consulta lo requiere, el chatbot escala al equipo humano con todo el contexto de la conversación. La experiencia del cliente no se rompe.',
  },
  {
    icon: Clock,
    title: 'Disponible las 24 horas',
    description:
      'Atiende a tus clientes fuera de horario de oficina, en festivos y fines de semana. Sin coste adicional y sin tiempos de espera.',
  },
  {
    icon: Globe,
    title: 'Multiidioma y multicanal',
    description:
      'Funciona en web, WhatsApp Business, Telegram, Instagram y otras plataformas. Detecta el idioma del usuario y responde automáticamente.',
  },
  {
    icon: Star,
    title: 'Personalización de marca',
    description:
      'Nombre, tono, avatar y flujo de conversación adaptados a tu imagen de marca. Tu cliente siente que habla con alguien de tu empresa.',
  },
  {
    icon: BarChart3,
    title: 'Analítica de conversaciones',
    description:
      'Dashboard con volumen de consultas, temas más frecuentes, tasa de resolución y satisfacción del cliente. Insights para mejorar tu producto o servicio.',
  },
]

const benefits = [
  {
    title: '70% de consultas resueltas sin intervención humana',
    description:
      'La mayoría de preguntas de los clientes son repetitivas. El chatbot las resuelve al instante, liberando a tu equipo para las consultas complejas que realmente necesitan atención humana.',
    stat: '70%',
    label: 'consultas resueltas automáticamente',
  },
  {
    title: 'Tiempo de respuesta inferior a 3 segundos',
    description:
      'Los clientes no esperan. Un chatbot IA responde de forma inmediata a cualquier hora, en cualquier canal, con precisión y coherencia. La satisfacción del cliente aumenta notablemente.',
    stat: '<3s',
    label: 'tiempo de respuesta',
  },
  {
    title: 'Reducción del 50% en carga del equipo de soporte',
    description:
      'Tu equipo deja de responder las mismas preguntas una y otra vez. Se concentra en casos complejos, en fidelizar clientes y en tareas de mayor valor para el negocio.',
    stat: '50%',
    label: 'menos carga para el equipo',
  },
]

export default function ChatbotsInteligentesPage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Chatbots inteligentes
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Atención al cliente inteligente{' '}
            <span className="text-blue-400">sin esperas y sin límite de escala</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-10">
            Chatbots con inteligencia artificial entrenados con el conocimiento de tu empresa.
            Responden con precisión, escalan a un humano cuando toca y aprenden con cada
            conversación para ser cada vez mejores.
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
              No es un chatbot de árbol de decisión con respuestas rígidas. Es un asistente
              conversacional inteligente que entiende el contexto y responde como lo haría un
              experto de tu equipo.
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
              Resultados medibles que obtienen nuestros clientes tras implantar chatbots con IA.
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
            ¿Quieres un chatbot que realmente resuelva a tus clientes?
          </h2>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto mb-8">
            En 30 minutos analizamos tu casuística de atención al cliente y te mostramos cómo
            un chatbot IA gestionaría las consultas más frecuentes de tu negocio.
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
