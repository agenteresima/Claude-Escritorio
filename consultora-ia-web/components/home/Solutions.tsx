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
    title: 'Auditoría IA gratuita',
    description:
      'En una sesión de 30 minutos analizamos tus procesos clave e identificamos qué se puede automatizar de forma inmediata. Recibes un informe con las 3 oportunidades de mayor ROI para tu empresa, sin coste y sin compromiso.',
  },
  {
    icon: Map,
    title: 'Estrategia IA personalizada',
    description:
      'Diseñamos una hoja de ruta realista y priorizada: qué implementar primero, con qué herramientas (n8n, Make, ChatGPT, modelos LLM propios) y con qué inversión. Incluye estimación de ahorro y retorno esperado en los primeros 12 meses.',
  },
  {
    icon: Zap,
    title: 'Automatización de procesos',
    description:
      'Conectamos tus herramientas (ERP, CRM, correo, Excel, WhatsApp) y creamos flujos automáticos con n8n, Make o Zapier. Facturación, albaranes, informes y comunicaciones funcionan solos. Media de ahorro: 8–12 horas semanales por empleado.',
  },
  {
    icon: Bot,
    title: 'Agentes IA con tus datos',
    description:
      'Desarrollamos agentes inteligentes con tecnología RAG que acceden a tu documentación interna, CRM o base de datos y responden preguntas, resuelven incidencias o ejecutan tareas de forma autónoma. Disponibles 24/7 sin intervención humana.',
  },
  {
    icon: GraduationCap,
    title: 'Formación IA para equipos',
    description:
      'Talleres presenciales y online adaptados a tu sector: cómo usar ChatGPT de forma profesional, automatización básica con IA, y casos de uso concretos de tu industria. Sin tecnicismos, con ejercicios prácticos y resultados desde el primer día.',
  },
  {
    icon: UserCheck,
    title: 'Consultor IA externo mensual',
    description:
      'Tu propio experto en inteligencia artificial para empresas disponible mes a mes, sin coste de plantilla. Supervisamos los sistemas implantados, detectamos nuevas oportunidades, formamos al equipo y garantizamos que la IA siga generando valor.',
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
