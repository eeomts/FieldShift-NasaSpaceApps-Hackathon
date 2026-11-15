"""Divisor de markdown em trechos."""
from app.services.rag.chunker import MAX_CARACTERES, dividir_markdown

DOC = """# Glossário

Introdução curta.

## Evapotranspiração

A evapotranspiração é a soma da água que evapora do solo com a que sai pelas folhas das plantas.
Ela mostra quanta água o campo perde para o ar em cada mês.

### Exemplo

```python
# isto é um comentário, não um título
et0 = 4.5
```

Num mês quente e seco, a perda pode passar de 150 mm.

## NDVI

O NDVI mede quão verde e vigorosa está a vegetação. Solo descoberto fica perto de 0,1 a 0,2.

#### Nível 4 não divide

Este título de nível 4 fica dentro do trecho do NDVI, porque só dividimos até o nível 3.
"""


def test_cada_secao_vira_trecho_com_caminho_de_titulos():
    secoes = [t.secao for t in dividir_markdown(DOC)]
    assert "Glossário > Evapotranspiração" in secoes
    assert "Glossário > Evapotranspiração > Exemplo" in secoes
    assert "Glossário > NDVI" in secoes


def test_ordem_e_sequencial():
    trechos = dividir_markdown(DOC)
    assert [t.ordem for t in trechos] == list(range(len(trechos)))


def test_hashtag_dentro_de_codigo_nao_vira_titulo():
    trechos = dividir_markdown(DOC)
    assert all("isto é um comentário" not in t.secao for t in trechos)
    assert any("isto é um comentário" in t.conteudo for t in trechos)


def test_titulo_de_nivel_4_nao_divide():
    ndvi = next(t for t in dividir_markdown(DOC) if t.secao == "Glossário > NDVI")
    assert "#### Nível 4" in ndvi.conteudo


def test_secao_curta_e_juntada_e_nao_some():
    assert any("Introdução curta." in t.conteudo for t in dividir_markdown(DOC))


def _doc_longo(n: int = 12) -> str:
    return "## Seção longa\n\n" + "\n\n".join(f"Parágrafo {i}: " + "texto " * 60 for i in range(n))


def test_secao_grande_respeita_o_limite_de_tamanho():
    trechos = dividir_markdown(_doc_longo())
    assert len(trechos) > 1
    assert all(len(t.conteudo) <= MAX_CARACTERES + 50 for t in trechos)
    assert all(t.secao == "Seção longa" for t in trechos)


def test_secao_quebrada_repete_o_ultimo_paragrafo_no_trecho_seguinte():
    trechos = dividir_markdown(_doc_longo())
    for anterior, seguinte in zip(trechos, trechos[1:]):
        assert seguinte.conteudo.startswith(anterior.conteudo.split("\n\n")[-1])


def test_paragrafo_unico_gigante_e_partido_por_linhas():
    linhas = "\n".join(f"- item {i}: " + "palavra " * 30 for i in range(30))
    trechos = dividir_markdown(f"## Lista\n\n{linhas}")
    assert len(trechos) > 1
    assert all(len(t.conteudo) <= MAX_CARACTERES + 50 for t in trechos)
