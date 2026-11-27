from analises.comum.siglas import linhagem, normalizar


def test_normalizar():
    assert normalizar("União") == "UNIÃO"
    assert normalizar("REP") == "REPUBLICANOS"
    assert normalizar("sfp") == normalizar("ind") == normalizar(None) == "np"


def test_linhagem():
    assert linhagem("PMDB") == "MDB"
    assert linhagem("PR", 2015) == "PL"
    assert linhagem("PL", 2003) == "PL_antigo"
    assert linhagem("DEM") == "DEM"          # fusão com o PSL não é linhagem
