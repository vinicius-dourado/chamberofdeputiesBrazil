import pytest

from analises.comum import tse

pytestmark = pytest.mark.dados_reais


def test_ligacao_deputados_2022():
    _, taxa = tse.deputados_tse(57, 2022)
    assert taxa > 0.75          # suplentes efetivados de outras eleições não ligam; relatar a taxa


def test_pesos_somam_um():
    w, _ = tse.pesos_municipais(57, 2022)
    s = w.groupby("deputado_id")["peso"].sum()
    assert ((s - 1).abs() < 1e-9).all()


def test_codigo_municipio_comum():
    w, _ = tse.pesos_municipais(57, 2022)
    pref = tse.prefeitos_eleitos(2024)
    w = w[~w["SG_UF"].isin(["ZZ", "DF"])]        # exterior e DF não têm prefeito
    cobertura = w.loc[w["CD_MUNICIPIO"].isin(pref["CD_MUNICIPIO"]), "peso"].sum() / w["peso"].sum()
    assert cobertura > 0.995


def test_um_prefeito_por_municipio():
    for ano in (2008, 2012, 2016, 2020, 2024):
        assert tse.prefeitos_eleitos(ano)["CD_MUNICIPIO"].is_unique
