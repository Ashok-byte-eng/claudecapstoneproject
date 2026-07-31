from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.accommodation import Accommodation
from app.schemas.accommodation import AccommodationResponse, AccommodationsListResponse, SearchParams

RECORD_THRESHOLD = 2000


async def get_accommodations(
    params: SearchParams,
    db: AsyncSession,
) -> AccommodationsListResponse:
    stmt = (
        select(Accommodation)
        .where(Accommodation.destination.ilike(f"%{params.destination}%"))
        .options(selectinload(Accommodation.amenities))
        .order_by(Accommodation.review_score.desc().nullslast())
        .limit(RECORD_THRESHOLD)  # enforced in SQL — never loads more than threshold into memory
    )

    result = await db.execute(stmt)
    rows = result.scalars().all()

    accommodations = [_serialize(row) for row in rows]
    return AccommodationsListResponse(total=len(accommodations), accommodations=accommodations)


def _serialize(row: Accommodation) -> AccommodationResponse:
    return AccommodationResponse(
        id=row.id,
        name=row.name,
        property_type=row.property_type.value,
        destination=row.destination,
        price_per_night=float(row.price_per_night) if row.price_per_night else None,
        review_score=float(row.review_score) if row.review_score else None,
        amenities=[a.name for a in row.amenities],
        image_url=row.image_url,
    )
