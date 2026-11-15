"""cache do solo por ponto (SoilGrids): tabela solo_ponto, uma linha por propriedade

Revision ID: 0007
Revises: 0006
"""
from alembic import op
import sqlalchemy as sa

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'solo_ponto',
        sa.Column('chave', sa.String(length=24), nullable=False),
        sa.Column('propriedade', sa.String(length=12), nullable=False),
        sa.Column('sem_dado', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('superficial', sa.Float(), nullable=True),
        sa.Column('raizes', sa.Float(), nullable=True),
        sa.Column('incerteza_superficial', sa.Float(), nullable=True),
        sa.Column('incerteza_raizes', sa.Float(), nullable=True),
        sa.Column('fonte', sa.String(length=100), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('chave', 'propriedade'),
    )


def downgrade() -> None:
    op.drop_table('solo_ponto')
