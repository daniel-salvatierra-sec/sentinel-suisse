import type { Messages } from "../i18n";
import type { Provider } from "../api";

type Props = {
  t: Messages;
  showPrice: boolean;
  providers: Provider[];
  providerIds: number[];
  onProviderIdsChange: (ids: number[]) => void;
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
  providerIds,
  onProviderIdsChange,
  priceMin,
  priceMax,
  onPriceMinChange,
  onPriceMaxChange,
  onApply,
}: Props) {
  const noneSelected = providerIds.length === 0;

  const toggleProvider = (id: number) => {
    if (providerIds.includes(id)) {
      onProviderIdsChange(providerIds.filter((pid) => pid !== id));
    } else {
      onProviderIdsChange([...providerIds, id]);
    }
  };

  return (
    <div className="filter-bar">
      <p className="filter-bar-label">{t.filters}</p>
      {providers.length > 0 && (
        <div className="provider-chips" role="group" aria-label={t.providerFilter}>
          <button
            type="button"
            className={noneSelected ? "chip active" : "chip"}
            aria-pressed={noneSelected}
            onClick={() => onProviderIdsChange([])}
          >
            {t.allProviders}
          </button>
          {providers.map((provider) => {
            const active = providerIds.includes(provider.id);
            return (
              <button
                key={provider.id}
                type="button"
                className={active ? "chip active" : "chip"}
                aria-pressed={active}
                onClick={() => toggleProvider(provider.id)}
              >
                {provider.name}
              </button>
            );
          })}
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
