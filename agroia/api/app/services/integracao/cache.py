"""Cache pequeno em memória para consultas externas (só guarda respostas que deram certo)."""
from collections import OrderedDict
from threading import Lock


class CacheLru:
    def __init__(self, tamanho: int = 1000):
        self.tamanho = tamanho
        self._dados: OrderedDict = OrderedDict()
        self._trava = Lock()

    def pegar(self, chave):
        with self._trava:
            if chave not in self._dados:
                return None
            self._dados.move_to_end(chave)
            return self._dados[chave]

    def guardar(self, chave, valor) -> None:
        with self._trava:
            self._dados[chave] = valor
            self._dados.move_to_end(chave)
            while len(self._dados) > self.tamanho:
                self._dados.popitem(last=False)

    def limpar(self) -> None:
        with self._trava:
            self._dados.clear()
