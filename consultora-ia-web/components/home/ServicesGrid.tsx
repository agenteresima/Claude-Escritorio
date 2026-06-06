'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  Lightbulb,
  UserCheck,
  Zap,
  Bot,
  Search,
  GraduationCap,
  ArrowRight,
} from 'lucide-react'

interface Service {
  icon: React.ElementType
  title: string
  description: string
  href: string
  cta: string
}

const services: Service[] = [
  {
    icon: Lightbulb,
    title: 'Consultoría IA',
    description:
      'Diseñamos la estrategia de inteligencia artificial para tu empresa: auditoría de procesos, hoja de ruta priorizada y selección de las herramientas más adecuadas. Asesoramiento experto para que la IA genere resultados reales y medibles desde el primer proyecto.',
    href: '/servicios',
    cta: 'Saber más',
  },
  {
    icon: UserCheck,
    title: 'Consultor IA Externo',
    description:
      'Tu propio experto en IA disponible mes a mes, sin coste de plantilla ni proceso de selección. Supervisamos los sistemas implantados, formamos al equipo, detectamos nuevas oportunidades de automatización y garantizamos que la inversión en IA siga rentabilizándose.',
    href: '/consultor-ia-externo',
    cta: 'Ver el servicio',
  },
  {
    icon: Zap,
    title: 'Automatización de Procesos',
    description:
      'Conectamos tu ERP, CRM, correo, hojas de cálculo y aplicaciones mediante n8n, Make y Zapier para eliminar el trabajo manual. Automatizamos facturación, albaranes, informes, sincronización de datos y comunicaciones. Media de ahorro: 8-12 horas semanales por persona.',
    href: '/automatizacion-procesos',
    cta: 'Ver cómo funciona',
  },
  {
    icon: Bot,
    title: 'Agentes IA',
    description:
      'Desarrollamos agentes inteligentes basados en LLMs con arquitectura RAG conectados a tus datos internos: documentación, CRM, base de conocimiento. Atienden consultas de clientes, procesan documentos, generan respuestas y ejecutan tareas de forma autónoma 24/7.',
    href: '/agentes-ia',
    cta: 'Explorar agentes',
  },
  {
    icon: Search,
    title: 'Auditoría IA',
    description:
      'Analizamos en profundidad tus procesos, herramientas actuales y puntos de dolor para identificar las 3-5 oportunidades de mayor impacto con inteligencia artificial. Recibes un informe detallado con priorización, ROI estimado y recomendaciones de implementación.',
    href: '/auditoria-ia',
    cta: 'Solicitar auditoría',
  },
  {
    icon: GraduationCap,
    title: 'Formación IA para empresas',
    description:
      'Talleres presenciales y online adaptados a tu sector y nivel: uso profesional de ChatGPT, automatización básica con IA, y creación de flujos con n8n o Make. Formación práctica con casos reales de tu industria, certificación incluida y sin conocimientos técnicos previos.',
    href: '/formacion-ia',
    cta: 'Ver formaciones',
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

export default function ServicesGrid() {
  return (
    <section
      aria-labelledby="services-heading"
      className="bg-slate-50 py-20 md:py-28"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="services-heading"
            className="text-3xl font-extrabold tracking-tight text-[#0F172A] sm:text-4xl"
          >
            Nuestros servicios
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Soluciones prácticas de IA adaptadas al tamaño y necesidades de tu empresa.
          </p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          {services.map((service) => {
            const Icon = service.icon
            return (
              <motion.article
                key={service.title}
                variants={cardVariants}
                className="group flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-[#2563EB] transition-colors group-hover:bg-[#2563EB] group-hover:text-white">
                  <Icon className="h-6 w-6" aria-hidden="true" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-[#0F172A]">
                  {service.title}
                </h3>
                <p className="flex-1 text-sm leading-relaxed text-slate-500">
                  {service.description}
                </p>
                <Link
                  href={service.href}
                  className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-[#2563EB] transition-colors hover:text-blue-700"
                  aria-label={`${service.cta} sobre ${service.title}`}
                >
                  {service.cta}
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" aria-hidden="true" />
                </Link>
              </motion.article>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
