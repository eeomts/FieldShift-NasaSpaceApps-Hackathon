from logging.config import fileConfig

from alembic import context

from app import models  # noqa: F401  (registra as tabelas)
from app.db import Base, get_engine

if context.config.config_file_name:
    fileConfig(context.config.config_file_name)

with get_engine().connect() as conn:
    context.configure(connection=conn, target_metadata=Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()
