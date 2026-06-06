import type { Metadata } from 'next'
import Link from 'next/link'
import { COMPANY_INFO } from '@/lib/constants'

export const metadata: Metadata = {
  title: 'Términos y condiciones — AP Automatización IA',
  description:
    'Términos y condiciones de contratación y uso del sitio web de AP Automatización IA. Información sobre objeto, condiciones de uso, propiedad intelectual y responsabilidad.',
  keywords: [
    'términos y condiciones AP Automatización IA',
    'condiciones de uso consultoría IA',
    'contrato servicios inteligencia artificial',
  ],
  openGraph: {
    title: 'Términos y condiciones — AP Automatización IA',
    description:
      'Términos y condiciones de contratación y uso del sitio web de AP Automatización IA.',
    type: 'website',
    locale: 'es_ES',
  },
  alternates: {
    canonical: 'https://www.ap-automatizacion-ia.es/terminos',
  },
  robots: {
    index: false,
  },
}

export default function TerminosPage() {
  return (
    <main className="bg-white min-h-screen">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 pt-20 pb-24">

        {/* Encabezado */}
        <div className="mb-10 border-b border-surface-200 pb-8">
          <p className="text-brand-600 text-sm font-semibold uppercase tracking-widest mb-3">
            Información legal
          </p>
          <h1 className="text-3xl sm:text-4xl font-bold text-navy-900 mb-3">
            Términos y condiciones
          </h1>
          <p className="text-navy-500 text-sm">
            Última actualización: junio de 2025
          </p>
        </div>

        {/* Contenido legal */}
        <div className="prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-navy-900 prose-h2:text-xl prose-h2:mt-10 prose-h2:mb-3 prose-h3:text-base prose-h3:mt-6 prose-h3:mb-2 prose-p:text-navy-600 prose-p:leading-relaxed prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline prose-ul:text-navy-600 prose-li:my-1 prose-strong:text-navy-800">

          <p>
            Los presentes Términos y Condiciones (en adelante, "los Términos") regulan la relación
            contractual entre <strong>{COMPANY_INFO.nombre_legal}</strong>, que opera bajo la marca
            comercial <strong>{COMPANY_INFO.nombre}</strong> (en adelante, "la Empresa"), y los
            usuarios y clientes que acceden al sitio web o contratan cualquiera de los servicios
            ofrecidos. El acceso al sitio web y la contratación de servicios implican la aceptación
            plena y sin reservas de los presentes Términos.
          </p>

          {/* 1 */}
          <h2>1. Objeto y ámbito de aplicación</h2>
          <p>
            Los presentes Términos tienen por objeto establecer las condiciones que rigen:
          </p>
          <ul>
            <li>El acceso y uso del sitio web <strong>automatizacionprocesos.es</strong> y sus subdominios asociados.</li>
            <li>La contratación de servicios de consultoría, implementación y formación en inteligencia artificial ofrecidos por la Empresa.</li>
            <li>La relación entre la Empresa y sus clientes durante la ejecución de los proyectos.</li>
          </ul>
          <p>
            Estos Términos se aplican con carácter general a todos los usuarios y clientes. En caso
            de existir condiciones particulares pactadas mediante contrato escrito, prevalecerán
            sobre lo dispuesto en los presentes Términos en aquellos aspectos que expresamente los
            modifiquen.
          </p>
          <p>
            La Empresa se reserva el derecho a modificar los presentes Términos en cualquier
            momento. Las modificaciones entrarán en vigor desde su publicación en el sitio web. El
            uso continuado de los servicios tras la publicación de las modificaciones implica su
            aceptación.
          </p>

          {/* 2 */}
          <h2>2. Identificación del prestador</h2>
          <p>
            En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la
            Sociedad de la Información y del Comercio Electrónico (LSSI-CE), se facilitan los
            siguientes datos identificativos:
          </p>
          <ul>
            <li><strong>Denominación comercial:</strong> {COMPANY_INFO.nombre}</li>
            <li><strong>Razón social:</strong> {COMPANY_INFO.nombre_legal}</li>
            <li>
              <strong>Domicilio social:</strong> {COMPANY_INFO.direccion},{' '}
              {COMPANY_INFO.ciudad}, {COMPANY_INFO.pais}
            </li>
            <li>
              <strong>Correo electrónico:</strong>{' '}
              <a href={`mailto:${COMPANY_INFO.email}`}>{COMPANY_INFO.email}</a>
            </li>
            <li><strong>Teléfono:</strong> {COMPANY_INFO.telefono}</li>
            <li><strong>Actividad:</strong> Consultoría e implementación de inteligencia artificial para empresas</li>
          </ul>

          {/* 3 */}
          <h2>3. Condiciones de uso del sitio web</h2>
          <h3>3.1 Acceso y uso lícito</h3>
          <p>
            El acceso al sitio web tiene carácter libre y gratuito. El usuario se compromete a
            hacer un uso adecuado y lícito de los contenidos y servicios disponibles, de conformidad
            con la legislación vigente, la moral y el orden público, y los presentes Términos.
          </p>
          <h3>3.2 Usos prohibidos</h3>
          <p>Queda expresamente prohibido:</p>
          <ul>
            <li>Reproducir, copiar, distribuir o transformar los contenidos del sitio web sin autorización expresa de la Empresa.</li>
            <li>Utilizar el sitio web con fines ilícitos, engañosos o que lesionen derechos de terceros.</li>
            <li>Introducir o difundir virus informáticos o cualquier otro elemento dañino.</li>
            <li>Vulnerar o intentar vulnerar los sistemas de seguridad del sitio web.</li>
            <li>Recopilar datos de otros usuarios sin su consentimiento.</li>
            <li>Utilizar técnicas de scraping automatizado sin autorización previa por escrito.</li>
          </ul>
          <h3>3.3 Menores de edad</h3>
          <p>
            Los servicios de la Empresa están dirigidos exclusivamente a empresas y profesionales.
            Los menores de 18 años no podrán contratar servicios ni facilitar datos personales a
            través del sitio web sin el consentimiento expreso de sus representantes legales.
          </p>

          {/* 4 */}
          <h2>4. Contratación de servicios</h2>
          <h3>4.1 Proceso de contratación</h3>
          <p>
            La contratación de servicios se formaliza mediante propuesta escrita aceptada por el
            cliente, ya sea a través de firma de presupuesto, aceptación por correo electrónico o
            firma de contrato específico. El envío de un formulario de contacto o solicitud de
            diagnóstico no implica por sí solo ningún compromiso contractual.
          </p>
          <h3>4.2 Condiciones económicas</h3>
          <p>
            Los precios indicados en el sitio web son orientativos y se expresan en euros sin IVA,
            salvo indicación en contrario. El precio definitivo se detalla en la propuesta
            individualizada para cada proyecto. La Empresa emitirá factura por los servicios
            prestados conforme a la normativa fiscal española vigente.
          </p>
          <h3>4.3 Forma de pago</h3>
          <p>
            Las condiciones de pago se establecen en la propuesta económica de cada proyecto. Con
            carácter general, los proyectos requieren un pago inicial del 50% a la firma y el 50%
            restante a la entrega. Para proyectos de mayor envergadura podrán acordarse hitos de
            pago parciales. El incumplimiento de los plazos de pago faculta a la Empresa para
            suspender la prestación del servicio.
          </p>
          <h3>4.4 Cancelaciones y desistimiento</h3>
          <p>
            El cliente podrá cancelar un proyecto en cualquier momento mediante comunicación escrita
            a <a href={`mailto:${COMPANY_INFO.email}`}>{COMPANY_INFO.email}</a>. En caso de
            cancelación, el cliente abonará el importe correspondiente a los trabajos efectivamente
            realizados hasta la fecha de notificación de la cancelación. El pago inicial no es
            reembolsable salvo incumplimiento imputable a la Empresa.
          </p>

          {/* 5 */}
          <h2>5. Propiedad intelectual</h2>
          <h3>5.1 Contenidos del sitio web</h3>
          <p>
            Todos los contenidos del sitio web —incluyendo, sin carácter limitativo, textos,
            imágenes, gráficos, logotipos, iconos, código fuente, diseño y estructura de
            navegación— son propiedad de la Empresa o de terceros que han autorizado su uso, y
            están protegidos por las leyes españolas e internacionales de propiedad intelectual e
            industrial.
          </p>
          <p>
            Queda prohibida la reproducción total o parcial de los contenidos del sitio web sin la
            autorización expresa y por escrito de la Empresa, salvo para uso personal y privado del
            usuario o para los usos permitidos por la normativa de propiedad intelectual vigente.
          </p>
          <h3>5.2 Entregables de los proyectos</h3>
          <p>
            Salvo pacto escrito en contrario, los derechos de propiedad intelectual sobre los
            entregables desarrollados específicamente para el cliente (flujos de automatización,
            código personalizado, materiales de formación a medida) se ceden al cliente tras el
            pago íntegro del proyecto.
          </p>
          <p>
            La Empresa se reserva el derecho a reutilizar métodos, técnicas, conocimientos
            generales y componentes reutilizables no específicos del cliente en otros proyectos,
            siempre que no impliquen divulgación de información confidencial del cliente.
          </p>
          <h3>5.3 Marcas comerciales</h3>
          <p>
            Las marcas, nombres comerciales y distintivos que aparecen en el sitio web son
            propiedad de la Empresa o de sus respectivos titulares. El acceso al sitio web no
            otorga ningún derecho sobre dichas marcas o nombres comerciales.
          </p>

          {/* 6 */}
          <h2>6. Confidencialidad</h2>
          <p>
            La Empresa se compromete a mantener la confidencialidad de toda información de negocio
            que el cliente le facilite en el marco del proyecto. Asimismo, el cliente se compromete
            a no divulgar a terceros los métodos de trabajo, herramientas propietarias y know-how
            de la Empresa sin su consentimiento previo y por escrito.
          </p>
          <p>
            La obligación de confidencialidad se mantendrá vigente durante el tiempo de duración
            del proyecto y los dos años siguientes a su finalización, salvo que la información se
            haya hecho pública por medios lícitos ajenos a las partes.
          </p>

          {/* 7 */}
          <h2>7. Limitación de responsabilidad</h2>
          <h3>7.1 Exactitud de la información</h3>
          <p>
            La Empresa no garantiza la exactitud, veracidad o actualidad de todos los contenidos
            informativos del sitio web. Dichos contenidos tienen finalidad meramente informativa y
            no constituyen asesoramiento profesional vinculante.
          </p>
          <h3>7.2 Disponibilidad del sitio web</h3>
          <p>
            La Empresa no garantiza la disponibilidad continua e ininterrumpida del sitio web y
            queda exenta de responsabilidad por los daños derivados de su falta de disponibilidad,
            interrupciones por mantenimiento o causas de fuerza mayor.
          </p>
          <h3>7.3 Resultados de los servicios</h3>
          <p>
            Los resultados descritos en casos de uso y estimaciones de ROI son indicativos y se
            basan en proyectos anteriores. La Empresa no garantiza que los resultados obtenidos en
            proyectos anteriores se reproduzcan en todo caso, dado que dependen de múltiples
            factores propios del negocio del cliente.
          </p>
          <p>
            La responsabilidad total de la Empresa frente al cliente derivada del contrato de
            servicios quedará limitada al importe efectivamente abonado por el cliente por dichos
            servicios, salvo en casos de dolo o negligencia grave.
          </p>
          <h3>7.4 Terceros y herramientas externas</h3>
          <p>
            Los servicios de la Empresa pueden hacer uso de herramientas, APIs y modelos de
            inteligencia artificial de terceros (OpenAI, Anthropic, Google, entre otros). La
            Empresa no es responsable de los cambios en las condiciones, disponibilidad o
            comportamiento de dichos servicios de terceros.
          </p>

          {/* 8 */}
          <h2>8. Protección de datos</h2>
          <p>
            El tratamiento de los datos personales de usuarios y clientes se rige por nuestra{' '}
            <Link href="/privacidad">Política de Privacidad</Link>, que forma parte integrante de
            los presentes Términos. En los proyectos donde la Empresa actúe como encargada del
            tratamiento de datos personales del cliente, se suscribirá el correspondiente Acuerdo
            de Procesamiento de Datos (DPA) conforme al Reglamento (UE) 2016/679 (RGPD) y la Ley
            Orgánica 3/2018, de Protección de Datos Personales y garantía de los derechos
            digitales.
          </p>

          {/* 9 */}
          <h2>9. Ley aplicable y jurisdicción</h2>
          <p>
            Los presentes Términos y Condiciones se rigen íntegramente por la legislación española.
            Para la resolución de cualquier controversia o reclamación derivada de la interpretación
            o ejecución de los presentes Términos o de los servicios prestados, las partes se
            someten, con renuncia expresa a cualquier otro fuero que pudiera corresponderles, a los
            Juzgados y Tribunales de la ciudad de Madrid.
          </p>
          <p>
            Sin perjuicio de lo anterior, si el cliente tiene la condición de consumidor conforme a
            la normativa vigente, podrá acudir a la plataforma de resolución de litigios en línea
            de la Unión Europea:{' '}
            <a
              href="https://ec.europa.eu/consumers/odr"
              target="_blank"
              rel="noopener noreferrer"
            >
              https://ec.europa.eu/consumers/odr
            </a>
            .
          </p>

          {/* 10 */}
          <h2>10. Contacto</h2>
          <p>
            Para cualquier consulta relacionada con los presentes Términos y Condiciones, puede
            contactar con nosotros a través de:
          </p>
          <ul>
            <li>
              <strong>Correo electrónico:</strong>{' '}
              <a href={`mailto:${COMPANY_INFO.email}`}>{COMPANY_INFO.email}</a>
            </li>
            <li>
              <strong>Dirección postal:</strong> {COMPANY_INFO.direccion},{' '}
              {COMPANY_INFO.ciudad}, {COMPANY_INFO.pais}
            </li>
          </ul>
          <p>
            También puede consultar nuestra{' '}
            <Link href="/privacidad">Política de Privacidad</Link>,{' '}
            <Link href="/cookies">Política de Cookies</Link> y{' '}
            <Link href="/aviso-legal">Aviso Legal</Link>.
          </p>

        </div>
      </div>
    </main>
  )
}
