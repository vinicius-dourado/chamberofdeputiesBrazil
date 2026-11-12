"""Gera painel/painel.html (página interativa) a partir de dados/leg57/embeddings e painel/modelo.html."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

P = Path("dados/leg57")
E = P / "embeddings"
r = lambda n: pd.read_parquet(E / f"{n}.parquet")

dep = pd.read_parquet(P / "deputados.parquet"); dep["id"] = dep["id"].astype(int)
v = r("emb_votos"); vi = r("emb_votos_intra"); al = r("alinhamento"); tr = r("trajetoria_partidaria")
te = r("emb_temas"); sim = r("similaridades"); aval = json.loads((E / "avaliacao.json").read_text())

d = (v[["deputado_id", "nome", "siglaPartido", "siglaUf", "dim1", "dim2", "n_votos", "confiavel"]]
     .merge(vi[["deputado_id", "dim1", "dim2"]].rename(columns={"dim1": "i1", "dim2": "i2"}), on="deputado_id")
     .merge(al, on="deputado_id", how="left")
     .merge(tr[["deputado_id", "n_trocas", "sequencia_partidos", "deslocamento_dim1", "salto_partidario_dim1"]],
            on="deputado_id", how="left"))
d = d[d["confiavel"]].reset_index(drop=True)

# grupo do partido pela mediana do partido no eixo governo×oposição
med = d.groupby("siglaPartido")["dim1"].median()
grupo = med.map(lambda x: "opo" if x < -0.8 else ("gov" if x > 0.45 else "cen"))
d["g"] = d["siglaPartido"].map(grupo)

# temas principais
tcols = [c for c in te.columns if c.startswith("t_")]
prop = te.set_index("deputado_id")[tcols].pow(2)
top = {i: [[c[2:], round(float(x) * 100)] for c, x in row.nlargest(3).items() if x > 0.03]
       for i, row in prop[te.set_index("deputado_id")["confiavel"]].iterrows()}

# vizinhos por aspecto
idx = {i: k for k, i in enumerate(d["deputado_id"])}
aspectos = {"media": "prox_media", "votos": "prox_votos", "frentes": "prox_frentes",
            "temas": "prox_temas", "fala": "prox_discursos_fala"}
s = sim[sim["deputado_a"].isin(idx) & sim["deputado_b"].isin(idx)]
viz = {a: {} for a in aspectos}
for a, col in aspectos.items():
    x = s[["deputado_a", "deputado_b", col]].dropna()
    x = pd.concat([x, x.rename(columns={"deputado_a": "deputado_b", "deputado_b": "deputado_a"})])
    x = x.sort_values(col, ascending=False).groupby("deputado_a").head(5)
    for i, g in x.groupby("deputado_a"):
        viz[a][i] = [idx[j] for j in g["deputado_b"]]

deps = []
for row in d.itertuples():
    deps.append({"n": row.nome, "p": row.siglaPartido, "u": row.siglaUf, "g": row.g,
                 "x": round(row.dim1, 3), "y": round(row.dim2, 3), "i1": round(row.i1, 2),
                 "gov": None if pd.isna(row.taxa_alinhamento_governo) else round(row.taxa_alinhamento_governo * 100),
                 "par": None if pd.isna(row.taxa_alinhamento_partido) else round(row.taxa_alinhamento_partido * 100),
                 "nv": int(row.n_votos), "seq": row.sequencia_partidos if row.n_trocas and row.n_trocas > 0 else None,
                 "t": top.get(row.deputado_id, []),
                 "v": {a: viz[a].get(row.deputado_id, []) for a in aspectos}})

# coesão por partido
co = (d.groupby("siglaPartido").agg(n=("dim1", "size"), med=("dim1", "median"),
                                    p10=("dim1", lambda s: s.quantile(.1)), p90=("dim1", lambda s: s.quantile(.9)),
                                    dp=("dim1", "std"), disc=("taxa_alinhamento_partido", "mean"))
      .query("n >= 8").sort_values("med").reset_index())
coesao = [{"p": c.siglaPartido, "g": grupo[c.siglaPartido], "n": int(c.n), "med": round(c.med, 2),
           "p10": round(c.p10, 2), "p90": round(c.p90, 2), "dp": round(c.dp, 2), "disc": round(c.disc * 100)}
          for c in co.itertuples()]

# pivôs e dissidentes
mp = d["dim1"].median()
piv = d.assign(dist=(d["dim1"] - mp).abs()).nsmallest(8, "dist")
d["desvio"] = d["dim1"] - d["siglaPartido"].map(med)
fmt = lambda t: [{"i": idx[x.deputado_id], "d": round(x.desvio, 2)} for x in t.itertuples()]

# temas × posição
tt = te[te["confiavel"]].merge(d[["deputado_id", "dim1"]], on="deputado_id")
corr = tt[tcols].pow(2).corrwith(tt["dim1"]).sort_values()
temas = [{"t": k[2:], "c": round(float(x), 2)} for k, x in pd.concat([corr.head(6), corr.tail(6)]).items()]

# trocas
t2 = d.dropna(subset=["deslocamento_dim1", "salto_partidario_dim1"])
trocas = [{"i": idx[x.deputado_id], "s": round(x.salto_partidario_dim1, 2), "d": round(x.deslocamento_dim1, 2)}
          for x in t2.itertuples()]
rt = float(np.corrcoef(t2["salto_partidario_dim1"], t2["deslocamento_dim1"])[0, 1])

# falam parecido, votam diferente (partidos diferentes)
part = d.set_index("deputado_id")["siglaPartido"]
fv = s.dropna(subset=["prox_discursos_fala", "prox_votos"])
fv = fv[(fv["prox_discursos_fala"] > 0.985) & (part.reindex(fv["deputado_a"]).to_numpy() != part.reindex(fv["deputado_b"]).to_numpy())]
fv = fv.sort_values("prox_votos").head(8)
falavoto = [{"a": idx[x.deputado_a], "b": idx[x.deputado_b], "f": round(x.prox_discursos_fala * 100, 1),
             "v": round(x.prox_votos * 100, 1)} for x in fv.itertuples()]

rep = aval["representacoes"]
dados = {"deps": deps, "coesao": coesao, "mediana": round(float(mp), 2),
         "pivos": [idx[i] for i in piv["deputado_id"]],
         "gov_mais": fmt(d.nlargest(6, "desvio")), "opo_mais": fmt(d.nsmallest(6, "desvio")),
         "temas": temas, "trocas": trocas, "r_trocas": round(rt, 2), "falavoto": falavoto,
         "aval": aval["votos"], "rep": rep,
         "n": {"deputados": int(len(dep)), "votos": 473323, "votacoes": 1604, "discursos": 52589,
               "frentes": 320, "proposicoes": 239509, "trocaram": int((tr["n_trocas"] > 0).sum())}}
html = Path("painel/modelo.html").read_text(encoding="utf-8").replace("/*DADOS*/null", json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
Path("painel/painel.html").write_text(html, encoding="utf-8")
print("painel/painel.html", len(html) // 1024, "KB;", len(deps), "deputados;", rt)
print(json.dumps({k: dados[k] for k in ["coesao", "temas", "falavoto", "aval"]}, ensure_ascii=False)[:1500])
