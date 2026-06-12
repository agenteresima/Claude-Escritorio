export default function LogoIcon({ className = '', size = 36 }: { className?: string; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="lg1" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#3B82F6" />
          <stop offset="100%" stopColor="#A855F7" />
        </linearGradient>
        <linearGradient id="lg2" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#60A5FA" />
          <stop offset="100%" stopColor="#C084FC" />
        </linearGradient>
      </defs>

      {/* Símbolo infinito */}
      <path
        d="M42 60 C42 46 52 36 62 36 C72 36 80 44 90 52 C80 60 72 68 62 68 C52 68 42 74 42 60 Z"
        stroke="url(#lg1)"
        strokeWidth="7"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M78 60 C78 46 88 36 98 36"
        stroke="url(#lg1)"
        strokeWidth="7"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M78 60 C78 74 88 84 98 84 C108 84 118 74 118 60 C118 46 108 36 98 36"
        stroke="url(#lg1)"
        strokeWidth="7"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M42 60 C42 74 32 84 22 84 C12 84 2 74 2 60 C2 46 12 36 22 36 C32 36 42 46 42 60 Z"
        stroke="url(#lg1)"
        strokeWidth="7"
        fill="none"
        strokeLinecap="round"
      />

      {/* Nodo izquierdo */}
      <circle cx="22" cy="60" r="4" fill="url(#lg2)" />
      <line x1="26" y1="56" x2="38" y2="50" stroke="url(#lg2)" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="26" y1="60" x2="40" y2="60" stroke="url(#lg2)" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="26" y1="64" x2="38" y2="70" stroke="url(#lg2)" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="40" cy="50" r="2.5" fill="#60A5FA" />
      <circle cx="42" cy="60" r="2.5" fill="#60A5FA" />
      <circle cx="40" cy="70" r="2.5" fill="#60A5FA" />

      {/* Nodo derecho */}
      <circle cx="98" cy="60" r="4" fill="url(#lg2)" />
      <line x1="94" y1="56" x2="82" y2="50" stroke="url(#lg2)" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="94" y1="60" x2="80" y2="60" stroke="url(#lg2)" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="94" y1="64" x2="82" y2="70" stroke="url(#lg2)" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="80" cy="50" r="2.5" fill="#C084FC" />
      <circle cx="78" cy="60" r="2.5" fill="#C084FC" />
      <circle cx="80" cy="70" r="2.5" fill="#C084FC" />
    </svg>
  )
}
