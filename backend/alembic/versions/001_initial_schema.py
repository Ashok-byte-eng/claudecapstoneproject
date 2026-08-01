"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE property_type_enum AS ENUM ('hotel', 'villa')")

    op.create_table(
        "accommodations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column(
            "property_type",
            sa.Enum("hotel", "villa", name="property_type_enum"),
            nullable=False,
        ),
        sa.Column("destination", sa.String(255), nullable=False),
        sa.Column("price_per_night", sa.Numeric(10, 2)),
        sa.Column("review_score", sa.Numeric(3, 2)),
        sa.Column("image_url", sa.String(500)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "amenities",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
    )

    op.create_table(
        "accommodation_amenities",
        sa.Column(
            "accommodation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accommodations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "amenity_id",
            sa.Integer,
            sa.ForeignKey("amenities.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "accommodation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accommodations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.Numeric(3, 2), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.CheckConstraint("score >= 0 AND score <= 5", name="reviews_score_range"),
    )

    op.create_index("idx_review_score", "accommodations", ["review_score"])
    op.create_index("idx_property_type", "accommodations", ["property_type"])
    op.create_index("idx_destination", "accommodations", ["destination"])
    op.create_index("idx_reviews_acc_id", "reviews", ["accommodation_id"])


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("accommodation_amenities")
    op.drop_table("amenities")
    op.drop_table("accommodations")
    op.execute("DROP TYPE property_type_enum")
