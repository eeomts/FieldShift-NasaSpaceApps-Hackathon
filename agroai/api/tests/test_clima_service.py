"""Serviço do clima contra o Postgres de teste, com um cliente do POWER falso (sem rede)."""
from datetime import date, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_engine
from app.core.erros import ErroDeNegocio
from app.repositories.clima_repository import ClimaRepository
from app.services.clima.agregacao import LinhaMensal
from app.services.clima.clima_service import FONTE, ClimaService, media_por_mes
from app.services.integracao.nasa_power import DiaPower, SeriePower


class ClienteFalso:
    """Série sintética de 1991 até o fim pedido: chuva em dias alternados, 1 de janeiro de cada ano sem dado."""

    def __init__(self):
        self.chamadas: list[tuple[float, float, date, date]] = []

    def serie_diaria(self, lat, lon, inicio, fim) -> SeriePower:
        self.chamadas.append((lat, lon, inicio, fim))
        dias, d = [], inicio
        while d <= fim:
            sem_dado = d.month == 1 and d.day == 1
            dias.append(
                DiaPower(
                    data=d,
                    t2m=None if sem_dado else 22.0,
                    tmax=None if sem_dado else 30.0,
                    tmin=None if sem_dado else 15.0,
                    chuva=None if sem_dado else (12.0 if d.toordinal() % 2 else 0.0),
                    ur=70.0,
                    radiacao=20.0,
                    vento=2.0,
                )
            )
            d += timedelta(days=1)
        return SeriePower(lat=lat, lon=lon, elevacao_m=800.0, dias=dias)


@pytest.fixture
def db():
    with Session(get_engine(), expire_on_commit=False) as s:
        yield s


def servico(db) -> tuple[ClimaService, ClienteFalso]:
    cliente = ClienteFalso()
    return ClimaService(ClimaRepository(db), cliente), cliente


HOJE = date(2026, 11, 14)


def test_primeira_chamada_baixa_e_guarda(db):
    s, cliente = servico(db)
    celula = s.obter(-11.314537, -41.814958, hoje=HOJE)
    assert len(cliente.chamadas) == 1
    assert cliente.chamadas[0] == (-11.5, -41.875, date(1991, 1, 1), date(2025, 12, 31))  # pelo centro da célula
    assert celula.id == "-11.5_-41.875"
    assert (celula.lat, celula.lon, celula.elevacao_m) == (-11.5, -41.875, 800.0)
    assert (celula.inicio, celula.fim, celula.fonte) == (date(1991, 1, 1), date(2025, 12, 31), FONTE)
    assert celula.limite_chuva_forte_mm == 12.0
    assert len(ClimaRepository(db).meses(celula.id)) == 35 * 12


def test_segunda_chamada_usa_o_cache(db):
    s, cliente = servico(db)
    s.obter(-11.314537, -41.814958, hoje=HOJE)
    s.obter(-11.314537, -41.814958, hoje=HOJE)
    s.obter(-11.4, -41.7, hoje=HOJE)  # vizinho na mesma célula
    assert len(cliente.chamadas) == 1


def test_ano_novo_baixa_de_novo_so_quando_falta_o_ultimo_ano(db):
    s, cliente = servico(db)
    s.obter(-11.3, -41.8, hoje=HOJE)
    celula = s.obter(-11.3, -41.8, hoje=date(2027, 2, 1))
    assert len(cliente.chamadas) == 2
    assert celula.fim == date(2026, 12, 31)
    assert len(ClimaRepository(db).meses(celula.id)) == 36 * 12  # atualiza sem duplicar


def test_coordenada_fora_do_mundo_e_recusada(db):
    s, cliente = servico(db)
    with pytest.raises(ErroDeNegocio):
        s.obter(95.0, 0.0, hoje=HOJE)
    with pytest.raises(ErroDeNegocio):
        s.obter(0.0, 200.0, hoje=HOJE)
    assert cliente.chamadas == []


def test_climatologia_leva_fonte_e_periodo(db):
    s, _ = servico(db)
    c = s.climatologia(s.obter(-11.3, -41.8, hoje=HOJE))
    assert c.periodo == "1991–2020"
    assert "NASA POWER" in c.fonte and "1991–2020" in c.fonte and "-11.5, -41.875" in c.fonte
    assert len(c.meses) == 12
    jan = c.meses[0]
    assert jan.anos_com_dado == 30  # só 1991-2020 entram, não 2021-2025
    assert jan.tmax_media_c == 30.0
    assert jan.dias_geada == 0.0  # tmin 15: zero real (há dado), não ausente
    assert c.limite_chuva_forte_mm == 12.0
    assert any("FAO-56" in n for n in c.notas)


def test_agregacao_grava_gd_por_tb(db):
    s, _ = servico(db)
    c = s.obter(-11.3, -41.8, hoje=HOJE)
    meses = {(m.ano, m.mes): m for m in s.repositorio.meses(c.id)}
    fev = meses[(2024, 2)].gd_por_tb  # 29 dias, Tmed = (30 + 15) / 2 = 22,5
    assert sorted(map(int, fev)) == list(range(0, 21))
    assert fev["10"] == pytest.approx(29 * 12.5) and fev["0"] == pytest.approx(29 * 22.5)
    assert fev["20"] == pytest.approx(29 * 2.5)
    # 1 de janeiro sem temperatura: o mês fica {} (nem soma parcial, nem NULL)
    assert meses[(2024, 1)].gd_por_tb == {}


def test_celula_sem_gd_por_tb_e_baixada_de_novo(db):
    s, cliente = servico(db)
    celula = s.obter(-11.3, -41.8, hoje=HOJE)
    s.obter(-11.3, -41.8, hoje=HOJE)
    assert len(cliente.chamadas) == 1
    db.execute(text("UPDATE clima_mensal SET gd_por_tb = NULL WHERE celula_id = :c AND ano = 2000"), {"c": celula.id})
    db.commit()
    s.obter(-11.3, -41.8, hoje=HOJE)
    assert len(cliente.chamadas) == 2
    assert all(m.gd_por_tb is not None for m in s.repositorio.meses(celula.id))
    s.obter(-11.3, -41.8, hoje=HOJE)
    assert len(cliente.chamadas) == 2


def test_agregacao_grava_tmin_diaria(db):
    s, _ = servico(db)
    c = s.obter(-11.3, -41.8, hoje=HOJE)
    meses = {(m.ano, m.mes): m for m in s.repositorio.meses(c.id)}
    jan, fev = meses[(2024, 1)].tmin_diaria, meses[(2024, 2)].tmin_diaria
    assert len(jan) == 31 and jan[0] is None and jan[1:] == [15.0] * 30  # 1 de janeiro sem dado: null
    assert len(fev) == 29 and fev == [15.0] * 29
    assert len(meses[(2023, 2)].tmin_diaria) == 28
    linhas = s.linhas(c)
    assert linhas[0].tmin_diaria == meses[(1991, 1)].tmin_diaria


def test_celula_sem_tmin_diaria_e_baixada_de_novo(db):
    s, cliente = servico(db)
    celula = s.obter(-11.3, -41.8, hoje=HOJE)
    s.obter(-11.3, -41.8, hoje=HOJE)
    assert len(cliente.chamadas) == 1
    db.execute(text("UPDATE clima_mensal SET tmin_diaria = NULL WHERE celula_id = :c AND ano = 2000 AND mes = 3"), {"c": celula.id})
    db.commit()
    assert s.repositorio.faltam_graus_dia(celula.id)
    s.obter(-11.3, -41.8, hoje=HOJE)
    assert len(cliente.chamadas) == 2
    assert all(m.tmin_diaria is not None for m in s.repositorio.meses(celula.id))
    s.obter(-11.3, -41.8, hoje=HOJE)
    assert len(cliente.chamadas) == 2


def test_ano_leva_fonte_e_periodo(db):
    s, _ = servico(db)
    a = s.ano(s.obter(-11.3, -41.8, hoje=HOJE), 2024)
    assert a.periodo == "2024" and "2024" in a.fonte and "NASA POWER" in a.fonte
    assert [m.mes for m in a.meses] == list(range(1, 13))


CAMPOS_VAZIOS = (
    "chuva_mm", "et0_mm", "tmed_c", "tmax_media_c", "tmin_media_c", "tmax_absoluta_c", "tmin_absoluta_c",
    "dias_geada", "dias_calor", "dias_chuva_forte", "maior_seq_seca_dias",
)  # fmt: skip


def linha(ano, mes, **kw) -> LinhaMensal:
    return LinhaMensal(ano=ano, mes=mes, dias_validos=0, **(dict.fromkeys(CAMPOS_VAZIOS) | kw))


def test_media_por_mes_ignora_ausente_e_mantem_none_sem_dado():
    linhas = [
        linha(2000, 1, chuva_mm=100.0, tmax_absoluta_c=36.0, dias_geada=0),
        linha(2001, 1, chuva_mm=50.0, tmax_absoluta_c=39.0, dias_geada=2),
        linha(2002, 1),  # ano sem dado: não puxa a média para baixo
        linha(2025, 1, chuva_mm=900.0),  # fora de 1991-2020
    ]
    jan, fev = media_por_mes(linhas)[:2]
    assert jan.chuva_mm == 75.0
    assert jan.dias_geada == 1.0
    assert jan.tmax_absoluta_c == 39.0  # extremo do período, não média
    assert jan.anos_com_dado == 2
    assert jan.et0_mm is None
    assert fev.chuva_mm is None and fev.anos_com_dado == 0
