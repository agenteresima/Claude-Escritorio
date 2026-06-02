import { cn } from '@/lib/utils'

interface SectionProps {
  id?: string
  title?: string
  subtitle?: string
  badge?: string
  description?: string
  centered?: boolean
  dark?: boolean
  className?: string
  contentClassName?: string
  children: React.ReactNode
  as?: 'section' | 'div' | 'article'
  noPadding?: boolean
}

export default function Section({
  id,
  title,
  subtitle,
  badge,
  description,
  centered = false,
  dark = false,
  className,
  contentClassName,
  children,
  as: Component = 'section',
  noPadding = false,
}: SectionProps) {
  return (
    <Component
      id={id}
      className={cn(
        !noPadding && 'section-padding',
        dark && 'bg-navy-900 text-white',
        !dark && 'bg-surface-50',
        className
      )}
    >
      <div className={cn('container-main', contentClassName)}>
        {/* Encabezado de sección */}
        {(badge || title || subtitle || description) && (
          <div
            className={cn(
              'mb-12 md:mb-16',
              centered && 'text-center',
              !centered && 'max-w-2xl'
            )}
          >
            {badge && (
              <div className={cn('mb-4', centered && 'flex justify-center')}>
                <span
                  className={cn(
                    'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider',
                    dark
                      ? 'bg-brand-600/20 text-brand-300 border border-brand-600/30'
                      : 'bg-brand-50 text-brand-700 border border-brand-100'
                  )}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-500" />
                  {badge}
                </span>
              </div>
            )}
            {title && (
              <h2
                className={cn(
                  'font-bold tracking-tight',
                  dark ? 'text-white' : 'text-navy-900',
                  subtitle && 'mb-2'
                )}
              >
                {title}
              </h2>
            )}
            {subtitle && (
              <p
                className={cn(
                  'text-xl md:text-2xl font-medium mb-4',
                  dark ? 'text-brand-300' : 'text-brand-600'
                )}
              >
                {subtitle}
              </p>
            )}
            {description && (
              <p
                className={cn(
                  'text-lg leading-relaxed',
                  dark ? 'text-navy-300' : 'text-navy-500'
                )}
              >
                {description}
              </p>
            )}
          </div>
        )}

        {/* Contenido de la sección */}
        {children}
      </div>
    </Component>
  )
}
