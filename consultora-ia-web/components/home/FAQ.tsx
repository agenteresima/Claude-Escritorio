'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'

interface FAQItem {
  question: string
  answer: string
}

const faqs: FAQItem[] = [
  {
    question: '¿Necesito conocimientos técnicos para trabajar con vosotros?',
    answer:
      'En absoluto. Nuestra filosofía es que la IA tiene que ser accesible para cualquier empresa, independientemente de su nivel técnico. Nos adaptamos a vuestro lenguaje y explicamos todo sin tecnicismos. Vosotros nos contáis vuestros problemas de negocio y nosotros nos encargamos de la parte técnica.',
  },
  {
    question: '¿Cuánto tiempo lleva ver resultados?',
    answer:
      'Depende del alcance del proyecto, pero en la mayoría de los casos los primeros resultados se ven en 4 a 8 semanas desde el inicio de la implementación. Las automatizaciones sencillas pueden estar operativas en días. Los proyectos más complejos, como agentes IA personalizados, pueden llevar 2 o 3 meses para estar completamente operativos.',
  },
  {
    question: '¿Trabajáis solo con grandes empresas?',
    answer:
      'No. La mayoría de nuestros clientes son pymes de entre 5 y 100 empleados. De hecho, las pymes suelen tener más que ganar con la IA, porque cada hora ahorrada tiene un impacto directo en la rentabilidad. Adaptamos nuestras soluciones y precios al tamaño real de tu empresa.',
  },
  {
    question: '¿Qué diferencia hay entre ChatGPT y un agente IA personalizado?',
    answer:
      'ChatGPT es una herramienta genérica: funciona bien para tareas generales pero no conoce tu empresa, no accede a tus sistemas y no puede actuar en tu nombre. Un agente IA personalizado está entrenado con tu información, conectado a tus herramientas (CRM, ERP, correo, calendario...) y puede ejecutar tareas concretas de forma autónoma. Es la diferencia entre un empleado temporal y alguien que lleva años en tu empresa.',
  },
  {
    question: '¿Tengo que cambiar todos mis sistemas actuales?',
    answer:
      'No. Trabajamos sobre lo que ya tienes. La mayoría de las automatizaciones y agentes que construimos se integran con tus herramientas actuales: correo, CRM, ERP, hojas de cálculo, WhatsApp Business, etc. Solo en casos muy concretos recomendamos cambiar alguna herramienta, y siempre lo discutimos contigo antes.',
  },
  {
    question: '¿Cuánto cuesta una consultoría IA?',
    answer:
      'Los precios varían según el alcance. Un diagnóstico inicial es gratuito. Una auditoría básica empieza desde 1.500€. Los proyectos de automatización o agentes IA suelen estar entre 3.000€ y 15.000€ según complejidad. El servicio de consultor externo mensual tiene un precio fijo mensual. En todos los casos, trabajamos con presupuesto cerrado sin sorpresas.',
  },
  {
    question: '¿Cómo funciona el servicio de Consultor IA externo?',
    answer:
      'Es un servicio de acompañamiento mensual en el que actuamos como tu equipo de IA interno. Incluye una reunión mensual, soporte continuo por chat, supervisión de automatizaciones activas, identificación de nuevas oportunidades y formación al equipo. Se contrata mes a mes, sin permanencia mínima, y puedes cancelar con 15 días de aviso.',
  },
  {
    question: '¿Qué pasa si ya tenemos ChatGPT o Copilot?',
    answer:
      'Perfecto, es un buen punto de partida. Nuestra labor es ayudaros a ir más allá: crear flujos de trabajo integrados, automatizar procesos completos, conectar estas herramientas con vuestros sistemas y formar al equipo para sacarles el máximo partido. Tener ChatGPT instalado no es lo mismo que tener una estrategia de IA. Nosotros os ayudamos a construir esa estrategia.',
  },
]

function FAQAccordionItem({ item, index }: { item: FAQItem; index: number }) {
  const [isOpen, setIsOpen] = useState(false)
  const id = `faq-item-${index}`

  return (
    <div className="border-b border-slate-200 last:border-0">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls={id}
        className="flex w-full items-center justify-between gap-4 py-5 text-left transition-colors hover:text-[#2563EB]"
      >
        <span className="text-base font-semibold text-[#0F172A]">{item.question}</span>
        <ChevronDown
          className={`h-5 w-5 flex-shrink-0 text-[#2563EB] transition-transform duration-300 ${
            isOpen ? 'rotate-180' : ''
          }`}
          aria-hidden="true"
        />
      </button>

      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            id={id}
            role="region"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <p className="pb-5 text-sm leading-relaxed text-slate-500">{item.answer}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function FAQ() {
  return (
    <section
      aria-labelledby="faq-heading"
      className="bg-slate-50 py-20 md:py-28"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="faq-heading"
            className="text-3xl font-extrabold tracking-tight text-[#0F172A] sm:text-4xl"
          >
            Preguntas frecuentes
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Respuestas honestas a las preguntas que nos hacen habitualmente las empresas
            que están valorando trabajar con nosotros.
          </p>
        </div>

        <div className="mx-auto mt-12 max-w-3xl divide-y-0 rounded-2xl border border-slate-200 bg-white px-6 shadow-sm md:px-8">
          {faqs.map((item, index) => (
            <FAQAccordionItem key={item.question} item={item} index={index} />
          ))}
        </div>
      </div>
    </section>
  )
}
