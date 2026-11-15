"""base do RAG: extensão vector, documento, trecho e busca_log

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table(
        'documento',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('fonte', sa.String(length=200), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('licenca', sa.String(length=60), nullable=True),
        sa.Column('idioma', sa.String(length=5), nullable=False, server_default='pt'),
        sa.Column('caminho_origem', sa.String(length=300), nullable=False),
        sa.Column('hash_conteudo', sa.String(length=64), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('caminho_origem', name='uq_documento_caminho_origem'),
    )
    op.create_index('ix_documento_tipo', 'documento', ['tipo'])

    op.create_table(
        'trecho',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('documento_id', sa.Integer(), sa.ForeignKey('documento.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=False),
        sa.Column('secao', sa.String(length=300), nullable=True),
        sa.Column('conteudo', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=False),
        sa.Column(
            'tsv',
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('portuguese'::regconfig, coalesce(secao,'') || ' ' || conteudo)", persisted=True),
        ),
        sa.Column('tokens', sa.Integer(), nullable=True),
        sa.Column('metadados', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index('ix_trecho_documento_id', 'trecho', ['documento_id'])
    op.create_index(
        'ix_trecho_embedding_hnsw', 'trecho', ['embedding'],
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'embedding': 'vector_cosine_ops'},
    )
    op.create_index('ix_trecho_tsv', 'trecho', ['tsv'], postgresql_using='gin')
    op.create_index('ix_trecho_metadados', 'trecho', ['metadados'], postgresql_using='gin')

    # conversa_id entra no PR da conversa, junto com a tabela conversa.
    op.create_table(
        'busca_log',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('expressao_original', sa.Text(), nullable=True),
        sa.Column('consulta', sa.Text(), nullable=False),
        sa.Column('filtros', postgresql.JSONB(), nullable=True),
        sa.Column('trechos_ids', postgresql.ARRAY(sa.Integer()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('notas', postgresql.ARRAY(sa.Float()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('descartados', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('criada_em', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('busca_log')
    op.drop_index('ix_trecho_metadados', table_name='trecho')
    op.drop_index('ix_trecho_tsv', table_name='trecho')
    op.drop_index('ix_trecho_embedding_hnsw', table_name='trecho')
    op.drop_index('ix_trecho_documento_id', table_name='trecho')
    op.drop_table('trecho')
    op.drop_index('ix_documento_tipo', table_name='documento')
    op.drop_table('documento')
    op.execute('DROP EXTENSION IF EXISTS vector')
