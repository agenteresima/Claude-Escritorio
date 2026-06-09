'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { CheckCircle, ArrowRight, Video, Clock, Shield } from 'lucide-react'

const tools = [
  'ChatGPT',
  'Claude',
  'Copilot',
  'Gemini',
  'n8n',
  'Make',
  'Zapier',
  'Power Automate',
  'Salesforce/HubSpot CRM',
  'SAP/Odoo ERP',
  'Excel avanzado',
  'Google Sheets',
  'Notion',
  'SharePoint',
  'Ninguna',
]

const schema = z.object({
  nombre: z.string().min(2, 'El nombre es obligatorio'),
  empresa: z.string().min(2, 'El nombre de la empresa es obligatorio'),
  cargo: z.string().min(2, 'El cargo es obligatorio'),
  email: z.string().email('Introduce un email válido'),
  telefono: z.string().optional(),
  sector: z.string().min(1, 'Selecciona tu sector'),
  empleados: z.string().min(1, 'Selecciona el tamaño de tu empresa'),
  problema: z.string().min(30, 'Descríbenos el problema con al menos 30 caracteres'),
  herramientas: z.array(z.string()).optional(),
  disponibilidad: z.string().min(1, 'Selecciona tu disponibilidad'),
  rgpd: z.literal(true, { errorMap: () => ({ message: 'Debes aceptar la política de privacidad' }) }),
})

type FormData = z.infer<typeof schema>

export default function DiagnosticoGratuitoPage() {
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { herramientas: [] },
  })

  const onSubmit = async (data: FormData) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (!res.ok) throw new Error('Error')
      setSubmitted(true)
    } catch {
      setError('Ha ocurrido un error. Por favor, inténtalo de nuevo o escríbenos a admin@automatizacionprocesos.es')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <span className="inline-block bg-green-500/20 border border-green-400/30 text-green-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
              Gratuito y sin compromiso
            </span>
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
              Diagnóstico gratuito de IA{' '}
              <span className="text-blue-400">para tu empresa</span>
            </h1>
            <p className="text-lg text-slate-300 mb-8 leading-relaxed">
              Una videollamada de 45 minutos en la que analizamos tu empresa, identificamos las
              mejores oportunidades de automatización con IA y te damos una hoja de ruta inicial.
              Sin coste. Sin compromiso de compra.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {[
                { icon: Video, text: 'Videollamada 45 min' },
                { icon: Clock, text: 'Respuesta en 24h' },
                { icon: Shield, text: 'Sin compromiso' },
              ].map(({ icon: Icon, text }) => (
                <div key={text} className="flex items-center gap-2 justify-center">
                  <Icon className="h-4 w-4 text-green-400" />
                  <span className="text-slate-300 text-sm">{text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* What it covers */}
      <section className="py-16 bg-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-slate-900 mb-3">Qué cubre el diagnóstico</h2>
          </div>
          <div className="grid sm:grid-cols-3 gap-6">
            {[
              {
                title: 'Análisis de situación',
                description: 'Entendemos cómo funciona tu empresa, qué herramientas usas y dónde están los mayores cuellos de botella.',
              },
              {
                title: 'Identificar oportunidades',
                description: 'Detectamos los 2-3 procesos con mayor potencial de automatización y el impacto estimado de cada uno.',
              },
              {
                title: 'Hoja de ruta inicial',
                description: 'Te damos un plan orientativo de los siguientes pasos: por dónde empezar, qué costaría y qué esperarías obtener.',
              },
            ].map((item) => (
              <div key={item.title} className="border border-slate-200 rounded-xl p-5 text-center">
                <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CheckCircle className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Form */}
      <section className="py-16 bg-slate-50">
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8">
          {submitted ? (
            <div className="bg-white border border-green-200 rounded-2xl p-10 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-3">
                ¡Solicitud recibida!
              </h2>
              <p className="text-slate-600 mb-4">
                Hemos recibido tu solicitud de diagnóstico. Nos pondremos en contacto contigo en
                menos de 24 horas para confirmar la fecha y hora de la videollamada.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-left mb-6">
                <h3 className="font-semibold text-slate-900 mb-2 text-sm">Próximos pasos:</h3>
                <ul className="space-y-2">
                  {[
                    'Recibirás un email de confirmación en los próximos minutos',
                    'En menos de 24h te contactaremos para agendar la videollamada',
                    'Antes de la llamada te enviaremos un breve cuestionario preparatorio',
                    'La videollamada dura 45 minutos y es totalmente gratuita',
                  ].map((step) => (
                    <li key={step} className="flex items-start gap-2 text-sm text-slate-700">
                      <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                      {step}
                    </li>
                  ))}
                </ul>
              </div>
              <Link href="/" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium">
                Volver al inicio <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8">
              <h2 className="text-xl font-bold text-slate-900 mb-2">
                Solicita tu diagnóstico gratuito
              </h2>
              <p className="text-slate-500 text-sm mb-6">
                Rellena el formulario y te contactaremos en menos de 24 horas.
              </p>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                {/* Personal data */}
                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Nombre *</label>
                    <input
                      {...register('nombre')}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Tu nombre completo"
                    />
                    {errors.nombre && <p className="text-red-500 text-xs mt-1">{errors.nombre.message}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Empresa *</label>
                    <input
                      {...register('empresa')}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Nombre de la empresa"
                    />
                    {errors.empresa && <p className="text-red-500 text-xs mt-1">{errors.empresa.message}</p>}
                  </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Cargo *</label>
                    <input
                      {...register('cargo')}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Tu cargo en la empresa"
                    />
                    {errors.cargo && <p className="text-red-500 text-xs mt-1">{errors.cargo.message}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Email *</label>
                    <input
                      {...register('email')}
                      type="email"
                      className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="tu@empresa.es"
                    />
                    {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Teléfono (opcional)</label>
                  <input
                    {...register('telefono')}
                    type="tel"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="+34 600 000 000"
                  />
                </div>

                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Sector *</label>
                    <select
                      {...register('sector')}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                    >
                      <option value="">Selecciona tu sector</option>
                      {['Tecnología', 'Salud', 'Finanzas', 'Construcción', 'Logística', 'Comercio', 'Servicios profesionales', 'Industria', 'Educación', 'Otro'].map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                    {errors.sector && <p className="text-red-500 text-xs mt-1">{errors.sector.message}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Número de empleados *</label>
                    <select
                      {...register('empleados')}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                    >
                      <option value="">Selecciona</option>
                      {['1-10', '11-50', '51-200', '201-500', '+500'].map((e) => (
                        <option key={e} value={e}>{e}</option>
                      ))}
                    </select>
                    {errors.empleados && <p className="text-red-500 text-xs mt-1">{errors.empleados.message}</p>}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    ¿Cuál es tu principal problema o reto? *
                  </label>
                  <textarea
                    {...register('problema')}
                    rows={3}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    placeholder="Describe brevemente qué proceso te consume más tiempo o qué te gustaría mejorar con IA..."
                  />
                  {errors.problema && <p className="text-red-500 text-xs mt-1">{errors.problema.message}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Herramientas que ya utilizas
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {tools.map((tool) => (
                      <label key={tool} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          value={tool}
                          {...register('herramientas')}
                          className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-slate-600">{tool}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    ¿Cuándo tienes disponibilidad? *
                  </label>
                  <div className="flex flex-col sm:flex-row gap-3">
                    {['Mañanas (9-13h)', 'Tardes (14-18h)', 'Flexible'].map((option) => (
                      <label key={option} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          value={option}
                          {...register('disponibilidad')}
                          className="text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-slate-600">{option}</span>
                      </label>
                    ))}
                  </div>
                  {errors.disponibilidad && <p className="text-red-500 text-xs mt-1">{errors.disponibilidad.message}</p>}
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      {...register('rgpd')}
                      className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 mt-0.5"
                    />
                    <span className="text-sm text-slate-600">
                      Acepto la{' '}
                      <Link href="/privacidad" className="text-blue-600 hover:underline">
                        política de privacidad
                      </Link>{' '}
                      y consiento el tratamiento de mis datos personales para la prestación del servicio
                      solicitado y el envío de comunicaciones relacionadas. *
                    </span>
                  </label>
                  {errors.rgpd && <p className="text-red-500 text-xs mt-1">{errors.rgpd.message}</p>}
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white font-semibold px-8 py-3.5 rounded-xl transition-colors text-base"
                >
                  {loading ? 'Enviando solicitud...' : 'Solicitar diagnóstico gratuito'}
                  <ArrowRight className="h-4 w-4" />
                </button>
                <p className="text-center text-xs text-slate-400">
                  Sin coste · Sin compromiso · Respuesta en menos de 24 horas
                </p>
              </form>
            </div>
          )}
        </div>
      </section>
    </>
  )
}
