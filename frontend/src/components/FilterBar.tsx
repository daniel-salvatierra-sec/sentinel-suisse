import type { Messages } from "../i18n";
import type { Provider } from "../api";

type Props = {
  t: Messages;
  showPrice: boolean;
  providers: Provider[];
  providerId: number | null;
  onProviderChange: (id: number | null) => void;
  priceMin: string;
  priceMax: string;
  onPriceMinChange: (value: string) => void;
  onPriceMaxChange: (value: string) => void;
  onApply: () => void;
};

export function FilterBar({
  t,
  showPrice,
  providers,
  providerId,
  onProviderChange,
  priceMin,
  priceMax,
  onPriceMinChange,
  onPriceMaxChange,
  onApply,
}: Props) {
  return (
    <div className="filter-bar">
      <p className="filter-bar-label">{t.filters}</p>
      {providers.length > 0 && (
        <div className="provider-chips" role="group" aria-label={t.providerFilter}>
          <button
            type="button"
            className={providerId == null ? "chip active" : "chip"}
            onClick={() => onProviderChange(null)}
          >
            {t.allProviders}
          </button>
          {providers.map((provider) => (
            <button
              key={provider.id}
              type="button"
              className={providerId === provider.id ? "chip active" : "chip"}
              onClick={() => onProviderChange(provider.id)}
            >
              {provider.name}
            </button>
          ))}
        </div>
      )}
      {showPrice && (
        <form
          className="filter-row"
          onSubmit={(event) => {
            event.preventDefault();
            onApply();
          }}
        >
          <label>
            {t.priceMin}
            <input
              type="number"
              min={0}
              inputMode="numeric"
              value={priceMin}
              onChange={(event) => onPriceMinChange(event.target.value)}
              placeholder="0"
            />
          </label>
          <label>
            {t.priceMax}
            <input
              type="number"
              min={0}
              inputMode="numeric"
              value={priceMax}
              onChange={(event) => onPriceMaxChange(event.target.value)}
              placeholder="5000"
            />
          </label>
          <button type="submit" className="secondary-btn">
            {t.applyFilters}
          </button>
        </form>
      )}
    </div>
  );
}
