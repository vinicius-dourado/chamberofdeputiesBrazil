"""6-c.2a: integridade dos painéis e recuperação de efeito sintético com atribuição por partido.
Nenhum teste calcula desfechos com dados reais."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paineis as P  # noqa: E402

from analises.comum import estimacao as E  # noqa: E402


@pytest.fixture(scope="module")
def p1_57():
    from analises.comum import p1
    pa = p1.carregar_cache(57)
    pa["data"] = pd.to_datetime(pa["data"]).dt.date
    return pa


@pytest.mark.dados_reais
@pytest.mark.parametrize("ev", list(P.EVENTOS))
def test_painel_evento(p1_57, ev):
    e = P.EVENTOS[ev]
    d = P.montar(p1_57, ev)
    assert set(d["linhagem"]) <= e["tratados"] | e["controles"]
    assert d["data"].between(e["inicio"], e["fim"]).all()
    assert set(d["fonte_orient_gov"]) <= P.NIVEIS_PRINCIPAIS
    assert d["deputado_id"].isin(P.trocadores(p1_57, e["inicio"], e["fim"])).sum() == 0
    # os dois lados do choque e os dois grupos têm observações
    assert d.groupby(["tratado", "pos"]).size().shape[0] == 4
    assert set(d["y1"].dropna().unique()) <= {0.0, 1.0}


@pytest.mark.dados_reais
def test_pos_coerente_com_mes_rel(p1_57):
    d = P.montar(p1_57, "A")
    assert ((d["mes_rel"] >= 0) == (d["pos"] == 1)).all()


def test_did_recupera_efeito_atribuido_por_partido():
    """Atribuição por partido (5 partidos, como no evento A) com choque comum de votação."""
    rng = np.random.default_rng(1)
    partidos = {"PP": 1, "REPUBLICANOS": 1, "MDB": 0, "PSD": 0, "UNIÃO": 0}
    dep = pd.DataFrame([(f"{p}{i}", p, t) for p, t in partidos.items() for i in range(40)],
                       columns=["deputado_id", "linhagem", "tratado"])
    dep["a"] = rng.normal(0.7, 0.08, len(dep))
    vot = pd.DataFrame({"idVotacao": [f"v{j}" for j in range(150)], "t": range(150)})
    vot["g"] = rng.normal(0, 0.1, 150)
    d = dep.merge(vot, how="cross")
    d["pos"] = (d["t"] >= 75).astype(float)
    d["tratado_pos"] = d["tratado"] * d["pos"]
    d["y1"] = (rng.uniform(size=len(d)) < (d["a"] + d["g"] + 0.08 * d["tratado_pos"]).clip(0, 1)).astype(float)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import estimacao as M
    m = M.did(d)
    assert abs(m.coef()["tratado_pos"] - 0.08) < 3 * m.se()["tratado_pos"]


def test_placebo_pvalor():
    r = E.inferencia_placebo_datas(lambda x: x, [0.01, -0.02, 0.5, 0.03], 0.2)
    assert r["p_valor"] == pytest.approx(2 / 5)
