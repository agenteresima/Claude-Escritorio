import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { createServerClient } from '@/lib/supabase'
import { Resend } from 'resend'

const supabase = createServerClient()

function getResend() { return new Resend(process.env.RESEND_API_KEY ?? "") }

// ─── Validación ───────────────────────────────────────────────────────────────

const newsletterSchema = z.object({
  email: z.string().email('Introduce un email válido'),
  source: z.string().optional().default('web'),
})

// ─── Handler POST ─────────────────────────────────────────────────────────────

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const parsed = newsletterSchema.safeParse(body)

    if (!parsed.success) {
      return NextResponse.json(
        { success: false, errors: parsed.error.flatten().fieldErrors },
        { status: 400 }
      )
    }

    const { email, source } = parsed.data

    // Upsert — si ya existe, actualizar source/status sin error
    const { data: subscriber, error: dbError } = await supabase
      .from('newsletter_subscribers')
      .upsert(
        [{ email, source, status: 'activo' }],
        { onConflict: 'email', ignoreDuplicates: false }
      )
      .select('id, created_at')
      .single()

    if (dbError) {
      console.error('Error Supabase newsletter:', dbError)
      return NextResponse.json(
        { success: false, error: 'Error al procesar la suscripción' },
        { status: 500 }
      )
    }

    // Email de bienvenida
    await getResend().emails.send({
      from: 'AP Automatización IA <hola@automatizacionprocesos.es>',
      to: email,
      subject: '¡Bienvenido/a a la newsletter de AP Automatización IA! 🚀',
      html: `
        <!DOCTYPE html>
        <html lang="es">
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="margin:0; padding:0; background-color:#f9fafb; font-family: Arial, sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f9fafb; padding: 40px 20px;">
            <tr><td align="center">
              <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.07);">
                <tr>
                  <td style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 40px; text-align: center;">
                    <h1 style="color:#ffffff; margin:0; font-size:28px; font-weight:700;">AP Automatización IA</h1>
                    <p style="color:#bfdbfe; margin:10px 0 0; font-size:15px;">Consultora de Inteligencia Artificial</p>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 40px;">
                    <h2 style="color:#1e40af; margin: 0 0 16px; font-size:22px;">¡Ya formas parte de nuestra comunidad! 🎉</h2>
                    <p style="color:#374151; line-height:1.7; margin: 0 0 16px; font-size:15px;">Gracias por suscribirte a la newsletter de AP Automatización IA. Cada semana recibirás:</p>
                    <ul style="color:#374151; line-height:1.8; font-size:15px; padding-left: 20px;">
                      <li>Las últimas tendencias en IA para empresas</li>
                      <li>Casos de uso reales y casos de éxito</li>
                      <li>Guías prácticas de automatización</li>
                      <li>Novedades exclusivas de AP Automatización IA</li>
                    </ul>
                    <table cellpadding="0" cellspacing="0" style="margin: 32px auto;">
                      <tr>
                        <td style="background-color:#1e40af; border-radius:8px; padding: 14px 28px;">
                          <a href="https://www.automatizacionprocesos.es/blog" style="color:#ffffff; text-decoration:none; font-weight:600; font-size:15px;">Leer el blog →</a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="background-color:#f9fafb; padding: 24px 40px; border-top: 1px solid #e5e7eb;">
                    <p style="color:#9ca3af; font-size:11px; margin:0; line-height:1.6; text-align: center;">
                      AP Automatización IA · Consultora de Inteligencia Artificial<br>
                      Has recibido este email porque te suscribiste en <a href="https://www.automatizacionprocesos.es" style="color:#9ca3af;">automatizacionprocesos.es</a><br><br>
                      Si no deseas recibir más emails, <a href="https://www.automatizacionprocesos.es/baja-newsletter?email=${encodeURIComponent(email)}" style="color:#9ca3af;">cancela tu suscripción aquí</a>.<br>
                      De conformidad con el RGPD, tratamos tus datos exclusivamente para enviarte esta newsletter.
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

    return NextResponse.json(
      { success: true, id: subscriber.id, already_subscribed: false },
      { status: 200 }
    )
  } catch (err) {
    console.error('Error en /api/newsletter:', err)
    return NextResponse.json(
      { success: false, error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
}
