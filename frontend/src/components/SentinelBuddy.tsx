type Props = {
  zone: "housing" | "job";
  searching: boolean;
  talking?: boolean;
  hidden?: boolean;
  label: string;
  hint?: string;
  onOpen: () => void;
};

const FACE_SRC = "/hub/sentinel-buddy.png?v=2";
const FIGURE_SRC = "/hub/sentinel-figure.png?v=2";

/** Photoreal companion face — reused in sheet + alerts. */
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

/** Full-body cutout over the search page — not a circular button. */
export function SentinelBuddy({
  zone,
  searching,
  talking = false,
  hidden = false,
  label,
  hint,
  onOpen,
}: Props) {
  const live = searching || talking;
  return (
    <button
      type="button"
      className={`sentinel-buddy zone-${zone}${searching ? " searching" : ""}${talking ? " talking" : ""}${hidden ? " is-hidden" : ""}`}
      onClick={onOpen}
      aria-label={label}
    >
      {hint ? <span className="sentinel-hint">{hint}</span> : null}
      <img
        className={`sentinel-figure${live ? " is-live" : ""}`}
        src={FIGURE_SRC}
        alt=""
        draggable={false}
      />
    </button>
  );
}
