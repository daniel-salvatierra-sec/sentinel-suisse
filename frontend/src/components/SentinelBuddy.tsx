import { useEffect, useState } from "react";
import { poseSrc, type SentinelPose } from "../sentinelPose";

const POSES: SentinelPose[] = ["idle", "account", "search", "think"];
const POINT_HOLD_MS = 5000;

if (typeof window !== "undefined") {
  for (const pose of POSES) {
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

/** Full-body cutout: a gesture lasts 5s, then she stands at ease. */
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
}: Props) {
  const live = searching || talking || Boolean(hint);
  const choices = hintChoices?.length && onHintChoice ? hintChoices : null;
  const [shownPose, setShownPose] = useState<SentinelPose>(pose);

  useEffect(() => {
    setShownPose(pose);
    if (pose === "idle") return;
    const timer = window.setTimeout(() => setShownPose("idle"), POINT_HOLD_MS);
    return () => window.clearTimeout(timer);
  }, [pose]);

  return (
    <button
      type="button"
      className={`sentinel-buddy zone-${zone} pose-${shownPose} dock-${dock}${searching ? " searching" : ""}${talking || hint ? " talking" : ""}${sheetOpen ? " is-hidden" : ""}`}
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
        src={poseSrc(shownPose)}
        alt=""
        draggable={false}
      />
    </button>
  );
}
