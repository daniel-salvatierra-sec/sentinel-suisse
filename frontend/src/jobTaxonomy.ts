/** Job field → branches (jobs.ch style, compact). */

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
  other: [],
};

/** Map branch → parent field (for match + API). */
export const BRANCH_PARENT: Record<string, JobField> = Object.fromEntries(
  JOB_FIELDS.flatMap((field) => JOB_BRANCHES[field].map((branch) => [branch, field])),
) as Record<string, JobField>;

export function resolveJobCategory(
  field: JobField | "",
  branch: string,
): string | undefined {
  if (branch) return branch;
  if (field) return field;
  return undefined;
}
