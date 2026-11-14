from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import Usuario

_hasher = PasswordHasher()
_bearer = HTTPBearer(auto_error=False)
# Usado para gastar o mesmo tempo quando o e-mail não existe (não revela quais contas existem).
_DUMMY_HASH = _hasher.hash("senha-que-nao-existe")


def hash_senha(senha: str) -> str:
    return _hasher.hash(senha)


def confere_senha(senha_hash: str | None, senha: str) -> bool:
    try:
        return _hasher.verify(senha_hash or _DUMMY_HASH, senha) and senha_hash is not None
    except (VerifyMismatchError, InvalidHashError):
        return False


def cria_token(usuario_id: UUID) -> str:
    s = get_settings()
    agora = datetime.now(UTC)
    payload = {"sub": str(usuario_id), "iat": agora, "exp": agora + timedelta(minutes=s.jwt_expires_min)}
    return jwt.encode(payload, s.jwt_secret, algorithm="HS256")


def usuario_atual(
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    erro = HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessão expirada. Entre de novo.", headers={"WWW-Authenticate": "Bearer"})
    if cred is None:
        raise erro
    try:
        payload = jwt.decode(cred.credentials, get_settings().jwt_secret, algorithms=["HS256"])
        usuario = db.get(Usuario, UUID(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise erro from None
    if usuario is None:
        raise erro
    return usuario
