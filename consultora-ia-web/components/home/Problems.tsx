'use client'

import { motion } from 'framer-motion'
import {
  Clock,
  HelpCircle,
  Layers,
  BarChart2,
  FileText,
  TrendingUp,
} from 'lucide-react'

interface Problem {
  icon: React.ElementType
  title: string
  description: string
}

const problems: Problem[] = [
  {
    icon: Clock,
    title: 'Tu equipo pierde horas en tareas repetitivas',
    description:
      'Copiar datos entre sistemas, generar informes manuales, responder siempre las mismas preguntas... tiempo valioso que se podría dedicar a lo que realmente importa.',
  },
  {
    icon: HelpCircle,
    title: 'Queréis usar IA pero no sabéis por dónde empezar',
    description:
      'Sabéis que la inteligencia artificial puede ayudaros, pero el mercado es confuso y no tenéis claro qué herramientas son útiles de verdad para vuestro negocio.',
  },
  {
    icon: Layers,
    title: 'Demasiadas herramientas, muy poca estrategia',
    description:
      'ChatGPT, Copilot, Make, Zapier, n8n… La lista es interminable. Sin una estrategia clara, acabáis pagando suscripciones que nadie usa.',
  },
  {
    icon: BarChart2,
    title: 'Se toman decisiones sin datos actualizados',
    description:
      'Los datos están dispersos en hojas de cálculo, correos y sistemas distintos. Tomar decisiones con información fiable se convierte en un reto diario.',
  },
  {
    icon: FileText,
    title: 'Los procesos de administración son lentos y manuales',
    description:
      'Facturación, albaranes, gestión de citas, incorporación de empleados… procesos que podrían funcionar solos siguen dependiendo de alguien que los ejecute a mano.',
  },
  {
    icon: TrendingUp,
    title: 'La competencia ya está avanzando con IA',
    description:
      'Mientras lo analizáis, hay empresas de vuestro sector que ya están automatizando, ahorrando costes y mejorando tiempos de respuesta. El momento de actuar es ahora.',
  },
]

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.1 },
  },
}

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
}

export default function Problems() {
  return (
    <section
      aria-labelledby="problems-heading"
      className="bg-slate-50 py-20 md:py-28"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="problems-heading"
            className="text-3xl font-extrabold tracking-tight text-[#0F172A] sm:text-4xl"
          >
            ¿Te suena alguna de estas situaciones?
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Son los problemas más comunes que encontramos en las empresas con las que trabajamos.
            Si reconoces alguno, podemos ayudarte.
          </p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.15 }}
          className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          {problems.map((problem) => {
            const Icon = problem.icon
            return (
              <motion.div
                key={problem.title}
                variants={cardVariants}
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-[#2563EB]">
                  <Icon className="h-6 w-6" aria-hidden="true" />
                </div>
                <h3 className="mb-2 text-base font-semibold text-[#0F172A]">
                  {problem.title}
                </h3>
                <p className="text-sm leading-relaxed text-slate-500">
                  {problem.description}
                </p>
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
