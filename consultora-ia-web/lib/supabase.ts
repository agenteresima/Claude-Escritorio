import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

// Cliente público (browser / components) — lazy para evitar errores en build
export function getSupabaseClient() {
  return createClient(supabaseUrl, supabaseAnonKey)
}

// Alias para compatibilidad
export const supabase = {
  from: (table: string) => getSupabaseClient().from(table),
}

// Cliente servidor con service role — bypasa RLS, solo usar en API routes
export function createServerClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  if (!url || (!serviceKey && !anonKey)) {
    // Durante el build sin variables, devolver cliente mock
    return createClient('https://placeholder.supabase.co', 'placeholder-key')
  }

  return createClient(url, serviceKey ?? anonKey!, {
    auth: { persistSession: false },
  })
}

export interface Lead {
  id?: string
  created_at?: string
  name: string
  company?: string
  role?: string
  email: string
  phone?: string
  sector?: string
  employees_range?: string
  service_interest?: string
  main_problem?: string
  tools_used?: string[]
  preferred_contact_time?: string
  lead_score?: number
  status?: string
  source?: string
  notes?: string
  qualification?: string
}

export interface BotConversation {
  id?: string
  lead_id?: string
  created_at?: string
  messages: BotMessageRecord[]
  summary?: string
  intent?: string
  qualification_score?: number
}

export interface BotMessageRecord {
  role: 'bot' | 'user'
  content: string
  timestamp: string
  options?: string[]
  selected?: string
}

export interface ContactRequest {
  id?: string
  created_at?: string
  name: string
  email: string
  phone?: string
  company?: string
  message?: string
  service_interest?: string
  status?: string
}

export interface NewsletterSubscriber {
  id?: string
  created_at?: string
  email: string
  source?: string
  status?: string
}
