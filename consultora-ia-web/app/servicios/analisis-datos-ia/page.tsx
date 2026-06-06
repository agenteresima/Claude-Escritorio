import type { Metadata } from 'next'
import Link from 'next/link'
import { BarChart3, Database, TrendingUp, Zap, Eye, PieChart, ArrowRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Análisis de Datos con IA | Dashboards e Insights | AP Automatización IA',
  description:
    'Análisis de datos empresariales con inteligencia artificial. Dashboards interactivos, detección de patrones, predicciones y insights accionables para tomar mejores decisiones.',
  alternates: { canonical: 'https://automatizacionprocesos.es/servicios/analisis-datos-ia' },
  openGraph: {
    title: 'Análisis de Datos con IA | AP Automatización IA',
    description:
      'Convertimos tus datos en decisiones. Dashboards inteligentes, análisis predictivo e insights automáticos con inteligencia artificial.',
    url: 'https://automatizacionprocesos.es/servicios/analisis-datos-ia',
  },
}

const includes = [
  {
    icon: BarChart3,
    title: 'Dashboards interactivos en tiempo real',
    description:
      'Diseñamos paneles de control personalizados con los KPIs que realmente importan a tu negocio. Actualizados automáticamente, accesibles desde cualquier dispositivo.',
  },
  {
    icon: Database,
    title: 'Integración de fuentes de datos',
    description:
      'Conectamos tu CRM, ERP, hojas de cálculo, bases de datos y plataformas digitales en un único modelo de datos coherente y actualizado.',
  },
  {
    icon: TrendingUp,
    title: 'Análisis predictivo con IA',
    description:
      'Utilizamos modelos de machine learning para predecir ventas, demanda, churn de clientes, riesgo de crédito u otras métricas clave para tu negocio.',
  },
  {
    icon: Zap,
    title: 'Alertas automáticas sobre anomalías',
    description:
      'El sistema detecta automáticamente desviaciones, tendencias inesperadas o métricas fuera de rango y alerta al equipo antes de que el problema escale.',
  },
  {
    icon: Eye,
    title: 'Insights en lenguaje natural',
    description:
      'Con IA generativa, el sistema interpreta los datos y genera resúmenes en lenguaje natural. Cualquier persona del equipo entiende qué está pasando sin saber de estadística.',
  },
  {
    icon: PieChart,
    title: 'Informes automáticos y periódicos',
    description:
      'Generación automática de informes semanales, mensuales o a demanda. Tu equipo directivo recibe los datos relevantes sin tener que pedirlos.',
  },
]

const benefits = [
  {
    title: 'Decisiones basadas en datos, no en intuición',
    description:
      'Las empresas que toman decisiones con datos obtienen un 23% más de rentabilidad que la media de su sector. La IA hace que ese proceso sea rápido, accesible y continuo.',
    stat: '+23%',
    label: 'rentabilidad frente a competidores',
  },
  {
    title: 'Del dato a la acción en minutos, no en días',
    description:
      'Antes de tener un dashboard inteligente, preparar un informe podía llevar días. Con análisis automatizado, los datos están disponibles en tiempo real y el equipo actúa al instante.',
    stat: '10x',
    label: 'más rápido del dato a la decisión',
  },
  {
    title: 'Detección temprana de problemas y oportunidades',
    description:
      'Los patrones ocultos en los datos revelan problemas antes de que se conviertan en crisis y oportunidades antes de que la competencia las vea. La IA no descansa ni se distrae.',
    stat: '3x',
    label: 'más rápida la detección de anomalías',
  },
]

export default function AnalisisDatosIAPage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Análisis de datos con IA
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Convierte tus datos en decisiones{' '}
            <span className="text-blue-400">que impulsan el negocio</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-10">
            Integramos todas tus fuentes de datos, construimos dashboards inteligentes y aplicamos
            inteligencia artificial para detectar patrones, predecir tendencias y generar insights
            accionables que tu equipo directivo puede usar de inmediato.
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
              No solo visualizamos datos: los interpretamos, los conectamos y los convertimos en
              ventaja competitiva para tu empresa.
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
              El impacto real que tiene el análisis de datos con IA en empresas como la tuya.
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
            ¿Quieres ver qué esconden los datos de tu empresa?
          </h2>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto mb-8">
            En 45 minutos analizamos qué datos tienes disponibles y te mostramos qué tipo de
            insights y predicciones podríamos generar para mejorar tus decisiones de negocio.
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
