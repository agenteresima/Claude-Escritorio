# AP Automatización IA — Web Corporativa

Sitio web de AP Automatización IA, consultora de inteligencia artificial para empresas en España.

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Framework | Next.js 14 (App Router) |
| Lenguaje | TypeScript |
| Estilos | Tailwind CSS |
| Base de datos | Supabase (PostgreSQL) |
| Email | Resend |
| Animaciones | Framer Motion |
| Iconos | Lucide React |
| Despliegue | Vercel |

## Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/ap-automatizacion-ia/web.git

# 2. Acceder al directorio
cd consultora-ia-web

# 3. Instalar dependencias
npm install

# 4. Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus valores reales

# 5. Configurar Supabase
# Ver docs/supabase-setup.md para instrucciones completas

# 6. Iniciar en modo desarrollo
npm run dev
```

El sitio estará disponible en http://localhost:3000

## Variables de entorno

| Variable | Descripción | Obligatoria |
|----------|-------------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | URL del proyecto de Supabase | Sí |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Clave pública anon de Supabase | Sí |
| `SUPABASE_SERVICE_ROLE_KEY` | Clave de servicio con permisos de admin | Sí |
| `RESEND_API_KEY` | Clave de API de Resend para emails | Sí |
| `RESEND_FROM_EMAIL` | Dirección de envío de emails transaccionales | Sí |
| `RESEND_TEAM_EMAIL` | Email interno que recibe notificaciones de leads | Sí |
| `NEXT_PUBLIC_SITE_URL` | URL pública del sitio (sin barra final) | Sí |
| `NEXT_PUBLIC_COMPANY_NAME` | Nombre de la empresa (AP Automatización IA) | Sí |
| `NEXT_PUBLIC_COMPANY_EMAIL` | Email de contacto público | Sí |
| `NEXT_PUBLIC_COMPANY_PHONE` | Teléfono de contacto público | Sí |
| `N8N_WEBHOOK_URL` | URL del webhook de n8n para nuevo lead | No |
| `N8N_WEBHOOK_SECRET` | Secreto para validar webhooks de n8n | No |
| `NEXT_PUBLIC_CALENDLY_URL` | URL de Calendly para reservar reunión | No |
| `NEXT_PUBLIC_GA_ID` | ID de Google Analytics (G-XXXXXXXXXX) | No |

## Estructura del proyecto

```
consultora-ia-web/
├── app/                          # Páginas y rutas (Next.js App Router)
│   ├── layout.tsx                # Layout raíz con metadatos globales
│   ├── page.tsx                  # Homepage
│   ├── blog/
│   │   ├── page.tsx              # Listado del blog
│   │   └── [slug]/page.tsx       # Artículo individual
│   ├── servicios/
│   │   ├── page.tsx              # Página de servicios
│   │   ├── automatizacion/       # Servicio de automatización
│   │   ├── agentes-ia/           # Servicio de agentes IA
│   │   └── consultoria/          # Servicio de consultoría
│   ├── diagnostico-gratuito/     # Formulario de diagnóstico (captación de leads)
│   ├── contacto/                 # Página de contacto
│   ├── casos-de-exito/           # Casos de éxito de clientes
│   ├── sobre-nosotros/           # Página sobre AP Automatización IA
│   ├── precios/                  # Página de precios
│   ├── aviso-legal/              # Aviso legal obligatorio
│   ├── privacidad/               # Política de privacidad RGPD
│   ├── cookies/                  # Política de cookies
│   └── api/
│       ├── contact/route.ts      # Endpoint: formulario de contacto
│       ├── diagnostic/route.ts   # Endpoint: formulario de diagnóstico
│       └── newsletter/route.ts   # Endpoint: suscripción newsletter
├── components/
│   ├── layout/
│   │   ├── Header.tsx            # Cabecera con navegación
│   │   └── Footer.tsx            # Pie de página
│   └── ui/
│       ├── Badge.tsx             # Badge de categoría/estado
│       ├── BlogCard.tsx          # Card para listado de blog
│       ├── Button.tsx            # Botón reutilizable con variantes
│       ├── Card.tsx              # Card genérico
│       ├── CookieBanner.tsx      # Banner RGPD de cookies (slide-up)
│       ├── NewsletterForm.tsx    # Formulario de suscripción al newsletter
│       ├── PricingCard.tsx       # Card de precios con opción "destacado"
│       ├── ProcessSteps.tsx      # Pasos de proceso numerados con animación
│       ├── Section.tsx           # Wrapper de sección con padding estándar
│       ├── ServiceCard.tsx       # Card de servicio con highlights
│       └── TestimonialCard.tsx   # Card de testimonio con avatar y stars
├── lib/
│   ├── blog-data.ts              # 12 artículos completos del blog
│   ├── constants.ts              # Constantes globales de la app
│   ├── email-templates.ts        # Plantillas HTML de email
│   ├── supabase.ts               # Cliente Supabase
│   ├── types.ts                  # Tipos TypeScript globales
│   └── utils.ts                  # Funciones utilitarias
├── supabase/
│   └── schema.sql                # Schema completo de la base de datos
├── docs/
│   ├── n8n-setup.md              # Configuración de los 3 flujos de n8n
│   ├── supabase-setup.md         # Configuración de Supabase paso a paso
│   ├── vercel-deployment.md      # Despliegue en Vercel
│   └── instagram-plan.md         # Plan de contenidos para Instagram (12 semanas)
├── public/
│   ├── favicon.ico
│   ├── og-image.png              # Imagen Open Graph (1200x630px)
│   └── logo.svg
├── .env.example                  # Plantilla de variables de entorno
├── CHECKLIST.md                  # Checklist completo de lanzamiento
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

## Páginas del sitio

| URL | Propósito |
|-----|-----------|
| `/` | Homepage con propuesta de valor, servicios destacados y CTA principal |
| `/servicios` | Visión general de todos los servicios con comparativa |
| `/servicios/automatizacion` | Detalle del servicio de automatización de procesos |
| `/servicios/agentes-ia` | Detalle del servicio de agentes de IA personalizados |
| `/servicios/consultoria` | Detalle del servicio de consultoría estratégica |
| `/diagnostico-gratuito` | Formulario de captación de leads premium |
| `/contacto` | Formulario de contacto general |
| `/casos-de-exito` | Casos de uso reales con métricas de impacto |
| `/sobre-nosotros` | Presentación del equipo y metodología de trabajo |
| `/precios` | Tabla de precios y planes disponibles |
| `/blog` | Listado de los 12 artículos del blog |
| `/blog/[slug]` | Artículo individual del blog |
| `/aviso-legal` | Aviso legal obligatorio (datos empresa, CIF) |
| `/privacidad` | Política de privacidad y cumplimiento RGPD |
| `/cookies` | Política de cookies con listado de cookies usadas |

## Despliegue en Vercel

Ver instrucciones completas en `docs/vercel-deployment.md`. Pasos clave:

1. Conectar el repositorio de GitHub a Vercel desde el dashboard
2. Configurar todas las variables de entorno en Vercel (Project → Settings → Environment Variables)
3. Configurar el dominio personalizado `automatizacionprocesos.es` en la sección Domains
4. El despliegue es automático en cada push a la rama `main`

## Cómo añadir una página nueva

1. Crear el directorio en `app/nombre-pagina/`
2. Crear `page.tsx` con la exportación por defecto del componente React
3. Añadir metadatos de SEO con `export const metadata` al inicio del archivo
4. Añadir la ruta al sitemap en `app/sitemap.ts`
5. Añadir el enlace en Header y/o Footer si corresponde

```tsx
// app/nueva-pagina/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Título de la página | AP Automatización IA',
  description: 'Descripción para SEO de entre 155 y 160 caracteres.',
}

export default function NuevaPagina() {
  return (
    <main>
      {/* contenido de la página */}
    </main>
  )
}
```

## Cómo modificar el bot conversacional

La lógica de conversación del chatbot está en `app/api/chat/route.ts`. El prompt del sistema que define el comportamiento del bot está en `lib/constants.ts` bajo la constante `BOT_SYSTEM_PROMPT`. Para modificar el comportamiento:

1. Editar `BOT_SYSTEM_PROMPT` en `lib/constants.ts` con las nuevas instrucciones
2. Los flujos de conversación y las preguntas del diagnóstico están tipados en `lib/types.ts`
3. El componente de chat con el historial de conversación está en `components/ui/ChatBot.tsx`

## Cómo personalizar el diseño

**Colores de marca:** editar `tailwind.config.ts` en `theme.extend.colors`:
- `brand.*`: paleta azul principal (azul AP Automatización IA)
- `navy.*`: fondos oscuros para secciones con fondo oscuro

**Tipografía:** la fuente se importa en `app/layout.tsx` desde Google Fonts y se aplica como variable CSS `--font-sans`.

**Componentes UI:** todos los componentes base están en `components/ui/`. Son componentes de servidor por defecto. Si necesitan interactividad del cliente (useState, useEffect), añadir `'use client'` como primera línea del archivo.

---

## Índice

1. [Descripción del proyecto](#descripción-del-proyecto)
2. [Stack tecnológico](#stack-tecnológico)
3. [Requisitos previos](#requisitos-previos)
4. [Instalación](#instalación)
5. [Variables de entorno](#variables-de-entorno)
6. [Configuración de Supabase](#configuración-de-supabase)
7. [Configuración de Resend](#configuración-de-resend)
8. [Despliegue en Vercel](#despliegue-en-vercel)
9. [Estructura de carpetas](#estructura-de-carpetas)
10. [Comandos útiles](#comandos-útiles)
11. [Arquitectura del sistema](#arquitectura-del-sistema)
12. [Cómo añadir nuevas páginas](#cómo-añadir-nuevas-páginas)
13. [Cómo modificar el bot](#cómo-modificar-el-bot)
14. [Troubleshooting](#troubleshooting)
15. [Checklist de lanzamiento](#checklist-de-lanzamiento)

---

## Descripción del proyecto

AP Automatización IA es una consultora especializada en la adopción de inteligencia artificial para empresas medianas y pymes. Esta web tiene tres objetivos principales:

1. **Generar leads cualificados** mediante un bot conversacional que recoge datos del potencial cliente (sector, tamaño, problema principal, herramientas actuales) y calcula un `lead_score` automático.
2. **Comunicar propuesta de valor** a través de servicios, casos de uso reales y blog educativo.
3. **Automatizar el seguimiento comercial** integrando Supabase + Resend + n8n para que cada nuevo lead reciba emails personalizados y el equipo comercial sea notificado en tiempo real.

---

## Stack tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Framework | Next.js (App Router) | 14.x |
| Lenguaje | TypeScript | 5.x |
| Estilos | Tailwind CSS | 3.x |
| Componentes UI | shadcn/ui + Radix UI | — |
| Animaciones | Framer Motion | 11.x |
| Base de datos | Supabase (PostgreSQL) | — |
| Auth (futuro) | Supabase Auth | — |
| Emails | Resend | 3.x |
| Automatización | n8n | Cloud / Self-hosted |
| Despliegue | Vercel | — |
| Analytics | Vercel Analytics + GA4 | — |
| Package manager | pnpm | 9.x |

---

## Requisitos previos

Asegúrate de tener instalado en tu máquina:

- **Node.js** 20.x o superior — [descargar](https://nodejs.org)
- **pnpm** 9.x — `npm install -g pnpm`
- **Git** — `git --version`
- Cuenta en **Supabase** — [supabase.com](https://supabase.com)
- Cuenta en **Resend** — [resend.com](https://resend.com)
- Cuenta en **Vercel** (para despliegue) — [vercel.com](https://vercel.com)

---

## Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-org/ap-automatizacion-ia-web.git
cd ap-automatizacion-ia-web
```

### 2. Instala las dependencias

```bash
pnpm install
```

### 3. Copia el fichero de variables de entorno

```bash
cp .env.example .env.local
```

### 4. Rellena las variables de entorno

Edita `.env.local` con tus claves reales. Consulta la sección [Variables de entorno](#variables-de-entorno) para el detalle de cada variable.

### 5. Ejecuta el schema de Supabase

Accede a tu proyecto en Supabase > SQL Editor y ejecuta el contenido de `supabase/schema.sql`. Consulta la [guía completa de Supabase](./docs/supabase-setup.md).

### 6. Arranca el servidor de desarrollo

```bash
pnpm dev
```

La web estará disponible en [http://localhost:3000](http://localhost:3000).

---

## Variables de entorno

Copia `.env.example` como `.env.local` para desarrollo local. **Nunca subas `.env.local` al repositorio.**

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `NEXT_PUBLIC_SUPABASE_URL` | URL del proyecto Supabase | ✅ Sí |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Clave anónima pública de Supabase | ✅ Sí |
| `SUPABASE_SERVICE_ROLE_KEY` | Clave de servicio de Supabase (solo servidor) | ✅ Sí |
| `RESEND_API_KEY` | API key de Resend para emails | ✅ Sí |
| `RESEND_FROM_EMAIL` | Email remitente verificado en Resend | ✅ Sí |
| `RESEND_TEAM_EMAIL` | Email del equipo que recibe leads | ✅ Sí |
| `RESEND_CC_EMAIL` | Email en copia (opcional) | ❌ No |
| `N8N_WEBHOOK_URL` | URL del webhook de n8n para nuevos leads | ✅ Sí |
| `N8N_WEBHOOK_SECRET` | Secret de autenticación del webhook | ✅ Sí |
| `N8N_WEBHOOK_FOLLOWUP_URL` | URL del webhook de seguimiento | ❌ No |
| `NEXT_PUBLIC_SITE_URL` | URL pública del sitio sin trailing slash | ✅ Sí |
| `NEXT_PUBLIC_COMPANY_NAME` | Nombre de la empresa | ✅ Sí |
| `NEXT_PUBLIC_COMPANY_EMAIL` | Email público de contacto | ✅ Sí |
| `NEXT_PUBLIC_COMPANY_PHONE` | Teléfono formato E.164 | ✅ Sí |
| `NEXT_PUBLIC_COMPANY_ADDRESS` | Dirección física completa | ✅ Sí |
| `NEXT_PUBLIC_COMPANY_CIF` | CIF/NIF de la empresa | ✅ Sí |
| `NEXT_PUBLIC_CALENDLY_URL` | URL del evento Calendly para reuniones | ✅ Sí |
| `CALENDLY_API_KEY` | API key de Calendly (para n8n) | ❌ No |
| `NEXT_PUBLIC_GA_ID` | Google Analytics 4 Measurement ID | ❌ No |
| `NEXT_PUBLIC_HOTJAR_ID` | ID de Hotjar (mapas de calor) | ❌ No |
| `NEXT_PUBLIC_INSTAGRAM_URL` | URL perfil de Instagram | ❌ No |
| `NEXT_PUBLIC_LINKEDIN_URL` | URL página de LinkedIn | ❌ No |
| `NEXT_PUBLIC_TWITTER_URL` | URL perfil de Twitter/X | ❌ No |
| `NEXTAUTH_SECRET` | Secret para JWT internos | ❌ No |
| `EMAIL_DRY_RUN` | `true` para no enviar emails reales en desarrollo | — |
| `N8N_DRY_RUN` | `true` para no disparar webhooks en desarrollo | — |
| `DEBUG_BOT` | `true` para logs detallados del bot en consola | — |

### Generar secretos seguros

```bash
# Para N8N_WEBHOOK_SECRET
openssl rand -hex 32

# Para NEXTAUTH_SECRET
openssl rand -base64 64
```

---

## Configuración de Supabase

Consulta la guía detallada en [`docs/supabase-setup.md`](./docs/supabase-setup.md).

### Resumen rápido

1. Crea un nuevo proyecto en [supabase.com](https://supabase.com/dashboard)
2. Ve a **SQL Editor** y ejecuta `supabase/schema.sql`
3. Copia las claves desde **Settings > API**:
   - `Project URL` → `NEXT_PUBLIC_SUPABASE_URL`
   - `anon public` → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `service_role` → `SUPABASE_SERVICE_ROLE_KEY`
4. Verifica que las políticas RLS están activas

---

## Configuración de Resend

1. Crea una cuenta en [resend.com](https://resend.com)
2. Ve a **Domains** y añade `automatizacionprocesos.es`
3. Añade los registros DNS indicados (SPF, DKIM, DMARC) en tu proveedor de dominio
4. Espera la verificación (puede tardar hasta 48 h)
5. Ve a **API Keys** > **Create API Key**
6. Copia la clave en `RESEND_API_KEY`
7. Establece `RESEND_FROM_EMAIL=noreply@automatizacionprocesos.es`

> **Nota:** Hasta que el dominio esté verificado, Resend solo permite enviar a la dirección de email con la que te registraste. Perfecto para desarrollo.

### Probar el envío de emails en local

```bash
# Con EMAIL_DRY_RUN=false en .env.local
curl -X POST http://localhost:3000/api/test-email \
  -H "Content-Type: application/json" \
  -d '{"to": "tu@email.com", "template": "lead-confirmation"}'
```

---

## Despliegue en Vercel

Consulta la guía completa en [`docs/vercel-deployment.md`](./docs/vercel-deployment.md).

### Pasos resumidos

#### 1. Sube el código a GitHub

```bash
git remote add origin https://github.com/tu-org/ap-automatizacion-ia-web.git
git push -u origin main
```

#### 2. Importa el proyecto en Vercel

1. Ve a [vercel.com/new](https://vercel.com/new)
2. Selecciona el repositorio `ap-automatizacion-ia-web`
3. Vercel detecta automáticamente que es Next.js
4. **NO pulses Deploy todavía** — antes configura las variables de entorno

#### 3. Configura las variables de entorno

En **Settings > Environment Variables**, añade todas las variables de `.env.example` con sus valores reales de producción.

#### 4. Despliega

Pulsa **Deploy**. Vercel tardará aproximadamente 2-3 minutos.

#### 5. Configura el dominio personalizado

1. Ve a **Settings > Domains**
2. Añade `automatizacionprocesos.es` y `www.automatizacionprocesos.es`
3. Añade los registros DNS en tu proveedor de dominio:
   - Registro `A`: `76.76.21.21`
   - `CNAME www`: `cname.vercel-dns.com`
4. Configura el redirect de `automatizacionprocesos.es` → `www.automatizacionprocesos.es`

---

## Estructura de carpetas

```
ap-automatizacion-ia-web/
│
├── app/                          # Next.js App Router
│   ├── (marketing)/              # Grupo de rutas públicas
│   │   ├── page.tsx              # Página de inicio (/)
│   │   ├── servicios/            # Página de servicios (/servicios)
│   │   ├── casos-de-uso/         # Casos de uso reales
│   │   ├── sobre-nosotros/       # Quiénes somos
│   │   ├── blog/                 # Blog con MDX
│   │   │   └── [slug]/           # Post individual
│   │   ├── contacto/             # Formulario de contacto
│   │   ├── politica-privacidad/
│   │   ├── aviso-legal/
│   │   └── cookies/
│   │
│   ├── api/                      # API Routes (servidor)
│   │   ├── leads/
│   │   │   └── route.ts          # POST /api/leads
│   │   ├── contact/
│   │   │   └── route.ts          # POST /api/contact
│   │   ├── newsletter/
│   │   │   └── route.ts          # POST /api/newsletter
│   │   └── bot/
│   │       └── route.ts          # POST /api/bot
│   │
│   ├── layout.tsx                # Layout raíz
│   ├── globals.css
│   └── sitemap.ts
│
├── components/
│   ├── bot/                      # Bot conversacional
│   │   ├── ChatBot.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ChatOptions.tsx
│   │   ├── TypingIndicator.tsx
│   │   └── bot-flow.ts           # Árbol de conversación
│   │
│   ├── sections/                 # Secciones de la home
│   │   ├── Hero.tsx
│   │   ├── Services.tsx
│   │   ├── HowItWorks.tsx
│   │   ├── UseCases.tsx
│   │   ├── Testimonials.tsx
│   │   ├── FAQ.tsx
│   │   └── FinalCTA.tsx
│   │
│   ├── ui/                       # Componentes shadcn/ui
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── CookieBanner.tsx
│   │
│   └── forms/
│       ├── LeadForm.tsx
│       └── ContactForm.tsx
│
├── lib/
│   ├── supabase.ts               # Cliente Supabase + interfaces
│   ├── resend.ts                 # Funciones de email
│   ├── n8n.ts                    # Disparo de webhook n8n
│   ├── lead-scoring.ts           # Algoritmo de puntuación
│   └── utils.ts
│
├── public/
│   ├── images/
│   ├── icons/
│   ├── og/                       # Open Graph images (1200x630)
│   └── robots.txt
│
├── supabase/
│   └── schema.sql
│
├── docs/
│   ├── n8n-setup.md
│   ├── email-templates.md
│   ├── supabase-setup.md
│   ├── vercel-deployment.md
│   └── instagram-plan.md
│
├── .env.example
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── CHECKLIST.md
└── README.md
```

---

## Comandos útiles

```bash
# Desarrollo
pnpm dev                    # Servidor de desarrollo en localhost:3000
pnpm build                  # Compilar para producción
pnpm start                  # Servidor de producción local
pnpm lint                   # ESLint
pnpm type-check             # Verificar tipos TypeScript

# Supabase — regenerar tipos
npx supabase gen types typescript \
  --project-id TU_PROJECT_ID \
  > lib/database.types.ts

# Analizar bundle
ANALYZE=true pnpm build

# Previsualizar emails
pnpm email:preview          # localhost:3001
```

---

## Arquitectura del sistema

```
Usuario (Navegador)
        │ HTTPS
        ▼
Vercel CDN / Edge (Next.js App Router)
  ├── Páginas estáticas (RSC/SSG)
  ├── API Routes (servidor)
  └── Bot conversacional (cliente React)
        │
        ├──► POST /api/leads
        │         │
        │         ├──► Supabase PostgreSQL (guarda lead)
        │         ├──► Resend (email confirmación al cliente)
        │         └──► n8n Webhook
        │                   │
        │                   ├──► Email interno al equipo comercial
        │                   ├──► Notificación Telegram/Slack
        │                   ├──► Google Sheets (log de leads)
        │                   └──► Si lead_score > 70: email con link Calendly
        │
        └──► POST /api/contact (formulario general)
                  │
                  ├──► Supabase (guarda solicitud)
                  └──► Resend (email al equipo)
```

### Flujo de un nuevo lead

1. El usuario interactúa con el **bot conversacional** (React, lado cliente)
2. Al finalizar, el bot llama a `POST /api/leads` con todos los datos recogidos
3. La API Route valida los datos, calcula el `lead_score` y guarda en **Supabase**
4. La API Route envía email de confirmación al usuario via **Resend**
5. La API Route dispara el **webhook de n8n** con el payload completo
6. n8n notifica al equipo y registra en Google Sheets
7. Si `lead_score > 70`, n8n envía automáticamente el link de Calendly al lead

---

## Cómo añadir nuevas páginas

### Página de marketing estática

```tsx
// app/(marketing)/nueva-pagina/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Nueva Página — AP Automatización IA',
  description: 'Descripción para SEO (150-160 caracteres).',
  openGraph: {
    title: 'Nueva Página — AP Automatización IA',
    description: 'Descripción para redes sociales.',
    images: ['/og/nueva-pagina.png'],
  },
}

export default function NuevaPaginaPage() {
  return (
    <main>
      <h1>Nueva Página</h1>
    </main>
  )
}
```

### Post de blog con MDX

Crea `app/(marketing)/blog/mi-articulo/page.mdx` con frontmatter:

```mdx
---
title: "Cómo automatizar la gestión de facturas con IA"
description: "Guía práctica para eliminar el trabajo manual en administración"
date: "2025-06-15"
author: "Equipo AP Automatización IA"
tags: ["automatización", "administración", "IA"]
image: "/images/blog/facturas-ia.webp"
---

Contenido del artículo...
```

### Nueva API Route

```typescript
// app/api/nuevo-endpoint/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    // lógica aquí
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('[/api/nuevo-endpoint]', error)
    return NextResponse.json({ error: 'Error interno' }, { status: 500 })
  }
}
```

---

## Cómo modificar el bot

El flujo conversacional está en `components/bot/bot-flow.ts`. Cada nodo:

```typescript
interface BotNode {
  id: string
  message: string
  options?: Array<{
    label: string       // Texto del botón
    value: string       // Valor que se guarda
    next: string        // ID del siguiente nodo
  }>
  inputType?: 'text' | 'email' | 'phone' | 'none'
  field?: keyof Lead   // Qué campo del Lead se rellena
  scoring?: Record<string, number>  // Puntos por opción
}
```

### Algoritmo de lead scoring (lib/lead-scoring.ts)

Escala 0-100 puntos, distribuidos entre las respuestas:

| Pregunta | Opciones y puntos |
|----------|------------------|
| Sector | Industria (20), Logística (18), Retail (15), Servicios (12), Otro (8) |
| Empleados | 50-200 (20), 200-500 (25), >500 (20), 10-50 (10), <10 (5) |
| Problema principal | Procesos manuales (20), Atención cliente (15), Análisis datos (15) |
| Herramientas actuales | Solo Excel (15), ERP sin IA (12), Mixto (8) |
| Urgencia | Inmediata (15), Este trimestre (10), Este año (5) |

**Interpretación del score:**
- **0-30**: Lead frío — solo se registra en Supabase
- **31-60**: Lead templado — email de seguimiento automático en 48 h
- **61-80**: Lead caliente — notificación inmediata al equipo
- **81-100**: Lead muy cualificado — envío automático de link Calendly

---

## Troubleshooting

### El bot no guarda los datos en Supabase

1. Verifica que `NEXT_PUBLIC_SUPABASE_URL` y `NEXT_PUBLIC_SUPABASE_ANON_KEY` son correctos en `.env.local`
2. Comprueba en Supabase > **Table Editor** > tabla `leads` que existe con las columnas correctas
3. Revisa las políticas RLS: la política `INSERT` debe permitir el rol `anon`
4. Abre la consola del navegador y busca errores en la petición a `/api/leads`

### Los emails no se envían

1. Verifica que `RESEND_API_KEY` es válida (empieza por `re_`)
2. Asegúrate de que `EMAIL_DRY_RUN=false` en `.env.local`
3. Comprueba que el dominio `automatizacionprocesos.es` está verificado en Resend > **Domains**
4. Revisa Resend > **Logs** para ver si llegan las peticiones y qué error devuelven

### El webhook de n8n no se dispara

1. Verifica que `N8N_WEBHOOK_URL` apunta al webhook activo en n8n
2. Asegúrate de que `N8N_DRY_RUN=false`
3. En n8n, activa el workflow (estado **Active**)
4. Prueba el webhook manualmente:
   ```bash
   curl -X POST "$N8N_WEBHOOK_URL" \
     -H "Authorization: Bearer $N8N_WEBHOOK_SECRET" \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","email":"test@test.com","lead_score":75}'
   ```

### Error de build en Vercel

```bash
# Reproduce el error localmente
pnpm type-check
pnpm build
```

Corrige los errores de TypeScript antes de hacer push.

### La página carga lento

1. Optimiza imágenes: convierte a WebP con `next/image`
2. Revisa que las fuentes usan `display: swap`
3. Activa **Vercel Speed Insights** para localizar el cuello de botella
4. Usa `ANALYZE=true pnpm build` para ver qué módulos pesan más

### Error CORS en desarrollo local

Las API Routes de Next.js no tienen CORS por defecto en local. Asegúrate de llamar a rutas relativas (`/api/leads`), no absolutas.

---

## Checklist de lanzamiento

Ver el fichero completo en [`CHECKLIST.md`](./CHECKLIST.md).

---

## Licencia

Propietario — © 2025 AP Automatización IA. Todos los derechos reservados.
