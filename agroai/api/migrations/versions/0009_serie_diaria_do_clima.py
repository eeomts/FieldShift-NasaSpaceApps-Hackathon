"""serie diaria de Tmin e Tmax do clima: tabela clima_serie_diaria (uma linha por celula e ano)

Substitui a coluna clima_mensal.tmin_diaria (migration 0008), que guardava so a Tmin por mes: a serie diaria
traz a Tmin e a Tmax de todos os dias (regra 17 do frio e o calor por dias seguidos). A coluna e apagada.
Celulas baixadas antes desta migration ficam sem serie diaria; o servico de clima baixa de novo uma vez no proximo uso.
O downgrade recria a coluna vazia (o servico nao a preenche mais) e apaga a tabela.

Revision ID: 0009
Revises: 0008
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0009'
down_revision = '0008'
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
    op.drop_column('clima_mensal', 'tmin_diaria')


def downgrade() -> None:
    op.add_column('clima_mensal', sa.Column('tmin_diaria', postgresql.JSONB(none_as_null=True), nullable=True))
    op.drop_table('clima_serie_diaria')
