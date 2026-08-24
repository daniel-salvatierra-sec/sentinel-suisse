/** Job field → branches → roles (compact, not hyper-specific). */

export const JOB_FIELDS = [
  "it",
  "healthcare",
  "construction",
  "hospitality",
  "admin",
  "finance",
  "sales",
  "education",
  "logistics",
  "watchmaking",
  "other",
] as const;

export type JobField = (typeof JOB_FIELDS)[number];

export const JOB_BRANCHES: Record<JobField, readonly string[]> = {
  it: ["software", "soc", "data", "network", "support"],
  healthcare: ["nursing", "doctor", "therapy", "care", "pharma"],
  construction: ["architecture", "civil", "engineering", "trades"],
  hospitality: ["kitchen", "service", "hotel", "tourism"],
  admin: ["hr", "office", "accounting", "consulting"],
  finance: ["banking", "insurance", "fiduciary"],
  sales: ["retail", "b2b", "customer"],
  education: ["teaching", "social", "public"],
  logistics: ["warehouse", "transport", "purchasing"],
  watchmaking: ["watchmaker", "jewelry", "microtech", "aftersales"],
  other: ["legal", "creative", "science", "manufacturing", "property"],
};

/** Extra chip row only where one specialty still covers many jobs. */
export const JOB_ROLES: Record<string, readonly string[]> = {
  transport: ["bus", "truck", "delivery", "crane", "taxi"],
  nursing: ["hospital", "homecare", "geriatric", "clinic"],
  watchmaker: ["assembly", "restoration", "polishing"],
  retail: ["florist", "cashier"],
};

/** Map branch → parent field (for match + API). */
export const BRANCH_PARENT: Record<string, JobField> = Object.fromEntries(
  JOB_FIELDS.flatMap((field) => JOB_BRANCHES[field].map((branch) => [branch, field])),
) as Record<string, JobField>;

export const ROLE_PARENT: Record<string, string> = Object.fromEntries(
  Object.entries(JOB_ROLES).flatMap(([branch, roles]) => roles.map((role) => [role, branch])),
);

export function resolveJobCategory(
  field: JobField | "",
  branch: string,
  role = "",
): string | undefined {
  if (role) return role;
  if (branch) return branch;
  if (field) return field;
  return undefined;
}

export function jobCategoryAncestors(slug: string): string[] {
  const chain: string[] = [];
  let current: string | undefined = ROLE_PARENT[slug] ?? BRANCH_PARENT[slug];
  while (current) {
    chain.push(current);
    current = ROLE_PARENT[current] ?? BRANCH_PARENT[current];
  }
  return chain;
}
