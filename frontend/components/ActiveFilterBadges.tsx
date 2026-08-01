"use client";
import { useFilterStore } from "@/store/filterStore";

const LABELS: Record<string, string> = {
  wifi: "Free Wi-Fi", breakfast: "Breakfast", pool: "Pool",
  gym: "Gym", spa: "Spa", hotel: "Hotel", villa: "Villa",
};

export default function ActiveFilterBadges() {
  const {
    selectedAmenities, selectedPropertyTypes, reviewScoreFilter,
    toggleAmenity, togglePropertyType, toggleReviewFilter, clearAllFilters,
  } = useFilterStore();

  const hasFilters = selectedAmenities.length > 0 || selectedPropertyTypes.length > 0 || reviewScoreFilter;
  if (!hasFilters) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 py-2">
      {selectedAmenities.map((a) => (
        <Chip key={a} label={LABELS[a] ?? a} onRemove={() => toggleAmenity(a)} />
      ))}
      {selectedPropertyTypes.map((t) => (
        <Chip key={t} label={LABELS[t] ?? t} onRemove={() => togglePropertyType(t)} />
      ))}
      {reviewScoreFilter && (
        <Chip label="★ 4+ only" onRemove={toggleReviewFilter} />
      )}
      <button onClick={clearAllFilters} className="text-xs text-blue-600 hover:underline ml-1">
        Clear all
      </button>
    </div>
  );
}

function Chip({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full">
      {label}
      <button onClick={onRemove} aria-label={`Remove ${label} filter`} className="hover:text-blue-900">
        ×
      </button>
    </span>
  );
}
