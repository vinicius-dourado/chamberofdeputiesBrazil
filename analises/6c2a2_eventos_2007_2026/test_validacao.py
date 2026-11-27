"""6-c.2a-ii: regras de eventos, integridade do painel empilhado e recuperação de efeitos sintéticos."""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from analises.comum.script import modulo_irmao  # noqa: E402
EV = modulo_irmao(__file__, "eventos")


@pytest.fixture(scope="module")
def todos():
    return EV.classificar()


def test_regras_de_exclusao(todos):
    g = todos.set_index("evento")["grupo"]
    assert g["sai_PCdoB_20111026"] == "excluido_troca_de_ministro"
    assert g["sai_PL_20220331"] == "excluido_desincompatibilizacao"
    assert g["sai_PP_20160413"] == "impeachment_2016"
    assert g["ent_PP_20230913"] == "principal"
    assert (todos["grupo"] == "principal").sum() == 20


def test_janela_nao_cruza_outro_evento_do_partido(todos):
    princ = todos[todos["grupo"] == "principal"]
    for _, ev in princ.iterrows():
        ini, fim = EV.janela(ev, todos)
        assert ini <= ev["data"] <= fim
        outros = princ[(princ["partido"] == ev["partido"]) & (princ["data"] != ev["data"])]["data"]
        assert not any(ini < o <= fim for o in outros if o > ev["data"])


@pytest.fixture(scope="module")
def pilha():
    f = AQUI / "cache" / "pilha.parquet"
    if not f.exists():
        pytest.skip("rode paineis.py antes")
    return pd.read_parquet(f)


@pytest.mark.dados_reais
def test_pilha_integridade(pilha):
    assert not pilha.duplicated(["evento", "idVotacao", "deputado_id"]).any()
    assert ((pilha["ent_pos"] > 0) <= (pilha["tipo_evento"] == "entrada")).all()
    assert ((pilha["sai_pos"] > 0) <= (pilha["tipo_evento"] == "saida")).all()
    for ev, g in pilha.groupby("evento"):
        assert g.loc[g["tratado"] == 1, "linhagem"].nunique() == 1, ev
        assert ((g["mes_rel"] >= 0) == (g["pos"] == 1)).all(), ev
    assert pilha["evento"].nunique() == 17


def test_recupera_efeitos_assimetricos_empilhados():
    """Duas pilhas sintéticas: entrada com +0,10 e saída com -0,03; o estimador separa os dois."""
    M = modulo_irmao(__file__, "estimacao")
    from analises.comum import estimacao as E
    partes = []
    for k, (tipo, ef) in enumerate((("entrada", 0.10), ("saida", -0.03), ("entrada", 0.10), ("saida", -0.03))):
        d = E.simular_painel_votos(efeito=ef, n_dep=80, n_vot=120, t_choque=60, semente=k)
        d["evento"], d["tipo_evento"] = f"e{k}", tipo
        d["tratado"] = d["dose"]
        d["ent_pos"] = d["tratado_pos"] * (tipo == "entrada")
        d["sai_pos"] = d["tratado_pos"] * (tipo == "saida")
        d["dep_stack"], d["vot_stack"] = d["deputado_id"] + f"|e{k}", d["idVotacao"] + f"|e{k}"
        d["deputado_id"] = d["deputado_id"] + f"_{k}"
        d["y1"] = d["y"]
        partes.append(d)
    m = M.principal(pd.concat(partes, ignore_index=True))
    assert abs(m.coef()["ent_pos"] - 0.10) < 3 * m.se()["ent_pos"]
    assert abs(m.coef()["sai_pos"] + 0.03) < 3 * m.se()["sai_pos"]
    s = M.simetria(m)
    assert s["ic95"][0] < s["soma"] < s["ic95"][1]


def test_p_placebo():
    M = modulo_irmao(__file__, "estimacao")
    r = M.p_placebo(np.array([0.01, -0.2, np.nan, 0.05]), 0.1)
    assert r["n_placebos"] == 3 and r["p_valor"] == pytest.approx(2 / 4)
