"""Leitura dos parquets de dados/legNN, empilhando legislaturas com a coluna ``leg``."""
from functools import lru_cache

import duckdb
import pandas as pd

from . import config

TABELAS_LEG = ("votos", "votacoes", "votacoes_orientacoes", "lideres", "mesa", "deputados",
               "deputados_exercicio", "deputados_partidos", "deputados_complemento",
               "proposicoes", "proposicoes_autores", "proposicoes_temas")


def _legs(legs):
    if legs is None:
        return tuple(config.LEGISLATURAS)
    return (legs,) if isinstance(legs, int) else tuple(legs)


def tabela(nome, legs=None, colunas=None, onde=None):
    """Lê ``dados/legNN/<nome>.parquet`` para as legislaturas pedidas e empilha.

    colunas: lista de colunas (None = todas); onde: filtro SQL aplicado em cada arquivo.
    """
    if nome not in TABELAS_LEG:
        raise ValueError(f"tabela desconhecida: {nome}")
    sel = "*" if colunas is None else ", ".join(f'"{c}"' for c in colunas)
    partes = []
    for leg in _legs(legs):
        f = config.DADOS / f"leg{leg}" / f"{nome}.parquet"
        if not f.exists():
            continue
        sql = f"select {sel}, {leg} as leg from read_parquet('{f.as_posix()}')"
        if onde:
            sql += f" where {onde}"
        partes.append(duckdb.sql(sql).df())
    if not partes:
        raise FileNotFoundError(f"nenhum arquivo {nome}.parquet para as legislaturas {legs}")
    return pd.concat(partes, ignore_index=True)


@lru_cache(maxsize=None)
def tse(nome):
    return pd.read_parquet(config.TSE / f"{nome}.parquet")


@lru_cache(maxsize=None)
def executivo(nome):
    return pd.read_parquet(config.EXECUTIVO / f"{nome}_executivo.parquet")


def em_exercicio(legs=None):
    """Períodos de exercício (deputado_id, partido, inicio, fim) só com em_exercicio == True."""
    e = tabela("deputados_exercicio", legs)
    e = e[e["em_exercicio"]].rename(columns={"id": "deputado_id", "siglaPartido": "partido",
                                            "dataInicio": "inicio", "dataFim": "fim"})
    e["deputado_id"] = e["deputado_id"].astype(str)
    return e[["leg", "deputado_id", "nome", "partido", "condicaoEleitoral", "inicio", "fim"]]


def cadeiras_na_data(d, legs=None):
    """Deputados em exercício por partido numa data (meio-dia, como na extensão da L5)."""
    e = em_exercicio(legs or config.legislatura_na_data(d))
    t = pd.Timestamp(d) + pd.Timedelta(hours=12)
    ativos = e[(e["inicio"] <= t) & (e["fim"].isna() | (e["fim"] > t))]
    return ativos.groupby("partido").size()
