import pytest

from analises.comum import config


def test_choque_nao_verificado_recusado():
    with pytest.raises(ValueError):
        config.choque("stf_suspende_emendas")
    assert config.choque("stf_suspende_emendas", permitir_nao_verificado=True).year == 2024
    assert config.choque("entrada_pp_rep").month == 9


def test_governo_e_legislatura():
    from datetime import date
    assert config.governo_na_data(date(2016, 6, 1)) == "Temer"
    assert config.legislatura_na_data(date(2025, 1, 1)) == 57
