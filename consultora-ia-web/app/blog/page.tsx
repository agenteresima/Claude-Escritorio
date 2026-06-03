'use client'

import { useState } from 'react'
import Link from 'next/link'
import { blogPosts, blogCategories } from '@/lib/blog-data'
import { Calendar, Clock, ArrowRight, Mail } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'

const newsletterSchema = z.object({
  email: z.string().email('Introduce un email válido'),
})
type NewsletterData = z.infer<typeof newsletterSchema>

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
}

const categoryColors: Record<string, string> = {
  'Estrategia IA': 'bg-blue-50 text-blue-700 border-blue-200',
  'Automatización': 'bg-purple-50 text-purple-700 border-purple-200',
  'Herramientas IA': 'bg-green-50 text-green-700 border-green-200',
  'Agentes IA': 'bg-orange-50 text-orange-700 border-orange-200',
}

export default function BlogPage() {
  const [activeCategory, setActiveCategory] = useState('Todos')
  const [newsletterSent, setNewsletterSent] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<NewsletterData>({
    resolver: zodResolver(newsletterSchema),
  })

  const filtered = activeCategory === 'Todos'
    ? blogPosts
    : blogPosts.filter((p) => p.category === activeCategory)

  const onNewsletter = async (data: NewsletterData) => {
    await fetch('/api/newsletter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    setNewsletterSent(true)
  }

  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 pt-24 pb-16 text-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block bg-blue-600/20 border border-blue-500/30 text-blue-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            Blog
          </span>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Blog de IA <span className="text-blue-400">para empresas</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto">
            Guías prácticas, casos reales y estrategias para directivos y responsables de empresa
            que quieren implementar la inteligencia artificial con resultados medibles.
          </p>
        </div>
      </section>

      {/* Filters + Posts */}
      <section className="py-16 bg-slate-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          {/* Category filters */}
          <div className="flex flex-wrap gap-2 mb-10">
            {['Todos', ...blogCategories].map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  activeCategory === cat
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-slate-200 text-slate-600 hover:border-blue-400 hover:text-blue-600'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Posts grid */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((post) => (
              <Link
                key={post.slug}
                href={`/blog/${post.slug}`}
                className="group bg-white border border-slate-200 rounded-2xl overflow-hidden hover:border-blue-300 hover:shadow-md transition-all flex flex-col"
              >
                <div className="p-6 flex flex-col flex-grow">
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`text-xs font-medium px-2.5 py-1 rounded-full border ${
                        categoryColors[post.category] ?? 'bg-slate-100 text-slate-600 border-slate-200'
                      }`}
                    >
                      {post.category}
                    </span>
                    <div className="flex items-center gap-1 text-slate-400 text-xs">
                      <Clock className="h-3 w-3" />
                      {post.readTime} min
                    </div>
                  </div>
                  <h2 className="font-bold text-slate-900 mb-3 group-hover:text-blue-700 transition-colors leading-snug">
                    {post.title}
                  </h2>
                  <p className="text-sm text-slate-600 leading-relaxed flex-grow">
                    {post.description}
                  </p>
                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <Calendar className="h-3 w-3" />
                      {formatDate(post.date)}
                    </div>
                    <span className="text-xs text-blue-600 font-medium group-hover:gap-2 flex items-center gap-1 transition-all">
                      Leer
                      <ArrowRight className="h-3 w-3" />
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="py-20 bg-blue-600">
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 text-center">
          <Mail className="h-10 w-10 text-blue-200 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-white mb-3">
            Recibe los artículos en tu bandeja de entrada
          </h2>
          <p className="text-blue-100 mb-8">
            Publicamos cada semana. Sin spam. Solo contenido práctico sobre IA para empresas.
          </p>
          {newsletterSent ? (
            <div className="bg-white/10 border border-white/20 rounded-xl p-4 text-white font-medium">
              ¡Suscripción confirmada! Recibirás los próximos artículos en tu email.
            </div>
          ) : (
            <form onSubmit={handleSubmit(onNewsletter)} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
              <div className="flex-grow">
                <input
                  {...register('email')}
                  type="email"
                  placeholder="tu@empresa.es"
                  className="w-full px-4 py-3 rounded-xl text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-white"
                />
                {errors.email && (
                  <p className="text-red-200 text-xs mt-1 text-left">{errors.email.message}</p>
                )}
              </div>
              <button
                type="submit"
                className="bg-white hover:bg-blue-50 text-blue-700 font-semibold px-6 py-3 rounded-xl transition-colors whitespace-nowrap"
              >
                Suscribirme
              </button>
            </form>
          )}
        </div>
      </section>
    </>
  )
}
