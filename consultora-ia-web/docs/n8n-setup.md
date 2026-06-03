# Configuración de n8n — AP Automatización IA

Esta documentación describe los tres flujos de automatización de n8n que procesan los leads captados por la web de AP Automatización IA.

## Visión general de los flujos

| Flujo | Disparador | Propósito |
|-------|------------|-----------|
| Flujo 1: Nuevo Lead | Webhook POST | Procesar un lead nuevo del formulario de diagnóstico |
| Flujo 2: Seguimiento 48h | Schedule (cada hora) | Enviar email de seguimiento a leads sin respuesta |
| Flujo 3: Post Reunión | Webhook manual | Enviar materiales y próximos pasos tras una reunión |

---

## Flujo 1: Nuevo Lead

### Descripción
Se activa cuando el formulario de diagnóstico de la web envía los datos al webhook. Guarda el lead en Supabase, envía email de confirmación al lead, notifica al equipo por email y opcionalmente por Telegram.

### Nodos del flujo

```
Webhook (POST) →
  Validar datos →
    Insertar en Supabase (tabla leads) →
      Email confirmación al lead (Resend) →
        Email notificación al equipo (Resend) →
          [Opcional] Notificación Telegram
```

### Configuración del Webhook

- **Método:** POST
- **URL de producción:** `https://tu-n8n.app.n8n.cloud/webhook/nuevo-lead`
- **Authentication:** Header `X-Webhook-Secret: {{$credentials.webhookSecret}}`
- **Respuesta:** HTTP 200 con `{ "success": true, "lead_id": "..." }`

### Ejemplo de body del webhook de entrada

```json
{
  "lead_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "María García",
  "email": "maria.garcia@empresa.com",
  "phone": "+34 666 123 456",
  "company": "Distribuciones García SL",
  "company_size": "11-50",
  "sector": "distribución",
  "current_tools": "Excel, email, un CRM básico",
  "main_challenge": "Perdemos mucho tiempo procesando facturas de proveedores manualmente. Somos 3 personas en administración y dedicamos casi 2 días a la semana solo a esto.",
  "budget_range": "2000-5000",
  "timeline": "3-6 meses",
  "lead_score": 75,
  "intent": "automatizacion",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "automatizacion-facturas",
  "created_at": "2026-06-03T10:32:00.000Z",
  "ip_country": "ES"
}
```

### Nodo: Insertar en Supabase

- **Operación:** Insert
- **Tabla:** `leads`
- **Campos a mapear:** todos los campos del body anterior
- **Campo adicional a añadir:** `status: 'nuevo'`, `notified_at: new Date().toISOString()`

### Nodo: Email confirmación al lead

- **Servicio:** Resend (credencial configurada en n8n)
- **From:** `hola@automatizacionprocesos.es`
- **To:** `{{$json.email}}`
- **Subject:** `Tu diagnóstico gratuito está confirmado, {{$json.name.split(' ')[0]}}`
- **Body:** usar plantilla HTML de `lib/email-templates.ts` > `diagnosticConfirmation`

### Nodo: Email notificación al equipo

- **To:** `hola@automatizacionprocesos.es`
- **Subject:** `Nuevo lead: {{$json.company}} (puntuación: {{$json.lead_score}})`
- **Body HTML:**
```html
<h2>Nuevo lead recibido</h2>
<table>
  <tr><td><strong>Nombre:</strong></td><td>{{$json.name}}</td></tr>
  <tr><td><strong>Empresa:</strong></td><td>{{$json.company}}</td></tr>
  <tr><td><strong>Email:</strong></td><td>{{$json.email}}</td></tr>
  <tr><td><strong>Teléfono:</strong></td><td>{{$json.phone}}</td></tr>
  <tr><td><strong>Sector:</strong></td><td>{{$json.sector}}</td></tr>
  <tr><td><strong>Lead score:</strong></td><td>{{$json.lead_score}}/100</td></tr>
  <tr><td><strong>Intención:</strong></td><td>{{$json.intent}}</td></tr>
  <tr><td><strong>Reto principal:</strong></td><td>{{$json.main_challenge}}</td></tr>
  <tr><td><strong>Presupuesto:</strong></td><td>{{$json.budget_range}} €</td></tr>
</table>
<a href="https://supabase.com/dashboard/project/TU_PROJECT/table-editor" style="background:#2563EB;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;">Ver en Supabase</a>
```

---

## Flujo 2: Seguimiento a las 48 horas

### Descripción
Se ejecuta cada hora. Busca en Supabase los leads que: llevan más de 48 horas desde su creación, tienen status `nuevo` (no han sido contactados), y no han respondido. Envía un email de seguimiento personalizado.

### Nodos del flujo

```
Schedule Trigger (cada hora) →
  Consulta Supabase (leads pendientes) →
    IF hay leads pendientes →
      Loop por cada lead →
        Enviar email de seguimiento (Resend) →
          Actualizar status en Supabase →
            Notificar al equipo
```

### Nodo: Schedule Trigger

- **Intervalo:** cada 1 hora
- **Zona horaria:** Europe/Madrid

### Nodo: Consulta Supabase

- **Operación:** GetAll con filtros
- **Tabla:** `leads`
- **Filtros:**
  - `status` = `nuevo`
  - `created_at` <= `NOW() - INTERVAL '48 hours'`
  - `follow_up_sent` = `false`
- **Límite:** 50 registros por ejecución

### Query SQL directa (alternativa)

```sql
SELECT *
FROM leads
WHERE
  status = 'nuevo'
  AND created_at <= NOW() - INTERVAL '48 hours'
  AND follow_up_sent = false
ORDER BY lead_score DESC
LIMIT 50;
```

### Nodo: Email de seguimiento

- **Subject:** `¿Tienes 5 minutos esta semana, {{$json.name.split(' ')[0]}}?`
- **Body:** email de seguimiento personalizado con referencia al reto mencionado en el formulario.

### Nodo: Actualizar status en Supabase

- **Operación:** Update
- **Tabla:** `leads`
- **ID:** `{{$json.lead_id}}`
- **Campos:** `follow_up_sent: true`, `follow_up_sent_at: new Date().toISOString()`, `status: 'seguimiento_1'`

---

## Flujo 3: Post Reunión

### Descripción
Se activa manualmente desde el dashboard de n8n o mediante un webhook específico después de celebrar una reunión de diagnóstico con un lead. Envía los materiales acordados, la propuesta o los próximos pasos.

### Webhook de activación

- **URL:** `https://tu-n8n.app.n8n.cloud/webhook/post-reunion`
- **Método:** POST

### Body del webhook de activación

```json
{
  "lead_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "reunion_date": "2026-06-03T11:00:00.000Z",
  "outcome": "interesado",
  "next_step": "propuesta",
  "notes": "Interesados en automatizar el proceso de facturación. Tienen 150 facturas/mes. Presupuesto confirmado entre 3.000 y 5.000 €. Quieren propuesta formal en 48h.",
  "send_materials": true,
  "materials": ["caso-exito-distribucion", "metodologia-nexus"]
}
```

### Nodos del flujo

```
Webhook POST →
  Obtener datos del lead de Supabase →
    Actualizar status del lead (reunión realizada) →
      Enviar email con materiales y próximos pasos →
        Crear tarea de seguimiento (actualizar Supabase) →
          Notificar al equipo con resumen
```

---

## Variables de credenciales en n8n

Configurar en n8n bajo **Settings → Credentials**:

| Nombre de credencial | Tipo | Campos requeridos |
|---------------------|------|-------------------|
| `apautomatizacion-supabase` | HTTP Request | URL base, API Key (service role) |
| `apautomatizacion-resend` | HTTP Request | API Key de Resend |
| `apautomatizacion-webhook-secret` | Generic credential | Secreto para validar webhooks entrantes |
| `apautomatizacion-telegram` (opcional) | Telegram API | Bot Token, Chat ID |

## Cómo conectar credenciales de Supabase en n8n

1. En el dashboard de n8n, ir a **Settings → Credentials → New Credential**
2. Seleccionar tipo **Supabase** (si está disponible) o **HTTP Request** para mayor control
3. Para HTTP Request con Supabase:
   - **Base URL:** `https://tu-proyecto.supabase.co`
   - **Header:** `apikey: eyJ...` (tu SUPABASE_SERVICE_ROLE_KEY)
   - **Header:** `Authorization: Bearer eyJ...` (misma clave)
   - **Header:** `Content-Type: application/json`
4. Guardar la credencial con el nombre `apautomatizacion-supabase`
5. En cada nodo que use Supabase, seleccionar esta credencial en el campo Credential

## Activar y probar los flujos

1. **Flujo 1 (Nuevo Lead):** activar el webhook en n8n, copiar la URL y configurarla en `N8N_WEBHOOK_URL` del `.env.local`. Enviar una petición de prueba desde el formulario de diagnóstico en desarrollo.
2. **Flujo 2 (Seguimiento):** activar el schedule trigger. Para probar sin esperar, ejecutar el nodo de consulta Supabase manualmente con datos de prueba.
3. **Flujo 3 (Post Reunión):** activar el webhook. Probar enviando el body de ejemplo con cURL o Postman.

## Troubleshooting común

- **Webhook no recibe datos:** verificar que `N8N_WEBHOOK_URL` está correctamente configurado en Vercel y que el CORS del endpoint `/api/diagnostic/route.ts` permite la llamada.
- **Error en Supabase:** verificar que el service role key tiene permisos de INSERT/UPDATE en la tabla `leads`.
- **Email no llega:** verificar que el dominio `automatizacionprocesos.es` está verificado en Resend y que los registros DNS (DKIM, SPF) están configurados correctamente.
