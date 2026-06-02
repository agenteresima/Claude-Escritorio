import { cn } from '@/lib/utils'

interface CardProps {
  variant?: 'default' | 'elevated' | 'outlined' | 'filled' | 'glass' | 'dark'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
  className?: string
  children: React.ReactNode
  onClick?: () => void
  as?: 'div' | 'article' | 'section' | 'li'
}

const variantClasses: Record<NonNullable<CardProps['variant']>, string> = {
  default: 'bg-white border border-surface-200 shadow-card',
  elevated: 'bg-white shadow-card-hover',
  outlined: 'bg-white border border-surface-200',
  filled: 'bg-surface-50 border border-surface-200',
  glass: 'bg-white/80 backdrop-blur-sm border border-white/20',
  dark: 'bg-navy-800 border border-white/10 text-white',
}

const paddingClasses: Record<NonNullable<CardProps['padding']>, string> = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

export default function Card({
  variant = 'default',
  padding = 'md',
  hover = false,
  className,
  children,
  onClick,
  as: Component = 'div',
}: CardProps) {
  return (
    <Component
      className={cn(
        'rounded-2xl transition-all duration-300',
        variantClasses[variant],
        paddingClasses[padding],
        hover && 'hover:shadow-card-hover hover:-translate-y-1',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </Component>
  )
}

// Sub-componentes de Card para composición flexible
Card.Header = function CardHeader({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className={cn('mb-4', className)}>
      {children}
    </div>
  )
}

Card.Body = function CardBody({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className={cn('', className)}>
      {children}
    </div>
  )
}

Card.Footer = function CardFooter({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className={cn('mt-4 pt-4 border-t border-surface-100', className)}>
      {children}
    </div>
  )
}

Card.Title = function CardTitle({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <h3 className={cn('text-lg font-semibold text-navy-900', className)}>
      {children}
    </h3>
  )
}

Card.Description = function CardDescription({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <p className={cn('text-navy-500 text-sm leading-relaxed mt-1', className)}>
      {children}
    </p>
  )
}
