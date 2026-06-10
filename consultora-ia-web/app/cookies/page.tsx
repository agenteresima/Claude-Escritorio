import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Política de Cookies | Automatización Procesos IA',
  description:
    'Política de cookies de Automatización Procesos IA conforme al Reglamento General de Protección de Datos (RGPD) y la normativa española de cookies.',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/cookies' },
}

const cookieTable = [
  {
    type: 'Necesarias',
    color: 'green',
    cookies: [
      {
        name: 'session',
        purpose: 'Mantiene la sesión activa del usuario durante la navegación',
        duration: 'Sesión',
        provider: 'Automatización Procesos IA',
      },
      {
        name: 'csrf_token',
        purpose: 'Protección contra ataques de falsificación de solicitudes entre sitios',
        duration: 'Sesión',
        provider: 'Automatización Procesos IA',
      },
      {
        name: 'cookie_consent',
        purpose: 'Almacena las preferencias de cookies del usuario',
        duration: '12 meses',
        provider: 'Automatización Procesos IA',
      },
    ],
  },
  {
    type: 'Análisis',
    color: 'blue',
    cookies: [
      {
        name: '_ga',
        purpose: 'Cookie principal de Google Analytics para distinguir usuarios',
        duration: '2 años',
        provider: 'Google Analytics',
      },
      {
        name: '_ga_[ID]',
        purpose: 'Almacena y actualiza el identificador de sesión de Google Analytics',
        duration: '2 años',
        provider: 'Google Analytics',
      },
      {
        name: '_gid',
        purpose: 'Identifica a los usuarios para Google Analytics',
        duration: '24 horas',
        provider: 'Google Analytics',
      },
    ],
  },
  {
    type: 'Marketing',
    color: 'orange',
    cookies: [
      {
        name: '_fbp',
        purpose: 'Utilizada por Facebook para mostrar anuncios relevantes y medir su efectividad',
        duration: '3 meses',
        provider: 'Meta (Facebook)',
      },
      {
        name: 'li_fat_id',
        purpose: 'Cookie de seguimiento de LinkedIn para medir conversiones de anuncios',
        duration: '30 días',
        provider: 'LinkedIn',
      },
    ],
  },
]

const colorMap: Record<string, { badge: string; header: string }> = {
  green: {
    badge: 'bg-green-50 text-green-700 border border-green-200',
    header: 'bg-green-50',
  },
  blue: {
    badge: 'bg-blue-50 text-blue-700 border border-blue-200',
    header: 'bg-blue-50',
  },
  orange: {
    badge: 'bg-orange-50 text-orange-700 border border-orange-200',
    header: 'bg-orange-50',
  },
}

export default function CookiesPage() {
  return (
    <div className="bg-white pt-24 pb-20">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
            Política de cookies
          </h1>
          <p className="text-slate-500 text-sm">Última actualización: enero de 2025</p>
        </div>

        <div className="prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-slate-900 prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-3 prose-p:text-slate-600 prose-p:leading-relaxed prose-a:text-blue-600 prose-ul:text-slate-600 prose-li:my-1">

          <h2>1. ¿Qué son las cookies?</h2>
          <p>
            Las cookies son pequeños ficheros de texto que se almacenan en el dispositivo del
            usuario cuando visita un sitio web. Permiten al sitio web recordar sus acciones y
            preferencias (como inicio de sesión, idioma, tamaño de fuente y otras preferencias de
            visualización) durante un período de tiempo, para que no tenga que volver a
            introducirlas cuando regrese al sitio o navegue por sus páginas.
          </p>

          <h2>2. ¿Qué tipos de cookies utilizamos?</h2>
          <p>Utilizamos los siguientes tipos de cookies:</p>
          <ul>
            <li>
              <strong>Cookies estrictamente necesarias:</strong> Son esenciales para el
              funcionamiento del sitio web. Sin ellas, determinados servicios no pueden prestarse.
              No requieren su consentimiento.
            </li>
            <li>
              <strong>Cookies de análisis:</strong> Nos permiten conocer cómo los usuarios
              utilizan el sitio web para mejorar su funcionamiento y contenidos. Requieren su
              consentimiento.
            </li>
            <li>
              <strong>Cookies de marketing:</strong> Se utilizan para mostrarle publicidad relevante
              basada en sus intereses y medir la efectividad de las campañas publicitarias.
              Requieren su consentimiento.
            </li>
          </ul>

          <h2>3. Tabla de cookies</h2>
        </div>

        {/* Cookie tables */}
        <div className="mt-6 space-y-8 not-prose">
          {cookieTable.map((section) => (
            <div key={section.type}>
              <div className="flex items-center gap-2 mb-3">
                <h3 className="font-bold text-slate-900 text-lg">
                  Cookies {section.type.toLowerCase()}
                </h3>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${colorMap[section.color].badge}`}>
                  {section.type}
                </span>
              </div>
              <div className="overflow-x-auto rounded-xl border border-slate-200">
                <table className="w-full text-sm">
                  <thead>
                    <tr className={`border-b border-slate-200 ${colorMap[section.color].header}`}>
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Nombre</th>
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Finalidad</th>
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Duración</th>
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Proveedor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {section.cookies.map((cookie, idx) => (
                      <tr
                        key={cookie.name}
                        className={`border-t border-slate-100 ${idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}`}
                      >
                        <td className="py-3 px-4 font-mono text-xs text-slate-800 font-semibold">
                          {cookie.name}
                        </td>
                        <td className="py-3 px-4 text-slate-600">{cookie.purpose}</td>
                        <td className="py-3 px-4 text-slate-600 whitespace-nowrap">{cookie.duration}</td>
                        <td className="py-3 px-4 text-slate-600 whitespace-nowrap">{cookie.provider}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>

        <div className="prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-slate-900 prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-3 prose-p:text-slate-600 prose-p:leading-relaxed prose-a:text-blue-600 prose-ul:text-slate-600 prose-li:my-1 mt-8">

          <h2>4. Cómo gestionar las cookies</h2>
          <p>
            Puede configurar su navegador para rechazar, aceptar o eliminar las cookies. Las
            instrucciones varían según el navegador:
          </p>
          <ul>
            <li>
              <strong>Google Chrome:</strong> Configuración &gt; Privacidad y seguridad &gt; Cookies y
              otros datos de sitios
            </li>
            <li>
              <strong>Mozilla Firefox:</strong> Configuración &gt; Privacidad y seguridad &gt; Cookies y
              datos del sitio
            </li>
            <li>
              <strong>Microsoft Edge:</strong> Configuración &gt; Privacidad, búsqueda y servicios &gt;
              Cookies
            </li>
            <li>
              <strong>Safari:</strong> Preferencias &gt; Privacidad &gt; Cookies y datos de sitios web
            </li>
          </ul>
          <p>
            Tenga en cuenta que la desactivación de ciertas cookies puede afectar al funcionamiento
            del sitio web y limitar el acceso a determinadas funcionalidades.
          </p>

          <h2>5. Cookies de terceros</h2>
          <p>
            Algunas cookies son instaladas por servicios de terceros. Le recomendamos revisar las
            políticas de privacidad de dichos terceros:
          </p>
          <ul>
            <li>
              <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">
                Google Analytics — Política de privacidad
              </a>
            </li>
            <li>
              <a href="https://www.facebook.com/privacy/policy/" target="_blank" rel="noopener noreferrer">
                Meta (Facebook) — Política de privacidad
              </a>
            </li>
            <li>
              <a href="https://www.linkedin.com/legal/privacy-policy" target="_blank" rel="noopener noreferrer">
                LinkedIn — Política de privacidad
              </a>
            </li>
          </ul>

          <h2>6. Base legal y consentimiento</h2>
          <p>
            La instalación de cookies estrictamente necesarias se fundamenta en el interés legítimo
            de garantizar el correcto funcionamiento del sitio web (art. 6.1.f RGPD). Para el resto
            de cookies, la base legal es el consentimiento del usuario (art. 6.1.a RGPD), otorgado
            a través del banner de cookies que aparece en su primera visita.
          </p>
          <p>
            Puede retirar su consentimiento en cualquier momento modificando la configuración de su
            navegador o contactando con nosotros en{' '}
            <a href="mailto:admin@automatizacionprocesos.es">admin@automatizacionprocesos.es</a>.
          </p>

          <h2>7. Actualizaciones de esta política</h2>
          <p>
            Podemos actualizar esta política de cookies en cualquier momento. Le notificaremos
            cualquier cambio significativo mediante un aviso en el sitio web. Le recomendamos
            revisar periódicamente esta página.
          </p>

          <h2>8. Más información</h2>
          <p>
            Para más información sobre el tratamiento de sus datos personales, consulte nuestra{' '}
            <Link href="/privacidad">política de privacidad</Link>. Para cualquier consulta sobre
            esta política de cookies, puede contactarnos en{' '}
            <a href="mailto:admin@automatizacionprocesos.es">admin@automatizacionprocesos.es</a>.
          </p>
        </div>
      </div>
    </div>
  )
}
