import { LANG_LABELS, LANGS, type Lang } from "../i18n";

type Props = {
  lang: Lang;
  onChange: (lang: Lang) => void;
};

export function LanguageBar({ lang, onChange }: Props) {
  return (
    <nav className="lang-bar" aria-label="Language">
      {LANGS.map((code) => (
        <button
          key={code}
          type="button"
          className={code === lang ? "active" : ""}
          onClick={() => onChange(code)}
        >
          {LANG_LABELS[code]}
        </button>
      ))}
    </nav>
  );
}
