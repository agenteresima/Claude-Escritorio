'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, CheckCircle2, Sparkles } from 'lucide-react'

const stats = [
  { value: '50+', label: 'Empresas asesoradas' },
  { value: '200+', label: 'Procesos automatizados' },
  { value: '30%', label: 'Ahorro de tiempo medio' },
]

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (delay: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay, ease: 'easeOut' },
  }),
}

export default function Hero() {
  return (
    <section
      aria-label="Sección principal"
      className="relative overflow-hidden bg-[#0F172A] pt-24 pb-20 md:pt-32 md:pb-28"
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 overflow-hidden"
      >
        <div className="absolute -top-40 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-[#2563EB] opacity-10 blur-3xl" />
        <div className="absolute top-1/2 right-0 h-[400px] w-[400px] rounded-full bg-[#2563EB] opacity-5 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center">

          <motion.div
            custom={0}
            initial="hidden"
            animate="visible"
            variants={fadeUp}
            className="mb-6"
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-sm font-medium text-blue-400">
              <Sparkles className="h-4 w-4" aria-hidden="true" />
              Consultoría IA para empresas
            </span>
          </motion.div>

          <motion.h1
            custom={0.15}
            initial="hidden"
            animate="visible"
            variants={fadeUp}
            className="mx-auto max-w-4xl text-4xl font-extrabold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl"
          >
            El experto en IA que tu empresa{' '}
            <span className="bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
              todavía no tiene en plantilla
            </span>
          </motion.h1>

          <motion.p
            custom={0.3}
            initial="hidden"
            animate="visible"
            variants={fadeUp}
            className="mt-6 max-w-2xl text-lg leading-relaxed text-slate-300 sm:text-xl"
          >
            Ayudamos a empresas y pymes a implementar inteligencia artificial de forma práctica,
            sin tecnicismos y con resultados medibles.
          </motion.p>

          <motion.div
            custom={0.45}
            initial="hidden"
            animate="visible"
            variants={fadeUp}
            className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center"
          >
            <Link
              href="/diagnostico-gratuito"
              className="inline-flex items-center gap-2 rounded-lg bg-[#2563EB] px-7 py-3.5 text-base font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:bg-blue-500 hover:shadow-blue-500/40 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#0F172A]"
              aria-label="Solicitar diagnóstico gratuito de IA"
            >
              Solicitar diagnóstico gratuito
              <ArrowRight className="h-5 w-5" aria-hidden="true" />
            </Link>
            <Link
              href="/servicios"
              className="inline-flex items-center gap-2 rounded-lg border border-slate-600 bg-transparent px-7 py-3.5 text-base font-semibold text-slate-200 transition-all hover:border-slate-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-[#0F172A]"
              aria-label="Ver todos los servicios de AP Automatización IA"
            >
              Ver nuestros servicios
            </Link>
          </motion.div>

          <motion.div
            custom={0.55}
            initial="hidden"
            animate="visible"
            variants={fadeUp}
            className="mt-6 flex flex-wrap items-center justify-center gap-5 text-sm text-slate-400"
          >
            {['Sin permanencia', 'Primera sesión gratuita', 'Resultados en semanas'].map((item) => (
              <span key={item} className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-blue-400" aria-hidden="true" />
                {item}
              </span>
            ))}
          </motion.div>

          <motion.div
            custom={0.65}
            initial="hidden"
            animate="visible"
            variants={fadeUp}
            className="mt-16 grid w-full max-w-3xl grid-cols-1 gap-6 sm:grid-cols-3 sm:gap-8"
          >
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="rounded-xl border border-slate-700/50 bg-slate-800/40 px-8 py-6 text-center backdrop-blur-sm"
              >
                <p className="text-4xl font-extrabold text-white">{stat.value}</p>
                <p className="mt-1 text-sm font-medium text-slate-400">{stat.label}</p>
              </div>
            ))}
          </motion.div>

        </div>
      </div>
    </section>
  )
}
