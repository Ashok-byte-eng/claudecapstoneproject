import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint, DateTime, Enum, ForeignKey,
    Numeric, String, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class PropertyType(str, enum.Enum):
    hotel = "hotel"
    villa = "villa"


class Amenity(Base):
    __tablename__ = "amenities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    accommodations: Mapped[list["Accommodation"]] = relationship(
        "Accommodation", secondary="accommodation_amenities", back_populates="amenities"
    )


class AccommodationAmenity(Base):
    __tablename__ = "accommodation_amenities"

    accommodation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accommodations.id", ondelete="CASCADE"), primary_key=True
    )
    amenity_id: Mapped[int] = mapped_column(
        ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True
    )


class Accommodation(Base):
    __tablename__ = "accommodations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    property_type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType, name="property_type_enum"), nullable=False
    )
    destination: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    price_per_night: Mapped[float | None] = mapped_column(Numeric(10, 2))
    review_score: Mapped[float | None] = mapped_column(Numeric(3, 2), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    amenities: Mapped[list[Amenity]] = relationship(
        Amenity, secondary="accommodation_amenities", back_populates="accommodations"
    )
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="accommodation")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    accommodation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accommodations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        info={"constraints": [CheckConstraint("score >= 0 AND score <= 5")]},
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    accommodation: Mapped[Accommodation] = relationship(
        Accommodation, back_populates="reviews"
    )
