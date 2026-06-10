'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Menu,
  X,
  ChevronDown,
  Zap,
  Bot,
  MessageSquare,
  GraduationCap,
  Target,
  BarChart3,
  Sparkles,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { NAV_ITEMS } from '@/lib/constants'
import Button from '@/components/ui/Button'

const serviceIcons: Record<string, React.ReactNode> = {
  '/servicios/automatizacion-procesos': <Zap className="w-5 h-5 text-brand-500" />,
  '/servicios/agentes-ia': <Bot className="w-5 h-5 text-accent-purple" />,
  '/servicios/chatbots-inteligentes': <MessageSquare className="w-5 h-5 text-accent-cyan" />,
  '/servicios/formacion-ia': <GraduationCap className="w-5 h-5 text-success-500" />,
  '/servicios/estrategia-ia': <Target className="w-5 h-5 text-accent-amber" />,
  '/servicios/analisis-datos-ia': <BarChart3 className="w-5 h-5 text-brand-400" />,
}

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const pathname = usePathname()

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    setMobileMenuOpen(false)
    setActiveDropdown(null)
  }, [pathname])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setActiveDropdown(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])


  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname.startsWith(href)
  }

  return (
    <>
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        isScrolled
          ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-surface-200'
          : 'bg-navy-900/20 backdrop-blur-sm'
      )}
    >
      <div className="container-main">
        <div className="flex items-center justify-between h-16 lg:h-18">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-2 flex-shrink-0 group"
            aria-label="Automatización Procesos IA — Inicio"
          >
            <div
              className={cn(
                'flex items-center justify-center w-9 h-9 rounded-xl transition-all duration-300',
                isScrolled
                  ? 'bg-brand-600 shadow-brand-sm'
                  : 'bg-brand-600/90 shadow-brand'
              )}
            >
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span
              className={cn(
                'font-bold text-xl tracking-tight transition-colors duration-300',
                isScrolled ? 'text-navy-900' : 'text-white'
              )}
            >
              Automatización Procesos IA
            </span>
          </Link>

          {/* Navegación desktop */}
          <nav className="hidden lg:flex items-center gap-1" ref={dropdownRef}>
            {NAV_ITEMS.map((item) => (
              <div key={item.href} className="relative">
                {item.hijos ? (
                  <button
                    className={cn(
                      'flex items-center gap-1 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                      isScrolled
                        ? 'text-navy-700 hover:text-navy-900 hover:bg-surface-100'
                        : 'text-white/80 hover:text-white hover:bg-white/10',
                      isActive(item.href) && (isScrolled ? 'text-brand-600' : 'text-brand-300')
                    )}
                    onClick={() =>
                      setActiveDropdown(activeDropdown === item.href ? null : item.href)
                    }
                    aria-expanded={activeDropdown === item.href}
                  >
                    {item.label}
                    <ChevronDown
                      className={cn(
                        'w-4 h-4 transition-transform duration-200',
                        activeDropdown === item.href && 'rotate-180'
                      )}
                    />
                  </button>
                ) : (
                  <Link
                    href={item.href}
                    className={cn(
                      'flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                      isScrolled
                        ? 'text-navy-700 hover:text-navy-900 hover:bg-surface-100'
                        : 'text-white/80 hover:text-white hover:bg-white/10',
                      isActive(item.href) && (isScrolled ? 'text-brand-600 bg-brand-50' : 'text-white')
                    )}
                  >
                    {item.label}
                  </Link>
                )}

                {/* Dropdown de servicios */}
                {item.hijos && activeDropdown === item.href && (
                  <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-[540px] bg-white rounded-2xl shadow-card-hover border border-surface-200 p-4 grid grid-cols-2 gap-1 animate-fade-in">
                    <div className="col-span-2 px-3 py-2 mb-1 border-b border-surface-100">
                      <p className="text-xs font-semibold text-navy-400 uppercase tracking-wider">
                        Nuestros servicios
                      </p>
                    </div>
                    {item.hijos.map((hijo) => (
                      <Link
                        key={hijo.href}
                        href={hijo.href}
                        className="flex items-start gap-3 px-3 py-3 rounded-xl hover:bg-surface-50 transition-colors group"
                        onClick={() => setActiveDropdown(null)}
                      >
                        <span className="mt-0.5 p-1.5 bg-surface-100 rounded-lg group-hover:bg-brand-50 transition-colors">
                          {serviceIcons[hijo.href]}
                        </span>
                        <div>
                          <p className="text-sm font-semibold text-navy-800 group-hover:text-brand-600 transition-colors">
                            {hijo.label}
                          </p>
                          {hijo.descripcion && (
                            <p className="text-xs text-navy-500 mt-0.5 leading-relaxed line-clamp-2">
                              {hijo.descripcion}
                            </p>
                          )}
                        </div>
                      </Link>
                    ))}
                    <div className="col-span-2 mt-2 pt-2 border-t border-surface-100 px-3">
                      <Link
                        href="/servicios"
                        className="flex items-center gap-2 text-sm text-brand-600 font-semibold hover:text-brand-700 transition-colors"
                        onClick={() => setActiveDropdown(null)}
                      >
                        Ver todos los servicios
                        <ChevronDown className="w-4 h-4 -rotate-90" />
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* CTA desktop */}
          <div className="hidden lg:flex items-center gap-3">
            <Button href="/diagnostico-gratuito" size="sm" variant="primary">
              Diagnóstico gratuito
            </Button>
          </div>

          {/* Botón hamburger mobile */}
          <button
            className={cn(
              'lg:hidden flex items-center justify-center w-10 h-10 rounded-lg transition-colors',
              isScrolled ? 'text-navy-700 hover:bg-surface-100' : 'text-white hover:bg-white/10'
            )}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label={mobileMenuOpen ? 'Cerrar menú' : 'Abrir menú'}
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>
    </header>

      {/* Menú mobile */}
      {mobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-x-0 top-16 bottom-0 bg-white z-[60] overflow-y-auto"
          style={{ WebkitOverflowScrolling: 'touch' }}
        >
          <div className="px-4 py-6 space-y-1">
            {NAV_ITEMS.map((item) => (
              <div key={item.href}>
                {item.hijos ? (
                  <div>
                    <button
                      className="w-full flex items-center justify-between px-4 py-3 rounded-xl text-navy-700 font-medium hover:bg-surface-50 transition-colors"
                      onClick={() =>
                        setActiveDropdown(activeDropdown === item.href ? null : item.href)
                      }
                    >
                      {item.label}
                      <ChevronDown
                        className={cn(
                          'w-5 h-5 transition-transform duration-200',
                          activeDropdown === item.href && 'rotate-180'
                        )}
                      />
                    </button>
                    {activeDropdown === item.href && (
                      <div className="pl-4 mt-1 space-y-1">
                        {item.hijos.map((hijo) => (
                          <Link
                            key={hijo.href}
                            href={hijo.href}
                            className="flex items-center gap-3 px-4 py-3 rounded-lg text-navy-600 hover:text-brand-600 hover:bg-brand-50 transition-colors text-sm"
                            onClick={() => setMobileMenuOpen(false)}
                          >
                            <span>{serviceIcons[hijo.href]}</span>
                            {hijo.label}
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <Link
                    href={item.href}
                    className={cn(
                      'block px-4 py-3 rounded-xl font-medium transition-colors',
                      isActive(item.href)
                        ? 'text-brand-600 bg-brand-50'
                        : 'text-navy-700 hover:bg-surface-50'
                    )}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {item.label}
                  </Link>
                )}
              </div>
            ))}

            <div className="pt-4 mt-4 border-t border-surface-200 space-y-3">
              <Button
                href="/diagnostico-gratuito"
                variant="primary"
                className="w-full justify-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                Solicitar diagnóstico gratuito
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
