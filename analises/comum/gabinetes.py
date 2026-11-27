"""Partidos no ministério (L5): composição em cada data, base do governo, índice de
proporcionalidade (Acir Almeida, Ipea NT 53/2021) e o painel P4 partido × mês.

Convenções (ver dados/gabinetes/README.md):
- sfp/ind/vazio = 'np' (sem partido);
- Fufuca (Esporte) = PP desde a posse; Anielle Franco = PT a partir de 02/04/2024;
- Sílvio Costa Filho = config.SILVIO_COSTA_FILHO_COMO (principal 'np', como o Ipea);
- desembarque (18/09/2025 a 19/12/2025): pastas de União (Turismo, Comunicações, Integração) e
  PP (Esporte) = 'np'. ``desembarque=False`` desliga a regra (série alternativa).
"""
import math
import re
from collections import Counter
from datetime import date
from functools import lru_cache

import pandas as pd

from . import carregar, config
from .siglas import linhagem, normalizar

ANIELLE_PT = date(2024, 4, 2)
PASTAS_UNIAO = {"Turismo", "Comunicações", "Integração Nacional e Desenvolvimento Regional"}


@lru_cache(maxsize=1)
def ministros():
    m = pd.read_parquet(config.GABINETES / "ministros.parquet")
    for c in ("gov_inicio", "gov_fim", "min_inicio", "min_fim"):
        m[c] = pd.to_datetime(m[c]).dt.date
    return m


def partido_da_pasta(linha, d, desembarque=True, silvio=None):
    """Partido atribuído a uma pasta numa data, aplicando as convenções."""
    silvio = silvio or config.SILVIO_COSTA_FILHO_COMO
    p = normalizar(linha["partido_pasta"])
    nome, pasta = str(linha["ministro"]), linha["ministerio"]
    if linha["governante"] != "Lula 3":
        return p
    saida = config.CHOQUES["desembarque_uniao_pp"].data
    volta = config.CHOQUES["volta_uniao"].data
    if pasta == "Esporte" and "Fufuca" in nome:
        p = "PP" if (not desembarque or d < saida) else "np"
    if "Sílvio Costa Filho" in nome:
        p = normalizar(silvio)
    if pasta == "Igualdade Racial" and "Anielle" in nome and d >= ANIELLE_PT:
        p = "PT"
    if desembarque and pasta in PASTAS_UNIAO and p == "UNIÃO" and saida <= d < volta:
        p = "np"
    return p


def composicao(d, desembarque=True, silvio=None):
    """Counter {partido: número de pastas} vigente na data d (ministro com início <= d < fim)."""
    m = ministros()
    ativos = m[(m["min_inicio"] <= d) & (m["min_fim"].isna() | (m["min_fim"] > d))]
    return Counter(partido_da_pasta(r, d, desembarque, silvio) for _, r in ativos.iterrows())


def base_na_data(d, desembarque=True, silvio=None):
    """Linhagens com ao menos uma pasta na data (sem 'np')."""
    return {linhagem(p, d.year) for p, n in composicao(d, desembarque, silvio).items() if p != "np" and n > 0}


# ------------------------------------------------------------------ proporcionalidade
def _cos(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return 0.0 if na == 0 or nb == 0 else 100 * sum(x * y for x, y in zip(a, b)) / (na * nb)


def proporcionalidade(comp):
    """comp: lista (partido, n_ministros, cadeiras); 'np' = sem partido, 0 cadeiras.
    Devolve (v1, v2): v1 trata 'np' como um bloco; v2 conta cada ministro np separado."""
    v1 = _cos([m for _, m, _ in comp], [c for _, _, c in comp])
    a, b = [], []
    for p, m, c in comp:
        if p == "np":
            a += [1] * m
            b += [0] * m
        else:
            a.append(m)
            b.append(c)
    return v1, _cos(a, b)


def ler_composicao(texto):
    """'PT(10,68);np(8,0)' -> [('PT', 10, 68), ('np', 8, 0)]"""
    return [(p, int(m), int(c)) for p, m, c in re.findall(r"([^;()]+)\((\d+),(\d+)\)", texto)]


def proporcionalidade_na_data(d, desembarque=True, silvio=None):
    comp = composicao(d, desembarque, silvio)
    cad = carregar.cadeiras_na_data(d)
    linhas = [(p, n, 0 if p == "np" else int(cad.get(p, 0))) for p, n in comp.items()]
    return proporcionalidade(linhas)


def serie_proporcionalidade():
    """Série por gabinete (Ipea original + ponte + extensão) de dados/gabinetes/proporcionalidade.parquet."""
    return pd.read_parquet(config.GABINETES / "proporcionalidade.parquet")


# ------------------------------------------------------------------ P4 partido × mês
def painel_p4(inicio, fim, desembarque=True, silvio=None):
    """Partido (linhagem) × mês, medido no dia 15: pastas, cadeiras, se está na base, e o índice
    de proporcionalidade do gabinete. Colunas de recursos (RP2, emendas) entram via emendas.py."""
    linhas = []
    for mes in pd.period_range(inicio, fim, freq="M"):
        d = date(mes.year, mes.month, 15)
        comp = composicao(d, desembarque, silvio)
        cad = carregar.cadeiras_na_data(d)
        v1, v2 = proporcionalidade([(p, n, 0 if p == "np" else int(cad.get(p, 0))) for p, n in comp.items()])
        pastas = Counter()
        for p, n in comp.items():
            if p != "np":
                pastas[linhagem(p, d.year)] += n
        cad_l = Counter()
        for p, n in cad.items():
            cad_l[linhagem(p, d.year)] += int(n)
        total_pastas = sum(comp.values())
        for p in sorted(set(cad_l) | set(pastas)):
            linhas.append({"mes": str(mes), "data_ref": d, "partido": p, "pastas": pastas.get(p, 0),
                           "share_pastas": pastas.get(p, 0) / total_pastas if total_pastas else float("nan"),
                           "cadeiras": cad_l.get(p, 0), "na_base": pastas.get(p, 0) > 0,
                           "governo": config.governo_na_data(d), "prop_v1": v1, "prop_v2": v2})
    return pd.DataFrame(linhas)
