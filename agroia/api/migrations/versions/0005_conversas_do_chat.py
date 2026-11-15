"""conversas do chat: conversa, mensagem e busca_log.conversa_id

Revision ID: 0005
Revises: 0004
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'conversa',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('usuario_id', sa.Uuid(), sa.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False),
        sa.Column('titulo', sa.String(length=80), nullable=True),
        sa.Column('criada_em', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('atualizada_em', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_conversa_usuario_id', 'conversa', ['usuario_id'])

    op.create_table(
        'mensagem',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('conversa_id', sa.Integer(), sa.ForeignKey('conversa.id', ondelete='CASCADE'), nullable=False),
        sa.Column('papel', sa.String(length=10), nullable=False),
        sa.Column('conteudo', postgresql.JSONB(), nullable=False),
        sa.Column('visivel', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('texto', sa.Text(), nullable=True),
        sa.Column('fontes', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('ferramentas_usadas', postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('tokens_entrada', sa.Integer(), nullable=True),
        sa.Column('tokens_saida', sa.Integer(), nullable=True),
        sa.Column('criada_em', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("papel IN ('user','model')", name='ck_mensagem_papel'),
    )
    op.create_index('ix_mensagem_conversa_id', 'mensagem', ['conversa_id'])

    # A busca continua registrada se a conversa for apagada (conversa_id vira NULL).
    op.add_column('busca_log', sa.Column('conversa_id', sa.Integer(), nullable=True))
    op.create_foreign_key('busca_log_conversa_id_fkey', 'busca_log', 'conversa', ['conversa_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_busca_log_conversa_id', 'busca_log', ['conversa_id'])


def downgrade() -> None:
    op.drop_index('ix_busca_log_conversa_id', table_name='busca_log')
    op.drop_constraint('busca_log_conversa_id_fkey', 'busca_log', type_='foreignkey')
    op.drop_column('busca_log', 'conversa_id')
    op.drop_index('ix_mensagem_conversa_id', table_name='mensagem')
    op.drop_table('mensagem')
    op.drop_index('ix_conversa_usuario_id', table_name='conversa')
    op.drop_table('conversa')
