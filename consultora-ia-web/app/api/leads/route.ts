import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { createServerClient } from '@/lib/supabase'
import { Resend } from 'resend'
import {
  emailNuevoLead,
  emailConfirmacionCliente,
} from '@/lib/email-templates'

const supabase = createServerClient()

function getResend() { return new Resend(process.env.RESEND_API_KEY ?? "") }

// ─── Validación ───────────────────────────────────────────────────────────────

const leadSchema = z.object({
  name: z.string().min(2, 'El nombre es obligatorio'),
  email: z.string().email('Email no válido'),
  company: z.string().optional(),
  role: z.string().optional(),
  phone: z.string().optional(),
  sector: z.string().optional(),
  employees_range: z.string().optional(),
  service_interest: z.string().optional(),
  main_problem: z.string().optional(),
  tools_used: z.array(z.string()).optional(),
  preferred_contact_time: z.string().optional(),
  source: z.string().optional().default('web'),
  notes: z.string().optional(),
  qualification: z.string().optional(),
})

// ─── Cálculo de lead_score ────────────────────────────────────────────────────

function calculateLeadScore(data: z.infer<typeof leadSchema>): number {
  let score = 0

  // Tamaño de empresa (0–25)
  const sizeMap: Record<string, number> = {
    '1-10 empleados': 10,
    '11-50 empleados': 18,
    '51-200 empleados': 22,
    'Más de 200': 25,
  }
  score += sizeMap[data.employees_range ?? ''] ?? 5

  // Herramientas usadas (0–20): más herramientas = más madurez digital
  const tools = data.tools_used ?? []
  if (tools.length >= 4) score += 20
  else if (tools.length >= 2) score += 12
  else if (tools.length === 1) score += 6

  // Interés específico (0–25)
  const interestMap: Record<string, number> = {
    automatización: 25,
    agentes_ia: 25,
    'consultoría_ia': 20,
    información: 10,
    no_cualificado: 0,
  }
  score += interestMap[data.qualification ?? ''] ?? 5

  // Datos completados (0–30)
  if (data.name) score += 5
  if (data.email) score += 5
  if (data.company) score += 5
  if (data.role) score += 5
  if (data.phone) score += 5
  if (data.preferred_contact_time) score += 5

  return Math.min(score, 100)
}

// ─── Disparar webhook n8n ─────────────────────────────────────────────────────

async function triggerN8nWebhook(data: Record<string, unknown>) {
  const webhookUrl = process.env.NEXT_PUBLIC_N8N_WEBHOOK_URL
  if (!webhookUrl) return
  try {
    await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
  } catch (err) {
    console.error('Error al disparar webhook n8n:', err)
  }
}

// ─── Handler POST ─────────────────────────────────────────────────────────────

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const parsed = leadSchema.safeParse(body)

    if (!parsed.success) {
      return NextResponse.json(
        { success: false, errors: parsed.error.flatten().fieldErrors },
        { status: 400 }
      )
    }

    const data = parsed.data
    const lead_score = calculateLeadScore(data)

    // Guardar en Supabase
    const { data: insertedLead, error: dbError } = await supabase
      .from('leads')
      .insert([{ ...data, lead_score }])
      .select('id')
      .single()

    if (dbError) {
      console.error('Error Supabase:', dbError)
      return NextResponse.json(
        { success: false, error: 'Error al guardar el lead' },
        { status: 500 }
      )
    }

    const lead = { ...data, id: insertedLead.id, lead_score }

    // Enviar email interno al equipo comercial
    await getResend().emails.send({
      from: 'AP Automatización IA <noreply@automatizacionprocesos.es>',
      to: 'admin@automatizacionprocesos.es',
      subject: `🔔 Nuevo lead: ${data.name} — ${data.company ?? 'Sin empresa'} (Score: ${lead_score})`,
      html: emailNuevoLead(lead),
    })

    // Enviar email de confirmación al cliente
    await getResend().emails.send({
      from: 'AP Automatización IA <admin@automatizacionprocesos.es>',
      to: data.email,
      subject: 'Hemos recibido tu solicitud — AP Automatización IA',
      html: emailConfirmacionCliente(lead),
    })

    // Disparar webhook n8n
    await triggerN8nWebhook({ event: 'new_lead', lead })

    return NextResponse.json({ success: true, lead_id: insertedLead.id }, { status: 200 })
  } catch (err) {
    console.error('Error en /api/leads:', err)
    return NextResponse.json(
      { success: false, error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
}
