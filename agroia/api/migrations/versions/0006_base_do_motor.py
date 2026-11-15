"""base do motor: fazenda.pais/codigo_local, clima_mensal.gd_por_tb e relevo_ponto

Revision ID: 0006
Revises: 0005
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('fazenda', sa.Column('pais', sa.String(length=2), nullable=True))
    op.add_column('fazenda', sa.Column('codigo_local', sa.String(length=7), nullable=True))
    op.create_check_constraint('ck_fazenda_pais', 'fazenda', "pais IS NULL OR pais IN ('BR','US')")

    # NULL = célula baixada antes desta coluna; o serviço do clima baixa de novo.
    op.add_column('clima_mensal', sa.Column('gd_por_tb', postgresql.JSONB(none_as_null=True), nullable=True))

    op.create_table(
        'relevo_ponto',
        sa.Column('chave', sa.String(length=24), primary_key=True),
        sa.Column('declividade_pct', sa.Float(), nullable=False),
        sa.Column('classe', sa.String(length=20), nullable=False),
        sa.Column('fonte', sa.String(length=100), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    _preencher_pais_das_fazendas()


def _preencher_pais_das_fazendas() -> None:
    """Fazendas que já têm ponto recebem país e código. Sem as malhas ou o shapely, fica NULL até o próximo salvar."""
    try:
        from app.services.motor.local import pais_e_codigo

        pais_e_codigo(0.0, 0.0)  # carrega as malhas (falha aqui, antes de mexer em linha alguma)
    except (ImportError, OSError) as e:
        print(f"0006: país das fazendas não preenchido ({type(e).__name__}); será preenchido no próximo salvar.")
        return
    conexao = op.get_bind()
    fazendas = conexao.execute(sa.text("SELECT id, lat, lon FROM fazenda WHERE lat IS NOT NULL AND lon IS NOT NULL"))
    for id_, lat, lon in fazendas.fetchall():
        pais, codigo = pais_e_codigo(lat, lon)
        conexao.execute(
            sa.text("UPDATE fazenda SET pais = :p, codigo_local = :c WHERE id = :i"), {"p": pais, "c": codigo, "i": id_}
        )


def downgrade() -> None:
    op.drop_table('relevo_ponto')
    op.drop_column('clima_mensal', 'gd_por_tb')
    op.drop_constraint('ck_fazenda_pais', 'fazenda', type_='check')
    op.drop_column('fazenda', 'codigo_local')
    op.drop_column('fazenda', 'pais')
