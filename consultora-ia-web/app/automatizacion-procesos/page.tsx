import type { Metadata } from 'next'
import Link from 'next/link'
import {
  Mail,
  FileText,
  BarChart3,
  Table2,
  Database,
  FolderOpen,
  Bell,
  PieChart,
  Package,
  Users,
  CheckCircle,
  ArrowRight,
  Zap,
  Clock,
  Wrench,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Automatización de Procesos con IA para Empresas | Automatización Procesos IA',
  description:
    'Automatizamos los procesos administrativos y operativos de tu empresa con inteligencia artificial: facturas, emails, informes, CRM, ERP y más. Ahorra horas cada semana.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/automatizacion-procesos' },
  openGraph: {
    title: 'Automatización de Procesos con IA para Empresas | Automatización Procesos IA',
    description:
      'Automatizamos los procesos que más tiempo consumen a tu equipo. Resultados medibles desde las primeras semanas.',
    url: 'https://www.automatizacionprocesos.es/automatizacion-procesos',
  },
}

const whatWeAutomate = [
  {
    icon: Mail,
    title: 'Correos electrónicos',
    description:
      'Respuestas automáticas a consultas frecuentes, seguimiento de presupuestos enviados, notificaciones de pedidos y clasificación inteligente de la bandeja de entrada.',
  },
  {
    icon: FileText,
    title: 'Facturas y albaranes',
    description:
      'Extracción automática de datos de facturas de proveedores, generación de facturas de venta a partir de pedidos y conciliación con el sistema de contabilidad.',
  },
  {
    icon: BarChart3,
    title: 'Informes y reportes',
    description:
      'Informes semanales y mensuales generados automáticamente desde tus fuentes de datos: ventas, operaciones, finanzas. Listos en tu bandeja de entrada sin intervención.',
  },
  {
    icon: Table2,
    title: 'Hojas de cálculo (Excel)',
    description:
      'Actualización automática de hojas de cálculo, consolidación de datos de múltiples fuentes y generación de resúmenes ejecutivos con un solo clic.',
  },
  {
    icon: Users,
    title: 'CRM',
    description:
      'Actualización del CRM tras reuniones y llamadas, clasificación automática de leads, envío de secuencias de seguimiento y alertas cuando un cliente lleva tiempo sin actividad.',
  },
  {
    icon: Package,
    title: 'ERP',
    description:
      'Sincronización de pedidos, actualizaciones de stock, alertas de mínimos y volcado automático de datos entre el ERP y otras herramientas de la empresa.',
  },
  {
    icon: Database,
    title: 'Bases de datos',
    description:
      'Consultas automáticas, actualizaciones programadas, detección de anomalías y generación de informes a partir de tus bases de datos internas.',
  },
  {
    icon: FolderOpen,
    title: 'Gestión documental',
    description:
      'Clasificación, nomenclatura y archivo automático de documentos según su contenido. Contratos, facturas, actas y cualquier tipo de documento empresarial.',
  },
  {
    icon: Bell,
    title: 'Alertas y notificaciones',
    description:
      'Alertas automáticas cuando un KPI se desvía del objetivo, una factura vence, un contrato se acerca a renovación o un pedido supera el plazo previsto.',
  },
  {
    icon: PieChart,
    title: 'Reportes para dirección',
    description:
      'Cuadros de mando actualizados en tiempo real y reportes ejecutivos generados automáticamente para que la dirección tenga siempre los datos clave a mano.',
  },
]

const tools = [
  { name: 'n8n', description: 'Automatización de flujos open-source, ideal para integraciones complejas' },
  { name: 'Make', description: 'Plataforma visual para automatizaciones sin código de alta flexibilidad' },
  { name: 'Zapier', description: 'Conector entre aplicaciones, perfecto para flujos sencillos y rápidos' },
  { name: 'Power Automate', description: 'Automatización nativa para entornos Microsoft 365' },
  { name: 'OpenAI API', description: 'Procesamiento inteligente de texto, documentos y datos no estructurados' },
  { name: 'Claude API', description: 'Análisis en profundidad, extracción precisa y razonamiento complejo' },
]

const phases = [
  {
    number: '01',
    title: 'Análisis',
    duration: '1 semana',
    description:
      'Entrevistamos al equipo, mapeamos los procesos actuales e identificamos exactamente dónde se pierde tiempo. Cuantificamos el coste real de cada proceso antes de tocar nada.',
    deliverable: 'Mapa de procesos y lista de automatizaciones priorizadas',
  },
  {
    number: '02',
    title: 'Diseño',
    duration: '1 semana',
    description:
      'Diseñamos el flujo de la automatización, definimos las reglas de negocio, los criterios de excepción y cómo se integra con tus sistemas actuales. Todo documentado y validado contigo antes de implementar.',
    deliverable: 'Diagrama de flujo aprobado y plan técnico',
  },
  {
    number: '03',
    title: 'Implementación',
    duration: '2-4 semanas',
    description:
      'Construimos la automatización, la probamos con datos reales y ajustamos el comportamiento hasta que funciona exactamente como debe. Incluye pruebas de errores y casos límite.',
    deliverable: 'Automatización en producción y documentación técnica',
  },
  {
    number: '04',
    title: 'Seguimiento',
    duration: 'Continuo',
    description:
      'Tras el lanzamiento, monitorizamos el funcionamiento, formamos al equipo para que pueda gestionar y supervisar la automatización, y realizamos ajustes según los resultados reales.',
    deliverable: 'Informe de rendimiento y equipo formado',
  },
]

const roiExamples = [
  {
    process: 'Procesamiento de facturas de proveedores',
    before: '3 horas/día',
    after: '20 minutos/día',
    saving: '~7.000 €/año',
    payback: '6 meses',
  },
  {
    process: 'Generación de informes de ventas semanales',
    before: '4 horas/semana',
    after: '0 horas (automático)',
    saving: '~5.500 €/año',
    payback: '4 meses',
  },
  {
    process: 'Seguimiento de presupuestos enviados',
    before: '6 horas/semana',
    after: '30 min/semana (revisión)',
    saving: '~8.000 €/año',
    payback: '5 meses',
  },
  {
    process: 'Actualización del CRM post-reunión',
    before: '90 min/día',
    after: '10 min/día',
    saving: '~6.500 €/año',
    payback: '7 meses',
  },
]

export default function AutomatizacionProcesosPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Service',
            name: 'Automatización de Procesos con IA',
            description:
              'Automatización de procesos empresariales con inteligencia artificial.',
            provider: { '@type': 'Organization', name: 'Automatización Procesos IA', url: 'https://www.automatizacionprocesos.es' },
            url: 'https://www.automatizacionprocesos.es/automatizacion-procesos',
            offers: {
              '@type': 'Offer',
              price: '2500',
              priceCurrency: 'EUR',
              description: 'Proyecto desde 2.500 €',
            },
          }),
        }}
      />

      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
              Automatización de procesos
            </span>
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
              Automatización de procesos con{' '}
              <span className="text-blue-400">inteligencia artificial</span>
            </h1>
            <p className="text-lg text-slate-300 mb-8 leading-relaxed">
              Identificamos los procesos que más tiempo consumen a tu equipo y los automatizamos
              con IA. Facturas, emails, informes, CRM, ERP y gestión documental. Resultados
              medibles en semanas, no en meses.
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
          <div className="mt-14 grid grid-cols-2 sm:grid-cols-4 gap-6">
            {[
              { value: '80%', label: 'Reducción de tiempo en procesos automatizados' },
              { value: '4-8', label: 'Meses para recuperar la inversión' },
              { value: '0', label: 'Errores de introducción manual de datos' },
              { value: '24/7', label: 'Procesos funcionando sin supervisión' },
            ].map((stat) => (
              <div key={stat.label} className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-blue-400 mb-1">{stat.value}</div>
                <div className="text-xs text-slate-400 leading-tight">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What we automate */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Qué automatizamos</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Cubrimos los procesos administrativos, operativos y de comunicación que más tiempo
              consumen en cualquier empresa española.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {whatWeAutomate.map((item) => {
              const Icon = item.icon
              return (
                <div
                  key={item.title}
                  className="border border-slate-200 rounded-xl p-6 hover:border-blue-300 hover:shadow-md transition-all"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <Icon className="h-5 w-5 text-blue-600" />
                    </div>
                    <h3 className="font-semibold text-slate-900">{item.title}</h3>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">{item.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Process phases */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Nuestro proceso de trabajo</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Un método probado en decenas de proyectos. Sin sorpresas, con entregables claros en
              cada fase.
            </p>
          </div>
          <div className="space-y-6">
            {phases.map((phase) => (
              <div
                key={phase.number}
                className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 flex flex-col sm:flex-row gap-6"
              >
                <div className="flex-shrink-0">
                  <div className="w-14 h-14 bg-blue-600 rounded-xl flex items-center justify-center">
                    <span className="text-white font-bold text-lg">{phase.number}</span>
                  </div>
                </div>
                <div className="flex-grow">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-3">
                    <h3 className="text-xl font-bold text-slate-900">{phase.title}</h3>
                    <span className="inline-flex items-center gap-1 text-sm text-blue-600 bg-blue-50 px-3 py-1 rounded-full font-medium w-fit">
                      <Clock className="h-3.5 w-3.5" />
                      {phase.duration}
                    </span>
                  </div>
                  <p className="text-slate-600 mb-3 leading-relaxed">{phase.description}</p>
                  <div className="inline-flex items-center gap-2 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2">
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{phase.deliverable}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ROI */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">ROI típico en proyectos reales</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Ejemplos reales de ahorro. Los datos se calculan de forma conservadora antes de
              cada implementación.
            </p>
          </div>
          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Proceso</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Antes</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Después</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-green-700">Ahorro anual</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Retorno</th>
                </tr>
              </thead>
              <tbody>
                {roiExamples.map((row, idx) => (
                  <tr key={row.process} className={`border-t border-slate-100 ${idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}`}>
                    <td className="py-4 px-4 text-sm font-medium text-slate-900">{row.process}</td>
                    <td className="py-4 px-4 text-sm text-slate-500">{row.before}</td>
                    <td className="py-4 px-4 text-sm text-slate-600">{row.after}</td>
                    <td className="py-4 px-4 text-sm font-semibold text-green-700">{row.saving}</td>
                    <td className="py-4 px-4 text-sm text-blue-600 font-medium">{row.payback}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-slate-400 mt-3 text-center">
            * Ahorros calculados sobre un coste empresa de 28.000 €/año. Los resultados reales pueden variar.
          </p>
        </div>
      </section>

      {/* Tools */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Herramientas que utilizamos</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Seleccionamos la herramienta más adecuada para cada proyecto. Sin atarte a ninguna
              plataforma concreta.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {tools.map((tool) => (
              <div
                key={tool.name}
                className="bg-white border border-slate-200 rounded-xl p-5 flex items-start gap-4"
              >
                <div className="p-2 bg-slate-100 rounded-lg flex-shrink-0">
                  <Wrench className="h-4 w-4 text-slate-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1">{tool.name}</h3>
                  <p className="text-sm text-slate-600">{tool.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-blue-600">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 text-center">
          <Zap className="h-10 w-10 text-blue-200 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-white mb-4">
            ¿Cuánto tiempo pierde tu equipo en tareas repetitivas?
          </h2>
          <p className="text-blue-100 mb-8 text-lg">
            En 45 minutos de diagnóstico gratuito identificamos exactamente qué puedes automatizar,
            cuánto ahorrarías y cuánto costaría la implementación. Sin compromiso.
          </p>
          <Link
            href="/diagnostico-gratuito"
            className="inline-flex items-center gap-2 bg-white hover:bg-blue-50 text-blue-700 font-bold px-8 py-4 rounded-xl transition-colors text-lg"
          >
            Solicitar diagnóstico gratuito
            <ArrowRight className="h-5 w-5" />
          </Link>
          <p className="text-blue-200 text-sm mt-4">
            Videollamada de 45 minutos · Sin coste · Sin compromiso
          </p>
        </div>
      </section>
    </>
  )
}
