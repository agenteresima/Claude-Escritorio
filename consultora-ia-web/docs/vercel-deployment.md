# Vercel — Guía de Despliegue Completa

Esta guía cubre el despliegue completo del proyecto AP Automatización IA en Vercel, desde la conexión del repositorio hasta la configuración de dominio personalizado y CI/CD.

---

## 1. Conectar el repositorio GitHub

### 1.1 Asegúrate de que el código está en GitHub

```bash
# Si todavía no tienes remote configurado:
git remote add origin https://github.com/TU_ORG/ap-automatizacion-ia-web.git
git branch -M main
git push -u origin main
```

Verifica que `.env.local` está en `.gitignore` (nunca debe subirse al repositorio).

### 1.2 Importar en Vercel

1. Ve a [vercel.com/new](https://vercel.com/new)
2. Conecta tu cuenta de GitHub si aún no lo has hecho
3. Busca el repositorio `ap-automatizacion-ia-web` y pulsa **Import**
4. Vercel detecta automáticamente el framework (Next.js)
5. **Importante:** NO pulses Deploy todavía — configura las variables de entorno primero

---

## 2. Configurar variables de entorno en Vercel

En la pantalla de configuración del proyecto (antes del primer deploy):

1. Expande **Environment Variables**
2. Añade cada variable. Para cada una, selecciona en qué entornos aplica:
   - **Production**: la web real
   - **Preview**: deployments de Pull Requests (usa valores de staging)
   - **Development**: `vercel dev` local (normalmente usas `.env.local` en su lugar)

### Variables mínimas para producción

| Variable | Entorno | Valor |
|----------|---------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | Production, Preview | URL de tu proyecto Supabase |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Production, Preview | Clave anon de Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Production, Preview | Clave service_role (¡nunca pública!) |
| `RESEND_API_KEY` | Production | API key de Resend |
| `RESEND_FROM_EMAIL` | Production | `noreply@automatizacionprocesos.es` |
| `RESEND_TEAM_EMAIL` | Production | `hola@automatizacionprocesos.es` |
| `N8N_WEBHOOK_URL` | Production | URL del webhook activo en n8n |
| `N8N_WEBHOOK_SECRET` | Production | Secret del webhook |
| `NEXT_PUBLIC_SITE_URL` | Production | `https://www.automatizacionprocesos.es` |
| `NEXT_PUBLIC_COMPANY_NAME` | All | `AP Automatización IA` |
| `NEXT_PUBLIC_COMPANY_EMAIL` | All | `hola@automatizacionprocesos.es` |
| `NEXT_PUBLIC_COMPANY_PHONE` | All | `+34900000000` |
| `NEXT_PUBLIC_COMPANY_ADDRESS` | All | `Calle Gran Vía 28, 28013 Madrid` |
| `NEXT_PUBLIC_COMPANY_CIF` | All | `B-XXXXXXXXX` |
| `NEXT_PUBLIC_CALENDLY_URL` | All | URL de tu evento Calendly |
| `NEXT_PUBLIC_GA_ID` | Production | `G-XXXXXXXXXX` |
| `EMAIL_DRY_RUN` | Production | `false` |
| `N8N_DRY_RUN` | Production | `false` |

> Para Preview (Pull Requests), usa `EMAIL_DRY_RUN=true` y `N8N_DRY_RUN=true` para evitar enviar emails reales en entornos de prueba.

### Importar variables masivamente

Si ya tienes todas las variables en `.env.local`, puedes importarlas desde la CLI de Vercel:

```bash
npm i -g vercel
vercel login
vercel env pull .env.vercel  # descarga las vars de Vercel a un fichero local
# O para subir las de .env.local:
vercel env add < .env.local
```

---

## 3. Primer despliegue

Después de configurar las variables, pulsa **Deploy**. Vercel:

1. Clona el repositorio
2. Ejecuta `pnpm install`
3. Ejecuta `pnpm build` (Next.js compila)
4. Despliega en su CDN global

El proceso tarda entre 2 y 5 minutos. Recibirás una URL temporal como `ap-automatizacion-ia-web.vercel.app`.

### Si el build falla

1. Mira los logs del build en Vercel > Deployments > [el deployment fallido] > Build Logs
2. Reproduce el error en local:
   ```bash
   pnpm build
   ```
3. Los errores más comunes son:
   - Variables de entorno que faltan (`process.env.X is undefined`)
   - Errores de TypeScript que no se detectaron en desarrollo
   - Importaciones de módulos que no existen en el servidor (p.ej., `window` en RSC)

---

## 4. Configurar dominio personalizado

### 4.1 Añadir el dominio en Vercel

1. Ve a tu proyecto en Vercel > **Settings > Domains**
2. Escribe `automatizacionprocesos.es` y pulsa **Add**
3. Añade también `www.automatizacionprocesos.es`
4. Configura el redirect: `automatizacionprocesos.es` → `www.automatizacionprocesos.es` (o al revés)

### 4.2 Configurar DNS en tu proveedor de dominio

Vercel te indicará exactamente qué registros añadir. Los habituales son:

| Tipo | Nombre | Valor |
|------|--------|-------|
| `A` | `@` (raíz) | `76.76.21.21` |
| `CNAME` | `www` | `cname.vercel-dns.com` |

Si tu proveedor no admite registros `CNAME` en el apex (raíz), usa el registro `A` para la raíz y `CNAME` para `www`.

> La propagación DNS puede tardar entre 5 minutos y 48 horas. Usa [dnschecker.org](https://dnschecker.org) para verificar.

### 4.3 SSL/HTTPS automático

Vercel provisiona automáticamente certificados SSL/TLS de Let's Encrypt. No necesitas configurar nada adicional. Una vez que el DNS apunta a Vercel, el certificado se emite en minutos.

---

## 5. Configurar headers de seguridad

Añade esto en `next.config.ts`:

```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          // Previene clickjacking
          { key: 'X-Frame-Options', value: 'DENY' },
          // Previene MIME-type sniffing
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          // Política de referrer
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          // Permissions Policy (deshabilita funciones no usadas)
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
          // Content Security Policy — ajusta según tus dominios
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://www.googletagmanager.com https://assets.calendly.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: blob: https:",
              "connect-src 'self' https://*.supabase.co https://api.resend.com",
              "frame-src https://calendly.com",
            ].join('; '),
          },
        ],
      },
    ]
  },
}

export default nextConfig
```

---

## 6. Configurar redirects

```typescript
// En next.config.ts, dentro del objeto de configuración:
async redirects() {
  return [
    // Redirect del dominio sin www al www (si usas www como canónico)
    // Esto se gestiona mejor desde el panel de Vercel > Domains,
    // pero también se puede hacer aquí para rutas específicas:
    {
      source: '/diagnostico',
      destination: '/#bot',
      permanent: false,  // 302 — usa false hasta que estés seguro
    },
    {
      source: '/contactar',
      destination: '/contacto',
      permanent: true,   // 301 — para URLs que ya no usarás
    },
    // Redirect de blog antiguo (si migras desde WordPress, p.ej.)
    {
      source: '/blog/:slug',
      destination: '/blog/:slug',  // misma ruta, útil si cambia la estructura
      permanent: true,
    },
  ]
},
```

---

## 7. Activar Vercel Analytics y Speed Insights

### Analytics (visitas y páginas vistas)

1. En tu proyecto Vercel > **Analytics** > **Enable**
2. Añade el componente en `app/layout.tsx`:
   ```typescript
   import { Analytics } from '@vercel/analytics/react'
   
   export default function RootLayout({ children }) {
     return (
       <html>
         <body>
           {children}
           <Analytics />
         </body>
       </html>
     )
   }
   ```
3. Instala el paquete: `pnpm add @vercel/analytics`

### Speed Insights (Core Web Vitals)

```bash
pnpm add @vercel/speed-insights
```

```typescript
import { SpeedInsights } from '@vercel/speed-insights/next'

// En app/layout.tsx, dentro del body:
<SpeedInsights />
```

Los datos aparecen en Vercel > **Speed Insights** tras unas horas de tráfico.

---

## 8. CI/CD automatizado

Vercel crea automáticamente:

- **Deploy de producción** en cada push a la rama `main`
- **Deploy de Preview** en cada Pull Request (URL única por PR)

### Configurar protección de la rama main en GitHub

1. Ve a tu repositorio en GitHub > **Settings > Branches**
2. Añade una regla para `main`:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass: añade el check de Vercel
   - ✅ Require branches to be up to date

### Variables de entorno por rama

En Vercel puedes tener variables diferentes por entorno:

```
Production  → N8N_DRY_RUN=false, EMAIL_DRY_RUN=false
Preview     → N8N_DRY_RUN=true,  EMAIL_DRY_RUN=true
Development → (usa .env.local en local)
```

---

## 9. Rollback si hay problemas

Si un deploy de producción rompe algo:

1. Ve a Vercel > **Deployments**
2. Busca el último deployment que funcionaba bien
3. Pulsa el menú (...) del deployment y selecciona **Promote to Production**

Vercel hace el rollback en segundos, sin downtime.

Para hacer rollback con la CLI:

```bash
vercel rollback [deployment-url]
```

---

## 10. Monitorizar errores en producción

### Logs en tiempo real

```bash
vercel logs --follow
```

### Logs filtrados por ruta

```bash
vercel logs --filter /api/leads
```

### Alertas de error (recomendado)

Conecta [Sentry](https://sentry.io) para monitorización de errores en producción:

```bash
pnpm add @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

---

## 11. Checklist final pre-lanzamiento

Ver el fichero completo en [`../CHECKLIST.md`](../CHECKLIST.md).

### Verificaciones rápidas post-deploy

```bash
# 1. Verificar que el sitio responde
curl -I https://www.automatizacionprocesos.es

# 2. Verificar redirects
curl -I https://automatizacionprocesos.es  # debe redirigir a www

# 3. Verificar headers de seguridad
curl -I https://www.automatizacionprocesos.es | grep -E "X-Frame|X-Content|Referrer"

# 4. Verificar sitemap
curl https://www.automatizacionprocesos.es/sitemap.xml

# 5. Verificar robots.txt
curl https://www.automatizacionprocesos.es/robots.txt

# 6. Probar formulario de lead (con datos de prueba)
curl -X POST https://www.automatizacionprocesos.es/api/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","lead_score":50,"status":"nuevo"}'
```
