import { Star } from 'lucide-react'

interface TestimonialCardProps {
  name: string
  role: string
  company: string
  sector: string
  text: string
  rating?: number
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase()
}

const sectorColors: Record<string, string> = {
  'industria': 'bg-slate-100 text-slate-600',
  'retail': 'bg-amber-50 text-amber-700',
  'servicios': 'bg-blue-50 text-blue-700',
  'salud': 'bg-emerald-50 text-emerald-700',
  'legal': 'bg-purple-50 text-purple-700',
  'logística': 'bg-orange-50 text-orange-700',
}

export default function TestimonialCard({
  name,
  role,
  company,
  sector,
  text,
  rating,
}: TestimonialCardProps) {
  const initials = getInitials(name)
  const sectorColor = sectorColors[sector.toLowerCase()] ?? 'bg-gray-100 text-gray-600'

  return (
    <div className="flex flex-col bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-md hover:shadow-gray-200/80 transition-all duration-300">
      {/* Opening quotes */}
      <div className="text-5xl font-serif text-blue-100 leading-none mb-3 select-none" aria-hidden>
        &ldquo;
      </div>

      {/* Stars */}
      {rating !== undefined && (
        <div className="flex gap-0.5 mb-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Star
              key={i}
              className={`w-4 h-4 ${i < rating ? 'text-amber-400 fill-amber-400' : 'text-gray-200 fill-gray-200'}`}
            />
          ))}
        </div>
      )}

      {/* Quote text */}
      <blockquote className="text-sm text-gray-700 leading-relaxed flex-1 mb-5">
        {text}
      </blockquote>

      {/* Author */}
      <div className="flex items-center gap-3 pt-4 border-t border-gray-100">
        {/* Avatar */}
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shrink-0">
          <span className="text-white text-xs font-bold">{initials}</span>
        </div>

        {/* Info */}
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-gray-900 leading-tight truncate">{name}</p>
          <p className="text-xs text-gray-500 leading-tight truncate">
            {role} · {company}
          </p>
        </div>

        {/* Sector badge */}
        <span className={`shrink-0 text-xs font-medium px-2.5 py-1 rounded-full ${sectorColor}`}>
          {sector}
        </span>
      </div>
    </div>
  )
}
