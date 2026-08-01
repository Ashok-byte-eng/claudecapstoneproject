"""Seed the database with amenities, accommodations, and reviews."""
import asyncio
import random
import uuid
from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.models.accommodation import Accommodation, Amenity, AccommodationAmenity, Review, PropertyType

AMENITY_NAMES = ["wifi", "breakfast", "pool", "gym", "spa"]

DESTINATIONS = ["Lisbon", "Paris", "London"]

HOTEL_NAMES = [
    "Grand Central Hotel", "Blue Horizon Inn", "The Royal Stay",
    "Sunset Suites", "Palm Garden Hotel", "City View Lodge",
    "The Metropolitan", "Golden Gate Hotel", "Heritage House",
    "Atlantic Pearl Hotel",
]

VILLA_NAMES = [
    "Villa Rosa", "Casa Blanca Villa", "The Olive Grove",
    "Serenity Villa", "Le Petit Château", "Villa Bellissima",
    "The Vineyard Retreat", "Azure Coast Villa", "Villa Nova",
    "Hillside Sanctuary",
]


async def seed(session: AsyncSession) -> None:
    existing = await session.execute(select(Amenity))
    if existing.scalars().first():
        print("Database already seeded — skipping.")
        return

    # Amenities
    amenities = {name: Amenity(name=name) for name in AMENITY_NAMES}
    session.add_all(amenities.values())
    await session.flush()

    # Accommodations + reviews
    for destination in DESTINATIONS:
        for name in HOTEL_NAMES:
            acc = Accommodation(
                id=uuid.uuid4(),
                name=f"{name} {destination}",
                property_type=PropertyType.hotel,
                destination=destination,
                price_per_night=Decimal(str(round(random.uniform(60, 350), 2))),
                image_url=f"https://cdn.example.com/{destination.lower()}-hotel.jpg",
            )
            session.add(acc)
            await session.flush()
            _add_amenities(session, acc, amenities)
            _add_reviews(session, acc)

        for name in VILLA_NAMES:
            acc = Accommodation(
                id=uuid.uuid4(),
                name=f"{name} {destination}",
                property_type=PropertyType.villa,
                destination=destination,
                price_per_night=Decimal(str(round(random.uniform(100, 600), 2))),
                image_url=f"https://cdn.example.com/{destination.lower()}-villa.jpg",
            )
            session.add(acc)
            await session.flush()
            _add_amenities(session, acc, amenities)
            _add_reviews(session, acc)

    # Flush inserts so the UPDATE subquery can see them within this transaction
    await session.flush()

    # Recompute review_score from reviews in the same atomic transaction
    await session.execute(
        text(
            "UPDATE accommodations SET review_score = sub.avg_score "
            "FROM (SELECT accommodation_id, AVG(score) as avg_score FROM reviews GROUP BY accommodation_id) sub "
            "WHERE accommodations.id = sub.accommodation_id"
        )
    )
    await session.commit()
    print("Seed complete.")


def _add_amenities(session, acc: Accommodation, amenities: dict) -> None:
    chosen = random.sample(AMENITY_NAMES, k=random.randint(2, 5))
    for name in chosen:
        session.add(
            AccommodationAmenity(accommodation_id=acc.id, amenity_id=amenities[name].id)
        )


def _add_reviews(session, acc: Accommodation) -> None:
    for _ in range(random.randint(3, 10)):
        session.add(
            Review(
                id=uuid.uuid4(),
                accommodation_id=acc.id,
                score=Decimal(str(round(random.uniform(2.5, 5.0), 1))),
            )
        )


async def main() -> None:
    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
