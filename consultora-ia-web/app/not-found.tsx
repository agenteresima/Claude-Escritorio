import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Página no encontrada | AP Automatización IA',
  description: 'La página que buscas no existe. Vuelve a la página principal de AP Automatización IA.',
  robots: { index: false, follow: false },
}

export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="max-w-lg w-full text-center">
        <div className="mb-8">
          <span className="text-8xl font-bold text-blue-600">404</span>
        </div>
        <h1 className="text-3xl font-bold text-slate-900 mb-4">
          Esta página no existe
        </h1>
        <p className="text-slate-600 text-lg mb-8">
          La dirección que has introducido no corresponde a ninguna página de
          AP Automatización IA. Es posible que haya sido movida o eliminada.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Volver al inicio
          </Link>
          <Link
            href="/servicios"
            className="inline-flex items-center justify-center px-6 py-3 border border-slate-300 text-slate-700 font-semibold rounded-lg hover:bg-slate-100 transition-colors"
          >
            Ver servicios
          </Link>
        </div>
        <p className="mt-8 text-sm text-slate-500">
          ¿Necesitas ayuda?{' '}
          <Link href="/contacto" className="text-blue-600 hover:underline">
            Contáctanos
          </Link>
        </p>
      </div>
    </div>
  )
}
