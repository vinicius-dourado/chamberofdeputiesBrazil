"""7-c.2: integridade do Δ e dos painéis; recuperação de efeito contínuo sintético."""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paineis as P  # noqa: E402


@pytest.mark.dados_reais
def test_delta_limitado_e_cobertura():
    d, diag = P.delta_alinhamento(P.PRINCIPAL)
    assert d["delta"].between(-1, 1).all()
    assert d[["al_antigo", "al_novo"]].stack().between(0, 1 + 1e-9).all()
    assert diag["cobertura_peso_prefeitos"] > 0.99
    assert diag["taxa_ligacao_tse"] > 0.9


@pytest.mark.dados_reais
def test_base_fixa_na_posse():
    """Com a base fixa, Δ só muda se mudar o prefeito: base vazia dá Δ = 0."""
    d, _ = P.delta_alinhamento(P.PRINCIPAL, base=set())
    assert (d["delta"] == 0).all()


@pytest.mark.dados_reais
def test_mesa_conferida():
    """Fatos usados no PREREG (troca na Presidência da Câmara por réplica)."""
    assert P.presidente_camara_eleito(2017)["troca"] is False
    for ano in (2013, 2021, 2025):
        assert P.presidente_camara_eleito(ano)["troca"] is True


def test_janelas_nao_se_sobrepoem():
    for ano in P.REPLICAS:
        j = P.janelas(ano)
        assert j["pre"][1] < j["transicao"][0] < j["pos"][0] == date(ano, 1, 1)


def test_recupera_efeito_continuo():
    from analises.comum import estimacao as E
    df = E.simular_painel_votos(efeito=0.2, dose_continua=True, semente=7)
    df = df.rename(columns={"dose": "delta", "tratado_pos": "delta_pos", "y": "y1"})
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import estimacao as M
    m = M.did(df)
    assert abs(m.coef()["delta_pos"] - 0.2) < 3 * m.se()["delta_pos"]
