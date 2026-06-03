'use client'

import { useState, type FormEvent } from 'react'
import { Send, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

type FormState = 'idle' | 'loading' | 'success' | 'error'

export default function NewsletterForm() {
  const [email, setEmail] = useState('')
  const [state, setState] = useState<FormState>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!email || state === 'loading') return

    setState('loading')
    setErrorMessage('')

    try {
      const res = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.error || 'Error al procesar la suscripción')
      }

      setState('success')
      setEmail('')
    } catch (err) {
      setState('error')
      setErrorMessage(err instanceof Error ? err.message : 'Error inesperado. Por favor, inténtalo de nuevo.')
    }
  }

  if (state === 'success') {
    return (
      <div className="flex items-center gap-3 p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
        <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0" />
        <div>
          <p className="text-sm font-medium text-emerald-800">¡Suscripción confirmada!</p>
          <p className="text-xs text-emerald-600 mt-0.5">
            Recibirás el próximo artículo directamente en tu bandeja de entrada.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <p className="text-xs text-gray-400 mb-3">
        Artículos sobre IA para empresas, sin spam. Cada 2 semanas.
      </p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="tu@empresa.com"
          required
          disabled={state === 'loading'}
          className="flex-1 min-w-0 bg-white border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-60 disabled:cursor-not-allowed transition-all"
        />
        <button
          type="submit"
          disabled={state === 'loading' || !email}
          className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2.5 text-sm font-medium transition-all shrink-0"
        >
          {state === 'loading' ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">Suscribirme</span>
            </>
          )}
        </button>
      </form>
      {state === 'error' && (
        <div className="flex items-center gap-2 mt-2">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
          <p className="text-xs text-red-600">{errorMessage}</p>
        </div>
      )}
    </div>
  )
}
