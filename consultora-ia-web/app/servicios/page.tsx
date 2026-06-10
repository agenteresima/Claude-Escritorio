import type { Metadata } from 'next'
import Link from 'next/link'
import {
  Brain,
  Cpu,
  GraduationCap,
  LayoutDashboard,
  Search,
  Users,
  ArrowRight,
  CheckCircle,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Servicios de Consultoría IA para Empresas | Automatización Procesos IA',
  description:
    'Automatización de procesos, agentes IA, consultor externo, auditoría y formación en inteligencia artificial para empresas. Soluciones prácticas con resultados medibles.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/servicios' },
  openGraph: {
    title: 'Servicios de Consultoría IA para Empresas | Automatización Procesos IA',
    description:
      'Automatización de procesos, agentes IA, consultor externo, auditoría y formación en inteligencia artificial para empresas.',
    url: 'https://www.automatizacionprocesos.es/servicios',
  },
}

const services = [
  {
    icon: Search,
    title: 'Auditoría IA',
    slug: 'auditoria-ia',
    price: 'Desde 790 €',
    description:
      'Analizamos todos tus procesos y te entregamos un informe con exactamente qué puedes automatizar, cuánto tiempo ahorrarías y cuánto costaría. El punto de partida correcto.',
    benefits: [
      'Mapa completo de automatizaciones posibles',
      'Priorización por impacto y esfuerzo',
      'Estimación de ahorro en horas y euros',
      'Plan de acción concreto',
    ],
    cta: 'Solicitar auditoría',
    highlight: false,
  },
  {
    icon: Cpu,
    title: 'Automatización de procesos',
    slug: 'automatizacion-procesos',
    price: 'Proyecto desde 2.500 €',
    description:
      'Automatizamos los procesos administrativos, de comunicación y de gestión que consumen más tiempo de tu equipo: facturas, emails, informes, CRM, ERP y mucho más.',
    benefits: [
      'Procesamiento automático de facturas y documentos',
      'Emails y seguimientos automáticos',
      'Informes generados solos',
      'Integración con tus sistemas actuales',
    ],
    cta: 'Ver automatizaciones',
    highlight: true,
  },
  {
    icon: Brain,
    title: 'Agentes IA',
    slug: 'agentes-ia',
    price: 'Proyecto desde 5.000 €',
    description:
      'Desarrollamos agentes de inteligencia artificial personalizados para tu empresa: comercial, atención al cliente, administración, reporting. Trabajan 24/7 sin errores.',
    benefits: [
      'Agente comercial que cualifica leads',
      'Agente de atención al cliente 24/7',
      'Agente administrativo que procesa documentos',
      'Integración con email, CRM y ERP',
    ],
    cta: 'Ver agentes',
    highlight: false,
  },
  {
    icon: Users,
    title: 'Consultor IA externo',
    slug: 'consultor-ia-externo',
    price: 'Desde 490 €/mes',
    description:
      'Tu experto en IA sin contratarlo en plantilla. Acompañamiento mensual continuo: videollamadas quincenales, revisión de herramientas, validación de proveedores y roadmap.',
    benefits: [
      'Videollamadas quincenales de estrategia',
      'Revisión y validación de herramientas',
      'Apoyo en decisiones de compra',
      'Formación continua del equipo',
    ],
    cta: 'Ver modalidades',
    highlight: false,
  },
  {
    icon: GraduationCap,
    title: 'Formación en IA',
    slug: 'formacion-ia',
    price: 'Desde 800 €',
    description:
      'Formación práctica y aplicada para que tu equipo domine ChatGPT, Claude, Copilot y las herramientas de automatización. Sin teoría innecesaria. Solo lo que sirve en el trabajo del día a día.',
    benefits: [
      'Formación presencial, online o híbrida',
      'Adaptada al sector y rol de tu equipo',
      'Materiales descargables incluidos',
      'Seguimiento post-formación',
    ],
    cta: 'Ver módulos',
    highlight: false,
  },
  {
    icon: LayoutDashboard,
    title: 'Casos de uso',
    slug: 'casos-uso',
    price: 'Consulta libre',
    description:
      'Descubre cómo empresas de tu sector están usando la IA: asesorías, logísticas, clínicas, constructoras, ecommerce y más. Casos reales con resultados medibles.',
    benefits: [
      'Casos por sector y tipo de empresa',
      'Tecnologías usadas en cada caso',
      'Resultados y ahorro real',
      'Aplicable a tu situación concreta',
    ],
    cta: 'Ver casos',
    highlight: false,
  },
]

const selectionGuide = [
  {
    profile: 'No sé por dónde empezar',
    recommendation: 'Auditoría IA',
    slug: 'auditoria-ia',
    description: 'Un diagnóstico profesional te da el mapa completo antes de invertir.',
  },
  {
    profile: 'Quiero automatizar procesos concretos',
    recommendation: 'Automatización de procesos',
    slug: 'automatizacion-procesos',
    description: 'Ya sabes qué quieres automatizar. Nosotros lo construimos.',
  },
  {
    profile: 'Necesito un asistente inteligente personalizado',
    recommendation: 'Agentes IA',
    slug: 'agentes-ia',
    description: 'Un agente que trabaja en tu nombre, integrado en tus sistemas.',
  },
  {
    profile: 'Quiero un experto IA sin contratarlo',
    recommendation: 'Consultor IA externo',
    slug: 'consultor-ia-externo',
    description: 'Acompañamiento estratégico mensual. Pagas solo por lo que necesitas.',
  },
  {
    profile: 'Mi equipo necesita formarse en IA',
    recommendation: 'Formación en IA',
    slug: 'formacion-ia',
    description: 'Formación práctica adaptada al trabajo real de tu equipo.',
  },
]

export default function ServiciosPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'ItemList',
            name: 'Servicios de Automatización Procesos IA',
            description: 'Consultoría de inteligencia artificial para empresas',
            url: 'https://www.automatizacionprocesos.es/servicios',
            itemListElement: services.map((s, i) => ({
              '@type': 'ListItem',
              position: i + 1,
              item: {
                '@type': 'Service',
                name: s.title,
                description: s.description,
                url: `https://www.automatizacionprocesos.es/${s.slug}`,
                provider: {
                  '@type': 'Organization',
                  name: 'Automatización Procesos IA',
                },
              },
            })),
          }),
        }}
      />

      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Servicios de IA para empresas
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Servicios de inteligencia artificial{' '}
            <span className="text-blue-400">para empresas</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-8">
            No vendemos tecnología. Resolvemos problemas concretos de negocio con IA. Desde la
            primera auditoría hasta el agente en producción, estamos contigo en cada paso.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/diagnostico-gratuito"
              className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
            >
              Diagnóstico gratuito
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
      </section>

      {/* Services Grid */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Qué hacemos</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Cada servicio está diseñado para resolver un problema empresarial concreto, con
              resultados medibles y transferencia de conocimiento a tu equipo.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((service) => {
              const Icon = service.icon
              return (
                <div
                  key={service.slug}
                  className={`relative rounded-2xl border p-6 flex flex-col ${
                    service.highlight
                      ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500/20'
                      : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-md'
                  } transition-all`}
                >
                  {service.highlight && (
                    <span className="absolute -top-3 left-6 bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
                      Más solicitado
                    </span>
                  )}
                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className={`p-2.5 rounded-xl ${service.highlight ? 'bg-blue-600' : 'bg-slate-100'}`}
                    >
                      <Icon
                        className={`h-5 w-5 ${service.highlight ? 'text-white' : 'text-slate-700'}`}
                      />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900">{service.title}</h3>
                      <span className="text-sm text-blue-600 font-medium">{service.price}</span>
                    </div>
                  </div>
                  <p className="text-sm text-slate-600 mb-4 flex-grow">{service.description}</p>
                  <ul className="space-y-2 mb-6">
                    {service.benefits.map((b) => (
                      <li key={b} className="flex items-start gap-2 text-sm text-slate-700">
                        <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                        {b}
                      </li>
                    ))}
                  </ul>
                  <Link
                    href={`/${service.slug}`}
                    className={`inline-flex items-center justify-center gap-2 font-semibold text-sm px-4 py-2.5 rounded-lg transition-colors ${
                      service.highlight
                        ? 'bg-blue-600 hover:bg-blue-500 text-white'
                        : 'border border-slate-300 hover:border-blue-500 hover:text-blue-600 text-slate-700'
                    }`}
                  >
                    {service.cta}
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Selection Guide */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              ¿Qué servicio necesitas?
            </h2>
            <p className="text-slate-600">
              Encuentra el servicio adecuado según tu situación actual.
            </p>
          </div>

          <div className="space-y-4">
            {selectionGuide.map((item) => (
              <Link
                key={item.slug}
                href={`/${item.slug}`}
                className="flex items-center justify-between gap-4 bg-white border border-slate-200 hover:border-blue-400 rounded-xl px-6 py-4 group transition-all hover:shadow-md"
              >
                <div>
                  <p className="font-semibold text-slate-900 group-hover:text-blue-700 transition-colors">
                    {item.profile}
                  </p>
                  <p className="text-sm text-slate-500 mt-0.5">{item.description}</p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className="hidden sm:block text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                    {item.recommendation}
                  </span>
                  <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-blue-600 transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-blue-600">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            ¿No estás seguro por dónde empezar?
          </h2>
          <p className="text-blue-100 mb-8 text-lg">
            En 45 minutos de videollamada gratuita analizamos tu empresa y te decimos exactamente
            qué tiene sentido hacer, por dónde empezar y cuánto costaría. Sin compromiso.
          </p>
          <Link
            href="/diagnostico-gratuito"
            className="inline-flex items-center gap-2 bg-white hover:bg-blue-50 text-blue-700 font-bold px-8 py-4 rounded-xl transition-colors text-lg"
          >
            Solicitar diagnóstico gratuito
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>
    </>
  )
}
