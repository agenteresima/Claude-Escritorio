import Link from 'next/link'
import { Check, Star } from 'lucide-react'

interface PricingCardProps {
  name: string
  price: string
  period: string
  description: string
  features: string[]
  cta: string
  href: string
  highlighted?: boolean
}

export default function PricingCard({
  name,
  price,
  period,
  description,
  features,
  cta,
  href,
  highlighted = false,
}: PricingCardProps) {
  return (
    <div
      className={`relative flex flex-col rounded-2xl p-7 transition-all duration-300 ${
        highlighted
          ? 'bg-blue-600 border-2 border-blue-500 shadow-2xl shadow-blue-500/25 scale-[1.02]'
          : 'bg-white border border-gray-200 hover:shadow-lg hover:shadow-gray-200/80 hover:-translate-y-0.5'
      }`}
    >
      {/* Popular badge */}
      {highlighted && (
        <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
          <span className="inline-flex items-center gap-1 bg-amber-400 text-amber-900 text-xs font-bold px-3 py-1 rounded-full shadow-sm">
            <Star className="w-3 h-3 fill-current" />
            Más popular
          </span>
        </div>
      )}

      {/* Plan name */}
      <p
        className={`text-sm font-semibold uppercase tracking-wider mb-4 ${
          highlighted ? 'text-blue-200' : 'text-blue-600'
        }`}
      >
        {name}
      </p>

      {/* Price */}
      <div className="mb-4">
        <div className="flex items-end gap-1.5">
          <span
            className={`text-4xl font-bold ${highlighted ? 'text-white' : 'text-gray-900'}`}
          >
            {price}
          </span>
          <span
            className={`text-sm mb-1.5 ${highlighted ? 'text-blue-200' : 'text-gray-400'}`}
          >
            {period}
          </span>
        </div>
      </div>

      {/* Description */}
      <p
        className={`text-sm leading-relaxed mb-6 ${
          highlighted ? 'text-blue-100' : 'text-gray-500'
        }`}
      >
        {description}
      </p>

      {/* CTA */}
      <Link
        href={href}
        className={`block w-full text-center py-3 px-5 rounded-xl text-sm font-semibold transition-all duration-200 mb-7 ${
          highlighted
            ? 'bg-white text-blue-600 hover:bg-blue-50 shadow-sm'
            : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
        }`}
      >
        {cta}
      </Link>

      {/* Features */}
      <ul className="space-y-3 flex-1">
        {features.map((feature, i) => (
          <li key={i} className="flex items-start gap-2.5">
            <div
              className={`mt-0.5 shrink-0 flex items-center justify-center w-4 h-4 rounded-full ${
                highlighted ? 'bg-blue-400/30' : 'bg-blue-50'
              }`}
            >
              <Check
                className={`w-2.5 h-2.5 ${highlighted ? 'text-white' : 'text-blue-600'}`}
              />
            </div>
            <span
              className={`text-sm leading-snug ${
                highlighted ? 'text-blue-50' : 'text-gray-600'
              }`}
            >
              {feature}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
