"""usuario, fazenda e calendario

Revision ID: 0001
Revises: 
Create Date: 2026-11-14 18:08:05.352257
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('usuario',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('senha_hash', sa.String(length=255), nullable=False),
    sa.Column('nome', sa.String(length=120), nullable=False),
    sa.Column('idioma', sa.String(length=5), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usuario_email'), 'usuario', ['email'], unique=True)
    op.create_table('fazenda',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('usuario_id', sa.Uuid(), nullable=False),
    sa.Column('lat', sa.Float(), nullable=True),
    sa.Column('lon', sa.Float(), nullable=True),
    sa.Column('nome_local', sa.String(length=200), nullable=True),
    sa.Column('perfil', sa.String(length=1), nullable=True),
    sa.Column('irrigacao', sa.String(length=10), nullable=True),
    sa.Column('animais', sa.Boolean(), nullable=True),
    sa.Column('terreno', sa.String(length=20), nullable=True),
    sa.Column('prioridades', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('culturas_excluidas', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('equipamentos', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('retrato_solo', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('proximos_passos', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('respostas', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('passo_atual', sa.Integer(), nullable=False),
    sa.Column('onboarding_concluido', sa.Boolean(), nullable=False),
    sa.Column('status_processamento', sa.String(length=20), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("perfil IS NULL OR perfil IN ('A','B','C','D')", name='ck_fazenda_perfil'),
    sa.CheckConstraint('lat IS NULL OR (lat BETWEEN -90 AND 90)', name='ck_fazenda_lat'),
    sa.CheckConstraint('lon IS NULL OR (lon BETWEEN -180 AND 180)', name='ck_fazenda_lon'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario_id')
    )
    op.create_table('calendario_item',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('fazenda_id', sa.Uuid(), nullable=False),
    sa.Column('ordem', sa.Integer(), nullable=False),
    sa.Column('cultura_id', sa.String(length=40), nullable=True),
    sa.Column('texto_original', sa.Text(), nullable=False),
    sa.Column('inicio_mes', sa.Integer(), nullable=True),
    sa.Column('fim_mes', sa.Integer(), nullable=True),
    sa.Column('perene', sa.Boolean(), nullable=False),
    sa.Column('consorcio_com', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('ocupa', sa.String(length=10), nullable=True),
    sa.CheckConstraint('fim_mes IS NULL OR fim_mes BETWEEN 1 AND 12', name='ck_cal_fim'),
    sa.CheckConstraint('inicio_mes IS NULL OR inicio_mes BETWEEN 1 AND 12', name='ck_cal_inicio'),
    sa.ForeignKeyConstraint(['fazenda_id'], ['fazenda.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calendario_item_fazenda_id'), 'calendario_item', ['fazenda_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_calendario_item_fazenda_id'), table_name='calendario_item')
    op.drop_table('calendario_item')
    op.drop_table('fazenda')
    op.drop_index(op.f('ix_usuario_email'), table_name='usuario')
    op.drop_table('usuario')
