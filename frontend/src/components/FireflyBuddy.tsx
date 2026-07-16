type Props = {
  zone: "housing" | "job";
  searching: boolean;
  label: string;
  onOpen: () => void;
};

/** Original firefly companion — pulses faster while searching; opens the guide. */
export function FireflyBuddy({ zone, searching, label, onOpen }: Props) {
  return (
    <button
      type="button"
      className={`firefly-buddy zone-${zone}${searching ? " searching" : ""}`}
      onClick={onOpen}
      aria-label={label}
    >
      <span className="firefly-glow" aria-hidden />
      <span className="firefly-body" aria-hidden>
        <svg viewBox="0 0 32 32" width="28" height="28" role="img">
          <ellipse cx="16" cy="18" rx="5" ry="7" fill="currentColor" opacity="0.92" />
          <circle cx="16" cy="10" r="4.5" fill="#f6e27a" />
          <path
            d="M10 14 Q4 10 6 6"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.4"
            opacity="0.55"
          />
          <path
            d="M22 14 Q28 10 26 6"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.4"
            opacity="0.55"
          />
        </svg>
      </span>
    </button>
  );
}
