"""7-c.2: ΔAlinhaBase por deputado e réplica, e o painel deputado × votação nas janelas.

Uso (da raiz): python analises/7c2_prefeitos_base/paineis.py
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd  # noqa: E402

from analises.comum import carregar, gabinetes, p1, script, tse  # noqa: E402
from analises.comum.estimacao import meses_relativos  # noqa: E402

# réplica: (legislatura, eleição do deputado, prefeitos antigos, prefeitos novos)
REPLICAS = {2013: (54, 2010, 2008, 2012), 2017: (55, 2014, 2012, 2016),
            2021: (56, 2018, 2016, 2020), 2025: (57, 2022, 2020, 2024)}
PRINCIPAL = 2025
NIVEIS = {"1_oficial", "2_bancada_governo"}


def janelas(ano):
    return {"pre": (date(ano - 1, 3, 1), date(ano - 1, 9, 30)),
            "transicao": (date(ano - 1, 10, 1), date(ano - 1, 12, 31)),
            "pos": (date(ano, 1, 1), date(ano, 6, 30))}


def delta_alinhamento(ano, base=None):
    """Δ por deputado. Devolve (df, diagnóstico com taxas de ligação e cobertura)."""
    leg, eleicao, antigos, novos = REPLICAS[ano]
    posse = date(ano, 1, 1)
    base = base if base is not None else gabinetes.base_na_data(posse)
    w, taxa = tse.pesos_municipais(leg, eleicao)
    pa = tse.prefeitos_eleitos(antigos)[["CD_MUNICIPIO", "linhagem"]].rename(columns={"linhagem": "pref_antigo"})
    pn = tse.prefeitos_eleitos(novos)[["CD_MUNICIPIO", "linhagem"]].rename(columns={"linhagem": "pref_novo"})
    m = w.merge(pa, on="CD_MUNICIPIO", how="left").merge(pn, on="CD_MUNICIPIO", how="left")
    m = m[~m["SG_UF"].isin(["ZZ", "DF"])]
    ok = m["pref_antigo"].notna() & m["pref_novo"].notna()
    cobertura = float(m.loc[ok, "peso"].sum() / m["peso"].sum())
    m = m[ok].copy()
    m["peso"] = m["peso"] / m.groupby("deputado_id")["peso"].transform("sum")   # renormaliza nos cobertos
    m["al_antigo"] = m["pref_antigo"].isin(base) * m["peso"]
    m["al_novo"] = m["pref_novo"].isin(base) * m["peso"]
    d = m.groupby("deputado_id")[["al_antigo", "al_novo"]].sum().reset_index()
    d["delta"] = d["al_novo"] - d["al_antigo"]
    dep, _ = tse.deputados_tse(leg, eleicao)
    d = d.merge(dep[["deputado_id", "hhi_municipios", "concentracao"]], on="deputado_id", how="left")
    d["replica"] = ano
    return d, {"replica": ano, "taxa_ligacao_tse": taxa, "cobertura_peso_prefeitos": cobertura,
               "deputados_com_delta": int(len(d)), "base_na_posse": sorted(base)}


def presidente_camara_eleito(ano):
    leg = REPLICAS[ano][0]
    mesa = carregar.tabela("mesa", leg)
    pres = mesa[mesa["titulo"].eq("Presidente")].copy()
    pres["inicio"] = pd.to_datetime(pres["dataInicio"]).dt.date
    antes = pres[pres["inicio"] <= date(ano - 1, 12, 31)].sort_values("inicio").tail(1)
    depois = pres[pres["inicio"] <= date(ano, 2, 28)].sort_values("inicio").tail(1)
    return {"antes": antes["nome"].tolist(), "depois": depois["nome"].tolist(),
            "partido_depois": depois["siglaPartido"].tolist(),
            "troca": antes["nome"].tolist() != depois["nome"].tolist()}


def painel_replica(ano):
    leg = REPLICAS[ano][0]
    delta, diag = delta_alinhamento(ano)
    v = p1.carregar_cache(leg)
    v["data"] = pd.to_datetime(v["data"]).dt.date
    j = janelas(ano)
    v = v[(v["data"] >= j["pre"][0]) & (v["data"] <= j["pos"][1]) & v["fonte_orient_gov"].isin(NIVEIS)
          & v["dir_gov"].notna() & v["dir_voto"].notna()].copy()
    v = v.merge(delta, on="deputado_id", how="inner")
    v["periodo"] = "pre"
    v.loc[v["data"] >= j["transicao"][0], "periodo"] = "transicao"
    v.loc[v["data"] >= j["pos"][0], "periodo"] = "pos"
    v["pos"] = (v["periodo"] == "pos").astype(float)
    v["delta_pos"] = v["delta"] * v["pos"]
    v["mes_rel"] = meses_relativos(v["data"], date(ano, 1, 1))
    mesa = presidente_camara_eleito(ano)
    v["partido_pres_camara"] = (v["partido"].isin(mesa["partido_depois"])).astype(float)
    v["y1"] = v["seguiu_gov"].astype(float)
    diag.update({"mesa": mesa})
    return v, diag


def main():
    diags = []
    for ano in REPLICAS:
        v, diag = painel_replica(ano)
        script.gravar_painel(__file__, f"replica_{ano}", v)
        diags.append(diag)
        print(script.descrever(v, ["replica", "periodo"]).to_string(index=False))
    pd.DataFrame(diags).to_json(script.cache(__file__) / "diagnostico.json", orient="records",
                                force_ascii=False, indent=2, default_handler=str)
    for dg in diags:
        print({k: dg[k] for k in ("replica", "taxa_ligacao_tse", "cobertura_peso_prefeitos", "deputados_com_delta")},
              "| troca na Presidência da Câmara:", dg["mesa"]["troca"])


if __name__ == "__main__":
    main()
