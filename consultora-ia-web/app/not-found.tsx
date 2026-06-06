import Link from 'next/link'
import { Home, Zap, BookOpen, MessageSquare } from 'lucide-react'

const quickLinks = [
  {
    label: 'Ver nuestros servicios',
    href: '/servicios',
    icon: Zap,
    description: 'Automatización, agentes IA y consultoría',
  },
  {
    label: 'Leer el blog de IA',
    href: '/blog',
    icon: BookOpen,
    description: 'Guías y casos prácticos de IA empresarial',
  },
  {
    label: 'Contactar con nosotros',
    href: '/contacto',
    icon: MessageSquare,
    description: 'Resolvemos tus dudas sin compromiso',
  },
]

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex flex-col items-center justify-center text-white px-6 py-16">
      <div className="max-w-2xl w-full text-center">
        {/* 404 number */}
        <div className="text-9xl font-black text-blue-400 leading-none mb-4">404</div>

        {/* Heading */}
        <h1 className="text-3xl md:text-4xl font-bold mb-4">Esta página no existe</h1>

        {/* Description */}
        <p className="text-slate-300 text-lg mb-12 max-w-lg mx-auto">
          Parece que la página que buscas ha sido movida, eliminada o nunca existió. No te
          preocupes, te ayudamos a encontrar lo que necesitas.
        </p>

        {/* Quick links grid */}
        <div className="grid sm:grid-cols-3 gap-4 mb-10">
          {quickLinks.map((link) => {
            const Icon = link.icon
            return (
              <Link
                key={link.href}
                href={link.href}
                className="flex flex-col items-center gap-3 bg-white/10 hover:bg-white/20 border border-white/10 hover:border-white/20 rounded-xl p-5 transition-all group"
              >
                <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center group-hover:bg-blue-500/30 transition-colors">
                  <Icon className="w-5 h-5 text-blue-300" />
                </div>
                <div>
                  <div className="font-semibold text-sm text-white mb-1">{link.label}</div>
                  <div className="text-xs text-slate-400">{link.description}</div>
                </div>
              </Link>
            )
          })}
        </div>

        {/* Main CTA */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold px-8 py-4 rounded-xl transition-colors text-lg"
        >
          <Home className="w-5 h-5" />
          Volver al inicio
        </Link>
      </div>
    </div>
  )
}
