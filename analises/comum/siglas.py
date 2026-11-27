"""Siglas partidárias: grafia padronizada e linhagem através de renomeações.

``normalizar`` só uniformiza grafias (fontes diferentes escrevem o mesmo partido de jeitos
diferentes na mesma data). ``linhagem`` liga nomes sucessivos do mesmo partido, para comparar
datas distantes. Fusões (DEM + PSL -> UNIÃO; PTB + PATRIOTA -> PRD; PSC -> PODE) não são
linhagem: o partido resultante é outro, e cada desenho decide como tratá-las.
"""

GRAFIA = {
    "União": "UNIÃO", "UNIAO": "UNIÃO", "Rede": "REDE", "REP": "REPUBLICANOS", "Republicanos": "REPUBLICANOS",
    "SD": "SOLIDARIEDADE", "Solidariedade": "SOLIDARIEDADE", "PATRI": "PATRIOTA", "Podemos": "PODE",
    "Cidadania": "CIDADANIA", "Novo": "NOVO", "Avante": "AVANTE", "PC do B": "PCdoB", "PCDOB": "PCdoB",
    "S.PART.": "S.PART.", "sfp": "np", "ind": "np", "": "np", None: "np",
}

# nome antigo -> nome atual (renomeação, mesmo registro partidário)
RENOMEACAO = {
    "PMDB": "MDB", "PR": "PL", "PRB": "REPUBLICANOS", "PPS": "CIDADANIA", "PFL": "DEM",
    "PEN": "PATRIOTA", "PTN": "PODE", "PTdoB": "AVANTE", "PSDC": "DC",
}


def normalizar(sigla):
    """Grafia da Câmara. Ministro sem partido (sfp/ind/vazio) vira 'np'."""
    if sigla is None or (isinstance(sigla, float) and sigla != sigla):
        return "np"
    s = str(sigla).strip()
    return GRAFIA.get(s, s)


def linhagem(sigla, ano=None):
    """Nome atual do partido. O PL anterior a 2007 (fundido no PR em 2006) não é o PL atual."""
    s = normalizar(sigla)
    if s == "PL" and ano is not None and ano < 2007:
        return "PL_antigo"
    return RENOMEACAO.get(s, s)
