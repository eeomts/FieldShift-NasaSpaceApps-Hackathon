"""clima do NASA POWER: clima_celula e clima_mensal

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'clima_celula',
        sa.Column('id', sa.String(length=32), primary_key=True),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('elevacao_m', sa.Float(), nullable=True),
        sa.Column('inicio', sa.Date(), nullable=False),
        sa.Column('fim', sa.Date(), nullable=False),
        sa.Column('limite_chuva_forte_mm', sa.Float(), nullable=True),
        sa.Column('fonte', sa.String(length=100), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'clima_mensal',
        sa.Column('celula_id', sa.String(length=32), sa.ForeignKey('clima_celula.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ano', sa.SmallInteger(), nullable=False),
        sa.Column('mes', sa.SmallInteger(), nullable=False),
        sa.Column('chuva_mm', sa.Float(), nullable=True),
        sa.Column('et0_mm', sa.Float(), nullable=True),
        sa.Column('tmed_c', sa.Float(), nullable=True),
        sa.Column('tmax_media_c', sa.Float(), nullable=True),
        sa.Column('tmin_media_c', sa.Float(), nullable=True),
        sa.Column('tmax_absoluta_c', sa.Float(), nullable=True),
        sa.Column('tmin_absoluta_c', sa.Float(), nullable=True),
        sa.Column('dias_geada', sa.SmallInteger(), nullable=True),
        sa.Column('dias_calor', sa.SmallInteger(), nullable=True),
        sa.Column('dias_chuva_forte', sa.SmallInteger(), nullable=True),
        sa.Column('maior_seq_seca_dias', sa.SmallInteger(), nullable=True),
        sa.Column('dias_validos', sa.SmallInteger(), nullable=True),
        sa.PrimaryKeyConstraint('celula_id', 'ano', 'mes'),
        sa.CheckConstraint('mes BETWEEN 1 AND 12', name='ck_clima_mensal_mes'),
    )


def downgrade() -> None:
    op.drop_table('clima_mensal')
    op.drop_table('clima_celula')
