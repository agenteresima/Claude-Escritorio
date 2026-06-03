import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { createServerClient } from '@/lib/supabase'
import { Resend } from 'resend'
import { emailNuevoLead, emailConfirmacionCliente } from '@/lib/email-templates'

const supabase = createServerClient()

const resend = new Resend(process.env.RESEND_API_KEY)

// ─── Validación ───────────────────────────────────────────────────────────────

const botMessageSchema = z.object({
  role: z.enum(['bot', 'user']),
  content: z.string(),
  timestamp: z.string(),
  options: z.array(z.string()).optional(),
  selected: z.string().optional(),
})

const botConversationSchema = z.object({
  messages: z.array(botMessageSchema),
  intent: z.string().optional(),
  companySize: z.string().optional(),
  toolsUsed: z.array(z.string()).optional(),
  mainProblem: z.string().optional(),
  wantsCall: z.boolean().optional(),
  name: z.string().optional(),
  company: z.string().optional(),
  role: z.string().optional(),
  email: z.string().email().optional().or(z.literal('')),
  phone: z.string().optional(),
  availability: z.string().optional(),
  qualification: z.string().optional(),
})

// ─── Cálculo qualification_score ─────────────────────────────────────────────

function calculateQualificationScore(data: z.infer<typeof botConversationSchema>): number {
  let score = 0

  // Intención (0–30)
  const intentMap: Record<string, number> = {
    automatizar: 30,
    agente: 30,
    asesoramiento: 25,
    información: 10,
    persona: 20,
  }
  score += intentMap[data.intent ?? ''] ?? 5

  // Tamaño empresa (0–25)
  const sizeMap: Record<string, number> = {
    '1-10 empleados': 8,
    '11-50 empleados': 16,
    '51-200 empleados': 22,
    'Más de 200': 25,
  }
  score += sizeMap[data.companySize ?? ''] ?? 0

  // Quiere llamada (0–20)
  if (data.wantsCall) score += 20

  // Datos de contacto completos (0–25)
  if (data.name) score += 5
  if (data.email) score += 8
  if (data.company) score += 5
  if (data.role) score += 4
  if (data.phone) score += 3

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

// ─── Resumen de conversación ──────────────────────────────────────────────────

function buildSummary(data: z.infer<typeof botConversationSchema>): string {
  const parts: string[] = []
  if (data.intent) parts.push(`Intención: ${data.intent}`)
  if (data.companySize) parts.push(`Empresa: ${data.companySize}`)
  if (data.toolsUsed?.length) parts.push(`Herramientas: ${data.toolsUsed.join(', ')}`)
  if (data.mainProblem) parts.push(`Problema: ${data.mainProblem}`)
  if (data.wantsCall !== undefined) parts.push(`Quiere llamada: ${data.wantsCall ? 'Sí' : 'No'}`)
  if (data.name) parts.push(`Contacto: ${data.name}`)
  if (data.email) parts.push(`Email: ${data.email}`)
  return parts.join(' | ')
}

// ─── Handler POST ─────────────────────────────────────────────────────────────

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const parsed = botConversationSchema.safeParse(body)

    if (!parsed.success) {
      return NextResponse.json(
        { success: false, errors: parsed.error.flatten().fieldErrors },
        { status: 400 }
      )
    }

    const data = parsed.data
    const qualification_score = calculateQualificationScore(data)
    const summary = buildSummary(data)

    let lead_id: string | null = null

    // Si tenemos email, crear también registro en leads
    if (data.email && data.wantsCall) {
      const { data: insertedLead, error: leadError } = await supabase
        .from('leads')
        .insert([
          {
            name: data.name ?? 'Desconocido',
            email: data.email,
            company: data.company,
            role: data.role,
            phone: data.phone,
            employees_range: data.companySize,
            service_interest: data.intent,
            main_problem: data.mainProblem,
            tools_used: data.toolsUsed,
            preferred_contact_time: data.availability,
            lead_score: qualification_score,
            status: 'nuevo',
            source: 'chatbot',
            qualification: data.qualification,
          },
        ])
        .select('id')
        .single()

      if (leadError) {
        console.error('Error al insertar lead:', leadError)
      } else {
        lead_id = insertedLead.id

        // Enviar emails si tenemos lead completo
        const lead = {
          id: lead_id,
          name: data.name ?? 'Desconocido',
          email: data.email,
          company: data.company,
          role: data.role,
          phone: data.phone,
          employees_range: data.companySize,
          service_interest: data.intent,
          main_problem: data.mainProblem,
          tools_used: data.toolsUsed,
          preferred_contact_time: data.availability,
          lead_score: qualification_score,
          source: 'chatbot',
          qualification: data.qualification,
        }

        await resend.emails.send({
          from: 'AP Automatización IA <noreply@automatizacionprocesos.es>',
          to: 'hola@automatizacionprocesos.es',
          subject: `🤖 Lead del chatbot: ${data.name} — ${data.company ?? 'Sin empresa'} (Score: ${qualification_score})`,
          html: emailNuevoLead(lead),
        })

        await resend.emails.send({
          from: 'AP Automatización IA <hola@automatizacionprocesos.es>',
          to: data.email,
          subject: 'Tu solicitud de consultoría ha sido recibida — AP Automatización IA',
          html: emailConfirmacionCliente(lead),
        })
      }
    }

    // Guardar conversación en Supabase
    const { data: conversation, error: convError } = await supabase
      .from('bot_conversations')
      .insert([
        {
          lead_id,
          messages: data.messages,
          summary,
          intent: data.intent,
          qualification_score,
        },
      ])
      .select('id')
      .single()

    if (convError) {
      console.error('Error al guardar conversación:', convError)
      return NextResponse.json(
        { success: false, error: 'Error al guardar la conversación' },
        { status: 500 }
      )
    }

    // Disparar webhook n8n
    await triggerN8nWebhook({
      event: 'bot_conversation',
      conversation_id: conversation.id,
      lead_id,
      qualification_score,
      summary,
      data,
    })

    return NextResponse.json(
      {
        success: true,
        conversation_id: conversation.id,
        lead_id,
        qualification_score,
      },
      { status: 200 }
    )
  } catch (err) {
    console.error('Error en /api/bot:', err)
    return NextResponse.json(
      { success: false, error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
}
