'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, MessageCircle } from 'lucide-react'

export default function CTAFinal() {
  return (
    <section
      aria-labelledby="cta-final-heading"
      className="bg-white py-20 md:py-24"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#0F172A] via-[#0F172A] to-[#1e3a70] px-8 py-16 text-center md:px-16"
        >
          {/* Decorative blobs */}
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 overflow-hidden"
          >
            <div className="absolute -left-20 -top-20 h-64 w-64 rounded-full bg-[#2563EB] opacity-10 blur-3xl" />
            <div className="absolute -bottom-20 -right-20 h-64 w-64 rounded-full bg-blue-400 opacity-10 blur-3xl" />
          </div>

          <div className="relative">
            <h2
              id="cta-final-heading"
              className="mx-auto max-w-2xl text-3xl font-extrabold tracking-tight text-white sm:text-4xl"
            >
              ¿Listo para dar el primer paso con la IA?
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-lg text-slate-300">
              Reserva una videollamada de diagnóstico gratuita de 45 minutos.
              Sin compromiso, sin tecnicismos, sin presión.
            </p>

            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link
                href="/diagnostico-gratuito"
                className="inline-flex items-center gap-2 rounded-lg bg-[#2563EB] px-8 py-4 text-base font-semibold text-white shadow-xl shadow-blue-500/30 transition-all hover:bg-blue-500 hover:shadow-blue-400/40 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-[#0F172A]"
                aria-label="Solicitar diagnóstico gratuito de inteligencia artificial"
              >
                Solicitar diagnóstico gratuito
                <ArrowRight className="h-5 w-5" aria-hidden="true" />
              </Link>
              <Link
                href="/contacto"
                className="inline-flex items-center gap-2 rounded-lg border border-slate-500 bg-transparent px-8 py-4 text-base font-semibold text-slate-200 transition-all hover:border-slate-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-[#0F172A]"
                aria-label="Contactar con Automatización Procesos IA"
              >
                <MessageCircle className="h-5 w-5" aria-hidden="true" />
                Hablar con nosotros
              </Link>
            </div>

            <p className="mt-6 text-sm text-slate-500">
              Respuesta garantizada en menos de 24 horas laborables
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
