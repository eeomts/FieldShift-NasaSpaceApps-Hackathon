"""clima_mensal.tmin_diaria: Tmin de cada dia do mês (regra 17, frio por fase)

Revision ID: 0008
Revises: 0007

Lista JSONB de 28 a 31 valores (índice = dia - 1; null no dia sem dado). As linhas já gravadas ficam com NULL:
o serviço de clima baixa a célula de novo no primeiro uso (mesma regra do gd_por_tb).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('clima_mensal', sa.Column('tmin_diaria', postgresql.JSONB(none_as_null=True), nullable=True))


def downgrade() -> None:
    op.drop_column('clima_mensal', 'tmin_diaria')
