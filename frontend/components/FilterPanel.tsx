"use client";
import { useState } from "react";
import { useFilterStore } from "@/store/filterStore";

const AMENITIES = [
  { value: "wifi", label: "Free Wi-Fi" },
  { value: "breakfast", label: "Breakfast Included" },
  { value: "pool", label: "Pool" },
  { value: "gym", label: "Gym" },
  { value: "spa", label: "Spa" },
];

const PROPERTY_TYPES = [
  { value: "hotel", label: "Hotel" },
  { value: "villa", label: "Villa" },
];

function FilterContent() {
  const {
    selectedAmenities, selectedPropertyTypes, reviewScoreFilter,
    toggleAmenity, togglePropertyType, toggleReviewFilter, clearAllFilters,
  } = useFilterStore();

  const activeCount = selectedAmenities.length + selectedPropertyTypes.length + (reviewScoreFilter ? 1 : 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-gray-900 text-base">
          Filters{activeCount > 0 && (
            <span className="ml-2 bg-blue-600 text-white text-xs rounded-full px-2 py-0.5">{activeCount}</span>
          )}
        </h2>
        {activeCount > 0 && (
          <button onClick={clearAllFilters} className="text-xs text-blue-600 hover:underline">
            Clear all
          </button>
        )}
      </div>

      {/* Amenities */}
      <section>
        <h3 className="text-sm font-medium text-gray-700 mb-2">Amenities</h3>
        <div className="space-y-2">
          {AMENITIES.map(({ value, label }) => (
            <label key={value} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedAmenities.includes(value)}
                onChange={() => toggleAmenity(value)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{label}</span>
            </label>
          ))}
        </div>
      </section>

      {/* Property Type */}
      <section>
        <h3 className="text-sm font-medium text-gray-700 mb-2">Property Type</h3>
        <div className="space-y-2">
          {PROPERTY_TYPES.map(({ value, label }) => (
            <label key={value} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedPropertyTypes.includes(value)}
                onChange={() => togglePropertyType(value)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{label}</span>
            </label>
          ))}
        </div>
      </section>

      {/* Review Score */}
      <section>
        <h3 className="text-sm font-medium text-gray-700 mb-2">Review Score</h3>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={reviewScoreFilter}
            onChange={toggleReviewFilter}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">★ 4 and above only</span>
        </label>
      </section>
    </div>
  );
}

export default function FilterPanel() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { selectedAmenities, selectedPropertyTypes, reviewScoreFilter } = useFilterStore();
  const activeCount = selectedAmenities.length + selectedPropertyTypes.length + (reviewScoreFilter ? 1 : 0);

  return (
    <>
      {/* Desktop sidebar — hidden on mobile */}
      <aside className="hidden md:block w-64 flex-shrink-0">
        <div className="sticky top-4 bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <FilterContent />
        </div>
      </aside>

      {/* Mobile — filter button + drawer */}
      <div className="md:hidden">
        <button
          onClick={() => setDrawerOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg shadow-sm text-sm font-medium text-gray-700"
        >
          <span>Filters</span>
          {activeCount > 0 && (
            <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-0.5">{activeCount}</span>
          )}
        </button>

        {/* Drawer overlay */}
        {drawerOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/40"
            onClick={() => setDrawerOpen(false)}
            aria-hidden="true"
          />
        )}

        {/* Drawer panel */}
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Filters"
          className={`fixed inset-x-0 bottom-0 z-50 bg-white rounded-t-2xl p-6 shadow-xl transition-transform duration-300 ${
            drawerOpen ? "translate-y-0" : "translate-y-full"
          }`}
          onKeyDown={(e) => e.key === "Escape" && setDrawerOpen(false)}
          tabIndex={-1}
        >
          <FilterContent />
          <button
            onClick={() => setDrawerOpen(false)}
            className="mt-6 w-full py-3 bg-blue-600 text-white rounded-xl font-medium text-sm"
          >
            Show results
          </button>
        </div>
      </div>
    </>
  );
}
