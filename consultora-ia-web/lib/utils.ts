import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format, formatDistanceToNow, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import type { Lead } from './types'

// ============================================================
// cn — Tailwind class merger
// ============================================================

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

// ============================================================
// formatDate — Formatea fechas en español
// ============================================================

export function formatDate(
  date: string | Date,
  pattern = "d 'de' MMMM 'de' yyyy"
): string {
  const parsed = typeof date === 'string' ? parseISO(date) : date
  return format(parsed, pattern, { locale: es })
}

export function formatDateShort(date: string | Date): string {
  const parsed = typeof date === 'string' ? parseISO(date) : date
  return format(parsed, 'dd/MM/yyyy', { locale: es })
}

export function formatRelativeDate(date: string | Date): string {
  const parsed = typeof date === 'string' ? parseISO(date) : date
  return formatDistanceToNow(parsed, { addSuffix: true, locale: es })
}

// ============================================================
// truncate — Trunca texto
// ============================================================

export function truncate(text: string, maxLength: number = 160): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trimEnd() + '…'
}

// ============================================================
// slugify — Convierte texto a slug URL-safe
// ============================================================

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '') // Eliminar acentos
    .replace(/[^a-z0-9\s-]/g, '') // Solo alfanumérico, espacios y guiones
    .trim()
    .replace(/\s+/g, '-') // Espacios a guiones
    .replace(/-+/g, '-') // Múltiples guiones a uno
}

// ============================================================
// generateLeadScore — Puntuación de lead 0-100
// ============================================================

export function generateLeadScore(lead: Partial<Lead>): number {
  let score = 0

  // Email corporativo (no gratuito) +20
  const freeEmailDomains = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 'icloud.com']
  if (lead.email) {
    const domain = lead.email.split('@')[1]?.toLowerCase()
    if (domain && !freeEmailDomains.includes(domain)) {
      score += 20
    }
  }

  // Tiene empresa +15
  if (lead.empresa) score += 15

  // Tiene teléfono +15
  if (lead.telefono) score += 15

  // Tiene mensaje con más de 50 caracteres +10
  if (lead.mensaje && lead.mensaje.length > 50) score += 10

  // Tiene sector +10
  if (lead.sector) score += 10

  // Tamaño empresa
  if (lead.tamaño_empresa) {
    const sizeScores: Record<string, number> = {
      '1-10': 5,
      '11-50': 10,
      '51-200': 15,
      '201-500': 20,
      '500+': 25,
    }
    score += sizeScores[lead.tamaño_empresa] ?? 5
  }

  // Fuente del lead
  if (lead.fuente === 'formulario_contacto') score += 5
  if (lead.fuente === 'chatbot') score += 3

  return Math.min(score, 100)
}

// ============================================================
// formatPhone — Formatea teléfonos españoles
// ============================================================

export function formatPhone(phone: string): string {
  const cleaned = phone.replace(/\D/g, '')
  if (cleaned.startsWith('34') && cleaned.length === 11) {
    return `+34 ${cleaned.slice(2, 5)} ${cleaned.slice(5, 8)} ${cleaned.slice(8)}`
  }
  if (cleaned.length === 9) {
    return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6)}`
  }
  return phone
}

// ============================================================
// isValidEmail — Validación básica de email
// ============================================================

export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

// ============================================================
// getInitials — Iniciales de nombre
// ============================================================

export function getInitials(name: string): string {
  return name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0]?.toUpperCase())
    .join('')
}

// ============================================================
// formatNumber — Formatea números con separadores ES
// ============================================================

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('es-ES').format(num)
}

// ============================================================
// generateSessionId — ID de sesión único para el chatbot
// ============================================================

export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

// ============================================================
// clampNumber — Limita un número entre min y max
// ============================================================

export function clampNumber(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

// ============================================================
// debounce — Función debounce
// ============================================================

export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

// ============================================================
// parseUTMParams — Extrae parámetros UTM de la URL
// ============================================================

export function parseUTMParams(url: string): Record<string, string> {
  try {
    const params = new URL(url).searchParams
    const utmKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
    return Object.fromEntries(
      utmKeys
        .filter((key) => params.has(key))
        .map((key) => [key, params.get(key)!])
    )
  } catch {
    return {}
  }
}
