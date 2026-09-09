import { useEffect, useState } from "react";
import { poseSrc, ALL_POSES, type SentinelPose } from "../sentinelPose";

const POSE_HOLD_MS = 60 * 1000;

if (typeof window !== "undefined") {
  for (const pose of ALL_POSES) {
    const preload = new Image();
    preload.src = poseSrc(pose);
  }
}

export type HintChoice = {
  id: string;
  label: string;
  quiet?: boolean;
};

type Props = {
  zone: "housing" | "job";
  pose?: SentinelPose;
  searching: boolean;
  talking?: boolean;
  sheetOpen?: boolean;
  dock?: "left" | "right";
  label: string;
  hint?: string;
  name?: string;
  hintChoices?: HintChoice[];
  onHintChoice?: (id: string) => void;
  onOpen: () => void;
  /** Bump after "no thanks" so she leans on the wall again, then thinks. */
  restKey?: number;
};

const FACE_SRC = "/hub/sentinel-buddy.png?v=3";

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
export function SentinelFace({
  size = 40,
  zone,
}: {
  size?: number;
  zone?: "housing" | "job";
}) {
  return (
    <img
      className={`sentinel-face${zone ? ` zone-${zone}` : ""}`}
      src={FACE_SRC}
      alt=""
      width={size}
      height={size}
      draggable={false}
    />
  );
}

/** Still figure. Parent pose is the reaction; idle leans on the wall, then thinks after 1 min. */
export function SentinelBuddy({
  zone,
  pose = "idle",
  searching,
  talking = false,
  sheetOpen = false,
  dock = "right",
  label,
  hint,
  name = "Sentinela",
  hintChoices,
  onHintChoice,
  onOpen,
  restKey = 0,
}: Props) {
  const choices = hintChoices?.length && onHintChoice ? hintChoices : null;
  const [idleBeat, setIdleBeat] = useState<SentinelPose>("sit");

  useEffect(() => {
    if (pose !== "idle" || sheetOpen) {
      return;
    }
    setIdleBeat("sit");
    const timer = window.setTimeout(() => setIdleBeat("think"), POSE_HOLD_MS);
    return () => window.clearTimeout(timer);
  }, [pose, sheetOpen, restKey]);

  const displayPose = pose !== "idle" ? pose : idleBeat;

  return (
    <button
      type="button"
      className={`sentinel-buddy zone-${zone} pose-${displayPose} dock-${dock}${searching ? " searching" : ""}${talking || hint ? " talking" : ""}${sheetOpen ? " is-hidden" : ""}`}
      aria-hidden={sheetOpen}
      onClick={(event) => {
        if ((event.target as HTMLElement).closest(".sentinel-hint-actions")) return;
        onOpen();
      }}
      aria-label={label}
    >
      {hint ? (
        <span className={`sentinel-hint${choices ? " has-choices" : ""}`}>
          <NamedCopy text={hint} name={name} />
          {choices ? (
            <span className="sentinel-hint-actions">
              {choices.map((choice) => (
                <span
                  key={choice.id}
                  className={`sentinel-hint-choice${choice.quiet ? " is-quiet" : ""}`}
                  role="button"
                  tabIndex={0}
                  onClick={(event) => {
                    event.stopPropagation();
                    onHintChoice?.(choice.id);
                  }}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      event.stopPropagation();
                      onHintChoice?.(choice.id);
                    }
                  }}
                >
                  {choice.label}
                </span>
              ))}
            </span>
          ) : null}
        </span>
      ) : null}
      <img
        className={`sentinel-figure${live ? " is-live" : ""}`}
        src={poseSrc(displayPose)}
        alt=""
        draggable={false}
      />
    </button>
  );
}
