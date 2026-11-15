"""Erro de negócio lançado pelos services e convertido em resposta HTTP no main.py."""


class ErroDeNegocio(Exception):
    def __init__(self, status_code: int, mensagem: str):
        super().__init__(mensagem)
        self.status_code = status_code
        self.mensagem = mensagem
