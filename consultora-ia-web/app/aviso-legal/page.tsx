import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Aviso Legal | AP Automatización IA',
  description:
    'Aviso legal de AP Automatización IA conforme a la Ley 34/2002, de Servicios de la Sociedad de la Información y del Comercio Electrónico (LSSI-CE).',
  alternates: { canonical: 'https://www.automatizacionprocesos.es/aviso-legal' },
}

export default function AvisoLegalPage() {
  return (
    <div className="bg-white pt-24 pb-20">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div className="mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">Aviso legal</h1>
          <p className="text-slate-500 text-sm">Última actualización: enero de 2025</p>
        </div>

        <div className="prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-slate-900 prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-3 prose-p:text-slate-600 prose-p:leading-relaxed prose-a:text-blue-600 prose-ul:text-slate-600 prose-li:my-1">

          <h2>1. Datos identificativos del titular</h2>
          <p>
            En cumplimiento de lo dispuesto en el artículo 10 de la Ley 34/2002, de 11 de julio, de
            Servicios de la Sociedad de la Información y del Comercio Electrónico (LSSI-CE), se
            facilitan a continuación los datos identificativos del titular del sitio web:
          </p>
          <ul>
            <li><strong>Denominación:</strong> AP Automatización IA</li>
            <li><strong>Actividad:</strong> Consultoría e implementación de inteligencia artificial para empresas</li>
            <li><strong>Email:</strong> admin@automatizacionprocesos.es</li>
            <li><strong>Teléfono:</strong> +34 900 000 000</li>
            <li><strong>Sitio web:</strong> https://www.automatizacionprocesos.es</li>
          </ul>

          <h2>2. Objeto y ámbito de aplicación</h2>
          <p>
            El presente Aviso Legal regula el uso del sitio web automatizacionprocesos.es (en adelante, "el sitio
            web"), cuyo titular es AP Automatización IA. El acceso y uso del sitio web implica la aceptación
            plena y sin reservas de todas las disposiciones contenidas en este Aviso Legal.
          </p>
          <p>
            AP Automatización IA se reserva el derecho a modificar en cualquier momento las condiciones de uso
            del sitio web, así como sus contenidos y servicios. El uso continuado del sitio web tras
            la publicación de tales modificaciones implica la aceptación de los mismos.
          </p>

          <h2>3. Condiciones de acceso y uso</h2>
          <p>
            El acceso al sitio web tiene carácter libre y gratuito. El usuario se compromete a
            hacer un uso adecuado y lícito de los contenidos y servicios del sitio web conforme a
            la legislación aplicable, las normas de la moral y el orden público, y el presente Aviso
            Legal.
          </p>
          <p>Queda expresamente prohibido:</p>
          <ul>
            <li>Reproducir, copiar, distribuir, transformar o modificar los contenidos sin autorización</li>
            <li>Usar técnicas de ingeniería inversa, descifrado u otros medios para obtener el código fuente</li>
            <li>Introducir virus, troyanos o cualquier otro programa dañino</li>
            <li>Vulnerar los sistemas de seguridad del sitio web</li>
            <li>Usar el sitio web para fines comerciales no autorizados</li>
          </ul>

          <h2>4. Propiedad intelectual e industrial</h2>
          <p>
            Todos los contenidos del sitio web, incluyendo, a título enunciativo y no limitativo,
            textos, imágenes, gráficos, logotipos, iconos, código fuente, diseño y estructura de
            navegación, son propiedad de AP Automatización IA o de terceros que han autorizado su uso, y están
            protegidos por las leyes españolas e internacionales de propiedad intelectual e
            industrial.
          </p>
          <p>
            Queda prohibida la reproducción total o parcial de los contenidos del sitio web sin la
            autorización expresa y por escrito de AP Automatización IA, salvo para uso personal y privado del
            usuario.
          </p>
          <p>
            Las marcas, nombres comerciales y distintivos que aparecen en el sitio web son
            propiedad de AP Automatización IA o de sus respectivos propietarios. El acceso al sitio web no
            otorga ningún derecho sobre dichas marcas o nombres comerciales.
          </p>

          <h2>5. Exclusión de responsabilidad</h2>
          <h3>5.1 Contenidos del sitio web</h3>
          <p>
            AP Automatización IA no garantiza la exactitud, veracidad, exhaustividad o actualidad de los
            contenidos del sitio web. Los contenidos tienen finalidad meramente informativa y no
            constituyen asesoramiento profesional de ningún tipo.
          </p>
          <h3>5.2 Disponibilidad del sitio web</h3>
          <p>
            AP Automatización IA no garantiza la disponibilidad continua e ininterrumpida del sitio web. Nexus
            IA se exime de cualquier responsabilidad por los daños y perjuicios que pudieran
            derivarse de la falta de disponibilidad o accesibilidad del sitio web.
          </p>
          <h3>5.3 Virus y elementos dañinos</h3>
          <p>
            AP Automatización IA no se responsabiliza de los daños producidos en el equipo del usuario como
            consecuencia de la descarga de programas dañinos en el sitio web.
          </p>
          <h3>5.4 Sitios web enlazados</h3>
          <p>
            El sitio web puede contener enlaces a otros sitios web de terceros. AP Automatización IA no
            controla ni es responsable de los contenidos, políticas de privacidad o prácticas de
            dichos sitios web.
          </p>

          <h2>6. Política de privacidad y cookies</h2>
          <p>
            Para más información sobre el tratamiento de sus datos personales y el uso de cookies,
            consulte nuestra{' '}
            <Link href="/privacidad">política de privacidad</Link> y nuestra{' '}
            <Link href="/cookies">política de cookies</Link>.
          </p>

          <h2>7. Jurisdicción y legislación aplicable</h2>
          <p>
            El presente Aviso Legal se rige íntegramente por la legislación española. Para la
            resolución de cualquier controversia derivada del acceso o uso del sitio web, las partes
            se someten a los Juzgados y Tribunales de España, con renuncia expresa a cualquier otro
            fuero que pudiera corresponderles.
          </p>
          <p>
            En caso de que el usuario sea considerado consumidor conforme a la normativa vigente,
            podrá acudir a la plataforma de resolución de litigios en línea de la Unión Europea:{' '}
            <a href="https://ec.europa.eu/consumers/odr" target="_blank" rel="noopener noreferrer">
              https://ec.europa.eu/consumers/odr
            </a>
            .
          </p>

          <h2>8. Contacto</h2>
          <p>
            Para cualquier consulta relacionada con el presente Aviso Legal, puede ponerse en
            contacto con nosotros a través de:{' '}
            <a href="mailto:admin@automatizacionprocesos.es">admin@automatizacionprocesos.es</a>
          </p>
        </div>
      </div>
    </div>
  )
}
