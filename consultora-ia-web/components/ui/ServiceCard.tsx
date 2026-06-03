import Link from 'next/link'
import { ArrowRight, Check, type LucideIcon } from 'lucide-react'

interface ServiceCardProps {
  icon: LucideIcon
  title: string
  description: string
  href: string
  highlights?: string[]
}

export default function ServiceCard({
  icon: Icon,
  title,
  description,
  href,
  highlights,
}: ServiceCardProps) {
  return (
    <div className="group relative flex flex-col bg-white border border-gray-200 rounded-2xl p-6 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/8 hover:-translate-y-1 hover:border-blue-200">
      {/* Icon */}
      <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-50 rounded-xl mb-5 group-hover:bg-blue-100 transition-colors">
        <Icon className="w-6 h-6 text-blue-600" />
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-3 group-hover:text-blue-700 transition-colors">
        {title}
      </h3>

      {/* Description */}
      <p className="text-sm text-gray-500 leading-relaxed mb-5 flex-1">
        {description}
      </p>

      {/* Highlights */}
      {highlights && highlights.length > 0 && (
        <ul className="space-y-2 mb-6">
          {highlights.map((item, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
              <Check className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )}

      {/* CTA */}
      <Link
        href={href}
        className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 mt-auto group/link"
      >
        Saber más
        <ArrowRight className="w-4 h-4 transition-transform group-hover/link:translate-x-1" />
      </Link>
    </div>
  )
}
