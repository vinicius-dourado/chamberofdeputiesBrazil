"""6-c.2a-ii: estimação pré-registrada (PREREG.md). Recusa-se a rodar sem o PREREG commitado.
Uso (da raiz): python analises/6c2a2_eventos_2007_2026/estimacao.py [--placebos 30]
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analises.comum.script import modulo_irmao  # noqa: E402
EV = modulo_irmao(__file__, "eventos")
from analises.comum.script import modulo_irmao  # noqa: E402
P = modulo_irmao(__file__, "paineis")
from analises.comum import config, gabinetes, script  # noqa: E402
from analises.comum import estimacao as E  # noqa: E402

FORMULA = "y1 ~ ent_pos + sai_pos | dep_stack + vot_stack"
VCOV = {"CRV1": "deputado_id+idVotacao"}
MERITO = {"Mérito (texto principal)", "PEC (mérito)", "Emenda / destaque de emenda", "Destaque (texto)"}
JANELA_EVENTO = (-6, 6)
N_PLACEBOS = 30


def tentar(fn):
    try:
        return fn()
    except ValueError as erro:
        return {"nao_identificado": str(erro).strip().splitlines()[0]}


def principal(pilha, formula=FORMULA):
    tipos = set(pilha["tipo_evento"])
    if tipos == {"entrada"}:
        formula = formula.replace(" + sai_pos", "")
    elif tipos == {"saida"}:
        formula = formula.replace("ent_pos + ", "")
    return E.feols(formula, pilha, vcov=VCOV)


def coefs(m):
    return E.coeficientes(m, ["ent_pos", "sai_pos"]).to_dict("records")


def simetria(m):
    est = list(m.coef().index)
    if not {"ent_pos", "sai_pos"} <= set(est):
        return None
    R = np.zeros((1, len(est)))
    R[0, est.index("ent_pos")] = R[0, est.index("sai_pos")] = 1
    w = m.wald_test(R=R)
    soma = float(m.coef()["ent_pos"] + m.coef()["sai_pos"])
    V = m._vcov
    i, j = est.index("ent_pos"), est.index("sai_pos")
    ep = float(np.sqrt(V[i, i] + V[j, j] + 2 * V[i, j]))
    return {"soma": soma, "ep": ep, "ic95": [soma - 1.96 * ep, soma + 1.96 * ep], "p_valor": float(w.pvalue)}


def estudo_evento(pilha):
    d = pilha.copy()
    d, nomes = E.dummies_evento(d, "mes_rel", JANELA_EVENTO)
    termos = []
    for n in nomes:
        for tipo, suf in (("entrada", "ent"), ("saida", "sai")):
            c = f"{n}_{suf}"
            d[c] = d[n] * d["tratado"] * (d["tipo_evento"] == tipo)
            if d[c].sum() > 0:
                termos.append(c)
    m = E.feols(f"y1 ~ {' + '.join(termos)} | dep_stack + vot_stack", d, vcov=VCOV)
    est = list(m.coef().index)
    testes = {}
    for suf in ("ent", "sai"):
        pre = [t for t in est if t.startswith("ev_m") and t.endswith(suf)]
        if pre:
            w = m.wald_test(R=np.eye(len(est))[[est.index(t) for t in pre]])
            testes[suf] = {"estatistica": float(w.stat), "p_valor": float(w.pvalue), "df1": int(w.df1)}
    return E.coeficientes(m, termos).to_dict("records"), testes


# ------------------------------------------------------------------ placebo
def _candidatas(ev, todos):
    """Datas fictícias (dia 15) no mesmo governo, com o partido no mesmo status pré-choque e sem
    mudança real de status do partido a menos de 6 meses."""
    gov = next(g for g in config.GOVERNOS if g[0] == ev["governo"])
    status_pre = ev["tipo"] == "saida"
    reais = todos[(todos["partido"] == ev["partido"])
                  & ~todos["grupo"].isin(["excluido_troca_de_ministro", "excluido_transicao_de_governo"])]["data"]
    out = []
    for mes in pd.period_range(gov[1], gov[2], freq="M"):
        d = date(mes.year, mes.month, 15)
        if d < date(2007, 2, 1) or any(abs((d - r).days) < 183 for r in reais):
            continue
        if (ev["partido"] in gabinetes.base_na_data(d)) == status_pre:
            out.append(d)
    return out


def placebo(eventos_incluidos, todos, n=N_PLACEBOS, semente=config.SEMENTE):
    rng = np.random.default_rng(semente)
    cand = {e["evento"]: _candidatas(e, todos) for _, e in eventos_incluidos.iterrows()}
    betas = []
    for _ in range(n):
        partes = []
        for _, ev in eventos_incluidos.iterrows():
            c = cand[ev["evento"]]
            if not c:
                continue
            dp = c[rng.integers(len(c))]
            fake = ev.copy()
            fake["data"] = dp
            ini, fim = EV.janela(fake, todos)
            v, dg = P.montar_evento(fake, todos, data_choque=dp, janela=(ini, fim))
            if dg["incluido"]:
                partes.append(v)
        if not partes:
            continue
        pilha = pd.concat(partes, ignore_index=True)
        r = tentar(lambda: principal(pilha).coef())
        betas.append({k: float(r.get(k, np.nan)) if not isinstance(r, dict) else np.nan for k in ("ent_pos", "sai_pos")})
    return pd.DataFrame(betas), {k: len(v) for k, v in cand.items()}


def p_placebo(dist, real):
    dist = dist[np.isfinite(dist)]
    return {"p_valor": float((1 + np.sum(np.abs(dist) >= abs(real))) / (1 + len(dist))),
            "n_placebos": int(len(dist)), "placebos": dist.tolist()}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--placebos", type=int, default=N_PLACEBOS)
    a = ap.parse_args(argv)
    pilha = script.ler_painel(__file__, "pilha")
    diag = pd.read_csv(script.cache(__file__) / "eventos.csv")
    res = {"eventos": diag.to_dict("records")}
    m = principal(pilha)
    res["principal"] = coefs(m)
    res["simetria"] = simetria(m)
    res["estudo_evento"], res["teste_pre"] = estudo_evento(pilha)

    todos = EV.classificar()
    inc = todos[todos["evento"].isin(diag.loc[diag["incluido"], "evento"])]
    dist, ncand = placebo(inc, todos, n=a.placebos)
    res["placebo"] = {"candidatas_por_evento": ncand}
    for k in ("ent_pos", "sai_pos"):
        res["placebo"][k] = p_placebo(dist[k].to_numpy(), m.coef()[k])

    rob = {}
    for nome, arq in (("controles_todos", "pilha_ctrl_todos"), ("niveis1234", "pilha_niveis1234")):
        f = script.cache(__file__) / f"{arq}.parquet"
        if f.exists():
            rob[nome] = tentar(lambda: coefs(principal(pd.read_parquet(f))))
    rob["merito"] = tentar(lambda: coefs(principal(pilha[pilha["tipo_votacao"].isin(MERITO)])))
    rob["janela_3m"] = tentar(lambda: coefs(principal(pilha[pilha["mes_rel"].between(-3, 2)])))
    loo = {}
    for ev in sorted(pilha["evento"].unique()):
        loo[ev] = tentar(lambda: {k: float(v) for k, v in principal(pilha[pilha["evento"] != ev]).coef().items()})
    rob["deixa_um_fora"] = loo
    por_evento = {}
    for ev, g in pilha.groupby("evento"):
        por_evento[ev] = tentar(lambda: E.coeficientes(E.feols("y1 ~ tratado_pos | deputado_id + idVotacao", g),
                                                       ["tratado_pos"]).to_dict("records"))
    rob["por_evento"] = por_evento
    res["robustez"] = rob
    print(E.salvar_resultados(AQUI, res))


if __name__ == "__main__":
    main()
