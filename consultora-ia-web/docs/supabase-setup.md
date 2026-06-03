# Supabase — Guía de Configuración Completa

Esta guía cubre desde la creación del proyecto hasta la monitorización en producción.

---

## 1. Crear el proyecto en Supabase

1. Ve a [supabase.com/dashboard](https://supabase.com/dashboard) e inicia sesión
2. Pulsa **New Project**
3. Rellena los datos:
   - **Name**: `ap-automatizacion-ia-prod` (o `ap-automatizacion-ia-dev` para el entorno de desarrollo)
   - **Database Password**: genera una contraseña segura y guárdala en un gestor de contraseñas
   - **Region**: `West EU (Ireland)` — más cercana a usuarios de España
   - **Pricing Plan**: Free para empezar, Pro cuando superes 50.000 filas o necesites backups diarios
4. Espera 1-2 minutos a que el proyecto se aprovisione

---

## 2. Ejecutar el schema SQL

Ve a **SQL Editor** (icono de base de datos en el menú lateral) y ejecuta el siguiente schema:

```sql
-- =============================================================================
-- NEXUS IA — Schema de base de datos
-- =============================================================================

-- Extensión para UUIDs
create extension if not exists "uuid-ossp";

-- -----------------------------------------------------------------------------
-- TABLA: leads
-- Almacena todos los leads generados por el bot conversacional
-- -----------------------------------------------------------------------------
create table if not exists public.leads (
  id                    uuid primary key default uuid_generate_v4(),
  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now(),

  -- Datos personales
  name                  text not null,
  email                 text not null,
  phone                 text,
  company               text,
  role                  text,               -- Cargo en la empresa

  -- Cualificación
  sector                text,               -- Industria, Logística, Retail...
  employees_range       text,               -- '10-50', '50-200', '200-500', '+500'
  service_interest      text,               -- Servicio de mayor interés
  main_problem          text,               -- Problema principal que describe el lead
  tools_used            text[],             -- Herramientas actuales ['Excel', 'SAP'...]
  preferred_contact_time text,              -- 'mañana', 'tarde', 'indistinto'
  budget_range          text,               -- 'menos-5k', '5k-15k', '15k-50k', '+50k'
  urgency               text,               -- 'inmediata', 'trimestre', 'año'

  -- Scoring y estado
  lead_score            integer default 0 check (lead_score >= 0 and lead_score <= 100),
  status                text not null default 'nuevo'
                          check (status in ('nuevo', 'contactado', 'reunión', 'propuesta', 'cliente', 'perdido')),
  qualification         text,               -- 'frío', 'templado', 'caliente', 'muy-caliente'
  source                text default 'bot', -- 'bot', 'formulario', 'referido', 'linkedin'

  -- Seguimiento comercial
  notes                 text,
  assigned_to           text,               -- Email del comercial asignado
  next_action_date      date,
  meeting_scheduled_at  timestamptz,
  proposal_sent_at      timestamptz,
  closed_at             timestamptz,

  -- Metadata técnica
  utm_source            text,
  utm_medium            text,
  utm_campaign          text,
  ip_country            text,
  user_agent            text
);

-- Índices para consultas frecuentes
create index if not exists leads_email_idx on public.leads(email);
create index if not exists leads_status_idx on public.leads(status);
create index if not exists leads_lead_score_idx on public.leads(lead_score desc);
create index if not exists leads_created_at_idx on public.leads(created_at desc);

-- Trigger para actualizar updated_at automáticamente
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger set_leads_updated_at
  before update on public.leads
  for each row execute function public.handle_updated_at();

-- -----------------------------------------------------------------------------
-- TABLA: bot_conversations
-- Historial completo de conversaciones del bot
-- -----------------------------------------------------------------------------
create table if not exists public.bot_conversations (
  id                    uuid primary key default uuid_generate_v4(),
  created_at            timestamptz not null default now(),
  lead_id               uuid references public.leads(id) on delete set null,
  messages              jsonb not null default '[]',
  summary               text,
  intent                text,
  qualification_score   integer,
  duration_seconds      integer,
  completed             boolean default false
);

create index if not exists bot_conversations_lead_id_idx on public.bot_conversations(lead_id);

-- -----------------------------------------------------------------------------
-- TABLA: contact_requests
-- Formulario de contacto general (no el bot)
-- -----------------------------------------------------------------------------
create table if not exists public.contact_requests (
  id                    uuid primary key default uuid_generate_v4(),
  created_at            timestamptz not null default now(),
  name                  text not null,
  email                 text not null,
  phone                 text,
  company               text,
  message               text,
  service_interest      text,
  status                text not null default 'pendiente'
                          check (status in ('pendiente', 'respondido', 'archivado'))
);

-- -----------------------------------------------------------------------------
-- TABLA: newsletter_subscribers
-- Suscriptores al newsletter
-- -----------------------------------------------------------------------------
create table if not exists public.newsletter_subscribers (
  id                    uuid primary key default uuid_generate_v4(),
  created_at            timestamptz not null default now(),
  email                 text unique not null,
  source                text,               -- 'footer', 'blog', 'popup'
  status                text not null default 'activo'
                          check (status in ('activo', 'baja', 'rebotado'))
);

-- -----------------------------------------------------------------------------
-- VISTAS útiles para el dashboard comercial
-- -----------------------------------------------------------------------------

-- Métricas diarias de leads
create or replace view public.leads_daily_metrics as
select
  date_trunc('day', created_at) as day,
  count(*) as total_leads,
  avg(lead_score) as avg_score,
  count(*) filter (where lead_score >= 61) as hot_leads,
  count(*) filter (where status = 'cliente') as converted
from public.leads
group by date_trunc('day', created_at)
order by day desc;

-- Distribución por sector
create or replace view public.leads_by_sector as
select
  coalesce(sector, 'Sin especificar') as sector,
  count(*) as total,
  round(avg(lead_score)) as avg_score
from public.leads
group by sector
order by total desc;
```

Pulsa **Run** (▶). Deberías ver "Success. No rows returned".

---

## 3. Configurar Row Level Security (RLS)

RLS controla qué datos puede leer/escribir cada rol. Ejecuta en el SQL Editor:

```sql
-- Activar RLS en todas las tablas
alter table public.leads enable row level security;
alter table public.bot_conversations enable row level security;
alter table public.contact_requests enable row level security;
alter table public.newsletter_subscribers enable row level security;

-- -----------------------------------------------------------------------------
-- Políticas para LEADS
-- -----------------------------------------------------------------------------

-- El frontend (rol anon) puede INSERTAR leads (el bot los crea)
create policy "Anon puede insertar leads"
  on public.leads for insert
  to anon
  with check (true);

-- El service_role (servidor) puede hacer todo
create policy "Service role acceso total a leads"
  on public.leads for all
  to service_role
  using (true)
  with check (true);

-- -----------------------------------------------------------------------------
-- Políticas para BOT_CONVERSATIONS
-- -----------------------------------------------------------------------------
create policy "Anon puede insertar conversaciones"
  on public.bot_conversations for insert
  to anon
  with check (true);

create policy "Service role acceso total a conversaciones"
  on public.bot_conversations for all
  to service_role
  using (true)
  with check (true);

-- -----------------------------------------------------------------------------
-- Políticas para CONTACT_REQUESTS
-- -----------------------------------------------------------------------------
create policy "Anon puede insertar solicitudes de contacto"
  on public.contact_requests for insert
  to anon
  with check (true);

create policy "Service role acceso total a contactos"
  on public.contact_requests for all
  to service_role
  using (true)
  with check (true);

-- -----------------------------------------------------------------------------
-- Políticas para NEWSLETTER
-- -----------------------------------------------------------------------------
create policy "Anon puede suscribirse al newsletter"
  on public.newsletter_subscribers for insert
  to anon
  with check (true);

create policy "Service role acceso total a newsletter"
  on public.newsletter_subscribers for all
  to service_role
  using (true)
  with check (true);
```

> **Importante:** Nunca uses la `anon key` para leer datos sensibles. Toda lectura de leads en el panel comercial debe hacerse con la `service_role key` desde el servidor.

---

## 4. Obtener las claves API

Ve a **Settings > API** en tu proyecto de Supabase:

| Clave | Dónde encontrarla | Variable de entorno |
|-------|------------------|---------------------|
| Project URL | Settings > API > Project URL | `NEXT_PUBLIC_SUPABASE_URL` |
| `anon` public | Settings > API > Project API keys > anon | `NEXT_PUBLIC_SUPABASE_ANON_KEY` |
| `service_role` | Settings > API > Project API keys > service_role | `SUPABASE_SERVICE_ROLE_KEY` |

> ⚠️ La `service_role` key **bypasea todas las políticas RLS**. Úsala únicamente en código de servidor (API Routes de Next.js). Nunca en el frontend ni en variables `NEXT_PUBLIC_*`.

---

## 5. Configurar en .env.local

```bash
NEXT_PUBLIC_SUPABASE_URL=https://abcdefghijklmnop.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 6. Configurar Storage (para documentos y propuestas)

Si en el futuro necesitas subir archivos (PDFs de propuestas, etc.):

1. Ve a **Storage** en el menú lateral
2. Pulsa **New Bucket**:
   - Name: `propuestas`
   - Public bucket: **No** (privado, solo acceso autenticado)
3. Para el bucket `og-images` (imágenes públicas):
   - Name: `og-images`
   - Public bucket: **Sí**

```sql
-- Política para que solo service_role pueda subir a 'propuestas'
create policy "Solo service_role puede subir propuestas"
  on storage.objects for insert
  to service_role
  with check (bucket_id = 'propuestas');
```

---

## 7. Configurar Auth (para área de clientes futura)

Si en el futuro añades un área de clientes donde los leads puedan ver el estado de su propuesta:

1. Ve a **Authentication > Settings**
2. En **Email Auth**: activa "Confirm email"
3. En **Email Templates**: personaliza los emails de confirmación con la marca AP Automatización IA
4. En **URL Configuration**:
   - Site URL: `https://www.automatizacionprocesos.es`
   - Redirect URLs: `https://www.automatizacionprocesos.es/clientes/**`

```typescript
// lib/supabase-server.ts — cliente para uso en servidor con auth
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export function createSupabaseServerClient() {
  const cookieStore = cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) { return cookieStore.get(name)?.value },
        set(name, value, options) { cookieStore.set({ name, value, ...options }) },
        remove(name, options) { cookieStore.set({ name, value: '', ...options }) },
      },
    }
  )
}
```

---

## 8. Monitorización y backups

### Monitorización

- Ve a **Reports** en Supabase para ver métricas de la base de datos
- Activa alertas en **Settings > Alerts** si la base de datos supera el 80% de espacio en el plan Free
- Usa **Logs** para depurar consultas lentas

### Backups automáticos

- **Plan Free**: backups diarios, retención de 7 días
- **Plan Pro**: backups diarios, retención de 30 días + Point-in-Time Recovery

Para exportar manualmente:
```bash
# Requiere psql y las credenciales de conexión directa
# (Settings > Database > Connection string)
pg_dump "postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres" \
  > backup_$(date +%Y%m%d).sql
```

---

## 9. Queries SQL para el dashboard comercial

Ejecuta estas consultas en el SQL Editor para análisis rápidos:

### Resumen general de leads

```sql
select
  count(*) as total_leads,
  count(*) filter (where status = 'nuevo') as nuevos,
  count(*) filter (where status = 'contactado') as contactados,
  count(*) filter (where status = 'reunión') as en_reunion,
  count(*) filter (where status = 'propuesta') as con_propuesta,
  count(*) filter (where status = 'cliente') as clientes,
  round(avg(lead_score)) as score_promedio,
  count(*) filter (where lead_score >= 61) as leads_calientes
from public.leads
where created_at >= now() - interval '30 days';
```

### Leads de hoy pendientes de contactar

```sql
select
  name, email, phone, company, sector,
  employees_range, lead_score, qualification,
  main_problem, tools_used, created_at
from public.leads
where status = 'nuevo'
  and created_at >= now() - interval '24 hours'
order by lead_score desc;
```

### Tasa de conversión por fuente

```sql
select
  source,
  count(*) as total,
  count(*) filter (where status = 'cliente') as convertidos,
  round(
    count(*) filter (where status = 'cliente')::numeric / count(*) * 100, 1
  ) as conversion_pct,
  round(avg(lead_score)) as avg_score
from public.leads
group by source
order by conversion_pct desc;
```

### Leads sin contactar después de 48 horas

```sql
select
  name, email, phone, company, lead_score,
  created_at,
  extract(hours from now() - created_at)::int as horas_sin_contacto
from public.leads
where status = 'nuevo'
  and created_at < now() - interval '48 hours'
order by lead_score desc, created_at asc;
```

---

## 10. Regenerar tipos TypeScript

Después de modificar el schema, regenera los tipos para TypeScript:

```bash
npx supabase gen types typescript \
  --project-id TU_PROJECT_ID \
  --schema public \
  > lib/database.types.ts
```

Sustituye `TU_PROJECT_ID` por el ID de tu proyecto (lo encuentras en **Settings > General > Reference ID**).
