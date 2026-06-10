import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const alt = 'Automatización Procesos IA — Consultoría de Inteligencia Artificial para Empresas'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default function OGImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: '1200px',
          height: '630px',
          display: 'flex',
          flexDirection: 'column',
          background: 'linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #1D4ED8 100%)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Círculos decorativos de fondo */}
        <div
          style={{
            position: 'absolute',
            top: '-100px',
            right: '-100px',
            width: '500px',
            height: '500px',
            borderRadius: '50%',
            background: 'rgba(37, 99, 235, 0.15)',
            display: 'flex',
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: '-150px',
            left: '-80px',
            width: '400px',
            height: '400px',
            borderRadius: '50%',
            background: 'rgba(37, 99, 235, 0.1)',
            display: 'flex',
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: '200px',
            right: '300px',
            width: '200px',
            height: '200px',
            borderRadius: '50%',
            background: 'rgba(99, 179, 237, 0.08)',
            display: 'flex',
          }}
        />

        {/* Contenido principal */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            padding: '70px 80px',
            height: '100%',
            justifyContent: 'space-between',
          }}
        >
          {/* Logo y nombre */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div
              style={{
                width: '52px',
                height: '52px',
                borderRadius: '14px',
                background: '#2563EB',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '28px',
              }}
            >
              ✦
            </div>
            <span
              style={{
                color: 'white',
                fontSize: '24px',
                fontWeight: '700',
                letterSpacing: '-0.5px',
              }}
            >
              Automatización Procesos IA
            </span>
          </div>

          {/* Título principal */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div
              style={{
                display: 'flex',
                background: 'rgba(37, 99, 235, 0.3)',
                border: '1px solid rgba(99, 179, 237, 0.3)',
                borderRadius: '100px',
                padding: '8px 20px',
                width: 'fit-content',
              }}
            >
              <span style={{ color: '#93C5FD', fontSize: '16px', fontWeight: '600' }}>
                Consultoría de IA para Empresas · Valencia, España
              </span>
            </div>

            <div
              style={{
                color: 'white',
                fontSize: '56px',
                fontWeight: '800',
                lineHeight: '1.1',
                letterSpacing: '-2px',
                maxWidth: '780px',
              }}
            >
              El experto en IA que tu empresa todavía no tiene en plantilla
            </div>

            <div
              style={{
                color: 'rgba(255,255,255,0.65)',
                fontSize: '22px',
                lineHeight: '1.5',
                maxWidth: '700px',
              }}
            >
              Automatizamos procesos, implantamos agentes IA y formamos a tus equipos. Resultados reales en 4–6 semanas.
            </div>
          </div>

          {/* Métricas en la parte inferior */}
          <div style={{ display: 'flex', gap: '40px' }}>
            {[
              { num: '+50', label: 'Empresas automatizadas' },
              { num: '+200', label: 'Automatizaciones activas' },
              { num: '340%', label: 'ROI medio primer año' },
              { num: '4–6sem', label: 'Tiempo hasta resultados' },
            ].map((stat) => (
              <div
                key={stat.num}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px',
                  borderLeft: '3px solid #2563EB',
                  paddingLeft: '16px',
                }}
              >
                <span style={{ color: 'white', fontSize: '28px', fontWeight: '800' }}>
                  {stat.num}
                </span>
                <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '14px' }}>
                  {stat.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Franja inferior */}
        <div
          style={{
            position: 'absolute',
            bottom: '0',
            left: '0',
            right: '0',
            height: '4px',
            background: 'linear-gradient(90deg, #2563EB, #60A5FA, #2563EB)',
            display: 'flex',
          }}
        />
      </div>
    ),
    { ...size }
  )
}
