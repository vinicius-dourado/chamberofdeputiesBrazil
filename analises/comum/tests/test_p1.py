"""Integridade do P1 com dados reais (sem olhar nenhum resultado substantivo)."""
import pytest

from analises.comum import p1

pytestmark = pytest.mark.dados_reais


@pytest.fixture(scope="module")
def painel57():
    return p1.carregar_cache(57)


def test_chave_unica(painel57):
    assert not painel57.duplicated(["idVotacao", "deputado_id"]).any()


def test_votos_validos(painel57):
    assert set(painel57["voto"]) <= {"Sim", "Não", "Obstrução", "Abstenção"}


def test_hierarquia_orientacao(painel57):
    f = painel57["fonte_orient_gov"]
    assert set(f) <= {"1_oficial", "2_bancada_governo", "3_lider", "4_vice_lideres", "sem"}
    assert (painel57.loc[f == "sem", "orient_gov"].isna()).all()
    assert (f == "1_oficial").mean() > 0.6


def test_divergente_definido(painel57):
    d = painel57[painel57["divergente"]]
    assert (d["dir_gov"] != d["dir_partido"]).all()
    assert d["dir_gov"].notna().all() and d["dir_partido"].notna().all()


def test_oposicao_fora_da_base(painel57):
    assert not painel57.loc[painel57["linhagem"].isin(["PL", "NOVO"]), "na_base"].any()


def test_concordancia_proxy_lider(painel57):
    """Validação do nível 3: voto do Líder do Governo vs orientação oficial onde as duas existem."""
    import pandas as pd
    from analises.comum.p1 import _lideres_governo, _voto_proxy
    v = painel57[painel57["fonte_orient_gov"] == "1_oficial"]
    lider, _ = _voto_proxy(v.assign(data=pd.to_datetime(v["data"]).dt.strftime("%Y-%m-%d")),
                           _lideres_governo(57))
    o = v.drop_duplicates("idVotacao").set_index("idVotacao")["orient_gov"]
    comum = o.index.intersection(lider.index)
    o, l = o[comum], lider[comum]
    ok = o.isin(["Sim", "Não"]) & l.isin(["Sim", "Não"])
    assert (o[ok] == l[ok]).mean() > 0.95
