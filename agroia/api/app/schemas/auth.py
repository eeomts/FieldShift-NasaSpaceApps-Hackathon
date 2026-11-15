"""Entrada e saída das rotas de login e conta (≈ FormRequest + Resource)."""
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class Cadastro(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    idioma: Literal["pt", "en", "es"] = "pt"


class Login(BaseModel):
    email: EmailStr
    senha: str = Field(max_length=128)


class UsuarioOut(BaseModel):
    id: str
    nome: str
    email: str
    idioma: str
    onboarding_concluido: bool


class Token(BaseModel):
    token: str
    usuario: UsuarioOut
