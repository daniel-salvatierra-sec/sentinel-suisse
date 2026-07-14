import type { Lang } from "./i18n";

export type CountryDial = {
  dial: string;
  iso: string;
  names: Record<Lang, string>;
};

/** Common countries for Geneva — searchable by localized name. */
export const COUNTRY_DIALS: CountryDial[] = [
  { dial: "+41", iso: "CH", names: { fr: "Suisse", de: "Schweiz", es: "Suiza", pt: "Suíça", en: "Switzerland" } },
  { dial: "+33", iso: "FR", names: { fr: "France", de: "Frankreich", es: "Francia", pt: "França", en: "France" } },
  { dial: "+49", iso: "DE", names: { fr: "Allemagne", de: "Deutschland", es: "Alemania", pt: "Alemanha", en: "Germany" } },
  { dial: "+39", iso: "IT", names: { fr: "Italie", de: "Italien", es: "Italia", pt: "Itália", en: "Italy" } },
  { dial: "+34", iso: "ES", names: { fr: "Espagne", de: "Spanien", es: "España", pt: "Espanha", en: "Spain" } },
  { dial: "+351", iso: "PT", names: { fr: "Portugal", de: "Portugal", es: "Portugal", pt: "Portugal", en: "Portugal" } },
  { dial: "+44", iso: "GB", names: { fr: "Royaume-Uni", de: "Vereinigtes Königreich", es: "Reino Unido", pt: "Reino Unido", en: "United Kingdom" } },
  { dial: "+1", iso: "US", names: { fr: "États-Unis", de: "USA", es: "Estados Unidos", pt: "Estados Unidos", en: "United States" } },
  { dial: "+55", iso: "BR", names: { fr: "Brésil", de: "Brasilien", es: "Brasil", pt: "Brasil", en: "Brazil" } },
  { dial: "+90", iso: "TR", names: { fr: "Turquie", de: "Türkei", es: "Turquía", pt: "Turquia", en: "Turkey" } },
  { dial: "+40", iso: "RO", names: { fr: "Roumanie", de: "Rumänien", es: "Rumanía", pt: "Roménia", en: "Romania" } },
  { dial: "+48", iso: "PL", names: { fr: "Pologne", de: "Polen", es: "Polonia", pt: "Polónia", en: "Poland" } },
  { dial: "+381", iso: "RS", names: { fr: "Serbie", de: "Serbien", es: "Serbia", pt: "Sérvia", en: "Serbia" } },
  { dial: "+383", iso: "XK", names: { fr: "Kosovo", de: "Kosovo", es: "Kosovo", pt: "Kosovo", en: "Kosovo" } },
  { dial: "+212", iso: "MA", names: { fr: "Maroc", de: "Marokko", es: "Marruecos", pt: "Marrocos", en: "Morocco" } },
  { dial: "+213", iso: "DZ", names: { fr: "Algérie", de: "Algerien", es: "Argelia", pt: "Argélia", en: "Algeria" } },
  { dial: "+216", iso: "TN", names: { fr: "Tunisie", de: "Tunesien", es: "Túnez", pt: "Tunísia", en: "Tunisia" } },
  { dial: "+243", iso: "CD", names: { fr: "RD Congo", de: "DR Kongo", es: "RD Congo", pt: "RD Congo", en: "DR Congo" } },
  { dial: "+237", iso: "CM", names: { fr: "Cameroun", de: "Kamerun", es: "Camerún", pt: "Camarões", en: "Cameroon" } },
  { dial: "+91", iso: "IN", names: { fr: "Inde", de: "Indien", es: "India", pt: "Índia", en: "India" } },
  { dial: "+86", iso: "CN", names: { fr: "Chine", de: "China", es: "China", pt: "China", en: "China" } },
  { dial: "+7", iso: "RU", names: { fr: "Russie", de: "Russland", es: "Rusia", pt: "Rússia", en: "Russia" } },
  { dial: "+380", iso: "UA", names: { fr: "Ukraine", de: "Ukraine", es: "Ucrania", pt: "Ucrânia", en: "Ukraine" } },
  { dial: "+43", iso: "AT", names: { fr: "Autriche", de: "Österreich", es: "Austria", pt: "Áustria", en: "Austria" } },
  { dial: "+32", iso: "BE", names: { fr: "Belgique", de: "Belgien", es: "Bélgica", pt: "Bélgica", en: "Belgium" } },
  { dial: "+31", iso: "NL", names: { fr: "Pays-Bas", de: "Niederlande", es: "Países Bajos", pt: "Países Baixos", en: "Netherlands" } },
  { dial: "+352", iso: "LU", names: { fr: "Luxembourg", de: "Luxemburg", es: "Luxemburgo", pt: "Luxemburgo", en: "Luxembourg" } },
];

export function filterCountries(query: string, _lang: Lang): CountryDial[] {
  const q = query.trim().toLowerCase();
  if (!q) return COUNTRY_DIALS;
  return COUNTRY_DIALS.filter((country) => {
    const names = Object.values(country.names).join(" ").toLowerCase();
    return (
      names.includes(q) ||
      country.dial.includes(q) ||
      country.iso.toLowerCase().includes(q)
    );
  });
}

export function defaultCountry(): CountryDial {
  return COUNTRY_DIALS[0];
}

export function formatFullPhone(dial: string, local: string): string {
  const digits = local.replace(/\D/g, "");
  if (!digits) return "";
  return `${dial}${digits}`;
}
