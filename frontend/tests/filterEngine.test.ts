import { filterAccommodations } from "../lib/filterEngine";
import type { Accommodation, FilterState } from "../types/accommodation";

const make = (overrides: Partial<Accommodation> = {}): Accommodation => ({
  id: "1",
  name: "Test Hotel",
  property_type: "hotel",
  destination: "Lisbon",
  price_per_night: 120,
  review_score: 4.5,
  amenities: ["wifi", "pool"],
  image_url: null,
  ...overrides,
});

const noFilters: FilterState = {
  selectedAmenities: [],
  selectedPropertyTypes: [],
  reviewScoreFilter: false,
};

test("returns all when no filters active", () => {
  const data = [make(), make({ id: "2" })];
  expect(filterAccommodations(data, noFilters)).toHaveLength(2);
});

test("amenity AND logic: both required amenities must be present", () => {
  const withBoth = make({ amenities: ["pool", "gym"] });
  const withOne = make({ id: "2", amenities: ["pool"] });
  const result = filterAccommodations([withBoth, withOne], {
    ...noFilters,
    selectedAmenities: ["pool", "gym"],
  });
  expect(result).toHaveLength(1);
  expect(result[0].id).toBe("1");
});

test("property type OR logic: hotel or villa matches either", () => {
  const hotel = make({ property_type: "hotel" });
  const villa = make({ id: "2", property_type: "villa" });
  const result = filterAccommodations([hotel, villa], {
    ...noFilters,
    selectedPropertyTypes: ["hotel", "villa"],
  });
  expect(result).toHaveLength(2);
});

test("review score filter excludes below 4.0", () => {
  const high = make({ review_score: 4.5 });
  const low = make({ id: "2", review_score: 3.8 });
  const nullScore = make({ id: "3", review_score: null });
  const result = filterAccommodations([high, low, nullScore], {
    ...noFilters,
    reviewScoreFilter: true,
  });
  expect(result).toHaveLength(1);
  expect(result[0].id).toBe("1");
});

test("score exactly 4.0 is included", () => {
  const acc = make({ review_score: 4.0 });
  const result = filterAccommodations([acc], { ...noFilters, reviewScoreFilter: true });
  expect(result).toHaveLength(1);
});

test("combined filters: amenity + property type + review score", () => {
  const match = make({ amenities: ["wifi"], property_type: "hotel", review_score: 4.2 });
  const noAmenity = make({ id: "2", amenities: [], property_type: "hotel", review_score: 4.5 });
  const wrongType = make({ id: "3", amenities: ["wifi"], property_type: "villa", review_score: 4.5 });
  const lowScore = make({ id: "4", amenities: ["wifi"], property_type: "hotel", review_score: 3.0 });
  const result = filterAccommodations([match, noAmenity, wrongType, lowScore], {
    selectedAmenities: ["wifi"],
    selectedPropertyTypes: ["hotel"],
    reviewScoreFilter: true,
  });
  expect(result).toHaveLength(1);
  expect(result[0].id).toBe("1");
});

test("no matches returns empty array", () => {
  const acc = make({ amenities: ["wifi"], review_score: 3.0 });
  const result = filterAccommodations([acc], { ...noFilters, reviewScoreFilter: true });
  expect(result).toHaveLength(0);
});
