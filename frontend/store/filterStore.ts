import { create } from "zustand";
import { filterAccommodations } from "@/lib/filterEngine";
import type { Accommodation, FilterState } from "@/types/accommodation";

interface FilterStore extends FilterState {
  allAccommodations: Accommodation[];
  isLoading: boolean;
  error: string | null;
  filteredAccommodations: Accommodation[];

  setAllAccommodations: (data: Accommodation[]) => void;
  setLoading: (v: boolean) => void;
  setError: (msg: string | null) => void;
  toggleAmenity: (name: string) => void;
  togglePropertyType: (name: string) => void;
  toggleReviewFilter: () => void;
  clearAllFilters: () => void;
}

const recompute = (state: FilterStore): Accommodation[] =>
  filterAccommodations(state.allAccommodations, {
    selectedAmenities: state.selectedAmenities,
    selectedPropertyTypes: state.selectedPropertyTypes,
    reviewScoreFilter: state.reviewScoreFilter,
  });

export const selectActiveFilterCount = (state: FilterStore): number =>
  state.selectedAmenities.length + state.selectedPropertyTypes.length + (state.reviewScoreFilter ? 1 : 0);

export const useFilterStore = create<FilterStore>((set, get) => ({
  allAccommodations: [],
  selectedAmenities: [],
  selectedPropertyTypes: [],
  reviewScoreFilter: false,
  isLoading: false,
  error: null,
  filteredAccommodations: [],

  setAllAccommodations: (data) =>
    set((state) => {
      const next = { ...state, allAccommodations: data };
      return { ...next, filteredAccommodations: recompute(next as FilterStore) };
    }),

  setLoading: (v) => set({ isLoading: v }),
  setError: (msg) => set({ error: msg }),

  toggleAmenity: (name) =>
    set((state) => {
      const selected = state.selectedAmenities.includes(name)
        ? state.selectedAmenities.filter((a) => a !== name)
        : [...state.selectedAmenities, name];
      const next = { ...state, selectedAmenities: selected };
      return { selectedAmenities: selected, filteredAccommodations: recompute(next as FilterStore) };
    }),

  togglePropertyType: (name) =>
    set((state) => {
      const selected = state.selectedPropertyTypes.includes(name)
        ? state.selectedPropertyTypes.filter((t) => t !== name)
        : [...state.selectedPropertyTypes, name];
      const next = { ...state, selectedPropertyTypes: selected };
      return { selectedPropertyTypes: selected, filteredAccommodations: recompute(next as FilterStore) };
    }),

  toggleReviewFilter: () =>
    set((state) => {
      const next = { ...state, reviewScoreFilter: !state.reviewScoreFilter };
      return { reviewScoreFilter: next.reviewScoreFilter, filteredAccommodations: recompute(next as FilterStore) };
    }),

  clearAllFilters: () =>
    set((state) => ({
      selectedAmenities: [],
      selectedPropertyTypes: [],
      reviewScoreFilter: false,
      filteredAccommodations: state.allAccommodations,
    })),
}));
