import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Política de Privacidad | AP Automatización IA',
  description:
    'Política de privacidad de AP Automatización IA conforme al Reglamento General de Protección de Datos (RGPD) y la Ley Orgánica de Protección de Datos (LOPDGDD).',
  alternates: { canonical: 'https://automatizacionprocesos.es/privacidad' },
}

export default function PrivacidadPage() {
  return (
    <div className="bg-white pt-24 pb-20">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div className="mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
            Política de privacidad
          </h1>
          <p className="text-slate-500 text-sm">Última actualización: enero de 2025</p>
        </div>

        <div className="prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-slate-900 prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-3 prose-p:text-slate-600 prose-p:leading-relaxed prose-a:text-blue-600 prose-ul:text-slate-600 prose-li:my-1">

          <h2>1. Responsable del tratamiento</h2>
          <p>
            En cumplimiento del Reglamento (UE) 2016/679 del Parlamento Europeo y del Consejo, de
            27 de abril de 2016, relativo a la protección de las personas físicas en lo que respecta
            al tratamiento de datos personales (RGPD), y de la Ley Orgánica 3/2018, de 5 de
            diciembre, de Protección de Datos Personales y garantía de los derechos digitales
            (LOPDGDD), le informamos que el responsable del tratamiento de sus datos personales es:
          </p>
          <ul>
            <li><strong>Denominación:</strong> AP Automatización IA</li>
            <li><strong>Email de contacto:</strong> hola@automatizacionprocesos.es</li>
            <li><strong>Sitio web:</strong> https://automatizacionprocesos.es</li>
          </ul>

          <h2>2. Datos personales que recopilamos</h2>
          <p>
            Recopilamos los datos personales que usted nos facilita voluntariamente a través de los
            formularios de nuestra web, incluyendo:
          </p>
          <ul>
            <li>Nombre y apellidos</li>
            <li>Nombre de la empresa y cargo</li>
            <li>Dirección de correo electrónico</li>
            <li>Número de teléfono (cuando se facilita voluntariamente)</li>
            <li>Información sobre su empresa y necesidades (texto libre)</li>
          </ul>
          <p>
            Asimismo, mediante el uso de cookies y tecnologías similares podemos recopilar datos
            técnicos sobre su navegación. Para más información, consulte nuestra{' '}
            <Link href="/cookies">política de cookies</Link>.
          </p>

          <h2>3. Finalidad del tratamiento</h2>
          <p>Sus datos personales son tratados para las siguientes finalidades:</p>
          <ul>
            <li>
              <strong>Gestión de solicitudes de contacto y diagnóstico:</strong> atender las
              consultas y solicitudes que nos remita a través de los formularios de la web.
            </li>
            <li>
              <strong>Prestación del servicio:</strong> gestionar la relación comercial y prestar
              los servicios contratados.
            </li>
            <li>
              <strong>Comunicaciones comerciales:</strong> enviarle información sobre nuestros
              servicios cuando haya dado su consentimiento expreso para ello.
            </li>
            <li>
              <strong>Newsletter:</strong> enviar el boletín de noticias cuando se haya suscrito
              voluntariamente.
            </li>
          </ul>

          <h2>4. Base legal del tratamiento</h2>
          <p>El tratamiento de sus datos personales se fundamenta en las siguientes bases legales:</p>
          <ul>
            <li>
              <strong>Consentimiento del interesado</strong> (art. 6.1.a RGPD): para el envío de
              comunicaciones comerciales y la suscripción al newsletter.
            </li>
            <li>
              <strong>Ejecución de un contrato</strong> (art. 6.1.b RGPD): cuando los datos son
              necesarios para la prestación de los servicios solicitados.
            </li>
            <li>
              <strong>Interés legítimo</strong> (art. 6.1.f RGPD): para la gestión de las
              solicitudes de información y diagnóstico recibidas.
            </li>
          </ul>

          <h2>5. Destinatarios de los datos</h2>
          <p>
            Sus datos personales no serán cedidos a terceros, salvo obligación legal. Para la
            prestación de nuestros servicios utilizamos proveedores de servicios tecnológicos que
            actúan como encargados del tratamiento y están sujetos a contratos de encargo del
            tratamiento conforme al RGPD:
          </p>
          <ul>
            <li>Proveedores de servicios de correo electrónico y CRM</li>
            <li>Servicios de almacenamiento en la nube</li>
            <li>Herramientas de analítica web</li>
          </ul>
          <p>
            Cuando estos proveedores estén ubicados fuera del Espacio Económico Europeo, se
            aplicarán las garantías adecuadas previstas en el RGPD.
          </p>

          <h2>6. Plazo de conservación</h2>
          <p>
            Sus datos personales serán conservados durante el tiempo necesario para cumplir con la
            finalidad para la que fueron recogidos:
          </p>
          <ul>
            <li>
              <strong>Solicitudes de contacto:</strong> hasta que se resuelva la consulta y durante
              los plazos de prescripción de las acciones legales aplicables (generalmente 5 años).
            </li>
            <li>
              <strong>Relaciones comerciales:</strong> durante la vigencia de la relación
              contractual y los plazos legales de conservación posteriores.
            </li>
            <li>
              <strong>Newsletter:</strong> hasta que retire su consentimiento o solicite la baja.
            </li>
          </ul>

          <h2>7. Derechos del interesado</h2>
          <p>
            Conforme a la normativa vigente en materia de protección de datos, usted tiene los
            siguientes derechos:
          </p>
          <ul>
            <li><strong>Acceso:</strong> conocer qué datos personales tratamos sobre usted.</li>
            <li><strong>Rectificación:</strong> corregir datos inexactos o incompletos.</li>
            <li><strong>Supresión:</strong> solicitar la eliminación de sus datos cuando, entre
            otros casos, ya no sean necesarios para los fines para los que fueron recogidos.</li>
            <li><strong>Limitación:</strong> solicitar que se restrinja el tratamiento de sus datos
            en determinadas circunstancias.</li>
            <li><strong>Portabilidad:</strong> recibir sus datos en un formato estructurado y de
            uso común.</li>
            <li><strong>Oposición:</strong> oponerse al tratamiento de sus datos.</li>
            <li><strong>Retirada del consentimiento:</strong> en cualquier momento, cuando el
            tratamiento esté basado en el consentimiento.</li>
          </ul>
          <p>
            Para ejercer cualquiera de estos derechos, puede dirigirse a{' '}
            <a href="mailto:hola@automatizacionprocesos.es">hola@automatizacionprocesos.es</a>. Tiene derecho a presentar una
            reclamación ante la Agencia Española de Protección de Datos (
            <a href="https://www.aepd.es" target="_blank" rel="noopener noreferrer">
              www.aepd.es
            </a>
            ).
          </p>

          <h2>8. Cookies</h2>
          <p>
            Nuestro sitio web utiliza cookies y tecnologías similares. Para más información, consulte
            nuestra <Link href="/cookies">política de cookies</Link>.
          </p>

          <h2>9. Seguridad de los datos</h2>
          <p>
            Hemos adoptado las medidas técnicas y organizativas necesarias para garantizar la
            seguridad de sus datos personales y evitar su alteración, pérdida, tratamiento o acceso
            no autorizados, teniendo en cuenta el estado de la tecnología, la naturaleza de los
            datos almacenados y los riesgos a los que están expuestos.
          </p>

          <h2>10. Modificaciones de esta política</h2>
          <p>
            AP Automatización IA se reserva el derecho a modificar la presente política de privacidad para
            adaptarla a novedades legislativas o jurisprudenciales. Le notificaremos cualquier
            cambio significativo por los medios adecuados. La continuación en el uso del sitio web
            tras la publicación de los cambios implica la aceptación de los mismos.
          </p>
        </div>
      </div>
    </div>
  )
}
