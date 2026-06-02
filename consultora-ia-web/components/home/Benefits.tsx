'use client'

import { motion } from 'framer-motion'
import { Timer, ShieldCheck, MessageSquare, TrendingUp } from 'lucide-react'

interface Benefit {
  icon: React.ElementType
  metric: string
  unit: string
  title: string
  description: string
}

const benefits: Benefit[] = [
  {
    icon: Timer,
    metric: '60',
    unit: '%',
    title: 'Ahorro en tareas repetitivas',
    description:
      'De media, las empresas que implementan automatización con IA reducen a la mitad el tiempo dedicado a tareas manuales y repetitivas.',
  },
  {
    icon: ShieldCheck,
    metric: '80',
    unit: '%',
    title: 'Reducción de errores administrativos',
    description:
      'Los procesos automatizados eliminan casi por completo los errores humanos en introducción de datos, facturación y comunicaciones.',
  },
  {
    icon: MessageSquare,
    metric: '5×',
    unit: '',
    title: 'Mejora en tiempo de respuesta',
    description:
      'Los agentes IA responden de forma inmediata, las 24 horas del día, sin colas de espera ni retrasos por horario de oficina.',
  },
  {
    icon: TrendingUp,
    metric: '3×',
    unit: '',
    title: 'ROI en automatizaciones',
    description:
      'La inversión en automatización se recupera habitualmente en menos de 6 meses. Después, el ahorro es beneficio directo y sostenido.',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12 } },
}

const cardVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: 'easeOut' } },
}

export default function Benefits() {
  return (
    <section
      aria-labelledby="benefits-heading"
      className="bg-white py-20 md:py-28"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="benefits-heading"
            className="text-3xl font-extrabold tracking-tight text-[#0F172A] sm:text-4xl"
          >
            Beneficios medibles para tu empresa
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            No hablamos de posibilidades abstractas. Estos son los resultados que
            consiguen las empresas que trabajan con nosotros.
          </p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4"
        >
          {benefits.map((benefit) => {
            const Icon = benefit.icon
            return (
              <motion.div
                key={benefit.title}
                variants={cardVariants}
                className="relative overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 p-6"
              >
                <div
                  aria-hidden="true"
                  className="absolute -right-4 -top-4 h-20 w-20 rounded-full bg-blue-50"
                />
                <div className="relative">
                  <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-blue-100 text-[#2563EB]">
                    <Icon className="h-5 w-5" aria-hidden="true" />
                  </div>
                  <div className="mb-3 flex items-end gap-1">
                    <span className="text-5xl font-extrabold leading-none text-[#0F172A]">
                      {benefit.metric}
                    </span>
                    {benefit.unit && (
                      <span className="mb-1 text-2xl font-bold text-[#2563EB]">
                        {benefit.unit}
                      </span>
                    )}
                  </div>
                  <h3 className="mb-2 text-sm font-semibold text-[#0F172A]">
                    {benefit.title}
                  </h3>
                  <p className="text-xs leading-relaxed text-slate-500">
                    {benefit.description}
                  </p>
                </div>
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
