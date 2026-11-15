from app.services.onboarding.perfil import calcula_papel, calcula_perfil, meses_sem_cobertura, proximos_passos, retrato_solo
from app.schemas.onboarding import ItemCalendario, Respostas


LAUDO = dict(q12_analise="sim", q12_tem_resultado="sim", q12_laudo={"ph_agua": 5.2, "argila_pct": 42})


def test_papel_e_independente_do_perfil():
    tecnico_com_laudo = Respostas(q1_quem="tecnico", **LAUDO)
    assert calcula_papel(tecnico_com_laudo) == "tecnico"
    assert calcula_perfil(tecnico_com_laudo) == "C"
    assert calcula_papel(Respostas(q1_quem="tecnico")) == "tecnico"
    assert calcula_perfil(Respostas(q1_quem="tecnico")) == "A"
    assert calcula_papel(Respostas()) == "produtor"


def test_regras_do_perfil():
    assert calcula_perfil(Respostas(**LAUDO)) == "C"
    assert calcula_perfil(Respostas(q12_analise="sim", q12_tem_resultado="nao")) == "A"
    assert calcula_perfil(Respostas(q13_textura="argilosa")) == "B"
    cinco = dict(q14_encharca="nao", q15_casca="sim", q16_erosao="sim", q17_dura="nao", q18_minhocas="sim")
    assert calcula_perfil(Respostas(**cinco)) == "B"
    assert calcula_perfil(Respostas(**(cinco | {"q18_minhocas": "nao_sei"}))) == "A"
    # cor + jeito da pergunta 19 contam como uma observação
    quatro_mais_figuras = (cinco | {"q18_minhocas": "nao_sei"}) | dict(q19_cor="vermelha", q19_jeito="gruda")
    assert calcula_perfil(Respostas(**quatro_mais_figuras)) == "B"
    assert calcula_perfil(Respostas()) == "A"


def test_perfil_c_exige_valores_do_laudo():
    so_diz_que_tem = Respostas(q12_analise="sim", q12_tem_resultado="sim")
    assert calcula_perfil(so_diz_que_tem) == "A"
    assert proximos_passos(so_diz_que_tem)[0]["id"] == "valores_laudo"
    um_valor = Respostas(q12_analise="sim", q12_tem_resultado="sim", q12_laudo={"ph_agua": 5.2})
    assert calcula_perfil(um_valor) == "A"
    assert calcula_perfil(Respostas(**LAUDO)) == "C"


def test_laudo_entra_no_retrato_com_confianca_alta():
    r = Respostas(**(LAUDO | {"q12_laudo": {"ph_agua": 5.2, "argila_pct": 42, "fosforo_mg_dm3": 8,
                                            "materia_organica_g_dm3": 25}}))
    do_laudo = {i["atributo"]: i for i in retrato_solo(r)["indicadores"] if i["fonte"] == "laudo"}
    assert do_laudo["textura"]["valor"] == "argilosa" and do_laudo["textura"]["numero"] == 42
    assert do_laudo["acidez"]["valor"] == "media"
    assert do_laudo["materia_organica"]["valor"] == "media"
    assert do_laudo["fosforo"]["valor"] == "informado"  # sem classe: depende da textura e do extrator
    assert do_laudo["textura"]["texto"] == "Argila: 42 % (laudo)"
    assert all(i["confianca"] == "alta" for i in do_laudo.values())
    # com a argila no laudo, não sugere o teste do tato
    assert "teste_tato" not in [p["id"] for p in proximos_passos(r)]


def test_retrato_do_solo_tem_valores_padronizados_para_o_motor():
    retrato = retrato_solo(Respostas(q13_textura="argilosa", q14_encharca="sim", q18_minhocas="nao",
                                     q19_cor="cinza", q19_jeito="gruda"))
    por_origem = {i["origem"]: i for i in retrato["indicadores"]}
    assert por_origem["q14_encharca"]["atributo"] == "drenagem"
    assert por_origem["q14_encharca"]["valor"] == "ruim"
    assert por_origem["q14_encharca"]["texto"] == "Água fica empoçada mais de um dia"
    assert por_origem["q18_minhocas"]["valor"] == "baixa"
    assert por_origem["q13_textura"]["valor"] == "argilosa"
    assert all(i["fonte"] == "produtor" for i in retrato["indicadores"])

    figuras = retrato["figuras"]
    assert figuras["leitura"].startswith("Argilosa com drenagem ruim")
    assert {(a["atributo"], a["valor"]) for a in figuras["atributos"]} == {("drenagem", "ruim"), ("textura", "argilosa")}
    assert all(a["confianca"] == "baixa" for a in figuras["atributos"])


def test_figura_so_com_cor_ou_nao_sei():
    so_cor = retrato_solo(Respostas(q19_cor="escura", q19_jeito="nao_sei"))["figuras"]
    assert so_cor["jeito"] is None and so_cor["leitura"] == "Mais matéria orgânica"
    assert so_cor["atributos"] == [{"atributo": "materia_organica", "valor": "alta", "texto": None,
                                    "fonte": "produtor", "origem": "q19_cor", "confianca": "baixa",
                                    "numero": None}]
    assert retrato_solo(Respostas(q19_cor="nao_sei"))["figuras"] is None


def test_perguntas_de_manejo_nao_contam_como_conhecimento_do_solo():
    # 3 observações + 3 respostas de manejo ("nunca fiz análise", "nunca usei calcário", "não uso adubo")
    manejo = dict(q12_analise="nao", q21_calcario="nao", q22_adubo="nao",
                  q14_encharca="sim", q15_casca="nao", q16_erosao="sim")
    assert calcula_perfil(Respostas(**manejo)) == "A"


def test_meses_sem_cobertura_com_virada_de_ano_e_perene():
    soja = ItemCalendario(cultura_id="soja", texto_original="soja", inicio_mes=11, fim_mes=3)
    assert meses_sem_cobertura([soja]) == [4, 5, 6, 7, 8, 9, 10]
    capim = ItemCalendario(cultura_id="pastagem", texto_original="capim", perene=True)
    assert meses_sem_cobertura([soja, capim]) == []
    assert meses_sem_cobertura([]) == []
