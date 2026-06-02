'use client'

import { motion } from 'framer-motion'

export interface MessageData {
  id: string
  role: 'bot' | 'user'
  content: string
  timestamp: Date
}

interface ChatMessageProps {
  message: MessageData
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isBot = message.role === 'bot'

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className={`flex items-end gap-2 mb-3 ${isBot ? 'justify-start' : 'justify-end'}`}
    >
      {/* Avatar bot */}
      {isBot && (
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center mb-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            className="w-4 h-4 text-white"
          >
            <path d="M12 8V4H8" />
            <rect width="16" height="12" x="4" y="8" rx="2" />
            <path d="M2 14h2" />
            <path d="M20 14h2" />
            <path d="M15 13v2" />
            <path d="M9 13v2" />
          </svg>
        </div>
      )}

      <div className={`flex flex-col ${isBot ? 'items-start' : 'items-end'} max-w-[80%]`}>
        {/* Burbuja del mensaje */}
        <div
          className={`
            px-4 py-2.5 rounded-2xl text-sm leading-relaxed
            ${isBot
              ? 'bg-gray-100 text-gray-800 rounded-tl-sm'
              : 'bg-blue-600 text-white rounded-tr-sm'
            }
          `}
        >
          {message.content}
        </div>

        {/* Timestamp */}
        <span className="text-xs text-gray-400 mt-1 px-1">
          {formatTime(message.timestamp)}
        </span>
      </div>

      {/* Avatar usuario */}
      {!isBot && (
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-gray-300 flex items-center justify-center mb-1">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            className="w-4 h-4 text-gray-600"
          >
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
          </svg>
        </div>
      )}
    </motion.div>
  )
}
