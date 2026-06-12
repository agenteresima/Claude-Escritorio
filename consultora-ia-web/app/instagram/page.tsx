import Link from 'next/link'

export default function InstagramPage() {
  const slides = [1, 2, 3, 4, 5, 6, 7]
  return (
    <div style={{ background: '#060D1A', minHeight: '100vh', padding: '40px', fontFamily: 'Inter, sans-serif' }}>
      <h1 style={{ color: 'white', fontSize: '28px', marginBottom: '32px', fontWeight: '700' }}>
        Post 1 — Instagram Carrusel
      </h1>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {slides.map((n) => (
          <a
            key={n}
            href={`/instagram/slide/1/${n}`}
            target="_blank"
            style={{
              display: 'block',
              background: 'rgba(37,99,235,0.15)',
              border: '1px solid rgba(37,99,235,0.4)',
              borderRadius: '12px',
              padding: '20px 28px',
              color: '#93C5FD',
              fontSize: '18px',
              fontWeight: '600',
              textDecoration: 'none',
            }}
          >
            📸 Diapositiva {n} / 7 — Abrir →
          </a>
        ))}
      </div>
    </div>
  )
}
