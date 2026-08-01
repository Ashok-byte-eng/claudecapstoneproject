import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accommodation import Accommodation, Amenity, AccommodationAmenity, PropertyType
from app.schemas.accommodation import SearchParams
from app.services.accommodation_service import get_accommodations, RECORD_THRESHOLD
from datetime import date


async def _create_accommodation(session: AsyncSession, destination: str, amenity_names: list[str],
                                 property_type=PropertyType.hotel, score=4.5) -> Accommodation:
    acc = Accommodation(
        id=uuid.uuid4(),
        name=f"Test {destination}",
        property_type=property_type,
        destination=destination,
        price_per_night=Decimal("100.00"),
        review_score=Decimal(str(score)),
    )
    session.add(acc)
    await session.flush()
    for name in amenity_names:
        result = await session.execute(
            __import__("sqlalchemy", fromlist=["select"]).select(Amenity).where(Amenity.name == name)
        )
        amenity = result.scalars().first()
        if not amenity:
            amenity = Amenity(name=name)
            session.add(amenity)
            await session.flush()
        session.add(AccommodationAmenity(accommodation_id=acc.id, amenity_id=amenity.id))
    await session.commit()
    return acc


@pytest.mark.anyio
async def test_returns_accommodations_for_destination(db_session: AsyncSession):
    await _create_accommodation(db_session, "Lisbon", ["wifi"])
    params = SearchParams(destination="Lisbon", check_in=date(2026, 8, 1), check_out=date(2026, 8, 5), guests=2)
    result = await get_accommodations(params, db_session)
    assert result.total >= 1
    assert all(a.destination == "Lisbon" for a in result.accommodations)


@pytest.mark.anyio
async def test_amenities_included_in_response(db_session: AsyncSession):
    await _create_accommodation(db_session, "Paris", ["pool", "gym"])
    params = SearchParams(destination="Paris", check_in=date(2026, 8, 1), check_out=date(2026, 8, 5), guests=1)
    result = await get_accommodations(params, db_session)
    paris = next(a for a in result.accommodations if a.destination == "Paris")
    assert "pool" in paris.amenities
    assert "gym" in paris.amenities


@pytest.mark.anyio
async def test_threshold_enforced(db_session: AsyncSession, monkeypatch):
    import app.services.accommodation_service as svc
    monkeypatch.setattr(svc, "RECORD_THRESHOLD", 2)
    for i in range(5):
        await _create_accommodation(db_session, "London", ["wifi"], score=3.0 + i * 0.1)
    params = SearchParams(destination="London", check_in=date(2026, 8, 1), check_out=date(2026, 8, 5), guests=1)
    result = await get_accommodations(params, db_session)
    assert result.total <= 2
