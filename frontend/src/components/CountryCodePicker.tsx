import { useMemo, useState } from "react";
import { COUNTRY_DIALS, defaultCountry, filterCountries } from "../countryCodes";
import type { Lang, Messages } from "../i18n";

type Props = {
  lang: Lang;
  t: Messages;
  dial: string;
  local: string;
  onDialChange: (dial: string) => void;
  onLocalChange: (local: string) => void;
};

export function CountryCodePicker({ lang, t, dial, local, onDialChange, onLocalChange }: Props) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");

  const selected = COUNTRY_DIALS.find((c) => c.dial === dial) ?? defaultCountry();
  const filtered = useMemo(() => filterCountries(search, lang), [search, lang]);

  return (
    <div className="phone-field">
      <label>{t.phone}</label>
      <div className="phone-row">
        <div className="country-picker">
          <button
            type="button"
            className="country-trigger"
            onClick={() => setOpen((value) => !value)}
            aria-expanded={open}
          >
            {selected.iso} {selected.dial}
          </button>
          {open && (
            <div className="country-dropdown">
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder={t.countryCodeSearch}
                autoFocus
              />
              <ul>
                {filtered.map((country) => (
                  <li key={country.iso}>
                    <button
                      type="button"
                      onClick={() => {
                        onDialChange(country.dial);
                        setOpen(false);
                        setSearch("");
                      }}
                    >
                      <span className="country-name">{country.names[lang]}</span>
                      <span className="country-dial">{country.dial}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <input
          type="tel"
          className="phone-local"
          value={local}
          onChange={(event) => onLocalChange(event.target.value)}
          placeholder="79 123 45 67"
          inputMode="tel"
        />
      </div>
    </div>
  );
}
