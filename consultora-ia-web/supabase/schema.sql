-- ============================================================================
-- AP Automatización IA — Esquema de base de datos Supabase
-- ============================================================================

-- ─── Habilitar extensiones ────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Tabla: leads ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS leads (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at            TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  name                  TEXT NOT NULL,
  company               TEXT,
  role                  TEXT,
  email                 TEXT NOT NULL,
  phone                 TEXT,
  sector                TEXT,
  employees_range       TEXT,
  service_interest      TEXT,
  main_problem          TEXT,
  tools_used            TEXT[],
  preferred_contact_time TEXT,
  lead_score            INTEGER DEFAULT 0 CHECK (lead_score >= 0 AND lead_score <= 100),
  status                TEXT DEFAULT 'nuevo' CHECK (status IN ('nuevo', 'contactado', 'reunión_agendada', 'propuesta_enviada', 'cerrado_ganado', 'cerrado_perdido', 'descartado')),
  source                TEXT DEFAULT 'web' CHECK (source IN ('web', 'chatbot', 'referido', 'email', 'linkedin', 'evento', 'otro')),
  notes                 TEXT,
  qualification         TEXT CHECK (qualification IN ('consultoría_ia', 'automatización', 'agentes_ia', 'información', 'no_cualificado'))
);

COMMENT ON TABLE leads IS 'Leads captados desde el sitio web y el chatbot de AP Automatización IA';
COMMENT ON COLUMN leads.lead_score IS 'Puntuación de 0-100 calculada automáticamente según criterios de cualificación';
COMMENT ON COLUMN leads.qualification IS 'Tipo de servicio de interés identificado en la conversación con el bot';

-- ─── Tabla: bot_conversations ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bot_conversations (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id               UUID REFERENCES leads(id) ON DELETE SET NULL,
  created_at            TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  messages              JSONB NOT NULL DEFAULT '[]'::jsonb,
  summary               TEXT,
  intent                TEXT,
  qualification_score   INTEGER DEFAULT 0 CHECK (qualification_score >= 0 AND qualification_score <= 100)
);

COMMENT ON TABLE bot_conversations IS 'Historial completo de conversaciones del chatbot comercial';
COMMENT ON COLUMN bot_conversations.messages IS 'Array JSON de mensajes con campos: role, content, timestamp';

-- ─── Tabla: contact_requests ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contact_requests (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at            TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  name                  TEXT NOT NULL,
  email                 TEXT NOT NULL,
  phone                 TEXT,
  company               TEXT,
  message               TEXT,
  service_interest      TEXT,
  status                TEXT DEFAULT 'pendiente' CHECK (status IN ('pendiente', 'en_gestión', 'resuelto', 'cerrado'))
);

COMMENT ON TABLE contact_requests IS 'Solicitudes de contacto recibidas a través del formulario de la web';

-- ─── Tabla: newsletter_subscribers ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at            TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  email                 TEXT UNIQUE NOT NULL,
  source                TEXT DEFAULT 'web',
  status                TEXT DEFAULT 'activo' CHECK (status IN ('activo', 'baja', 'rebotado'))
);

COMMENT ON TABLE newsletter_subscribers IS 'Suscriptores de la newsletter de AP Automatización IA';

-- ─── Índices ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS leads_email_idx           ON leads(email);
CREATE INDEX IF NOT EXISTS leads_status_idx          ON leads(status);
CREATE INDEX IF NOT EXISTS leads_created_at_idx      ON leads(created_at DESC);
CREATE INDEX IF NOT EXISTS leads_lead_score_idx      ON leads(lead_score DESC);
CREATE INDEX IF NOT EXISTS leads_qualification_idx   ON leads(qualification);

CREATE INDEX IF NOT EXISTS bot_conv_lead_id_idx      ON bot_conversations(lead_id);
CREATE INDEX IF NOT EXISTS bot_conv_created_at_idx   ON bot_conversations(created_at DESC);

CREATE INDEX IF NOT EXISTS contact_req_email_idx     ON contact_requests(email);
CREATE INDEX IF NOT EXISTS contact_req_status_idx    ON contact_requests(status);
CREATE INDEX IF NOT EXISTS contact_req_created_at_idx ON contact_requests(created_at DESC);

CREATE INDEX IF NOT EXISTS newsletter_email_idx      ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS newsletter_status_idx     ON newsletter_subscribers(status);

-- ─── Función: calcular lead_score ────────────────────────────────────────────
CREATE OR REPLACE FUNCTION calculate_lead_score(
  p_employees_range TEXT,
  p_qualification   TEXT,
  p_name            TEXT,
  p_email           TEXT,
  p_company         TEXT,
  p_role            TEXT,
  p_phone           TEXT,
  p_tools_count     INTEGER DEFAULT 0,
  p_preferred_time  TEXT DEFAULT NULL
) RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
  v_score INTEGER := 0;
BEGIN
  -- Tamaño empresa (0–25)
  v_score := v_score + CASE p_employees_range
    WHEN '1-10 empleados'    THEN 10
    WHEN '11-50 empleados'   THEN 18
    WHEN '51-200 empleados'  THEN 22
    WHEN 'Más de 200'        THEN 25
    ELSE 5
  END;

  -- Herramientas (0–20)
  IF p_tools_count >= 4    THEN v_score := v_score + 20;
  ELSIF p_tools_count >= 2 THEN v_score := v_score + 12;
  ELSIF p_tools_count = 1  THEN v_score := v_score + 6;
  END IF;

  -- Cualificación / interés (0–25)
  v_score := v_score + CASE p_qualification
    WHEN 'automatización'  THEN 25
    WHEN 'agentes_ia'      THEN 25
    WHEN 'consultoría_ia'  THEN 20
    WHEN 'información'     THEN 10
    WHEN 'no_cualificado'  THEN 0
    ELSE 5
  END;

  -- Datos de contacto completados (0–30)
  IF p_name IS NOT NULL AND p_name != ''     THEN v_score := v_score + 5; END IF;
  IF p_email IS NOT NULL AND p_email != ''   THEN v_score := v_score + 5; END IF;
  IF p_company IS NOT NULL AND p_company != '' THEN v_score := v_score + 5; END IF;
  IF p_role IS NOT NULL AND p_role != ''     THEN v_score := v_score + 5; END IF;
  IF p_phone IS NOT NULL AND p_phone != ''   THEN v_score := v_score + 5; END IF;
  IF p_preferred_time IS NOT NULL            THEN v_score := v_score + 5; END IF;

  RETURN LEAST(v_score, 100);
END;
$$;

COMMENT ON FUNCTION calculate_lead_score IS 'Calcula la puntuación de cualificación de un lead entre 0 y 100';

-- ─── Habilitar Row Level Security ─────────────────────────────────────────────
ALTER TABLE leads                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_conversations      ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_requests       ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

-- ─── Políticas RLS: solo el service role puede leer/escribir ──────────────────
-- Las API routes de Next.js usan el service_role key (en el servidor).
-- Desde el cliente nunca se exponen estas tablas directamente.

-- leads: solo inserción anónima (para el formulario de contacto en cliente)
--        lectura solo para autenticados (panel admin)
CREATE POLICY "leads_insert_anon"
  ON leads FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "leads_select_authed"
  ON leads FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "leads_update_authed"
  ON leads FOR UPDATE
  TO authenticated
  USING (true);

-- bot_conversations: solo inserción anónima, lectura autenticada
CREATE POLICY "bot_conv_insert_anon"
  ON bot_conversations FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "bot_conv_select_authed"
  ON bot_conversations FOR SELECT
  TO authenticated
  USING (true);

-- contact_requests: inserción anónima, gestión autenticada
CREATE POLICY "contact_insert_anon"
  ON contact_requests FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "contact_select_authed"
  ON contact_requests FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "contact_update_authed"
  ON contact_requests FOR UPDATE
  TO authenticated
  USING (true);

-- newsletter_subscribers: inserción anónima, gestión autenticada
CREATE POLICY "newsletter_insert_anon"
  ON newsletter_subscribers FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "newsletter_select_authed"
  ON newsletter_subscribers FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "newsletter_update_authed"
  ON newsletter_subscribers FOR UPDATE
  TO authenticated
  USING (true);

-- ─── Vista: leads con score calculado (útil para el panel admin) ──────────────
CREATE OR REPLACE VIEW leads_overview AS
SELECT
  l.id,
  l.created_at,
  l.name,
  l.email,
  l.company,
  l.role,
  l.employees_range,
  l.service_interest,
  l.qualification,
  l.lead_score,
  l.status,
  l.source,
  l.preferred_contact_time,
  COUNT(bc.id) AS conversation_count
FROM leads l
LEFT JOIN bot_conversations bc ON bc.lead_id = l.id
GROUP BY l.id;

COMMENT ON VIEW leads_overview IS 'Vista con datos de leads y número de conversaciones asociadas';
