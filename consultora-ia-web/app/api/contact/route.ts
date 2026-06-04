import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { createServerClient } from '@/lib/supabase'
import { Resend } from 'resend'

const supabase = createServerClient()

function getResend() { return new Resend(process.env.RESEND_API_KEY ?? "") }

// ─── Validación ───────────────────────────────────────────────────────────────

const contactSchema = z.object({
  name: z.string().min(2, 'El nombre es obligatorio'),
  email: z.string().email('Email no válido'),
  empresa: z.string().optional(),
  phone: z.string().optional(),
  mensaje: z.string().min(10, 'El mensaje debe tener al menos 10 caracteres'),
  servicio_interes: z.string().optional(),
})

// ─── Handler POST ─────────────────────────────────────────────────────────────

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const parsed = contactSchema.safeParse(body)

    if (!parsed.success) {
      return NextResponse.json(
        { success: false, errors: parsed.error.flatten().fieldErrors },
        { status: 400 }
      )
    }

    const data = parsed.data

    // Guardar en Supabase
    const { data: inserted, error: dbError } = await supabase
      .from('contact_requests')
      .insert([
        {
          name: data.name,
          email: data.email,
          phone: data.phone,
          company: data.empresa,
          message: data.mensaje,
          service_interest: data.servicio_interes,
          status: 'pendiente',
        },
      ])
      .select('id')
      .single()

    if (dbError) {
      console.error('Error Supabase:', dbError)
      return NextResponse.json(
        { success: false, error: 'Error al guardar la solicitud' },
        { status: 500 }
      )
    }

    // Email interno de notificación
    await getResend().emails.send({
      from: 'AP Automatización IA <noreply@automatizacionprocesos.es>',
      to: 'hola@automatizacionprocesos.es',
      subject: `📬 Nuevo mensaje de contacto: ${data.name}`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
          <h2 style="color: #1e40af;">Nuevo mensaje de contacto</h2>
          <table style="width:100%; border-collapse: collapse;">
            <tr><td style="padding: 8px; font-weight: bold; color: #374151;">Nombre:</td><td style="padding: 8px;">${data.name}</td></tr>
            <tr><td style="padding: 8px; font-weight: bold; color: #374151;">Email:</td><td style="padding: 8px;">${data.email}</td></tr>
            ${data.phone ? `<tr><td style="padding: 8px; font-weight: bold; color: #374151;">Teléfono:</td><td style="padding: 8px;">${data.phone}</td></tr>` : ''}
            ${data.empresa ? `<tr><td style="padding: 8px; font-weight: bold; color: #374151;">Empresa:</td><td style="padding: 8px;">${data.empresa}</td></tr>` : ''}
            ${data.servicio_interes ? `<tr><td style="padding: 8px; font-weight: bold; color: #374151;">Servicio de interés:</td><td style="padding: 8px;">${data.servicio_interes}</td></tr>` : ''}
          </table>
          <div style="margin-top: 16px; padding: 16px; background: #f3f4f6; border-radius: 8px;">
            <p style="font-weight: bold; color: #374151; margin: 0 0 8px;">Mensaje:</p>
            <p style="color: #4b5563; margin: 0;">${data.mensaje}</p>
          </div>
          <p style="margin-top: 16px; font-size: 12px; color: #9ca3af;">ID de solicitud: ${inserted.id}</p>
        </div>
      `,
    })

    // Email de confirmación al usuario
    await getResend().emails.send({
      from: 'AP Automatización IA <hola@automatizacionprocesos.es>',
      to: data.email,
      subject: 'Hemos recibido tu mensaje — AP Automatización IA',
      html: `
        <!DOCTYPE html>
        <html lang="es">
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="margin:0; padding:0; background-color:#f9fafb; font-family: Arial, sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f9fafb; padding: 40px 20px;">
            <tr><td align="center">
              <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.07);">
                <tr>
                  <td style="background-color:#1e40af; padding: 32px 40px; text-align: center;">
                    <h1 style="color:#ffffff; margin:0; font-size:24px; font-weight:700;">AP Automatización IA</h1>
                    <p style="color:#93c5fd; margin:8px 0 0; font-size:14px;">Consultora de Inteligencia Artificial</p>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 40px;">
                    <h2 style="color:#1e40af; margin: 0 0 16px; font-size:20px;">Hola, ${data.name} 👋</h2>
                    <p style="color:#374151; line-height:1.6; margin: 0 0 16px;">Hemos recibido tu mensaje y te responderemos en un plazo máximo de <strong>24 horas laborables</strong>.</p>
                    <p style="color:#374151; line-height:1.6; margin: 0 0 24px;">En AP Automatización IA estamos comprometidos a ayudarte a transformar tu empresa con inteligencia artificial. Tu consulta es importante para nosotros.</p>
                    <div style="background:#eff6ff; border-left: 4px solid #1e40af; padding: 16px; border-radius: 0 8px 8px 0; margin-bottom: 32px;">
                      <p style="margin:0; color:#1e40af; font-weight:bold; font-size:14px;">Tu mensaje:</p>
                      <p style="margin: 8px 0 0; color:#374151; font-size:14px;">${data.mensaje}</p>
                    </div>
                    <table cellpadding="0" cellspacing="0" style="margin: 0 auto 32px;">
                      <tr>
                        <td style="background-color:#1e40af; border-radius:8px; padding: 14px 28px;">
                          <a href="https://automatizacionprocesos.es" style="color:#ffffff; text-decoration:none; font-weight:600; font-size:15px;">Visitar AP Automatización IA →</a>
                        </td>
                      </tr>
                    </table>
                    <p style="color:#6b7280; font-size:13px; margin:0;">Si tienes alguna pregunta urgente, puedes escribirnos directamente a <a href="mailto:hola@automatizacionprocesos.es" style="color:#1e40af;">hola@automatizacionprocesos.es</a></p>
                  </td>
                </tr>
                <tr>
                  <td style="background-color:#f9fafb; padding: 24px 40px; border-top: 1px solid #e5e7eb;">
                    <p style="color:#9ca3af; font-size:11px; margin:0; line-height:1.6;">
                      AP Automatización IA · Consultora de Inteligencia Artificial<br>
                      Enviado a: ${data.email}<br><br>
                      De conformidad con el Reglamento (UE) 2016/679 (RGPD) y la LOPDGDD, tus datos personales son tratados por AP Automatización IA con la finalidad de gestionar tu solicitud. Puedes ejercer tus derechos de acceso, rectificación, supresión y oposición escribiendo a <a href="mailto:privacidad@automatizacionprocesos.es" style="color:#9ca3af;">privacidad@automatizacionprocesos.es</a>.
                    </p>
                  </td>
                </tr>
              </table>
            </td></tr>
          </table>
        </body>
        </html>
      `,
    })

    return NextResponse.json({ success: true, id: inserted.id }, { status: 200 })
  } catch (err) {
    console.error('Error en /api/contact:', err)
    return NextResponse.json(
      { success: false, error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
}
