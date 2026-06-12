'use client'

import Link from 'next/link'
import { useState } from 'react'
import {
  ArrowRight,
  CheckCircle,
  Tag,
  TrendingUp,
  Clock,
} from 'lucide-react'

const cases = [
  {
    id: 1,
    sector: 'Asesoría jurídica',
    category: 'Agentes IA',
    challenge:
      'El equipo dedicaba entre 3 y 5 horas por contrato revisando cláusulas problemáticas, fechas de vencimiento y condiciones no estándar. Con un volumen creciente de contratos, el cuello de botella era insostenible.',
    solution:
      'Agente IA basado en Claude que analiza contratos en PDF, extrae las cláusulas clave, identifica cláusulas atípicas o de riesgo, genera un resumen ejecutivo por contrato y crea alertas automáticas para vencimientos.',
    technologies: ['Claude API', 'n8n', 'Google Drive API'],
    result: '70% menos tiempo de revisión por contrato. Un análisis que tardaba 4 horas se completa en 30 minutos.',
    resultValue: '70% menos tiempo',
    highlight: true,
  },
  {
    id: 2,
    sector: 'Empresa logística',
    category: 'Agentes IA',
    challenge:
      'El servicio de atención al cliente recibía más de 200 consultas diarias, el 75% relacionadas con estado de envíos, incidencias de entrega y solicitudes de cambio de dirección. El equipo no daba abasto.',
    solution:
      'Agente de atención al cliente integrado en web y WhatsApp Business que conecta con el sistema de gestión logística, consulta el estado del envío en tiempo real, gestiona cambios de dirección y escala a humano solo las incidencias complejas.',
    technologies: ['OpenAI API', 'WhatsApp Business API', 'n8n', 'REST API logística'],
    result: '80% de las consultas resueltas sin intervención humana. El equipo de atención redujo el volumen de gestiones manuales en 160 consultas diarias.',
    resultValue: '80% resolución automática',
    highlight: false,
  },
  {
    id: 3,
    sector: 'Clínica dental',
    category: 'Automatización',
    challenge:
      'Las ausencias a citas sin previo aviso representaban el 18% del total de citas mensuales, con el coste operativo que supone para la clínica. Los recordatorios se hacían manualmente por teléfono, consumiendo 2 horas diarias del personal administrativo.',
    solution:
      'Sistema de recordatorios automáticos multicanal: SMS y WhatsApp 48h y 24h antes de cada cita, con opción de confirmar, cancelar o reprogramar desde el propio mensaje. Integración directa con el sistema de gestión de la clínica.',
    technologies: ['Make', 'WhatsApp Business API', 'Twilio SMS', 'API clínica'],
    result: 'Tasa de ausencias reducida del 18% al 2%. El personal administrativo recuperó 2 horas diarias.',
    resultValue: '0 ausencias sin aviso',
    highlight: false,
  },
  {
    id: 4,
    sector: 'Constructora mediana',
    category: 'Reporting',
    challenge:
      'Cada directivo dedicaba entre 4 y 6 horas semanales a recopilar datos de las obras, actualizar hojas de cálculo y preparar el informe de situación para la reunión de dirección del lunes. Datos de múltiples fuentes, siempre desactualizados.',
    solution:
      'Sistema de reporting automático que recoge datos de presupuesto, avance real, costes y desvíos de cada obra, los consolida y genera cada viernes a las 17:00 un informe ejecutivo personalizado por rol, enviado directamente a cada directivo.',
    technologies: ['Power Automate', 'Power BI', 'SharePoint', 'Microsoft 365'],
    result: 'Ahorro de 5 horas semanales por directivo. Los informes de los lunes se generan solos y llegan más completos y actualizados que los preparados manualmente.',
    resultValue: '5h/semana ahorradas por directivo',
    highlight: false,
  },
  {
    id: 5,
    sector: 'Ecommerce',
    category: 'Agentes IA',
    challenge:
      'Los leads que llegaban por web fuera del horario comercial (tarde y fines de semana) no recibían respuesta hasta el día siguiente. El 40% no contestaba cuando el equipo comercial los llamaba al día siguiente.',
    solution:
      'Agente comercial 24/7 integrado en el chat de la web que cualifica leads en tiempo real, responde preguntas sobre productos, catálogos y precios, detecta intención de compra y agenda automáticamente una llamada con el comercial adecuado para el día siguiente.',
    technologies: ['OpenAI API', 'Typebot', 'HubSpot API', 'Calendly API'],
    result: 'Conversión de leads a reunión aumentada un 35%. El equipo comercial solo dedica tiempo a prospectos que ya han mostrado interés real.',
    resultValue: '+35% conversión de leads',
    highlight: true,
  },
  {
    id: 6,
    sector: 'Gestoría',
    category: 'Automatización',
    challenge:
      'El equipo procesaba manualmente más de 500 facturas y albaranes al mes. Cada documento requería abrir el PDF, identificar los campos, introducirlos en el sistema de contabilidad y archivar el original. Tasa de error del 8% por fatiga.',
    solution:
      'Flujo automático de procesamiento documental: las facturas llegan por email a una dirección específica, la IA extrae todos los campos contables, los valida contra el registro de proveedores, los registra en el sistema y archiva el original con nomenclatura estandarizada.',
    technologies: ['Claude API', 'n8n', 'Holded API', 'Google Drive'],
    result: 'Tasa de error reducida del 8% al 0,3%. El equipo pasó de 3 horas diarias de introducción de datos a 20 minutos de supervisión.',
    resultValue: '60% reducción de errores',
    highlight: false,
  },
  {
    id: 7,
    sector: 'Inmobiliaria',
    category: 'Agentes IA',
    challenge:
      'El equipo comercial recibía entre 40 y 60 contactos nuevos a la semana, pero más del 70% eran personas que estaban en fases muy tempranas de búsqueda, sin presupuesto definido ni urgencia real. Los comerciales perdían horas en llamadas no productivas.',
    solution:
      'Agente de cualificación automática que recoge los datos del prospecto, le hace una serie de preguntas sobre presupuesto, urgencia, tipología de inmueble y zona, puntúa el lead y solo traslada al equipo comercial los que superan el umbral de cualificación.',
    technologies: ['OpenAI API', 'n8n', 'Pipedrive API', 'Typeform'],
    result: 'El equipo comercial solo habla con leads cualificados. Tiempo invertido en prospectos no cualificados reducido en un 70%.',
    resultValue: 'Solo leads cualificados',
    highlight: false,
  },
  {
    id: 8,
    sector: 'Empresa manufacturera',
    category: 'Reporting',
    challenge:
      'Los directivos de planta y producción no tenían visibilidad de los datos de producción en tiempo real. Los informes se preparaban manualmente cada semana y llegaban desactualizados al momento de revisarlos.',
    solution:
      'Sistema de reporting de producción conectado con el ERP y los sistemas SCADA de planta. Dashboard en tiempo real accesible desde cualquier dispositivo y envío automático de alertas cuando algún indicador de producción se desvía del objetivo.',
    technologies: ['Power BI', 'Power Automate', 'SAP API', 'Azure IoT'],
    result: 'Directivos con datos de producción en tiempo real. Las alertas automáticas permiten reaccionar en minutos ante desviaciones que antes se detectaban con días de retraso.',
    resultValue: 'Datos en tiempo real',
    highlight: false,
  },
]

const categories = ['Todos', ...Array.from(new Set(cases.map((c) => c.category)))]

export default function CasosUsoPage() {
  const [activeCategory, setActiveCategory] = useState('Todos')

  const filtered = activeCategory === 'Todos'
    ? cases
    : cases.filter((c) => c.category === activeCategory)

  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Casos de uso reales
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Casos de uso de inteligencia artificial{' '}
            <span className="text-blue-400">en empresas</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-8">
            Proyectos reales con retos reales y resultados medibles. Cómo empresas de diferentes
            sectores están usando la IA para ahorrar tiempo, reducir errores y mejorar su
            operativa.
          </p>
        </div>
      </section>

      {/* Filters + Cases */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          {/* Filters */}
          <div className="flex flex-wrap gap-2 mb-10 justify-center">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  activeCategory === cat
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-slate-200 text-slate-600 hover:border-blue-400 hover:text-blue-600'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Cases grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {filtered.map((caso) => (
              <div
                key={caso.id}
                className={`bg-white rounded-2xl border p-6 flex flex-col ${
                  caso.highlight
                    ? 'border-blue-400 ring-2 ring-blue-400/20'
                    : 'border-slate-200 hover:border-slate-300 hover:shadow-md'
                } transition-all`}
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-semibold text-slate-900">{caso.sector}</span>
                  <span className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-full flex items-center gap-1">
                    <Tag className="h-3 w-3" />
                    {caso.category}
                  </span>
                </div>

                <div className="mb-4">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">
                    Reto inicial
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">{caso.challenge}</p>
                </div>

                <div className="mb-4">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">
                    Solución implementada
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">{caso.solution}</p>
                </div>

                <div className="mb-4">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                    Tecnologías
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {caso.technologies.map((tech) => (
                      <span
                        key={tech}
                        className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-auto pt-4 border-t border-slate-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-green-50 rounded-lg">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    </div>
                    <div>
                      <div className="text-xs text-slate-400">Resultado</div>
                      <div className="text-sm font-semibold text-green-700">{caso.resultValue}</div>
                    </div>
                  </div>
                  <p className="text-xs text-slate-500 mt-2 leading-relaxed">{caso.result}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-blue-600">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            ¿Ves algo parecido a lo que necesitas?
          </h2>
          <p className="text-blue-100 mb-8 text-lg">
            En 30 minutos analizamos tu empresa y te decimos exactamente qué solución tendría más
            impacto en tu caso concreto. Sin compromiso.
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
