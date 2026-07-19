import type { Messages } from "../i18n";
import type { CountryCode, EmploymentType, ListingType } from "../api";

export type RoomsChoice = "" | "studio" | "1.5" | "2" | "2.5" | "3" | "3.5" | "4";
export type WorkloadChoice = "" | "40-60" | "80-100";
export type ZoneChoice = "" | CountryCode;

export const JOB_CATEGORIES = [
  "it",
  "healthcare",
  "hospitality",
  "admin",
  "construction",
  "other",
] as const;

export type JobCategory = (typeof JOB_CATEGORIES)[number];

type Props = {
  t: Messages;
  category: ListingType;
  zoneChoice: ZoneChoice;
  onZoneChoiceChange: (value: ZoneChoice) => void;
  roomsChoice: RoomsChoice;
  onRoomsChoiceChange: (value: RoomsChoice) => void;
  hasParking: boolean;
  onHasParkingChange: (value: boolean) => void;
  priceMin: string;
  priceMax: string;
  onPriceMinChange: (value: string) => void;
  onPriceMaxChange: (value: string) => void;
  jobCategory: JobCategory | "";
  onJobCategoryChange: (value: JobCategory | "") => void;
  employmentType: EmploymentType | "";
  onEmploymentTypeChange: (value: EmploymentType | "") => void;
  workloadChoice: WorkloadChoice;
  onWorkloadChoiceChange: (value: WorkloadChoice) => void;
  onApply: () => void;
};

const ROOM_OPTIONS: { value: RoomsChoice; labelKey: keyof Messages }[] = [
  { value: "studio", labelKey: "roomsStudio" },
  { value: "1.5", labelKey: "rooms15" },
  { value: "2", labelKey: "rooms2" },
  { value: "2.5", labelKey: "rooms25" },
  { value: "3", labelKey: "rooms3" },
  { value: "3.5", labelKey: "rooms35" },
  { value: "4", labelKey: "rooms4plus" },
];

const EMPLOYMENT_OPTIONS: EmploymentType[] = [
  "permanent",
  "temporary",
  "internship",
  "freelance",
];

const WORKLOAD_OPTIONS: { value: WorkloadChoice; labelKey: keyof Messages }[] = [
  { value: "40-60", labelKey: "workload4060" },
  { value: "80-100", labelKey: "workload80100" },
];

function jobCategoryLabel(t: Messages, category: JobCategory): string {
  const map: Record<JobCategory, string> = {
    it: t.jobCatIt,
    healthcare: t.jobCatHealthcare,
    hospitality: t.jobCatHospitality,
    admin: t.jobCatAdmin,
    construction: t.jobCatConstruction,
    other: t.jobCatOther,
  };
  return map[category];
}

function employmentLabel(t: Messages, type: EmploymentType): string {
  const map: Record<EmploymentType, string> = {
    permanent: t.employmentPermanent,
    temporary: t.employmentTemporary,
    internship: t.employmentInternship,
    freelance: t.employmentFreelance,
    other: t.employmentOther,
  };
  return map[type];
}

export function FilterBar({
  t,
  category,
  zoneChoice,
  onZoneChoiceChange,
  roomsChoice,
  onRoomsChoiceChange,
  hasParking,
  onHasParkingChange,
  priceMin,
  priceMax,
  onPriceMinChange,
  onPriceMaxChange,
  jobCategory,
  onJobCategoryChange,
  employmentType,
  onEmploymentTypeChange,
  workloadChoice,
  onWorkloadChoiceChange,
  onApply,
}: Props) {
  return (
    <div className="filter-bar">
      <p className="filter-bar-label">{t.filters}</p>

      <p className="filter-group-label">{t.zoneLabel}</p>
      <div className="filter-chips" role="group" aria-label={t.zoneLabel}>
        <button
          type="button"
          className={zoneChoice === "" ? "chip active" : "chip"}
          aria-pressed={zoneChoice === ""}
          onClick={() => onZoneChoiceChange("")}
        >
          {t.zoneBoth}
        </button>
        <button
          type="button"
          className={zoneChoice === "CH" ? "chip active" : "chip"}
          aria-pressed={zoneChoice === "CH"}
          onClick={() => onZoneChoiceChange(zoneChoice === "CH" ? "" : "CH")}
        >
          {t.zoneCH}
        </button>
        <button
          type="button"
          className={zoneChoice === "FR" ? "chip active" : "chip"}
          aria-pressed={zoneChoice === "FR"}
          onClick={() => onZoneChoiceChange(zoneChoice === "FR" ? "" : "FR")}
        >
          {t.zoneFR}
        </button>
      </div>

      {category === "housing" && (
        <>
          <p className="filter-group-label">{t.roomsLabel}</p>
          <div className="filter-chips" role="group" aria-label={t.roomsLabel}>
            <button
              type="button"
              className={roomsChoice === "" ? "chip active" : "chip"}
              aria-pressed={roomsChoice === ""}
              onClick={() => onRoomsChoiceChange("")}
            >
              {t.filterAny}
            </button>
            {ROOM_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={roomsChoice === option.value ? "chip active" : "chip"}
                aria-pressed={roomsChoice === option.value}
                onClick={() =>
                  onRoomsChoiceChange(roomsChoice === option.value ? "" : option.value)
                }
              >
                {t[option.labelKey]}
              </button>
            ))}
          </div>

          <div className="filter-chips" role="group" aria-label={t.parkingLabel}>
            <button
              type="button"
              className={hasParking ? "chip active" : "chip"}
              aria-pressed={hasParking}
              onClick={() => onHasParkingChange(!hasParking)}
            >
              {t.parkingLabel}
            </button>
          </div>

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
        </>
      )}

      {category === "job" && (
        <>
          <p className="filter-group-label">{t.jobCategoryLabel}</p>
          <div className="filter-chips" role="group" aria-label={t.jobCategoryLabel}>
            <button
              type="button"
              className={jobCategory === "" ? "chip active" : "chip"}
              aria-pressed={jobCategory === ""}
              onClick={() => onJobCategoryChange("")}
            >
              {t.filterAny}
            </button>
            {JOB_CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                className={jobCategory === cat ? "chip active" : "chip"}
                aria-pressed={jobCategory === cat}
                onClick={() => onJobCategoryChange(jobCategory === cat ? "" : cat)}
              >
                {jobCategoryLabel(t, cat)}
              </button>
            ))}
          </div>

          <p className="filter-group-label">{t.employmentTypeLabel}</p>
          <div className="filter-chips" role="group" aria-label={t.employmentTypeLabel}>
            <button
              type="button"
              className={employmentType === "" ? "chip active" : "chip"}
              aria-pressed={employmentType === ""}
              onClick={() => onEmploymentTypeChange("")}
            >
              {t.filterAny}
            </button>
            {EMPLOYMENT_OPTIONS.map((type) => (
              <button
                key={type}
                type="button"
                className={employmentType === type ? "chip active" : "chip"}
                aria-pressed={employmentType === type}
                onClick={() =>
                  onEmploymentTypeChange(employmentType === type ? "" : type)
                }
              >
                {employmentLabel(t, type)}
              </button>
            ))}
          </div>

          <p className="filter-group-label">{t.workloadLabel}</p>
          <div className="filter-chips" role="group" aria-label={t.workloadLabel}>
            <button
              type="button"
              className={workloadChoice === "" ? "chip active" : "chip"}
              aria-pressed={workloadChoice === ""}
              onClick={() => onWorkloadChoiceChange("")}
            >
              {t.filterAny}
            </button>
            {WORKLOAD_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={workloadChoice === option.value ? "chip active" : "chip"}
                aria-pressed={workloadChoice === option.value}
                onClick={() =>
                  onWorkloadChoiceChange(
                    workloadChoice === option.value ? "" : option.value,
                  )
                }
              >
                {t[option.labelKey]}
              </button>
            ))}
          </div>

          <div className="filter-row">
            <button type="button" className="secondary-btn" onClick={onApply}>
              {t.applyFilters}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
