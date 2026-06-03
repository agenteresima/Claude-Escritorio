# n8n — Guía de Automatización Completa

Esta guía documenta todos los flujos de automatización de Nexus IA, los payloads de webhook, las credenciales necesarias y cómo instalar n8n.

---

## Visión general de los flujos

| Flujo | Trigger | Propósito |
|-------|---------|-----------|
| Flujo 1: Nuevo Lead | Webhook POST desde la web | Notificar al equipo, enviar confirmación al cliente, registrar en Sheets |
| Flujo 2: Seguimiento 48h | Schedule diario 9:00 | Recordatorio a leads sin reunión agendada |
| Flujo 3: Post Reunión | Webhook manual desde CRM | Email post-reunión con resumen y próximos pasos |

---

## Instalación de n8n

### Opción A: n8n Cloud (recomendado para empezar)

1. Ve a [app.n8n.cloud](https://app.n8n.cloud) y crea una cuenta
2. Selecciona el plan **Starter** (gratis hasta 5.000 ejecuciones/mes)
3. Tu instancia estará en `https://TU-NOMBRE.app.n8n.cloud`
4. No necesitas gestionar servidores

### Opción B: Docker self-hosted

```bash
# docker-compose.yml para n8n
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=n8n.nexusia.es
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.nexusia.es
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=TU_PASSWORD_SEGURO
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=tu-postgres-host
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n_user
      - DB_POSTGRESDB_PASSWORD=TU_DB_PASSWORD
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

```bash
docker compose up -d
# Accede a http://localhost:5678
```

---

## Variables de entorno para n8n

En n8n, las variables de entorno se configuran en **Settings > Variables** (en n8n Cloud) o directamente en el `docker-compose.yml`.

| Variable | Valor |
|----------|-------|
| `SUPABASE_URL` | URL de tu proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Clave service_role de Supabase |
| `RESEND_API_KEY` | API key de Resend |
| `TEAM_EMAIL` | `hola@nexusia.es` |
| `FROM_EMAIL` | `noreply@nexusia.es` |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | ID del grupo/canal de Telegram del equipo |
| `CALENDLY_URL` | `https://calendly.com/nexusia/diagnostico-gratuito` |
| `GOOGLE_SHEETS_ID` | ID del Google Sheet para el log de leads |
| `WEBHOOK_SECRET` | El mismo valor que `N8N_WEBHOOK_SECRET` en tu web |

---

## Credenciales necesarias en n8n

Antes de crear los flujos, configura estas credenciales en n8n > **Credentials > New**:

### Supabase (vía HTTP Request con Bearer token)
- Tipo: **Header Auth**
- Name: `Supabase Service Role`
- Header Name: `Authorization`
- Header Value: `Bearer TU_SERVICE_ROLE_KEY`

### Resend (para emails)
- Tipo: **HTTP Header Auth**
- Name: `Resend API`
- Header Name: `Authorization`
- Header Value: `Bearer re_TU_API_KEY`

### Telegram Bot
1. Crea un bot en [@BotFather](https://t.me/BotFather): `/newbot`
2. Copia el token
3. En n8n: tipo **Telegram API**, pega el token
4. Añade el bot al grupo/canal del equipo y obtén el `chat_id`

### Google Sheets
- Tipo: **Google Sheets OAuth2** (sigue el proceso OAuth de Google)
- Necesitarás una cuenta de servicio de Google Cloud o autenticación OAuth

### Gmail / Outlook (alternativa a Resend para emails internos)
- Tipo: **Gmail OAuth2** o **Microsoft Outlook OAuth2**

---

## Flujo 1: Nuevo Lead desde Web

### Descripción

Se activa cuando la web envía un webhook al confirmar un nuevo lead. Valida los datos, envía emails al equipo y al cliente, notifica por Telegram, registra en Google Sheets y, si el score es alto, envía el link de Calendly automáticamente.

### Estructura del webhook entrante (Request)

```json
POST /webhook/nuevo-lead
Authorization: Bearer TU_WEBHOOK_SECRET
Content-Type: application/json

{
  "lead": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-06-15T10:30:00Z",
    "name": "María García",
    "email": "maria.garcia@empresa.es",
    "phone": "+34612345678",
    "company": "Distribuciones García S.L.",
    "role": "Directora de Operaciones",
    "sector": "Logística",
    "employees_range": "50-200",
    "service_interest": "Automatización de procesos",
    "main_problem": "Gestionamos más de 500 albaranes al mes de forma manual. El equipo pasa 2 horas diarias copiando datos entre Excel y el ERP.",
    "tools_used": ["Excel", "SAP"],
    "urgency": "trimestre",
    "lead_score": 82,
    "qualification": "muy-caliente",
    "source": "bot"
  }
}
```

### Respuesta esperada del webhook (Response)

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "workflow_execution_id": "abc123",
  "actions_triggered": [
    "email_team",
    "email_client_confirmation",
    "telegram_notification",
    "google_sheets_log",
    "calendly_link_sent"
  ]
}
```

### Pasos del flujo

#### Paso 1: Webhook Trigger

- **Tipo de nodo**: Webhook
- **HTTP Method**: POST
- **Path**: `nuevo-lead`
- **Authentication**: Header Auth (verifica el header `Authorization: Bearer TU_SECRET`)
- **Response Mode**: Last Node (devuelve la respuesta al finalizar)

Configuración de autenticación:
```
Header Name: Authorization
Header Value: Bearer {{ $env.WEBHOOK_SECRET }}
```

#### Paso 2: Validar datos recibidos

- **Tipo de nodo**: Code (JavaScript)
- **Propósito**: Verificar que el payload tiene los campos mínimos obligatorios

```javascript
const lead = $input.first().json.lead;

// Validaciones mínimas
if (!lead.email || !lead.name) {
  throw new Error('Faltan campos obligatorios: name y email');
}

if (typeof lead.lead_score !== 'number' || lead.lead_score < 0 || lead.lead_score > 100) {
  throw new Error('lead_score inválido');
}

// Enriquecer datos si faltan
const enriched = {
  ...lead,
  qualification: lead.lead_score >= 81 ? 'muy-caliente'
    : lead.lead_score >= 61 ? 'caliente'
    : lead.lead_score >= 31 ? 'templado'
    : 'frío',
  received_at: new Date().toISOString(),
};

return [{ json: enriched }];
```

#### Paso 3: Guardar en Supabase (si no se hizo en la web)

- **Tipo de nodo**: HTTP Request
- **Method**: POST
- **URL**: `{{ $env.SUPABASE_URL }}/rest/v1/leads`
- **Authentication**: Header Auth (Supabase Service Role)
- **Headers adicionales**:
  - `apikey: TU_SUPABASE_ANON_KEY`
  - `Prefer: return=representation`
- **Body** (JSON):
  ```json
  {
    "id": "{{ $json.id }}",
    "name": "{{ $json.name }}",
    "email": "{{ $json.email }}",
    "lead_score": {{ $json.lead_score }},
    "status": "nuevo"
  }
  ```

> Nota: Si la web ya guardó el lead en Supabase (lo cual es lo habitual), este paso usará `ON CONFLICT DO NOTHING`. Configura el header `Prefer: resolution=ignore-duplicates`.

#### Paso 4: Enviar email interno al equipo comercial

- **Tipo de nodo**: HTTP Request a la API de Resend
- **URL**: `https://api.resend.com/emails`
- **Method**: POST
- **Headers**: `Authorization: Bearer {{ $env.RESEND_API_KEY }}`
- **Body**:
```json
{
  "from": "Nexus IA Bot <noreply@nexusia.es>",
  "to": ["hola@nexusia.es"],
  "subject": "🎯 Nuevo lead cualificado: {{ $json.name }} de {{ $json.company }}",
  "html": "<!-- Ver template completo en docs/email-templates.md -->"
}
```

El template HTML completo está en [`email-templates.md`](./email-templates.md) — Email 1.

#### Paso 5: Enviar email de confirmación al cliente

- **Tipo de nodo**: HTTP Request a la API de Resend
- **URL**: `https://api.resend.com/emails`
- **Body**:
```json
{
  "from": "Equipo Nexus IA <hola@nexusia.es>",
  "to": ["{{ $json.email }}"],
  "subject": "Hemos recibido tu solicitud de diagnóstico — Nexus IA",
  "html": "<!-- Ver Email 2 en email-templates.md -->"
}
```

#### Paso 6: Notificación por Telegram al equipo

- **Tipo de nodo**: Telegram
- **Credential**: Telegram Bot (configurada en paso previo)
- **Chat ID**: `{{ $env.TELEGRAM_CHAT_ID }}`
- **Message**:
```
🎯 *Nuevo lead: {{ $json.qualification | upper }}*

👤 *{{ $json.name }}* — {{ $json.role }} en {{ $json.company }}
📧 {{ $json.email }}
📱 {{ $json.phone || 'Sin teléfono' }}
🏭 Sector: {{ $json.sector }} · {{ $json.employees_range }} empleados
⭐ Score: {{ $json.lead_score }}/100

💬 _"{{ $json.main_problem }}"_

👉 [Ver en Supabase]({{ $env.SUPABASE_URL }}/project/default/editor)
```

#### Paso 7: Añadir a Google Sheets

- **Tipo de nodo**: Google Sheets
- **Operation**: Append Row
- **Sheet ID**: `{{ $env.GOOGLE_SHEETS_ID }}`
- **Sheet Name**: `Leads`
- **Columnas** (en este orden en el Sheet):
  - Fecha, Nombre, Email, Teléfono, Empresa, Cargo, Sector, Empleados, Score, Cualificación, Problema, Estado

```javascript
// Mapping de datos para el Sheet
{
  "Fecha": $json.created_at,
  "Nombre": $json.name,
  "Email": $json.email,
  "Teléfono": $json.phone,
  "Empresa": $json.company,
  "Cargo": $json.role,
  "Sector": $json.sector,
  "Empleados": $json.employees_range,
  "Score": $json.lead_score,
  "Cualificación": $json.qualification,
  "Problema": $json.main_problem,
  "Estado": "Nuevo"
}
```

#### Paso 8: Condicional — Si lead_score > 70, enviar Calendly

- **Tipo de nodo**: IF
- **Condición**: `{{ $json.lead_score }}` > `70`

**Rama Verdadero**: Envía email con link de Calendly:
```json
{
  "from": "Equipo Nexus IA <hola@nexusia.es>",
  "to": ["{{ $json.email }}"],
  "subject": "¿Agendamos tu diagnóstico gratuito? — 30 minutos que pueden cambiar tu empresa",
  "html": "<p>Hola {{ $json.name }},</p><p>Hemos revisado tu solicitud y, dado el nivel de automatización que podemos aportar a {{ $json.company }}, queremos reservar tiempo contigo esta semana.</p><p><a href='{{ $env.CALENDLY_URL }}?name={{ $json.name }}&email={{ $json.email }}' style='background:#6366f1;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;display:inline-block'>Reservar mi diagnóstico gratuito →</a></p><p>El equipo de Nexus IA</p>"
}
```

**Rama Falso**: No envía nada (el flujo de seguimiento de 48h se encargará).

---

## Flujo 2: Seguimiento de Lead (48h sin reunión)

### Descripción

Se ejecuta cada día a las 9:00. Busca leads con más de 48 horas de antigüedad que siguen en estado `nuevo` (no se han contactado ni agendado reunión) y envía un email de seguimiento personalizado.

### Trigger: Schedule

- **Tipo de nodo**: Schedule Trigger
- **Configuración**: Todos los días a las 9:00 (hora española, UTC+1 o UTC+2 en verano)
- **Cron**: `0 8 * * 1-5` (9:00 hora española en horario de invierno; ajusta en verano a `0 7 * * 1-5`)

### Paso 1: Consultar leads pendientes en Supabase

- **Tipo de nodo**: HTTP Request
- **Method**: GET
- **URL**: 
```
{{ $env.SUPABASE_URL }}/rest/v1/leads?select=*&status=eq.nuevo&created_at=lt.{{ DateTime.now().minus({hours: 48}).toISO() }}&lead_score=gte.31&order=lead_score.desc
```
- **Headers**: 
  - `apikey: TU_ANON_KEY`
  - `Authorization: Bearer TU_SERVICE_ROLE_KEY`

### Paso 2: Comprobar si hay resultados

- **Tipo de nodo**: IF
- **Condición**: `{{ $json.length }}` > `0`

Si no hay leads, el flujo termina aquí.

### Paso 3: Iterar sobre cada lead

- **Tipo de nodo**: Split In Batches (o Loop Over Items)
- Para cada lead, ejecuta los siguientes pasos

### Paso 4: Enviar email de seguimiento personalizado

```json
{
  "from": "Equipo Nexus IA <hola@nexusia.es>",
  "to": ["{{ $json.email }}"],
  "subject": "¿Pudiste revisar tu diagnóstico gratuito? 👋",
  "html": "<!-- Ver Email 3 en email-templates.md -->"
}
```

### Paso 5: Actualizar estado en Supabase

```
PATCH {{ $env.SUPABASE_URL }}/rest/v1/leads?id=eq.{{ $json.id }}
Body: { "status": "contactado", "notes": "Email de seguimiento automático enviado el {{ DateTime.now().toISODate() }}" }
```

---

## Flujo 3: Post Reunión

### Descripción

Se activa manualmente desde el CRM (o via webhook desde Calendly cuando una reunión termina). Envía el email de post-reunión con resumen y próximos pasos.

### Trigger: Webhook manual

```
POST /webhook/post-reunion
Authorization: Bearer TU_WEBHOOK_SECRET

{
  "lead_id": "550e8400-e29b-41d4-a716-446655440000",
  "meeting_date": "2025-06-15",
  "meeting_notes": "Empresa con 80 empleados. Proceso de facturación manual. Integración con SAP posible. Presupuesto disponible para Q3. Muy interesados.",
  "next_steps": "Enviar propuesta antes del 20 de junio. Llamada de seguimiento el 22.",
  "proposal_value": "15000-25000"
}
```

### Pasos

1. **Obtener datos del lead** desde Supabase por `lead_id`
2. **Enviar email post-reunión** (ver Email 4 en `email-templates.md`)
3. **Actualizar estado** del lead a `propuesta` en Supabase
4. **Notificar por Telegram** al equipo que la reunión fue completada

---

## Probar los webhooks

### Probar Flujo 1 manualmente

```bash
curl -X POST https://TU-INSTANCIA.app.n8n.cloud/webhook/nuevo-lead \
  -H "Authorization: Bearer TU_WEBHOOK_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "lead": {
      "id": "test-id-001",
      "created_at": "2025-06-15T10:00:00Z",
      "name": "Test Usuario",
      "email": "test@nexusia.es",
      "company": "Empresa Test S.L.",
      "role": "Director General",
      "sector": "Industria",
      "employees_range": "50-200",
      "service_interest": "Automatización de procesos",
      "main_problem": "Procesos manuales que consumen mucho tiempo",
      "tools_used": ["Excel"],
      "lead_score": 85,
      "qualification": "muy-caliente",
      "source": "bot"
    }
  }'
```

### Probar Flujo 3 (post reunión)

```bash
curl -X POST https://TU-INSTANCIA.app.n8n.cloud/webhook/post-reunion \
  -H "Authorization: Bearer TU_WEBHOOK_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "550e8400-e29b-41d4-a716-446655440000",
    "meeting_date": "2025-06-15",
    "meeting_notes": "Reunión muy productiva. Empresa con procesos manuales claros.",
    "next_steps": "Enviar propuesta antes del viernes.",
    "proposal_value": "12000"
  }'
```

---

## Notas de mantenimiento

- Revisa los logs de ejecución en n8n > **Executions** periódicamente
- Si un flujo falla repetidamente, n8n puede pausarlo automáticamente — revisa las alertas de error
- Haz un backup de los workflows exportándolos como JSON: n8n > **Workflows** > selecciona todos > **Export**
- Guarda los backups en `docs/n8n-workflows/` en el repositorio (sin credenciales)
