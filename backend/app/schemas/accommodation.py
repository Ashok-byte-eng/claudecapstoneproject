from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SearchParams(BaseModel):
    destination: str = Field(..., min_length=1, max_length=255)
    check_in: date
    check_out: date
    guests: int = Field(..., ge=1, le=30)

    @model_validator(mode="after")
    def check_dates(self) -> "SearchParams":
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self


class AccommodationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    property_type: str
    destination: str
    price_per_night: float | None
    review_score: float | None
    amenities: list[str]
    image_url: str | None


class AccommodationsListResponse(BaseModel):
    total: int
    accommodations: list[AccommodationResponse]
