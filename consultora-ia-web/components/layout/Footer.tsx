'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  Linkedin,
  Twitter,
  Youtube,
  Mail,
  MapPin,
  ArrowRight,
  CheckCircle,
} from 'lucide-react'
import LogoIcon from '@/components/ui/LogoIcon'
import { cn } from '@/lib/utils'
import { COMPANY_INFO } from '@/lib/constants'

const footerLinks = {
  servicios: [
    { label: 'Automatización de procesos', href: '/servicios/automatizacion-procesos' },
    { label: 'Agentes de IA', href: '/servicios/agentes-ia' },
    { label: 'Chatbots inteligentes', href: '/servicios/chatbots-inteligentes' },
    { label: 'Formación en IA', href: '/servicios/formacion-ia' },
    { label: 'Estrategia de IA', href: '/servicios/estrategia-ia' },
    { label: 'Análisis de datos con IA', href: '/servicios/analisis-datos-ia' },
  ],
  recursos: [
    { label: 'Blog de IA', href: '/blog' },
    { label: 'Casos de éxito', href: '/casos-de-exito' },
    { label: 'Diagnóstico gratuito', href: '/diagnostico-gratuito' },
    { label: 'Precios', href: '/precios' },
    { label: 'Sobre nosotros', href: '/sobre-nosotros' },
    { label: 'FAQ', href: '/#faq' },
  ],
  legal: [
    { label: 'Política de privacidad', href: '/privacidad' },
    { label: 'Términos y condiciones', href: '/terminos' },
    { label: 'Política de cookies', href: '/cookies' },
    { label: 'Aviso legal', href: '/aviso-legal' },
  ],
}

export default function Footer() {
  const [email, setEmail] = useState('')
  const [subscribed, setSubscribed] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || subscribed) return
    setLoading(true)

    try {
      const response = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      if (response.ok) {
        setSubscribed(true)
        setEmail('')
      }
    } catch (error) {
      console.error('Error suscripción newsletter:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <footer className="bg-navy-900 text-white">
      {/* Franja superior — newsletter */}
      <div className="border-b border-white/10">
        <div className="container-main py-12">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
            <div className="max-w-md">
              <h3 className="text-xl font-semibold text-white mb-2">
                Aprende IA aplicada cada semana
              </h3>
              <p className="text-navy-300 text-sm">
                Guías prácticas, casos reales y las últimas tendencias en IA empresarial. Sin spam,
                solo contenido de valor.
              </p>
            </div>
            <form
              onSubmit={handleNewsletterSubmit}
              className="flex w-full md:w-auto gap-2 max-w-md"
            >
              {subscribed ? (
                <div className="flex items-center gap-2 text-success-400 bg-success-500/10 px-4 py-2.5 rounded-xl">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">¡Suscrito correctamente!</span>
                </div>
              ) : (
                <>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="tu@empresa.es"
                    required
                    className="flex-1 min-w-0 bg-white/10 border border-white/20 text-white placeholder-white/40 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className={cn(
                      'flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold rounded-xl transition-colors whitespace-nowrap',
                      loading && 'opacity-70 cursor-not-allowed'
                    )}
                  >
                    {loading ? 'Enviando...' : 'Suscribirme'}
                    {!loading && <ArrowRight className="w-4 h-4" />}
                  </button>
                </>
              )}
            </form>
          </div>
        </div>
      </div>

      {/* Cuerpo principal del footer */}
      <div className="container-main py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-10">
          {/* Columna empresa */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <LogoIcon size={40} />
              <span className="font-bold text-xl text-white">Automatización Procesos IA</span>
            </Link>
            <p className="text-navy-300 text-sm leading-relaxed mb-6 max-w-sm">
              {COMPANY_INFO.descripcion}
            </p>

            {/* Datos de contacto */}
            <ul className="space-y-3 mb-8">
              <li>
                <a
                  href={`mailto:${COMPANY_INFO.email}`}
                  className="flex items-center gap-2.5 text-navy-300 hover:text-white text-sm transition-colors"
                >
                  <Mail className="w-4 h-4 text-brand-400 flex-shrink-0" />
                  {COMPANY_INFO.email}
                </a>
              </li>
<li>
                <span className="flex items-center gap-2.5 text-navy-300 text-sm">
                  <MapPin className="w-4 h-4 text-brand-400 flex-shrink-0" />
                  {COMPANY_INFO.ciudad}, {COMPANY_INFO.pais}
                </span>
              </li>
            </ul>

            {/* Redes sociales */}
            <div className="flex items-center gap-3">
              {COMPANY_INFO.redes_sociales.linkedin && (
                <a
                  href={COMPANY_INFO.redes_sociales.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="LinkedIn Automatización Procesos IA"
                  className="flex items-center justify-center w-9 h-9 bg-white/10 hover:bg-brand-600 rounded-lg transition-colors"
                >
                  <Linkedin className="w-4 h-4" />
                </a>
              )}
              {COMPANY_INFO.redes_sociales.twitter && (
                <a
                  href={COMPANY_INFO.redes_sociales.twitter}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Twitter Automatización Procesos IA"
                  className="flex items-center justify-center w-9 h-9 bg-white/10 hover:bg-brand-600 rounded-lg transition-colors"
                >
                  <Twitter className="w-4 h-4" />
                </a>
              )}
              {COMPANY_INFO.redes_sociales.youtube && (
                <a
                  href={COMPANY_INFO.redes_sociales.youtube}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="YouTube Automatización Procesos IA"
                  className="flex items-center justify-center w-9 h-9 bg-white/10 hover:bg-brand-600 rounded-lg transition-colors"
                >
                  <Youtube className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>

          {/* Columna servicios */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-5">
              Servicios
            </h4>
            <ul className="space-y-3">
              {footerLinks.servicios.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-navy-300 hover:text-white text-sm transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Columna recursos */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-5">
              Recursos
            </h4>
            <ul className="space-y-3">
              {footerLinks.recursos.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-navy-300 hover:text-white text-sm transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Columna legal */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-5">
              Legal
            </h4>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-navy-300 hover:text-white text-sm transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>

            {/* Certificaciones / badges */}
            <div className="mt-8">
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-success-500/10 border border-success-500/20 rounded-lg">
                <span className="w-2 h-2 rounded-full bg-success-500 animate-pulse-slow" />
                <span className="text-xs text-success-400 font-medium">RGPD Compliant</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Barra de copyright */}
      <div className="border-t border-white/10">
        <div className="container-main py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-navy-400 text-sm text-center sm:text-left">
              &copy; {new Date().getFullYear()} {COMPANY_INFO.nombre}. Todos los derechos
              reservados.
            </p>
            <p className="text-navy-500 text-xs">
              Hecho con IA en Valencia, España
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
