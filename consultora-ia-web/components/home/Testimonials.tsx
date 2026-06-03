'use client'

import { motion } from 'framer-motion'
import { Quote } from 'lucide-react'

interface Testimonial {
  quote: string
  name: string
  role: string
  company: string
  sector: string
  initials: string
}

const testimonials: Testimonial[] = [
  {
    quote:
      'Llevábamos años queriendo modernizar nuestros procesos pero nunca encontrábamos el momento ni sabíamos por dónde empezar. En tres meses con AP Automatización IA automatizamos la gestión de expedientes y la comunicación con clientes. El equipo tiene ahora tiempo para hacer lo que realmente importa.',
    name: 'María Dolores Fuentes',
    role: 'Socia directora',
    company: 'Fuentes & Asociados',
    sector: 'Asesoría jurídica · Madrid',
    initials: 'MF',
  },
  {
    quote:
      'Éramos escépticos con todo lo de la IA. Pensábamos que era para grandes corporaciones o que era muy cara. AP Automatización IA nos demostró lo contrario: en semanas teníamos automatizada la gestión de pedidos y un agente respondiendo a nuestros transportistas fuera de horario. El ROI fue claro desde el primer mes.',
    name: 'Jordi Puigdomènech',
    role: 'Director de operaciones',
    company: 'Translogix Barcelona',
    sector: 'Logística · Barcelona',
    initials: 'JP',
  },
  {
    quote:
      'Tenemos una clínica mediana y el mayor dolor de cabeza era la gestión de citas y los olvidos de pacientes. Con el sistema que nos implementaron, los recordatorios y confirmaciones son automáticos. Las ausencias sin aviso son prácticamente cero y la agenda siempre está llena. Ojalá lo hubiéramos hecho antes.',
    name: 'Alejandro Moreno',
    role: 'Gerente',
    company: 'Clínica Dental Moreno',
    sector: 'Salud · Sevilla',
    initials: 'AM',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.15 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: 'easeOut' } },
}

export default function Testimonials() {
  return (
    <section
      aria-labelledby="testimonials-heading"
      className="bg-slate-50 py-20 md:py-28"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="testimonials-heading"
            className="text-3xl font-extrabold tracking-tight text-[#0F172A] sm:text-4xl"
          >
            Lo que dicen nuestros clientes
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Empresas reales que ya han transformado sus procesos con nuestra ayuda.
          </p>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="mt-14 grid gap-6 md:grid-cols-3"
        >
          {testimonials.map((testimonial) => (
            <motion.figure
              key={testimonial.name}
              variants={cardVariants}
              className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div className="mb-4 text-[#2563EB]">
                <Quote className="h-8 w-8 opacity-30" aria-hidden="true" />
              </div>
              <blockquote className="flex-1">
                <p className="text-sm leading-relaxed text-slate-600">
                  "{testimonial.quote}"
                </p>
              </blockquote>
              <figcaption className="mt-6 flex items-center gap-4">
                <div
                  className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-full bg-[#0F172A] text-sm font-bold text-blue-400"
                  aria-hidden="true"
                >
                  {testimonial.initials}
                </div>
                <div>
                  <p className="text-sm font-semibold text-[#0F172A]">{testimonial.name}</p>
                  <p className="text-xs text-slate-500">
                    {testimonial.role} · {testimonial.company}
                  </p>
                  <p className="mt-0.5 text-xs text-slate-400">{testimonial.sector}</p>
                </div>
              </figcaption>
            </motion.figure>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
