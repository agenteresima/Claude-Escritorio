// ============================================================
// AP Automatización IA — TypeScript Types
// ============================================================

// --- Enums ---

export type LeadStatus =
  | 'nuevo'
  | 'contactado'
  | 'calificado'
  | 'propuesta'
  | 'cerrado_ganado'
  | 'cerrado_perdido'

export type ServiceCategory =
  | 'automatizacion'
  | 'agentes'
  | 'formacion'
  | 'estrategia'
  | 'analisis'
  | 'chatbots'
  | 'integraciones'

// --- Lead ---

export interface Lead {
  id?: string
  created_at?: string
  nombre: string
  email: string
  empresa?: string
  telefono?: string
  sector?: string
  tamaño_empresa?: string
  mensaje?: string
  fuente: 'chatbot' | 'formulario_contacto' | 'newsletter' | 'landing' | 'otro'
  status: LeadStatus
  score?: number
  etiquetas?: string[]
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
}

// --- Bot Conversation ---

export interface BotMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  typing?: boolean
}

export interface BotConversation {
  id?: string
  created_at?: string
  session_id: string
  messages: BotMessage[]
  lead_id?: string
  duracion_segundos?: number
  finalizada: boolean
  convirtio_lead: boolean
}

// --- Contact Request ---

export interface ContactRequest {
  id?: string
  created_at?: string
  nombre: string
  email: string
  empresa?: string
  telefono?: string
  servicio_interes?: ServiceCategory
  presupuesto?: string
  mensaje: string
  respondido: boolean
  fecha_respuesta?: string
}

// --- Newsletter Subscriber ---

export interface NewsletterSubscriber {
  id?: string
  created_at?: string
  email: string
  nombre?: string
  activo: boolean
  fuente?: string
  tags?: string[]
}

// --- Blog Post ---

export interface BlogPost {
  id: string
  slug: string
  titulo: string
  extracto: string
  contenido: string
  imagen_portada?: string
  autor: string
  fecha_publicacion: string
  fecha_actualizacion?: string
  categorias: string[]
  etiquetas: string[]
  publicado: boolean
  tiempo_lectura: number // minutos
  seo_title?: string
  seo_description?: string
}

// --- Service ---

export interface Service {
  id: string
  slug: string
  nombre: string
  descripcion_corta: string
  descripcion_larga: string
  icono: string
  categoria: ServiceCategory
  beneficios: string[]
  caracteristicas: string[]
  precio_desde?: string
  duracion_tipica?: string
  destacado: boolean
  orden: number
}

// --- Use Case ---

export interface UseCase {
  id: string
  titulo: string
  descripcion: string
  sector: string
  resultado: string
  metricas?: {
    label: string
    valor: string
    mejora?: string
  }[]
  icono: string
  servicio_relacionado?: ServiceCategory
}

// --- FAQ Item ---

export interface FAQItem {
  id: string
  pregunta: string
  respuesta: string
  categoria?: string
  orden: number
}

// --- Navigation ---

export interface NavItem {
  label: string
  href: string
  descripcion?: string
  hijos?: NavItem[]
  externo?: boolean
  badge?: string
}

// --- Company Info ---

export interface CompanyInfo {
  nombre: string
  nombre_legal: string
  slogan: string
  descripcion: string
  email: string
  email_soporte: string
  telefono: string
  direccion: string
  ciudad: string
  pais: string
  cif?: string
  redes_sociales: {
    linkedin?: string
    twitter?: string
    youtube?: string
    instagram?: string
  }
}

// --- Form Types ---

export interface ContactFormData {
  nombre: string
  email: string
  empresa?: string
  telefono?: string
  servicio?: ServiceCategory
  presupuesto?: string
  mensaje: string
  acepta_privacidad: boolean
}

export interface NewsletterFormData {
  email: string
  nombre?: string
}

// --- API Response ---

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
  message?: string
}
