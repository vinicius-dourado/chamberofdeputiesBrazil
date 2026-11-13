"""
Artigo 1 - Pontos ideais das votações nominais da 57ª Legislatura da Câmara dos Deputados.

Script reprodutível: gera todos os números, tabelas e figuras de artigo.md a partir de
dados/leg57/*.parquet. Não altera nada fora desta pasta.

    pip install pandas pyarrow scipy scikit-learn matplotlib
    python artigos/01-pontos-ideais/analise.py            # tudo (~25 min em 4 núcleos)
    python artigos/01-pontos-ideais/analise.py --etapas cv final   # só algumas etapas
    python artigos/01-pontos-ideais/analise.py --refazer  # ignora o cache

Saídas (nesta pasta):
    resultados.json     todos os números citados no texto
    tabelas/*.csv|.md   tabelas do artigo
    figuras/*.png       figuras do artigo
    cache/              resultados intermediários (não versionado)

O modelo é o mesmo de embeddings_deputados.py (ajustar_irt), reimplementado aqui com pesos
por observação, partida a quente e semente explícita - necessários para o bootstrap e para as
análises de sensibilidade. A etapa "reproducao" confere a reimplementação contra a função
original, na mesma partição treino/teste.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import argparse
import json
import pickle
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
DADOS = RAIZ / "dados" / "leg57"
CACHE, FIGS, TABS = AQUI / "cache", AQUI / "figuras", AQUI / "tabelas"
NPROC = 4
PADRAO = dict(lam_x=1.0, lam_b=0.04, lam_a=0.01, lam_d=4.0)   # hiperparâmetros do projeto
MIN_VOTOS = 50                                                # deputado/período "confiável"

ESQUERDA = {"PT", "PCdoB", "PV", "PSOL", "REDE", "PSB", "PDT"}
DIREITA_OPOS = {"PL", "NOVO", "MISSÃO"}
BLOCOS = ["Esquerda", "Centro e centrão", "Direita de oposição"]

# Codificação ordinal "campo ideológico" (esquerda = -1, centro = 0, direita = +1), adotada
# pelos autores a partir da classificação convencional da literatura brasileira (p.ex. Bolognesi,
# Ribeiro e Codato, 2023). É deliberadamente grosseira: os escores numéricos daquele survey não
# puderam ser conferidos e não são usados. O ponto decisivo do teste não depende de nuances: PL,
# NOVO, PP, REPUBLICANOS e UNIÃO estão todos à direita em qualquer classificação usual.
CAMPO = {**{p: -1 for p in ["PSOL", "PCdoB", "PT", "PV", "REDE", "PSB", "PDT"]},
         **{p: 0 for p in ["MDB", "PSD", "PSDB", "CIDADANIA", "PODE", "SOLIDARIEDADE", "AVANTE", "PRD"]},
         **{p: 1 for p in ["PL", "NOVO", "MISSÃO", "PP", "REPUBLICANOS", "UNIÃO"]}}
ROT_CAMPO = {-1: "esquerda", 0: "centro", 1: "direita"}


def bloco_de(partido):
    return BLOCOS[0] if partido in ESQUERDA else BLOCOS[2] if partido in DIREITA_OPOS else BLOCOS[1]


# ============================================================================ modelo
def ajustar(i, j, y, n_i, n_j, ndim, base=None, w=None, th0=None, semente=0,
            lam_x=1.0, lam_b=0.04, lam_a=0.01, lam_d=4.0, maxiter=15000):
    """IRT 2PL multidimensional: P(Sim) = σ(a_j + b_j·x_i); x_i = u_base(i) + δ_i se base dado.
    Máxima verossimilhança penalizada (priors normais), L-BFGS. w: pesos por observação."""
    n_u = 0 if base is None else int(base.max()) + 1
    cortes = np.cumsum([0, n_j, n_j * ndim, n_i * ndim, n_u * ndim])
    lam_dd = lam_x if base is None else lam_d
    w = np.ones(len(y)) if w is None else w

    def desemp(th):
        a = th[cortes[0]:cortes[1]]
        b = th[cortes[1]:cortes[2]].reshape(n_j, ndim)
        d = th[cortes[2]:cortes[3]].reshape(n_i, ndim)
        u = th[cortes[3]:cortes[4]].reshape(n_u, ndim)
        return a, b, d, u, (d + u[base] if base is not None else d)

    def f(th):
        a, b, d, u, x = desemp(th)
        z = a[j] + np.einsum("nk,nk->n", b[j], x[i])
        p = expit(z)
        ll = -np.sum(w * (y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)))
        pen = lam_a * a @ a + lam_b * np.sum(b * b) + lam_dd * np.sum(d * d) + lam_x * np.sum(u * u)
        r = w * (p - y)
        ga = np.bincount(j, r, n_j) + 2 * lam_a * a
        gb = np.stack([np.bincount(j, r * x[i, k], n_j) for k in range(ndim)], 1).reshape(n_j, ndim) \
            + 2 * lam_b * b
        gx = np.stack([np.bincount(i, r * b[j, k], n_i) for k in range(ndim)], 1).reshape(n_i, ndim)
        gd = gx + 2 * lam_dd * d
        gu = np.zeros((n_u, ndim))
        if base is not None:
            for k in range(ndim):
                gu[:, k] = np.bincount(base, gx[:, k], n_u)
            gu += 2 * lam_x * u
        return ll + pen, np.concatenate([ga, gb.ravel(), gd.ravel(), gu.ravel()])

    if th0 is None:
        th0 = np.random.default_rng(semente).normal(0, 0.1, cortes[-1])
    res = minimize(f, th0, jac=True, method="L-BFGS-B", options={"maxiter": maxiter, "maxfun": 2 * maxiter})
    a, b, d, u, x = desemp(res.x)
    return dict(a=a, b=b, d=d, u=u, x=x, th=res.x, convergiu=bool(res.success), nll=float(res.fun),
                nit=int(res.nit))


def ajustar_quad(i, j, y, n_i, n_j, base, semente=0, lam_x=1.0, lam_b=0.04, lam_a=0.01, lam_d=4.0,
                 lam_c=None, maxiter=15000):
    """Modelo 1D com termo quadrático por votação: P(Sim) = σ(a_j + b_j x_i + c_j x_i²).
    Utilidade de proximidade num único eixo gera, em 2D linear, a 'ferradura' (extremos × meio);
    este modelo captura essa não linearidade sem uma segunda dimensão latente."""
    lam_c = lam_b if lam_c is None else lam_c
    n_u = int(base.max()) + 1
    cortes = np.cumsum([0, n_j, n_j, n_j, n_i, n_u])

    def desemp(th):
        a, b, c = th[:cortes[1]], th[cortes[1]:cortes[2]], th[cortes[2]:cortes[3]]
        d, u = th[cortes[3]:cortes[4]], th[cortes[4]:cortes[5]]
        return a, b, c, d, u, d + u[base]

    def f(th):
        a, b, c, d, u, x = desemp(th)
        xi = x[i]
        p = expit(a[j] + b[j] * xi + c[j] * xi ** 2)
        ll = -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12))
        pen = lam_a * a @ a + lam_b * b @ b + lam_c * c @ c + lam_d * d @ d + lam_x * u @ u
        r = p - y
        ga = np.bincount(j, r, n_j) + 2 * lam_a * a
        gb = np.bincount(j, r * xi, n_j) + 2 * lam_b * b
        gc = np.bincount(j, r * xi ** 2, n_j) + 2 * lam_c * c
        gx = np.bincount(i, r * (b[j] + 2 * c[j] * xi), n_i)
        gd = gx + 2 * lam_d * d
        gu = np.bincount(base, gx, n_u) + 2 * lam_x * u
        return ll + pen, np.concatenate([ga, gb, gc, gd, gu])

    th0 = np.random.default_rng(semente).normal(0, 0.1, cortes[-1])
    res = minimize(f, th0, jac=True, method="L-BFGS-B", options={"maxiter": maxiter, "maxfun": 2 * maxiter})
    a, b, c, d, u, x = desemp(res.x)
    return dict(a=a, b=b, c=c, x=x, u=u, convergiu=bool(res.success), nll=float(res.fun), _f=f, th=res.x)


def prever_quad(m, i, j):
    xi = m["x"][i]
    return expit(m["a"][j] + m["b"][j] * xi + m["c"][j] * xi ** 2)


def prever(m, i, j):
    return expit(m["a"][j] + np.einsum("nk,nk->n", m["b"][j], m["x"][i]))


def acc(p, y):
    return float(np.mean((p > 0.5) == (y > 0.5)))


def logloss(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def procrustes(x, ref, w=None):
    """Rotação/reflexão ortogonal + translação (sem escala) que aproxima x de ref."""
    w = np.ones(len(x)) if w is None else w
    mx, mr = np.average(x, 0, w), np.average(ref, 0, w)
    u, _, vt = np.linalg.svd(((x - mx) * w[:, None]).T @ (ref - mr))
    q = u @ vt
    return lambda z: (z - mx) @ q + mr


# ============================================================================ dados
def carregar_votos():
    v = pd.read_parquet(DADOS / "votos.parquet")
    v["deputado_id"] = v["deputado_id"].astype(int)
    if os.environ.get("TESTE_RAPIDO"):   # teste de fumaça: ~10% das votações
        ids = v["idVotacao"].drop_duplicates().sample(frac=0.1, random_state=0)
        v = v[v["idVotacao"].isin(ids)]
    return v


def preparar(v, min_minoria=0.025, obstrucao="nao", abstencao="fora"):
    """Mesma regra de embeddings_deputados.preparar_votos, com variações para a robustez."""
    mapa = {"Sim": 1.0, "Não": 0.0}
    if obstrucao == "nao":
        mapa["Obstrução"] = 0.0
    if abstencao == "nao":
        mapa["Abstenção"] = 0.0
    v = v[v["voto"].isin(mapa)].copy()
    v["y"] = v["voto"].map(mapa)
    minoria = v.groupby("idVotacao")["y"].agg(lambda s: min(s.mean(), 1 - s.mean()))
    v = v[v["idVotacao"].isin(minoria[minoria >= min_minoria].index)]
    return v.reset_index(drop=True)


class Painel:
    """Índices do modelo: linhas = período de filiação (deputado|partido), colunas = votações."""

    def __init__(self, v):
        self.v = v
        per = v["deputado_id"].astype(str) + "|" + v["deputado_siglaPartido"]
        self.i, self.periodos = pd.factorize(per)
        self.j, self.votacoes = pd.factorize(v["idVotacao"])
        self.dep_periodo = self.periodos.str.split("|").str[0].astype(int)
        self.part_periodo = np.array(self.periodos.str.split("|").str[1])
        self.base, self.deps = pd.factorize(self.dep_periodo)
        self.y = v["y"].to_numpy()
        self.n_i, self.n_j, self.n_u = len(self.periodos), len(self.votacoes), len(self.deps)
        self.nv_periodo = np.bincount(self.i, minlength=self.n_i)
        self.nv_dep = np.bincount(self.base[self.i], minlength=self.n_u)
        # partido "principal" do deputado = aquele em que deu mais votos
        t = pd.DataFrame({"dep": self.dep_periodo, "part": self.part_periodo, "n": self.nv_periodo})
        t = t.sort_values("n", ascending=False).drop_duplicates("dep").set_index("dep")
        self.part_dep = t["part"].reindex(self.deps).to_numpy()

    def ajustar(self, ndim=2, mask=None, **kw):
        cfg = {**PADRAO, **kw}
        mk = slice(None) if mask is None else mask
        return ajustar(self.i[mk], self.j[mk], self.y[mk], self.n_i, self.n_j, ndim, base=self.base,
                       w=None if cfg.get("w") is None else cfg.pop("w")[mk],
                       **{k: x for k, x in cfg.items() if k != "w"})

    def final(self, ndim=2, **kw):
        """Ajuste com todos os votos, girado para eixos principais e orientado:
        dim1 > 0 = governista; dim2 > 0 = lado do PSOL."""
        m = self.ajustar(ndim, **kw)
        return self.orientar(m)

    def orientar(self, m):
        u = m["u"]
        conf = self.nv_dep >= MIN_VOTOS
        if conf.sum() < 20:          # amostras pequenas (teste de fumaça, recortes estreitos)
            conf = self.nv_dep >= np.median(self.nv_dep)
        mu = u[conf].mean(0)
        _, _, vt = np.linalg.svd(u[conf] - mu, full_matrices=False)
        R = vt.T.copy()
        gov = (self.v.assign(s=self.v["seguiu_orientacao_governo"].astype(float))
               .groupby("deputado_id")["s"].mean().reindex(self.deps).to_numpy())
        ok = ~np.isnan(gov)
        if np.corrcoef(((u - mu) @ R)[ok, 0], gov[ok])[0, 1] < 0:
            R[:, 0] *= -1
        if R.shape[1] > 1:
            psol = self.part_dep == "PSOL"
            if psol.any() and ((u - mu) @ R)[psol, 1].mean() < 0:
                R[:, 1] *= -1
        m = dict(m)
        m["u"] = (u - mu) @ R
        m["x"] = (m["x"] - mu) @ R
        m["a"] = m["a"] + m["b"] @ mu
        m["b"] = m["b"] @ R
        m["gov"] = gov
        m["R"], m["mu"] = R, mu
        return m


def particao_hash(v, frac=10):
    """Partição treino/teste determinística por célula (votação, deputado): a mesma célula fica no
    teste em qualquer variação de pré-processamento, o que torna as acurácias comparáveis."""
    h = pd.util.hash_pandas_object(v[["idVotacao", "deputado_id"]].astype(str), index=False).to_numpy()
    return (h % frac) == 0


def particao_original(n):
    """A partição treino/teste usada por embeddings_deputados.py (primeiro sorteio do RNG 42)."""
    return np.random.default_rng(42).random(n) < 0.10


# ====================================================================== infraestrutura
RES = {}
_G = {}


def em_cache(nome, fn, refazer):
    arq = CACHE / f"{nome}.pkl"
    if arq.exists() and not refazer:
        return pickle.loads(arq.read_bytes())
    t = time.time()
    out = fn()
    arq.write_bytes(pickle.dumps(out))
    print(f"  [{nome}] {time.time() - t:.0f}s", flush=True)
    return out


def paralelo(fn, tarefas):
    with Pool(NPROC) as pool:
        return pool.map(fn, tarefas, chunksize=1)


def tabela(df, nome, casas=3, index=False):
    """Salva CSV e Markdown da tabela."""
    df.to_csv(TABS / f"{nome}.csv", index=index)
    d = df.reset_index() if index else df
    linhas = ["| " + " | ".join(str(c) for c in d.columns) + " |", "|" + "---|" * len(d.columns)]
    for _, r in d.iterrows():
        cel = []
        for x in r:
            if isinstance(x, (float, np.floating)):
                cel.append("" if np.isnan(x) else f"{x:.{casas}f}".replace(".", ","))
            else:
                cel.append(str(x))
        linhas.append("| " + " | ".join(cel) + " |")
    (TABS / f"{nome}.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return df


# ============================================================================ etapas
def etapa_dados(P, bruto):
    vt = pd.read_parquet(DADOS / "votacoes.parquet")
    v = P.v
    r = {
        "votacoes_total": int(len(vt)),
        "votacoes_nominais": int(vt["tem_votos_nominais"].sum()),
        "votacoes_nominais_plenario": int((vt["tem_votos_nominais"] & (vt["siglaOrgao"] == "PLEN")).sum()),
        "votacoes_plenario_total": int((vt["siglaOrgao"] == "PLEN").sum()),
        "registros_voto_brutos": int(len(bruto)),
        "tipos_voto_brutos": {str(k): int(x) for k, x in bruto["voto"].value_counts(dropna=False).items()},
        "votos": int(len(v)), "votacoes": int(P.n_j), "deputados": int(P.n_u), "periodos": int(P.n_i),
        "deputados_confiaveis": int((P.nv_dep >= MIN_VOTOS).sum()),
        "periodos_confiaveis": int((P.nv_periodo >= MIN_VOTOS).sum()),
        "deputados_com_mais_de_um_periodo": int((np.bincount(P.base) > 1).sum()),
        "densidade_matriz": float(len(v) / (P.n_i * P.n_j)),
        "prop_sim": float(v["y"].mean()),
        "data_min": v["data"].min(), "data_max": v["data"].max(),
        "votacoes_plenario": int(v.loc[v["siglaOrgao"] == "PLEN", "idVotacao"].nunique()),
        "votacoes_comissoes": int(v.loc[v["siglaOrgao"] != "PLEN", "idVotacao"].nunique()),
        "votos_plenario": int((v["siglaOrgao"] == "PLEN").sum()),
        "votos_comissoes": int((v["siglaOrgao"] != "PLEN").sum()),
        "votacoes_ccjc": int(v.loc[v["siglaOrgao"] == "CCJC", "idVotacao"].nunique()),
        "obstrucao_na_amostra": int((v["voto"] == "Obstrução").sum()),
        "orientacao_fonte": {str(k): float(x) for k, x in
                             v["orientacao_fonte"].value_counts(dropna=False, normalize=True).items()},
        "orientacao_utilizavel": float(v["orientacao_partido"].isin(["Sim", "Não", "Obstrução"]).mean()),
        "orientacao_liberado": float((v["orientacao_partido"] == "Liberado").mean()),
        "orientacao_ausente": float(v["orientacao_partido"].isna().mean()),
    }
    por_ano = v.groupby(v["data"].str[:4]).agg(votacoes=("idVotacao", "nunique"), votos=("y", "size"))
    por_ano["no plenário"] = v[v["siglaOrgao"] == "PLEN"].groupby(v["data"].str[:4])["idVotacao"].nunique()
    por_ano["prop. Sim"] = v.groupby(v["data"].str[:4])["y"].mean()
    por_ano.index.name = "ano"
    tabela(por_ano.reset_index(), "t1_dados_por_ano")
    r["por_ano"] = por_ano.reset_index().to_dict("records")
    RES["dados"] = r


def _reproducao(_):
    """Confere a reimplementação contra embeddings_deputados.ajustar_irt na mesma partição."""
    P = _G["P"]
    sys.path.insert(0, str(RAIZ))
    import embeddings_deputados as E
    E.RNG = np.random.default_rng(42)
    v0 = E.preparar_votos(DADOS)
    assert len(v0) == len(P.v)
    teste = E.RNG.random(len(P.y)) < 0.10
    tr = ~teste
    m0 = E.ajustar_irt(P.i[tr], P.j[tr], P.y[tr], P.n_i, P.n_j, 2, base=P.base, lam_d=4.0)
    p0 = E.predizer(m0, P.i[teste], P.j[teste])
    m1 = P.ajustar(2, mask=tr)
    p1 = prever(m1, P.i[teste], P.j[teste])
    return {"original_acuracia": acc(p0, P.y[teste]), "original_logloss": logloss(p0, P.y[teste]),
            "reimpl_acuracia": acc(p1, P.y[teste]), "reimpl_logloss": logloss(p1, P.y[teste]),
            "nll_original": float(m0["nll"]), "nll_reimpl": m1["nll"],
            "concordancia_previsoes": float(np.mean((p0 > .5) == (p1 > .5))),
            "corr_probabilidades": float(np.corrcoef(p0, p1)[0, 1]),
            "n_teste": int(teste.sum())}


# ----------------------------------------------------------------- validação cruzada
N_FOLDS = 10
DIMS = [1, 2, 3, 4]


def _cv_tarefa(t):
    fold, tipo = t
    P = _G["P"]
    te = _G["fold"] == fold
    tr = ~te
    if tipo == "partido":      # um ponto por partido (sem variação individual)
        ip, _ = pd.factorize(P.v["deputado_siglaPartido"])
        m = ajustar(ip[tr], P.j[tr], P.y[tr], ip.max() + 1, P.n_j, 2, **PADRAO)
        return fold, tipo, prever(m, ip[te], P.j[te])
    m = P.ajustar(tipo, mask=tr)
    return fold, tipo, prever(m, P.i[te], P.j[te])


def _cv_quad_tarefa(fold):
    P = _G["P"]
    te = _G["fold"] == fold
    tr = ~te
    m = ajustar_quad(P.i[tr], P.j[tr], P.y[tr], P.n_i, P.n_j, P.base, **PADRAO)
    return fold, prever_quad(m, P.i[te], P.j[te]), m["convergiu"]


def etapa_cv_quad(P):
    pred = np.full(len(P.y), np.nan)
    conv = []
    for f, p, c in paralelo(_cv_quad_tarefa, list(range(N_FOLDS))):
        pred[_G["fold"] == f] = p
        conv.append(c)
    return pred, conv


def etapa_cv(P):
    fold = _G["fold"]
    saida = paralelo(_cv_tarefa, [(f, t) for f in range(N_FOLDS) for t in DIMS + ["partido"]])
    n = len(P.y)
    pred = {t: np.full(n, np.nan) for t in DIMS + ["partido"]}
    for f, t, p in saida:
        pred[t][fold == f] = p
    # baselines calculadas só com os votos de treino de cada fold
    v = P.v
    gp, _ = pd.factorize(v["deputado_siglaPartido"] + "|" + v["idVotacao"])
    ori = v["orientacao_partido"].map({"Sim": 1.0, "Não": 0.0, "Obstrução": 0.0}).to_numpy()
    b_mai, b_ori, b_par = np.zeros(n), np.zeros(n), np.zeros(n)
    for f in range(N_FOLDS):
        te = fold == f
        tr = ~te
        s = np.bincount(P.j[tr], P.y[tr], P.n_j)
        c = np.bincount(P.j[tr], minlength=P.n_j)
        mai = np.where(c > 0, s / np.maximum(c, 1), 0.5)
        sp = np.bincount(gp[tr], P.y[tr], gp.max() + 1)
        cp = np.bincount(gp[tr], minlength=gp.max() + 1)
        par = np.where(cp > 0, sp / np.maximum(cp, 1), np.nan)
        b_mai[te] = mai[P.j[te]]
        b_ori[te] = np.where(np.isnan(ori[te]), mai[P.j[te]], ori[te])
        pp = par[gp[te]]
        b_par[te] = np.where(np.isnan(pp) | (pp == 0.5), mai[P.j[te]], pp)
    pred["maioria"], pred["orientacao"], pred["maioria_partido"] = b_mai, b_ori, b_par
    return pred


def resumo_cv(P, pred):
    y, fold = P.y, _G["fold"]
    nomes = {"maioria": "Maioria da votação (0D)", "orientacao": "Orientação da bancada",
             "maioria_partido": "Maioria do partido na votação", "partido": "IRT 2D, um ponto por partido",
             1: "IRT 1D", "quad": "IRT 1D quadrático", 2: "IRT 2D", 3: "IRT 3D", 4: "IRT 4D"}
    linhas = []
    err_mai = (pred["maioria"] > .5) != (y > .5)
    for k, nome in nomes.items():
        p = pred[k]
        accs = np.array([acc(p[fold == f], y[fold == f]) for f in range(N_FOLDS)])
        err = (p > .5) != (y > .5)
        prob = k not in ("orientacao",)
        linhas.append({"modelo": nome, "acurácia": accs.mean(), "dp entre partições": accs.std(ddof=1),
                       "APRE": 1 - err.sum() / err_mai.sum(),
                       "log-loss": logloss(p, y) if prob else np.nan,
                       "GMP": float(np.exp(-logloss(p, y))) if prob else np.nan})
    t = pd.DataFrame(linhas)
    tabela(t, "t2_validacao_cruzada", casas=4)
    r = {l["modelo"]: {k: float(x) for k, x in l.items() if k != "modelo"} for l in linhas}
    # ganhos pareados entre dimensões (diferença por partição)
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4)]:
        pa = pred["maioria"] if a == 0 else pred[a]
        d = np.array([acc(pred[b][fold == f], y[fold == f]) - acc(pa[fold == f], y[fold == f])
                      for f in range(N_FOLDS)])
        r[f"ganho_{a}D_{b}D"] = {"media": float(d.mean()), "dp": float(d.std(ddof=1)),
                                 "min": float(d.min()), "max": float(d.max())}
    d = np.array([acc(pred[2][fold == f], y[fold == f]) - acc(pred["maioria_partido"][fold == f], y[fold == f])
                  for f in range(N_FOLDS)])
    r["ganho_2D_vs_maioria_partido"] = {"media": float(d.mean()), "dp": float(d.std(ddof=1)),
                                        "min": float(d.min()), "max": float(d.max())}
    # IC 95% por bootstrap de proposições (sem reajuste: reamostra os votos de teste em blocos)
    cl = _G["cluster"][P.j]
    ncl = cl.max() + 1
    W = np.random.default_rng(77).multinomial(ncl, np.full(ncl, 1 / ncl), size=1000).astype(float)
    nc = np.bincount(cl, minlength=ncl)

    def ic(d):
        sc = np.bincount(cl, d, minlength=ncl)
        bt = (W @ sc) / (W @ nc)
        return {"media": float(d.mean()), "ic": [float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))]}

    cor = {k: ((pred[k] > .5) == (y > .5)).astype(float) for k in pred}
    pl = lambda k: -(y * np.log(np.clip(pred[k], 1e-6, 1)) + (1 - y) * np.log(np.clip(1 - pred[k], 1e-6, 1)))
    for a, b in [(1, 2), (2, 3), ("quad", 2), (1, "quad"), ("maioria_partido", 2), ("orientacao", 2), ("partido", 2)]:
        r[f"ic_acuracia_{a}_para_{b}"] = ic(cor[b] - cor[a])
        if a != "orientacao":
            r[f"ic_logloss_{a}_para_{b}"] = ic(pl(b) - pl(a))
    r["cv_quad_convergiu"] = _G.get("cv_quad_conv")
    RES["cv"] = r

    # ---- o que as coordenadas acrescentam à orientação: por fonte da orientação
    v = P.v
    cat = np.where(v["orientacao_partido"].isin(["Sim", "Não", "Obstrução"]),
                   "orientada: " + v["orientacao_fonte"].fillna("?"),
                   np.where(v["orientacao_partido"] == "Liberado", "liberada", "sem orientação"))
    linhas = []
    for c in ["orientada: partido", "orientada: federacao", "orientada: bloco", "orientada: bloco (inferido)",
              "liberada", "sem orientação"]:
        mk = cat == c
        linhas.append({"situação da orientação": c, "votos": int(mk.sum()), "% dos votos": 100 * mk.mean(),
                       "orientação": acc(pred["orientacao"][mk], y[mk]) if c.startswith("orientada") else np.nan,
                       "maioria": acc(pred["maioria"][mk], y[mk]),
                       "maioria do partido": acc(pred["maioria_partido"][mk], y[mk]),
                       "IRT 1D": acc(pred[1][mk], y[mk]), "IRT 2D": acc(pred[2][mk], y[mk])})
    t = pd.DataFrame(linhas)
    tabela(t, "t3_por_fonte_orientacao")
    RES["por_fonte"] = t.to_dict("records")
    orientado = np.char.startswith(cat.astype(str), "orientada")
    seguiu = (pred["orientacao"] > .5) == (y > .5)
    dis = orientado & ~seguiu
    RES["dissidencia"] = {
        "prop_votos_orientados": float(orientado.mean()),
        "taxa_disciplina": float(seguiu[orientado].mean()),
        "n_dissidentes": int(dis.sum()),
        "irt2d_acerta_dissidentes": acc(pred[2][dis], y[dis]),
        "irt1d_acerta_dissidentes": acc(pred[1][dis], y[dis]),
        "maioria_partido_acerta_dissidentes": acc(pred["maioria_partido"][dis], y[dis]),
        "irt2d_acerta_disciplinados": acc(pred[2][orientado & seguiu], y[orientado & seguiu]),
        "orientacao_so_orientados": acc(pred["orientacao"][orientado], y[orientado]),
        "irt2d_so_orientados": acc(pred[2][orientado], y[orientado]),
        "irt2d_nao_orientados": acc(pred[2][~orientado], y[~orientado]),
        "maioria_nao_orientados": acc(pred["maioria"][~orientado], y[~orientado]),
    }
    # ---- ganho da 2ª dimensão por partido e por órgão
    part = v["deputado_siglaPartido"].to_numpy()
    linhas = []
    for pa in pd.Series(part).value_counts().index:
        mk = part == pa
        if mk.sum() < 2000:
            continue
        linhas.append({"partido": pa, "votos": int(mk.sum()), "maioria": acc(pred["maioria"][mk], y[mk]),
                       "orientação": acc(pred["orientacao"][mk], y[mk]),
                       "IRT 1D": acc(pred[1][mk], y[mk]), "IRT 2D": acc(pred[2][mk], y[mk]),
                       "IRT 3D": acc(pred[3][mk], y[mk])})
    t = pd.DataFrame(linhas)
    t["ganho 1D→2D"] = t["IRT 2D"] - t["IRT 1D"]
    t["ganho 2D→3D"] = t["IRT 3D"] - t["IRT 2D"]
    t = t.sort_values("ganho 1D→2D", ascending=False)
    tabela(t, "t4_ganho_por_partido")
    RES["ganho_por_partido"] = t.to_dict("records")
    org = np.where(v["siglaOrgao"] == "PLEN", "Plenário", np.where(v["siglaOrgao"] == "CCJC", "CCJC",
                                                                 "Outras comissões"))
    linhas = []
    for o in ["Plenário", "CCJC", "Outras comissões"]:
        mk = org == o
        linhas.append({"órgão": o, "votações": int(v.loc[mk, "idVotacao"].nunique()), "votos": int(mk.sum()),
                       "maioria": acc(pred["maioria"][mk], y[mk]), "orientação": acc(pred["orientacao"][mk], y[mk]),
                       "maioria do partido": acc(pred["maioria_partido"][mk], y[mk]),
                       "IRT 1D": acc(pred[1][mk], y[mk]), "IRT 2D": acc(pred[2][mk], y[mk]),
                       "IRT 3D": acc(pred[3][mk], y[mk])})
    t = pd.DataFrame(linhas)
    tabela(t, "t9a_cv_por_orgao")
    RES["cv_por_orgao"] = t.to_dict("records")
    ano = v["data"].str[:4].to_numpy()
    RES["cv_por_ano"] = [{"ano": a, "maioria": acc(pred["maioria"][ano == a], y[ano == a]),
                          "orientação": acc(pred["orientacao"][ano == a], y[ano == a]),
                          "IRT 1D": acc(pred[1][ano == a], y[ano == a]),
                          "IRT 2D": acc(pred[2][ano == a], y[ano == a])} for a in sorted(set(ano))]


# ------------------------------------------------- metade/metade e recortes por orientação
def _recorte_tarefa(nome):
    P = _G["P"]
    if nome == "metades":
        # u estimado só com as votações pares; alinhamento ao Governo medido só nas ímpares
        par = (P.j % 2) == 0
        m = P.orientar(P.ajustar(2, mask=par))
        imp = P.v[~par]
        g = (imp.assign(s=imp["seguiu_orientacao_governo"].astype(float)).groupby("deputado_id")["s"].mean()
             .reindex(P.deps).to_numpy())
        nv = np.bincount(P.base[P.i[par]], minlength=P.n_u)
        return nome, {"u": m["u"], "gov_impares": g, "nv": nv}
    O = _G["O"]
    g, pl, psol = O["Governo"].to_numpy(), O["PL"].to_numpy(), O["PSOL-REDE"].to_numpy()
    sel = {"governo_igual_PL": (g == pl), "governo_oposto_PL": (g == -pl),
           "governo_oposto_PSOL": (g == -psol)}[nome] & ~np.isnan(g) & ~np.isnan(pl if "PL" in nome else psol)
    mk = sel[P.j]
    if mk.sum() < 1000:
        return nome, None
    P2 = Painel(P.v[mk].reset_index(drop=True))
    m = P2.final(2)
    return nome, {"votacoes": int(sel.sum()), "votos": int(mk.sum()), "u": m["u"], "deps": np.asarray(P2.deps),
                  "nv": P2.nv_dep, "part": P2.part_dep, "autovalores": np.linalg.eigvalsh(
                      np.cov(m["u"][P2.nv_dep >= min(MIN_VOTOS, np.median(P2.nv_dep))].T))[::-1]}


def etapa_recortes(P, m):
    from scipy.stats import pearsonr
    saida = dict(paralelo(_recorte_tarefa, ["metades", "governo_igual_PL", "governo_oposto_PL",
                                            "governo_oposto_PSOL"]))
    r = {}
    h = saida["metades"]
    ok = (h["nv"] >= MIN_VOTOS) & ~np.isnan(h["gov_impares"])
    r["metades_r_dim1_gov"] = float(pearsonr(h["u"][ok, 0], h["gov_impares"][ok])[0])
    r["metades_r_dim2_gov"] = float(pearsonr(h["u"][ok, 1], h["gov_impares"][ok])[0])
    r["metades_n"] = int(ok.sum())
    lin = []
    for nome, rot in [("governo_igual_PL", "Governo e PL orientam igual"),
                      ("governo_oposto_PL", "Governo e PL orientam opostos"),
                      ("governo_oposto_PSOL", "Governo e PSOL-REDE orientam opostos")]:
        o = saida[nome]
        if o is None:
            continue
        conf = o["nv"] >= min(MIN_VOTOS, np.median(o["nv"]))
        d = pd.DataFrame({"p": o["part"], "d1": o["u"][:, 0], "d2": o["u"][:, 1]})[conf]
        med = d.groupby("p")[["d1", "d2"]].mean()
        l = {"recorte": rot, "votações": o["votacoes"], "votos": o["votos"],
             "var. dim1 / total": float(o["autovalores"][0] / o["autovalores"].sum())}
        for pa in ["PSOL", "PT", "PSB", "MDB", "PSD", "UNIÃO", "PP", "REPUBLICANOS", "PL", "NOVO"]:
            l[pa] = float(med.loc[pa, "d1"]) if pa in med.index else np.nan
        # correlação da dim1 do recorte com a dim1 e a dim2 do modelo completo
        ref = pd.DataFrame(m["u"], index=P.deps)
        dd = pd.Index(o["deps"])[conf]
        l["r com dim1 completa"] = float(np.corrcoef(o["u"][conf, 0], ref.loc[dd, 0])[0, 1])
        l["r com dim2 completa"] = float(np.corrcoef(o["u"][conf, 0], ref.loc[dd, 1])[0, 1])
        lin.append(l)
    t = pd.DataFrame(lin)
    tabela(t, "t7b_recortes_orientacao", casas=2)
    r["recortes"] = lin
    RES["recortes"] = r


# ------------------------------------------------------------- ajuste final e estrutura
def _final_tarefa(k):
    return _G["P"].final(k)


def ajuste_dentro_da_amostra(P, finais):
    linhas = []
    y = P.y
    mai = (np.bincount(P.j, y, P.n_j) / np.bincount(P.j, minlength=P.n_j))[P.j]
    err0 = ((mai > .5) != (y > .5)).sum()
    for k, m in finais.items():
        p = prever(m, P.i, P.j)
        err = ((p > .5) != (y > .5)).sum()
        linhas.append({"dimensões": k, "classificação correta": 1 - err / len(y), "APRE": 1 - err / err0,
                       "GMP": float(np.exp(-logloss(p, y))), "parâmetros": int(len(m["th"])),
                       "convergiu": m["convergiu"]})
    t = pd.DataFrame(linhas)
    tabela(t, "t2b_ajuste_dentro_da_amostra", casas=4)
    RES["dentro_da_amostra"] = t.to_dict("records")
    RES["dentro_da_amostra_maioria"] = float(1 - err0 / len(y))


def orientacoes_por_votacao(P):
    """Orientação (Sim=+1, Não/Obstrução=-1) de bancadas-chave em cada votação."""
    o = pd.read_parquet(DADOS / "votacoes_orientacoes.parquet")
    o["b"] = o["siglaBancada"].str.strip().str.upper()
    chave = {"GOVERNO": "Governo", "OPOSIÇÃO": "Oposição", "MAIORIA": "Maioria", "MINORIA": "Minoria",
             "FDR PSOL-REDE": "PSOL-REDE", "FDR PT-PCDOB-PV": "PT-PCdoB-PV", "PL": "PL", "NOVO": "NOVO"}
    o = o[o["b"].isin(chave)].assign(b=lambda d: d["b"].map(chave))
    o["s"] = o["orientacao"].map({"Sim": 1.0, "Não": -1.0, "Obstrução": -1.0})
    w = o.dropna(subset=["s"]).pivot_table(index="idVotacao", columns="b", values="s", aggfunc="first")
    return w.reindex(P.votacoes)


def angulo_reta(graus):
    """Ângulo de uma direção em relação ao eixo 1, tratada como reta (sem sentido): [0°, 90°]."""
    a = abs(graus) % 180
    return float(min(a, 180 - a))


def estatisticas_h1(P, u, x, gov, campo):
    """Estatísticas do teste governo × campo ideológico, para a estimativa pontual e para cada
    réplica do bootstrap (gov e campo fixos; u e x variam)."""
    conf_d = P.nv_dep >= MIN_VOTOS
    conf_p = P.nv_periodo >= MIN_VOTOS
    ok = conf_d & ~np.isnan(gov) & ~np.isnan(campo)
    out = {}

    def ols(Xm, yv):
        Z = np.column_stack([np.ones(len(yv)), Xm])
        beta, *_ = np.linalg.lstsq(Z, yv, rcond=None)
        res = yv - Z @ beta
        return beta, float(1 - res @ res / np.sum((yv - yv.mean()) ** 2))

    bg, out["r2_plano_governo"] = ols(u[ok], gov[ok])
    bc, out["r2_plano_campo"] = ols(u[ok], campo[ok])
    out["theta_governo"] = angulo_reta(np.degrees(np.arctan2(bg[2], bg[1])))
    out["theta_campo"] = angulo_reta(np.degrees(np.arctan2(bc[2], bc[1])))
    out["angulo_entre_governo_e_campo"] = angulo_reta(np.degrees(np.arctan2(bg[2], bg[1]) - np.arctan2(bc[2], bc[1])))
    esq, dire = campo[ok] == -1, campo[ok] == 1
    _, out["r2_dim1_campo"] = ols(np.column_stack([esq, dire]).astype(float), u[ok, 0])
    _, out["r2_dim1_governo"] = ols(gov[ok][:, None], u[ok, 0])
    _, out["r2_dim1_ambos"] = ols(np.column_stack([esq, dire, gov[ok]]).astype(float), u[ok, 0])
    d = ok & (campo == 1)
    out["direita_r_dim1_governo"] = float(np.corrcoef(u[d, 0], gov[d])[0, 1])
    opos = conf_d & np.isin(P.part_dep, ["PL", "NOVO", "MISSÃO"])
    cen = conf_d & np.isin(P.part_dep, ["PP", "REPUBLICANOS", "UNIÃO"])
    e = ok & (campo == -1)
    out["fracao_distancia_direita_interna"] = float((u[cen, 0].mean() - u[opos, 0].mean())
                                                    / (u[e, 0].mean() - u[opos, 0].mean()))
    for pa in ["UNIÃO", "PP", "REPUBLICANOS"]:
        out[f"dif_{pa}_PL_dim1"] = float(x[conf_p & (P.part_periodo == pa), 0].mean()
                                         - x[conf_p & (P.part_periodo == "PL"), 0].mean())
    return out


def etapa_estrutura(P, m):
    v = P.v
    conf_p = P.nv_periodo >= MIN_VOTOS
    conf_d = P.nv_dep >= MIN_VOTOS
    r = {}
    # ---- partidos (pontos por período de filiação, com >= 50 votos)
    per = pd.DataFrame({"partido": P.part_periodo, "dim1": m["x"][:, 0], "dim2": m["x"][:, 1],
                        "n": P.nv_periodo})[conf_p]
    g = per.groupby("partido")
    tp = pd.DataFrame({"períodos": g.size(), "dim1 (média)": g["dim1"].mean(), "dim1 (dp)": g["dim1"].std(),
                       "dim2 (média)": g["dim2"].mean(), "dim2 (dp)": g["dim2"].std()})
    vv = v[v["seguiu_orientacao_governo"].notna()]
    tp["alinh. Governo"] = vv.groupby("deputado_siglaPartido")["seguiu_orientacao_governo"].apply(
        lambda s: s.astype(float).mean())
    tp["campo"] = [ROT_CAMPO.get(CAMPO.get(p), "") for p in tp.index]
    r["periodos_por_partido"] = {k: int(x) for k, x in tp["períodos"].items()}
    tp = tp[tp["períodos"] >= 3].sort_values("dim1 (média)")
    tabela(tp.reset_index(), "t5_partidos")
    r["partidos"] = tp.reset_index().to_dict("records")
    r["dp_dim1"], r["dp_dim2"] = float(m["u"][conf_d, 0].std()), float(m["u"][conf_d, 1].std())
    r["var_dim1_share"] = float(m["u"][conf_d, 0].var() / m["u"][conf_d].var(0).sum())
    # variância entre partidos / total (deputados confiáveis, partido principal)
    dd = pd.DataFrame({"p": P.part_dep, "d1": m["u"][:, 0], "d2": m["u"][:, 1]})[conf_d]
    for c in ["d1", "d2"]:
        entre = (dd.groupby("p")[c].transform("mean") - dd[c].mean()).pow(2).sum()
        r[f"eta2_partido_{c}"] = float(entre / (dd[c] - dd[c].mean()).pow(2).sum())

    # ---- dim1: governo x oposição ou esquerda x direita?
    gov = m["gov"]
    ok = conf_d & ~np.isnan(gov)
    par = (v.assign(s=v["seguiu_orientacao_partido"].astype(float)).groupby("deputado_id")["s"].mean()
           .reindex(P.deps).to_numpy())
    from scipy.stats import spearmanr, pearsonr
    r["r_dim1_alinh_governo"] = float(pearsonr(m["u"][ok, 0], gov[ok])[0])
    r["rho_dim1_alinh_governo"] = float(spearmanr(m["u"][ok, 0], gov[ok])[0])
    r["r_dim2_alinh_governo"] = float(pearsonr(m["u"][ok, 1], gov[ok])[0])
    okp = conf_d & ~np.isnan(par)
    r["r_dim2_alinh_partido"] = float(pearsonr(m["u"][okp, 1], par[okp])[0])
    # Teste invariante à rotação: a direção do plano que melhor prediz (MQO) o alinhamento ao
    # Governo e a que melhor prediz o campo ideológico; ângulo de cada uma com o eixo 1.
    campo = np.array([CAMPO.get(p, np.nan) for p in P.part_dep], float)
    okc = conf_d & ~np.isnan(campo)

    def direcao(alvo, mk):
        Z = np.column_stack([np.ones(mk.sum()), m["u"][mk]])
        beta, *_ = np.linalg.lstsq(Z, alvo[mk], rcond=None)
        res = alvo[mk] - Z @ beta
        r2 = 1 - res @ res / np.sum((alvo[mk] - alvo[mk].mean()) ** 2)
        ang = float(np.degrees(np.arctan2(beta[2], beta[1])))
        return ang, float(r2)

    r["angulo_governo"], r["r2_plano_governo"] = direcao(gov, ok)
    r["angulo_campo"], r["r2_plano_campo"] = direcao(campo, okc)
    r["h1"] = estatisticas_h1(P, m["u"], m["x"], gov, campo)
    # coeficientes da regressão conjunta dim1 ~ esquerda + direita + alinhamento (base: centro)
    okj = okc & ok
    Z = np.column_stack([np.ones(okj.sum()), campo[okj] == -1, campo[okj] == 1, gov[okj]]).astype(float)
    beta, *_ = np.linalg.lstsq(Z, m["u"][okj, 0], rcond=None)
    r["coef_dim1_conjunta"] = {"const": float(beta[0]), "esquerda": float(beta[1]), "direita": float(beta[2]),
                               "alinhamento_governo": float(beta[3])}
    r["r_dim1_campo"] = float(pearsonr(m["u"][okc, 0], campo[okc])[0])
    r["r_dim2_campo"] = float(pearsonr(m["u"][okc, 1], campo[okc])[0])
    r["r_campo_alinh_governo"] = float(pearsonr(campo[okc & ok], gov[okc & ok])[0])
    # dentro do campo da direita: o eixo 1 acompanha o governo, não a ideologia
    dire = okc & ok & (campo == 1)
    r["direita_n_deputados"] = int(dire.sum())
    r["direita_r_dim1_governo"] = float(pearsonr(m["u"][dire, 0], gov[dire])[0])
    opos = np.isin(P.part_dep, ["PL", "NOVO", "MISSÃO"])
    centrao_dir = np.isin(P.part_dep, ["PP", "REPUBLICANOS", "UNIÃO"])
    esq = okc & (campo == -1)
    r["dim1_media_direita_oposicao"] = float(m["u"][conf_d & opos, 0].mean())
    r["dim1_media_direita_centrao"] = float(m["u"][conf_d & centrao_dir, 0].mean())
    r["dim1_media_esquerda"] = float(m["u"][esq, 0].mean())
    r["dim1_media_centro"] = float(m["u"][okc & (campo == 0), 0].mean())
    r["fracao_distancia_direita_interna"] = float(
        (r["dim1_media_direita_centrao"] - r["dim1_media_direita_oposicao"])
        / (r["dim1_media_esquerda"] - r["dim1_media_direita_oposicao"]))
    # R² do eixo 1 explicado pelo campo (dummies) e pelo alinhamento ao Governo
    for nome, X in [("campo", np.column_stack([campo[okc & ok] == -1, campo[okc & ok] == 1]).astype(float)),
                    ("governo", gov[okc & ok][:, None]),
                    ("ambos", np.column_stack([campo[okc & ok] == -1, campo[okc & ok] == 1, gov[okc & ok]]).astype(float))]:
        Z = np.column_stack([np.ones(len(X)), X])
        yv = m["u"][okc & ok, 0]
        beta, *_ = np.linalg.lstsq(Z, yv, rcond=None)
        res = yv - Z @ beta
        r[f"r2_dim1_{nome}"] = float(1 - res @ res / np.sum((yv - yv.mean()) ** 2))
    # a dim2 é um "efeito ferradura" (extremos × meio)? u2 ~ u1 + u1²
    u1, u2 = m["u"][conf_d, 0], m["u"][conf_d, 1]
    for nome, Z in [("linear", np.column_stack([np.ones_like(u1), u1])),
                    ("quadratico", np.column_stack([np.ones_like(u1), u1, u1 ** 2]))]:
        beta, *_ = np.linalg.lstsq(Z, u2, rcond=None)
        res = u2 - Z @ beta
        r[f"r2_dim2_em_dim1_{nome}"] = float(1 - res @ res / np.sum((u2 - u2.mean()) ** 2))
        if nome == "quadratico":
            r["coef_quadratico"] = float(beta[2])
    ev = np.linalg.eigvalsh(np.cov(m["u"][conf_d].T))[::-1]
    r["autovalores_u"] = [float(e) for e in ev]

    # ---- votações: de que lado fica cada liderança no eixo 1 e no eixo 2
    O = orientacoes_por_votacao(P)
    b = m["b"]
    s1, s2 = np.sign(b[:, 0]), np.sign(b[:, 1])
    forte = np.abs(b[:, 0]) > np.median(np.abs(b[:, 0]))
    lin = []
    for c in ["Governo", "PT-PCdoB-PV", "PSOL-REDE", "Oposição", "PL", "NOVO"]:
        o = O[c].to_numpy()
        ok = ~np.isnan(o)
        lin.append({"liderança": c, "votações orientadas": int(ok.sum()),
                    "concorda com o sinal de b1": float(np.mean(o[ok] == s1[ok])),
                    "idem, |b1| acima da mediana": float(np.mean(o[ok & forte] == s1[ok & forte])),
                    "concorda com o sinal de b2": float(np.mean(o[ok] == s2[ok]))})
    tabela(pd.DataFrame(lin), "t6_liderancas_eixos")
    r["liderancas_eixos"] = lin

    def teste(a, bb, igual):
        x, z = O[a].to_numpy(), O[bb].to_numpy()
        mk = ~np.isnan(x) & ~np.isnan(z) & ((x == z) if igual else (x != z))
        return mk, x

    lin = []
    for a, bb, igual, rot in [("Governo", "PSOL-REDE", False, "Governo ≠ PSOL-REDE"),
                              ("Governo", "PT-PCdoB-PV", False, "Governo ≠ PT-PCdoB-PV"),
                              ("Governo", "PL", True, "Governo = PL"),
                              ("Governo", "Oposição", True, "Governo = Oposição"),
                              ("PSOL-REDE", "NOVO", True, "PSOL-REDE = NOVO"),
                              ("PSOL-REDE", "PL", True, "PSOL-REDE = PL")]:
        mk, x = teste(a, bb, igual)
        ambos = ~np.isnan(O[a].to_numpy()) & ~np.isnan(O[bb].to_numpy())
        lin.append({"situação": rot, "votações": int(mk.sum()), "% das orientadas por ambos": 100 * mk.sum() / ambos.sum(),
                    f"b1 com o 1º": float(np.mean(x[mk] == s1[mk])) if mk.sum() else np.nan,
                    "|b2| > |b1|": float(np.mean(np.abs(b[mk, 1]) > np.abs(b[mk, 0]))) if mk.sum() else np.nan,
                    "média |b1|": float(np.abs(b[mk, 0]).mean()), "média |b2|": float(np.abs(b[mk, 1]).mean())})
    tabela(pd.DataFrame(lin), "t7_testes_orientacao")
    r["testes_orientacao"] = lin
    r["media_abs_b1"], r["media_abs_b2"] = float(np.abs(b[:, 0]).mean()), float(np.abs(b[:, 1]).mean())
    r["prop_votacoes_dim2_dominante"] = float(np.mean(np.abs(b[:, 1]) > np.abs(b[:, 0])))
    RES["estrutura"] = r
    return O


def classe_objeto(desc, titulo):
    """Classe do objeto votado, pela descrição do resultado e pelo prefixo do objeto
    (REQ = requerimento; EMP/EMC/EMS/ERD/DTQ = emendas e destaques; RDF = redação final)."""
    d = desc.lower() if isinstance(desc, str) else ""
    pre = titulo.split(" ")[0].upper() if isinstance(titulo, str) else ""
    if pre == "RDF" or "redação final" in d:
        return "redação final"
    if pre == "REQ" or "requerimento" in d:
        if re.search(r"urg[êe]ncia", d):
            return "requerimento de urgência"
        if re.search(r"retirada de pauta|adiamento|encerramento d|quebra de interst|retirada da ordem do dia", d):
            return "requerimento procedimental (pauta, adiamento)"
        return "outro requerimento"
    if "ressalvad" in d:                       # "aprovado o texto..., ressalvados os destaques"
        return "texto principal / parecer"
    if pre in ("EMP", "EMC", "EMS", "ERD", "DTQ") or re.search(
            r"destaque|dvs|mantido o texto|mantida a|suprimid|(?<!proposta de )emenda", d):
        return "destaque / emenda"
    return "texto principal / parecer"


def etapa_dim3(P, m3, m2):
    """Exploratório: a terceira dimensão do modelo 3D (H2b não sustentou "2D suficiente")."""
    conf = P.nv_dep >= MIN_VOTOS
    u3 = m3["u"]
    r = {"autovalores": [float(e) for e in np.linalg.eigvalsh(np.cov(u3[conf].T))[::-1]],
         "r_dim1_3D_2D": float(np.corrcoef(u3[conf, 0], m2["u"][conf, 0])[0, 1]),
         "r_dim2_3D_2D": float(np.corrcoef(u3[conf, 1], m2["u"][conf, 1])[0, 1]),
         "r_dim3_com_2D": [float(np.corrcoef(u3[conf, 2], m2["u"][conf, k])[0, 1]) for k in (0, 1)]}
    d = pd.DataFrame(u3, columns=["d1", "d2", "d3"]).assign(p=P.part_dep)[conf]
    for c in ["d1", "d2", "d3"]:
        r[f"eta2_partido_{c}"] = float(((d.groupby("p")[c].transform("mean") - d[c].mean()) ** 2).sum()
                                       / ((d[c] - d[c].mean()) ** 2).sum())
    t = d.groupby("p").agg(deputados=("d3", "size"), dim1=("d1", "mean"), dim2=("d2", "mean"),
                           dim3=("d3", "mean"), dim3_dp=("d3", "std"))
    t = t[t["deputados"] >= 4].sort_values("dim3")
    t.index.name = "partido"
    tabela(t.reset_index(), "t14_dim3_partidos", casas=2)
    r["partidos"] = t.reset_index().to_dict("records")
    vt = pd.read_parquet(DADOS / "votacoes.parquet").set_index("idVotacao").reindex(P.votacoes)
    b = m3["b"]
    pureza = np.abs(b[:, 2]) / np.linalg.norm(b, axis=1)
    top = np.argsort(-(pureza * np.abs(b[:, 2])))[:15]
    tt = pd.DataFrame({"data": vt["data"].to_numpy()[top], "proposição": vt["proposicao_titulo"].to_numpy()[top],
                       "ementa": vt["proposicao_ementa"].fillna("").str.replace(r"\s+", " ", regex=True)
                       .str.slice(0, 90).to_numpy()[top], "b1": b[top, 0], "b2": b[top, 1], "b3": b[top, 2]})
    tabela(tt, "t14b_dim3_votacoes", casas=1)
    r["top"] = tt.to_dict("records")
    r["prop_votacoes_dim3_dominante"] = float(np.mean(np.abs(b[:, 2]) > np.abs(b[:, :2]).max(1)))
    RES["dim3"] = r


def etapa_dim2(P, m, O):
    vt = pd.read_parquet(DADOS / "votacoes.parquet").set_index("idVotacao").reindex(P.votacoes)
    b = m["b"]
    v = P.v
    sim = v.assign(bl=v["deputado_siglaPartido"].map(
        lambda p: "PSOL" if p == "PSOL" else "NOVO" if p == "NOVO" else "PT" if p == "PT" else "PL" if p == "PL"
        else "centrão" if p in ("PP", "REPUBLICANOS", "UNIÃO", "MDB", "PSD") else None)).dropna(subset=["bl"])
    S = sim.pivot_table(index="idVotacao", columns="bl", values="y", aggfunc="mean").reindex(P.votacoes)
    t = pd.DataFrame({"idVotacao": P.votacoes, "data": vt["data"].to_numpy(), "órgão": vt["siglaOrgao"].to_numpy(),
                      "proposição": vt["proposicao_titulo"].to_numpy(), "descricao": vt["descricao"].to_numpy(),
                      "objeto": vt["objeto_titulo"].to_numpy(), "ementa": vt["proposicao_ementa"].to_numpy(),
                      "b1": b[:, 0], "b2": b[:, 1], "a": m["a"]})
    for c in ["PSOL", "PT", "centrão", "PL", "NOVO"]:
        t[f"% Sim {c}"] = 100 * S[c].to_numpy()
    for c in ["Governo", "Oposição"]:
        t[f"or. {c}"] = pd.Series(O[c].to_numpy()).map({1.0: "Sim", -1.0: "Não"}).to_numpy()
    ps = P.v.groupby("idVotacao")["y"].mean().reindex(P.votacoes).to_numpy()
    t["minoria (%)"] = 100 * np.minimum(ps, 1 - ps)
    t["classe"] = [classe_objeto(d, o) for d, o in zip(t["descricao"], t["objeto"])]
    t["dim2_dominante"] = np.abs(t["b2"]) > np.abs(t["b1"])
    t["razao"] = np.abs(t["b2"]) / np.sqrt(t["b1"] ** 2 + t["b2"] ** 2)
    t.to_csv(TABS / "votacoes_cargas.csv", index=False)

    r = {"n_dim2_dominante": int(t["dim2_dominante"].sum())}
    # perfil das votações em que a dim2 domina, contra as demais
    lin = []
    for nome, mk in [("dim2 dominante (|b2| > |b1|)", t["dim2_dominante"]), ("dim1 dominante", ~t["dim2_dominante"])]:
        s = t[mk]
        go = s.dropna(subset=["or. Governo", "or. Oposição"])
        lin.append({"grupo": nome, "votações": len(s), "% no plenário": 100 * (s["órgão"] == "PLEN").mean(),
                    "% Governo = Oposição": 100 * (go["or. Governo"] == go["or. Oposição"]).mean(),
                    "minoria média (%)": s["minoria (%)"].mean(),
                    "|PSOL − PT| (pp)": (s["% Sim PSOL"] - s["% Sim PT"]).abs().mean(),
                    "|NOVO − PL| (pp)": (s["% Sim NOVO"] - s["% Sim PL"]).abs().mean(),
                    "|PSOL − NOVO| (pp)": (s["% Sim PSOL"] - s["% Sim NOVO"]).abs().mean(),
                    "|PT − PL| (pp)": (s["% Sim PT"] - s["% Sim PL"]).abs().mean(),
                    "|centrão − PT| (pp)": (s["% Sim centrão"] - s["% Sim PT"]).abs().mean()})
    tabela(pd.DataFrame(lin), "t8a_perfil_dim2", casas=1)
    r["perfil"] = lin
    cl = (t.groupby("classe")["dim2_dominante"].agg(["size", "mean"])
          .rename(columns={"size": "votações", "mean": "prop. dim2 dominante"}).sort_values("votações", ascending=False))
    cl["|b2| médio"] = t.groupby("classe")["b2"].apply(lambda s: s.abs().mean())
    cl["|b1| médio"] = t.groupby("classe")["b1"].apply(lambda s: s.abs().mean())
    tabela(cl.reset_index(), "t8b_classe_objeto")
    r["classes"] = cl.reset_index().to_dict("records")
    # direção: nas votações de dim2 dominante, o polo positivo (PSOL/NOVO) vota Sim ou Não?
    d2 = t[t["dim2_dominante"]]
    r["dim2_polo_positivo_vota_nao"] = float((d2["b2"] < 0).mean())
    # quem se separa de quem nas votações de dim2 dominante (lado = maioria do grupo > 50% "Sim")
    lado = {c: (t[f"% Sim {c}"] > 50) for c in ["PSOL", "PT", "centrão", "PL", "NOVO"]}
    for nome, mk in [("dim2", t["dim2_dominante"]), ("dim1", ~t["dim2_dominante"])]:
        ok = mk & t[[f"% Sim {c}" for c in lado]].notna().all(axis=1)
        L = {c: v[ok] for c, v in lado.items()}
        r[f"coalizoes_{nome}"] = {
            "n": int(ok.sum()),
            "psol_e_novo_juntos_contra_centrao": float(((L["PSOL"] == L["NOVO"]) & (L["PSOL"] != L["centrão"])).mean()),
            "so_psol_contra_centrao": float(((L["PSOL"] != L["centrão"]) & (L["NOVO"] == L["centrão"])).mean()),
            "so_novo_contra_centrao": float(((L["NOVO"] != L["centrão"]) & (L["PSOL"] == L["centrão"])).mean()),
            "algum_polo_contra_centrao": float(((L["PSOL"] != L["centrão"]) | (L["NOVO"] != L["centrão"])).mean()),
            "pt_com_centrao": float((L["PT"] == L["centrão"]).mean()),
            "pl_com_centrao": float((L["PL"] == L["centrão"]).mean())}
    pec3 = t["proposição"].fillna("").str.startswith("PEC 3/2021") & t["dim2_dominante"]
    r["pec3_2021"] = {c: [float(t.loc[pec3, f"% Sim {c}"].min()), float(t.loc[pec3, f"% Sim {c}"].max())]
                      for c in ["PSOL", "PT", "centrão", "PL", "NOVO"]}
    r["dim2_dominante_aprovadas_centrao_sim"] = float((d2["% Sim centrão"] > 50).mean())
    # tipo de proposição
    tipo = t["proposição"].fillna("?").str.split().str[0]
    tp = pd.DataFrame({"votações": tipo.value_counts(), "prop. dim2 dominante": t.groupby(tipo)["dim2_dominante"].mean(),
                       "|b2| médio": t.groupby(tipo)["b2"].apply(lambda s: s.abs().mean())})
    tp = tp[tp["votações"] >= 15].sort_values("votações", ascending=False)
    tp.index.name = "tipo"
    tabela(tp.reset_index(), "t8c_tipo_proposicao")
    r["tipos"] = tp.reset_index().to_dict("records")
    # proposições que concentram as votações de dim2 dominante
    pr = (t[t["dim2_dominante"]].groupby("proposição").agg(votações=("b2", "size"), b2_medio_abs=("b2", lambda s: s.abs().mean()))
          .sort_values("votações", ascending=False).head(15))
    em = t.drop_duplicates("proposição").set_index("proposição")["ementa"]
    pr["ementa"] = em.reindex(pr.index).fillna("").str.slice(0, 110)
    tabela(pr.reset_index(), "t8d_proposicoes_dim2", casas=2)
    cont = t[t["dim2_dominante"]].groupby("proposição").size().sort_values(ascending=False)
    r["n_proposicoes_dim2"] = int(len(cont))
    r["prop_top10_proposicoes_dim2"] = float(cont.head(10).sum() / cont.sum())
    r["proposicoes_dim2"] = pr.reset_index().to_dict("records")
    # as votações que mais carregam na dim2 (b2 padronizado alto e direção quase pura)
    top = t[t["razao"] > 0.8].assign(ab2=lambda d: d["b2"].abs()).sort_values("ab2", ascending=False).head(25)
    cols = ["data", "órgão", "proposição", "descricao", "b1", "b2", "% Sim PSOL", "% Sim PT", "% Sim centrão",
            "% Sim PL", "% Sim NOVO", "or. Governo", "or. Oposição"]
    top = top[cols].copy()
    top["descricao"] = top["descricao"].fillna("").str.replace(r"\s+", " ", regex=True).str.slice(0, 140)
    tabela(top, "t8_top_dim2", casas=1)
    r["top"] = top.to_dict("records")
    RES["dim2"] = r
    return t


# ------------------------------------------------------- comparação 1D × 2D (eixo central)
N_BOOT_1D = 100


def _boot1d_tarefa(b):
    P = _G["P"]
    cl, ncl = _G["cluster"], _G["cluster"].max() + 1
    c = np.bincount(np.random.default_rng(5000 + b).integers(0, ncl, ncl), minlength=ncl).astype(float)
    m = ajustar(P.i, P.j, P.y, P.n_i, P.n_j, 1, base=P.base, w=c[cl][P.j], semente=5000 + b, **PADRAO)
    return P.orientar(m)["u"][:, 0], m["convergiu"]


PARTIDOS_COMP = ["PSOL", "PT", "PCdoB", "REDE", "PSB", "PDT", "MDB", "PSD", "PP", "REPUBLICANOS", "UNIÃO", "PL", "NOVO"]


def etapa_comparacao(P, pred, finais, tvot, boot1d):
    """Onde e como a análise de um eixo só difere da de dois eixos (análises exploratórias)."""
    y, j = P.y, P.j
    r = {}
    acerto = lambda k, mk: acc(pred[k][mk], y[mk])
    # (a) acurácia fora da amostra segundo a dimensão que domina a votação
    d2 = tvot["dim2_dominante"].to_numpy()[j]
    lin = []
    for nome, mk in [("dimensão 2 dominante", d2), ("dimensão 1 dominante", ~d2), ("todas", np.ones_like(d2))]:
        lin.append({"votações": nome, "n votações": int(np.unique(j[mk]).size), "votos": int(mk.sum()),
                    "% dos votos": 100 * mk.mean(), "maioria do partido": acerto("maioria_partido", mk),
                    "orientação": acerto("orientacao", mk), "IRT 1D": acerto(1, mk), "IRT 2D": acerto(2, mk)})
    t = pd.DataFrame(lin)
    t["ganho 1D→2D (pp)"] = 100 * (t["IRT 2D"] - t["IRT 1D"])
    tabela(t, "t15_comparacao_por_votacao")
    r["por_tipo_votacao"] = t.to_dict("records")
    # IC por proposição do ganho nas votações de dim2 dominante
    cl = _G["cluster"][j]
    ncl = cl.max() + 1
    W = np.random.default_rng(78).multinomial(ncl, np.full(ncl, 1 / ncl), size=1000).astype(float)
    dif = (((pred[2] > .5) == (y > .5)).astype(float) - ((pred[1] > .5) == (y > .5)).astype(float))
    for nome, mk in [("dim2", d2), ("dim1", ~d2)]:
        sc = np.bincount(cl[mk], dif[mk], ncl)
        nc = np.bincount(cl[mk], minlength=ncl)
        bt = (W @ sc) / np.maximum(W @ nc, 1)
        r[f"ic_ganho_{nome}"] = [float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))]
    # (b) posição coletiva de cada partido em cada votação (fora da amostra)
    df = pd.DataFrame({"j": j, "y": y, "p1": pred[1], "p2": pred[2], "part": P.v["deputado_siglaPartido"].to_numpy()})
    pv = df.groupby(["part", "j"]).agg(y=("y", "mean"), p1=("p1", "mean"), p2=("p2", "mean"), n=("y", "size"))
    pv = pv[pv["n"] >= 3]
    lin = []
    for pa in PARTIDOS_COMP:
        if pa not in pv.index.get_level_values(0):
            continue
        q = pv.loc[pa]
        lin.append({"partido": pa, "votações": len(q),
                    "erra a maioria do partido: 1D": int(((q.p1 > .5) != (q.y > .5)).sum()),
                    "erra a maioria do partido: 2D": int(((q.p2 > .5) != (q.y > .5)).sum()),
                    "erro médio da % de Sim: 1D": 100 * float((q.p1 - q.y).abs().mean()),
                    "erro médio da % de Sim: 2D": 100 * float((q.p2 - q.y).abs().mean())})
    t = pd.DataFrame(lin)
    tabela(t, "t16_comparacao_por_partido", casas=1)
    r["por_partido"] = t.to_dict("records")
    # (c) resultado da votação (lado majoritário entre os votantes)
    g = df.groupby("j")[["y", "p1", "p2"]].mean()
    venc = g["y"] > .5
    apertada = (g["y"] - .5).abs() < .1
    r["resultado"] = {"votacoes": int(len(g)), "apertadas": int(apertada.sum()),
                      "erra_vencedor_1D": int(((g.p1 > .5) != venc).sum()), "erra_vencedor_2D": int(((g.p2 > .5) != venc).sum()),
                      "erro_medio_pct_sim_1D": 100 * float((g.p1 - g.y).abs().mean()),
                      "erro_medio_pct_sim_2D": 100 * float((g.p2 - g.y).abs().mean())}
    # (d) posições: modelo de um eixo × dimensão 1 do modelo de dois eixos (escores padronizados)
    conf = P.nv_dep >= MIN_VOTOS
    z = lambda v: (v - v[conf].mean()) / v[conf].std()
    u1, d1, d2v = z(finais[1]["u"][:, 0]), z(finais[2]["u"][:, 0]), finais[2]["u"][:, 1]
    dd = pd.DataFrame({"p": P.part_dep, "1D": u1, "2D: dim. 1": d1, "2D: dim. 2": d2v})[conf]
    m = dd.groupby("p").mean().reindex(PARTIDOS_COMP)
    m["deslocamento"] = m["1D"] - m["2D: dim. 1"]
    m.index.name = "partido"
    tabela(m.reset_index(), "t17_posicoes_1d_2d", casas=2)
    r["posicoes"] = m.reset_index().to_dict("records")
    r["r_1D_dim1"] = float(np.corrcoef(u1[conf], d1[conf])[0, 1])
    r["r_1D_dim2"] = float(np.corrcoef(u1[conf], d2v[conf])[0, 1])
    # incerteza das diferenças no 1D (bootstrap por proposição, escores padronizados por réplica)
    U1, conv = boot1d
    U1 = U1[conv]

    def dif_part(a, b, U):
        out = []
        for u in U:
            uz = z(u)
            out.append(uz[conf & (P.part_dep == a)].mean() - uz[conf & (P.part_dep == b)].mean())
        return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]
    for a_, b_ in [("PSOL", "PT"), ("PSOL", "PCdoB"), ("NOVO", "PL")]:
        r[f"dif_1D_{a_}_{b_}"] = {"ponto": float(m.loc[a_, "1D"] - m.loc[b_, "1D"]), "ic": dif_part(a_, b_, U1)}
        r[f"dif_2Ddim1_{a_}_{b_}"] = float(m.loc[a_, "2D: dim. 1"] - m.loc[b_, "2D: dim. 1"])
    r["boot1d_B"], r["boot1d_convergiram"] = int(len(conv)), int(conv.sum())
    # correlação do eixo único com alinhamento ao Governo e com o campo
    gov = finais[2]["gov"]
    campo = np.array([CAMPO.get(p_, np.nan) for p_ in P.part_dep], float)
    ok = conf & ~np.isnan(gov) & ~np.isnan(campo)
    r["r_1D_governo"] = float(np.corrcoef(u1[ok], gov[ok])[0, 1])
    r["r_1D_campo"] = float(np.corrcoef(u1[ok], campo[ok])[0, 1])
    r["r_dim1_governo"] = float(np.corrcoef(d1[ok], gov[ok])[0, 1])
    r["r_dim1_campo"] = float(np.corrcoef(d1[ok], campo[ok])[0, 1])
    RES["comparacao"] = r
    return m


# ------------------------------------------------------------------------- robustez
CONFIGS = {
    "padrão": {},
    "λx = 0,25 (prior do ponto mais frouxo)": dict(lam_x=0.25),
    "λx = 4 (prior do ponto mais apertado)": dict(lam_x=4.0),
    "λb = 0,01 (discriminação mais livre)": dict(lam_b=0.01),
    "λb = 0,16 (discriminação mais contida)": dict(lam_b=0.16),
    "λδ = 0,25 (períodos quase independentes)": dict(lam_d=0.25),
    "λδ = 64 (um ponto por deputado)": dict(lam_d=64.0),
    "sem corte de votações desiguais": dict(min_minoria=0.0),
    "corte de minoria em 5%": dict(min_minoria=0.05),
    "corte de minoria em 10%": dict(min_minoria=0.10),
    "corte de minoria em 20%": dict(min_minoria=0.20),
    "obstrução como ausência": dict(obstrucao="fora"),
    "obstrução e abstenção como Não": dict(abstencao="nao"),
}


def _robustez_tarefa(nome):
    cfg = dict(CONFIGS[nome])
    dados = {k: cfg.pop(k) for k in ["min_minoria", "obstrucao", "abstencao"] if k in cfg}
    P = Painel(preparar(_G["bruto"], **dados)) if dados else _G["P"]
    te = particao_hash(P.v)
    out = {"config": nome, "votos": len(P.y), "votações": P.n_j, "deputados": P.n_u}
    mai = (np.bincount(P.j[~te], P.y[~te], P.n_j) / np.maximum(np.bincount(P.j[~te], minlength=P.n_j), 1))
    out["maioria"] = acc(mai[P.j[te]], P.y[te])
    for k in (1, 2):
        mk = P.ajustar(k, mask=~te, **cfg)
        p = prever(mk, P.i[te], P.j[te])
        out[f"acurácia {k}D"] = acc(p, P.y[te])
        if k == 2:
            out["log-loss 2D"] = logloss(p, P.y[te])
            # acurácia nas votações comuns a todas as configurações (minoria >= 20%)
            out["_pred"] = pd.Series((p > .5) == (P.y[te] > .5),
                                     index=pd.MultiIndex.from_arrays([P.v["idVotacao"].to_numpy()[te],
                                                                      P.v["deputado_id"].to_numpy()[te]]))
    m = P.final(2, **cfg)
    out["_u"] = pd.DataFrame(m["u"], index=P.deps)
    out["_nv"] = pd.Series(P.nv_dep, index=P.deps)
    return out


def etapa_robustez(P, m):
    saida = paralelo(_robustez_tarefa, list(CONFIGS))
    ref = pd.DataFrame(m["u"], index=P.deps)
    conf = set(P.deps[P.nv_dep >= MIN_VOTOS])
    # células de teste comuns a todas as configurações (mesma partição por hash)
    comuns = None
    for o in saida:
        idx = o["_pred"].index
        comuns = idx if comuns is None else comuns.intersection(idx)
    lin = []
    for o in saida:
        u = o.pop("_u")
        nv = o.pop("_nv")
        pr = o.pop("_pred")
        o["acurácia 2D (células comuns)"] = float(pr.loc[comuns].mean())
        o["células comuns"] = int(len(comuns))
        com = [d for d in u.index if d in conf and nv[d] >= MIN_VOTOS]
        a, b = u.loc[com].to_numpy(), ref.loc[com].to_numpy()
        o["r dim1"] = float(np.corrcoef(a[:, 0], b[:, 0])[0, 1])
        o["r dim2"] = float(np.corrcoef(a[:, 1], b[:, 1])[0, 1])
        al = procrustes(a, b)(a)
        o["r dim2 (Procrustes)"] = float(np.corrcoef(al[:, 1], b[:, 1])[0, 1])
        o["dp dim1"], o["dp dim2"] = float(a[:, 0].std()), float(a[:, 1].std())
        lin.append(o)
    t = pd.DataFrame(lin)
    t["APRE 2D"] = 1 - (1 - t["acurácia 2D"]) / (1 - t["maioria"])
    t["ganho 1D→2D"] = t["acurácia 2D"] - t["acurácia 1D"]
    tabela(t, "t10_robustez")
    RES["robustez"] = t.to_dict("records")


# ------------------------------------------------------------------------- bootstrap
N_BOOT = 200


def _boot_tarefa(b):
    """Réplica de bootstrap: reamostra proposições (blocos de votações sobre a mesma matéria) com
    reposição, reajusta do zero (partida fria) e aplica o pipeline completo de orientação (PCA +
    sinais), sem girar a réplica para a estimativa pontual."""
    P = _G["P"]
    cl, ncl = _G["cluster"], _G["cluster"].max() + 1
    c = np.bincount(np.random.default_rng(1000 + b).integers(0, ncl, ncl), minlength=ncl).astype(float)
    m = ajustar(P.i, P.j, P.y, P.n_i, P.n_j, 2, base=P.base, w=c[cl][P.j], semente=1000 + b, **PADRAO)
    m = P.orientar(m)
    return m["u"], m["x"], m["convergiu"]


def etapa_bootstrap(P, m):
    saida = paralelo(_boot_tarefa, list(range(N_BOOT)))
    conf = P.nv_dep >= MIN_VOTOS
    U = np.array([s[0] for s in saida])
    X = np.array([s[1] for s in saida])
    conv = np.array([s[2] for s in saida])
    # ângulo da rotação de Procrustes que levaria cada réplica à estimativa pontual (diagnóstico
    # da estabilidade dos eixos; as réplicas NÃO são giradas)
    ang = []
    for u in U:
        a, ref = u[conf] - u[conf].mean(0), m["u"][conf] - m["u"][conf].mean(0)
        uu, _, vt = np.linalg.svd(a.T @ ref)
        q = uu @ vt
        ang.append(float(np.degrees(np.arctan2(q[1, 0], q[0, 0]))))
    return U, X, conv, np.array(ang)


def resumo_bootstrap(P, m, U, X, conv, ang):
    U, X, ang_ok = U[conv].copy(), X[conv].copy(), ang[conv]
    conf_d = P.nv_dep >= MIN_VOTOS
    # A escala latente só é identificada pelos priors: ao duplicar votações, a reamostragem dá mais
    # peso aos dados frente ao prior de b, as cargas crescem e os pontos encolhem. Cada réplica é
    # recentrada e reescalada por UM fator isotrópico (sem rotação nem escala por eixo) para ter a
    # mesma variância total que a estimativa pontual entre os deputados confiáveis.
    alvo = m["u"][conf_d].var(0).sum()
    mu0 = m["u"][conf_d].mean(0)
    escalas = []
    for b in range(len(U)):
        mu = U[b][conf_d].mean(0)
        f = np.sqrt(alvo / U[b][conf_d].var(0).sum())
        escalas.append(f)
        U[b] = (U[b] - mu) * f + mu0
        X[b] = (X[b] - mu) * f + mu0
    conf_p = P.nv_periodo >= MIN_VOTOS
    se = U.std(0, ddof=1)
    lo, hi = np.percentile(U, 2.5, 0), np.percentile(U, 97.5, 0)
    r = {"B": int(len(conv)), "convergiram": int(conv.sum()), "reamostragem": "proposições",
         "n_clusters": int(_G["cluster"].max() + 1),
         "fator_escala_mediano": float(np.median(escalas)), "fator_escala_p5": float(np.percentile(escalas, 5)),
         "fator_escala_p95": float(np.percentile(escalas, 95)),
         "angulo_eixos_mediana_abs": float(np.median(np.abs(ang_ok))),
         "angulo_eixos_p95_abs": float(np.percentile(np.abs(ang_ok), 95)),
         "angulo_eixos_max_abs": float(np.max(np.abs(ang_ok))),
         "ep_mediano_dim1": float(np.median(se[conf_d, 0])), "ep_mediano_dim2": float(np.median(se[conf_d, 1])),
         "ep_p90_dim1": float(np.percentile(se[conf_d, 0], 90)), "ep_p90_dim2": float(np.percentile(se[conf_d, 1], 90)),
         "ep_mediano_dim1_nao_conf": float(np.median(se[~conf_d, 0])) if (~conf_d).any() else None,
         "ep_mediano_dim2_nao_conf": float(np.median(se[~conf_d, 1])) if (~conf_d).any() else None,
         "confiabilidade_dim1": float(1 - np.mean(se[conf_d, 0] ** 2) / m["u"][conf_d, 0].var()),
         "confiabilidade_dim2": float(1 - np.mean(se[conf_d, 1] ** 2) / m["u"][conf_d, 1].var()),
         "ic_dim1_inclui_zero": float(np.mean((lo[conf_d, 0] < 0) & (hi[conf_d, 0] > 0))),
         "ic_dim2_inclui_zero": float(np.mean((lo[conf_d, 1] < 0) & (hi[conf_d, 1] > 0))),
         "vies_medio_abs_dim1": float(np.abs(U.mean(0) - m["u"])[conf_d, 0].mean()),
         "vies_medio_abs_dim2": float(np.abs(U.mean(0) - m["u"])[conf_d, 1].mean())}
    from scipy.stats import spearmanr
    r["rho_ep_nvotos_dim1"] = float(spearmanr(se[:, 0], P.nv_dep)[0])
    r["rho_ep_nvotos_dim2"] = float(spearmanr(se[:, 1], P.nv_dep)[0])
    # correlação das réplicas com a estimativa pontual
    r["r_replica_dim1_min"] = float(min(np.corrcoef(u[conf_d, 0], m["u"][conf_d, 0])[0, 1] for u in U))
    r["r_replica_dim2_min"] = float(min(np.corrcoef(u[conf_d, 1], m["u"][conf_d, 1])[0, 1] for u in U))
    r["r_replica_dim2_mediana"] = float(np.median([np.corrcoef(u[conf_d, 1], m["u"][conf_d, 1])[0, 1] for u in U]))
    # ordem no eixo 1: largura do IC em posições
    rk = np.array([pd.Series(u[conf_d, 0]).rank().to_numpy() for u in U])
    larg = np.percentile(rk, 97.5, 0) - np.percentile(rk, 2.5, 0)
    r["largura_ic_rank_dim1_mediana"] = float(np.median(larg))
    r["n_confiaveis"] = int(conf_d.sum())
    # partidos: IC das médias (pontos por período confiável)
    lin = []
    partidos = pd.Series(P.part_periodo[conf_p]).value_counts()
    for pa in partidos[partidos >= 3].index:
        mk = conf_p & (P.part_periodo == pa)
        md = X[:, mk, :].mean(1)
        lin.append({"partido": pa, "dim1": m["x"][mk, 0].mean(), "dim1 IC2,5": np.percentile(md[:, 0], 2.5),
                    "dim1 IC97,5": np.percentile(md[:, 0], 97.5), "dim2": m["x"][mk, 1].mean(),
                    "dim2 IC2,5": np.percentile(md[:, 1], 2.5), "dim2 IC97,5": np.percentile(md[:, 1], 97.5)})
    t = pd.DataFrame(lin).sort_values("dim1")
    tabela(t, "t11_partidos_ic", casas=2)
    r["partidos"] = t.to_dict("records")

    def dif(a, b, k):
        ma = X[:, conf_p & (P.part_periodo == a), k].mean(1)
        mb = X[:, conf_p & (P.part_periodo == b), k].mean(1)
        d = ma - mb
        return {"dif": float(m["x"][conf_p & (P.part_periodo == a), k].mean() - m["x"][conf_p & (P.part_periodo == b), k].mean()),
                "ic": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}

    r["dif_PSOL_PT_dim1"], r["dif_PSOL_PT_dim2"] = dif("PSOL", "PT", 0), dif("PSOL", "PT", 1)
    r["dif_NOVO_PL_dim1"], r["dif_NOVO_PL_dim2"] = dif("NOVO", "PL", 0), dif("NOVO", "PL", 1)
    r["dif_PSOL_NOVO_dim2"] = dif("PSOL", "NOVO", 1)
    r["dif_REPUBLICANOS_PP_dim2"] = dif("REPUBLICANOS", "PP", 1)
    r["dif_PP_PL_dim1"] = dif("PP", "PL", 0)
    r["dif_REPUBLICANOS_PL_dim1"] = dif("REPUBLICANOS", "PL", 0)
    r["dif_UNIÃO_PL_dim1"] = dif("UNIÃO", "PL", 0)
    campo = np.array([CAMPO.get(p, np.nan) for p in P.part_dep], float)
    pt = estatisticas_h1(P, m["u"], m["x"], m["gov"], campo)
    reps = [estatisticas_h1(P, U[b], X[b], m["gov"], campo) for b in range(len(U))]
    r["h1_ic"] = {k: {"ponto": pt[k], "ic": [float(np.percentile([q[k] for q in reps], 2.5)),
                                             float(np.percentile([q[k] for q in reps], 97.5))]} for k in pt}
    RES["bootstrap"] = r
    d = pd.DataFrame({"deputado_id": P.deps, "partido": P.part_dep, "n_votos": P.nv_dep, "dim1": m["u"][:, 0],
                      "dim1_ep": se[:, 0], "dim1_ic_inf": lo[:, 0], "dim1_ic_sup": hi[:, 0], "dim2": m["u"][:, 1],
                      "dim2_ep": se[:, 1], "dim2_ic_inf": lo[:, 1], "dim2_ic_sup": hi[:, 1]})
    nomes = pd.read_parquet(DADOS / "deputados.parquet")[["id", "nome"]]
    nomes["id"] = nomes["id"].astype(int)
    d = d.merge(nomes, left_on="deputado_id", right_on="id", how="left").drop(columns="id")
    d.to_csv(TABS / "pontos_ideais_deputados.csv", index=False)
    return se


# -------------------------------------------------------------- plenário x comissões
def _orgao_tarefa(nome):
    bruto = _G["bruto"]
    sub = {"plenario": bruto[bruto["siglaOrgao"] == "PLEN"], "comissoes": bruto[bruto["siglaOrgao"] != "PLEN"],
           "ccjc": bruto[bruto["siglaOrgao"] == "CCJC"]}[nome]
    P = Painel(preparar(sub))
    te = np.random.default_rng(7).random(len(P.y)) < 0.10
    out = {"nome": nome, "votos": len(P.y), "votações": P.n_j, "deputados": P.n_u,
           "deputados ≥ 50 votos": int((P.nv_dep >= MIN_VOTOS).sum())}
    mai = (np.bincount(P.j[~te], P.y[~te], P.n_j) / np.maximum(np.bincount(P.j[~te], minlength=P.n_j), 1))
    out["maioria"] = acc(mai[P.j[te]], P.y[te])
    ori = P.v["orientacao_partido"].map({"Sim": 1.0, "Não": 0.0, "Obstrução": 0.0}).to_numpy()
    out["orientação"] = acc(np.where(np.isnan(ori[te]), mai[P.j[te]], ori[te]), P.y[te])
    for k in (1, 2, 3):
        out[f"IRT {k}D"] = acc(prever(P.ajustar(k, mask=~te), P.i[te], P.j[te]), P.y[te])
    m = P.final(2)
    out["_u"] = pd.DataFrame(m["u"], index=P.deps)
    out["_nv"] = pd.Series(P.nv_dep, index=P.deps)
    out["_part"] = pd.Series(P.part_dep, index=P.deps)
    return out


def etapa_orgaos(P, m):
    saida = {o["nome"]: o for o in paralelo(_orgao_tarefa, ["plenario", "comissoes", "ccjc"])}
    ref = pd.DataFrame(m["u"], index=P.deps)
    lin, r = [], {}
    for nome, rot in [("plenario", "Só plenário"), ("comissoes", "Só comissões"), ("ccjc", "Só CCJC")]:
        o = saida[nome]
        l = {"amostra": rot, **{k: x for k, x in o.items() if not k.startswith("_") and k != "nome"}}
        l["APRE 2D"] = 1 - (1 - l["IRT 2D"]) / (1 - l["maioria"])
        com = o["_nv"].index[(o["_nv"] >= MIN_VOTOS)].intersection(P.deps[P.nv_dep >= MIN_VOTOS])
        a, b = o["_u"].loc[com].to_numpy(), ref.loc[com].to_numpy()
        al = procrustes(a, b)(a)
        for k in (0, 1):
            l[f"r dim{k + 1} (eixos próprios)"] = float(np.corrcoef(a[:, k], b[:, k])[0, 1])
            l[f"r dim{k + 1} (Procrustes)"] = float(np.corrcoef(al[:, k], b[:, k])[0, 1])
        lin.append(l)
    tabela(pd.DataFrame(lin), "t9_plenario_comissoes")
    r["tabela"] = lin
    pl, co = saida["plenario"], saida["comissoes"]
    com = pl["_nv"].index[pl["_nv"] >= MIN_VOTOS].intersection(co["_nv"].index[co["_nv"] >= MIN_VOTOS])
    a, b = co["_u"].loc[com].to_numpy(), pl["_u"].loc[com].to_numpy()
    al = procrustes(a, b)(a)
    r["n_comuns"] = int(len(com))
    r["r_dim1_bruto"] = float(np.corrcoef(a[:, 0], b[:, 0])[0, 1])
    r["r_dim2_bruto"] = float(np.corrcoef(a[:, 1], b[:, 1])[0, 1])
    r["r_dim1"] = float(np.corrcoef(al[:, 0], b[:, 0])[0, 1])
    r["r_dim2"] = float(np.corrcoef(al[:, 1], b[:, 1])[0, 1])
    # dentro dos blocos: a posição nas comissões ainda acompanha a do plenário?
    part = pl["_part"].loc[com].to_numpy()
    for bl in BLOCOS:
        mk = np.array([bloco_de(p) == bl for p in part])
        r[f"r_dim1_{bl}"] = float(np.corrcoef(al[mk, 0], b[mk, 0])[0, 1])
        r[f"n_{bl}"] = int(mk.sum())
    # resíduo dentro do partido
    d = pd.DataFrame({"p": part, "c": al[:, 0], "l": b[:, 0]})
    d = d[d.groupby("p")["p"].transform("size") >= 5]
    rc, rl = d["c"] - d.groupby("p")["c"].transform("mean"), d["l"] - d.groupby("p")["l"].transform("mean")
    r["r_dim1_intrapartido"] = float(np.corrcoef(rc, rl)[0, 1])
    RES["orgaos"] = r
    return pd.DataFrame({"plen1": b[:, 0], "plen2": b[:, 1], "com1": al[:, 0], "com2": al[:, 1], "partido": part},
                        index=com)


# --------------------------------------------------------------------- SVD / fatoração
def etapa_svd(P, m):
    """Método alternativo: decomposição em valores singulares da matriz deputado × votação
    (Sim=+1, Não=-1), com e sem imputação iterativa dos votos ausentes."""
    te = particao_original(len(P.y))
    tr = ~te
    li, cj = P.base[P.i], P.j           # linhas = deputados
    s = 2 * P.y - 1

    def matriz(mask):
        M = np.full((P.n_u, P.n_j), np.nan)
        M[li[mask], cj[mask]] = s[mask]
        return M

    def fatorar(M, K, iters):
        obs = ~np.isnan(M)
        cm = np.nanmean(M, 0)
        cm = np.where(np.isnan(cm), 0, cm)
        Z = np.where(obs, M - cm, 0.0)
        low = None
        for _ in range(max(iters, 1)):
            u, sv, vt = np.linalg.svd(Z, full_matrices=False)
            low = (u[:, :K] * sv[:K]) @ vt[:K]
            if iters == 0:
                break
            Z = np.where(obs, M - cm, low)
        return low + cm, u[:, :K] * sv[:K], sv

    r, lin = {}, []
    Mtr = matriz(tr)
    for K in (1, 2, 3):
        for iters, rot in [(0, "SVD, ausentes na média da votação"), (50, "SVD com imputação iterativa")]:
            rec, _, _ = fatorar(Mtr, K, iters)
            p = rec[li[te], cj[te]]
            lin.append({"método": rot, "dimensões": K, "acurácia fora da amostra": float(np.mean((p > 0) == (s[te] > 0)))})
    conf = P.nv_dep >= MIN_VOTOS
    Mall = matriz(np.ones(len(s), bool))
    for iters, rot in [(0, "SVD, ausentes na média da votação"), (50, "SVD com imputação iterativa")]:
        _, sc, sv = fatorar(Mall, 2, iters)
        al = procrustes(sc[conf], m["u"][conf])(sc[conf])
        for l in lin:
            if l["método"] == rot and l["dimensões"] == 2:
                l["r dim1 com IRT"] = float(np.corrcoef(al[:, 0], m["u"][conf, 0])[0, 1])
                l["r dim2 com IRT"] = float(np.corrcoef(al[:, 1], m["u"][conf, 1])[0, 1])
        if iters == 0:
            r["valores_singulares"] = [float(x) for x in sv[:10]]
            r["var_explicada"] = [float(x) for x in (sv ** 2 / np.sum(sv ** 2))[:10]]
        else:
            r["_sc"] = al
    # só entre deputados confiáveis: scree da matriz restrita
    _, _, sv = fatorar(Mall[conf], 2, 0)
    r["var_explicada_confiaveis"] = [float(x) for x in (sv ** 2 / np.sum(sv ** 2))[:10]]
    mtr = P.ajustar(2, mask=tr)
    r["irt2d_mesma_particao"] = acc(prever(mtr, P.i[te], P.j[te]), P.y[te])
    t = pd.DataFrame(lin)
    tabela(t, "t12_svd", casas=4)
    r["tabela"] = lin
    sc = r.pop("_sc")
    RES["svd"] = r
    return sc


# ---------------------------------------------------------------------------- por ano
def _ano_tarefa(ano):
    bruto = _G["bruto"]
    P = Painel(preparar(bruto[bruto["data"].str[:4] == ano]))
    te = np.random.default_rng(11).random(len(P.y)) < 0.10
    out = {"ano": ano, "votos": len(P.y), "votações": P.n_j,
           "deputados ≥ 50 votos": int((P.nv_dep >= MIN_VOTOS).sum())}
    mai = (np.bincount(P.j[~te], P.y[~te], P.n_j) / np.maximum(np.bincount(P.j[~te], minlength=P.n_j), 1))
    out["maioria"] = acc(mai[P.j[te]], P.y[te])
    for k in (1, 2):
        out[f"IRT {k}D"] = acc(prever(P.ajustar(k, mask=~te), P.i[te], P.j[te]), P.y[te])
    m = P.final(2)
    out["_u"] = pd.DataFrame(m["u"], index=P.deps)
    out["_nv"] = pd.Series(P.nv_dep, index=P.deps)
    out["_part"] = pd.Series(P.part_dep, index=P.deps)
    return out


def etapa_anos(P, m):
    anos = sorted(P.v["data"].str[:4].unique())
    saida = paralelo(_ano_tarefa, anos)
    ref = pd.DataFrame(m["u"], index=P.deps)
    lin, part = [], {}
    for o in saida:
        com = o["_nv"].index[o["_nv"] >= MIN_VOTOS].intersection(P.deps[P.nv_dep >= MIN_VOTOS])
        a, b = o["_u"].loc[com].to_numpy(), ref.loc[com].to_numpy()
        al = procrustes(a, b)(a)
        l = {k: x for k, x in o.items() if not k.startswith("_")}
        l["ganho 1D→2D"] = l["IRT 2D"] - l["IRT 1D"]
        l["r dim1 (eixos próprios)"] = float(np.corrcoef(a[:, 0], b[:, 0])[0, 1])
        l["r dim2 (eixos próprios)"] = float(np.corrcoef(a[:, 1], b[:, 1])[0, 1])
        l["r dim1 (Procrustes)"] = float(np.corrcoef(al[:, 0], b[:, 0])[0, 1])
        l["r dim2 (Procrustes)"] = float(np.corrcoef(al[:, 1], b[:, 1])[0, 1])
        lin.append(l)
        z = pd.DataFrame(al, index=com, columns=["d1", "d2"]).assign(p=o["_part"].loc[com])
        part[o["ano"]] = z.groupby("p")[["d1", "d2"]].mean()[z.groupby("p").size() >= 5]
    tabela(pd.DataFrame(lin), "t13_por_ano")
    RES["anos"] = lin
    pm = pd.concat({a: x["d1"] for a, x in part.items()}, axis=1).dropna(thresh=3)
    pm2 = pd.concat({a: x["d2"] for a, x in part.items()}, axis=1).reindex(pm.index)
    pm = pm.sort_values(pm.columns[0])
    pm.index.name = "partido"
    tabela(pm.reset_index(), "t13b_partidos_dim1_por_ano", casas=2)
    pm2 = pm2.reindex(pm.index)
    pm2.index.name = "partido"
    tabela(pm2.reset_index(), "t13c_partidos_dim2_por_ano", casas=2)
    RES["partidos_dim1_por_ano"] = pm.reset_index().to_dict("records")
    RES["partidos_dim2_por_ano"] = pm2.reset_index().to_dict("records")


# ============================================================================ figuras
COR = {"Esquerda": "#2a78d6", "Centro e centrão": "#eb6834", "Direita de oposição": "#1baf7a"}
TINTA, TINTA2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e7e6e2", "#fcfcfb"


def estilo():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "savefig.facecolor": FUNDO, "font.size": 10,
        "font.family": "DejaVu Sans", "axes.edgecolor": GRADE, "axes.labelcolor": TINTA2, "text.color": TINTA,
        "xtick.color": TINTA2, "ytick.color": TINTA2, "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 11, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "legend.frameon": False, "figure.dpi": 100, "savefig.dpi": 200,
        "savefig.bbox": "tight", "axes.axisbelow": True})
    return plt


def rotulos_partidos(ax, cent, fs=8):
    import matplotlib.patheffects as pe
    for p, (x, y) in cent.iterrows():
        ax.annotate(p, (x, y), fontsize=fs, ha="center", va="center", color=TINTA, weight="bold",
                    path_effects=[pe.withStroke(linewidth=2.5, foreground=FUNDO)])


def legenda_blocos(ax, **kw):
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", color=COR[b], markersize=7, label=b) for b in BLOCOS]
    ax.legend(handles=h, **kw)


def figuras(P, m, pred, tvot, se, dcom, sc_svd):
    plt = estilo()
    conf_p, conf_d = P.nv_periodo >= MIN_VOTOS, P.nv_dep >= MIN_VOTOS
    cor_p = np.array([COR[bloco_de(p)] for p in P.part_periodo])
    cor_d = np.array([COR[bloco_de(p)] for p in P.part_dep])

    # --- Fig. 1: mapa
    fig, ax = plt.subplots(figsize=(8.2, 6.4))
    ax.scatter(m["x"][conf_p, 0], m["x"][conf_p, 1], s=16, c=cor_p[conf_p], alpha=0.55, edgecolors=FUNDO, linewidths=0.4)
    cent = pd.DataFrame(m["x"][conf_p], columns=["x", "y"]).assign(p=P.part_periodo[conf_p]).groupby("p")
    n_per = cent.size()
    cent = cent.mean()
    # rótulos só para bancadas grandes (≥ 15 períodos) e para os polos da dim2; o resto está na Tabela 5
    cent = cent[cent.index.isin(["PL", "NOVO", "UNIÃO", "REPUBLICANOS", "MDB", "PSB", "PT", "PCdoB", "REDE", "PSOL"])]
    rotulos_partidos(ax, cent)
    ax.axhline(0, color=GRADE, lw=1), ax.axvline(0, color=GRADE, lw=1)
    ax.set_xlabel("Dimensão 1: oposição (−)  ×  governo (+)")
    ax.set_ylabel("Dimensão 2: centrão (−)  ×  polos ideológicos (+)")
    legenda_blocos(ax, loc="lower left", fontsize=8.5)
    fig.savefig(FIGS / "fig1_mapa_pontos_ideais.png"), plt.close(fig)

    # --- Fig. 2: dimensionalidade
    y, fold = P.y, _G["fold"]
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    ks = [1, 2, 3, 4]
    accs = np.array([[acc(pred[k][fold == f], y[fold == f]) for f in range(N_FOLDS)] for k in ks]) * 100
    ax = axs[0]
    ax.errorbar(ks, accs.mean(1), yerr=accs.std(1, ddof=1), color=COR["Esquerda"], lw=2, marker="o", ms=7,
                mec=FUNDO, mew=1.5, capsize=3)
    for k, a in zip(ks, accs.mean(1)):
        ax.annotate(f"{a:.1f}".replace(".", ","), (k, a), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=9)
    for nome, chave in [("maioria da votação", "maioria"), ("orientação da bancada", "orientacao"),
                        ("maioria do partido na votação", "maioria_partido")]:
        a = acc(pred[chave], y) * 100
        ax.axhline(a, color=TINTA2, lw=1)
        ax.annotate(f"{nome}: {a:.1f}".replace(".", ","), (4.45, a), xytext=(0, 3), textcoords="offset points",
                    ha="right", fontsize=8.5, color=TINTA2)
    ax.set_xticks(ks), ax.set_xlim(0.6, 4.5), ax.set_ylim(72, 95)
    ax.set_xlabel("Número de dimensões do modelo"), ax.set_ylabel("Acerto fora da amostra (%)")
    ax.set_title("a) Acurácia em validação cruzada (10 partições)")
    ax = axs[1]
    ll = [logloss(pred[k], y) for k in ks]
    ax.plot(ks, ll, color=COR["Esquerda"], lw=2, marker="o", ms=7, mec=FUNDO, mew=1.5)
    for k, a in zip(ks, ll):
        ax.annotate(f"{a:.3f}".replace(".", ","), (k, a), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=9)
    ax.set_xticks(ks), ax.set_xlim(0.6, 4.5), ax.set_ylim(min(ll) - 0.02, max(ll) + 0.02)
    ax.set_xlabel("Número de dimensões do modelo"), ax.set_ylabel("Log-loss fora da amostra (menor é melhor)")
    ax.set_title("b) Perda logarítmica")
    fig.tight_layout(), fig.savefig(FIGS / "fig2_dimensionalidade.png"), plt.close(fig)

    # --- Fig. 3: dim1 x alinhamento ao governo; x escala esquerda-direita
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.4))
    ax = axs[0]
    ok = conf_d & ~np.isnan(m["gov"])
    ax.scatter(100 * m["gov"][ok], m["u"][ok, 0], s=14, c=cor_d[ok], alpha=0.55, edgecolors=FUNDO, linewidths=0.4)
    ax.set_xlabel("Votos que seguem a orientação do Governo (%)"), ax.set_ylabel("Dimensão 1")
    ax.set_title("a) Deputados: dimensão 1 × alinhamento ao Governo")
    legenda_blocos(ax, loc="upper left", fontsize=8.5)
    ax = axs[1]
    tp = pd.DataFrame(RES["estrutura"]["partidos"])
    tp = tp[tp["campo"] != ""]
    ordem = {"esquerda": 0, "centro": 1, "direita": 2}
    xs = tp["campo"].map(ordem).to_numpy().astype(float)
    # espalha horizontalmente os partidos de um mesmo campo, em ordem de dim1, para não sobrepor rótulos
    for c in range(3):
        idx = np.where(xs == c)[0]
        idx = idx[np.argsort(tp["dim1 (média)"].to_numpy()[idx])]
        xs[idx] = c + np.linspace(-0.4, 0.4, len(idx)) if len(idx) > 1 else c
    ax.scatter(xs, tp["dim1 (média)"], s=40, c=[COR[bloco_de(p)] for p in tp["partido"]], edgecolors=FUNDO,
               linewidths=1, zorder=3)
    for k, (x_, (_, l)) in enumerate(zip(xs, tp.iterrows())):
        lado = 1 if k % 2 == 0 else -1
        ax.annotate(l["partido"], (x_, l["dim1 (média)"]), xytext=(6 * lado, -3), textcoords="offset points",
                    fontsize=7, color=TINTA, ha="left" if lado > 0 else "right")
    ax.set_xticks([0, 1, 2]), ax.set_xticklabels(["Esquerda", "Centro", "Direita"]), ax.set_xlim(-0.8, 2.8)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("Campo ideológico (classificação convencional)")
    ax.set_ylabel("Dimensão 1 (média do partido)")
    ax.set_title("b) Partidos: dimensão 1 × campo ideológico")
    fig.tight_layout(), fig.savefig(FIGS / "fig3_governo_ou_ideologia.png"), plt.close(fig)

    # --- Fig. 4: cargas das votações
    fig, ax = plt.subplots(figsize=(7.6, 5.6))
    go = np.where(tvot["or. Governo"].isna() | tvot["or. Oposição"].isna(), "sem as duas orientações",
                  np.where(tvot["or. Governo"] == tvot["or. Oposição"], "Governo e Oposição orientam igual",
                           "Governo e Oposição orientam opostos"))
    cores = {"Governo e Oposição orientam opostos": "#2a78d6", "Governo e Oposição orientam igual": "#eb6834",
             "sem as duas orientações": "#b9b8b2"}
    for nome in ["sem as duas orientações", "Governo e Oposição orientam opostos", "Governo e Oposição orientam igual"]:
        mk = go == nome
        ax.scatter(tvot.loc[mk, "b1"], tvot.loc[mk, "b2"], s=14, c=cores[nome], alpha=0.6, edgecolors=FUNDO,
                   linewidths=0.4, label=f"{nome} ({mk.sum()})")
    lim = np.abs(tvot[["b1", "b2"]].to_numpy()).max() * 1.05
    ax.plot([-lim, lim], [-lim, lim], color=GRADE, lw=1), ax.plot([-lim, lim], [lim, -lim], color=GRADE, lw=1)
    ax.axhline(0, color=GRADE, lw=1), ax.axvline(0, color=GRADE, lw=1)
    ax.set_xlabel("Carga na dimensão 1 (b1): > 0 = governistas votam Sim")
    ax.set_ylabel("Carga na dimensão 2 (b2): > 0 = polos (PSOL, NOVO) votam Sim")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=1, fontsize=8.5)
    fig.savefig(FIGS / "fig4_cargas_votacoes.png"), plt.close(fig)

    # --- Fig. 5: incerteza (partidos)
    tb = pd.DataFrame(RES["bootstrap"]["partidos"])
    fig, axs = plt.subplots(1, 2, figsize=(10, 5.2), sharey=True)
    yy = np.arange(len(tb))
    for ax, d, tit in [(axs[0], "dim1", "a) Dimensão 1 (oposição × governo)"), (axs[1], "dim2", "b) Dimensão 2 (centrão × polos)")]:
        cs = [COR[bloco_de(p)] for p in tb["partido"]]
        for k in range(len(tb)):
            ax.plot([tb[f"{d} IC2,5"].iloc[k], tb[f"{d} IC97,5"].iloc[k]], [yy[k], yy[k]], color=cs[k], lw=2, solid_capstyle="round")
        ax.scatter(tb[d], yy, s=45, c=cs, edgecolors=FUNDO, linewidths=1.5, zorder=3)
        ax.axvline(0, color=GRADE, lw=1)
        ax.set_title(tit), ax.set_xlabel("Média do partido e IC 95% (bootstrap por proposição)")
    axs[0].set_yticks(yy), axs[0].set_yticklabels(tb["partido"])
    legenda_blocos(axs[0], loc="lower right", fontsize=8.5)
    fig.tight_layout(), fig.savefig(FIGS / "fig5_incerteza_partidos.png"), plt.close(fig)

    # --- Fig. 6: incerteza individual × nº de votos
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, k, tit in [(axs[0], 0, "a) Dimensão 1"), (axs[1], 1, "b) Dimensão 2")]:
        ax.scatter(P.nv_dep, se[:, k], s=12, c=cor_d, alpha=0.55, edgecolors=FUNDO, linewidths=0.3)
        ax.axvline(MIN_VOTOS, color=TINTA2, lw=1)
        ax.set_xscale("log"), ax.set_xlabel("Número de votos do deputado (escala log)"), ax.set_title(tit)
    axs[0].set_ylabel("Erro-padrão bootstrap do ponto ideal")
    axs[0].annotate("limiar de 50 votos", (MIN_VOTOS, axs[0].get_ylim()[1] * 0.93), xytext=(5, 0),
                    textcoords="offset points", fontsize=8.5, color=TINTA2)
    legenda_blocos(axs[1], loc="upper right", fontsize=8.5)
    fig.tight_layout(), fig.savefig(FIGS / "fig6_incerteza_deputados.png"), plt.close(fig)

    # --- Fig. 7: plenário × comissões; IRT × SVD
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.6))
    ax = axs[0]
    ax.scatter(dcom["plen1"], dcom["com1"], s=16, c=[COR[bloco_de(p)] for p in dcom["partido"]], alpha=0.6,
               edgecolors=FUNDO, linewidths=0.4)
    l = [min(dcom["plen1"].min(), dcom["com1"].min()), max(dcom["plen1"].max(), dcom["com1"].max())]
    ax.plot(l, l, color=GRADE, lw=1)
    ax.set_xlabel("Dimensão 1 estimada só com o plenário"), ax.set_ylabel("Dimensão 1 estimada só com as comissões")
    ax.set_title(f"a) Plenário × comissões ({len(dcom)} deputados)")
    legenda_blocos(ax, loc="upper left", fontsize=8.5)
    ax = axs[1]
    ax.scatter(m["u"][conf_d, 1], sc_svd[:, 1], s=14, c=cor_d[conf_d], alpha=0.55, edgecolors=FUNDO, linewidths=0.4)
    ax.set_xlabel("Dimensão 2, IRT"), ax.set_ylabel("Dimensão 2, SVD com imputação (alinhada)")
    ax.set_title("b) Segunda dimensão: IRT × SVD")
    fig.tight_layout(), fig.savefig(FIGS / "fig7_comissoes_e_svd.png"), plt.close(fig)

    # --- Fig. 8: ganho da segunda dimensão por partido
    t = pd.DataFrame(RES["ganho_por_partido"]).sort_values("ganho 1D→2D")
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(t["partido"], 100 * t["ganho 1D→2D"], height=0.6, color=[COR[bloco_de(p)] for p in t["partido"]])
    for p, g in zip(t["partido"], 100 * t["ganho 1D→2D"]):
        ax.annotate(f"{g:+.1f}".replace(".", ","), (max(g, 0), p), xytext=(4, 0), textcoords="offset points",
                    va="center", ha="left", fontsize=8.5)
    ax.axvline(0, color=TINTA2, lw=1), ax.grid(axis="y", visible=False)
    ax.set_xlabel("Ganho de acerto fora da amostra de 1D para 2D (pontos percentuais)")
    legenda_blocos(ax, loc="lower right", fontsize=8.5)
    fig.savefig(FIGS / "fig8_ganho_por_partido.png"), plt.close(fig)

    # --- Fig. 9: o que o eixo único distorce
    m = _G["pos12"].dropna(subset=["1D"])
    tp = pd.DataFrame(RES["comparacao"]["por_partido"]).set_index("partido")
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 5))
    ax = axs[0]
    ordem = m.sort_values("2D: dim. 1").index
    yy = np.arange(len(ordem))
    for k, pa in enumerate(ordem):
        a1, a2 = m.loc[pa, "2D: dim. 1"], m.loc[pa, "1D"]
        ax.plot([a1, a2], [k, k], color=GRADE, lw=2, zorder=1)
    ax.scatter(m.loc[ordem, "2D: dim. 1"], yy, s=45, color="#2a78d6", edgecolors=FUNDO, linewidths=1.5, zorder=3,
               label="dimensão 1 do modelo de dois eixos")
    ax.scatter(m.loc[ordem, "1D"], yy, s=45, color="#eb6834", edgecolors=FUNDO, linewidths=1.5, zorder=3,
               label="modelo de um eixo só")
    ax.set_yticks(yy), ax.set_yticklabels(ordem), ax.axvline(0, color=GRADE, lw=1)
    ax.set_xlabel("Posição média do partido (escore padronizado; + = governista)")
    ax.set_title("a) Posições: um eixo × dois eixos")
    ax.legend(loc="lower right", fontsize=8.5)
    ax = axs[1]
    tp = tp.loc[[p_ for p_ in ordem if p_ in tp.index]]
    pct1 = 100 * tp["erra a maioria do partido: 1D"] / tp["votações"]
    pct2 = 100 * tp["erra a maioria do partido: 2D"] / tp["votações"]
    yy = np.arange(len(tp))
    ax.barh(yy + 0.2, pct1, height=0.38, color="#eb6834", label="modelo de um eixo só")
    ax.barh(yy - 0.2, pct2, height=0.38, color="#2a78d6", label="modelo de dois eixos")
    ax.set_yticks(yy), ax.set_yticklabels(tp.index), ax.grid(axis="y", visible=False)
    ax.set_xlabel("Votações em que o modelo erra o lado da maioria do partido (%)")
    ax.set_title("b) Posição coletiva dos partidos")
    ax.legend(loc="center right", fontsize=8.5)
    fig.tight_layout(), fig.savefig(FIGS / "fig9_um_eixo_x_dois_eixos.png"), plt.close(fig)


# =============================================================================== main
ETAPAS = ["dados", "reproducao", "cv", "final", "estrutura", "dim2", "recortes", "robustez", "bootstrap", "orgaos", "svd",
          "anos", "figuras"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--etapas", nargs="*", default=ETAPAS)
    ap.add_argument("--refazer", action="store_true")
    args = ap.parse_args()
    global CACHE, FIGS, TABS, AQUI_RES, N_BOOT, MIN_VOTOS, N_BOOT_1D
    AQUI_RES = AQUI
    if os.environ.get("TESTE_RAPIDO"):
        base = Path(os.environ["TESTE_RAPIDO"])
        CACHE, FIGS, TABS, AQUI_RES, N_BOOT = base / "cache", base / "figuras", base / "tabelas", base, 4
        MIN_VOTOS = 5
        N_BOOT_1D = 4
        base.mkdir(parents=True, exist_ok=True)
    for d in (CACHE, FIGS, TABS):
        d.mkdir(exist_ok=True)
    arq_res = AQUI_RES / "resultados.json"
    if arq_res.exists():
        RES.update(json.loads(arq_res.read_text(encoding="utf-8")))
    quer = lambda e: e in args.etapas
    rf = args.refazer

    bruto = carregar_votos()
    P = Painel(preparar(bruto))
    _G.update(P=P, bruto=bruto, fold=np.random.default_rng(2026).integers(0, N_FOLDS, len(P.y)))
    print(f"{len(P.y):,} votos, {P.n_j} votações, {P.n_u} deputados, {P.n_i} períodos", flush=True)

    if quer("dados"):
        etapa_dados(P, bruto)
    if quer("reproducao"):
        RES["reproducao"] = em_cache("reproducao", lambda: paralelo(_reproducao, [0])[0], rf)
    vt = pd.read_parquet(DADOS / "votacoes.parquet").set_index("idVotacao")["proposicao_id"]
    prop = vt.reindex(P.votacoes).fillna(pd.Series(P.votacoes, index=P.votacoes)).to_numpy()
    _G["cluster"] = pd.factorize(prop)[0]
    pred = em_cache("cv", lambda: etapa_cv(P), rf)
    pq, cq = em_cache("cv_quad", lambda: etapa_cv_quad(P), rf)
    pred["quad"] = pq
    _G["cv_quad_conv"] = [bool(c) for c in cq]
    if quer("cv"):
        resumo_cv(P, pred)
    finais = em_cache("finais", lambda: dict(zip([1, 2, 3, 4], paralelo(_final_tarefa, [1, 2, 3, 4]))), rf)
    m = finais[2]
    if quer("final"):
        ajuste_dentro_da_amostra(P, finais)
        etapa_dim3(P, P.orientar(finais[3]) if "R" not in finais[3] else finais[3], m)
    O = etapa_estrutura(P, m)
    _G["O"] = O
    tvot = etapa_dim2(P, m, O)
    boot1d = em_cache("bootstrap_1d", lambda: (lambda s_: (np.array([a_ for a_, _ in s_]), np.array([c_ for _, c_ in s_])))(
        paralelo(_boot1d_tarefa, list(range(N_BOOT_1D)))), rf)
    pos12 = etapa_comparacao(P, pred, finais, tvot, boot1d)
    _G["pos12"] = pos12
    if quer("recortes"):
        RES["recortes"] = em_cache("recortes", lambda: (etapa_recortes(P, m), RES["recortes"])[1], rf)
    if quer("robustez"):
        em_cache("robustez", lambda: (etapa_robustez(P, m), RES["robustez"])[1], rf)
        RES["robustez"] = pickle.loads((CACHE / "robustez.pkl").read_bytes())
    U, X, conv, ang = em_cache("bootstrap", lambda: etapa_bootstrap(P, m), rf)
    se = resumo_bootstrap(P, m, U, X, conv, ang)
    dcom = em_cache("orgaos", lambda: (etapa_orgaos(P, m), RES["orgaos"]), rf)
    RES["orgaos"] = dcom[1]
    sc = em_cache("svd", lambda: (etapa_svd(P, m), RES["svd"]), rf)
    RES["svd"] = sc[1]
    if quer("anos"):
        em_cache("anos", lambda: (etapa_anos(P, m), {k: RES[k] for k in ["anos", "partidos_dim1_por_ano", "partidos_dim2_por_ano"]})[1], rf)
        RES.update(pickle.loads((CACHE / "anos.pkl").read_bytes()))
    if quer("figuras"):
        figuras(P, m, pred, tvot, se, dcom[0], sc[0])

    arq_res.write_text(json.dumps(RES, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print("ok ->", arq_res)


if __name__ == "__main__":
    main()
