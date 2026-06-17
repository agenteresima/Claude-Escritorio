# Guía de Accesos — Automatización Procesos IA

## 🌐 WEB

| Qué | URL | Acceso |
|-----|-----|--------|
| **Web pública** | https://automatizacionprocesos.es | — |
| **Vercel (deploy)** | https://vercel.com/dashboard | agente.resima@gmail.com |
| **GitHub repo web** | https://github.com/OscarResima/consultora-ia-web | cuenta GitHub OscarResima |
| **GitHub repo general** | https://github.com/agenteresima/Claude-Escritorio | cuenta GitHub agenteresima |

---

## 📊 ANALÍTICA

| Herramienta | URL | ID / Acceso |
|-------------|-----|-------------|
| **Google Analytics GA4** | https://analytics.google.com | agente.resima@gmail.com · ID: G-50KP99T5BP |
| **Google Tag Manager** | https://tagmanager.google.com | agente.resima@gmail.com · ID: GTM-W58RKX78 |
| **Google Search Console** | https://search.google.com/search-console | agente.resima@gmail.com · Token verificación: TceEaWudgp_DnrexQdit-LP27Gc-UYA6bJHXq28prrE |

---

## 📧 EMAIL Y DOMINIO

| Qué | URL | Acceso |
|-----|-----|--------|
| **Email empresa** | admin@automatizacionprocesos.es | — |
| **Email personal** | agente.resima@gmail.com | cuenta Google |
| **Dominio** | automatizacionprocesos.es | Raiola Networks |
| **Raiola (DNS)** | https://raiolanetworks.es | cuenta Raiola |

---

## 📱 REDES SOCIALES

| Red | URL / Cuenta | Acceso |
|-----|-------------|--------|
| **Instagram** | @automatizacionprocesos_ia (pendiente crear) | — |
| **LinkedIn empresa** | pendiente crear | — |
| **Google Business** | business.google.com | agente.resima@gmail.com · Creado ✅ |

---

## 🤖 AUTOMATIZACIÓN

| Herramienta | URL | Acceso |
|-------------|-----|--------|
| **n8n** | tu instalación local/servidor | — |
| **Supabase (web)** | https://supabase.com/dashboard/project/kgmookumxhkbkohwkxim | Proyecto "automatizacionprocesos-web" · org Resima SL · agente.resima@gmail.com |
| **Supabase (otro proyecto)** | https://supabase.com/dashboard/project/achgrrqncnhacewluata | Proyecto "Automatización y Agente N8N" (datos de contabilidad, NO usar para la web) |
| **Resend email** (pendiente) | https://resend.com | pendiente crear cuenta + verificar dominio |

### Variables de entorno en Vercel (formulario web)

| Variable | Valor |
|----------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://kgmookumxhkbkohwkxim.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ver dashboard Supabase → API Keys → "anon" |
| `SUPABASE_SERVICE_ROLE_KEY` | ver dashboard Supabase → API Keys → "service_role" (pendiente copiar) |
| `RESEND_API_KEY` | pendiente crear cuenta Resend |

Tablas creadas en Supabase: `contact_requests`, `leads`, `newsletter_subscribers`, `bot_conversations` (RLS activado, solo accesibles con la service_role key).

---

## 💻 ARCHIVOS LOCALES (en tu ordenador)

| Archivo | Ruta | Qué es |
|---------|------|--------|
| **Post Instagram 1** | instagram-post1.html | 7 slides "5 procesos que puedes automatizar" |
| **Post Instagram 2** | instagram-post2/slide-1 a 7.html | 7 slides "Tu competencia ya usa IA" |
| **Imagen perfil Instagram** | instagram-profile.html | Foto de perfil circular |
| **Logo variantes** | logo-automatizacion-procesos-ia.html | 4 variantes del logo |
| **Logo 500x500** | logo-500x500.html | Logo cuadrado para apps |

---

## ⚙️ CONFIGURACIÓN WEB

| Variable | Valor |
|----------|-------|
| **Email contacto** | admin@automatizacionprocesos.es |
| **Ciudad** | Valencia, España |
| **Videollamada diagnóstico** | 30 minutos |
| **Google Analytics** | G-50KP99T5BP |
| **Google Tag Manager** | GTM-W58RKX78 |
| **Google Search Console** | Verificado ✅ |

---

## 📋 PENDIENTE CONFIGURAR

- [x] Supabase → proyecto creado y tablas listas (contact_requests, leads, newsletter_subscribers, bot_conversations)
- [ ] Supabase → copiar `service_role` key y añadir las 3 variables de Supabase en Vercel
- [ ] Resend → crear cuenta, verificar dominio, añadir API key en Vercel
- [ ] Instagram Business → convertir cuenta a profesional
- [ ] LinkedIn → crear página de empresa
- [ ] n8n → flujo de captura de leads automático
- [ ] Google Ads → campaña de búsqueda
- [ ] Directorios → Páginas Amarillas, Yelp, Hotfrog
