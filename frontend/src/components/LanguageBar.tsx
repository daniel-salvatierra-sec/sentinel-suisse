import { useEffect, useRef, useState } from "react";
import { LANG_LABELS, LANGS, type Lang } from "../i18n";

type Props = {
  lang: Lang;
  onChange: (lang: Lang) => void;
  label: string;
};

export function LanguageBar({ lang, onChange, label }: Props) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node | null;
      if (target && rootRef.current?.contains(target)) return;
      setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  return (
    <div className={`lang-bar${open ? " is-open" : ""}`} ref={rootRef}>
      <button
        type="button"
        className="lang-bar-toggle"
        aria-label={label}
        aria-expanded={open}
        aria-haspopup="listbox"
        onClick={() => setOpen((current) => !current)}
      >
        <span className="lang-bar-globe" aria-hidden>
          <svg viewBox="0 0 24 24" width="18" height="18">
            <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.7" />
            <path
              d="M3 12h18M12 3c2.5 3 3.8 6 3.8 9s-1.3 6-3.8 9c-2.5-3-3.8-6-3.8-9s1.3-6 3.8-9z"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            />
          </svg>
        </span>
        <span className="lang-bar-current">{LANG_LABELS[lang]}</span>
      </button>
      {open ? (
        <div className="lang-bar-menu" role="listbox" aria-label={label}>
          {LANGS.map((code) => (
            <button
              key={code}
              type="button"
              role="option"
              aria-selected={code === lang}
              className={code === lang ? "active" : ""}
              onClick={() => {
                onChange(code);
                setOpen(false);
              }}
            >
              {LANG_LABELS[code]}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
