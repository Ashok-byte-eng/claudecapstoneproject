from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.limiter import limiter
from app.schemas.accommodation import AccommodationsListResponse, SearchParams
from app.services.accommodation_service import get_accommodations

router = APIRouter()


@router.get("/accommodations", response_model=AccommodationsListResponse)
@limiter.limit("60/minute")
async def list_accommodations(
    request: Request,
    params: SearchParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> AccommodationsListResponse:
    return await get_accommodations(params, db)
