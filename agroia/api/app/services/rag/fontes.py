"""Documentos que entram na base de conhecimento (caminhos relativos à raiz do repositório)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Fonte:
    caminho: str
    titulo: str
    tipo: str  # glossario | metodologia | cultura | satelite
    fonte: str | None = None
    url: str | None = None
    licenca: str | None = None
    idioma: str = "pt"


# Só conhecimento para o produtor. Documentação técnica de API não entra: enche o contexto do agente.
FONTES: list[Fonte] = [
    Fonte(
        caminho="docs/NasaSpaceApps-FieldShift/v1/.md/glossario-cientifico-ampliado-field-shift-brasil.md",
        titulo="Glossário científico do Field Shift",
        tipo="glossario",
        fonte="Equipe Field Shift",
        licenca="interna",
    ),
    # Os quatro abaixo ainda serão escritos (ver data/rag/README.md); a ingestão pula o que não existe.
    Fonte(
        caminho="data/rag/glossario-produtor.md",
        titulo="Glossário para o produtor",
        tipo="glossario",
        fonte="Equipe Field Shift",
        licenca="interna",
    ),
    Fonte(
        caminho="data/rag/metodologia-indicadores.md",
        titulo="Como cada indicador é calculado",
        tipo="metodologia",
        fonte="Equipe Field Shift",
        licenca="interna",
    ),
    Fonte(
        caminho="data/rag/o-que-mede-cada-satelite.md",
        titulo="O que mede cada satélite",
        tipo="satelite",
        fonte="Equipe Field Shift",
        licenca="interna",
    ),
    Fonte(
        caminho="data/rag/fichas-culturas.md",
        titulo="Fichas das culturas",
        tipo="cultura",
        fonte="Equipe Field Shift",
        licenca="interna",
    ),
]
