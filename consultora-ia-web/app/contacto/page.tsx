'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { Mail, Phone, Clock, CheckCircle, ArrowRight, Send } from 'lucide-react'

const schema = z.object({
  nombre: z.string().min(2, 'El nombre es obligatorio'),
  empresa: z.string().min(2, 'El nombre de la empresa es obligatorio'),
  cargo: z.string().min(2, 'El cargo es obligatorio'),
  email: z.string().email('Introduce un email válido'),
  telefono: z.string().optional(),
  servicio: z.string().min(1, 'Selecciona un servicio'),
  mensaje: z.string().min(20, 'El mensaje debe tener al menos 20 caracteres'),
})

type FormData = z.infer<typeof schema>

const services = [
  'Diagnóstico gratuito (videollamada 45 min)',
  'Auditoría IA',
  'Automatización de procesos',
  'Agentes IA',
  'Consultor IA externo',
  'Formación en IA',
  'Otro / No sé todavía',
]

export default function ContactoPage() {
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (!res.ok) throw new Error('Error al enviar el formulario')
      setSubmitted(true)
    } catch {
      setError('Ha ocurrido un error. Por favor, inténtalo de nuevo o escríbenos directamente a hola@automatizacionprocesos.es')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Contacto
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Hablemos sobre <span className="text-blue-400">tu empresa</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto">
            Cuéntanos qué necesitas y te respondemos en menos de 24 horas. Sin presión comercial,
            sin compromiso.
          </p>
        </div>
      </section>

      {/* Content */}
      <section className="py-20 bg-slate-50">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-3 gap-10">
            {/* Contact info */}
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-slate-900 mb-4">Información de contacto</h2>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <Mail className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Email</div>
                      <a
                        href="mailto:hola@automatizacionprocesos.es"
                        className="text-slate-900 font-medium hover:text-blue-600 transition-colors"
                      >
                        hola@automatizacionprocesos.es
                      </a>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <Phone className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Teléfono</div>
                      <a
                        href="tel:+34900000000"
                        className="text-slate-900 font-medium hover:text-blue-600 transition-colors"
                      >
                        +34 900 000 000
                      </a>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <Clock className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Horario</div>
                      <div className="text-slate-900 font-medium">Lunes–Viernes 9:00–18:00</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-blue-600 rounded-2xl p-5 text-white">
                <h3 className="font-bold mb-2">¿Prefieres empezar con una llamada?</h3>
                <p className="text-blue-100 text-sm mb-4">
                  El diagnóstico gratuito es una videollamada de 45 minutos sin coste ni compromiso.
                </p>
                <Link
                  href="/diagnostico-gratuito"
                  className="inline-flex items-center gap-2 bg-white text-blue-700 font-semibold text-sm px-4 py-2.5 rounded-lg hover:bg-blue-50 transition-colors"
                >
                  Solicitar diagnóstico gratuito
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>

            {/* Form */}
            <div className="lg:col-span-2">
              {submitted ? (
                <div className="bg-white border border-green-200 rounded-2xl p-10 text-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-2">
                    Mensaje recibido
                  </h2>
                  <p className="text-slate-600 mb-6">
                    Gracias por contactar con AP Automatización IA. Te responderemos en menos de 24 horas en
                    días laborables.
                  </p>
                  <Link
                    href="/"
                    className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Volver al inicio
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              ) : (
                <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8">
                  <h2 className="text-xl font-bold text-slate-900 mb-6">Envíanos un mensaje</h2>
                  <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                    <div className="grid sm:grid-cols-2 gap-5">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Nombre *
                        </label>
                        <input
                          {...register('nombre')}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Tu nombre"
                        />
                        {errors.nombre && (
                          <p className="text-red-500 text-xs mt-1">{errors.nombre.message}</p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Empresa *
                        </label>
                        <input
                          {...register('empresa')}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Nombre de tu empresa"
                        />
                        {errors.empresa && (
                          <p className="text-red-500 text-xs mt-1">{errors.empresa.message}</p>
                        )}
                      </div>
                    </div>

                    <div className="grid sm:grid-cols-2 gap-5">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Cargo *
                        </label>
                        <input
                          {...register('cargo')}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Tu cargo"
                        />
                        {errors.cargo && (
                          <p className="text-red-500 text-xs mt-1">{errors.cargo.message}</p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Email *
                        </label>
                        <input
                          {...register('email')}
                          type="email"
                          className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="tu@empresa.es"
                        />
                        {errors.email && (
                          <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>
                        )}
                      </div>
                    </div>

                    <div className="grid sm:grid-cols-2 gap-5">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Teléfono
                        </label>
                        <input
                          {...register('telefono')}
                          type="tel"
                          className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="+34 600 000 000"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          ¿En qué podemos ayudarte? *
                        </label>
                        <select
                          {...register('servicio')}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                        >
                          <option value="">Selecciona un servicio</option>
                          {services.map((s) => (
                            <option key={s} value={s}>
                              {s}
                            </option>
                          ))}
                        </select>
                        {errors.servicio && (
                          <p className="text-red-500 text-xs mt-1">{errors.servicio.message}</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Mensaje *
                      </label>
                      <textarea
                        {...register('mensaje')}
                        rows={4}
                        className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        placeholder="Cuéntanos brevemente qué necesitas o qué problema quieres resolver..."
                      />
                      {errors.mensaje && (
                        <p className="text-red-500 text-xs mt-1">{errors.mensaje.message}</p>
                      )}
                    </div>

                    {error && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
                        {error}
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white font-semibold px-8 py-3 rounded-xl transition-colors"
                    >
                      {loading ? 'Enviando...' : 'Enviar mensaje'}
                      <Send className="h-4 w-4" />
                    </button>
                  </form>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
