'use client'

import { motion } from 'framer-motion'
import { Building2, Truck, Stethoscope, HardHat, ShoppingCart, Calculator } from 'lucide-react'

interface UseCase {
  icon: React.ElementType
  sector: string
  problem: string
  solution: string
  result: string
  resultHighlight: string
}

const useCases: UseCase[] = [
  {
    icon: Building2,
    sector: 'Asesoría jurídica',
    problem: 'La revisión manual de contratos y documentos legales consumía horas de trabajo de los abogados.',
    solution: 'Automatización de la revisión y clasificación de documentos con IA especializada en lenguaje jurídico.',
    result: '70% menos tiempo',
    resultHighlight: 'en revisión de documentos',
  },
  {
    icon: Truck,
    sector: 'Empresa logística',
    problem: 'El servicio de atención al cliente colapsaba con consultas repetitivas sobre pedidos y entregas.',
    solution: 'Agente IA conectado al sistema de gestión de pedidos, disponible 24/7 para resolver consultas.',
    result: '80% de consultas',
    resultHighlight: 'resueltas sin intervención humana',
  },
  {
    icon: Stethoscope,
    sector: 'Clínica dental',
    problem: 'Los pacientes olvidaban sus citas con frecuencia, generando huecos en la agenda y pérdidas económicas.',
    solution: 'Sistema automático de recordatorios por WhatsApp y SMS con confirmación y opción de reprogramar.',
    result: '0 ausencias',
    resultHighlight: 'sin previo aviso desde la implementación',
  },
  {
    icon: HardHat,
    sector: 'Empresa constructora',
    problem: 'Los directivos dedicaban horas a la semana a recopilar datos de obra y preparar informes para reuniones.',
    solution: 'Sistema de generación automática de reportes a partir de los datos de gestión de obra.',
    result: '5 horas/semana',
    resultHighlight: 'ahorradas por cada directivo',
  },
  {
    icon: ShoppingCart,
    sector: 'Ecommerce',
    problem: 'Muchos visitantes llegaban a la web pero no convertían por falta de atención personalizada en tiempo real.',
    solution: 'Agente comercial IA que acompaña al usuario, resuelve dudas y guía hacia la compra las 24 horas.',
    result: '+35% conversión',
    resultHighlight: 'de leads en los primeros 60 días',
  },
  {
    icon: Calculator,
    sector: 'Gestoría contable',
    problem: 'El proceso de entrada de facturas y albaranes era manual, lento y propenso a errores humanos.',
    solution: 'Extracción automática de datos de facturas con IA y volcado directo al software de contabilidad.',
    result: '60% reducción',
    resultHighlight: 'en errores administrativos',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
}

export default function UseCases() {
  return (
    <section
      aria-labelledby="usecases-heading"
      className="bg-[#0F172A] py-20 md:py-28"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="usecases-heading"
            className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl"
          >
            Casos de uso reales
          </h2>
          <p className="mt-4 text-lg text-slate-400">
            Resultados concretos que hemos conseguido para empresas de sectores muy distintos.
          </p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          {useCases.map((uc) => {
            const Icon = uc.icon
            return (
              <motion.article
                key={uc.sector}
                variants={cardVariants}
                className="flex flex-col rounded-2xl border border-slate-700/50 bg-slate-800/50 p-6 backdrop-blur-sm"
              >
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-blue-500/20 text-blue-400">
                    <Icon className="h-5 w-5" aria-hidden="true" />
                  </div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
                    {uc.sector}
                  </span>
                </div>

                <div className="space-y-3 flex-1">
                  <div>
                    <p className="mb-1 text-xs font-medium uppercase tracking-wider text-slate-500">
                      Problema
                    </p>
                    <p className="text-sm text-slate-300">{uc.problem}</p>
                  </div>
                  <div>
                    <p className="mb-1 text-xs font-medium uppercase tracking-wider text-slate-500">
                      Solución
                    </p>
                    <p className="text-sm text-slate-300">{uc.solution}</p>
                  </div>
                </div>

                <div className="mt-5 rounded-xl bg-blue-500/10 border border-blue-500/20 p-4">
                  <p className="text-2xl font-extrabold text-blue-400">{uc.result}</p>
                  <p className="text-xs text-slate-400">{uc.resultHighlight}</p>
                </div>
              </motion.article>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
