import Link from 'next/link'
import { Calendar, Clock, ArrowRight } from 'lucide-react'

interface BlogCardProps {
  slug: string
  title: string
  description: string
  date: string
  category: string
  readTime: number
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
}

const categoryColors: Record<string, string> = {
  'Estrategia IA': 'bg-blue-50 text-blue-700 border border-blue-100',
  'Automatización': 'bg-emerald-50 text-emerald-700 border border-emerald-100',
  'Herramientas IA': 'bg-purple-50 text-purple-700 border border-purple-100',
  'Agentes IA': 'bg-orange-50 text-orange-700 border border-orange-100',
  'Tecnología': 'bg-cyan-50 text-cyan-700 border border-cyan-100',
  'Consultoría': 'bg-rose-50 text-rose-700 border border-rose-100',
}

export default function BlogCard({
  slug,
  title,
  description,
  date,
  category,
  readTime,
}: BlogCardProps) {
  const colorClass = categoryColors[category] ?? 'bg-gray-50 text-gray-700 border border-gray-100'

  return (
    <Link href={`/blog/${slug}`} className="group block h-full">
      <article className="h-full flex flex-col bg-white border border-gray-200 rounded-2xl p-6 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/5 hover:-translate-y-0.5 hover:border-blue-100">
        {/* Category badge */}
        <div className="mb-4">
          <span className={`inline-block text-xs font-semibold px-3 py-1 rounded-full ${colorClass}`}>
            {category}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-base font-semibold text-gray-900 leading-snug mb-3 group-hover:text-blue-600 transition-colors line-clamp-2">
          {title}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-500 leading-relaxed mb-5 flex-1 line-clamp-3">
          {description}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center gap-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              {formatDate(date)}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {readTime} min
            </span>
          </div>
          <span className="flex items-center gap-1 text-xs font-medium text-blue-600 group-hover:gap-2 transition-all">
            Leer
            <ArrowRight className="w-3.5 h-3.5" />
          </span>
        </div>
      </article>
    </Link>
  )
}
