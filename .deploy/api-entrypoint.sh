#!/bin/sh
# Aplica as migrations pendentes antes de servir; se falhar, o container cai e o restart tenta de novo.

set -eu

alembic upgrade head

exec "$@"
