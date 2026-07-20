import { useId } from "react";

type Props = {
  zone: "housing" | "job";
  searching: boolean;
  label: string;
  onOpen: () => void;
};

/** Friendly matte-black face with soft blue eyes — reused in dock + sheet. */
export function SentinelFace({ size = 34 }: { size?: number }) {
  const uid = useId().replace(/:/g, "");
  const eyeId = `sentinel-eye-${uid}`;
  const glowId = `sentinel-glow-${uid}`;

  return (
    <svg viewBox="0 0 40 40" width={size} height={size} role="img" aria-hidden>
      <defs>
        <radialGradient id={eyeId} cx="35%" cy="30%" r="70%">
          <stop offset="0%" stopColor="#d9f4ff" />
          <stop offset="45%" stopColor="#5ec8f0" />
          <stop offset="100%" stopColor="#1a8fc4" />
        </radialGradient>
        <filter id={glowId} x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="0.8" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <ellipse cx="20" cy="34" rx="11" ry="4.5" fill="#0e1016" />
      <circle cx="20" cy="18" r="13" fill="#14161c" />
      <circle cx="20" cy="18" r="13" fill="none" stroke="#2a2e38" strokeWidth="0.8" />
      <ellipse cx="14" cy="21" rx="3.2" ry="2.2" fill="#1c2028" opacity="0.7" />
      <ellipse cx="26" cy="21" rx="3.2" ry="2.2" fill="#1c2028" opacity="0.7" />
      <g filter={`url(#${glowId})`}>
        <ellipse cx="14.5" cy="16.5" rx="3.1" ry="3.4" fill={`url(#${eyeId})`} />
        <ellipse cx="25.5" cy="16.5" rx="3.1" ry="3.4" fill={`url(#${eyeId})`} />
        <circle cx="13.4" cy="15.4" r="0.9" fill="#f0fbff" opacity="0.95" />
        <circle cx="24.4" cy="15.4" r="0.9" fill="#f0fbff" opacity="0.95" />
      </g>
      <path
        d="M14.5 23.5 Q20 27.5 25.5 23.5"
        fill="none"
        stroke="#3a4250"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <line x1="20" y1="5" x2="20" y2="2.5" stroke="#2a2e38" strokeWidth="1.2" strokeLinecap="round" />
      <circle cx="20" cy="2" r="1.3" fill="#5ec8f0" opacity="0.85" />
    </svg>
  );
}

/** Matte-black sentinel companion — dock FAB that opens the guide sheet. */
export function SentinelBuddy({ zone, searching, label, onOpen }: Props) {
  return (
    <button
      type="button"
      className={`sentinel-buddy zone-${zone}${searching ? " searching" : ""}`}
      onClick={onOpen}
      aria-label={label}
    >
      <span className="sentinel-ring" aria-hidden />
      <span className="sentinel-body" aria-hidden>
        <SentinelFace size={34} />
      </span>
    </button>
  );
}
