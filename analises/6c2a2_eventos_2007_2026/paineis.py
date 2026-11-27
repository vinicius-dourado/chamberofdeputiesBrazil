"""6-c.2a-ii: painel empilhado (stacked) deputado × votação × evento para todas as entradas e saídas
de partidos do gabinete entre 2007 e 2026 que passam pelas regras de eventos.py.

Uso (da raiz): python analises/6c2a2_eventos_2007_2026/paineis.py [--niveis 1234] [--controles todos]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402

from analises.comum.script import modulo_irmao  # noqa: E402
EV = modulo_irmao(__file__, "eventos")
from analises.comum import config, p1, script  # noqa: E402
from analises.comum.estimacao import meses_relativos  # noqa: E402

NIVEIS = {"1": "1_oficial", "2": "2_bancada_governo", "3": "3_lider", "4": "4_vice_lideres"}
_P1 = {}


def p1_leg(leg):
    if leg not in _P1:
        p = p1.carregar_cache(leg)
        p["data"] = pd.to_datetime(p["data"]).dt.date
        _P1[leg] = p
    return _P1[leg]


def montar_evento(ev, todos, niveis=frozenset({"1_oficial", "2_bancada_governo"}), controles="mesmo_status",
                  data_choque=None, janela=None):
    """Painel de um evento. ``data_choque``/``janela`` permitem placebos (mesmas regras, outra data)."""
    choque = data_choque or ev["data"]
    ini, fim = janela or EV.janela(ev, todos)
    leg = config.legislatura_na_data(choque)
    v = p1_leg(leg)
    v = v[(v["data"] >= ini) & (v["data"] <= fim) & v["fonte_orient_gov"].isin(niveis)
          & v["dir_gov"].notna() & v["dir_voto"].notna()].copy()
    # trocadores: deputados que votaram por mais de uma linhagem na janela saem
    n = v.groupby("deputado_id")["linhagem"].nunique()
    v = v[~v["deputado_id"].isin(n[n > 1].index)]
    mud = EV.mudaram_na_janela(ini, fim, todos) - {ev["partido"]}
    status_pre = ev["tipo"] == "saida"              # saída: o tratado estava na base antes
    estavel = v.groupby("linhagem")["na_base"].agg(lambda s: s.nunique() == 1 and s.iloc[0] == status_pre)
    if controles == "mesmo_status":
        ctrl = set(estavel[estavel].index) - mud - {ev["partido"]}
    else:   # robustez: todos os partidos sem mudança de status na janela
        est_any = v.groupby("linhagem")["na_base"].nunique() == 1
        ctrl = set(est_any[est_any].index) - mud - {ev["partido"]}
    v = v[v["linhagem"].isin(ctrl | {ev["partido"]})]
    v["evento"], v["tipo_evento"], v["grupo"] = ev["evento"], ev["tipo"], ev["grupo"]
    v["governo_evento"] = ev["governo"]
    v["tratado"] = (v["linhagem"] == ev["partido"]).astype(float)
    v["pos"] = (v["data"] >= choque).astype(float)
    v["tratado_pos"] = v["tratado"] * v["pos"]
    v["ent_pos"] = v["tratado_pos"] * (ev["tipo"] == "entrada")
    v["sai_pos"] = v["tratado_pos"] * (ev["tipo"] == "saida")
    v["mes_rel"] = meses_relativos(v["data"], choque)
    v["dep_stack"] = v["deputado_id"] + "|" + ev["evento"]
    v["vot_stack"] = v["idVotacao"] + "|" + ev["evento"]
    v["y1"] = v["seguiu_gov"].astype(float)
    diag = {"evento": ev["evento"], "tipo": ev["tipo"], "grupo": ev["grupo"], "partido": ev["partido"],
            "data": str(choque), "janela": f"{ini} a {fim}", "controles": ",".join(sorted(ctrl)),
            "votacoes_antes": int(v.loc[v["pos"] == 0, "idVotacao"].nunique()),
            "votacoes_depois": int(v.loc[v["pos"] == 1, "idVotacao"].nunique()),
            "deputados_tratados": int(v.loc[v["tratado"] == 1, "deputado_id"].nunique()),
            "deputados_controle": int(v.loc[v["tratado"] == 0, "deputado_id"].nunique())}
    diag["incluido"] = (diag["votacoes_antes"] >= EV.MIN_VOTACOES_LADO and diag["votacoes_depois"] >= EV.MIN_VOTACOES_LADO
                        and diag["deputados_tratados"] > 0 and diag["deputados_controle"] > 0)
    return v, diag


def empilhar(grupos=("principal", "impeachment_2016"), **kw):
    todos = EV.classificar()
    sel = todos[todos["grupo"].isin(grupos)]
    partes, diags = [], []
    for _, ev in sel.iterrows():
        v, dg = montar_evento(ev, todos, **kw)
        diags.append(dg)
        if dg["incluido"]:
            partes.append(v)
    cols = ["evento", "tipo_evento", "grupo", "governo_evento", "idVotacao", "data", "deputado_id", "linhagem",
            "tipo_votacao", "proposicao_titulo", "tratado", "pos", "tratado_pos", "ent_pos", "sai_pos", "mes_rel",
            "dep_stack", "vot_stack", "y1"]
    return pd.concat([p[cols] for p in partes], ignore_index=True), pd.DataFrame(diags)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--niveis", default="12")
    ap.add_argument("--controles", default="mesmo_status", choices=["mesmo_status", "todos"])
    a = ap.parse_args(argv)
    suf = ("" if a.niveis == "12" else f"_niveis{a.niveis}") + ("" if a.controles == "mesmo_status" else "_ctrl_todos")
    pilha, diag = empilhar(niveis=frozenset(NIVEIS[c] for c in a.niveis), controles=a.controles)
    script.gravar_painel(__file__, f"pilha{suf}", pilha)
    diag.to_csv(script.cache(__file__) / f"eventos{suf}.csv", index=False)
    print(diag.drop(columns=["controles"]).to_string(index=False))


if __name__ == "__main__":
    main()
