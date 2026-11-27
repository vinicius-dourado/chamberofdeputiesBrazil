"""4-c.3: índice multiarena, H1 (substituição) e H3 (validade preditiva fora da amostra).
Uso (da raiz): python analises/4c3_dissenso_multiarena/estimacao.py [--legs 57 56 55]"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analises.comum import estimacao as E, script  # noqa: E402

AQUI = Path(__file__).resolve().parent
COMPONENTES = ["i1", "i2", "i3", "i5"]


def indice(s, componentes=COMPONENTES):
    """Média dos z-escores (principal) e primeiro componente principal (alternativa)."""
    z = s[componentes].apply(lambda c: (c - c.mean()) / c.std(ddof=0)).fillna(0.0)
    s = s.assign(indice_media=z.mean(axis=1))
    u, sv, vt = np.linalg.svd(z.to_numpy() - z.to_numpy().mean(0), full_matrices=False)
    pc1 = vt[0] * np.sign(vt[0].sum())
    s["indice_pc1"] = z.to_numpy() @ pc1
    return s, dict(zip(componentes, pc1.tolist()))


def defasar(s):
    s = s.sort_values(["deputado_id", "semestre"]).copy()
    s["defeccao_seguinte"] = s.groupby("deputado_id")["defeccao"].shift(-1)
    return s


def validade_preditiva(s, col_indice="indice_media"):
    """Compara o erro quadrático fora da amostra (validação por deputado em 5 partes) com e sem o índice."""
    from sklearn.model_selection import GroupKFold
    from sklearn.linear_model import LinearRegression
    d = s.dropna(subset=["defeccao_seguinte", "defeccao", col_indice])
    X0, X1, y = d[["defeccao"]], d[["defeccao", col_indice]], d["defeccao_seguinte"]
    e0, e1 = [], []
    for tr, te in GroupKFold(5).split(d, groups=d["deputado_id"]):
        for X, e in ((X0, e0), (X1, e1)):
            m = LinearRegression().fit(X.iloc[tr], y.iloc[tr])
            e.append(float(np.mean((m.predict(X.iloc[te]) - y.iloc[te]) ** 2)))
    return {"eqm_sem_indice": float(np.mean(e0)), "eqm_com_indice": float(np.mean(e1)), "n": int(len(d))}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--legs", nargs="+", type=int, default=[57])
    a = ap.parse_args(argv)
    res = {}
    for leg in a.legs:
        r = {}
        pp = script.ler_painel(__file__, f"proposicao_leg{leg}")
        m = E.feols("fora ~ urgencia | deputado_id + partido_mes", pp.dropna(subset=["fora"]),
                    vcov={"CRV1": "deputado_id+proposicao_id"})
        r["h1_fora"] = E.coeficientes(m, ["urgencia"]).to_dict("records")
        m = E.feols("defeccao_plen ~ urgencia | deputado_id + partido_mes", pp.dropna(subset=["defeccao_plen"]),
                    vcov={"CRV1": "deputado_id+proposicao_id"})
        r["h1_plenario"] = E.coeficientes(m, ["urgencia"]).to_dict("records")
        s, cargas = indice(script.ler_painel(__file__, f"semestre_leg{leg}"))
        s = defasar(s)
        s["partido_sem"] = s["partido"] + "_" + s["semestre"]
        r["cargas_pc1"] = cargas
        m = E.feols("defeccao_seguinte ~ indice_media + defeccao | partido_sem", s.dropna(subset=["defeccao_seguinte"]),
                    vcov={"CRV1": "deputado_id"})
        r["h3"] = E.coeficientes(m, ["indice_media", "defeccao"]).to_dict("records")
        r["h3_fora_da_amostra"] = validade_preditiva(s)
        res[f"leg{leg}"] = r
    print(E.salvar_resultados(AQUI, res))


if __name__ == "__main__":
    main()
