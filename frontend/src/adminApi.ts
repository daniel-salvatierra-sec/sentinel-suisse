const AUTH_KEY = "linkswiss.admin.basic";

export type ProviderIngestHealth = {
  slug: string;
  name: string;
  is_active: boolean;
  listing_count: number;
  last_fetched_at: string | null;
  hours_since_fetch: number | null;
  stale: boolean;
};

export type DashboardOverview = {
  users_total: number;
  users_active: number;
  users_premium: number;
  listings_housing: number;
  listings_job: number;
  listings_direct: number;
  listings_hidden: number;
  listing_fresh_hours: number;
  database_ok: boolean;
  providers: ProviderIngestHealth[];
};

export type AdminListing = {
  id: number;
  title: string;
  listing_type: "housing" | "job";
  location: string | null;
  source_url: string;
  fetched_at: string;
  is_hidden: boolean;
  owner_user_id: number | null;
  provider_slug: string;
};

export type AdminUser = {
  id: number;
  email: string;
  locale: string;
  is_active: boolean;
  is_premium: boolean;
  created_at: string;
  saved_search_count: number;
};

function token(): string | null {
  return sessionStorage.getItem(AUTH_KEY);
}

export function hasAdminSession(): boolean {
  return Boolean(token());
}

export function saveAdminSession(username: string, password: string): void {
  sessionStorage.setItem(AUTH_KEY, btoa(`${username}:${password}`));
}

export function clearAdminSession(): void {
  sessionStorage.removeItem(AUTH_KEY);
}

async function adminFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const basic = token();
  if (!basic) {
    throw new Error("unauthenticated");
  }
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Basic ${basic}`);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(path, { ...init, headers });
  if (response.status === 401) {
    clearAdminSession();
  }
  return response;
}

export async function fetchOverview(): Promise<DashboardOverview> {
  const response = await adminFetch("/api/v1/admin/overview");
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<DashboardOverview>;
}

export async function fetchAdminListings(params: {
  q?: string;
  listing_type?: "housing" | "job" | "";
  hidden?: boolean;
  owner_only?: boolean;
}): Promise<AdminListing[]> {
  const query = new URLSearchParams();
  if (params.q?.trim()) {
    query.set("q", params.q.trim());
  }
  if (params.listing_type) {
    query.set("listing_type", params.listing_type);
  }
  if (params.hidden === true) {
    query.set("hidden", "true");
  }
  if (params.owner_only) {
    query.set("owner_only", "true");
  }
  query.set("limit", "50");
  const response = await adminFetch(`/api/v1/admin/listings?${query.toString()}`);
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<AdminListing[]>;
}

export async function setListingHidden(id: number, isHidden: boolean): Promise<AdminListing> {
  const response = await adminFetch(`/api/v1/admin/listings/${id}/visibility`, {
    method: "PATCH",
    body: JSON.stringify({ is_hidden: isHidden }),
  });
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<AdminListing>;
}

export async function fetchAdminUsers(): Promise<AdminUser[]> {
  const response = await adminFetch("/api/v1/admin/users?limit=50");
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<AdminUser[]>;
}

export async function setUserPremium(id: number, isPremium: boolean): Promise<AdminUser> {
  const response = await adminFetch(`/api/v1/admin/users/${id}/premium`, {
    method: "PATCH",
    body: JSON.stringify({ is_premium: isPremium }),
  });
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<AdminUser>;
}

export async function eraseAdminUser(id: number): Promise<void> {
  const response = await adminFetch(`/api/v1/admin/users/${id}`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(String(response.status));
  }
}
