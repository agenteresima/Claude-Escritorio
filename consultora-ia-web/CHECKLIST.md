# Checklist de Lanzamiento — AP Automatización IA Web

Usar este checklist antes de hacer pública la web. Marcar cada ítem cuando esté completado y verificado.

---

## Técnico

- [ ] `npm run build` completa sin errores ni warnings críticos
- [ ] `npm run lint` completa sin errores
- [ ] Variables de entorno configuradas en Vercel (todas las marcadas como obligatorias en `.env.example`)
- [ ] `supabase/schema.sql` ejecutado en el proyecto de Supabase de producción
- [ ] Row Level Security (RLS) activado en todas las tablas de Supabase
- [ ] Políticas de RLS probadas: anon solo puede INSERT en `leads`, no SELECT
- [ ] Test completo del formulario de diagnóstico: datos recibidos correctamente en Supabase + email de confirmación enviado al lead + email de notificación recibido en `hola@automatizacionprocesos.es`
- [ ] Test completo del formulario de contacto general
- [ ] Test del bot de conversación: completar flujo completo de principio a fin
- [ ] Webhook de n8n conectado, testado y activo (Flujo 1: Nuevo Lead)
- [ ] Flujo de seguimiento 48h (Flujo 2) activado y probado con dato de prueba
- [ ] SSL/HTTPS activo y válido en el dominio `automatizacionprocesos.es`
- [ ] Redirect `www.automatizacionprocesos.es` → `automatizacionprocesos.es` configurado (o viceversa, de forma consistente)
- [ ] Redirect HTTP → HTTPS funcionando
- [ ] Página 404 personalizada accesible y con el diseño correcto
- [ ] Core Web Vitals > 90 en PageSpeed Insights en mobile y desktop (probar en https://pagespeed.web.dev)
- [ ] Sin errores en la consola del navegador en ninguna página

---

## SEO

- [ ] Metadatos (title + description) únicos y correctos en las 14 páginas principales
- [ ] `/sitemap.xml` accesible y con todas las páginas listadas
- [ ] `/robots.txt` accesible con las directivas correctas
- [ ] Schema.org validado en https://validator.schema.org (LocalBusiness o Organization)
- [ ] Open Graph image de 1200x630px creada y configurada (`og:image`)
- [ ] Twitter Card configurada correctamente
- [ ] Canonical URLs configuradas en todas las páginas
- [ ] Google Search Console: dominio `automatizacionprocesos.es` añadido y verificado
- [ ] Sitemap enviado a Google Search Console
- [ ] Google Analytics o Vercel Analytics activo y recibiendo datos
- [ ] Imágenes con atributos `alt` descriptivos en todas las páginas
- [ ] Estructura de headings correcta (un único H1 por página, H2/H3 jerárquicos)

---

## Legal / RGPD

- [ ] Política de privacidad con datos reales de la empresa (nombre legal, CIF, domicilio, email DPO si aplica)
- [ ] Aviso legal con datos reales (nombre legal, CIF, domicilio, número de inscripción en Registro Mercantil)
- [ ] Banner de cookies activo, visible al primer acceso sin consent previo
- [ ] Banner de cookies guarda la preferencia en localStorage correctamente
- [ ] Todos los formularios con checkbox de RGPD explícito y enlace a política de privacidad
- [ ] Ningún formulario tiene el checkbox de RGPD pre-marcado
- [ ] Email de confirmación al lead incluye enlace de baja/oposición
- [ ] Newsletter incluye enlace de baja en cada email
- [ ] Datos de Supabase almacenados en región europea (EU West)

---

## Contenido

- [ ] Teléfono y email reales (no placeholders) en Header, Footer y páginas de contacto
- [ ] Dirección física real (si se quiere publicar) o ciudad al menos
- [ ] Precios actualizados y revisados en todas las páginas de servicio y precios
- [ ] Logo en SVG subido en `/public/logo.svg` y configurado en Header y Footer
- [ ] Favicon configurado (`/public/favicon.ico` y variantes para Apple Touch Icon)
- [ ] Todas las imágenes en formato WebP y optimizadas (< 200KB por imagen)
- [ ] Open Graph image (1200x630px) creada con el logo y tagline de AP Automatización IA
- [ ] Primeros 3 artículos del blog publicados y con contenido real completo
- [ ] Páginas de servicios con contenido real, no placeholder
- [ ] Página "Sobre nosotros" con información real del equipo
- [ ] Sin texto "Lorem ipsum" o "[PENDIENTE]" en ninguna página pública
- [ ] Todos los enlaces internos funcionan (sin 404s)
- [ ] Todos los enlaces externos abren en nueva pestaña con `target="_blank" rel="noopener"`

---

## Comercial

- [ ] `hola@automatizacionprocesos.es` configurado, operativo y revisado al menos 2 veces al día
- [ ] Calendly configurado con disponibilidad real, confirmación automática por email, y URL configurada en `.env`: `NEXT_PUBLIC_CALENDLY_URL`
- [ ] CRM (o hoja de seguimiento) preparado para recibir y gestionar los leads entrantes
- [ ] Notificación de nuevo lead llegando correctamente a email del equipo
- [ ] Notificación de nuevo lead llegando a Telegram/Slack si está configurado
- [ ] Envío de respuesta automática al primer lead de prueba verificado
- [ ] Flujo de n8n de seguimiento 48h activado y probado
- [ ] Plantillas de respuesta manual preparadas para los primeros contactos
- [ ] Precio y condiciones del diagnóstico gratuito claros y consistentes en todo el sitio

---

## Performance y accesibilidad

- [ ] Lighthouse score Accesibilidad > 90
- [ ] Contraste de colores correcto (WCAG AA) en todos los textos sobre fondos de color
- [ ] Navegación completa con teclado posible
- [ ] Focus visible en todos los elementos interactivos
- [ ] Textos alternativos en todas las imágenes decorativas con `alt=""`
- [ ] Web funciona correctamente en Chrome, Firefox, Safari y Edge
- [ ] Web funciona correctamente en iOS Safari (iPhone) y Chrome Android

---

## Post-lanzamiento (semana 1)

- [ ] Google Search Console: confirmar que la homepage está indexada (puede tardar 3-7 días)
- [ ] Revisar leads recibidos en Supabase dashboard
- [ ] Comprobar tasa de apertura de emails de confirmación en Resend dashboard (objetivo: >60%)
- [ ] Comprobar que no hay emails rebotados ni marcados como spam
- [ ] Publicar primeros posts en Instagram según el plan de contenidos
- [ ] Publicar anuncio del lanzamiento en LinkedIn personal y de empresa
- [ ] Enviar email de lanzamiento a lista de contactos previos si existe
- [ ] Solicitar al menos 3 reseñas o testimonios a clientes actuales o anteriores
- [ ] Configurar alerta en Google Alerts para "AP Automatización IA" y variantes del nombre
