"""Erros de negócio esperados (e-mail repetido, fazenda inexistente...).

Os services lançam `ErroDeNegocio` sem saber de HTTP; o `main.py` transforma em resposta
`{"detail": mensagem}` com o status indicado, o mesmo formato do `HTTPException` do FastAPI.
"""


class ErroDeNegocio(Exception):
    def __init__(self, status_code: int, mensagem: str):
        super().__init__(mensagem)
        self.status_code = status_code
        self.mensagem = mensagem
