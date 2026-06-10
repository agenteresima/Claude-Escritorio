// ─── Tipos ────────────────────────────────────────────────────────────────────

export interface Lead {
  id?: string
  name: string
  email: string
  company?: string
  role?: string
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

// ─── Estilos compartidos ──────────────────────────────────────────────────────

const BASE_STYLES = {
  container: 'font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f9fafb; padding: 40px 20px;',
  card: 'background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.07);',
  header: 'background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 32px 40px; text-align: center;',
  body: 'padding: 40px;',
  footer: 'background-color: #f9fafb; padding: 24px 40px; border-top: 1px solid #e5e7eb;',
  h1: 'color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;',
  subtitle: 'color: #bfdbfe; margin: 8px 0 0; font-size: 14px;',
  h2: 'color: #1e40af; margin: 0 0 16px; font-size: 20px;',
  p: 'color: #374151; line-height: 1.7; margin: 0 0 16px; font-size: 15px;',
  cta: 'background-color: #1e40af; border-radius: 8px; padding: 14px 28px; display: inline-block;',
  ctaLink: 'color: #ffffff; text-decoration: none; font-weight: 600; font-size: 15px;',
  footerText: 'color: #9ca3af; font-size: 11px; margin: 0; line-height: 1.6;',
  badge: 'display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600;',
  tableCell: 'padding: 10px 12px; border-bottom: 1px solid #f3f4f6; font-size: 14px;',
}

const FOOTER_LEGAL = `
  <p style="${BASE_STYLES.footerText} text-align: center;">
    Automatización Procesos IA · Consultora de Inteligencia Artificial<br>
    <a href="https://automatizacionprocesos.es" style="color: #9ca3af;">automatizacionprocesos.es</a> · 
    <a href="mailto:admin@automatizacionprocesos.es" style="color: #9ca3af;">admin@automatizacionprocesos.es</a><br><br>
    De conformidad con el Reglamento (UE) 2016/679 (RGPD) y la LOPDGDD, tus datos personales son tratados 
    por Automatización Procesos IA con la finalidad de gestionar tu solicitud y contactarte comercialmente. 
    Puedes ejercer tus derechos de acceso, rectificación, supresión y oposición escribiendo a 
    <a href="mailto:privacidad@automatizacionprocesos.es" style="color: #9ca3af;">privacidad@automatizacionprocesos.es</a>.
  </p>
`

function scoreColor(score?: number): string {
  if (!score) return '#6b7280'
  if (score >= 70) return '#16a34a'
  if (score >= 40) return '#d97706'
  return '#dc2626'
}

function scoreLabel(score?: number): string {
  if (!score) return 'Sin puntuación'
  if (score >= 70) return 'Lead caliente 🔥'
  if (score >= 40) return 'Lead templado ⚡'
  return 'Lead frío ❄️'
}

function qualificationLabel(q?: string): string {
  const map: Record<string, string> = {
    'consultoría_ia': 'Consultoría IA',
    automatización: 'Automatización',
    agentes_ia: 'Agentes IA',
    información: 'Información',
    no_cualificado: 'No cualificado',
  }
  return map[q ?? ''] ?? q ?? '—'
}

// ─── Email interno: nuevo lead para el equipo ─────────────────────────────────

export function emailNuevoLead(lead: Lead): string {
  const score = lead.lead_score ?? 0
  return `
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0; padding:0; ${BASE_STYLES.container}">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td>
          <div style="${BASE_STYLES.card}">
            <!-- Header -->
            <div style="${BASE_STYLES.header}">
              <h1 style="${BASE_STYLES.h1}">🔔 Nuevo Lead — Automatización Procesos IA</h1>
              <p style="${BASE_STYLES.subtitle}">Solicitud recibida desde ${lead.source ?? 'web'}</p>
            </div>

            <!-- Score badge -->
            <div style="padding: 20px 40px; background: #eff6ff; border-bottom: 1px solid #dbeafe; text-align: center;">
              <span style="${BASE_STYLES.badge} background-color: ${scoreColor(score)}20; color: ${scoreColor(score)}; border: 1px solid ${scoreColor(score)}40; font-size: 16px; padding: 8px 20px;">
                Lead Score: ${score}/100 — ${scoreLabel(score)}
              </span>
              <span style="${BASE_STYLES.badge} background-color: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; margin-left: 8px;">
                ${qualificationLabel(lead.qualification)}
              </span>
            </div>

            <!-- Datos del lead -->
            <div style="${BASE_STYLES.body}">
              <h2 style="${BASE_STYLES.h2}">Datos de contacto</h2>
              <table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; margin-bottom: 24px;">
                ${lead.name ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb; width: 35%;">Nombre</td><td style="${BASE_STYLES.tableCell} color: #1f2937;">${lead.name}</td></tr>` : ''}
                ${lead.email ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb;">Email</td><td style="${BASE_STYLES.tableCell}"><a href="mailto:${lead.email}" style="color: #1e40af;">${lead.email}</a></td></tr>` : ''}
                ${lead.phone ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb;">Teléfono</td><td style="${BASE_STYLES.tableCell} color: #1f2937;"><a href="tel:${lead.phone}" style="color: #1e40af;">${lead.phone}</a></td></tr>` : ''}
                ${lead.company ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb;">Empresa</td><td style="${BASE_STYLES.tableCell} color: #1f2937;">${lead.company}</td></tr>` : ''}
                ${lead.role ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb;">Cargo</td><td style="${BASE_STYLES.tableCell} color: #1f2937;">${lead.role}</td></tr>` : ''}
                ${lead.employees_range ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb;">Tamaño empresa</td><td style="${BASE_STYLES.tableCell} color: #1f2937;">${lead.employees_range}</td></tr>` : ''}
                ${lead.preferred_contact_time ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb;">Disponibilidad</td><td style="${BASE_STYLES.tableCell} color: #1f2937;">${lead.preferred_contact_time}</td></tr>` : ''}
              </table>

              <h2 style="${BASE_STYLES.h2}">Información de cualificación</h2>
              <table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; margin-bottom: 24px;">
                ${lead.service_interest ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb; width: 35%;">Interés</td><td style="${BASE_STYLES.tableCell} color: #1f2937;">${lead.service_interest}</td></tr>` : ''}
                ${lead.main_problem ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb;">Problema principal</td><td style="${BASE_STYLES.tableCell} color: #1f2937;">${lead.main_problem}</td></tr>` : ''}
                ${lead.tools_used?.length ? `<tr><td style="${BASE_STYLES.tableCell} font-weight: bold; color: #374151; background: #f9fafb;">Herramientas</td><td style="${BASE_STYLES.tableCell} color: #1f2937;">${lead.tools_used.join(', ')}</td></tr>` : ''}
              </table>

              ${lead.notes ? `
              <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 0 8px 8px 0; margin-bottom: 24px;">
                <p style="margin:0; font-weight: bold; color: #92400e;">Notas:</p>
                <p style="margin: 8px 0 0; color: #78350f;">${lead.notes}</p>
              </div>` : ''}

              <!-- CTA -->
              <table cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                <tr>
                  <td style="${BASE_STYLES.cta}">
                    <a href="mailto:${lead.email}?subject=Tu solicitud en Automatización Procesos IA" style="${BASE_STYLES.ctaLink}">
                      Contactar a ${lead.name?.split(' ')[0] ?? 'este lead'} →
                    </a>
                  </td>
                </tr>
              </table>
            </div>

            <!-- Footer -->
            <div style="${BASE_STYLES.footer}">
              ${lead.id ? `<p style="${BASE_STYLES.footerText} text-align: center; margin-bottom: 8px;">ID de lead: ${lead.id}</p>` : ''}
              ${FOOTER_LEGAL}
            </div>
          </div>
        </td></tr>
      </table>
    </body>
    </html>
  `
}

// ─── Email de confirmación al cliente ─────────────────────────────────────────

export function emailConfirmacionCliente(lead: Lead): string {
  return `
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0; padding:0; ${BASE_STYLES.container}">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td>
          <div style="${BASE_STYLES.card}">
            <div style="${BASE_STYLES.header}">
              <h1 style="${BASE_STYLES.h1}">Automatización Procesos IA</h1>
              <p style="${BASE_STYLES.subtitle}">Consultora de Inteligencia Artificial</p>
            </div>

            <div style="${BASE_STYLES.body}">
              <h2 style="${BASE_STYLES.h2}">Hola, ${lead.name?.split(' ')[0] ?? 'bienvenido/a'} 👋</h2>
              <p style="${BASE_STYLES.p}">
                Hemos recibido tu solicitud y nos pondremos en contacto contigo en <strong>menos de 24 horas laborables</strong> para confirmar la videollamada gratuita de 45 minutos.
              </p>
              <p style="${BASE_STYLES.p}">
                En esa llamada, un consultor de Automatización Procesos IA analizará junto a ti:
              </p>
              <ul style="color: #374151; line-height: 1.8; font-size: 15px; padding-left: 20px; margin-bottom: 24px;">
                <li>Qué procesos de tu empresa tienen mayor potencial de automatización</li>
                <li>Qué soluciones de IA se adaptan mejor a tu sector y tamaño</li>
                <li>Cuál sería el ROI estimado de implementar IA en tu organización</li>
                <li>Por dónde empezar y cuáles serían los siguientes pasos</li>
              </ul>

              <div style="background: #eff6ff; border-radius: 8px; padding: 20px; margin-bottom: 28px;">
                <p style="margin: 0; font-size: 14px; color: #1e40af; font-weight: 600;">📅 Tu solicitud</p>
                ${lead.preferred_contact_time ? `<p style="margin: 8px 0 0; font-size: 14px; color: #374151;">Disponibilidad indicada: <strong>${lead.preferred_contact_time}</strong></p>` : ''}
                <p style="margin: 8px 0 0; font-size: 14px; color: #374151;">Te contactaremos a: <strong>${lead.email}</strong>${lead.phone ? ` y al ${lead.phone}` : ''}</p>
              </div>

              <table cellpadding="0" cellspacing="0" style="margin: 0 auto 28px;">
                <tr>
                  <td style="${BASE_STYLES.cta}">
                    <a href="https://automatizacionprocesos.es/servicios" style="${BASE_STYLES.ctaLink}">Explorar nuestros servicios →</a>
                  </td>
                </tr>
              </table>

              <p style="color: #6b7280; font-size: 13px; margin: 0;">
                ¿Tienes alguna pregunta? Escríbenos a 
                <a href="mailto:admin@automatizacionprocesos.es" style="color: #1e40af;">admin@automatizacionprocesos.es</a>
              </p>
            </div>

            <div style="${BASE_STYLES.footer}">
              ${FOOTER_LEGAL}
            </div>
          </div>
        </td></tr>
      </table>
    </body>
    </html>
  `
}

// ─── Email de seguimiento (48h sin agendar) ───────────────────────────────────

export function emailSeguimiento(lead: Lead): string {
  return `
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0; padding:0; ${BASE_STYLES.container}">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td>
          <div style="${BASE_STYLES.card}">
            <div style="${BASE_STYLES.header}">
              <h1 style="${BASE_STYLES.h1}">Automatización Procesos IA</h1>
              <p style="${BASE_STYLES.subtitle}">Consultora de Inteligencia Artificial</p>
            </div>
            <div style="${BASE_STYLES.body}">
              <h2 style="${BASE_STYLES.h2}">Hola de nuevo, ${lead.name?.split(' ')[0] ?? ''} 👋</h2>
              <p style="${BASE_STYLES.p}">
                Hace unos días mostraste interés en cómo la inteligencia artificial puede transformar tu empresa. Queremos asegurarnos de que tienes toda la información que necesitas.
              </p>
              <p style="${BASE_STYLES.p}">
                Nuestra videollamada gratuita de 45 minutos sigue disponible para ti. Sin compromiso, solo una conversación honesta sobre lo que la IA puede hacer por ${lead.company ?? 'tu empresa'}.
              </p>
              <table cellpadding="0" cellspacing="0" style="margin: 24px auto 28px;">
                <tr>
                  <td style="${BASE_STYLES.cta}">
                    <a href="https://automatizacionprocesos.es/diagnostico-gratuito" style="${BASE_STYLES.ctaLink}">Reservar mi videollamada gratuita →</a>
                  </td>
                </tr>
              </table>
              <p style="color: #6b7280; font-size: 13px;">
                Si ya no estás interesado/a, no te preocupes. No recibirás más correos de seguimiento.
              </p>
            </div>
            <div style="${BASE_STYLES.footer}">${FOOTER_LEGAL}</div>
          </div>
        </td></tr>
      </table>
    </body>
    </html>
  `
}

// ─── Email post-reunión ───────────────────────────────────────────────────────

export function emailPostReunion(lead: Lead): string {
  return `
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0; padding:0; ${BASE_STYLES.container}">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td>
          <div style="${BASE_STYLES.card}">
            <div style="${BASE_STYLES.header}">
              <h1 style="${BASE_STYLES.h1}">Automatización Procesos IA</h1>
              <p style="${BASE_STYLES.subtitle}">Consultora de Inteligencia Artificial</p>
            </div>
            <div style="${BASE_STYLES.body}">
              <h2 style="${BASE_STYLES.h2}">¡Gracias por tu tiempo, ${lead.name?.split(' ')[0] ?? ''}! 🙏</h2>
              <p style="${BASE_STYLES.p}">
                Ha sido un placer conocer ${lead.company ?? 'tu empresa'} y entender vuestros retos. Como hemos comentado, hay un potencial muy interesante para implementar soluciones de IA en vuestro día a día.
              </p>
              <p style="${BASE_STYLES.p}">
                En los próximos <strong>2 días laborables</strong> recibirás una propuesta personalizada con las soluciones que mejor se adaptan a vuestras necesidades y un plan de implementación detallado.
              </p>
              <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 16px; border-radius: 0 8px 8px 0; margin: 24px 0;">
                <p style="margin:0; color: #15803d; font-weight: 600; font-size: 14px;">📌 Próximos pasos acordados:</p>
                <ul style="color: #166534; font-size: 14px; margin: 8px 0 0; padding-left: 16px; line-height: 1.8;">
                  <li>Envío de propuesta personalizada (48h)</li>
                  <li>Revisión conjunta de la propuesta</li>
                  <li>Inicio del proyecto (si hay acuerdo)</li>
                </ul>
              </div>
              <table cellpadding="0" cellspacing="0" style="margin: 24px auto 28px;">
                <tr>
                  <td style="${BASE_STYLES.cta}">
                    <a href="https://automatizacionprocesos.es" style="${BASE_STYLES.ctaLink}">Explorar casos de éxito →</a>
                  </td>
                </tr>
              </table>
            </div>
            <div style="${BASE_STYLES.footer}">${FOOTER_LEGAL}</div>
          </div>
        </td></tr>
      </table>
    </body>
    </html>
  `
}

// ─── Email propuesta comercial ────────────────────────────────────────────────

export function emailPropuesta(lead: Lead): string {
  return `
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0; padding:0; ${BASE_STYLES.container}">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td>
          <div style="${BASE_STYLES.card}">
            <div style="${BASE_STYLES.header}">
              <h1 style="${BASE_STYLES.h1}">Automatización Procesos IA</h1>
              <p style="${BASE_STYLES.subtitle}">Propuesta Personalizada</p>
            </div>
            <div style="${BASE_STYLES.body}">
              <h2 style="${BASE_STYLES.h2}">Tu propuesta personalizada está lista, ${lead.name?.split(' ')[0] ?? ''} 🚀</h2>
              <p style="${BASE_STYLES.p}">
                Hemos preparado una propuesta específica para ${lead.company ?? 'tu empresa'}, basada en la conversación que mantuvimos y en el análisis de vuestras necesidades.
              </p>
              <p style="${BASE_STYLES.p}">
                La propuesta incluye soluciones de IA adaptadas a ${lead.employees_range ?? 'vuestro tamaño'}, con un plan de implementación por fases, estimación de costes y ROI esperado.
              </p>
              <div style="background: #eff6ff; border-radius: 8px; padding: 20px; margin: 24px 0;">
                <p style="margin: 0; font-size: 14px; color: #1e40af; font-weight: 600;">📎 Contenido de la propuesta:</p>
                <ul style="color: #1e40af; font-size: 14px; margin: 8px 0 0; padding-left: 16px; line-height: 1.8;">
                  <li>Diagnóstico de procesos automatizables</li>
                  <li>Soluciones recomendadas con stack tecnológico</li>
                  <li>Plan de implementación (roadmap)</li>
                  <li>Inversión y ROI estimado</li>
                  <li>Garantías y soporte</li>
                </ul>
              </div>
              <table cellpadding="0" cellspacing="0" style="margin: 24px auto 16px;">
                <tr>
                  <td style="${BASE_STYLES.cta}">
                    <a href="https://automatizacionprocesos.es/propuesta/${lead.id ?? ''}" style="${BASE_STYLES.ctaLink}">Ver mi propuesta completa →</a>
                  </td>
                </tr>
              </table>
              <p style="color: #6b7280; font-size: 13px; text-align: center;">
                Esta propuesta es válida durante 30 días. Cualquier duda, escríbenos a 
                <a href="mailto:admin@automatizacionprocesos.es" style="color: #1e40af;">admin@automatizacionprocesos.es</a>
              </p>
            </div>
            <div style="${BASE_STYLES.footer}">${FOOTER_LEGAL}</div>
          </div>
        </td></tr>
      </table>
    </body>
    </html>
  `
}
