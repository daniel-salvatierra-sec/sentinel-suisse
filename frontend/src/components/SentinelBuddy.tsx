import { useEffect, useState } from "react";
import { poseSrc, type SentinelPose } from "../sentinelPose";

const POSES: SentinelPose[] = ["idle", "account", "search", "think"];
const POINTING: SentinelPose[] = ["account", "search"];
const POINT_HOLD_MS = 5000;

if (typeof window !== "undefined") {
  for (const pose of POSES) {
    const preload = new Image();
    preload.src = poseSrc(pose);
  }
}

type Props = {
  zone: "housing" | "job";
  pose?: SentinelPose;
  searching: boolean;
  talking?: boolean;
  label: string;
  hint?: string;
  name?: string;
  hintYes?: string;
  hintNo?: string;
  onHintYes?: () => void;
  onHintNo?: () => void;
  onOpen: () => void;
};

const FACE_SRC = "/hub/sentinel-buddy.png?v=2";

function NamedCopy({ text, name }: { text: string; name: string }) {
  const parts = text.split("{name}");
  if (parts.length === 1) return <>{text}</>;
  return (
    <>
      {parts[0]}
      <strong className="sentinel-name">{name}</strong>
      {parts.slice(1).join(name)}
    </>
  );
}

export { NamedCopy };

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

/** Full-body cutout: feet planted, pose swaps head/arms/gaze. */
export function SentinelBuddy({
  zone,
  pose = "idle",
  searching,
  talking = false,
  label,
  hint,
  name = "Sentinela",
  hintYes,
  hintNo,
  onHintYes,
  onHintNo,
  onOpen,
}: Props) {
  const live = searching || talking;
  const hasChoices = Boolean(hintYes && hintNo && onHintYes && onHintNo);
  const [shownPose, setShownPose] = useState<SentinelPose>(pose);

  useEffect(() => {
    setShownPose(pose);
    if (!POINTING.includes(pose)) return;
    const timer = window.setTimeout(() => setShownPose("idle"), POINT_HOLD_MS);
    return () => window.clearTimeout(timer);
  }, [pose]);

  return (
    <button
      type="button"
      className={`sentinel-buddy zone-${zone} pose-${shownPose}${searching ? " searching" : ""}${talking ? " talking" : ""}`}
      onClick={(event) => {
        if ((event.target as HTMLElement).closest(".sentinel-hint-actions")) return;
        onOpen();
      }}
      aria-label={label}
    >
      {hint ? (
        <span className="sentinel-hint">
          <NamedCopy text={hint} name={name} />
          {hasChoices ? (
            <span className="sentinel-hint-actions">
              <span
                className="sentinel-hint-choice"
                role="button"
                tabIndex={0}
                onClick={(event) => {
                  event.stopPropagation();
                  onHintYes?.();
                }}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    event.stopPropagation();
                    onHintYes?.();
                  }
                }}
              >
                {hintYes}
              </span>
              <span
                className="sentinel-hint-choice is-quiet"
                role="button"
                tabIndex={0}
                onClick={(event) => {
                  event.stopPropagation();
                  onHintNo?.();
                }}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    event.stopPropagation();
                    onHintNo?.();
                  }
                }}
              >
                {hintNo}
              </span>
            </span>
          ) : null}
        </span>
      ) : null}
      <img
        className={`sentinel-figure${live ? " is-live" : ""}`}
        src={poseSrc(shownPose)}
        alt=""
        draggable={false}
      />
    </button>
  );
}
