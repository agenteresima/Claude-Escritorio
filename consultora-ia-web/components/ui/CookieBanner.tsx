'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { X } from 'lucide-react'

type ConsentType = 'all' | 'necessary' | null

export default function CookieBanner() {
  const [visible, setVisible] = useState(false)
  const [showManage, setShowManage] = useState(false)
  const [analyticsEnabled, setAnalyticsEnabled] = useState(true)
  const [marketingEnabled, setMarketingEnabled] = useState(false)

  useEffect(() => {
    const consent = localStorage.getItem('cookie-consent')
    if (!consent) {
      setVisible(true)
    }
  }, [])

  const saveConsent = (type: ConsentType) => {
    localStorage.setItem('cookie-consent', type as string)
    localStorage.setItem('cookie-consent-date', new Date().toISOString())
    setVisible(false)
  }

  const handleAcceptAll = () => {
    saveConsent('all')
  }

  const handleNecessaryOnly = () => {
    saveConsent('necessary')
  }

  const handleSavePreferences = () => {
    const preference = analyticsEnabled || marketingEnabled ? 'all' : 'necessary'
    saveConsent(preference)
  }

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed bottom-0 left-0 right-0 z-50 p-4 sm:p-6"
        >
          <div className="mx-auto max-w-5xl bg-white border border-gray-200 rounded-2xl shadow-2xl p-5 sm:p-6">
            {!showManage ? (
              <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 leading-relaxed">
                    Utilizamos cookies propias y de terceros para analizar el uso de nuestra web y mejorar nuestros
                    servicios. Puedes aceptarlas todas, solo las necesarias o gestionar tus preferencias.{' '}
                    <Link href="/cookies" className="text-blue-600 hover:underline font-medium">
                      Política de cookies
                    </Link>
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2 shrink-0">
                  <button
                    onClick={() => setShowManage(true)}
                    className="text-sm text-gray-500 hover:text-gray-700 underline-offset-2 hover:underline px-1 py-1.5 transition-colors"
                  >
                    Gestionar
                  </button>
                  <button
                    onClick={handleNecessaryOnly}
                    className="text-sm border border-gray-300 text-gray-700 hover:border-gray-400 hover:bg-gray-50 rounded-lg px-4 py-2 transition-colors whitespace-nowrap"
                  >
                    Solo necesarias
                  </button>
                  <button
                    onClick={handleAcceptAll}
                    className="text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium transition-colors whitespace-nowrap"
                  >
                    Aceptar todas
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-semibold text-gray-900">Gestionar preferencias de cookies</h3>
                  <button
                    onClick={() => setShowManage(false)}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                    aria-label="Cerrar"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <div className="space-y-3 mb-5">
                  <div className="flex items-center justify-between py-3 border-b border-gray-100">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Cookies necesarias</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        Imprescindibles para el funcionamiento básico del sitio.
                      </p>
                    </div>
                    <span className="text-xs text-gray-400 font-medium">Siempre activas</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-gray-100">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Cookies analíticas</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        Nos ayudan a entender cómo se usa la web (Google Analytics, Vercel Analytics).
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={analyticsEnabled}
                        onChange={(e) => setAnalyticsEnabled(e.target.checked)}
                      />
                      <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Cookies de marketing</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        Permiten mostrarte publicidad relevante en otras plataformas.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={marketingEnabled}
                        onChange={(e) => setMarketingEnabled(e.target.checked)}
                      />
                      <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 justify-end">
                  <button
                    onClick={handleNecessaryOnly}
                    className="text-sm border border-gray-300 text-gray-700 hover:border-gray-400 rounded-lg px-4 py-2 transition-colors"
                  >
                    Solo necesarias
                  </button>
                  <button
                    onClick={handleSavePreferences}
                    className="text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium transition-colors"
                  >
                    Guardar preferencias
                  </button>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
