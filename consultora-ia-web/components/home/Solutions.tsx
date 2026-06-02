'use client'

import { motion } from 'framer-motion'
import {
  Search,
  Map,
  Zap,
  Bot,
  GraduationCap,
  UserCheck,
} from 'lucide-react'

interface Solution {
  icon: React.ElementType
  title: string
  description: string
}

const solutions: Solution[] = [
  {
    icon: Search,
    title: 'Auditoría IA',
    description:
      'Analizamos en detalle tus procesos actuales y detectamos exactamente dónde y cómo aplicar la inteligencia artificial para generar impacto real.',
  },
  {
    icon: Map,
    title: 'Estrategia IA',
    description:
      'Diseñamos una hoja de ruta realista, priorizada y adaptada a tu empresa: qué implementar primero, con qué herramientas y con qué inversión.',
  },
  {
    icon: Zap,
    title: 'Automatización de procesos',
    description:
      'Convertimos tareas repetitivas en flujos automáticos que funcionan solos: facturación, informes, comunicaciones, integraciones entre sistemas.',
  },
  {
    icon: Bot,
    title: 'Agentes IA',
    description:
      'Creamos agentes inteligentes conectados a tus sistemas que gestionan consultas, procesan información y actúan de forma autónoma las 24 horas.',
  },
  {
    icon: GraduationCap,
    title: 'Formación IA',
    description:
      'Formamos a tu equipo para que sepa usar la IA en su día a día: herramientas prácticas, casos reales y sin tecnicismos innecesarios.',
  },
  {
    icon: UserCheck,
    title: 'Acompañamiento mensual',
    description:
      'Te acompañamos como consultor IA externo mes a mes: supervisamos, ajustamos, resolvemos dudas y buscamos nuevas oportunidades de mejora.',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
}

export default function Solutions() {
  return (
    <section
      aria-labelledby="solutions-heading"
      className="bg-white py-20 md:py-28"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="solutions-heading"
            className="text-3xl font-extrabold tracking-tight text-[#0F172A] sm:text-4xl"
          >
            Lo que hacemos por tu empresa
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Cubrimos todo el ciclo de adopción de la IA: desde el diagnóstico inicial hasta
            la implementación y el acompañamiento continuo.
          </p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.15 }}
          className="mt-14 grid gap-8 sm:grid-cols-2 lg:grid-cols-3"
        >
          {solutions.map((solution, index) => {
            const Icon = solution.icon
            return (
              <motion.div
                key={solution.title}
                variants={itemVariants}
                className="group flex flex-col gap-4"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0F172A] text-blue-400 transition-colors group-hover:bg-[#2563EB] group-hover:text-white">
                  <Icon className="h-7 w-7" aria-hidden="true" />
                </div>
                <div>
                  <h3 className="mb-1 text-lg font-semibold text-[#0F172A]">
                    {solution.title}
                  </h3>
                  <p className="text-sm leading-relaxed text-slate-500">
                    {solution.description}
                  </p>
                </div>
                <div className="mt-auto h-0.5 w-12 rounded-full bg-blue-100 transition-all group-hover:w-full group-hover:bg-blue-200" />
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
