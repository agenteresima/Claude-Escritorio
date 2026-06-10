import type { Metadata } from 'next'
import Link from 'next/link'
import { Target, Eye, BarChart3, GraduationCap, ArrowRight, CheckCircle2 } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Sobre nosotros — Automatización Procesos IA',
  description:
    'Conoce al equipo de Automatización Procesos IA: profesionales especializados en inteligencia artificial que ayudan a empresas a implementar IA de forma práctica y con resultados reales.',
  keywords: [
    'equipo Automatización Procesos IA',
    'consultoría inteligencia artificial Madrid',
    'expertos IA para empresas',
    'sobre nosotros IA',
  ],
  openGraph: {
    title: 'Sobre nosotros — Automatización Procesos IA',
    description:
      'El equipo que convierte la IA en resultados reales para tu empresa. Conoce quiénes somos y por qué más de 50 empresas confían en nosotros.',
    type: 'website',
    locale: 'es_ES',
  },
  alternates: {
    canonical: 'https://www.automatizacionprocesos.es/sobre-nosotros',
  },
}

const valores = [
  {
    icon: Target,
    titulo: 'Pragmatismo',
    descripcion:
      'No vendemos tecnología por moda. Cada solución que proponemos tiene un caso de uso claro, un ROI medible y un plazo de implementación realista.',
  },
  {
    icon: Eye,
    titulo: 'Transparencia',
    descripcion:
      'Explicamos cada paso del proceso en lenguaje comprensible. Sin cajas negras, sin tecnicismos innecesarios: tú siempre sabes qué estamos haciendo y por qué.',
  },
  {
    icon: BarChart3,
    titulo: 'Resultados medibles',
    descripcion:
      'Definimos métricas de éxito antes de empezar. Horas ahorradas, costes reducidos, conversiones mejoradas: los resultados se miden, no se suponen.',
  },
  {
    icon: GraduationCap,
    titulo: 'Formación continua',
    descripcion:
      'El ecosistema de IA cambia cada semana. Invertimos en formación constante para garantizar que nuestras recomendaciones estén siempre a la vanguardia.',
  },
]

const metricas = [
  {
    numero: '+50',
    etiqueta: 'empresas acompañadas',
    descripcion: 'Pymes y medianas empresas de sectores muy diversos que ya trabajan con IA.',
  },
  {
    numero: '+200',
    etiqueta: 'automatizaciones implantadas',
    descripcion: 'Flujos de trabajo automatizados activos que generan valor día a día.',
  },
  {
    numero: '4,9/5',
    etiqueta: 'satisfacción media',
    descripcion: 'Puntuación media de nuestros clientes tras los proyectos completados.',
  },
]

const diferenciadores = [
  'Consultores con experiencia real en implantación, no solo en teoría',
  'Acompañamiento completo: de la estrategia al sistema en producción',
  'Sin dependencia de grandes plataformas: elegimos las herramientas que mejor se adaptan a ti',
  'Precios transparentes sin sorpresas ni costes ocultos',
  'Soporte post-implantación incluido en todos los proyectos',
]

export default function SobreNosotrosPage() {
  return (
    <main className="bg-surface-50 min-h-screen">
      {/* Hero */}
      <section className="bg-gradient-to-br from-navy-900 via-navy-800 to-navy-700 py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-brand-400 text-sm font-semibold uppercase tracking-widest mb-4">
            Quiénes somos
          </p>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
            El equipo que convierte{' '}
            <span className="text-brand-400">la IA en resultados reales</span>
          </h1>
          <p className="text-lg md:text-xl text-navy-300 max-w-2xl mx-auto leading-relaxed">
            Somos un equipo de especialistas en inteligencia artificial aplicada que trabaja codo a
            codo con empresas para que la IA deje de ser una promesa y se convierta en una ventaja
            competitiva tangible.
          </p>
        </div>
      </section>

      {/* Misión */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-brand-600 text-sm font-semibold uppercase tracking-widest mb-3">
                Nuestra misión
              </p>
              <h2 className="text-3xl md:text-4xl font-bold text-navy-900 mb-6 leading-tight">
                IA práctica, sin tecnicismos, con impacto real
              </h2>
            </div>
            <div className="space-y-5 text-navy-600 leading-relaxed">
              <p>
                En Automatización Procesos IA ayudamos a empresas de todos los sectores a implementar
                inteligencia artificial de forma práctica, asequible y sin fricciones. Creemos que
                la IA no debería ser patrimonio exclusivo de las grandes corporaciones.
              </p>
              <p>
                Nuestra misión es democratizar el acceso a estas tecnologías: desde la auditoría
                inicial que identifica dónde aplicar IA hasta la puesta en producción del primer
                agente o automatización, acompañamos a nuestros clientes en cada etapa del proceso.
              </p>
              <p>
                No somos una agencia de software ni una consultora generalista. Somos especialistas
                en IA aplicada a procesos de negocio reales, con el foco puesto siempre en el
                retorno de inversión.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Valores */}
      <section className="py-20 px-4 bg-surface-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-brand-600 text-sm font-semibold uppercase tracking-widest mb-3">
              Nuestros valores
            </p>
            <h2 className="text-3xl md:text-4xl font-bold text-navy-900">
              Los principios que guían cada proyecto
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {valores.map((valor) => {
              const Icon = valor.icon
              return (
                <div
                  key={valor.titulo}
                  className="bg-white rounded-2xl p-7 border border-surface-200 hover:border-brand-400 hover:shadow-lg transition-all duration-300 group"
                >
                  <div className="w-12 h-12 bg-brand-50 rounded-xl flex items-center justify-center mb-5 group-hover:bg-brand-500 transition-colors duration-300">
                    <Icon className="w-6 h-6 text-brand-600 group-hover:text-white transition-colors duration-300" />
                  </div>
                  <h3 className="text-lg font-bold text-navy-900 mb-3">{valor.titulo}</h3>
                  <p className="text-navy-600 text-sm leading-relaxed">{valor.descripcion}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Métricas */}
      <section className="py-20 px-4 bg-navy-900">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-brand-400 text-sm font-semibold uppercase tracking-widest mb-3">
              Por qué elegirnos
            </p>
            <h2 className="text-3xl md:text-4xl font-bold text-white">
              Números que hablan por nosotros
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {metricas.map((metrica) => (
              <div
                key={metrica.etiqueta}
                className="text-center bg-navy-800 rounded-2xl p-10 border border-navy-700"
              >
                <p className="text-5xl md:text-6xl font-extrabold text-brand-400 mb-2">
                  {metrica.numero}
                </p>
                <p className="text-lg font-semibold text-white mb-3">{metrica.etiqueta}</p>
                <p className="text-navy-400 text-sm leading-relaxed">{metrica.descripcion}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Diferenciadores */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-brand-600 text-sm font-semibold uppercase tracking-widest mb-3">
              Lo que nos diferencia
            </p>
            <h2 className="text-3xl md:text-4xl font-bold text-navy-900">
              Más que consultores, somos tu equipo de IA
            </h2>
          </div>
          <ul className="space-y-4">
            {diferenciadores.map((item) => (
              <li
                key={item}
                className="flex items-start gap-4 bg-surface-50 rounded-xl p-5 border border-surface-200"
              >
                <CheckCircle2 className="w-5 h-5 text-success-500 mt-0.5 flex-shrink-0" />
                <span className="text-navy-700 font-medium">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-gradient-to-br from-brand-600 to-brand-500">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            ¿Quieres conocernos mejor?
          </h2>
          <p className="text-brand-50 text-lg mb-10 leading-relaxed">
            Cuéntanos tu proyecto y en menos de 24 horas te respondemos con una propuesta inicial
            sin compromiso. O empieza con nuestro diagnóstico gratuito.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/contacto"
              className="inline-flex items-center justify-center gap-2 bg-white text-brand-600 font-bold px-8 py-4 rounded-xl hover:bg-brand-50 transition-colors duration-200 text-lg"
            >
              Contactar con el equipo
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/diagnostico-gratuito"
              className="inline-flex items-center justify-center gap-2 bg-transparent border-2 border-white text-white font-bold px-8 py-4 rounded-xl hover:bg-white/10 transition-colors duration-200 text-lg"
            >
              Diagnóstico gratuito
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}
