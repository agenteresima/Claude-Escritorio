import Link from 'next/link'
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  href?: string
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  external?: boolean
  className?: string
  children: React.ReactNode
}

const variantClasses: Record<NonNullable<ButtonProps['variant']>, string> = {
  primary: [
    'bg-brand-600 text-white',
    'hover:bg-brand-500 active:bg-brand-700',
    'shadow-brand-sm hover:shadow-brand',
    'focus-visible:ring-brand-500',
  ].join(' '),
  secondary: [
    'bg-navy-800 text-white',
    'hover:bg-navy-700 active:bg-navy-900',
    'focus-visible:ring-navy-600',
  ].join(' '),
  outline: [
    'bg-transparent text-brand-600 border border-brand-600',
    'hover:bg-brand-50 active:bg-brand-100',
    'focus-visible:ring-brand-500',
  ].join(' '),
  ghost: [
    'bg-transparent text-navy-700',
    'hover:bg-surface-100 active:bg-surface-200',
    'focus-visible:ring-navy-400',
  ].join(' '),
  danger: [
    'bg-red-600 text-white',
    'hover:bg-red-500 active:bg-red-700',
    'focus-visible:ring-red-500',
  ].join(' '),
}

const sizeClasses: Record<NonNullable<ButtonProps['size']>, string> = {
  sm: 'h-9 px-4 text-sm rounded-lg gap-1.5',
  md: 'h-11 px-6 text-sm rounded-xl gap-2',
  lg: 'h-13 px-8 text-base rounded-xl gap-2.5',
}

export default function Button({
  variant = 'primary',
  size = 'md',
  href,
  loading = false,
  leftIcon,
  rightIcon,
  external = false,
  className,
  children,
  disabled,
  ...props
}: ButtonProps) {
  const baseClasses = cn(
    'inline-flex items-center justify-center font-semibold',
    'transition-all duration-200 cursor-pointer select-none',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
    variantClasses[variant],
    sizeClasses[size],
    className
  )

  const content = (
    <>
      {loading ? (
        <svg
          className="animate-spin w-4 h-4 mr-1"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      ) : (
        leftIcon
      )}
      {children}
      {!loading && rightIcon}
    </>
  )

  if (href) {
    const linkProps = external
      ? { target: '_blank', rel: 'noopener noreferrer' }
      : {}

    return (
      <Link href={href} className={baseClasses} {...linkProps}>
        {content}
      </Link>
    )
  }

  return (
    <button className={baseClasses} disabled={disabled || loading} {...props}>
      {content}
    </button>
  )
}
