"""serie diaria de Tmin e Tmax do clima: tabela clima_serie_diaria (uma linha por celula e ano)

Celulas baixadas antes desta migration ficam sem serie diaria; o servico de clima baixa de novo uma vez no proximo uso.

Revision ID: 0008
Revises: 0007
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'clima_serie_diaria',
        sa.Column('celula_id', sa.String(length=32), sa.ForeignKey('clima_celula.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ano', sa.SmallInteger(), nullable=False),
        sa.Column('tmin_c', postgresql.ARRAY(sa.REAL()), nullable=False),
        sa.Column('tmax_c', postgresql.ARRAY(sa.REAL()), nullable=False),
        sa.PrimaryKeyConstraint('celula_id', 'ano'),
    )


def downgrade() -> None:
    op.drop_table('clima_serie_diaria')
