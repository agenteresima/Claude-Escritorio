import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { blogPosts, getBlogPost, getRelatedPosts } from '@/lib/blog-data'
import { Calendar, Clock, ArrowRight, ArrowLeft, ChevronRight, Tag } from 'lucide-react'
import ReadingProgress from '@/components/blog/ReadingProgress'

interface Props {
  params: Promise<{ slug: string }>
}

export function generateStaticParams() {
  return blogPosts.map((post) => ({ slug: post.slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const post = getBlogPost(slug)
  if (!post) return {}
  return {
    title: `${post.title} | Automatización Procesos IA`,
    description: post.description,
    alternates: { canonical: `https://www.automatizacionprocesos.es/blog/${post.slug}` },
    openGraph: {
      title: post.title,
      description: post.description,
      url: `https://www.automatizacionprocesos.es/blog/${post.slug}`,
      type: 'article',
      publishedTime: post.date,
      authors: ['Automatización Procesos IA'],
    },
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params
  const post = getBlogPost(slug)
  if (!post) notFound()

  const related = getRelatedPosts(slug, 3)

  const articleSchema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.description,
    datePublished: post.date,
    author: {
      '@type': 'Organization',
      name: 'Automatización Procesos IA',
      url: 'https://www.automatizacionprocesos.es',
    },
    publisher: {
      '@type': 'Organization',
      name: 'Automatización Procesos IA',
      url: 'https://www.automatizacionprocesos.es',
    },
    url: `https://www.automatizacionprocesos.es/blog/${post.slug}`,
  }

  return (
    <>
      <ReadingProgress />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />

      {/* Breadcrumbs */}
      <div className="bg-white border-b border-slate-200 pt-20">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-3">
          <nav className="flex items-center gap-2 text-sm text-slate-500">
            <Link href="/" className="hover:text-blue-600 transition-colors">
              Inicio
            </Link>
            <ChevronRight className="h-3.5 w-3.5" />
            <Link href="/blog" className="hover:text-blue-600 transition-colors">
              Blog
            </Link>
            <ChevronRight className="h-3.5 w-3.5" />
            <span className="text-slate-700 font-medium truncate max-w-xs">{post.title}</span>
          </nav>
        </div>
      </div>

      {/* Main */}
      <div className="py-12 bg-slate-50">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-3 gap-10">
            {/* Article */}
            <article className="lg:col-span-2">
              <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
                {/* Cabecera del artículo */}
                <div className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-8 sm:p-10 rounded-t-2xl">
                  <div className="flex items-center gap-3 mb-5">
                    <span className="text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30 px-3 py-1 rounded-full uppercase tracking-wide">
                      {post.category}
                    </span>
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <Clock className="h-3 w-3" />
                      {post.readTime} min de lectura
                    </div>
                  </div>
                  <h1 className="text-3xl sm:text-4xl font-bold text-white mb-5 leading-tight tracking-tight">
                    {post.title}
                  </h1>
                  <p className="text-lg text-slate-300 leading-relaxed mb-6 max-w-2xl">
                    {post.description}
                  </p>
                  <div className="flex items-center gap-3 pt-4 border-t border-white/10">
                    <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold">
                      AI
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{post.author}</p>
                      <div className="flex items-center gap-1 text-xs text-slate-400">
                        <Calendar className="h-3 w-3" />
                        {formatDate(post.date)}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-8 sm:p-10">
                  <div
                    className="prose prose-lg max-w-none
                      prose-headings:font-bold prose-headings:tracking-tight
                      prose-h2:text-2xl prose-h2:mt-12 prose-h2:mb-5
                      prose-h2:text-blue-700 prose-h2:border-l-4 prose-h2:border-blue-500 prose-h2:pl-4
                      prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3 prose-h3:text-slate-800
                      prose-p:text-slate-600 prose-p:leading-[1.85] prose-p:text-[1.05rem]
                      prose-a:text-blue-600 prose-a:font-medium prose-a:no-underline hover:prose-a:underline
                      prose-strong:text-slate-800 prose-strong:font-semibold
                      prose-ul:text-slate-600 prose-ol:text-slate-600
                      prose-li:my-2 prose-li:leading-relaxed
                      prose-blockquote:border-l-4 prose-blockquote:border-blue-400
                      prose-blockquote:bg-blue-50 prose-blockquote:rounded-r-xl
                      prose-blockquote:px-6 prose-blockquote:py-4 prose-blockquote:not-italic
                      prose-blockquote:text-slate-700
                      prose-code:bg-slate-100 prose-code:text-blue-700 prose-code:px-1.5
                      prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:font-medium
                      prose-pre:bg-slate-900 prose-pre:rounded-xl
                      prose-img:rounded-xl prose-img:shadow-md
                      prose-hr:border-slate-200 prose-hr:my-10"
                    dangerouslySetInnerHTML={{ __html: post.content }}
                  />
                </div>
              </div>

              {/* Tags */}
              {post.tags && post.tags.length > 0 && (
                <div className="mt-6 bg-white border border-slate-200 rounded-2xl p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <Tag className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-600">Temas</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {post.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-xs bg-slate-100 text-slate-600 px-3 py-1.5 rounded-full hover:bg-blue-50 hover:text-blue-700 transition-colors cursor-default"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Back to blog */}
              <div className="mt-4">
                <Link
                  href="/blog"
                  className="inline-flex items-center gap-2 text-slate-600 hover:text-blue-600 font-medium text-sm transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Volver al blog
                </Link>
              </div>
            </article>

            {/* Sidebar */}
            <aside className="space-y-6">
              {/* CTA */}
              <div className="bg-blue-600 rounded-2xl p-6 text-white">
                <h3 className="font-bold text-lg mb-2">¿Quieres aplicar esto en tu empresa?</h3>
                <p className="text-blue-100 text-sm mb-4">
                  Solicita un diagnóstico gratuito de 45 minutos y te diremos exactamente qué
                  tiene sentido implementar en tu caso concreto.
                </p>
                <Link
                  href="/diagnostico-gratuito"
                  className="inline-flex items-center gap-2 bg-white text-blue-700 font-semibold text-sm px-4 py-2.5 rounded-lg hover:bg-blue-50 transition-colors"
                >
                  Diagnóstico gratuito
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>

              {/* Related posts */}
              {related.length > 0 && (
                <div className="bg-white border border-slate-200 rounded-2xl p-6">
                  <h3 className="font-bold text-slate-900 mb-4">Artículos relacionados</h3>
                  <div className="space-y-4">
                    {related.map((rel) => (
                      <Link
                        key={rel.slug}
                        href={`/blog/${rel.slug}`}
                        className="group block"
                      >
                        <div className="flex items-start gap-2">
                          <ArrowRight className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0 group-hover:text-blue-600 transition-colors" />
                          <div>
                            <p className="text-sm font-medium text-slate-900 group-hover:text-blue-700 transition-colors leading-snug">
                              {rel.title}
                            </p>
                            <p className="text-xs text-slate-400 mt-0.5">{rel.category} · {rel.readTime} min</p>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}

              {/* Services CTA */}
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6">
                <h3 className="font-bold text-slate-900 mb-3">Nuestros servicios</h3>
                <ul className="space-y-2">
                  {[
                    { label: 'Auditoría IA', href: '/auditoria-ia' },
                    { label: 'Automatización de procesos', href: '/automatizacion-procesos' },
                    { label: 'Agentes IA', href: '/agentes-ia' },
                    { label: 'Consultor IA externo', href: '/consultor-ia-externo' },
                    { label: 'Formación en IA', href: '/formacion-ia' },
                  ].map((s) => (
                    <li key={s.href}>
                      <Link
                        href={s.href}
                        className="text-sm text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                      >
                        {s.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </>
  )
}
