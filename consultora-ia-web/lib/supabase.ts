import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

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
