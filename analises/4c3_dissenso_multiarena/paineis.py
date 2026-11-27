"""4-c.3: indicadores de dissenso por arena (I1, I2, I3, I5), painel deputado × proposição (H1) e
deputado × semestre (índice e H3). I4 depende da lacuna L8 (proposição principal das acessórias).

Uso (da raiz): python analises/4c3_dissenso_multiarena/paineis.py [--legs 57 56 55]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analises.comum import carregar, p1, script  # noqa: E402

PROPOSICAO_SIGLA = re.compile(r"\b(PL|PLP|PEC|MPV|PDL|PRC|PLN|PLV)\s*(?:n[º°o]\.?\s*)?(\d+)\s*/\s*(\d{2,4})")
PROPOSICAO_EXTENSO = re.compile(
    r"(Projeto de Lei Complementar|Projeto de Lei|Proposta de Emenda à Constituição|Medida Provisória|"
    r"Projeto de Decreto Legislativo|Projeto de Resolução)\s*n?[º°o]?\s*\.?\s*([\d\.]+)\s*,?\s*de\s*(\d{4})", re.I)
EXTENSO = {"projeto de lei complementar": "PLP", "projeto de lei": "PL", "proposta de emenda à constituição": "PEC",
           "medida provisória": "MPV", "projeto de decreto legislativo": "PDL", "projeto de resolução": "PRC"}


def proposicao_alvo(ementa):
    """'Destaque ... PL 3796/2004' -> 'PL 3796/2004' (ano com 4 dígitos). None se não achar."""
    s = str(ementa or "")
    m = PROPOSICAO_SIGLA.search(s)
    if m:
        sig, num, ano = m.groups()
    else:
        m = PROPOSICAO_EXTENSO.search(s)
        if not m:
            return None
        sig, num, ano = EXTENSO[m.group(1).lower()], m.group(2).replace(".", ""), m.group(3)
    ano = ano if len(ano) == 4 else ("20" + ano if int(ano) < 50 else "19" + ano)
    return f"{sig} {int(num)}/{ano}"


def votos_todas_arenas(leg):
    f = script.cache(__file__) / f"p1_todas_arenas_leg{leg}.parquet"
    if f.exists():
        return pd.read_parquet(f)
    v = p1.painel(leg, so_plenario=False)
    v.to_parquet(f, index=False)
    return v


def indicadores_voto(leg):
    """Deputado × votação com I1 (ausência), I2 (obstrução/abstenção contra), I5 (comissão) e defecção."""
    v = votos_todas_arenas(leg)
    v["plenario"] = v["siglaOrgao"].eq("PLEN")
    orientou = v["orientacao_partido"].isin(["Sim", "Não"])
    v["defeccao"] = np.where(orientou & v["dir_voto"].notna(), v["dir_voto"] != v["dir_partido"], np.nan)
    v["i2_obst_abst_contra"] = np.where(
        orientou, ((v["voto"] == "Abstenção") | ((v["voto"] == "Obstrução") & (v["orientacao_partido"] == "Sim"))), np.nan)
    v["i5_comissao_contra"] = np.where(~v["plenario"], v["defeccao"], np.nan)
    v["i1_ausente"] = 0.0
    # ausências: orientação do partido na votação = moda entre os que votaram
    aus = p1.ausencias(leg)
    aus["partido"] = aus["partido"].astype(str)
    orient = (v[v["plenario"]].groupby(["idVotacao", "partido"])["orientacao_partido"]
              .agg(lambda s: s.mode().iloc[0] if len(s.mode()) else None).reset_index())
    aus = aus.merge(orient, on=["idVotacao", "partido"], how="left")
    aus = aus[aus["orientacao_partido"].isin(["Sim", "Não"])]
    meta = v.drop_duplicates("idVotacao").set_index("idVotacao")
    aus["data"] = aus["idVotacao"].map(meta["data"])
    for c in ("proposicao_id", "tipo_votacao", "siglaOrgao"):
        aus[c] = aus["idVotacao"].map(meta[c])
    aus["plenario"], aus["i1_ausente"], aus["voto"] = True, 1.0, "Ausente"
    cols = ["idVotacao", "data", "siglaOrgao", "plenario", "proposicao_id", "tipo_votacao", "deputado_id", "partido",
            "orientacao_partido", "orientacao_fonte", "voto", "defeccao", "i1_ausente", "i2_obst_abst_contra",
            "i5_comissao_contra"]
    v["i1_ausente"] = np.where(v["plenario"] & orientou, 0.0, np.nan)
    return pd.concat([v[cols], aus.reindex(columns=cols)], ignore_index=True)


def destaques_da_base(leg):
    """I3: DTQ de deputados da base sobre proposições cujo texto principal o governo orientou Sim."""
    pr = carregar.tabela("proposicoes", leg, ["id", "siglaTipo", "ementa", "dataApresentacao"], onde="siglaTipo = 'DTQ'")
    au = carregar.tabela("proposicoes_autores", leg, ["idProposicao", "idDeputadoAutor", "siglaPartidoAutor"])
    d = pr.merge(au, left_on="id", right_on="idProposicao")
    d["alvo"] = d["ementa"].map(proposicao_alvo)
    taxa = float(d.drop_duplicates("id")["alvo"].notna().mean())
    pl = p1.carregar_cache(leg)
    princ = (pl[pl["tipo_votacao"].isin(["Mérito (texto principal)", "PEC (mérito)"])]
             .drop_duplicates("idVotacao")[["proposicao_titulo", "proposicao_id", "orient_gov"]]
             .drop_duplicates("proposicao_titulo"))
    d = d.merge(princ, left_on="alvo", right_on="proposicao_titulo", how="left")
    d["data"] = pd.to_datetime(d["dataApresentacao"]).dt.date
    from analises.comum import gabinetes
    from analises.comum.siglas import linhagem
    bases = {dt: gabinetes.base_na_data(dt) for dt in d["data"].dropna().unique()}
    d["autor_na_base"] = [linhagem(p, dt.year) in bases[dt] if pd.notna(dt) else False
                          for p, dt in zip(d["siglaPartidoAutor"], d["data"])]
    d["i3_dtq_base_contra_gov"] = (d["autor_na_base"] & d["orient_gov"].eq("Sim")).astype(float)
    return d.rename(columns={"idDeputadoAutor": "deputado_id"}), taxa


def urgencias(leg):
    vt = carregar.tabela("votacoes", leg, ["proposicao_id", "descricao", "aprovacao", "siglaOrgao"])
    u = vt[vt["siglaOrgao"].eq("PLEN") & vt["descricao"].str.lower().str.contains("urgência", na=False)
           & vt["aprovacao"].eq("1")]
    return set(u["proposicao_id"].dropna())


def painel_proposicao(ind, leg):
    """H1: deputado × proposição (com ao menos uma votação nominal de mérito no Plenário)."""
    x = ind[ind["proposicao_id"].notna()].copy()
    merito = x[x["plenario"] & x["tipo_votacao"].isin(["Mérito (texto principal)", "PEC (mérito)"])]["proposicao_id"]
    x = x[x["proposicao_id"].isin(set(merito))]
    x["fora"] = x[["i1_ausente", "i2_obst_abst_contra", "i5_comissao_contra"]].max(axis=1, skipna=True)
    g = x.groupby(["deputado_id", "proposicao_id"]).agg(
        partido=("partido", "first"), data=("data", "min"),
        defeccao_plen=("defeccao", lambda s: s[x.loc[s.index, "plenario"]].mean()),
        fora=("fora", "mean"), n=("idVotacao", "nunique")).reset_index()
    g["urgencia"] = g["proposicao_id"].isin(urgencias(leg)).astype(float)
    g["mes"] = pd.to_datetime(g["data"]).dt.strftime("%Y-%m")
    g["partido_mes"] = g["partido"] + "_" + g["mes"]
    return g


def painel_semestre(ind, dtq):
    ind = ind.copy()
    ind["semestre"] = pd.to_datetime(ind["data"]).dt.year.astype(str) + "S" + \
        ((pd.to_datetime(ind["data"]).dt.month > 6) + 1).astype(str)
    plen = ind[ind["plenario"]]
    s = plen.groupby(["deputado_id", "semestre"]).agg(partido=("partido", lambda p: p.mode().iloc[0]),
                                                      defeccao=("defeccao", "mean"), i1=("i1_ausente", "mean"),
                                                      i2=("i2_obst_abst_contra", "mean")).reset_index()
    i5 = ind[~ind["plenario"]].groupby(["deputado_id", "semestre"])["i5_comissao_contra"].mean().rename("i5")
    s = s.merge(i5.reset_index(), on=["deputado_id", "semestre"], how="left")
    dtq = dtq.copy()
    dtq["semestre"] = pd.to_datetime(dtq["data"]).dt.year.astype(str) + "S" + \
        ((pd.to_datetime(dtq["data"]).dt.month > 6) + 1).astype(str)
    i3 = dtq.groupby(["deputado_id", "semestre"])["i3_dtq_base_contra_gov"].sum().rename("i3")
    s = s.merge(i3.reset_index(), on=["deputado_id", "semestre"], how="left")
    s["i3"] = s["i3"].fillna(0.0)
    return s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--legs", nargs="+", type=int, default=[57])
    a = ap.parse_args(argv)
    for leg in a.legs:
        ind = indicadores_voto(leg)
        dtq, taxa = destaques_da_base(leg)
        script.gravar_painel(__file__, f"indicadores_leg{leg}", ind)
        script.gravar_painel(__file__, f"proposicao_leg{leg}", painel_proposicao(ind, leg))
        script.gravar_painel(__file__, f"semestre_leg{leg}", painel_semestre(ind, dtq))
        script.gravar_painel(__file__, f"dtq_leg{leg}", dtq)
        print(f"leg{leg}: {len(ind)} linhas deputado × votação; DTQ com proposição identificada: {taxa:.1%}")


if __name__ == "__main__":
    main()
