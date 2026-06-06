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
    metric: '20',
    unit: 'h',
    title: 'Horas ahorradas por empleado cada semana',
    description:
      'De media, los equipos que automatizan con IA recuperan hasta 20 horas semanales por persona. Tiempo que se puede reinvertir en tareas de mayor valor: ventas, atención al cliente o innovación.',
  },
  {
    icon: TrendingUp,
    metric: '340',
    unit: '%',
    title: 'ROI medio en el primer año',
    description:
      'La inversión en automatización de procesos con IA se recupera en 3 a 6 meses. A partir de ahí, el ahorro es beneficio directo y sostenido mes a mes sin coste adicional.',
  },
  {
    icon: ShieldCheck,
    metric: '4-6',
    unit: '',
    title: 'Semanas hasta ver resultados reales',
    description:
      'No hacemos promesas a largo plazo. En 2 semanas tienes un piloto funcionando y en 4-6 semanas el proceso automatizado está en producción con tu equipo formado y operativo.',
  },
  {
    icon: MessageSquare,
    metric: '0',
    unit: '',
    title: 'Conocimientos técnicos necesarios',
    description:
      'Nos encargamos de toda la parte técnica: instalación, integración con tus sistemas, formación y mantenimiento. Tu equipo solo necesita saber usar las herramientas, no programarlas.',
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
