import type { Metadata } from 'next'
import Link from 'next/link'
import { GraduationCap, Users, BookOpen, Award, Target, TrendingUp, ArrowRight } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Formación en IA para Empresas | Capacitación Equipos | AP Automatización IA',
  description:
    'Formación práctica en inteligencia artificial para equipos empresariales. ChatGPT, Claude, Copilot y herramientas de automatización. Adaptada a tu sector y resultados inmediatos.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/servicios/formacion-ia' },
  openGraph: {
    title: 'Formación en IA para Empresas | AP Automatización IA',
    description:
      'Capacitación práctica en IA para equipos. ChatGPT, Claude, Copilot y automatización. Adaptada a tu sector con resultados desde el primer día.',
    url: 'https://www.automatizacionprocesos.es/servicios/formacion-ia',
  },
}

const includes = [
  {
    icon: GraduationCap,
    title: 'Formación adaptada a tu sector',
    description:
      'No es un curso genérico. Cada módulo se adapta al sector de tu empresa: ejemplos reales, casos prácticos y herramientas específicas para tu industria.',
  },
  {
    icon: Users,
    title: 'Presencial, online o híbrida',
    description:
      'Nos adaptamos a tu equipo. Formación en tus instalaciones, en remoto o en formato híbrido. Grupos reducidos para garantizar la atención individual.',
  },
  {
    icon: BookOpen,
    title: 'Materiales descargables incluidos',
    description:
      'Guías de prompts, plantillas, checklists y recursos prácticos que el equipo puede usar desde el primer día después de la formación.',
  },
  {
    icon: Award,
    title: 'Certificado de participación',
    description:
      'Cada participante recibe un certificado de formación con las competencias adquiridas, útil para el desarrollo profesional del equipo.',
  },
  {
    icon: Target,
    title: 'Objetivos medibles',
    description:
      'Definimos antes de empezar qué debe saber hacer el equipo al terminar. La formación se evalúa sobre ejercicios prácticos reales, no sobre teoría.',
  },
  {
    icon: TrendingUp,
    title: 'Seguimiento post-formación',
    description:
      'Sesión de seguimiento a las 4 semanas para resolver dudas surgidas en el uso real. La formación no termina en el aula.',
  },
]

const benefits = [
  {
    title: 'El equipo gana 2 horas al día desde la primera semana',
    description:
      'Los empleados que aprenden a usar IA de forma efectiva reducen drásticamente el tiempo en redacción, búsqueda de información y tareas repetitivas. El impacto es inmediato.',
    stat: '+2h',
    label: 'productividad diaria por persona',
  },
  {
    title: 'Adopción real, no solo conocimiento teórico',
    description:
      'Nuestra metodología es 80% práctica. Cada ejercicio se realiza con las herramientas reales que el equipo va a usar en su trabajo cotidiano. No hay teoría innecesaria.',
    stat: '80%',
    label: 'práctica aplicada al trabajo real',
  },
  {
    title: 'Reducción del miedo y resistencia al cambio',
    description:
      'La mayor barrera de adopción de la IA en las empresas es el desconocimiento. Una formación bien diseñada convierte el escepticismo en entusiasmo y autonomía.',
    stat: '9/10',
    label: 'satisfacción media de participantes',
  },
]

export default function FormacionIAPage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Formación en IA para empresas
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Capacita a tu equipo en IA{' '}
            <span className="text-blue-400">con resultados desde el primer día</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-10">
            Formación práctica y aplicada para que tu equipo domine ChatGPT, Claude, Copilot y las
            principales herramientas de automatización. Adaptada a tu sector, sin teoría innecesaria
            y con impacto real en la productividad.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/diagnostico-gratuito"
              className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl font-semibold transition-colors"
            >
              Solicitar diagnóstico gratuito
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/contacto"
              className="inline-flex items-center justify-center gap-2 border border-slate-600 hover:border-slate-400 text-slate-300 hover:text-white px-8 py-4 rounded-xl font-semibold transition-colors"
            >
              Hablar con un consultor
            </Link>
          </div>
        </div>
      </section>

      {/* ¿Qué incluye? */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">¿Qué incluye el servicio?</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Una formación diseñada para que los conocimientos se apliquen al día siguiente en el
              trabajo real, no para quedar guardados en una carpeta de apuntes.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {includes.map((item) => {
              const Icon = item.icon
              return (
                <div key={item.title} className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200">
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-50 rounded-xl mb-4">
                    <Icon className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">{item.title}</h3>
                  <p className="text-slate-600 text-sm leading-relaxed">{item.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Beneficios */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Beneficios concretos</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Lo que consiguen las empresas que forman a sus equipos en inteligencia artificial.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {benefits.map((b) => (
              <div key={b.title} className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200">
                <div className="text-4xl font-bold text-blue-600 mb-1">{b.stat}</div>
                <div className="text-xs text-slate-500 mb-4 font-semibold uppercase tracking-wider">{b.label}</div>
                <h3 className="text-lg font-semibold text-slate-900 mb-3">{b.title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">{b.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section className="bg-slate-900 text-white py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            ¿Quieres que tu equipo domine la IA?
          </h2>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto mb-8">
            En 45 minutos de videollamada analizamos el nivel actual de tu equipo, los objetivos
            de la formación y diseñamos un plan adaptado a tu empresa. Sin compromiso.
          </p>
          <Link
            href="/diagnostico-gratuito"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-colors text-lg"
          >
            Solicitar diagnóstico gratuito
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>
    </>
  )
}
