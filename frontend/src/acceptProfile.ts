import type { AcceptGoal, AcceptProfile, Listing, ListingType } from "./api";
import type { Messages } from "./i18n";

export type AcceptReason = {
  kind: "yes" | "ask";
  text: string;
};

function fold(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

export function emptyAcceptProfile(): AcceptProfile {
  return {
    goal: null,
    live_in: "",
    work_in: "",
    permit: null,
    languages: "",
    budget_chf: null,
    cities: "",
    move_in: "",
    household: null,
  };
}

export function acceptProfileFilled(profile: AcceptProfile | null | undefined): boolean {
  if (!profile) return false;
  return Boolean(
    profile.goal ||
      profile.live_in?.trim() ||
      profile.work_in?.trim() ||
      profile.permit ||
      profile.languages?.trim() ||
      profile.budget_chf ||
      profile.cities?.trim() ||
      profile.move_in?.trim() ||
      profile.household,
  );
}

function placesOf(profile: AcceptProfile): string[] {
  const chunks = [
    profile.live_in ?? "",
    profile.work_in ?? "",
    ...(profile.cities ?? "").split(/[,;/]/),
  ];
  return chunks.map((item) => item.trim()).filter((item) => item.length >= 2);
}

function placeHit(listing: Listing, profile: AcceptProfile): string | null {
  const loc = fold(listing.location ?? "");
  if (!loc) return null;
  for (const city of placesOf(profile)) {
    const needle = fold(city);
    if (needle.length < 3) continue;
    if (loc.includes(needle) || needle.includes(loc)) return city;
  }
  return null;
}

function goalFits(listingType: ListingType, goal: AcceptGoal | null | undefined): boolean {
  if (!goal || goal === "both") return true;
  return goal === listingType;
}

/** Up to 5 honest reasons. Never a score. */
export function acceptReasons(
  listing: Listing,
  profile: AcceptProfile | null | undefined,
  t: Messages,
): AcceptReason[] {
  if (!acceptProfileFilled(profile) || !profile) return [];
  if (!goalFits(listing.listing_type, profile.goal ?? null)) return [];

  const out: AcceptReason[] = [];
  if (profile.goal === "housing" && listing.listing_type === "housing") {
    out.push({ kind: "yes", text: t.acceptWhyGoalHousing });
  }
  if (profile.goal === "job" && listing.listing_type === "job") {
    out.push({ kind: "yes", text: t.acceptWhyGoalJob });
  }
  if (profile.goal === "both") {
    out.push({
      kind: "yes",
      text: listing.listing_type === "job" ? t.acceptWhyGoalJob : t.acceptWhyGoalHousing,
    });
  }

  if (listing.listing_type === "housing" && profile.budget_chf && listing.price != null) {
    const price = Number(listing.price);
    if (Number.isFinite(price) && price <= profile.budget_chf) {
      out.push({
        kind: "yes",
        text: t.acceptWhyBudget
          .replace("{price}", String(Math.round(price)))
          .replace("{budget}", String(profile.budget_chf)),
      });
    }
  }

  const hit = placeHit(listing, profile);
  if (hit) {
    out.push({ kind: "yes", text: t.acceptWhyPlace.replace("{place}", hit) });
  }

  const live = (profile.live_in ?? "").trim();
  if (
    listing.listing_type === "job" &&
    listing.country === "CH" &&
    live &&
    /annemasse|gaillard|ferney|thonon|annecy|lorrach|weil|konstanz|como|varese|domodossola|france|italia|deutschland|allemagne/i.test(
      fold(live),
    )
  ) {
    out.push({ kind: "yes", text: t.acceptWhyFrontalier.replace("{place}", live) });
  }

  if (listing.listing_type === "job") {
    if (!profile.permit) {
      out.push({ kind: "ask", text: t.acceptWhyPermitAsk });
    } else if (profile.permit === "G" || profile.permit === "B" || profile.permit === "C" || profile.permit === "L") {
      out.push({
        kind: "yes",
        text: t.acceptWhyPermit.replace("{permit}", profile.permit),
      });
    } else if (profile.permit === "none") {
      out.push({ kind: "ask", text: t.acceptWhyPermitNone });
    }
  }

  return out.slice(0, 5);
}
