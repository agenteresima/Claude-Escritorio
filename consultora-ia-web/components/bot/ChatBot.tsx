'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, MessageCircle, Send, Bot } from 'lucide-react'
import ChatMessage, { MessageData } from './ChatMessage'
import TypingIndicator from './TypingIndicator'

// ─── Tipos ────────────────────────────────────────────────────────────────────

type BotState = 'greeting' | 'qualifying' | 'collecting_data' | 'confirmed'

type StepId =
  | 'welcome'
  | 'company_size'
  | 'tools'
  | 'main_problem'
  | 'qualification'
  | 'collect_name'
  | 'collect_company'
  | 'collect_role'
  | 'collect_email'
  | 'collect_phone'
  | 'collect_availability'
  | 'confirmed'
  | 'more_info'

interface BotStep {
  id: StepId
  message: string
  options?: string[]
  multiSelect?: boolean
  freeInput?: boolean
  inputPlaceholder?: string
}

interface CollectedData {
  intent?: string
  companySize?: string
  toolsUsed?: string[]
  mainProblem?: string
  wantsCall?: boolean
  name?: string
  company?: string
  role?: string
  email?: string
  phone?: string
  availability?: string
}

// ─── Pasos del flujo ──────────────────────────────────────────────────────────

const STEPS: Record<StepId, BotStep> = {
  welcome: {
    id: 'welcome',
    message: '¡Hola! 👋 Soy el asistente de AP Automatización IA. ¿En qué puedo ayudarte hoy?',
    options: [
      'Quiero saber qué procesos puedo automatizar',
      'Necesito un agente IA',
      'Busco asesoramiento estratégico',
      'Quiero información sobre servicios',
      'Hablar con una persona',
    ],
  },
  company_size: {
    id: 'company_size',
    message: 'Perfecto. Para poder orientarte mejor, ¿cuántas personas trabajan en tu empresa?',
    options: ['1-10 empleados', '11-50 empleados', '51-200 empleados', 'Más de 200'],
  },
  tools: {
    id: 'tools',
    message: '¿Qué herramientas usáis actualmente? (puedes seleccionar varias)',
    options: [
      'ChatGPT/Claude/Gemini',
      'Microsoft 365/Copilot',
      'CRM (Salesforce, HubSpot...)',
      'ERP (SAP, Odoo...)',
      'Excel/Google Sheets',
      'n8n/Make/Zapier',
      'Notion/SharePoint',
      'Ninguna especialmente',
    ],
    multiSelect: true,
  },
  main_problem: {
    id: 'main_problem',
    message: '¿Cuál es el principal problema que quieres resolver?',
    options: [
      'Demasiado trabajo manual y repetitivo',
      'Falta de información actualizada para tomar decisiones',
      'Atención al cliente lenta o ineficiente',
      'Procesos administrativos lentos',
      'No sé por dónde empezar con la IA',
      'Otro',
    ],
  },
  qualification: {
    id: 'qualification',
    message:
      'Gracias, esto me ayuda mucho a entenderte mejor. ¿Te gustaría que un consultor de AP Automatización IA te contactara para una videollamada gratuita de 45 minutos?',
    options: ['Sí, me interesa', 'Prefiero más información primero'],
  },
  collect_name: {
    id: 'collect_name',
    message:
      'Perfecto. Necesito algunos datos para coordinar la llamada. ¿Cuál es tu nombre completo?',
    freeInput: true,
    inputPlaceholder: 'Tu nombre completo...',
  },
  collect_company: {
    id: 'collect_company',
    message: '¿Y el nombre de tu empresa?',
    freeInput: true,
    inputPlaceholder: 'Nombre de la empresa...',
  },
  collect_role: {
    id: 'collect_role',
    message: '¿Cuál es tu cargo o puesto?',
    freeInput: true,
    inputPlaceholder: 'Tu cargo...',
  },
  collect_email: {
    id: 'collect_email',
    message: '¿Cuál es tu email de contacto?',
    freeInput: true,
    inputPlaceholder: 'tu@email.com',
  },
  collect_phone: {
    id: 'collect_phone',
    message: '¿Tienes teléfono de contacto? (opcional — puedes saltar escribiendo "–")',
    freeInput: true,
    inputPlaceholder: '+34 600 000 000 (opcional)',
  },
  collect_availability: {
    id: 'collect_availability',
    message: '¿Cuándo tienes disponibilidad para la llamada?',
    options: ['Mañanas', 'Tardes', 'Flexible'],
  },
  confirmed: {
    id: 'confirmed',
    message:
      '¡Listo! 🎉 He registrado tu solicitud. Un consultor de AP Automatización IA se pondrá en contacto contigo en menos de 24 horas laborables. Mientras tanto, puedes explorar nuestros servicios o leer nuestro blog.',
    options: ['Ver servicios', 'Ir al blog', 'Cerrar chat'],
  },
  more_info: {
    id: 'more_info',
    message:
      'Por supuesto 😊. Puedes explorar todos nuestros servicios en la web. Si en algún momento deseas que te contactemos, estaré aquí para ayudarte.',
    options: ['Ver servicios', 'Cerrar chat'],
  },
}

// ─── Lógica de clasificación ──────────────────────────────────────────────────

function getQualification(intent?: string, wantsCall?: boolean): string {
  if (!wantsCall) return 'información'
  if (!intent) return 'no_cualificado'
  if (intent.includes('automatizar')) return 'automatización'
  if (intent.includes('agente')) return 'agentes_ia'
  if (intent.includes('asesoramiento')) return 'consultoría_ia'
  if (intent.includes('información')) return 'información'
  return 'no_cualificado'
}

// ─── Componente principal ─────────────────────────────────────────────────────

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false)
  const [botState, setBotState] = useState<BotState>('greeting')
  const [messages, setMessages] = useState<MessageData[]>([])
  const [currentStep, setCurrentStep] = useState<StepId>('welcome')
  const [isTyping, setIsTyping] = useState(false)
  const [selectedTools, setSelectedTools] = useState<string[]>([])
  const [inputValue, setInputValue] = useState('')
  const [collectedData, setCollectedData] = useState<CollectedData>({})
  const [hasUnread, setHasUnread] = useState(false)
  const [isSending, setIsSending] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping, scrollToBottom])

  // Mostrar primer mensaje al abrir
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      showBotMessage(STEPS.welcome.message)
      setHasUnread(false)
    }
    if (isOpen) setHasUnread(false)
  }, [isOpen]) // eslint-disable-line react-hooks/exhaustive-deps

  // Indicador de no leído tras 3s
  useEffect(() => {
    if (!isOpen) {
      const timer = setTimeout(() => setHasUnread(true), 3000)
      return () => clearTimeout(timer)
    }
  }, [isOpen])

  const showBotMessage = useCallback((text: string, delayMs = 600) => {
    setIsTyping(true)
    setTimeout(() => {
      setIsTyping(false)
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'bot',
          content: text,
          timestamp: new Date(),
        },
      ])
    }, delayMs)
  }, [])

  const addUserMessage = useCallback((text: string) => {
    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: 'user',
        content: text,
        timestamp: new Date(),
      },
    ])
  }, [])

  // ─── Gestión de opciones ────────────────────────────────────────────────────

  const handleOptionClick = useCallback(
    (option: string) => {
      const step = STEPS[currentStep]

      // Multi-select: herramientas
      if (step.multiSelect) {
        setSelectedTools((prev) =>
          prev.includes(option) ? prev.filter((t) => t !== option) : [...prev, option]
        )
        return
      }

      // Opciones de confirmación final
      if (option === 'Ver servicios') {
        window.location.href = '/servicios'
        return
      }
      if (option === 'Ir al blog') {
        window.location.href = '/blog'
        return
      }
      if (option === 'Cerrar chat') {
        setIsOpen(false)
        return
      }

      addUserMessage(option)
      advanceFlow(option)
    },
    [currentStep, addUserMessage] // eslint-disable-line react-hooks/exhaustive-deps
  )

  const handleMultiSelectConfirm = useCallback(() => {
    const tools = selectedTools.length > 0 ? selectedTools : ['Ninguna especialmente']
    addUserMessage(tools.join(', '))
    setCollectedData((prev) => ({ ...prev, toolsUsed: tools }))
    setSelectedTools([])
    nextStep('main_problem')
    setTimeout(() => showBotMessage(STEPS.main_problem.message), 800)
  }, [selectedTools, addUserMessage, showBotMessage]) // eslint-disable-line react-hooks/exhaustive-deps

  // ─── Avance del flujo ───────────────────────────────────────────────────────

  const advanceFlow = useCallback(
    (answer: string) => {
      switch (currentStep) {
        case 'welcome': {
          const intentMap: Record<string, string> = {
            'Quiero saber qué procesos puedo automatizar': 'automatizar',
            'Necesito un agente IA': 'agente',
            'Busco asesoramiento estratégico': 'asesoramiento',
            'Quiero información sobre servicios': 'información',
            'Hablar con una persona': 'persona',
          }
          const intent = intentMap[answer] ?? 'información'
          setCollectedData((prev) => ({ ...prev, intent }))
          setBotState('qualifying')

          const responseMsg =
            intent === 'persona'
              ? 'Claro, enseguida te pongo en contacto. Primero déjame recabar algo de información. ¿Cuántas personas trabajan en tu empresa?'
              : `Entendido. Para poder orientarte mejor, ¿cuántas personas trabajan en tu empresa?`

          nextStep('company_size')
          setTimeout(() => showBotMessage(responseMsg), 800)
          break
        }

        case 'company_size':
          setCollectedData((prev) => ({ ...prev, companySize: answer }))
          nextStep('tools')
          setTimeout(() => showBotMessage(STEPS.tools.message), 800)
          break

        case 'main_problem':
          setCollectedData((prev) => ({ ...prev, mainProblem: answer }))
          nextStep('qualification')
          setTimeout(() => showBotMessage(STEPS.qualification.message), 800)
          break

        case 'qualification':
          if (answer === 'Sí, me interesa') {
            setCollectedData((prev) => ({ ...prev, wantsCall: true }))
            setBotState('collecting_data')
            nextStep('collect_name')
            setTimeout(() => showBotMessage(STEPS.collect_name.message), 800)
          } else {
            setCollectedData((prev) => ({ ...prev, wantsCall: false }))
            nextStep('more_info')
            setTimeout(() => showBotMessage(STEPS.more_info.message), 800)
            // Guardar lead sin datos de contacto
            saveBotConversation({ ...collectedData, wantsCall: false })
          }
          break

        case 'collect_availability':
          setCollectedData((prev) => ({ ...prev, availability: answer }))
          // Guardar y confirmar
          const finalData = { ...collectedData, availability: answer }
          saveBotConversation(finalData)
          setBotState('confirmed')
          nextStep('confirmed')
          setTimeout(() => showBotMessage(STEPS.confirmed.message), 800)
          break

        default:
          break
      }
    },
    [currentStep, collectedData, showBotMessage] // eslint-disable-line react-hooks/exhaustive-deps
  )

  const nextStep = (step: StepId) => {
    setCurrentStep(step)
  }

  // ─── Input libre ───────────────────────────────────────────────────────────

  const handleFreeInput = useCallback(() => {
    const value = inputValue.trim()
    if (!value) return

    addUserMessage(value)
    setInputValue('')

    switch (currentStep) {
      case 'collect_name':
        setCollectedData((prev) => ({ ...prev, name: value }))
        nextStep('collect_company')
        setTimeout(() => showBotMessage(STEPS.collect_company.message), 800)
        break
      case 'collect_company':
        setCollectedData((prev) => ({ ...prev, company: value }))
        nextStep('collect_role')
        setTimeout(() => showBotMessage(STEPS.collect_role.message), 800)
        break
      case 'collect_role':
        setCollectedData((prev) => ({ ...prev, role: value }))
        nextStep('collect_email')
        setTimeout(() => showBotMessage(STEPS.collect_email.message), 800)
        break
      case 'collect_email':
        setCollectedData((prev) => ({ ...prev, email: value }))
        nextStep('collect_phone')
        setTimeout(() => showBotMessage(STEPS.collect_phone.message), 800)
        break
      case 'collect_phone':
        setCollectedData((prev) => ({ ...prev, phone: value === '–' || value === '-' ? '' : value }))
        nextStep('collect_availability')
        setTimeout(() => showBotMessage(STEPS.collect_availability.message), 800)
        break
      default:
        break
    }
  }, [inputValue, currentStep, addUserMessage, showBotMessage])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleFreeInput()
  }

  // ─── Guardar lead ──────────────────────────────────────────────────────────

  const saveBotConversation = async (data: CollectedData) => {
    if (isSending) return
    setIsSending(true)
    try {
      const qualification = getQualification(data.intent, data.wantsCall)
      const payload = {
        messages: messages.map((m) => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp.toISOString(),
        })),
        intent: data.intent,
        companySize: data.companySize,
        toolsUsed: data.toolsUsed,
        mainProblem: data.mainProblem,
        wantsCall: data.wantsCall,
        name: data.name,
        company: data.company,
        role: data.role,
        email: data.email,
        phone: data.phone,
        availability: data.availability,
        qualification,
      }
      await fetch('/api/bot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
    } catch (err) {
      console.error('Error al guardar conversación:', err)
    } finally {
      setIsSending(false)
    }
  }

  // ─── Render ────────────────────────────────────────────────────────────────

  const step = STEPS[currentStep]
  const showOptions = !step.freeInput && step.options && botState !== 'confirmed'
  const showInput = step.freeInput && botState === 'collecting_data'
  const showMultiConfirm = step.multiSelect

  return (
    <>
      {/* Botón flotante */}
      <div className="fixed bottom-6 right-6 z-50">
        <AnimatePresence>
          {!isOpen && (
            <motion.button
              key="chat-toggle"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              onClick={() => setIsOpen(true)}
              className="relative w-14 h-14 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-xl flex items-center justify-center transition-colors"
              aria-label="Abrir chat"
            >
              <MessageCircle className="w-6 h-6" />
              {/* Indicador de no leído */}
              {hasUnread && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500 border-2 border-white"
                />
              )}
            </motion.button>
          )}
        </AnimatePresence>

        {/* Panel de chat */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              key="chat-panel"
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.95 }}
              transition={{ type: 'spring', stiffness: 300, damping: 28 }}
              className="
                fixed bottom-6 right-6
                w-[380px] max-w-[calc(100vw-1.5rem)]
                bg-white rounded-2xl shadow-2xl border border-gray-100
                flex flex-col overflow-hidden
                sm:h-[520px] h-[calc(100dvh-5rem)]
              "
              style={{ maxHeight: '520px' }}
            >
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 bg-blue-600 text-white flex-shrink-0">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-sm leading-tight">AP Automatización IA · Asistente</p>
                    <span className="flex items-center gap-1 text-xs text-blue-100">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
                      Online
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-full hover:bg-white/20 transition-colors"
                  aria-label="Cerrar chat"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Área de mensajes */}
              <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1 bg-gray-50">
                {messages.map((msg) => (
                  <ChatMessage key={msg.id} message={msg} />
                ))}
                {isTyping && <TypingIndicator />}
                <div ref={messagesEndRef} />
              </div>

              {/* Área de respuestas rápidas / input */}
              <div className="flex-shrink-0 border-t border-gray-100 bg-white px-3 py-3">
                {/* Opciones normales */}
                {showOptions && !isTyping && (
                  <div className="flex flex-col gap-1.5">
                    {step.multiSelect ? (
                      <>
                        <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto">
                          {step.options?.map((opt) => (
                            <button
                              key={opt}
                              onClick={() => handleOptionClick(opt)}
                              className={`
                                px-3 py-1.5 rounded-full text-xs border transition-all
                                ${selectedTools.includes(opt)
                                  ? 'bg-blue-600 text-white border-blue-600'
                                  : 'bg-white text-gray-700 border-gray-200 hover:border-blue-400 hover:text-blue-600'
                                }
                              `}
                            >
                              {selectedTools.includes(opt) ? '✓ ' : ''}{opt}
                            </button>
                          ))}
                        </div>
                        {showMultiConfirm && (
                          <button
                            onClick={handleMultiSelectConfirm}
                            className="mt-1 w-full py-2 rounded-xl bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
                          >
                            Confirmar selección →
                          </button>
                        )}
                      </>
                    ) : (
                      step.options?.map((opt) => (
                        <button
                          key={opt}
                          onClick={() => handleOptionClick(opt)}
                          className="w-full text-left px-3 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-700 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-all"
                        >
                          {opt}
                        </button>
                      ))
                    )}
                  </div>
                )}

                {/* Input de texto libre */}
                {showInput && !isTyping && (
                  <div className="flex items-center gap-2">
                    <input
                      ref={inputRef}
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder={step.inputPlaceholder ?? 'Escribe aquí...'}
                      className="flex-1 px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-transparent"
                      autoFocus
                    />
                    <button
                      onClick={handleFreeInput}
                      disabled={!inputValue.trim()}
                      className="p-2.5 rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                      aria-label="Enviar"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                )}

                {/* Opciones de confirmación final */}
                {botState === 'confirmed' && !isTyping && (
                  <div className="flex flex-col gap-1.5">
                    {STEPS.confirmed.options?.map((opt) => (
                      <button
                        key={opt}
                        onClick={() => handleOptionClick(opt)}
                        className="w-full text-left px-3 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-700 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-all"
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                )}

                {/* Texto legal */}
                <p className="text-center text-xs text-gray-400 mt-2">
                  AP Automatización IA · Tus datos están protegidos según el RGPD
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  )
}
