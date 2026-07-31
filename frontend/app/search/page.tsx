"use client";
import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { fetchAccommodations } from "@/lib/api";
import { useFilterStore } from "@/store/filterStore";
import FilterPanel from "@/components/FilterPanel";
import ResultsList from "@/components/ResultsList";
import ActiveFilterBadges from "@/components/ActiveFilterBadges";

export default function SearchPage() {
  const searchParams = useSearchParams();
  const { setAllAccommodations, setLoading, setError } = useFilterStore();

  const destination = searchParams.get("destination") ?? "Lisbon";
  const check_in = searchParams.get("check_in") ?? "2026-08-01";
  const check_out = searchParams.get("check_out") ?? "2026-08-07";
  const guests = Number(searchParams.get("guests") ?? "2");

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchAccommodations({ destination, check_in, check_out, guests })
      .then((data) => setAllAccommodations(data.accommodations))
      .catch((err) => setError(err.message ?? "Failed to load accommodations."))
      .finally(() => setLoading(false));
    // Zustand actions are referentially stable — safe to omit from deps
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [destination, check_in, check_out, guests]);

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-lg font-bold text-gray-900">
            Stays in <span className="text-blue-600">{destination}</span>
          </h1>
        </div>
      </header>

      {/* FilterPanel renders its own desktop sidebar + mobile drawer internally */}
      <div className="max-w-7xl mx-auto px-4 py-6 flex gap-6">
        <FilterPanel />
        <div className="flex-1 min-w-0">
          <ActiveFilterBadges />
          <ResultsList />
        </div>
      </div>
    </main>
  );
}
