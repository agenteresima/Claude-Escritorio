import type { Metadata } from 'next'
import Link from 'next/link'
import {
  Video,
  BarChart3,
  ShieldCheck,
  BookOpen,
  Map,
  Wrench,
  CheckCircle,
  ArrowRight,
  ChevronDown,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Consultor IA Externo para Empresas | Automatización Procesos IA',
  description:
    'Consultor de inteligencia artificial externo para empresas. Acompañamiento estratégico mensual: videollamadas, validación de herramientas, roadmap IA y formación del equipo. Desde 490 €/mes.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/consultor-ia-externo' },
  openGraph: {
    title: 'Consultor IA Externo para Empresas | Automatización Procesos IA',
    description:
      'Acompañamiento estratégico mensual en inteligencia artificial para directivos y gerentes. Sin compromiso de permanencia.',
  },
}

const includes = [
  {
    icon: Video,
    title: 'Videollamadas quincenales',
    description:
      'Dos sesiones al mes de 60 minutos para revisar el estado de los proyectos, tomar decisiones sobre nuevas herramientas, resolver dudas y mantener el rumbo estratégico.',
  },
  {
    icon: Wrench,
    title: 'Revisión y evaluación de herramientas',
    description:
      'Antes de contratar cualquier herramienta de IA, la evaluamos por ti: si es la adecuada para tu caso, si el precio es razonable, si tiene los controles de privacidad necesarios.',
  },
  {
    icon: ShieldCheck,
    title: 'Validación de proveedores',
    description:
      'Auditamos propuestas de proveedores de IA para que no te vendan humo. Te decimos si lo que proponen es factible, si el precio es justo y qué preguntas debes hacer.',
  },
  {
    icon: BarChart3,
    title: 'Apoyo en decisiones estratégicas',
    description:
      'Cuando tengas que tomar una decisión importante relacionada con la IA en tu empresa, tienes a un experto que conoce tu negocio con quien contrastarlo.',
  },
  {
    icon: BookOpen,
    title: 'Formación continua del equipo',
    description:
      'Formación práctica adaptada a las necesidades que vayan surgiendo: cómo usar mejor ChatGPT, cómo aprovechar Copilot, cómo supervisar las automatizaciones.',
  },
  {
    icon: Map,
    title: 'Roadmap de IA actualizado',
    description:
      'Mantenemos actualizado tu plan de implementación de IA, adaptándolo a medida que cambia la tecnología, el mercado y las necesidades de tu empresa.',
  },
]

const plans = [
  {
    name: 'Starter',
    price: '490',
    period: 'mes',
    description: 'Para empresas que empiezan a explorar la IA o que solo necesitan orientación estratégica básica.',
    features: [
      '1 videollamada mensual (60 min)',
      'Canal de comunicación por email',
      'Revisión de hasta 2 herramientas/mes',
      'Informe mensual de progreso',
      'Acceso a recursos y plantillas Automatización Procesos IA',
    ],
    cta: 'Solicitar videollamada',
    highlight: false,
  },
  {
    name: 'Professional',
    price: '890',
    period: 'mes',
    description: 'Para empresas con proyectos de IA activos que necesitan acompañamiento frecuente y apoyo en la implementación.',
    features: [
      '2 videollamadas mensuales (60 min c/u)',
      'Canal de comunicación por WhatsApp',
      'Revisión ilimitada de herramientas',
      'Validación de propuestas de proveedores',
      'Informe mensual + sesión de revisión',
      'Formación básica incluida (hasta 2h/mes)',
      'Revisión de automatizaciones en curso',
    ],
    cta: 'Solicitar videollamada',
    highlight: true,
  },
  {
    name: 'Executive',
    price: '1.490',
    period: 'mes',
    description: 'Para empresas con múltiples proyectos de IA en curso o que necesitan un experto disponible como parte del equipo directivo.',
    features: [
      '4 videollamadas mensuales (60 min c/u)',
      'Comunicación directa (WhatsApp + llamadas)',
      'Revisión ilimitada de herramientas y proveedores',
      'Participación en reuniones de dirección (1/mes)',
      'Formación incluida sin límite (hasta 4h/mes)',
      'Diseño y supervisión del roadmap de IA',
      'Acceso prioritario en urgencias',
      'Revisión de contratos con proveedores de IA',
    ],
    cta: 'Solicitar videollamada',
    highlight: false,
  },
]

const forWhom = [
  { role: 'Director General', reason: 'Quieres que la IA sea un activo estratégico sin tener que convertirte en experto técnico.' },
  { role: 'Director de Operaciones', reason: 'Tienes procesos que quieres mejorar con IA pero no sabes por dónde empezar ni qué herramientas usar.' },
  { role: 'Director Financiero (CFO)', reason: 'Quieres controlar el gasto en IA, validar propuestas y asegurarte de que las inversiones tienen retorno real.' },
  { role: 'Gerente de pyme', reason: 'Llevas el día a día de la empresa y necesitas a alguien de confianza que te oriente sin complicaciones.' },
]

const faqs = [
  {
    q: '¿Cuánto dura el compromiso mínimo?',
    a: 'No hay permanencia obligatoria. Puedes cancelar con un preaviso de 30 días. Dicho eso, los resultados más sólidos se ven a partir del tercer mes de acompañamiento.',
  },
  {
    q: '¿Qué pasa si necesito más horas de las incluidas?',
    a: 'Puedes ampliar el servicio con horas adicionales de consultoría a 120 €/hora. En la práctica, la mayoría de clientes encuentran que las horas incluidas son suficientes para el acompañamiento mensual.',
  },
  {
    q: '¿Trabajan con empresas de cualquier sector?',
    a: 'Sí. Tenemos experiencia en asesorías, logística, salud, construcción, ecommerce, industria, servicios profesionales y más. Lo que importa no es el sector sino los procesos.',
  },
  {
    q: '¿El servicio incluye implementación técnica?',
    a: 'El servicio de consultor externo es estratégico y de acompañamiento. Si necesitas implementación técnica (automatizaciones, agentes IA, integraciones), la podemos incluir como proyecto separado con precio acordado.',
  },
  {
    q: '¿Puedo cambiar de modalidad?',
    a: 'Sí, puedes subir o bajar de modalidad en cualquier momento con un preaviso de 30 días. Muchos clientes empiezan en Starter y pasan a Professional cuando tienen proyectos activos.',
  },
  {
    q: '¿Cómo son las videollamadas?',
    a: 'Por Google Meet o Teams, según tu preferencia. Siempre con el mismo consultor asignado a tu cuenta, que conoce el contexto de tu empresa. Recibes un resumen por escrito después de cada sesión.',
  },
]

export default function ConsultorIAExternoPage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Consultor IA externo
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Tu consultor de inteligencia artificial{' '}
            <span className="text-blue-400">externo</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-8">
            Un experto en IA que conoce tu empresa, te acompaña en las decisiones, te ayuda a
            elegir las herramientas correctas y te asegura que la inversión tiene retorno real. Sin
            contratarlo en plantilla.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/contacto?servicio=consultor-externo"
              className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
            >
              Solicitar una videollamada
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="#planes"
              className="inline-flex items-center justify-center gap-2 border border-slate-600 hover:border-slate-400 text-slate-300 hover:text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
            >
              Ver planes y precios
              <ChevronDown className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* What's included */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Qué incluye el servicio</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Un acompañamiento mensual completo para que la IA funcione en tu empresa, no solo
              sobre el papel.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {includes.map((item) => {
              const Icon = item.icon
              return (
                <div key={item.title} className="bg-slate-50 rounded-2xl p-6">
                  <div className="bg-blue-100 p-2.5 rounded-xl w-fit mb-4">
                    <Icon className="h-5 w-5 text-blue-700" />
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">{item.title}</h3>
                  <p className="text-sm text-slate-600">{item.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* For whom */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Para quién es</h2>
            <p className="text-slate-600">
              El servicio está diseñado para directivos y responsables que toman decisiones de
              negocio, no para perfiles técnicos.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            {forWhom.map((item) => (
              <div
                key={item.role}
                className="bg-white border border-slate-200 rounded-xl p-5 flex gap-4"
              >
                <CheckCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-900">{item.role}</p>
                  <p className="text-sm text-slate-600 mt-1">{item.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Plans */}
      <section id="planes" className="py-20 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Planes y precios</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Sin permanencia obligatoria. Cancela cuando quieras con 30 días de preaviso.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl border p-8 flex flex-col ${
                  plan.highlight
                    ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500/20 relative'
                    : 'border-slate-200 bg-white'
                }`}
              >
                {plan.highlight && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-semibold px-4 py-1 rounded-full whitespace-nowrap">
                    Más popular
                  </span>
                )}
                <div className="mb-6">
                  <h3 className="text-xl font-bold text-slate-900 mb-1">{plan.name}</h3>
                  <div className="flex items-baseline gap-1 mb-3">
                    <span className="text-4xl font-bold text-slate-900">{plan.price} €</span>
                    <span className="text-slate-500">/{plan.period}</span>
                  </div>
                  <p className="text-sm text-slate-600">{plan.description}</p>
                </div>

                <ul className="space-y-3 mb-8 flex-grow">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-slate-700">
                      <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                      {f}
                    </li>
                  ))}
                </ul>

                <Link
                  href="/contacto?servicio=consultor-externo"
                  className={`inline-flex items-center justify-center gap-2 font-semibold py-3 rounded-xl transition-colors ${
                    plan.highlight
                      ? 'bg-blue-600 hover:bg-blue-500 text-white'
                      : 'border border-slate-300 hover:border-blue-500 hover:text-blue-600 text-slate-700'
                  }`}
                >
                  {plan.cta}
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            ))}
          </div>

          <p className="text-center text-sm text-slate-500 mt-8">
            Todos los precios excluyen IVA. Sin permanencia mínima. Facturación mensual.
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Preguntas frecuentes</h2>
          </div>

          <div className="space-y-4">
            {faqs.map((faq) => (
              <div key={faq.q} className="bg-white border border-slate-200 rounded-xl p-6">
                <h3 className="font-semibold text-slate-900 mb-2">{faq.q}</h3>
                <p className="text-sm text-slate-600">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-blue-600">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            ¿Quieres saber si encaja con tu empresa?
          </h2>
          <p className="text-blue-100 mb-8">
            Solicita una videollamada de 30 minutos sin coste. Te explicamos cómo funciona el
            servicio, respondemos tus preguntas y, si tiene sentido, acordamos los siguientes pasos.
          </p>
          <Link
            href="/contacto?servicio=consultor-externo"
            className="inline-flex items-center gap-2 bg-white hover:bg-blue-50 text-blue-700 font-bold px-8 py-4 rounded-xl transition-colors"
          >
            Solicitar videollamada gratuita
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>
    </>
  )
}
