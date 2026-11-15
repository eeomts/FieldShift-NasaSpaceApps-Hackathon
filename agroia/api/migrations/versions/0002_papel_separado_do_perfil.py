"""papel (quem respondeu) separado do perfil (nível de dado)

O perfil D ("técnico") deixa de existir: quem respondeu vai para a coluna `papel`,
e o perfil passa a ser só o nível de dado sobre o solo (A, B ou C).

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('fazenda', sa.Column('papel', sa.String(length=10), nullable=True))
    op.execute(
        "UPDATE fazenda SET papel = CASE WHEN respostas->>'q1_quem' = 'tecnico' THEN 'tecnico' ELSE 'produtor' END"
    )
    # Fazendas que estavam como D: o perfil é recalculado no próximo salvamento do questionário.
    op.execute("UPDATE fazenda SET perfil = NULL WHERE perfil = 'D'")
    op.drop_constraint('ck_fazenda_perfil', 'fazenda', type_='check')
    op.create_check_constraint('ck_fazenda_perfil', 'fazenda', "perfil IS NULL OR perfil IN ('A','B','C')")
    op.create_check_constraint('ck_fazenda_papel', 'fazenda', "papel IS NULL OR papel IN ('produtor','tecnico')")


def downgrade() -> None:
    op.drop_constraint('ck_fazenda_papel', 'fazenda', type_='check')
    op.drop_constraint('ck_fazenda_perfil', 'fazenda', type_='check')
    op.execute("UPDATE fazenda SET perfil = 'D' WHERE papel = 'tecnico'")
    op.create_check_constraint('ck_fazenda_perfil', 'fazenda', "perfil IS NULL OR perfil IN ('A','B','C','D')")
    op.drop_column('fazenda', 'papel')
