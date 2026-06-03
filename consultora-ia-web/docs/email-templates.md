# Templates de Email — AP Automatización IA

Documentación y código HTML completo de los 5 emails transaccionales del sistema.

Todos los templates usan inline CSS para máxima compatibilidad con clientes de email (Gmail, Outlook, Apple Mail). Paleta de colores: índigo/púrpura (`#6366f1`) como color principal, gris oscuro (`#1f2937`) para textos.

---

## Email 1: Nuevo lead para el equipo comercial

**Asunto:** `🎯 Nuevo lead cualificado: [nombre] de [empresa]`

**Destinatario:** `hola@automatizacionprocesos.es` (equipo comercial)

**Cuándo se envía:** Inmediatamente tras recibir un nuevo lead via bot o formulario.

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nuevo Lead — AP Automatización IA</title>
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
          
          <!-- Cabecera -->
          <tr>
            <td style="background-color:#6366f1;border-radius:12px 12px 0 0;padding:24px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <span style="color:#ffffff;font-size:20px;font-weight:700;letter-spacing:-0.5px;">AP Automatización IA</span>
                  </td>
                  <td align="right">
                    <span style="background-color:#4f46e5;color:#ffffff;font-size:12px;font-weight:600;padding:4px 12px;border-radius:20px;">NUEVO LEAD</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- Score destacado -->
          <tr>
            <td style="background-color:#ffffff;padding:24px 32px 0;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background-color:#faf5ff;border:2px solid #6366f1;border-radius:8px;padding:16px 20px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td>
                          <p style="margin:0;font-size:13px;color:#7c3aed;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Lead Score</p>
                          <p style="margin:4px 0 0;font-size:36px;font-weight:800;color:#4f46e5;">{{lead_score}}/100</p>
                          <p style="margin:2px 0 0;font-size:14px;color:#6366f1;font-weight:500;">{{qualification}}</p>
                        </td>
                        <td align="right">
                          <p style="margin:0;font-size:13px;color:#6b7280;">Recibido</p>
                          <p style="margin:4px 0 0;font-size:15px;font-weight:600;color:#1f2937;">{{created_at_formatted}}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- Datos del lead -->
          <tr>
            <td style="background-color:#ffffff;padding:24px 32px;">
              <h2 style="margin:0 0 16px;font-size:18px;font-weight:700;color:#1f2937;">Datos del lead</h2>
              
              <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;width:40%;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Nombre</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:14px;color:#1f2937;font-weight:600;">{{name}}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Cargo</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:14px;color:#1f2937;">{{role}}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Empresa</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:14px;color:#1f2937;font-weight:600;">{{company}}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Email</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <a href="mailto:{{email}}" style="font-size:14px;color:#6366f1;text-decoration:none;">{{email}}</a>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Teléfono</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <a href="tel:{{phone}}" style="font-size:14px;color:#6366f1;text-decoration:none;">{{phone}}</a>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Sector</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:14px;color:#1f2937;">{{sector}}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Empleados</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:14px;color:#1f2937;">{{employees_range}}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Herramientas actuales</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:14px;color:#1f2937;">{{tools_used}}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Servicio de interés</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:14px;color:#1f2937;">{{service_interest}}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:13px;color:#6b7280;font-weight:500;">Urgencia</span>
                  </td>
                  <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="font-size:14px;color:#1f2937;">{{urgency}}</span>
                  </td>
                </tr>
              </table>
              
              <!-- Problema principal destacado -->
              <div style="margin-top:20px;background-color:#f9fafb;border-left:4px solid #6366f1;border-radius:0 6px 6px 0;padding:16px;">
                <p style="margin:0 0 6px;font-size:12px;font-weight:600;color:#6366f1;text-transform:uppercase;letter-spacing:0.05em;">Problema principal que describe</p>
                <p style="margin:0;font-size:14px;color:#374151;line-height:1.6;font-style:italic;">"{{main_problem}}"</p>
              </div>
            </td>
          </tr>
          
          <!-- CTAs -->
          <tr>
            <td style="background-color:#ffffff;padding:0 32px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding-right:8px;width:50%;">
                    <a href="{{supabase_dashboard_url}}" style="display:block;background-color:#6366f1;color:#ffffff;text-align:center;padding:12px;border-radius:6px;font-size:14px;font-weight:600;text-decoration:none;">
                      Ver en Supabase →
                    </a>
                  </td>
                  <td style="padding-left:8px;width:50%;">
                    <a href="mailto:{{email}}?subject=Hola {{name}}, soy del equipo de AP Automatización IA" style="display:block;background-color:#ffffff;color:#6366f1;text-align:center;padding:12px;border-radius:6px;font-size:14px;font-weight:600;text-decoration:none;border:2px solid #6366f1;">
                      Responder directamente
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="background-color:#f9fafb;border-radius:0 0 12px 12px;padding:16px 32px;border-top:1px solid #e5e7eb;">
              <p style="margin:0;font-size:12px;color:#9ca3af;text-align:center;">
                Email automático generado por el sistema de AP Automatización IA · 
                <a href="{{supabase_dashboard_url}}" style="color:#6366f1;text-decoration:none;">Ver todos los leads</a>
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
  
</body>
</html>
```

---

## Email 2: Confirmación al cliente

**Asunto:** `Hemos recibido tu solicitud de diagnóstico — AP Automatización IA`

**Destinatario:** Email del lead

**Cuándo se envía:** Inmediatamente tras registrar el lead.

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Confirmación — AP Automatización IA</title>
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
          
          <!-- Cabecera con gradiente -->
          <tr>
            <td style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);border-radius:12px 12px 0 0;padding:40px 32px;text-align:center;">
              <p style="margin:0 0 8px;font-size:13px;font-weight:600;color:#c4b5fd;text-transform:uppercase;letter-spacing:0.1em;">AP Automatización IA</p>
              <h1 style="margin:0;font-size:26px;font-weight:800;color:#ffffff;line-height:1.3;">
                Hemos recibido tu solicitud ✓
              </h1>
              <p style="margin:12px 0 0;font-size:16px;color:#e0e7ff;">
                Gracias, {{name}}. Nos ponemos en contacto contigo en menos de 24 horas.
              </p>
            </td>
          </tr>
          
          <!-- Cuerpo principal -->
          <tr>
            <td style="background-color:#ffffff;padding:32px;">
              
              <p style="margin:0 0 16px;font-size:15px;color:#374151;line-height:1.7;">
                Hola {{name}},
              </p>
              <p style="margin:0 0 24px;font-size:15px;color:#374151;line-height:1.7;">
                Acabamos de recibir tu solicitud de diagnóstico gratuito para <strong>{{company}}</strong>. Hemos anotado que tu mayor reto ahora mismo es:
              </p>
              
              <!-- Problema destacado -->
              <div style="background-color:#faf5ff;border:1px solid #e9d5ff;border-radius:8px;padding:20px;margin-bottom:24px;">
                <p style="margin:0;font-size:14px;color:#7c3aed;font-style:italic;line-height:1.6;">"{{main_problem}}"</p>
              </div>
              
              <p style="margin:0 0 24px;font-size:15px;color:#374151;line-height:1.7;">
                Esto es exactamente el tipo de problema que resolvemos para empresas del sector {{sector}}. 
                Nuestro equipo ya está revisando tu caso para preparar las preguntas clave de vuestra primera conversación.
              </p>
              
              <!-- Qué pasará -->
              <h2 style="margin:0 0 16px;font-size:16px;font-weight:700;color:#1f2937;">¿Qué pasa ahora?</h2>
              
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="vertical-align:top;padding:12px 0;border-bottom:1px solid #f3f4f6;">
                    <table cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="vertical-align:top;padding-right:16px;">
                          <div style="width:28px;height:28px;background-color:#6366f1;border-radius:50%;text-align:center;line-height:28px;">
                            <span style="color:#ffffff;font-size:13px;font-weight:700;">1</span>
                          </div>
                        </td>
                        <td>
                          <p style="margin:0;font-size:14px;font-weight:600;color:#1f2937;">En las próximas 24 horas</p>
                          <p style="margin:4px 0 0;font-size:13px;color:#6b7280;line-height:1.5;">Un consultor de AP Automatización IA te contactará por email o teléfono para presentarse y confirmar los detalles de vuestro diagnóstico.</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="vertical-align:top;padding:12px 0;border-bottom:1px solid #f3f4f6;">
                    <table cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="vertical-align:top;padding-right:16px;">
                          <div style="width:28px;height:28px;background-color:#8b5cf6;border-radius:50%;text-align:center;line-height:28px;">
                            <span style="color:#ffffff;font-size:13px;font-weight:700;">2</span>
                          </div>
                        </td>
                        <td>
                          <p style="margin:0;font-size:14px;font-weight:600;color:#1f2937;">Diagnóstico gratuito (30 min)</p>
                          <p style="margin:4px 0 0;font-size:13px;color:#6b7280;line-height:1.5;">Analizamos vuestros procesos actuales, identificamos dónde la IA puede aportar más valor y te damos una hoja de ruta sin compromiso.</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="vertical-align:top;padding:12px 0;">
                    <table cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="vertical-align:top;padding-right:16px;">
                          <div style="width:28px;height:28px;background-color:#a78bfa;border-radius:50%;text-align:center;line-height:28px;">
                            <span style="color:#ffffff;font-size:13px;font-weight:700;">3</span>
                          </div>
                        </td>
                        <td>
                          <p style="margin:0;font-size:14px;font-weight:600;color:#1f2937;">Propuesta personalizada</p>
                          <p style="margin:4px 0 0;font-size:13px;color:#6b7280;line-height:1.5;">Si hay encaje, te enviamos una propuesta detallada con casos similares al vuestro, ROI estimado y plan de implementación.</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              
              <!-- CTA Calendly -->
              <div style="background-color:#f9fafb;border-radius:8px;padding:20px;margin-top:24px;text-align:center;">
                <p style="margin:0 0 12px;font-size:14px;color:#374151;">¿Prefieres elegir tú la fecha y hora? Reserva directamente aquí:</p>
                <a href="{{calendly_url}}" style="display:inline-block;background-color:#6366f1;color:#ffffff;padding:12px 28px;border-radius:6px;font-size:14px;font-weight:600;text-decoration:none;">
                  Reservar mi diagnóstico gratuito →
                </a>
              </div>
              
            </td>
          </tr>
          
          <!-- Recursos -->
          <tr>
            <td style="background-color:#f9fafb;padding:24px 32px;border-top:1px solid #e5e7eb;">
              <p style="margin:0 0 12px;font-size:13px;font-weight:600;color:#374151;">Mientras tanto, puede interesarte:</p>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding-right:8px;width:33%;">
                    <a href="https://www.automatizacionprocesos.es/blog" style="display:block;background-color:#ffffff;border:1px solid #e5e7eb;border-radius:6px;padding:12px;text-align:center;text-decoration:none;">
                      <p style="margin:0;font-size:12px;font-weight:600;color:#6366f1;">Blog IA</p>
                      <p style="margin:4px 0 0;font-size:11px;color:#9ca3af;">Guías y casos prácticos</p>
                    </a>
                  </td>
                  <td style="padding:0 4px;width:33%;">
                    <a href="https://www.automatizacionprocesos.es/casos-de-uso" style="display:block;background-color:#ffffff;border:1px solid #e5e7eb;border-radius:6px;padding:12px;text-align:center;text-decoration:none;">
                      <p style="margin:0;font-size:12px;font-weight:600;color:#6366f1;">Casos reales</p>
                      <p style="margin:4px 0 0;font-size:11px;color:#9ca3af;">Resultados de clientes</p>
                    </a>
                  </td>
                  <td style="padding-left:8px;width:33%;">
                    <a href="https://www.instagram.com/automatizacionprocesos.es" style="display:block;background-color:#ffffff;border:1px solid #e5e7eb;border-radius:6px;padding:12px;text-align:center;text-decoration:none;">
                      <p style="margin:0;font-size:12px;font-weight:600;color:#6366f1;">Instagram</p>
                      <p style="margin:4px 0 0;font-size:11px;color:#9ca3af;">Consejos diarios de IA</p>
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="background-color:#1f2937;border-radius:0 0 12px 12px;padding:24px 32px;">
              <p style="margin:0 0 4px;font-size:14px;font-weight:700;color:#ffffff;">AP Automatización IA</p>
              <p style="margin:0 0 12px;font-size:12px;color:#9ca3af;">Calle Gran Vía 28, 28013 Madrid · hola@automatizacionprocesos.es · +34 900 000 000</p>
              <p style="margin:0;font-size:11px;color:#6b7280;">
                Has recibido este email porque solicitaste información en automatizacionprocesos.es. 
                <a href="{{unsubscribe_url}}" style="color:#6366f1;text-decoration:none;">Cancelar suscripción</a>
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
  
</body>
</html>
```

---

## Email 3: Seguimiento (sin reunión tras 48h)

**Asunto:** `¿Pudiste revisar tu diagnóstico gratuito? 👋`

**Destinatario:** Email del lead

**Cuándo se envía:** 48 horas después de crearse el lead si sigue en estado `nuevo`.

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Seguimiento — AP Automatización IA</title>
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
          
          <tr>
            <td style="background-color:#6366f1;border-radius:12px 12px 0 0;padding:20px 32px;">
              <span style="color:#ffffff;font-size:18px;font-weight:700;">AP Automatización IA</span>
            </td>
          </tr>
          
          <tr>
            <td style="background-color:#ffffff;padding:32px;border-radius:0 0 12px 12px;">
              
              <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">
                Hola {{name}},
              </p>
              
              <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">
                El otro día nos dejaste tu solicitud de diagnóstico gratuito y quería asegurarme de que llegó bien y de que tienes toda la información que necesitas.
              </p>
              
              <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">
                Sé que el día a día en una empresa de {{employees_range}} personas no para, así que lo entiendo perfectamente si todavía no has tenido un hueco.
              </p>
              
              <!-- Mini propuesta de valor -->
              <div style="background-color:#faf5ff;border-radius:8px;padding:20px;margin-bottom:24px;">
                <p style="margin:0 0 12px;font-size:14px;font-weight:700;color:#4f46e5;">Lo que hemos hecho para empresas similares a {{company}}:</p>
                <ul style="margin:0;padding-left:20px;">
                  <li style="margin-bottom:8px;font-size:14px;color:#374151;line-height:1.5;">Reducción del 70% del tiempo en gestión administrativa</li>
                  <li style="margin-bottom:8px;font-size:14px;color:#374151;line-height:1.5;">Atención al cliente 24/7 con agentes IA que resuelven el 60% de consultas sin intervención humana</li>
                  <li style="margin-bottom:8px;font-size:14px;color:#374151;line-height:1.5;">Análisis de datos en tiempo real sin necesidad de contratar analistas adicionales</li>
                </ul>
              </div>
              
              <p style="margin:0 0 24px;font-size:15px;color:#374151;line-height:1.7;">
                La llamada de diagnóstico dura solo 30 minutos y no tiene ningún compromiso. El objetivo es que salgas con claridad sobre si la IA tiene sentido para vosotros ahora mismo, y si es que sí, por dónde empezar.
              </p>
              
              <!-- CTA principal -->
              <div style="text-align:center;margin-bottom:24px;">
                <a href="{{calendly_url}}" style="display:inline-block;background-color:#6366f1;color:#ffffff;padding:14px 32px;border-radius:6px;font-size:15px;font-weight:600;text-decoration:none;">
                  Reservar mi diagnóstico gratuito (30 min) →
                </a>
              </div>
              
              <p style="margin:0 0 8px;font-size:14px;color:#6b7280;">O si prefieres, responde a este email y lo organizamos directamente.</p>
              
              <p style="margin:24px 0 0;font-size:14px;color:#374151;">
                Un saludo,<br>
                <strong>Equipo AP Automatización IA</strong><br>
                <span style="color:#6b7280;">hola@automatizacionprocesos.es · +34 900 000 000</span>
              </p>
              
              <hr style="border:none;border-top:1px solid #f3f4f6;margin:24px 0;">
              
              <p style="margin:0;font-size:11px;color:#9ca3af;">
                AP Automatización IA · Calle Gran Vía 28, 28013 Madrid · 
                <a href="{{unsubscribe_url}}" style="color:#6366f1;text-decoration:none;">No quiero recibir más emails</a>
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
  
</body>
</html>
```

---

## Email 4: Post reunión

**Asunto:** `Resumen de nuestra reunión — próximos pasos`

**Destinatario:** Email del lead

**Cuándo se envía:** Tras marcar la reunión como realizada en el CRM / webhook post-reunión.

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Resumen reunión — AP Automatización IA</title>
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
          
          <tr>
            <td style="background-color:#1f2937;border-radius:12px 12px 0 0;padding:24px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <span style="color:#ffffff;font-size:18px;font-weight:700;">AP Automatización IA</span>
                  </td>
                  <td align="right">
                    <span style="color:#9ca3af;font-size:13px;">Reunión del {{meeting_date}}</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <tr>
            <td style="background-color:#ffffff;padding:32px;">
              
              <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">
                Hola {{name}},
              </p>
              
              <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">
                Muchas gracias por el tiempo que has dedicado hoy a la llamada. Ha sido muy interesante entender en profundidad cómo funciona {{company}} y los retos que estáis afrontando.
              </p>
              
              <!-- Resumen de lo hablado -->
              <div style="background-color:#f9fafb;border-radius:8px;padding:24px;margin-bottom:24px;border:1px solid #e5e7eb;">
                <h2 style="margin:0 0 16px;font-size:16px;font-weight:700;color:#1f2937;">📋 Resumen de lo hablado</h2>
                <p style="margin:0;font-size:14px;color:#374151;line-height:1.7;">{{meeting_notes}}</p>
              </div>
              
              <!-- Próximos pasos -->
              <div style="background-color:#faf5ff;border-radius:8px;padding:24px;margin-bottom:24px;">
                <h2 style="margin:0 0 16px;font-size:16px;font-weight:700;color:#4f46e5;">✅ Próximos pasos</h2>
                <p style="margin:0;font-size:14px;color:#374151;line-height:1.7;">{{next_steps}}</p>
              </div>
              
              <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">
                Estamos preparando la propuesta personalizada para {{company}} y te la enviaremos en los próximos días. Incluirá el detalle técnico, el plan de implementación y el ROI estimado basándonos en datos del sector.
              </p>
              
              <p style="margin:0 0 8px;font-size:14px;color:#374151;">Si mientras tanto tienes cualquier pregunta, responde a este email o escríbeme directamente:</p>
              
              <p style="margin:0 0 24px;font-size:14px;color:#374151;">
                <a href="tel:+34900000000" style="color:#6366f1;text-decoration:none;">+34 900 000 000</a> · 
                <a href="mailto:hola@automatizacionprocesos.es" style="color:#6366f1;text-decoration:none;">hola@automatizacionprocesos.es</a>
              </p>
              
              <p style="margin:0;font-size:14px;color:#374151;">
                Hasta pronto,<br>
                <strong>Equipo AP Automatización IA</strong>
              </p>
              
            </td>
          </tr>
          
          <tr>
            <td style="background-color:#f9fafb;border-radius:0 0 12px 12px;padding:16px 32px;border-top:1px solid #e5e7eb;">
              <p style="margin:0;font-size:11px;color:#9ca3af;text-align:center;">
                AP Automatización IA · Calle Gran Vía 28, 28013 Madrid · 
                <a href="{{unsubscribe_url}}" style="color:#6366f1;text-decoration:none;">Gestionar preferencias de email</a>
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
  
</body>
</html>
```

---

## Email 5: Envío de propuesta

**Asunto:** `Tu propuesta personalizada de AP Automatización IA — {{company}}`

**Destinatario:** Email del lead

**Cuándo se envía:** Manualmente por el equipo comercial al enviar la propuesta.

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Propuesta — AP Automatización IA</title>
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
          
          <!-- Cabecera premium -->
          <tr>
            <td style="background:linear-gradient(135deg,#1f2937 0%,#4f46e5 100%);border-radius:12px 12px 0 0;padding:40px 32px;text-align:center;">
              <p style="margin:0 0 8px;font-size:13px;font-weight:600;color:#a5b4fc;text-transform:uppercase;letter-spacing:0.1em;">AP Automatización IA</p>
              <h1 style="margin:0;font-size:28px;font-weight:800;color:#ffffff;line-height:1.3;">
                Tu propuesta personalizada
              </h1>
              <p style="margin:12px 0 0;font-size:16px;color:#c7d2fe;">
                Preparada específicamente para {{company}}
              </p>
            </td>
          </tr>
          
          <tr>
            <td style="background-color:#ffffff;padding:32px;">
              
              <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">
                Hola {{name}},
              </p>
              
              <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">
                Como acordamos, adjunto encontrarás la propuesta personalizada para {{company}}. La hemos preparado teniendo en cuenta todo lo que hablamos: vuestros procesos actuales, el equipo involucrado y los objetivos que queréis conseguir.
              </p>
              
              <!-- Resumen de valor -->
              <div style="background-color:#f9fafb;border-radius:8px;padding:24px;margin-bottom:24px;border:1px solid #e5e7eb;">
                <h2 style="margin:0 0 16px;font-size:16px;font-weight:700;color:#1f2937;">💡 Resumen de lo que incluye</h2>
                
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="padding:8px 0;border-bottom:1px solid #f3f4f6;vertical-align:top;">
                      <span style="font-size:14px;color:#6b7280;">Solución</span>
                    </td>
                    <td style="padding:8px 0;border-bottom:1px solid #f3f4f6;vertical-align:top;">
                      <span style="font-size:14px;font-weight:600;color:#1f2937;">{{solution_summary}}</span>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;border-bottom:1px solid #f3f4f6;vertical-align:top;">
                      <span style="font-size:14px;color:#6b7280;">Tiempo de implementación</span>
                    </td>
                    <td style="padding:8px 0;border-bottom:1px solid #f3f4f6;vertical-align:top;">
                      <span style="font-size:14px;font-weight:600;color:#1f2937;">{{implementation_time}}</span>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;border-bottom:1px solid #f3f4f6;vertical-align:top;">
                      <span style="font-size:14px;color:#6b7280;">ROI estimado</span>
                    </td>
                    <td style="padding:8px 0;border-bottom:1px solid #f3f4f6;vertical-align:top;">
                      <span style="font-size:14px;font-weight:600;color:#059669;">{{roi_estimate}}</span>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;vertical-align:top;">
                      <span style="font-size:14px;color:#6b7280;">Inversión</span>
                    </td>
                    <td style="padding:8px 0;vertical-align:top;">
                      <span style="font-size:14px;font-weight:700;color:#6366f1;">{{price}}</span>
                    </td>
                  </tr>
                </table>
              </div>
              
              <p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">
                La propuesta tiene una validez de <strong>15 días naturales</strong>. Si tienes cualquier pregunta sobre el documento o quieres ajustar algún punto, dímelo y lo revisamos.
              </p>
              
              <!-- CTAs -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                <tr>
                  <td style="padding-right:8px;width:50%;">
                    <a href="{{proposal_link}}" style="display:block;background-color:#6366f1;color:#ffffff;text-align:center;padding:14px;border-radius:6px;font-size:14px;font-weight:600;text-decoration:none;">
                      Ver propuesta online →
                    </a>
                  </td>
                  <td style="padding-left:8px;width:50%;">
                    <a href="{{calendly_url}}" style="display:block;background-color:#ffffff;color:#6366f1;text-align:center;padding:14px;border-radius:6px;font-size:14px;font-weight:600;text-decoration:none;border:2px solid #6366f1;">
                      Hablar sobre la propuesta
                    </a>
                  </td>
                </tr>
              </table>
              
              <!-- Datos bancarios / pago -->
              <div style="background-color:#faf5ff;border-radius:8px;padding:20px;margin-bottom:24px;">
                <h3 style="margin:0 0 12px;font-size:14px;font-weight:700;color:#4f46e5;">Datos para formalizar el proyecto</h3>
                <p style="margin:0 0 4px;font-size:13px;color:#374151;"><strong>Empresa:</strong> AP Automatización IA Consulting S.L.</p>
                <p style="margin:0 0 4px;font-size:13px;color:#374151;"><strong>CIF:</strong> B-XXXXXXXXX</p>
                <p style="margin:0 0 4px;font-size:13px;color:#374151;"><strong>IBAN:</strong> ES12 1234 5678 9012 3456 7890</p>
                <p style="margin:0 0 4px;font-size:13px;color:#374151;"><strong>Forma de pago:</strong> 50% al firmar, 50% al entregar</p>
                <p style="margin:0;font-size:12px;color:#9ca3af;margin-top:8px;">También aceptamos Stripe (tarjeta/transferencia), Bizum empresarial y Stripe Checkout.</p>
              </div>
              
              <p style="margin:0;font-size:14px;color:#374151;">
                Muchas gracias por la confianza, {{name}}. Estamos deseando trabajar con {{company}}.<br><br>
                Un saludo,<br>
                <strong>Equipo AP Automatización IA</strong><br>
                <span style="color:#6b7280;">hola@automatizacionprocesos.es · +34 900 000 000</span>
              </p>
              
            </td>
          </tr>
          
          <tr>
            <td style="background-color:#1f2937;border-radius:0 0 12px 12px;padding:20px 32px;">
              <p style="margin:0;font-size:11px;color:#6b7280;text-align:center;">
                © 2025 AP Automatización IA Consulting S.L. · Calle Gran Vía 28, 28013 Madrid · 
                <a href="{{unsubscribe_url}}" style="color:#6366f1;text-decoration:none;">Gestionar emails</a>
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
  
</body>
</html>
```

---

## Variables de sustitución (placeholders)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `{{name}}` | Nombre del lead | María García |
| `{{email}}` | Email del lead | maria@empresa.es |
| `{{phone}}` | Teléfono | +34612345678 |
| `{{company}}` | Nombre de la empresa | Distribuciones García S.L. |
| `{{role}}` | Cargo | Directora de Operaciones |
| `{{sector}}` | Sector | Logística |
| `{{employees_range}}` | Rango de empleados | 50-200 |
| `{{main_problem}}` | Problema descrito por el lead | Texto libre |
| `{{lead_score}}` | Puntuación del lead | 82 |
| `{{qualification}}` | Cualificación | muy-caliente |
| `{{tools_used}}` | Herramientas actuales | Excel, SAP |
| `{{urgency}}` | Urgencia | Este trimestre |
| `{{created_at_formatted}}` | Fecha formateada | 15 jun 2025, 10:30 |
| `{{meeting_date}}` | Fecha de la reunión | 15 de junio de 2025 |
| `{{meeting_notes}}` | Notas de la reunión | Texto libre |
| `{{next_steps}}` | Próximos pasos acordados | Texto libre |
| `{{solution_summary}}` | Resumen de la solución propuesta | Automatización del proceso de albaranes |
| `{{implementation_time}}` | Tiempo estimado | 6-8 semanas |
| `{{roi_estimate}}` | ROI estimado | Recuperación de la inversión en 4 meses |
| `{{price}}` | Precio de la propuesta | 12.000 € + IVA |
| `{{calendly_url}}` | Link de Calendly | https://calendly.com/apautomatizacion/... |
| `{{proposal_link}}` | Link a la propuesta online | https://... |
| `{{supabase_dashboard_url}}` | Link al dashboard de Supabase | https://... |
| `{{unsubscribe_url}}` | Link de baja | https://www.automatizacionprocesos.es/baja?token=... |
