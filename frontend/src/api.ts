export type ListingType = "housing" | "job";

export type Listing = {
  id: number;
  title: string;
  location: string | null;
  price: number | null;
  listing_type: ListingType;
  source_url: string;
  description?: string | null;
};

export async function searchListings(params: {
  listing_type: ListingType;
  location?: string;
}): Promise<Listing[]> {
  const query = new URLSearchParams();
  query.set("listing_type", params.listing_type);
  if (params.location?.trim()) {
    query.set("location", params.location.trim());
  }
  const response = await fetch(`/api/v1/public/search?${query}`);
  if (!response.ok) {
    throw new Error("search failed");
  }
  return response.json();
}

export async function fetchPrivacy(lang: string): Promise<string> {
  const response = await fetch(`/api/v1/legal/privacy?lang=${lang}`);
  if (!response.ok) return "";
  const data = await response.json();
  return data.content as string;
}

export type SignupResponse = {
  api_key: string;
  user_id: number;
  saved_search_id: number;
  email_verified: boolean;
  whatsapp_verified: boolean;
  verification_pending: boolean;
};

const API_KEY_STORAGE = "suisse-alert-api-key";

export function saveApiKey(key: string): void {
  localStorage.setItem(API_KEY_STORAGE, key);
}

export async function subscribeAlerts(params: {
  email: string;
  phone?: string;
  locale: string;
  listing_type: ListingType;
  location?: string;
}): Promise<SignupResponse> {
  const response = await fetch("/api/v1/public/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: params.email,
      phone: params.phone?.trim() || undefined,
      locale: params.locale,
      consent: true,
      query: {
        listing_type: params.listing_type,
        location: params.location?.trim() || undefined,
      },
    }),
  });
  if (!response.ok) {
    let message = "signup failed";
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(message);
  }
  const data: SignupResponse = await response.json();
  saveApiKey(data.api_key);
  return data;
}
