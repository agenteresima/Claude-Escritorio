import type { Metadata } from 'next'
import Link from 'next/link'
import {
  ShoppingCart,
  HeadphonesIcon,
  ClipboardList,
  TrendingUp,
  BarChart3,
  BookOpen,
  CheckCircle,
  ArrowRight,
  Brain,
  Zap,
  XCircle,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Agentes IA para Empresas | Automatización Procesos IA',
  description:
    'Desarrollamos agentes de inteligencia artificial personalizados para tu empresa: comercial, atención al cliente, administración, finanzas y reporting. Trabajan 24/7 integrados en tus sistemas.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/agentes-ia' },
  openGraph: {
    title: 'Agentes IA para Empresas | Automatización Procesos IA',
    description:
      'Agentes de inteligencia artificial que trabajan 24/7 integrados en tus sistemas: CRM, ERP, email, WhatsApp Business.',
    url: 'https://www.automatizacionprocesos.es/agentes-ia',
  },
}

const agentTypes = [
  {
    icon: ShoppingCart,
    title: 'Agente Comercial',
    description:
      'Cualifica automáticamente los leads que llegan por web, email o WhatsApp. Responde preguntas sobre productos y servicios, detecta el nivel de interés del prospecto y agenda reuniones directamente en el calendario del comercial adecuado. El equipo de ventas solo dedica tiempo a personas que ya han mostrado interés real.',
    features: ['Cualificación automática de leads', 'Respuesta a preguntas frecuentes de ventas', 'Agenda reuniones con el comercial', 'Disponible 24/7 en web, email y WhatsApp'],
    color: 'blue',
  },
  {
    icon: HeadphonesIcon,
    title: 'Agente de Atención al Cliente',
    description:
      'Resuelve incidencias frecuentes sin intervención humana: estado de pedidos, gestión de devoluciones según política definida, consultas sobre facturación, actualización de datos. Cuando la consulta escapa a su ámbito, escala al agente humano con todo el contexto ya recopilado.',
    features: ['Resolución de incidencias frecuentes 24/7', 'Gestión de devoluciones y reclamaciones', 'Escalado inteligente a agente humano', 'Historial completo de cada conversación'],
    color: 'green',
  },
  {
    icon: ClipboardList,
    title: 'Agente de Administración',
    description:
      'Procesa documentos entrantes, extrae datos de facturas y albaranes, los registra en los sistemas correspondientes y genera alertas cuando detecta anomalías. Gestiona flujos de aprobación y mantiene actualizadas las bases de datos sin intervención manual.',
    features: ['Procesamiento de facturas y albaranes', 'Registro automático en ERP y contabilidad', 'Detección de anomalías y alertas', 'Gestión de flujos de aprobación'],
    color: 'purple',
  },
  {
    icon: TrendingUp,
    title: 'Agente Financiero',
    description:
      'Monitoriza datos financieros en tiempo real, detecta desviaciones respecto al presupuesto, genera alertas cuando un KPI sale del rango esperado y elabora informes automáticos para el departamento financiero. Conectado con tu ERP y sistema bancario.',
    features: ['Monitorización de KPIs financieros en tiempo real', 'Alertas automáticas de desviaciones', 'Informes financieros automáticos', 'Conexión con ERP y extractos bancarios'],
    color: 'orange',
  },
  {
    icon: BarChart3,
    title: 'Agente de Reporting',
    description:
      'Recoge datos de todas las fuentes de la empresa, los consolida y genera reportes ejecutivos de forma automática: semanal, mensual o a demanda. Los directivos reciben siempre los datos clave sin tener que pedirlos ni esperar a que alguien los prepare.',
    features: ['Reportes automáticos para dirección', 'Consolidación de datos de múltiples fuentes', 'Envío programado por email', 'Formato personalizado por departamento'],
    color: 'teal',
  },
  {
    icon: BookOpen,
    title: 'Agente RAG (documentación interna)',
    description:
      'Aprende el contenido de tus manuales, procedimientos, políticas internas, catálogos y cualquier documentación de la empresa. Permite que cualquier persona del equipo haga preguntas en lenguaje natural y obtenga respuestas precisas basadas en tus propios documentos.',
    features: ['Responde sobre manuales y procedimientos', 'Catálogo de productos accesible en segundos', 'Políticas y normativas internas', 'Formación de nuevas incorporaciones'],
    color: 'indigo',
  },
]

const colorMap: Record<string, string> = {
  blue: 'bg-blue-50 border-blue-200 text-blue-600',
  green: 'bg-green-50 border-green-200 text-green-600',
  purple: 'bg-purple-50 border-purple-200 text-purple-600',
  orange: 'bg-orange-50 border-orange-200 text-orange-600',
  teal: 'bg-teal-50 border-teal-200 text-teal-600',
  indigo: 'bg-indigo-50 border-indigo-200 text-indigo-600',
}

const iconBgMap: Record<string, string> = {
  blue: 'bg-blue-100',
  green: 'bg-green-100',
  purple: 'bg-purple-100',
  orange: 'bg-orange-100',
  teal: 'bg-teal-100',
  indigo: 'bg-indigo-100',
}

const creationSteps = [
  {
    step: '01',
    title: 'Definición del proceso',
    description:
      'Documentamos en detalle qué hace el agente, qué decisiones toma en cada situación, qué herramientas necesita y cuáles son los límites de su actuación autónoma.',
  },
  {
    step: '02',
    title: 'Conexión con tus sistemas',
    description:
      'Integramos el agente con tus herramientas: CRM, ERP, email, WhatsApp Business, bases de datos y cualquier sistema con el que deba interactuar.',
  },
  {
    step: '03',
    title: 'Entrenamiento con tu contexto',
    description:
      'Le proporcionamos toda la información necesaria: catálogos, políticas, preguntas frecuentes, procedimientos y ejemplos de conversaciones reales.',
  },
  {
    step: '04',
    title: 'Pruebas y puesta en marcha',
    description:
      'Probamos con casos reales durante 2 semanas, ajustamos el comportamiento, validamos los resultados y formamos al equipo para supervisarlo.',
  },
]

const integrations = [
  'CRM (HubSpot, Salesforce, Zoho)',
  'ERP (SAP, Odoo, Navision)',
  'Email (Gmail, Outlook)',
  'WhatsApp Business',
  'Slack y Microsoft Teams',
  'Bases de datos (SQL, PostgreSQL)',
  'Google Sheets / Excel',
  'Notion y Confluence',
]

const chatbotVsAgent = [
  {
    feature: 'Toma decisiones',
    chatbot: false,
    agent: true,
  },
  {
    feature: 'Ejecuta acciones en sistemas externos',
    chatbot: false,
    agent: true,
  },
  {
    feature: 'Aprende y se adapta al contexto',
    chatbot: false,
    agent: true,
  },
  {
    feature: 'Puede gestionar conversaciones complejas',
    chatbot: false,
    agent: true,
  },
  {
    feature: 'Se integra con CRM, ERP, email',
    chatbot: false,
    agent: true,
  },
  {
    feature: 'Responde preguntas simples predefinidas',
    chatbot: true,
    agent: true,
  },
]

export default function AgentesIAPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Service',
            name: 'Agentes IA para Empresas',
            description:
              'Desarrollo de agentes de inteligencia artificial personalizados para empresas.',
            provider: { '@type': 'Organization', name: 'Automatización Procesos IA', url: 'https://www.automatizacionprocesos.es' },
            url: 'https://www.automatizacionprocesos.es/agentes-ia',
            offers: {
              '@type': 'Offer',
              price: '5000',
              priceCurrency: 'EUR',
              description: 'Proyecto desde 5.000 €',
            },
          }),
        }}
      />

      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
              Agentes IA
            </span>
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
              Agentes de inteligencia artificial{' '}
              <span className="text-blue-400">para tu empresa</span>
            </h1>
            <p className="text-lg text-slate-300 mb-8 leading-relaxed">
              Un agente IA es un colaborador digital que trabaja 24 horas al día, 7 días a la
              semana, integrado en tus sistemas. No solo responde preguntas: toma decisiones,
              ejecuta acciones y gestiona procesos completos de forma autónoma.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/diagnostico-gratuito"
                className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
              >
                Solicitar diagnóstico gratuito
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/contacto"
                className="inline-flex items-center justify-center gap-2 border border-slate-600 hover:border-slate-400 text-slate-300 hover:text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
              >
                Hablar con un consultor
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* What is an agent */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-6">
                ¿Qué es un agente IA?
              </h2>
              <p className="text-slate-600 mb-4 leading-relaxed">
                Un agente de inteligencia artificial es un sistema que entiende instrucciones en
                lenguaje natural, planifica cómo ejecutarlas, utiliza herramientas externas (tu
                CRM, tu email, tu ERP) y toma decisiones adaptadas al contexto de cada situación.
              </p>
              <p className="text-slate-600 mb-4 leading-relaxed">
                La diferencia clave con un chatbot tradicional es que el agente{' '}
                <strong className="text-slate-900">no solo responde: actúa</strong>. Puede
                actualizar el CRM tras una conversación, enviar un email de seguimiento, generar
                un documento o registrar una incidencia en el sistema de gestión.
              </p>
              <p className="text-slate-600 leading-relaxed">
                Piensa en él como un miembro del equipo que nunca se cansa, no comete errores de
                introducción de datos y escala inmediatamente cuando la situación lo requiere.
              </p>
            </div>
            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 mb-4 text-center">Chatbot vs Agente IA</h3>
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-2 text-xs font-semibold text-slate-500 pb-2 border-b border-slate-200">
                  <span>Capacidad</span>
                  <span className="text-center">Chatbot</span>
                  <span className="text-center">Agente IA</span>
                </div>
                {chatbotVsAgent.map((row) => (
                  <div key={row.feature} className="grid grid-cols-3 gap-2 items-center">
                    <span className="text-sm text-slate-600">{row.feature}</span>
                    <div className="flex justify-center">
                      {row.chatbot ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-300" />
                      )}
                    </div>
                    <div className="flex justify-center">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Agent types */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Tipos de agentes IA</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Desarrollamos agentes a medida para cada función de la empresa. Cada agente es
              único, entrenado con el contexto y los datos de tu negocio.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {agentTypes.map((agent) => {
              const Icon = agent.icon
              return (
                <div
                  key={agent.title}
                  className="bg-white border border-slate-200 rounded-2xl p-6 hover:shadow-md transition-all"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`p-2.5 rounded-xl ${iconBgMap[agent.color]}`}>
                      <Icon className={`h-5 w-5 ${colorMap[agent.color].split(' ')[2]}`} />
                    </div>
                    <h3 className="font-bold text-slate-900 text-lg">{agent.title}</h3>
                  </div>
                  <p className="text-slate-600 mb-4 leading-relaxed text-sm">
                    {agent.description}
                  </p>
                  <ul className="space-y-2">
                    {agent.features.map((f) => (
                      <li key={f} className="flex items-start gap-2 text-sm text-slate-700">
                        <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Creation process */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Cómo creamos tu agente</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Un proceso estructurado de 6 a 10 semanas desde el primer análisis hasta el agente
              en producción.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 gap-6">
            {creationSteps.map((step) => (
              <div key={step.step} className="border border-slate-200 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold text-sm">{step.step}</span>
                  </div>
                  <h3 className="font-bold text-slate-900">{step.title}</h3>
                </div>
                <p className="text-slate-600 text-sm leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Integraciones disponibles</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Los agentes se integran con las herramientas que ya utilizas. No tienes que cambiar
              ningún sistema.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-3">
            {integrations.map((integration) => (
              <span
                key={integration}
                className="bg-white border border-slate-200 rounded-full px-4 py-2 text-sm font-medium text-slate-700"
              >
                {integration}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-blue-600">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 text-center">
          <Brain className="h-10 w-10 text-blue-200 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-white mb-4">
            ¿Qué proceso de tu empresa podría gestionar un agente?
          </h2>
          <p className="text-blue-100 mb-8 text-lg">
            En 30 minutos de videollamada gratuita identificamos el agente que más impacto tendría
            en tu empresa y te explicamos cómo lo construiríamos. Sin compromiso.
          </p>
          <Link
            href="/diagnostico-gratuito"
            className="inline-flex items-center gap-2 bg-white hover:bg-blue-50 text-blue-700 font-bold px-8 py-4 rounded-xl transition-colors text-lg"
          >
            Solicitar diagnóstico gratuito
            <ArrowRight className="h-5 w-5" />
          </Link>
          <p className="text-blue-200 text-sm mt-4">
            Videollamada de 30 minutos · Sin coste · Sin compromiso
          </p>
        </div>
      </section>
    </>
  )
}
