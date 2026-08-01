"""Nightly job: recompute review_score on all accommodations from reviews table."""
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.config import settings


async def main() -> None:
    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await session.execute(
            text(
                "UPDATE accommodations "
                "SET review_score = sub.avg_score, updated_at = NOW() "
                "FROM ("
                "  SELECT accommodation_id, AVG(score)::numeric(3,2) AS avg_score "
                "  FROM reviews GROUP BY accommodation_id"
                ") sub "
                "WHERE accommodations.id = sub.accommodation_id"
            )
        )
        await session.commit()
    await engine.dispose()
    print("Review scores refreshed.")


if __name__ == "__main__":
    asyncio.run(main())
