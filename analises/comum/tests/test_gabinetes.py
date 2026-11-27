"""L5: a fórmula reproduz o Ipea e as convenções reproduzem a extensão gravada."""
from datetime import date

import pytest

from analises.comum import gabinetes


def test_formula_reproduz_gabinetes_ipea():
    s = gabinetes.serie_proporcionalidade()
    orig = s[s["fonte_serie"] == "ipea_original"]
    assert len(orig) >= 50
    for _, r in orig.iterrows():
        v1, v2 = gabinetes.proporcionalidade(gabinetes.ler_composicao(r["composicao"]))
        assert v1 == pytest.approx(r["prop_v1"], abs=1e-9), r["gabinete"]
        assert v2 == pytest.approx(r["prop_v2"], abs=1e-9), r["gabinete"]


@pytest.mark.dados_reais
def test_convencoes_reproduzem_extensao():
    s = gabinetes.serie_proporcionalidade()
    ext = s[s["fonte_serie"] == "extensao"]
    for _, r in ext.iterrows():
        d = r["inicio"].date()
        v1, v2 = gabinetes.proporcionalidade_na_data(d)
        assert v1 == pytest.approx(r["prop_v1"], abs=1e-6), r["gabinete"]
        a1, _ = gabinetes.proporcionalidade_na_data(d, desembarque=False)
        assert a1 == pytest.approx(r["prop_v1_alt"], abs=1e-6), r["gabinete"]


def test_eventos_lula3_na_base():
    antes = gabinetes.base_na_data(date(2023, 9, 1))
    depois = gabinetes.base_na_data(date(2023, 10, 1))
    assert "PP" not in antes and "PP" in depois
    assert "REPUBLICANOS" not in depois            # convenção Ipea (Sílvio = np)
    assert "REPUBLICANOS" in gabinetes.base_na_data(date(2023, 10, 1), silvio="REPUBLICANOS")
    fora = gabinetes.base_na_data(date(2025, 10, 1))
    assert "UNIÃO" not in fora and "PP" not in fora
    assert "UNIÃO" in gabinetes.base_na_data(date(2026, 1, 15))
    assert "PP" in gabinetes.base_na_data(date(2025, 10, 1), desembarque=False)


def test_uma_pasta_aberta_por_ministerio_no_lula3():
    m = gabinetes.ministros()
    abertos = m[(m["governante"] == "Lula 3") & m["min_fim"].isna()]
    assert abertos["ministerio"].is_unique
