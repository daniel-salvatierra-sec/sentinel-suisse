export type ListingType = "housing" | "job";

export type Listing = {
  id: number;
  title: string;
  location: string | null;
  price: number | null;
  listing_type: ListingType;
  source_url: string;
  description?: string | null;
  provider_id?: number;
};

export type Provider = {
  id: number;
  name: string;
  slug: string;
  base_url: string;
  is_active: boolean;
};

export async function fetchProviders(): Promise<Provider[]> {
  const response = await fetch("/api/v1/public/providers");
  if (!response.ok) {
    throw new Error("providers failed");
  }
  return response.json();
}

export async function searchListings(params: {
  listing_type: ListingType;
  location?: string;
  price_min?: number;
  price_max?: number;
  provider_id?: number;
  limit?: number;
  offset?: number;
}): Promise<Listing[]> {
  const query = new URLSearchParams();
  query.set("listing_type", params.listing_type);
  if (params.location?.trim()) {
    query.set("location", params.location.trim());
  }
  if (params.price_min != null && !Number.isNaN(params.price_min)) {
    query.set("price_min", String(params.price_min));
  }
  if (params.price_max != null && !Number.isNaN(params.price_max)) {
    query.set("price_max", String(params.price_max));
  }
  if (params.provider_id != null) {
    query.set("provider_id", String(params.provider_id));
  }
  query.set("limit", String(params.limit ?? 20));
  query.set("offset", String(params.offset ?? 0));
  const response = await fetch(`/api/v1/public/search?${query}`);
  if (!response.ok) {
    throw new Error("search failed");
  }
  return response.json();
}

export const SEARCH_PAGE_SIZE = 20;

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
  verification_email_sent?: boolean;
  whatsapp_verification_sent?: boolean;
};

const API_KEY_STORAGE = "suisse-alert-api-key";

export function getApiKey(): string | null {
  return localStorage.getItem(API_KEY_STORAGE);
}

export function saveApiKey(key: string): void {
  localStorage.setItem(API_KEY_STORAGE, key);
}

export function clearApiKey(): void {
  localStorage.removeItem(API_KEY_STORAGE);
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error("not authenticated");
  }
  const response = await fetch(path, {
    ...init,
    headers: {
      ...(init.headers ?? {}),
      "X-API-Key": apiKey,
    },
  });
  if (!response.ok) {
    throw new Error(`request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export type UserProfile = {
  id: number;
  email: string;
  locale: string;
  is_active: boolean;
  created_at: string;
};

export type SavedSearch = {
  id: number;
  user_id: number;
  name: string;
  query: {
    listing_type?: ListingType;
    location?: string;
  };
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type AlertLog = {
  id: number;
  user_id: number;
  saved_search_id: number;
  listing_id: number;
  channel_type: string;
  status: string;
  error_message: string | null;
  sent_at: string | null;
  created_at: string;
};

export function fetchMe(): Promise<UserProfile> {
  return apiFetch<UserProfile>("/api/v1/users/me");
}

export function fetchSavedSearches(): Promise<SavedSearch[]> {
  return apiFetch<SavedSearch[]>("/api/v1/saved-searches");
}

export function deleteSavedSearch(id: number): Promise<void> {
  return apiFetch<void>(`/api/v1/saved-searches/${id}`, { method: "DELETE" });
}

export function fetchAlerts(): Promise<AlertLog[]> {
  return apiFetch<AlertLog[]>("/api/v1/alerts?limit=20");
}

export function deleteAccount(): Promise<void> {
  return apiFetch<void>("/api/v1/users/me", { method: "DELETE" });
}

export async function verifyChannelToken(
  token: string,
): Promise<{ channel_type: string }> {
  const response = await fetch(
    `/api/v1/public/verify-channel?token=${encodeURIComponent(token)}`,
  );
  if (!response.ok) {
    throw new Error("verify failed");
  }
  return response.json() as Promise<{ channel_type: string }>;
}

/** @deprecated use verifyChannelToken */
export async function verifyEmailToken(token: string): Promise<void> {
  await verifyChannelToken(token);
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
