"""add hazard_category column for better grouping

Revision ID: 9d253ef6b775
Revises: 6d42fa2ea67a
Create Date: 2026-07-06 17:28:58.039745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9d253ef6b775'
down_revision: Union[str, Sequence[str], None] = '6d42fa2ea67a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    hazard_category_enum = postgresql.ENUM(
        'FIRE', 'TRAFFIC', 'FLOOD', 'STRUCTURAL', 'ENVIRONMENTAL', 'CRIME', 'CRITICAL_SUPPLY',
        name='hazardcategory'
    )
    hazard_category_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'risks',
        sa.Column('hazard_category', hazard_category_enum, nullable=True)
    )

    risk_status_enum = postgresql.ENUM(
        'PENDING', 'VERIFIED', 'REJECTED',
        name='riskstatus'
    )
    risk_status_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        'risks', 'status',
        existing_type=sa.VARCHAR(),
        type_=risk_status_enum,
        existing_nullable=True,
        postgresql_using='status::riskstatus',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'risks', 'status',
        existing_type=postgresql.ENUM('PENDING', 'VERIFIED', 'REJECTED', name='riskstatus'),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using='status::varchar',
    )
    postgresql.ENUM(name='riskstatus').drop(op.get_bind(), checkfirst=True)

    op.drop_column('risks', 'hazard_category')
    postgresql.ENUM(name='hazardcategory').drop(op.get_bind(), checkfirst=True)