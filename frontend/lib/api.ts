import type { AccommodationsListResponse, SearchParams } from "@/types/accommodation";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function fetchAccommodations(
  params: SearchParams
): Promise<AccommodationsListResponse> {
  const query = new URLSearchParams({
    destination: params.destination,
    check_in: params.check_in,
    check_out: params.check_out,
    guests: String(params.guests),
  });

  const res = await fetch(`${API_BASE}/api/accommodations?${query}`);
  if (!res.ok) {
    throw new ApiError(res.status, `API error: ${res.status}`);
  }
  return res.json();
}
