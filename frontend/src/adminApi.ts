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
  description: string | null;
  price: number | null;
};

export type AdminUser = {
  id: number;
  email: string;
  locale: string;
  is_active: boolean;
  is_premium: boolean;
  free_alerts_grandfathered: boolean;
  can_receive_alerts: boolean;
  created_at: string;
  saved_search_count: number;
};

export type AdminListingInput = {
  listing_type: "housing" | "job";
  title: string;
  location: string;
  contact_url: string;
  price?: number;
  description?: string;
  owner_user_id?: number;
  is_hidden?: boolean;
};

export type AdminListingPatch = {
  title?: string;
  location?: string;
  contact_url?: string;
  price?: number;
  description?: string;
  listing_type?: "housing" | "job";
  is_hidden?: boolean;
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

export type OpsAppCard = {
  id: string;
  name: string;
  public_url: string;
  admin_url: string;
  status: string;
  is_current: boolean;
};

export type ActiveBoost = {
  id: number;
  title: string;
  listing_type: "housing" | "job";
  location: string | null;
  owner_user_id: number | null;
  featured_until: string | null;
};

export type DailySignupMetric = {
  day: string;
  count: number;
};

export type WeeklyPaymentMetric = {
  week_start: string;
  premium_count: number;
  boost_count: number;
  amount_chf: number | string;
};

export type RecentPayment = {
  checkout_id: string;
  kind: string;
  label: string;
  amount_chf: number | string;
  paid_at: string;
  listing_id: number | null;
};

export type StripeRevenueSummary = {
  configured: boolean;
  currency: string;
  last_30_days_total_chf: number | string;
  premium_payments_30d: number;
  boost_payments_30d: number;
  recent_payments: RecentPayment[];
  payments_by_week: WeeklyPaymentMetric[];
};

export type AdminSponsor = {
  id: number;
  sponsor_name: string;
  placement: string;
  context: "all" | "housing" | "job";
  headline: string | null;
  image_url: string | null;
  target_url: string;
  monthly_chf: number | string;
  starts_at: string | null;
  ends_at: string | null;
  is_active: boolean;
  sort_order: number;
  impression_count: number;
  click_count: number;
  created_at: string;
  updated_at: string;
};

export type SponsorRevenueSummary = {
  active_count: number;
  estimated_monthly_chf: number | string;
  total_impressions: number;
  total_clicks: number;
  active_sponsors: AdminSponsor[];
};

export type AdminInsights = {
  apps: OpsAppCard[];
  active_boosts: ActiveBoost[];
  signups_by_day: DailySignupMetric[];
  stripe: StripeRevenueSummary;
  sponsors: SponsorRevenueSummary;
};

export type AdminSponsorInput = {
  sponsor_name: string;
  context: "all" | "housing" | "job";
  headline?: string | null;
  image_url?: string | null;
  target_url: string;
  monthly_chf?: number;
  starts_at?: string | null;
  ends_at?: string | null;
  is_active?: boolean;
  sort_order?: number;
};

function sponsorPayload(input: AdminSponsorInput): Record<string, unknown> {
  const body: Record<string, unknown> = {
    sponsor_name: input.sponsor_name,
    context: input.context,
    target_url: input.target_url,
    monthly_chf: input.monthly_chf ?? 0,
    is_active: input.is_active ?? true,
    sort_order: input.sort_order ?? 0,
  };
  if (input.headline) {
    body.headline = input.headline;
  }
  if (input.image_url) {
    body.image_url = input.image_url;
  }
  if (input.starts_at) {
    body.starts_at = input.starts_at;
  }
  if (input.ends_at) {
    body.ends_at = input.ends_at;
  }
  return body;
}

export async function fetchAdminInsights(): Promise<AdminInsights> {
  const response = await adminFetch("/api/v1/admin/insights");
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<AdminInsights>;
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

export async function createAdminListing(payload: AdminListingInput): Promise<AdminListing> {
  const response = await adminFetch("/api/v1/admin/listings", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<AdminListing>;
}

export async function updateAdminListing(
  id: number,
  payload: AdminListingPatch,
): Promise<AdminListing> {
  const response = await adminFetch(`/api/v1/admin/listings/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
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

export async function setUserFreeAlerts(
  id: number,
  freeAlertsGrandfathered: boolean,
): Promise<AdminUser> {
  const response = await adminFetch(`/api/v1/admin/users/${id}/free-alerts`, {
    method: "PATCH",
    body: JSON.stringify({ free_alerts_grandfathered: freeAlertsGrandfathered }),
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

export async function fetchAdminSponsors(): Promise<AdminSponsor[]> {
  const response = await adminFetch("/api/v1/admin/sponsors?limit=100");
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<AdminSponsor[]>;
}

export async function createAdminSponsor(input: AdminSponsorInput): Promise<AdminSponsor> {
  const response = await adminFetch("/api/v1/admin/sponsors", {
    method: "POST",
    body: JSON.stringify(sponsorPayload(input)),
  });
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<AdminSponsor>;
}

export async function updateAdminSponsor(
  id: number,
  patch: Partial<AdminSponsorInput>,
): Promise<AdminSponsor> {
  const response = await adminFetch(`/api/v1/admin/sponsors/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
  if (!response.ok) {
    throw new Error(String(response.status));
  }
  return response.json() as Promise<AdminSponsor>;
}

export async function deleteAdminSponsor(id: number): Promise<void> {
  const response = await adminFetch(`/api/v1/admin/sponsors/${id}`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(String(response.status));
  }
}
