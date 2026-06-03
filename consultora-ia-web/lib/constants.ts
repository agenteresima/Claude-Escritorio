import type { CompanyInfo, NavItem, Service, FAQItem, UseCase } from './types'

// ============================================================
// Información de empresa
// ============================================================

export const COMPANY_INFO: CompanyInfo = {
  nombre: 'AP Automatización IA',
  nombre_legal: 'Nexus Inteligencia Artificial S.L.',
  slogan: 'El experto en IA que tu empresa todavía no tiene en plantilla',
  descripcion:
    'Ayudamos a empresas de todos los sectores a implantar inteligencia artificial de forma práctica, rentable y sin complicaciones. Desde la estrategia hasta la automatización de tus primeros procesos.',
  email: 'hola@automatizacionprocesos.es',
  email_soporte: 'soporte@automatizacionprocesos.es',
  telefono: '+34 900 000 000',
  direccion: 'Calle de Alcalá, 50, 1ª planta',
  ciudad: 'Madrid',
  pais: 'España',
  redes_sociales: {
    linkedin: 'https://www.linkedin.com/company/apautomatizacion',
    twitter: 'https://twitter.com/apautomatizacion_es',
    youtube: 'https://youtube.com/@apautomatizacion',
  },
}

// ============================================================
// Navegación principal
// ============================================================

export const NAV_ITEMS: NavItem[] = [
  {
    label: 'Servicios',
    href: '/servicios',
    hijos: [
      {
        label: 'Automatización de procesos',
        href: '/servicios/automatizacion-procesos',
        descripcion: 'Elimina tareas repetitivas y gana horas al día con flujos de trabajo inteligentes.',
      },
      {
        label: 'Agentes de IA',
        href: '/servicios/agentes-ia',
        descripcion: 'Asistentes autónomos que trabajan 24/7 para tu equipo sin supervisión constante.',
      },
      {
        label: 'Chatbots inteligentes',
        href: '/servicios/chatbots-inteligentes',
        descripcion: 'Atención al cliente automatizada que responde como un humano experto.',
      },
      {
        label: 'Formación en IA',
        href: '/servicios/formacion-ia',
        descripcion: 'Capacita a tu equipo para trabajar de forma nativa con herramientas de IA.',
      },
      {
        label: 'Estrategia de IA',
        href: '/servicios/estrategia-ia',
        descripcion: 'Hoja de ruta personalizada para la transformación digital de tu empresa.',
      },
      {
        label: 'Análisis de datos con IA',
        href: '/servicios/analisis-datos-ia',
        descripcion: 'Convierte tus datos en insights accionables usando modelos de lenguaje y ML.',
      },
    ],
  },
  {
    label: 'Casos de éxito',
    href: '/casos-de-exito',
  },
  {
    label: 'Blog',
    href: '/blog',
  },
  {
    label: 'Sobre nosotros',
    href: '/sobre-nosotros',
  },
  {
    label: 'Contacto',
    href: '/contacto',
  },
]

// ============================================================
// Servicios
// ============================================================

export const SERVICES: Service[] = [
  {
    id: 'automatizacion-procesos',
    slug: 'automatizacion-procesos',
    nombre: 'Automatización de procesos con IA',
    descripcion_corta:
      'Elimina tareas repetitivas y ahorra cientos de horas al mes automatizando tus flujos de trabajo con inteligencia artificial.',
    descripcion_larga:
      'Analizamos tus procesos operativos actuales y diseñamos soluciones de automatización inteligente que combinan RPA, flujos n8n y modelos de lenguaje avanzados. El resultado: menos errores, más velocidad y tu equipo enfocado en lo que realmente importa.',
    icono: 'Zap',
    categoria: 'automatizacion',
    beneficios: [
      'Reduce hasta un 80% del tiempo en tareas administrativas',
      'Elimina errores humanos en procesos críticos',
      'Escala sin contratar más personal',
      'ROI visible en los primeros 30 días',
    ],
    caracteristicas: [
      'Auditoría completa de procesos actuales',
      'Diseño de flujos automatizados con n8n y Make',
      'Integración con tus herramientas existentes (ERP, CRM, email)',
      'Procesamiento inteligente de documentos (facturas, contratos, informes)',
      'Panel de control y monitorización en tiempo real',
      'Soporte y mantenimiento incluido 3 meses',
    ],
    precio_desde: 'Desde 2.500 €',
    duracion_tipica: '2-6 semanas',
    destacado: true,
    orden: 1,
  },
  {
    id: 'agentes-ia',
    slug: 'agentes-ia',
    nombre: 'Agentes de Inteligencia Artificial',
    descripcion_corta:
      'Despliega agentes autónomos que ejecutan tareas complejas, toman decisiones y se coordinan con tu equipo sin supervisión constante.',
    descripcion_larga:
      'Los agentes de IA son el siguiente paso de la automatización: sistemas que no solo ejecutan tareas, sino que razonan, planifican y se adaptan. Diseñamos agentes a medida para ventas, soporte, operaciones o investigación que trabajan de forma continua.',
    icono: 'Bot',
    categoria: 'agentes',
    beneficios: [
      'Operaciones 24/7 sin intervención humana',
      'Gestión autónoma de tareas de alta complejidad',
      'Adaptación continua al contexto del negocio',
      'Coordinación multi-agente para proyectos complejos',
    ],
    caracteristicas: [
      'Diseño de arquitectura de agente a medida',
      'Integración con APIs, bases de datos y herramientas internas',
      'Memoria persistente y contexto de empresa',
      'Supervisión humana configurable (HITL)',
      'Logging completo de decisiones y acciones',
      'Evaluación y ajuste continuo del comportamiento',
    ],
    precio_desde: 'Desde 3.500 €',
    duracion_tipica: '3-8 semanas',
    destacado: true,
    orden: 2,
  },
  {
    id: 'chatbots-inteligentes',
    slug: 'chatbots-inteligentes',
    nombre: 'Chatbots inteligentes',
    descripcion_corta:
      'Asistentes conversacionales avanzados para atención al cliente, soporte interno o generación de leads que responden como expertos reales.',
    descripcion_larga:
      'Construimos chatbots potenciados por los mejores LLMs (GPT-4, Claude, Gemini) entrenados con el conocimiento de tu empresa. No son chatbots de árbol de decisión: entienden contexto, resuelven dudas complejas y escalan cuando es necesario.',
    icono: 'MessageSquare',
    categoria: 'chatbots',
    beneficios: [
      'Resuelve el 70-80% de las consultas sin intervención humana',
      'Disponible 24/7 en web, WhatsApp y otros canales',
      'Aprende y mejora con cada conversación',
      'Captura leads cualificados automáticamente',
    ],
    caracteristicas: [
      'Base de conocimiento personalizada con tus documentos',
      'Integración omnicanal (web, WhatsApp Business, Telegram)',
      'Escalado a agente humano con contexto completo',
      'Panel de conversaciones y analíticas',
      'RGPD compliant — datos en servidores europeos',
      'A/B testing de respuestas y flujos',
    ],
    precio_desde: 'Desde 1.800 €',
    duracion_tipica: '1-4 semanas',
    destacado: true,
    orden: 3,
  },
  {
    id: 'formacion-ia',
    slug: 'formacion-ia',
    nombre: 'Formación en IA para equipos',
    descripcion_corta:
      'Capacita a tu equipo para trabajar de forma nativa con herramientas de IA y multiplicar su productividad desde el primer día.',
    descripcion_larga:
      'La mejor inversión en IA es un equipo que sabe usarla. Diseñamos programas de formación práctica, desde la introducción a herramientas IA hasta cursos avanzados de prompt engineering y automatización, adaptados al sector y nivel de cada equipo.',
    icono: 'GraduationCap',
    categoria: 'formacion',
    beneficios: [
      'Equipos 40% más productivos en 30 días',
      'Reducción de la curva de aprendizaje IA',
      'Cultura de innovación interna',
      'Retorno inmediato en tareas del día a día',
    ],
    caracteristicas: [
      'Diagnóstico de nivel actual del equipo',
      'Formación presencial y/o en remoto',
      'Materiales y playbooks personalizados para tu sector',
      'Casos prácticos con herramientas del equipo',
      'Seguimiento y sesiones de refuerzo',
      'Certificado de formación en IA',
    ],
    precio_desde: 'Desde 800 € por sesión',
    duracion_tipica: '1 día a 8 semanas',
    destacado: false,
    orden: 4,
  },
  {
    id: 'estrategia-ia',
    slug: 'estrategia-ia',
    nombre: 'Estrategia e implantación de IA',
    descripcion_corta:
      'Hoja de ruta personalizada para integrar la IA en tu empresa: qué implantar, en qué orden, con qué presupuesto y qué resultados esperar.',
    descripcion_larga:
      'Antes de gastar un euro en tecnología, necesitas saber exactamente dónde la IA te dará más retorno. Analizamos tu empresa, identificamos las oportunidades de mayor impacto y te entregamos un plan de implantación claro, priorizado y con métricas de éxito.',
    icono: 'Target',
    categoria: 'estrategia',
    beneficios: [
      'Claridad absoluta sobre dónde invertir en IA',
      'Evita inversiones en tecnología sin retorno',
      'Plan ejecutable desde la primera semana',
      'Alineación de tecnología con objetivos de negocio',
    ],
    caracteristicas: [
      'Taller de diagnóstico digital con dirección',
      'Mapa de procesos y oportunidades IA',
      'Análisis de tecnología y proveedores',
      'Hoja de ruta 12 meses con hitos claros',
      'Estimación de ROI por iniciativa',
      'Presentación ejecutiva para consejo o inversores',
    ],
    precio_desde: 'Desde 3.000 €',
    duracion_tipica: '2-4 semanas',
    destacado: false,
    orden: 5,
  },
  {
    id: 'analisis-datos-ia',
    slug: 'analisis-datos-ia',
    nombre: 'Análisis de datos con IA',
    descripcion_corta:
      'Convierte los datos de tu empresa en decisiones inteligentes usando modelos de lenguaje, dashboards automáticos e informes generados por IA.',
    descripcion_larga:
      'Tus datos tienen respuestas valiosas, pero leerlos lleva tiempo. Construimos pipelines de análisis inteligente que conectan con tus fuentes de datos, generan informes automáticos, detectan anomalías y responden preguntas en lenguaje natural.',
    icono: 'BarChart3',
    categoria: 'analisis',
    beneficios: [
      'Informes automáticos que antes tardaban días',
      'Detección temprana de problemas y oportunidades',
      'Preguntas a tus datos en lenguaje natural',
      'Decisiones basadas en datos, no en intuición',
    ],
    caracteristicas: [
      'Conexión con tus fuentes de datos existentes',
      'Dashboards automáticos con IA generativa',
      'Alertas inteligentes por email o Slack',
      'Chat con tus datos (NL2SQL)',
      'Informes ejecutivos automáticos semanales',
      'Modelos predictivos para ventas y demanda',
    ],
    precio_desde: 'Desde 2.000 €',
    duracion_tipica: '2-5 semanas',
    destacado: false,
    orden: 6,
  },
]

// ============================================================
// Casos de uso
// ============================================================

export const USE_CASES: UseCase[] = [
  {
    id: 'administracion-facturas',
    titulo: 'Automatización de facturas y contabilidad',
    descripcion:
      'Un despacho contable procesaba 300 facturas al mes manualmente. Implantamos un agente que extrae, valida y registra automáticamente cada factura en su ERP.',
    sector: 'Contabilidad y finanzas',
    resultado: 'De 2 días de trabajo a 15 minutos',
    metricas: [
      { label: 'Reducción de tiempo', valor: '94%', mejora: '+94%' },
      { label: 'Errores de captura', valor: '0%', mejora: '-100%' },
      { label: 'ROI en', valor: '3 semanas', mejora: '' },
    ],
    icono: 'FileText',
    servicio_relacionado: 'automatizacion',
  },
  {
    id: 'ventas-asistente',
    titulo: 'Asistente de ventas con IA',
    descripcion:
      'Una empresa B2B recibía 200 consultas comerciales semanales. Desplegamos un agente que cualifica, responde y agenda reuniones automáticamente.',
    sector: 'Ventas B2B',
    resultado: 'Tasa de conversión +38% con el mismo equipo',
    metricas: [
      { label: 'Consultas atendidas 24/7', valor: '100%', mejora: '' },
      { label: 'Aumento conversión', valor: '+38%', mejora: '' },
      { label: 'Tiempo respuesta', valor: '< 2 min', mejora: '' },
    ],
    icono: 'TrendingUp',
    servicio_relacionado: 'agentes',
  },
  {
    id: 'rrhh-seleccion',
    titulo: 'Cribado de CVs con IA para RRHH',
    descripcion:
      'El departamento de RRHH de una empresa con 500 empleados tardaba 4 horas en cribar 100 CVs. Ahora un agente los analiza, puntúa y genera resúmenes en 10 minutos.',
    sector: 'Recursos Humanos',
    resultado: 'Proceso de selección 5x más rápido',
    metricas: [
      { label: 'Reducción tiempo cribado', valor: '96%', mejora: '' },
      { label: 'CVs procesados/hora', valor: '600', mejora: '+500%' },
      { label: 'Candidatos relevantes detectados', valor: '+22%', mejora: '' },
    ],
    icono: 'Users',
    servicio_relacionado: 'agentes',
  },
  {
    id: 'atencion-cliente',
    titulo: 'Atención al cliente 24/7 con chatbot',
    descripcion:
      'Un e-commerce con 10.000 pedidos mensuales gestionaba el soporte con 3 personas. Implantamos un chatbot que resuelve el 78% de las consultas sin intervención humana.',
    sector: 'E-commerce',
    resultado: '78% de consultas resueltas sin agente humano',
    metricas: [
      { label: 'Consultas auto-resueltas', valor: '78%', mejora: '' },
      { label: 'Satisfacción cliente (CSAT)', valor: '4.7/5', mejora: '+0.8' },
      { label: 'Coste por ticket', valor: '-65%', mejora: '' },
    ],
    icono: 'MessageCircle',
    servicio_relacionado: 'chatbots',
  },
  {
    id: 'informes-automaticos',
    titulo: 'Informes ejecutivos generados por IA',
    descripcion:
      'Una cadena de retail generaba informes semanales de ventas que tardaban medio día en preparar. Ahora se generan automáticamente cada lunes a las 7:00 en el buzón del director.',
    sector: 'Retail',
    resultado: 'Informes automáticos con cero intervención humana',
    metricas: [
      { label: 'Tiempo preparación informe', valor: '0 min', mejora: '-240 min' },
      { label: 'Datos analizados', valor: '100%', mejora: '+60%' },
      { label: 'Decisiones más rápidas', valor: '3x', mejora: '' },
    ],
    icono: 'BarChart3',
    servicio_relacionado: 'analisis',
  },
  {
    id: 'juridico-contratos',
    titulo: 'Revisión de contratos con IA jurídica',
    descripcion:
      'Un despacho de abogados revisaba contratos de 20-50 páginas en 3-4 horas por abogado. Con nuestro agente jurídico, el primer análisis está listo en 5 minutos.',
    sector: 'Legal y jurídico',
    resultado: 'Revisión inicial de contratos en 5 minutos',
    metricas: [
      { label: 'Reducción tiempo revisión', valor: '97%', mejora: '' },
      { label: 'Cláusulas de riesgo detectadas', valor: '+31%', mejora: '' },
      { label: 'Capacidad de casos por semana', valor: '+4x', mejora: '' },
    ],
    icono: 'Scale',
    servicio_relacionado: 'agentes',
  },
  {
    id: 'marketing-contenido',
    titulo: 'Generación de contenido de marketing',
    descripcion:
      'Una agencia de marketing producía 20 piezas de contenido semanales. Desplegamos un flujo de IA que genera borradores de blog, redes sociales y emails en el tono de marca.',
    sector: 'Marketing y comunicación',
    resultado: 'Producción de contenido x5 con el mismo equipo',
    metricas: [
      { label: 'Piezas producidas/semana', valor: '100', mejora: '+400%' },
      { label: 'Tiempo por pieza', valor: '8 min', mejora: '-85%' },
      { label: 'Consistencia de marca', valor: '95%', mejora: '' },
    ],
    icono: 'PenTool',
    servicio_relacionado: 'automatizacion',
  },
  {
    id: 'logistica-incidencias',
    titulo: 'Gestión de incidencias logísticas con IA',
    descripcion:
      'Una empresa de logística gestionaba 150 incidencias diarias por email. El agente las clasifica, prioriza y resuelve las más simples automáticamente, escalando solo las complejas.',
    sector: 'Logística y transporte',
    resultado: '60% de incidencias resueltas sin intervención',
    metricas: [
      { label: 'Incidencias auto-resueltas', valor: '60%', mejora: '' },
      { label: 'Tiempo medio resolución', valor: '-72%', mejora: '' },
      { label: 'Satisfacción cliente', valor: '+25%', mejora: '' },
    ],
    icono: 'Truck',
    servicio_relacionado: 'agentes',
  },
]

// ============================================================
// FAQ
// ============================================================

export const FAQ_ITEMS: FAQItem[] = [
  {
    id: 'faq-1',
    pregunta: '¿Necesito saber de tecnología para trabajar con vosotros?',
    respuesta:
      'No, en absoluto. Nos adaptamos al nivel técnico de cada empresa. Nuestro trabajo es hacer que la IA sea accesible y útil para tu negocio sin que tengas que entender cómo funciona por dentro. Tú nos explicas el problema, nosotros te damos la solución.',
    categoria: 'general',
    orden: 1,
  },
  {
    id: 'faq-2',
    pregunta: '¿Cuánto tiempo tarda en verse el retorno de la inversión?',
    respuesta:
      'En la mayoría de proyectos de automatización el ROI es visible en las primeras 2-6 semanas. Los proyectos de agentes y chatbots suelen tardar entre 1 y 3 meses en alcanzar su máximo rendimiento. Siempre te damos una estimación realista antes de comenzar.',
    categoria: 'inversión',
    orden: 2,
  },
  {
    id: 'faq-3',
    pregunta: '¿Con qué herramientas y plataformas trabajáis?',
    respuesta:
      'Trabajamos con los mejores modelos de lenguaje del mercado (GPT-4, Claude, Gemini) y plataformas de automatización como n8n, Make y Zapier. Para bases de datos y backend usamos Supabase, PostgreSQL y múltiples APIs de terceros. Siempre elegimos la herramienta más adecuada para cada caso, no la que más nos convenga a nosotros.',
    categoria: 'técnico',
    orden: 3,
  },
  {
    id: 'faq-4',
    pregunta: '¿Mis datos están seguros? ¿Cumplís con el RGPD?',
    respuesta:
      'Sí. Todos los proyectos que desarrollamos cumplen con el RGPD y la normativa española de protección de datos. Los datos de tus clientes y empresa se procesan en servidores europeos. Firmamos un Acuerdo de Procesamiento de Datos (DPA) con todos los clientes y nunca usamos tus datos para entrenar modelos de terceros.',
    categoria: 'seguridad',
    orden: 4,
  },
  {
    id: 'faq-5',
    pregunta: '¿Qué tamaño de empresa necesita para contratar vuestros servicios?',
    respuesta:
      'Trabajamos con empresas desde 5 empleados hasta grandes corporaciones. El valor de la IA no depende del tamaño de la empresa, sino de tener procesos repetitivos o necesidades de escala. Una pyme puede beneficiarse igual o más que una gran empresa.',
    categoria: 'general',
    orden: 5,
  },
  {
    id: 'faq-6',
    pregunta: '¿Qué ocurre si el proyecto no funciona como esperaba?',
    respuesta:
      'Todos nuestros proyectos incluyen una fase de validación con métricas de éxito acordadas antes de comenzar. Si el resultado no alcanza los objetivos pactados, seguimos trabajando sin coste adicional hasta conseguirlo. La satisfacción del cliente es nuestra garantía.',
    categoria: 'garantía',
    orden: 6,
  },
  {
    id: 'faq-7',
    pregunta: '¿Integráis la IA con nuestro software actual (ERP, CRM, etc.)?',
    respuesta:
      'Sí, es una de nuestras especialidades. Integramos con los sistemas más comunes: Salesforce, HubSpot, SAP, Holded, Sage, Odoo, Google Workspace, Microsoft 365, y prácticamente cualquier sistema que tenga API. Si no tiene API, buscamos soluciones alternativas.',
    categoria: 'técnico',
    orden: 7,
  },
  {
    id: 'faq-8',
    pregunta: '¿Cuánto cuesta un proyecto típico de automatización con IA?',
    respuesta:
      'Los precios varían según la complejidad. Un chatbot básico puede estar desde 1.800 €, una automatización de proceso desde 2.500 €, y un agente IA complejo desde 3.500 €. Siempre hacemos una propuesta detallada después de entender tu necesidad. El primer diagnóstico es gratuito y sin compromiso.',
    categoria: 'inversión',
    orden: 8,
  },
  {
    id: 'faq-9',
    pregunta: '¿Ofrecéis soporte y mantenimiento después del proyecto?',
    respuesta:
      'Todos los proyectos incluyen soporte de 3 meses post-implantación. Después ofrecemos contratos de mantenimiento mensual que incluyen monitorización, actualizaciones y mejoras continuas. Los modelos de IA evolucionan rápido y queremos que tu solución siempre esté al día.',
    categoria: 'soporte',
    orden: 9,
  },
  {
    id: 'faq-10',
    pregunta: '¿Cómo empezamos a trabajar juntos?',
    respuesta:
      'El proceso es sencillo: (1) Solicita un diagnóstico gratuito a través del formulario o el chatbot. (2) En 24 horas te contactamos para una llamada de 30 minutos para entender tu necesidad. (3) Te enviamos una propuesta concreta con alcance, plazo y precio. (4) Si aceptas, empezamos en menos de una semana.',
    categoria: 'proceso',
    orden: 10,
  },
]

// ============================================================
// Rutas del sitio (para sitemap y navegación)
// ============================================================

export const SITE_ROUTES = [
  { path: '/', prioridad: '1.0', cambio: 'weekly' },
  { path: '/servicios', prioridad: '0.9', cambio: 'weekly' },
  { path: '/servicios/automatizacion-procesos', prioridad: '0.8', cambio: 'monthly' },
  { path: '/servicios/agentes-ia', prioridad: '0.8', cambio: 'monthly' },
  { path: '/servicios/chatbots-inteligentes', prioridad: '0.8', cambio: 'monthly' },
  { path: '/servicios/formacion-ia', prioridad: '0.8', cambio: 'monthly' },
  { path: '/servicios/estrategia-ia', prioridad: '0.8', cambio: 'monthly' },
  { path: '/servicios/analisis-datos-ia', prioridad: '0.8', cambio: 'monthly' },
  { path: '/casos-de-exito', prioridad: '0.8', cambio: 'monthly' },
  { path: '/blog', prioridad: '0.7', cambio: 'daily' },
  { path: '/sobre-nosotros', prioridad: '0.6', cambio: 'monthly' },
  { path: '/contacto', prioridad: '0.9', cambio: 'monthly' },
  { path: '/diagnostico-gratuito', prioridad: '1.0', cambio: 'weekly' },
  { path: '/privacidad', prioridad: '0.3', cambio: 'yearly' },
  { path: '/terminos', prioridad: '0.3', cambio: 'yearly' },
  { path: '/cookies', prioridad: '0.3', cambio: 'yearly' },
]

// ============================================================
// Sectores objetivo
// ============================================================

export const SECTORES = [
  'Tecnología y Software',
  'E-commerce y Retail',
  'Servicios profesionales',
  'Legal y jurídico',
  'Contabilidad y finanzas',
  'Salud y sanidad',
  'Logística y transporte',
  'Marketing y comunicación',
  'Recursos humanos',
  'Inmobiliario',
  'Industria y manufactura',
  'Educación y formación',
  'Otro',
]

// ============================================================
// Opciones de presupuesto para formularios
// ============================================================

export const PRESUPUESTO_OPCIONES = [
  'Menos de 1.500 €',
  '1.500 € — 5.000 €',
  '5.000 € — 15.000 €',
  '15.000 € — 50.000 €',
  'Más de 50.000 €',
  'Todavía no lo sé',
]
