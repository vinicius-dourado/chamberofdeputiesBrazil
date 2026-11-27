"""6-c.2a: monta os painéis dos eventos A (entrada de PP e Republicanos), B (desembarque de União e
PP) e B' (volta do União) a partir do P1 da leg57. Não calcula nenhum desfecho agregado.

Uso (da raiz): python analises/6c2a_pastas_set2023/paineis.py [--niveis 1234]
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd  # noqa: E402

from analises.comum import config, p1, script  # noqa: E402
from analises.comum.estimacao import meses_relativos  # noqa: E402

EVENTOS = {
    "A": dict(choque=config.choque("entrada_pp_rep"), tratados={"PP", "REPUBLICANOS"},
              controles={"MDB", "PSD", "UNIÃO"}, inicio=date(2023, 3, 14), fim=date(2024, 3, 12), janela=(-6, 6)),
    "B": dict(choque=config.choque("desembarque_uniao_pp"), tratados={"UNIÃO", "PP"},
              controles={"MDB", "PSD"}, inicio=date(2025, 6, 2), fim=date(2025, 12, 1), janela=(-3, 3)),
    "Bv": dict(choque=config.choque("volta_uniao"), tratados={"UNIÃO"}, controles={"MDB", "PSD"},
               inicio=config.choque("ultimato_uniao") + timedelta(days=1), fim=date(2026, 3, 30), janela=(-3, 3)),
}
NIVEIS_PRINCIPAIS = {"1_oficial", "2_bancada_governo"}


def trocadores(painel, inicio, fim):
    """Deputados que votaram por mais de um partido dentro da janela."""
    j = painel[(painel["data"] >= inicio) & (painel["data"] <= fim)]
    n = j.groupby("deputado_id")["linhagem"].nunique()
    return set(n[n > 1].index)


def montar(painel, ev, niveis=NIVEIS_PRINCIPAIS, excluir_trocadores=True):
    e = EVENTOS[ev]
    d = painel[(painel["data"] >= e["inicio"]) & (painel["data"] <= e["fim"])
               & painel["fonte_orient_gov"].isin(niveis) & painel["dir_gov"].notna()
               & painel["dir_voto"].notna()
               & painel["linhagem"].isin(e["tratados"] | e["controles"])].copy()
    if excluir_trocadores:
        d = d[~d["deputado_id"].isin(trocadores(painel, e["inicio"], e["fim"]))]
    d["evento"] = ev
    d["tratado"] = d["linhagem"].isin(e["tratados"]).astype(float)
    d["pos"] = (d["data"] >= e["choque"]).astype(float)
    d["tratado_pos"] = d["tratado"] * d["pos"]
    d["mes_rel"] = meses_relativos(d["data"], e["choque"])
    d["y1"] = d["seguiu_gov"].astype(float)
    d["y2"] = d["seguiu_gov"].where(d["divergente"]).astype(float)
    if ev == "B":   # segundo degrau: ultimato do União (robustez 9 do PREREG)
        d["pos_ultimato_uniao"] = ((d["data"] >= config.choque("ultimato_uniao")) & d["linhagem"].eq("UNIÃO")).astype(float)
    return d


def painel_partido(d):
    """Y3: a orientação que vale para o partido (a própria, se orientou; senão a do bloco) coincide com
    a do governo. Partido × votação. ``orientacao_fonte`` guarda de onde veio."""
    x = d[d["dir_partido"].notna()].drop_duplicates(["idVotacao", "linhagem"])
    x = x[["evento", "idVotacao", "data", "linhagem", "tratado", "pos", "tratado_pos", "mes_rel",
           "dir_partido", "dir_gov", "orientacao_fonte"]].copy()
    x["y3"] = (x["dir_partido"] == x["dir_gov"]).astype(float)
    return x


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--niveis", default="12", help="níveis da orientação do governo (12 = principal; 1234 = robustez)")
    a = ap.parse_args(argv)
    mapa = {"1": "1_oficial", "2": "2_bancada_governo", "3": "3_lider", "4": "4_vice_lideres"}
    niveis = {mapa[c] for c in a.niveis}
    pa = p1.carregar_cache(57)
    pa["data"] = pd.to_datetime(pa["data"]).dt.date
    sufixo = "" if a.niveis == "12" else f"_niveis{a.niveis}"
    tam = []
    for ev in EVENTOS:
        d = montar(pa, ev, niveis)
        script.gravar_painel(__file__, f"evento_{ev}{sufixo}", d)
        script.gravar_painel(__file__, f"evento_{ev}_partido{sufixo}", painel_partido(d))
        tam.append(script.descrever(d, ["evento", "linhagem", "pos"]))
    t = pd.concat(tam)
    print(t.to_string(index=False))
    t.to_csv(script.cache(__file__) / f"tamanhos{sufixo}.csv", index=False)


if __name__ == "__main__":
    main()
