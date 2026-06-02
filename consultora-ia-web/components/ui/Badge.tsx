import { cn } from '@/lib/utils'

interface BadgeProps {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'outline' | 'dark'
  size?: 'sm' | 'md'
  dot?: boolean
  className?: string
  children: React.ReactNode
}

const variantClasses: Record<NonNullable<BadgeProps['variant']>, string> = {
  default: 'bg-surface-100 text-navy-600 border border-surface-200',
  primary: 'bg-brand-100 text-brand-700 border border-brand-200',
  success: 'bg-success-500/10 text-success-600 border border-success-500/20',
  warning: 'bg-amber-100 text-amber-700 border border-amber-200',
  danger: 'bg-red-100 text-red-700 border border-red-200',
  outline: 'bg-transparent text-navy-600 border border-surface-300',
  dark: 'bg-navy-800 text-navy-100 border border-white/10',
}

const dotColors: Record<NonNullable<BadgeProps['variant']>, string> = {
  default: 'bg-navy-400',
  primary: 'bg-brand-500',
  success: 'bg-success-500',
  warning: 'bg-amber-500',
  danger: 'bg-red-500',
  outline: 'bg-navy-400',
  dark: 'bg-navy-300',
}

const sizeClasses: Record<NonNullable<BadgeProps['size']>, string> = {
  sm: 'px-2 py-0.5 text-xs rounded-md gap-1',
  md: 'px-3 py-1 text-xs rounded-lg gap-1.5',
}

export default function Badge({
  variant = 'default',
  size = 'md',
  dot = false,
  className,
  children,
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center font-medium whitespace-nowrap',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full flex-shrink-0',
            dotColors[variant],
            variant === 'success' && 'animate-pulse'
          )}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  )
}
