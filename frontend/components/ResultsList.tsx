"use client";
import { useFilterStore } from "@/store/filterStore";
import type { Accommodation } from "@/types/accommodation";

const AMENITY_ICONS: Record<string, string> = {
  wifi: "📶", breakfast: "🍳", pool: "🏊", gym: "💪", spa: "🛁",
};

function AccommodationCard({ acc }: { acc: Accommodation }) {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden flex flex-col">
      {acc.image_url && (
        <img src={acc.image_url} alt={acc.name} className="h-40 w-full object-cover" />
      )}
      <div className="p-4 flex flex-col gap-2 flex-1">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight">{acc.name}</h3>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full whitespace-nowrap capitalize">
            {acc.property_type}
          </span>
        </div>
        <p className="text-xs text-gray-500">{acc.destination}</p>
        <div className="flex gap-1 flex-wrap">
          {acc.amenities.map((a) => (
            <span key={a} title={a} className="text-base" aria-label={a}>
              {AMENITY_ICONS[a] ?? a}
            </span>
          ))}
        </div>
        <div className="mt-auto flex items-center justify-between pt-2 border-t border-gray-100">
          {acc.review_score !== null ? (
            <span className="text-sm font-medium text-amber-600">★ {acc.review_score.toFixed(1)}</span>
          ) : (
            <span className="text-xs text-gray-400">No reviews</span>
          )}
          {acc.price_per_night !== null && (
            <span className="text-sm font-semibold text-gray-800">
              €{acc.price_per_night.toFixed(0)}<span className="font-normal text-gray-400">/night</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ResultsList() {
  const { filteredAccommodations, allAccommodations, isLoading, error } = useFilterStore();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-gray-100 rounded-xl h-64 animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16 text-red-500">
        <p className="font-medium">{error}</p>
        <p className="text-sm mt-1 text-gray-500">Please try refreshing the page.</p>
      </div>
    );
  }

  if (filteredAccommodations.length === 0) {
    return (
      <div className="text-center py-16 text-gray-500">
        <p className="text-lg font-medium">No properties match your filters.</p>
        <p className="text-sm mt-1">Try adjusting your selection.</p>
      </div>
    );
  }

  return (
    <div>
      <p className="text-sm text-gray-500 mb-4">
        Showing <strong className="text-gray-800">{filteredAccommodations.length}</strong> of{" "}
        {allAccommodations.length} properties
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredAccommodations.map((acc) => (
          <AccommodationCard key={acc.id} acc={acc} />
        ))}
      </div>
    </div>
  );
}
