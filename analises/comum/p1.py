"""P1: painel deputado × votação nominal, com a orientação do governo por hierarquia de fontes,
orientação do partido, divergência partido × governo, tipo de votação e pertença à base.

Uso:
    from analises.comum import p1
    painel = p1.painel(legs=[57])            # ou p1.carregar_cache(57), que grava em analises/cache/
"""
import re

import duckdb
import numpy as np
import pandas as pd

from . import carregar, config, gabinetes
from .siglas import linhagem, normalizar

ORIENTACOES_DIRECIONAIS = {"Sim": 1.0, "Não": 0.0, "Obstrução": 0.0}
CACHE = config.ANALISES / "cache"


def classificar_votacao(desc):
    """Tipo de votação pela descrição (mesmo classificador de artigos/02-disciplina-intrapartidaria)."""
    d = str(desc).lower()
    if "requerimento de urgência" in d or ("urgência" in d and "requerimento" in d):
        return "Urgência"
    if d.startswith(("mantido o texto", "suprimido o texto", "mantida a expressão", "suprimida",
                     "mantidos os", "mantido o dispositivo", "rejeitados os dispositivos", "mantida a")):
        return "Destaque (texto)"
    if "requerimento" in d:
        return "Requerimento procedimental"
    if "proposta de emenda à constituição" in d or "proposta de emenda a constituição" in d:
        return "PEC (mérito)"
    if ("emenda" in d or "subemenda" in d) and "substitutiva global" not in d:
        return "Emenda / destaque de emenda"
    return "Mérito (texto principal)"


def _votacoes(legs):
    v = carregar.tabela("votacoes", legs, ["idVotacao", "dataHoraRegistro", "siglaOrgao", "descricao",
                                           "proposicao_id", "proposicao_titulo", "objeto_titulo", "votosSim", "votosNao"],
                        onde="tem_votos_nominais")
    for c in ("votosSim", "votosNao"):
        v[c] = pd.to_numeric(v[c], errors="coerce")
    v["tipo_votacao"] = v["descricao"].map(classificar_votacao)
    v["sigla_prop"] = v["proposicao_titulo"].str.extract(r"^([A-Z]+)", expand=False)
    s, n = v["votosSim"], v["votosNao"]
    v["margem"] = (s - n).abs() / (s + n)
    # margem em relação ao quórum exigido: PEC 308, PLP 257 (maioria absoluta), demais maioria simples
    v["margem_quorum"] = np.select(
        [v["sigla_prop"].eq("PEC") & v["tipo_votacao"].eq("PEC (mérito)"), v["sigla_prop"].eq("PLP")],
        [(s - 308).abs() / 513, (s - 257).abs() / 513], default=v["margem"])
    return v.drop(columns=["leg"]).drop_duplicates("idVotacao")


def _orientacao_bancada_governo(legs):
    o = carregar.tabela("votacoes_orientacoes", legs, ["idVotacao", "siglaBancada", "orientacao"],
                        onde="siglaBancada in ('Governo', 'GOV.')")
    return o.drop_duplicates("idVotacao").set_index("idVotacao")["orientacao"]


def _lideres_governo(legs):
    lid = carregar.tabela("lideres", legs, ["titulo", "dataInicio", "dataFim", "deputado_id", "bancada_nome"],
                          onde="bancada_nome = 'Governo na CD'")
    lid["deputado_id"] = lid["deputado_id"].astype(str)
    lid["inicio"] = pd.to_datetime(lid["dataInicio"])
    lid["fim"] = pd.to_datetime(lid["dataFim"]).fillna(pd.Timestamp("2100-01-01"))
    lid["papel"] = np.where(lid["titulo"].eq("Líder"), "lider", "vice")
    return lid[["deputado_id", "inicio", "fim", "papel"]]


def _voto_proxy(votos, lideres):
    """Voto do Líder do Governo (nível 3) e moda dos vice-líderes (nível 4) por votação."""
    con = duckdb.connect()
    con.register("v", votos[["idVotacao", "data", "deputado_id", "voto"]])
    con.register("l", lideres)
    m = con.sql("""select v.idVotacao, l.papel, v.voto from v join l
                   on v.deputado_id = l.deputado_id and cast(v.data as timestamp) >= l.inicio
                   and cast(v.data as timestamp) < l.fim
                   where v.voto in ('Sim', 'Não', 'Obstrução')""").df()
    lider = m[m["papel"] == "lider"].drop_duplicates("idVotacao").set_index("idVotacao")["voto"]
    vice = (m[m["papel"] == "vice"].groupby("idVotacao")["voto"]
            .agg(lambda s: s.mode().iloc[0] if s.mode().size == 1 else None))
    return lider, vice


def orientacao_governo(votos, legs):
    """Série (por linha de votos) com a orientação do governo e a fonte usada (1 a 4)."""
    oficial = votos["orientacao_governo"].where(votos["orientacao_governo"].notna() &
                                                votos["orientacao_governo"].ne(""))
    banc = votos["idVotacao"].map(_orientacao_bancada_governo(legs))
    lider, vice = _voto_proxy(votos, _lideres_governo(legs))
    niv3 = votos["idVotacao"].map(lider)
    niv4 = votos["idVotacao"].map(vice)
    orient = oficial.fillna(banc).fillna(niv3).fillna(niv4)
    fonte = np.select([oficial.notna(), banc.notna(), niv3.notna(), niv4.notna()],
                      ["1_oficial", "2_bancada_governo", "3_lider", "4_vice_lideres"], default="sem")
    return orient, pd.Series(fonte, index=votos.index)


def _base_por_data(datas, **kw):
    return {d: gabinetes.base_na_data(d, **kw) for d in datas}


def painel(legs=None, so_plenario=True, desembarque=True, silvio=None):
    """Monta P1. Uma linha por deputado × votação nominal com voto válido."""
    legs = tuple(config.LEGISLATURAS) if legs is None else ((legs,) if isinstance(legs, int) else tuple(legs))
    onde = "voto in ('Sim', 'Não', 'Obstrução', 'Abstenção')"
    if so_plenario:
        onde += " and siglaOrgao = 'PLEN'"
    v = carregar.tabela("votos", legs, ["idVotacao", "data", "siglaOrgao", "deputado_id", "deputado_siglaPartido",
                                        "deputado_siglaUf", "voto", "orientacao_partido", "orientacao_fonte",
                                        "orientacao_governo"], onde=onde)
    v["orient_gov"], v["fonte_orient_gov"] = orientacao_governo(v, legs)
    v["data"] = pd.to_datetime(v["data"]).dt.date
    v["partido"] = v["deputado_siglaPartido"].map(normalizar)
    v["linhagem"] = [linhagem(p, d.year) for p, d in zip(v["partido"], v["data"])]
    v = v.merge(_votacoes(legs), on="idVotacao", how="left", suffixes=("", "_vt"))
    v["dir_voto"] = v["voto"].map(ORIENTACOES_DIRECIONAIS)
    v["dir_gov"] = v["orient_gov"].map(ORIENTACOES_DIRECIONAIS)
    v["dir_partido"] = v["orientacao_partido"].map(ORIENTACOES_DIRECIONAIS)
    v["divergente"] = v["dir_gov"].notna() & v["dir_partido"].notna() & (v["dir_gov"] != v["dir_partido"])
    v["seguiu_gov"] = np.where(v["dir_voto"].notna() & v["dir_gov"].notna(), v["dir_voto"] == v["dir_gov"], np.nan)
    v["seguiu_partido"] = np.where(v["dir_voto"].notna() & v["dir_partido"].notna(),
                                   v["dir_voto"] == v["dir_partido"], np.nan)
    bases = _base_por_data(sorted(v["data"].unique()), desembarque=desembarque, silvio=silvio)
    v["na_base"] = [lin in bases[d] for lin, d in zip(v["linhagem"], v["data"])]
    v["governo"] = v["data"].map(config.governo_na_data)
    v["deputado_id"] = v["deputado_id"].astype(str)
    return v.drop(columns=["deputado_siglaPartido", "orientacao_governo", "siglaOrgao_vt"], errors="ignore")


def carregar_cache(leg, **kw):
    """P1 de uma legislatura com cache em analises/cache/p1_legNN.parquet (convenções padrão)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"p1_leg{leg}.parquet"
    if f.exists() and not kw:
        return pd.read_parquet(f)
    p = painel(leg, **kw)
    if not kw:
        p.to_parquet(f, index=False)
    return p


def ausencias(legs, so_plenario=True):
    """Deputado × votação para quem estava em exercício e não tem voto registrado (4-c.3)."""
    legs = (legs,) if isinstance(legs, int) else tuple(legs)
    vt = carregar.tabela("votacoes", legs, ["idVotacao", "dataHoraRegistro", "siglaOrgao"],
                         onde="tem_votos_nominais" + (" and siglaOrgao = 'PLEN'" if so_plenario else ""))
    ex = carregar.em_exercicio(legs)
    vo = carregar.tabela("votos", legs, ["idVotacao", "deputado_id"])
    vo["deputado_id"] = vo["deputado_id"].astype(str)
    con = duckdb.connect()
    for n, df in (("vt", vt), ("ex", ex), ("vo", vo)):
        con.register(n, df)
    return con.sql("""
        select vt.idVotacao, ex.deputado_id, ex.partido, vt.dataHoraRegistro
        from vt join ex on cast(vt.dataHoraRegistro as timestamp) >= ex.inicio
                       and (ex.fim is null or cast(vt.dataHoraRegistro as timestamp) < ex.fim)
                       and vt.leg = ex.leg
        anti join vo on vo.idVotacao = vt.idVotacao and vo.deputado_id = ex.deputado_id""").df()
