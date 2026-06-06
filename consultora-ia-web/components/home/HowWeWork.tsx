'use client'

import { motion } from 'framer-motion'
import { CalendarCheck, ClipboardList, Route, Rocket } from 'lucide-react'

interface Step {
  number: string
  icon: React.ElementType
  title: string
  description: string
}

const steps: Step[] = [
  {
    number: '01',
    icon: CalendarCheck,
    title: 'Diagnóstico gratuito (45 min)',
    description:
      'Empezamos con una videollamada gratuita de 45 minutos en la que conocemos tu empresa, tus procesos y tus objetivos. Analizamos dónde se pierde más tiempo y dónde la inteligencia artificial puede generar impacto real. Sin venta agresiva, sin compromiso.',
  },
  {
    number: '02',
    icon: ClipboardList,
    title: 'Propuesta con ROI estimado',
    description:
      'Entregamos una propuesta personalizada con la hoja de ruta de transformación digital: qué automatizar primero, qué herramientas usar (n8n, Make, ChatGPT, agentes IA), plazos concretos y una estimación realista del ahorro y el retorno esperado en los primeros 12 meses.',
  },
  {
    number: '03',
    icon: Route,
    title: 'Implementación ágil (4-6 semanas)',
    description:
      'Ejecutamos el plan con metodología ágil: piloto funcional en 2 semanas, despliegue completo en 4 a 6 semanas. Tu equipo forma parte del proceso desde el principio para que la adopción sea natural y sin fricciones. Medimos resultados desde el primer día.',
  },
  {
    number: '04',
    icon: Rocket,
    title: 'Soporte continuo y optimización',
    description:
      'Formamos a tu equipo para que domine las herramientas implantadas y seguimos contigo como consultor IA externo: supervisamos el rendimiento, detectamos nuevas oportunidades de automatización y optimizamos los sistemas mes a mes para que el ROI siga creciendo.',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.15 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: 'easeOut' } },
}

export default function HowWeWork() {
  return (
    <section
      aria-labelledby="howwework-heading"
      className="bg-white py-20 md:py-28"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="howwework-heading"
            className="text-3xl font-extrabold tracking-tight text-[#0F172A] sm:text-4xl"
          >
            Cómo trabajamos
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Un proceso claro, sin sorpresas y orientado a resultados desde el primer día.
          </p>
        </div>

        <motion.ol
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.15 }}
          className="mt-14 grid gap-8 md:grid-cols-2 lg:grid-cols-4"
        >
          {steps.map((step, index) => {
            const Icon = step.icon
            return (
              <motion.li
                key={step.number}
                variants={itemVariants}
                className="relative flex flex-col"
              >
                {/* Connector line (hidden on last item) */}
                {index < steps.length - 1 && (
                  <div
                    aria-hidden="true"
                    className="absolute left-[calc(50%+2.5rem)] top-6 hidden h-0.5 w-[calc(100%-5rem)] bg-slate-200 lg:block"
                  />
                )}

                <div className="flex flex-col items-start gap-4 lg:items-center lg:text-center">
                  <div className="relative">
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0F172A] text-blue-400">
                      <Icon className="h-7 w-7" aria-hidden="true" />
                    </div>
                    <span className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-[#2563EB] text-xs font-bold text-white">
                      {step.number}
                    </span>
                  </div>
                  <div>
                    <h3 className="mb-2 text-base font-semibold text-[#0F172A]">
                      {step.title}
                    </h3>
                    <p className="text-sm leading-relaxed text-slate-500">
                      {step.description}
                    </p>
                  </div>
                </div>
              </motion.li>
            )
          })}
        </motion.ol>
      </div>
    </section>
  )
}
