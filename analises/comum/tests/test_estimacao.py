"""O estimador recupera efeitos conhecidos em dados sintéticos (nunca usa dados reais)."""
import pytest

from analises.comum import estimacao as E


@pytest.mark.parametrize("dose_continua", [False, True])
def test_twfe_recupera_efeito(dose_continua):
    df = E.simular_painel_votos(efeito=0.15, dose_continua=dose_continua)
    m = E.feols("y ~ tratado_pos | deputado_id + idVotacao", df)
    b, ep = m.coef()["tratado_pos"], m.se()["tratado_pos"]
    assert abs(b - 0.15) < 3 * ep


def test_placebo_nulo():
    df = E.simular_painel_votos(efeito=0.0)
    m = E.feols("y ~ tratado_pos | deputado_id + idVotacao", df)
    assert abs(m.coef()["tratado_pos"]) < 3 * m.se()["tratado_pos"]


def test_dummies_evento():
    import pandas as pd
    df, nomes = E.dummies_evento(pd.DataFrame({"t": [-5, -1, 0, 3, 9]}), "t", (-3, 3))
    assert "ev_m1" not in nomes and len(nomes) == 6
    assert df.loc[0, "ev_m3"] == 1 and df.loc[4, "ev_p3"] == 1


def test_limpar_nan():
    assert E._limpar({"a": float("nan"), "b": [1.0, float("inf")]}) == {"a": None, "b": [1.0, None]}
