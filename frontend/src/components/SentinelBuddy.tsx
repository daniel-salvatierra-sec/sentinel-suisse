type Props = {
  zone: "housing" | "job";
  searching: boolean;
  label: string;
  onOpen: () => void;
};

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
        <svg viewBox="0 0 40 40" width="34" height="34" role="img">
          <rect x="8" y="10" width="24" height="22" rx="4" fill="#12141a" />
          <rect x="11" y="14" width="18" height="10" rx="2" fill="#1c2028" />
          <circle cx="20" cy="19" r="3.2" fill="#c45c4a" />
          <circle cx="20" cy="19" r="1.4" fill="#f2d6d0" opacity="0.9" />
          <rect x="14" y="26" width="12" height="2" rx="1" fill="#2a303c" />
          <path d="M12 10 L14 6 H26 L28 10" fill="#0e1016" />
        </svg>
      </span>
    </button>
  );
}
