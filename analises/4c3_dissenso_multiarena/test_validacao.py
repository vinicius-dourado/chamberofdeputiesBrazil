"""4-c.3: integridade dos indicadores e do índice (sem calcular resultados substantivos)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import paineis as P  # noqa: E402


@pytest.mark.parametrize("ementa,esperado", [
    ("Destaque para Votação em Separado - PL 3796/2004", "PL 3796/2004"),
    ("... ao Projeto de Lei nº 2113, de 2019, com vistas a sua supressão.", "PL 2113/2019"),
    ("Emenda ao PL 2969/22", "PL 2969/2022"),
    ("Destaque de Emenda", None),
])
def test_proposicao_alvo(ementa, esperado):
    assert P.proposicao_alvo(ementa) == esperado


@pytest.fixture(scope="module")
def ind():
    f = AQUI / "cache" / "indicadores_leg57.parquet"
    if not f.exists():
        pytest.skip("rode paineis.py antes")
    return pd.read_parquet(f)


@pytest.mark.dados_reais
def test_ausente_nao_tem_voto(ind):
    aus = ind[ind["i1_ausente"] == 1]
    assert (aus["voto"] == "Ausente").all() and aus["plenario"].all()
    assert not aus.duplicated(["idVotacao", "deputado_id"]).any()
    votou = ind[ind["voto"] != "Ausente"][["idVotacao", "deputado_id"]]
    assert aus.merge(votou, on=["idVotacao", "deputado_id"]).empty


@pytest.mark.dados_reais
def test_indicadores_binarios(ind):
    for c in ("i1_ausente", "i2_obst_abst_contra", "i5_comissao_contra", "defeccao"):
        assert set(ind[c].dropna().unique()) <= {0.0, 1.0}
    assert ind.loc[ind["plenario"], "i5_comissao_contra"].isna().all()


@pytest.mark.dados_reais
def test_taxa_ausencia_plausivel(ind):
    """Ausência entre votações orientadas: entre 3% e 40% (fora disso, a ligação com o exercício falhou)."""
    taxa = ind.loc[ind["plenario"], "i1_ausente"].mean()
    assert 0.03 < taxa < 0.40


def test_indice_sinal_e_padronizacao():
    sys.path.insert(0, str(AQUI))
    import estimacao as M
    rng = np.random.default_rng(3)
    lat = rng.normal(size=300)
    s = pd.DataFrame({c: lat + rng.normal(scale=0.5, size=300) for c in M.COMPONENTES})
    s2, cargas = M.indice(s)
    assert np.corrcoef(s2["indice_media"], lat)[0, 1] > 0.9
    assert all(v > 0 for v in cargas.values())
