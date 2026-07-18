import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
};

export function SearchBar({ t, value, onChange, onSearch }: Props) {
  return (
    <form
      id="search-panel"
      className="search-box"
      onSubmit={(event) => {
        event.preventDefault();
        onSearch();
      }}
    >
      <input
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={t.searchPlaceholder}
        aria-label={t.searchPlaceholder}
      />
      <button type="submit">{t.search}</button>
    </form>
  );
}
