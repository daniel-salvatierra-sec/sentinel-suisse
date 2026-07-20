type Props = {
  zone: "housing" | "job";
  searching: boolean;
  label: string;
  onOpen: () => void;
};

const FACE_SRC = "/hub/sentinel-buddy.png";

/** Photoreal companion face — reused in dock + sheet. */
export function SentinelFace({ size = 40 }: { size?: number }) {
  return (
    <img
      className="sentinel-face"
      src={FACE_SRC}
      alt=""
      width={size}
      height={size}
      draggable={false}
    />
  );
}

/** Matte-black Avatar-style companion — dock FAB that opens the guide sheet. */
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
        <SentinelFace size={44} />
      </span>
    </button>
  );
}
