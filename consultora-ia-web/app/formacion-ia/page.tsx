import type { Metadata } from 'next'
import Link from 'next/link'
import {
  MessageSquare,
  FileText,
  Monitor,
  Sliders,
  Zap,
  ShieldCheck,
  Video,
  Users,
  BookOpen,
  CheckCircle,
  ArrowRight,
  GraduationCap,
  Clock,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Formación IA para Equipos Empresariales | AP Automatización IA',
  description:
    'Formación práctica en inteligencia artificial para equipos empresariales: ChatGPT, Claude, Microsoft Copilot, diseño de prompts y automatización. Presencial, online y grabado.',
  alternates: { canonical: 'https://automatizacionprocesos.es/formacion-ia' },
  openGraph: {
    title: 'Formación IA para Equipos Empresariales | AP Automatización IA',
    description:
      'Formación práctica en IA adaptada al trabajo real de tu equipo. Desde medio día hasta 3 días. Presencial, online o grabado.',
    url: 'https://automatizacionprocesos.es/formacion-ia',
  },
}

const modules = [
  {
    icon: MessageSquare,
    title: 'ChatGPT para empresas',
    duration: '3 horas',
    description:
      'Uso práctico de ChatGPT en el entorno empresarial: redacción de emails y documentos, análisis de información, soporte a ventas, gestión de RRHH y tareas administrativas. Ejercicios reales adaptados al sector de la empresa.',
    departments: ['Administración', 'Ventas', 'RRHH', 'Dirección'],
  },
  {
    icon: FileText,
    title: 'Claude para análisis y redacción',
    duration: '3 horas',
    description:
      'Aprovechamiento de Claude para tareas que requieren análisis en profundidad: revisión de contratos, informes financieros, documentación técnica, comunicaciones formales y toma de decisiones con datos complejos.',
    departments: ['Dirección', 'Finanzas', 'Legal', 'Operaciones'],
  },
  {
    icon: Monitor,
    title: 'Microsoft Copilot para M365',
    duration: '4 horas',
    description:
      'Integración completa de Copilot en el flujo de trabajo diario de Microsoft 365: resumen de reuniones en Teams, redacción en Outlook, análisis de datos en Excel, creación de presentaciones en PowerPoint y gestión documental en SharePoint.',
    departments: ['Todos los departamentos', 'Administración', 'Dirección'],
  },
  {
    icon: Sliders,
    title: 'Diseño de prompts efectivos',
    duration: '2 horas',
    description:
      'Técnicas avanzadas para obtener resultados consistentes y de calidad de los modelos de IA. Prompts por departamento, plantillas reutilizables, técnicas de refinamiento y cómo adaptar las instrucciones al contexto empresarial específico.',
    departments: ['Todos los departamentos'],
  },
  {
    icon: Zap,
    title: 'Automatización básica sin código',
    duration: '4 horas',
    description:
      'Introducción práctica a las herramientas de automatización: Zapier, Make y Power Automate. Creación de flujos básicos para conectar aplicaciones, automatizar emails, actualizar hojas de cálculo y enviar notificaciones automáticas.',
    departments: ['Administración', 'Operaciones', 'Marketing'],
  },
  {
    icon: ShieldCheck,
    title: 'Seguridad, privacidad y buenas prácticas',
    duration: '2 horas',
    description:
      'Marco regulatorio del uso de IA en empresas españolas: RGPD y datos personales, qué información no enviar a herramientas de IA, cómo gestionar la confidencialidad, evaluación de riesgos y protocolo de uso responsable.',
    departments: ['Dirección', 'Responsables de área', 'Toda la empresa'],
  },
]

const formats = [
  {
    icon: Video,
    title: 'Online en directo',
    description:
      'Sesiones en vídeoconferencia con el formador. Permite la interacción en tiempo real, resolución de dudas y ejercicios prácticos. Recomendado para equipos distribuidos geográficamente.',
    ideal: 'Equipos en diferentes ubicaciones',
  },
  {
    icon: Users,
    title: 'Presencial',
    description:
      'Formación en las instalaciones de tu empresa o en sala externa. Mayor dinámica de grupo, ejercicios colaborativos y seguimiento individual. Requiere desplazamiento del formador.',
    ideal: 'Equipos en una misma ubicación',
  },
  {
    icon: BookOpen,
    title: 'Grabado + tutorías',
    description:
      'Acceso a las grabaciones de los módulos más las sesiones de seguimiento en directo para resolver dudas. Permite que cada miembro del equipo aprenda a su propio ritmo.',
    ideal: 'Equipos con horarios variables',
  },
]

const forWhom = [
  {
    role: 'Administración',
    uses: ['Procesamiento de documentos', 'Redacción de comunicaciones', 'Gestión de agenda', 'Informes automáticos'],
  },
  {
    role: 'Ventas y comercial',
    uses: ['Preparación de propuestas', 'Seguimiento de clientes', 'Cualificación de leads', 'Análisis de competencia'],
  },
  {
    role: 'Finanzas',
    uses: ['Análisis de datos', 'Elaboración de informes', 'Detección de anomalías', 'Presentaciones ejecutivas'],
  },
  {
    role: 'RRHH',
    uses: ['Criba de candidatos', 'Redacción de ofertas', 'Onboarding de nuevas incorporaciones', 'Comunicación interna'],
  },
  {
    role: 'Dirección',
    uses: ['Toma de decisiones con datos', 'Resumen de informes extensos', 'Preparación de reuniones', 'Estrategia con IA'],
  },
]

export default function FormacionIAPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'EducationalOrganization',
            name: 'AP Automatización IA - Formación en IA para Empresas',
            description: 'Formación práctica en inteligencia artificial para equipos empresariales.',
            url: 'https://automatizacionprocesos.es/formacion-ia',
          }),
        }}
      />

      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
              Formación en IA
            </span>
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
              Formación práctica en inteligencia artificial{' '}
              <span className="text-blue-400">para equipos</span>
            </h1>
            <p className="text-lg text-slate-300 mb-8 leading-relaxed">
              Sin teoría innecesaria. Solo lo que sirve en el trabajo real. Formación diseñada para
              que tu equipo empiece a usar la IA de forma eficiente desde el primer día, adaptada
              al sector y al rol de cada persona.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 mb-10">
              <Link
                href="/contacto"
                className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
              >
                Solicitar propuesta
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/diagnostico-gratuito"
                className="inline-flex items-center justify-center gap-2 border border-slate-600 hover:border-slate-400 text-slate-300 hover:text-white font-semibold px-8 py-3.5 rounded-xl transition-colors"
              >
                Diagnóstico gratuito
              </Link>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {[
                { value: 'Desde 800 €', label: 'Por sesión o grupo' },
                { value: 'Medio día - 3 días', label: 'Duración flexible' },
                { value: '3 formatos', label: 'Presencial, online, grabado' },
              ].map((stat) => (
                <div key={stat.label} className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                  <div className="text-lg font-bold text-blue-400 mb-1">{stat.value}</div>
                  <div className="text-xs text-slate-400">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Modules */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Módulos formativos</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Cada módulo puede contratarse de forma independiente o combinarse para crear un
              programa formativo a medida. Todos incluyen materiales descargables.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {modules.map((mod) => {
              const Icon = mod.icon
              return (
                <div
                  key={mod.title}
                  className="border border-slate-200 rounded-2xl p-6 hover:border-blue-300 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 bg-blue-50 rounded-xl">
                        <Icon className="h-5 w-5 text-blue-600" />
                      </div>
                      <h3 className="font-bold text-slate-900">{mod.title}</h3>
                    </div>
                    <span className="inline-flex items-center gap-1 text-xs text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full flex-shrink-0">
                      <Clock className="h-3 w-3" />
                      {mod.duration}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mb-4 leading-relaxed">{mod.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {mod.departments.map((dept) => (
                      <span
                        key={dept}
                        className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-full"
                      >
                        {dept}
                      </span>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Formats */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Formatos disponibles</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Adaptamos el formato a las necesidades de tu equipo y a la estructura de tu empresa.
            </p>
          </div>
          <div className="grid sm:grid-cols-3 gap-6">
            {formats.map((format) => {
              const Icon = format.icon
              return (
                <div key={format.title} className="bg-white border border-slate-200 rounded-2xl p-6 text-center">
                  <div className="p-3 bg-blue-50 rounded-xl w-fit mx-auto mb-4">
                    <Icon className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="font-bold text-slate-900 mb-2">{format.title}</h3>
                  <p className="text-sm text-slate-600 mb-4 leading-relaxed">{format.description}</p>
                  <span className="text-xs text-green-700 bg-green-50 border border-green-200 px-3 py-1 rounded-full">
                    Ideal: {format.ideal}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* For whom */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Para quién está diseñada</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Cada departamento tiene necesidades distintas. Adaptamos el contenido al trabajo
              real de cada rol.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {forWhom.map((item) => (
              <div key={item.role} className="border border-slate-200 rounded-xl p-5">
                <h3 className="font-semibold text-slate-900 mb-3">{item.role}</h3>
                <ul className="space-y-2">
                  {item.uses.map((use) => (
                    <li key={use} className="flex items-start gap-2 text-sm text-slate-600">
                      <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                      {use}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Precios orientativos</h2>
            <p className="text-slate-600">
              El precio final depende del número de módulos, el formato, la duración y el número de
              participantes. Contacta para un presupuesto personalizado.
            </p>
          </div>
          <div className="grid sm:grid-cols-3 gap-6">
            {[
              { name: 'Sesión introductoria', price: 'Desde 800 €', duration: 'Medio día (4h)', includes: 'Un módulo, hasta 15 personas' },
              { name: 'Formación departamental', price: 'Desde 1.500 €', duration: '1 día completo (8h)', includes: 'Dos módulos combinados, materiales' },
              { name: 'Programa completo', price: 'Desde 3.500 €', duration: '2-3 días', includes: 'Todos los módulos relevantes, seguimiento post-formación' },
            ].map((plan) => (
              <div key={plan.name} className="bg-white border border-slate-200 rounded-2xl p-6 text-center">
                <h3 className="font-bold text-slate-900 mb-2">{plan.name}</h3>
                <div className="text-2xl font-bold text-blue-600 mb-1">{plan.price}</div>
                <p className="text-sm text-slate-500 mb-2">{plan.duration}</p>
                <p className="text-xs text-slate-400">{plan.includes}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-blue-600">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 text-center">
          <GraduationCap className="h-10 w-10 text-blue-200 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-white mb-4">
            ¿Tu equipo está usando la IA bien?
          </h2>
          <p className="text-blue-100 mb-8 text-lg">
            La mayoría de equipos usan el 10% del potencial de las herramientas que ya tienen
            contratadas. Con la formación adecuada, ese porcentaje puede multiplicarse en días.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/contacto"
              className="inline-flex items-center gap-2 bg-white hover:bg-blue-50 text-blue-700 font-bold px-8 py-4 rounded-xl transition-colors text-lg"
            >
              Solicitar propuesta
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/diagnostico-gratuito"
              className="inline-flex items-center gap-2 border-2 border-white/50 hover:border-white text-white font-bold px-8 py-4 rounded-xl transition-colors text-lg"
            >
              Diagnóstico gratuito
            </Link>
          </div>
        </div>
      </section>
    </>
  )
}
