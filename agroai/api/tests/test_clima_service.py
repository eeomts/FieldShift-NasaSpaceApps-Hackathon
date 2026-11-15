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


# --- série diária de Tmin/Tmax (clima_serie_diaria)
class ClienteComFalhas(ClienteFalso):
    """Como o falso, com tmin 15,3 e buracos: 4 de julho de 2010 sem Tmin, 29 de fevereiro de 2000 sem Tmax."""

    def serie_diaria(self, lat, lon, inicio, fim):
        serie = super().serie_diaria(lat, lon, inicio, fim)
        for d in serie.dias:
            if d.tmin is not None:
                d.tmin = 15.3
            if d.data == date(2010, 7, 4):
                d.tmin = None
            if d.data == date(2000, 2, 29):
                d.tmax = None
        return serie


def test_download_grava_a_serie_diaria_de_todos_os_anos_com_bissexto(db):
    s, _ = servico(db)
    celula = s.obter(-11.3, -41.8, hoje=HOJE)
    series = s.series_diarias(celula)
    assert sorted(series) == list(range(1991, 2026))
    assert len(series[2000].tmin_c) == len(series[2000].tmax_c) == 366  # bissexto
    assert len(series[1999].tmin_c) == len(series[2025].tmax_c) == 365
    assert series[2024].tmin_c[59] == 15.0 and series[2024].tmax_c[59] == 30.0  # 29 de fevereiro de 2024
    assert series[2023].tmin_c[59] == 15.0  # 1º de março: índice 59 em ano comum
    assert [x.ano for x in ClimaRepository(db).series_diarias(celula.id)] == list(range(1991, 2026))


def test_serie_diaria_guarda_nulo_onde_o_power_nao_deu_dado_e_nunca_zero(db):
    s, _ = servico(db)
    series = s.series_diarias(s.obter(-11.3, -41.8, hoje=HOJE))
    assert series[2010].tmin_c[0] is None and series[2010].tmax_c[0] is None  # 1º de janeiro sem dado (cliente falso)
    assert 0 not in series[2010].tmin_c and 0 not in series[2010].tmax_c


def test_serie_diaria_buracos_isolados_e_valor_real_volta_arredondado(db):
    cliente = ClienteComFalhas()
    s = ClimaService(ClimaRepository(db), cliente)
    series = s.series_diarias(s.obter(-11.3, -41.8, hoje=HOJE))
    julho_4 = date(2010, 7, 4).timetuple().tm_yday - 1
    assert series[2010].tmin_c[julho_4] is None and series[2010].tmax_c[julho_4] == 30.0  # só a Tmin falta
    assert series[2000].tmax_c[59] is None and series[2000].tmin_c[59] == 15.3  # só a Tmax falta
    assert series[2010].tmin_c[julho_4 + 1] == 15.3  # REAL de 4 bytes, de volta a 2 casas (15,3 e não 15,300000190734863)


def test_celula_baixada_antes_da_tabela_baixa_de_novo_uma_vez_e_grava_a_serie(db, caplog):
    s, cliente = servico(db)
    celula = s.obter(-11.3, -41.8, hoje=HOJE)
    db.execute(text("DELETE FROM clima_serie_diaria WHERE celula_id = :c"), {"c": celula.id})  # como uma célula antiga
    db.commit()
    assert s.repositorio.faltam_serie_diaria(celula)
    with caplog.at_level("INFO"):
        s.obter(-11.3, -41.8, hoje=HOJE)
    assert len(cliente.chamadas) == 2 and "sem a série diária" in caplog.text
    assert len(s.series_diarias(celula)) == 35 and not s.repositorio.faltam_serie_diaria(celula)
    s.obter(-11.3, -41.8, hoje=HOJE)
    assert len(cliente.chamadas) == 2  # só uma vez
    assert len(s.repositorio.meses(celula.id)) == 35 * 12  # os meses seguem sem duplicar


def test_ano_faltando_na_serie_diaria_nao_dispara_novo_download(db):
    s, cliente = servico(db)
    celula = s.obter(-11.3, -41.8, hoje=HOJE)
    db.execute(text("DELETE FROM clima_serie_diaria WHERE celula_id = :c AND ano = 2005"), {"c": celula.id})
    db.commit()
    assert not s.repositorio.faltam_serie_diaria(celula)  # só a célula sem nenhuma linha conta como antiga
    s.obter(-11.3, -41.8, hoje=HOJE)
    assert len(cliente.chamadas) == 1 and 2005 not in s.series_diarias(celula)  # não baixa de novo a cada análise


def test_ano_novo_acrescenta_o_ano_na_serie_sem_duplicar(db):
    s, _ = servico(db)
    celula = s.obter(-11.3, -41.8, hoje=HOJE)
    celula = s.obter(-11.3, -41.8, hoje=date(2027, 2, 1))
    assert sorted(s.series_diarias(celula)) == list(range(1991, 2027))


def test_apagar_a_celula_apaga_a_serie_diaria(db):
    s, _ = servico(db)
    celula = s.obter(-11.3, -41.8, hoje=HOJE)
    db.execute(text("DELETE FROM clima_celula WHERE id = :c"), {"c": celula.id})
    db.commit()
    assert ClimaRepository(db).series_diarias(celula.id) == []


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
