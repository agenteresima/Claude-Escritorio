import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { blogPosts, getBlogPost, getRelatedPosts } from '@/lib/blog-data'
import { Calendar, Clock, ArrowRight, ArrowLeft, ChevronRight } from 'lucide-react'

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
    title: `${post.title} | AP Automatización IA`,
    description: post.description,
    alternates: { canonical: `https://www.automatizacionprocesos.es/blog/${post.slug}` },
    openGraph: {
      title: post.title,
      description: post.description,
      url: `https://www.automatizacionprocesos.es/blog/${post.slug}`,
      type: 'article',
      publishedTime: post.date,
      authors: ['AP Automatización IA'],
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
      name: 'AP Automatización IA',
      url: 'https://www.automatizacionprocesos.es',
    },
    publisher: {
      '@type': 'Organization',
      name: 'AP Automatización IA',
      url: 'https://www.automatizacionprocesos.es',
    },
    url: `https://www.automatizacionprocesos.es/blog/${post.slug}`,
  }

  return (
    <>
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
                <div className="p-8 border-b border-slate-100">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-full">
                      {post.category}
                    </span>
                    <div className="flex items-center gap-1 text-xs text-slate-400">
                      <Clock className="h-3 w-3" />
                      {post.readTime} min de lectura
                    </div>
                  </div>
                  <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4 leading-tight">
                    {post.title}
                  </h1>
                  <p className="text-lg text-slate-600 leading-relaxed mb-4">
                    {post.description}
                  </p>
                  <div className="flex items-center gap-2 text-sm text-slate-400">
                    <Calendar className="h-4 w-4" />
                    {formatDate(post.date)} · Por {post.author}
                  </div>
                </div>
                <div className="p-8">
                  <div
                    className="prose prose-lg prose-slate max-w-none
                      prose-headings:font-bold prose-headings:text-slate-900
                      prose-h2:text-2xl prose-h2:mt-8 prose-h2:mb-4
                      prose-h3:text-xl prose-h3:mt-6 prose-h3:mb-3
                      prose-p:text-slate-600 prose-p:leading-relaxed
                      prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline
                      prose-strong:text-slate-900
                      prose-ul:text-slate-600 prose-ol:text-slate-600
                      prose-li:my-1"
                    dangerouslySetInnerHTML={{ __html: post.content }}
                  />
                </div>
              </div>

              {/* Back to blog */}
              <div className="mt-6">
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
