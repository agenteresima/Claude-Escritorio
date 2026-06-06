import Link from 'next/link'
import { CheckCircle, Zap, Bot, GraduationCap, ArrowRight, Star } from 'lucide-react'

export const metadata = {
  title: 'Precios y tarifas — AP Automatización IA',
  description:
    'Consulta nuestros precios orientativos para servicios de IA empresarial. Automatización de procesos, agentes IA, formación y consultoría estratégica. Presupuesto personalizado sin compromiso.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/precios' },
}

const plans = [
  {
    name: 'Automatización Starter',
    price: 'Desde 1.500 €',
    subtitle: 'Pago único',
    badge: 'Más popular para pymes',
    featured: true,
    icon: Zap,
    features: [
      'Diagnóstico y auditoría de procesos (45 min)',
      'Automatización de 1-2 procesos con n8n o Make',
      'Integración con tus herramientas actuales (CRM, ERP, email)',
      'Formación al equipo (2h)',
      '30 días de soporte post-implementación',
      'ROI estimado en el informe previo',
    ],
    cta: 'Solicitar diagnóstico gratuito',
    ctaHref: '/diagnostico-gratuito',
    ctaStyle: 'bg-blue-600 text-white hover:bg-blue-700',
  },
  {
    name: 'Agente IA Personalizado',
    price: 'Desde 3.500 €',
    subtitle: 'Pago único',
    badge: null,
    featured: false,
    icon: Bot,
    features: [
      'Todo lo del plan Starter',
      'Desarrollo de agente IA a medida con LLM',
      'Conexión con base de datos y documentos internos',
      'Panel de administración y monitorización',
      'Formación avanzada al equipo (4h)',
      '60 días de soporte y optimización',
    ],
    cta: 'Solicitar presupuesto',
    ctaHref: '/contacto',
    ctaStyle: 'bg-slate-900 text-white hover:bg-slate-800',
  },
  {
    name: 'Transformación Digital IA',
    price: 'Desde 8.000 €',
    subtitle: 'Proyecto completo',
    badge: 'Para empresas en crecimiento',
    featured: false,
    icon: GraduationCap,
    features: [
      'Auditoría completa de todos los procesos',
      'Hoja de ruta de IA para 12 meses',
      'Implementación de 4-6 automatizaciones',
      '2 agentes IA personalizados',
      'Formación completa del equipo + certificación',
      '6 meses de soporte y optimización continua',
      'Informes mensuales de ROI',
    ],
    cta: 'Hablar con un consultor',
    ctaHref: '/contacto',
    ctaStyle: 'bg-blue-600 text-white hover:bg-blue-700',
  },
]

const included = [
  'Diagnóstico inicial gratuito sin compromiso',
  'Propuesta detallada con ROI estimado antes de empezar',
  'Implementación ágil: resultados en 4-6 semanas',
  'Formación del equipo incluida en todos los planes',
]

const faqs = [
  {
    question: '¿Hay costes mensuales adicionales?',
    answer:
      'Las herramientas de automatización (n8n, Make) tienen sus propios costes de suscripción, generalmente entre 20-50€/mes. Los LLMs (OpenAI, Anthropic) se pagan por uso. Te lo detallamos todo en el presupuesto.',
  },
  {
    question: '¿Puedo empezar con un proyecto pequeño?',
    answer:
      'Sí. Recomendamos siempre empezar con el plan Starter para validar resultados antes de escalar.',
  },
  {
    question: '¿Los precios son fijos?',
    answer:
      'Son orientativos. Cada proyecto es diferente y hacemos un presupuesto personalizado tras el diagnóstico gratuito.',
  },
  {
    question: '¿Ofrecéis financiación?',
    answer:
      'Sí, trabajamos con opciones de pago en 2-3 plazos sin intereses para proyectos superiores a 3.000€.',
  },
]

export default function PreciosPage() {
  return (
    <main>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <span className="inline-block bg-blue-500/20 text-blue-300 border border-blue-500/30 text-sm font-semibold px-4 py-1.5 rounded-full mb-6">
            Precios transparentes
          </span>
          <h1 className="text-4xl md:text-5xl font-black mb-6 leading-tight">
            Inversión clara, resultados medibles
          </h1>
          <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
            Sin letras pequeñas. Sin sorpresas. Estos son nuestros precios orientativos para que
            puedas planificar tu inversión en IA.
          </p>
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-400/20 text-blue-200 text-sm px-4 py-2 rounded-lg">
            <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0" />
            Todos los proyectos incluyen diagnóstico inicial gratuito
          </div>
        </div>
      </section>

      {/* Plans */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900">
              Elige el punto de entrada que mejor se adapta a tu empresa
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8 items-stretch">
            {plans.map((plan) => {
              const Icon = plan.icon
              return (
                <div
                  key={plan.name}
                  className={`relative flex flex-col rounded-2xl p-8 ${
                    plan.featured
                      ? 'border-2 border-blue-500 shadow-2xl shadow-blue-100'
                      : 'border border-slate-200 shadow-sm'
                  }`}
                >
                  {plan.badge && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <span className="inline-flex items-center gap-1.5 bg-blue-600 text-white text-xs font-bold px-4 py-1.5 rounded-full whitespace-nowrap">
                        <Star className="w-3 h-3" />
                        {plan.badge}
                      </span>
                    </div>
                  )}
                  <div className="mb-6">
                    <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-4">
                      <Icon className="w-6 h-6 text-blue-600" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-1">{plan.name}</h3>
                    <div className="text-3xl font-black text-slate-900 mt-3">{plan.price}</div>
                    <div className="text-sm text-slate-500 mt-1">{plan.subtitle}</div>
                  </div>
                  <ul className="space-y-3 flex-1 mb-8">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2.5 text-sm text-slate-600">
                        <CheckCircle className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <Link
                    href={plan.ctaHref}
                    className={`inline-flex items-center justify-center gap-2 w-full py-3 px-6 rounded-xl font-semibold transition-colors ${plan.ctaStyle}`}
                  >
                    {plan.cta}
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Always included */}
      <section className="bg-slate-50 py-16">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl md:text-3xl font-bold text-slate-900">
              ¿Qué está incluido siempre?
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 gap-6">
            {included.map((item) => (
              <div
                key={item}
                className="flex items-start gap-3 bg-white rounded-xl p-5 border border-slate-100 shadow-sm"
              >
                <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <span className="text-slate-700 font-medium">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-16 bg-white">
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl md:text-3xl font-bold text-slate-900">
              Preguntas frecuentes sobre precios
            </h2>
          </div>
          <div className="space-y-6">
            {faqs.map((faq) => (
              <div key={faq.question} className="border border-slate-100 rounded-xl p-6 shadow-sm">
                <h3 className="font-bold text-slate-900 mb-2">{faq.question}</h3>
                <p className="text-slate-600 leading-relaxed">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-blue-600 text-white py-16">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            ¿No sabes qué plan necesitas?
          </h2>
          <p className="text-blue-100 text-lg mb-8">
            En 45 minutos analizamos tu empresa y te decimos exactamente qué automatizar primero
            y cuánto te va a costar.
          </p>
          <Link
            href="/diagnostico-gratuito"
            className="inline-flex items-center gap-2 bg-white text-blue-600 font-bold px-8 py-4 rounded-xl hover:bg-blue-50 transition-colors text-lg"
          >
            Solicitar diagnóstico gratuito
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </main>
  )
}
