"""6-c.2a: estimação pré-registrada (ver PREREG.md). Recusa-se a rodar se o PREREG.md não estiver
commitado sem mudanças. Uso (da raiz): python analises/6c2a_pastas_set2023/estimacao.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analises.comum import estimacao as E  # noqa: E402
from analises.comum import script  # noqa: E402

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import paineis as P  # noqa: E402

MERITO = {"Mérito (texto principal)", "PEC (mérito)", "Emenda / destaque de emenda", "Destaque (texto)"}
N_PLACEBOS = 12


def did(d, y="y1"):
    m = E.feols(f"{y} ~ tratado_pos | deputado_id + idVotacao", d.dropna(subset=[y]))
    return m


def estudo_evento(d, janela, y="y1"):
    d = d.dropna(subset=[y]).copy()
    d["k"] = d["mes_rel"]
    d, nomes = E.dummies_evento(d, "k", janela)
    for n in nomes:
        d[n] = d[n] * d["tratado"]
    m = E.feols(f"{y} ~ {' + '.join(nomes)} | deputado_id + idVotacao", d)
    pre = [n for n in nomes if n.startswith("ev_m")]
    teste_pre = m.wald_test(R=np.eye(len(nomes))[[nomes.index(n) for n in pre]]) if pre else None
    return m, nomes, teste_pre


def placebo_tempo(pa, ev, beta_real):
    """Choques fictícios mensais na leg57, fora da janela do evento real."""
    e = P.EVENTOS[ev]
    meses = pd.date_range("2023-06-15", "2026-02-15", freq="MS") + pd.Timedelta(days=14)
    cand = [m.date() for m in meses if not (e["inicio"] <= m.date() <= e["fim"])]
    rng = np.random.default_rng(20231)
    escolhidas = sorted(rng.choice(len(cand), size=min(N_PLACEBOS, len(cand)), replace=False))
    meio = (e["fim"] - e["inicio"]) / 2

    def estimar(dt):
        P.EVENTOS["_placebo"] = dict(e, choque=dt, inicio=dt - meio, fim=dt + meio)
        try:
            d = P.montar(pa, "_placebo")
            if d["tratado_pos"].sum() == 0 or d["pos"].min() == 1:
                return float("nan")
            return float(did(d).coef()["tratado_pos"])
        finally:
            P.EVENTOS.pop("_placebo", None)
    return E.inferencia_placebo_datas(estimar, [cand[i] for i in escolhidas], beta_real)


def placebo_grupo(pa, ev):
    """Troca os tratados por combinações de partidos de controle (mesmo tamanho, se possível)."""
    from itertools import combinations
    e = P.EVENTOS[ev]
    ctrl = sorted(e["controles"])
    k = min(len(e["tratados"]), len(ctrl) - 1)
    out = {}
    for falsos in combinations(ctrl, k):
        P.EVENTOS["_pg"] = dict(e, tratados=set(falsos), controles=set(ctrl) - set(falsos))
        try:
            out["+".join(falsos)] = float(did(P.montar(pa, "_pg")).coef()["tratado_pos"])
        finally:
            P.EVENTOS.pop("_pg", None)
    return out


def janelas_alternativas(pa, ev):
    e = P.EVENTOS[ev]
    meses = (3, 9) if ev == "A" else (2,)
    out = {}
    for m in meses:
        delta = pd.Timedelta(days=round(30.44 * m))
        # no evento A a janela de 9 meses é assimétrica: não há votações nominais antes de 14/03/2023
        P.EVENTOS["_jan"] = dict(e, inicio=(pd.Timestamp(e["choque"]) - delta).date(),
                                 fim=(pd.Timestamp(e["choque"]) + delta).date())
        try:
            out[f"{m}m"] = E.coeficientes(did(P.montar(pa, "_jan")), ["tratado_pos"]).to_dict("records")
        finally:
            P.EVENTOS.pop("_jan", None)
    return out


def logit(d):
    import pyfixest as pf
    try:
        m = pf.feglm("y1 ~ tratado_pos | deputado_id + idVotacao", data=d, family="logit",
                     vcov={"CRV1": "deputado_id"})
        return E.coeficientes(m, ["tratado_pos"]).to_dict("records")
    except Exception as erro:   # versões antigas do pyfixest não têm feglm com efeitos fixos
        return {"erro": str(erro)}


def main():
    res = {}
    from analises.comum import p1
    pa = p1.carregar_cache(57)
    pa["data"] = pd.to_datetime(pa["data"]).dt.date
    for ev in P.EVENTOS:
        d = script.ler_painel(__file__, f"evento_{ev}")
        dp = script.ler_painel(__file__, f"evento_{ev}_partido")
        r = {}
        m1 = did(d, "y1")
        r["y1"] = E.coeficientes(m1, ["tratado_pos"]).to_dict("records")
        r["y2"] = E.coeficientes(did(d, "y2"), ["tratado_pos"]).to_dict("records")
        m3 = E.feols("y3 ~ tratado_pos | linhagem + idVotacao", dp, vcov={"CRV1": "idVotacao"})
        r["y3"] = E.coeficientes(m3, ["tratado_pos"]).to_dict("records")
        me, nomes, pre = estudo_evento(d, P.EVENTOS[ev]["janela"])
        r["estudo_evento"] = E.coeficientes(me, nomes).to_dict("records")
        r["teste_pre"] = None if pre is None else pre.to_dict()
        r["placebo_tempo"] = placebo_tempo(pa, ev, m1.coef()["tratado_pos"])
        if ev == "A":   # heterogeneidade PP vs Republicanos
            for part in ("PP", "REPUBLICANOS"):
                sub = d[(d["linhagem"] == part) | (d["tratado"] == 0)]
                r[f"y1_{part}"] = E.coeficientes(did(sub), ["tratado_pos"]).to_dict("records")
        r["placebo_grupo"] = placebo_grupo(pa, ev)
        r["robustez"] = {
            "merito": E.coeficientes(did(d[d["tipo_votacao"].isin(MERITO)]), ["tratado_pos"]).to_dict("records"),
            "janelas": janelas_alternativas(pa, ev),
            "com_trocadores": E.coeficientes(did(P.montar(pa, ev, excluir_trocadores=False)),
                                             ["tratado_pos"]).to_dict("records"),
            "logit": logit(d),
        }
        for suf in ("_silvio_rep", "_niveis1234"):   # gerados por paineis.py --silvio/--niveis
            f = script.cache(__file__) / f"evento_{ev}{suf}.parquet"
            if f.exists():
                r["robustez"][suf.strip("_")] = E.coeficientes(did(pd.read_parquet(f)), ["tratado_pos"]).to_dict("records")
        res[ev] = r
    print(E.salvar_resultados(AQUI, res))


if __name__ == "__main__":
    main()
