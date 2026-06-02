'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { CheckCircle2, ArrowRight, Calendar, MessageSquare, TrendingUp, Settings } from 'lucide-react'

const includes = [
  'Reunión mensual de seguimiento y planificación (videollamada 1h)',
  'Soporte por chat para dudas y consultas rápidas (L-V)',
  'Supervisión y optimización de las automatizaciones activas',
  'Identificación continua de nuevas oportunidades de mejora con IA',
  'Acceso a nuestra biblioteca de prompts, plantillas y herramientas',
  'Informes mensuales de impacto: horas ahorradas, errores evitados, ROI',
  'Formación continua del equipo en nuevas funcionalidades',
  'Prioridad en la atención y en nuevas implementaciones',
]

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: 'easeOut' } },
}

export default function ExternalConsultant() {
  return (
    <section
      aria-labelledby="extconsultant-heading"
      className="bg-[#0F172A] py-20 md:py-28"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="overflow-hidden rounded-3xl border border-blue-500/20 bg-gradient-to-br from-slate-800/80 to-[#0F172A]">
          <div className="grid gap-12 p-8 md:grid-cols-2 md:gap-16 md:p-12 lg:p-16">

            {/* Left column */}
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeUp}
              className="flex flex-col justify-center"
            >
              <span className="mb-4 inline-flex w-fit items-center rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-400">
                Servicio estrella
              </span>
              <h2
                id="extconsultant-heading"
                className="text-3xl font-extrabold leading-tight tracking-tight text-white sm:text-4xl"
              >
                Tu consultor de IA externo,{' '}
                <span className="bg-gradient-to-r from-blue-400 to-blue-300 bg-clip-text text-transparent">
                  sin coste de plantilla
                </span>
              </h2>
              <p className="mt-5 text-base leading-relaxed text-slate-300">
                Tener un experto en IA en plantilla cuesta entre 40.000€ y 70.000€ al año,
                y es difícil de encontrar. Nosotros te damos ese expertise, de forma flexible
                y por una fracción del coste, mes a mes y sin permanencia.
              </p>
              <p className="mt-3 text-base leading-relaxed text-slate-400">
                Somos tu equipo de IA externo: conocemos tu empresa, tus sistemas y tus
                objetivos. Trabajamos contigo de forma continua para que la IA
                siga aportando valor cada mes.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  href="/consultor-ia-externo"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-[#2563EB] px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:bg-blue-500"
                  aria-label="Conocer el servicio de consultor IA externo"
                >
                  Conocer este servicio
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
                <Link
                  href="/diagnostico-gratuito"
                  className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-600 px-6 py-3 text-sm font-semibold text-slate-300 transition-all hover:border-slate-400 hover:text-white"
                  aria-label="Reservar llamada de diagnóstico gratuita"
                >
                  Reservar llamada gratuita
                </Link>
              </div>
            </motion.div>

            {/* Right column — what's included */}
            <motion.div
              initial={{ opacity: 0, x: 24 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut', delay: 0.15 }}
              viewport={{ once: true }}
            >
              <div className="rounded-2xl border border-slate-700/50 bg-slate-900/50 p-6 md:p-8">
                <h3 className="mb-6 text-base font-semibold text-white">
                  Qué incluye el servicio mensual
                </h3>
                <ul className="space-y-3" role="list">
                  {includes.map((item) => (
                    <li key={item} className="flex items-start gap-3">
                      <CheckCircle2
                        className="mt-0.5 h-5 w-5 flex-shrink-0 text-blue-400"
                        aria-hidden="true"
                      />
                      <span className="text-sm leading-relaxed text-slate-300">{item}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-6 rounded-xl bg-blue-500/10 border border-blue-500/20 p-4">
                  <p className="text-xs text-slate-400">
                    <span className="font-semibold text-blue-300">Sin permanencia.</span>{' '}
                    Cancela cuando quieras con 15 días de aviso. Sin letra pequeña.
                  </p>
                </div>
              </div>
            </motion.div>

          </div>
        </div>
      </div>
    </section>
  )
}
