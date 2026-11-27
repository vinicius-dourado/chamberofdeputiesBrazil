"""Ligação Câmara ↔ TSE e painéis eleitorais (base municipal do deputado, prefeitos).

Chave: ``cpf_hash``; para candidaturas de 2024 (CPF mascarado pelo TSE), ``nome_nasc_hash``.
Toda função que liga bases devolve também a taxa de ligação, que deve ser relatada.
"""
import pandas as pd

from . import carregar
from .siglas import linhagem, normalizar


def deputados_tse(leg, ano_eleicao):
    """Deputados da legislatura ligados à sua candidatura a deputado federal no ano dado.
    Devolve (df, taxa_ligacao)."""
    comp = carregar.tabela("deputados_complemento", leg, ["id", "cpf_hash", "nome_nasc_hash"])
    comp["deputado_id"] = comp["id"].astype(str)
    res = carregar.tse("depfed_resumo")
    res = res[res["ANO_ELEICAO"] == str(ano_eleicao)]
    m = comp.merge(res, on="cpf_hash", how="left", suffixes=("", "_tse"))
    falta = m["SQ_CANDIDATO"].isna()
    if falta.any():   # segunda chave
        alt = comp[comp["deputado_id"].isin(m.loc[falta, "deputado_id"])].merge(
            res.drop(columns="cpf_hash"), on="nome_nasc_hash", how="inner")
        m = pd.concat([m[~falta], alt], ignore_index=True)
    m = m.drop_duplicates("deputado_id")
    taxa = m["SQ_CANDIDATO"].notna().sum() / comp["deputado_id"].nunique()
    return m, float(taxa)


def pesos_municipais(leg, ano_eleicao):
    """peso_dm: participação do município m nos votos do deputado d na eleição dada."""
    dep, taxa = deputados_tse(leg, ano_eleicao)
    vm = carregar.tse("votacao_depfed_municipio")
    vm = vm[vm["ANO_ELEICAO"] == str(ano_eleicao)]
    w = dep[["deputado_id", "SQ_CANDIDATO"]].dropna().merge(vm, on="SQ_CANDIDATO")
    w["CD_MUNICIPIO"] = codigo_municipio(w["CD_MUNICIPIO"])
    w["peso"] = w["votos"] / w.groupby("deputado_id")["votos"].transform("sum")
    return w[["deputado_id", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "votos", "peso"]], taxa


def prefeitos_eleitos(ano_eleicao):
    """Prefeito eleito por município (último turno), com partido normalizado e linhagem."""
    c = carregar.tse("candidatos_municipais")
    c = c[(c["ANO_ELEICAO"] == str(ano_eleicao)) & c["DS_CARGO"].str.upper().eq("PREFEITO") & c["eleito"]]
    c = c.sort_values("NR_TURNO").drop_duplicates("SG_UE", keep="last")
    c["CD_MUNICIPIO"] = codigo_municipio(c["SG_UE"])
    c["partido"] = c["SG_PARTIDO"].map(normalizar)
    c["linhagem"] = c["partido"].map(lambda p: linhagem(p, int(ano_eleicao)))
    return c[["SG_UF", "CD_MUNICIPIO", "NM_UE", "partido", "linhagem", "SG_FEDERACAO", "cpf_hash", "nome_nasc_hash"]]


def governadores_eleitos(ano_eleicao):
    c = carregar.tse("candidatos_gerais")
    c = c[(c["ANO_ELEICAO"] == str(ano_eleicao)) & c["DS_CARGO"].str.upper().eq("GOVERNADOR") & c["eleito"]]
    c = c.sort_values("NR_TURNO").drop_duplicates("SG_UF", keep="last")
    c["partido"] = c["SG_PARTIDO"].map(normalizar)
    c["linhagem"] = c["partido"].map(lambda p: linhagem(p, int(ano_eleicao)))
    return c[["SG_UF", "partido", "linhagem", "SG_FEDERACAO"]]


def codigo_municipio(serie):
    """Código TSE do município com 5 dígitos. Os arquivos de votação gravam sem zeros à esquerda
    ('7030') e os de candidatos com ('07030'); sem isto a ligação perde ~18% do peso eleitoral."""
    return serie.astype(str).str.strip().str.zfill(5)
