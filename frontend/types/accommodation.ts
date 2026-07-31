export interface Accommodation {
  id: string;
  name: string;
  property_type: "hotel" | "villa";
  destination: string;
  price_per_night: number | null;
  review_score: number | null;
  amenities: string[];
  image_url: string | null;
}

export interface AccommodationsListResponse {
  total: number;
  accommodations: Accommodation[];
}

export interface SearchParams {
  destination: string;
  check_in: string;
  check_out: string;
  guests: number;
}

export interface FilterState {
  selectedAmenities: string[];
  selectedPropertyTypes: string[];
  reviewScoreFilter: boolean;
}
