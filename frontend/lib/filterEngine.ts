import type { Accommodation, FilterState } from "@/types/accommodation";

export function filterAccommodations(
  accommodations: Accommodation[],
  filters: FilterState
): Accommodation[] {
  return accommodations.filter((acc) => {
    if (
      filters.selectedAmenities.length > 0 &&
      !filters.selectedAmenities.every((a) => acc.amenities.includes(a))
    ) {
      return false;
    }

    if (
      filters.selectedPropertyTypes.length > 0 &&
      !filters.selectedPropertyTypes.includes(acc.property_type)
    ) {
      return false;
    }

    if (filters.reviewScoreFilter && (acc.review_score === null || acc.review_score < 4.0)) {
      return false;
    }

    return true;
  });
}
