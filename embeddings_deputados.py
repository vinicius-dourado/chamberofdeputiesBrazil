"""
Representações vetoriais ("embeddings") dos deputados por aspecto, a partir das
tabelas de dados/leg<N>/ geradas por baixar_legislatura.py e baixar_discursos.py.

Aspectos (cada um gera dados/leg<N>/embeddings/emb_<aspecto>.parquet):
  votos            pontos ideais (IRT 2D, à la IDEAL/NOMINATE) a partir das votações nominais
  votos_intra      pontos ideais *dentro do partido*: o modelo absorve a posição de cada
                   partido em cada votação, sobrando só a variação individual
  temas            perfil temático das proposições apresentadas (embedding de Hellinger)
  frentes          participação em frentes parlamentares (TF-IDF + SVD)
  discursos        embeddings de sentença dos discursos, agregados por deputado
  (trajetoria_partidaria.parquet: trocas de partido e deslocamento do ponto ideal)

Também gera:
  avaliacao.json          métricas de qualidade de cada representação
  similaridades.parquet   similaridade entre todos os pares de deputados, por aspecto e combinada

Uso:
  python embeddings_deputados.py                       # todos os aspectos disponíveis
  python embeddings_deputados.py --aspectos votos temas
  python embeddings_deputados.py --aspectos nada --consultar "Tabata" --aspecto discursos_fala
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

RNG = np.random.default_rng(42)


# ============================================================================ IRT
def ajustar_irt(i, j, y, n_i, n_j, ndim=2, grupos=None, lam_x=1.0, lam_b=0.04, lam_a=0.01,
                lam_g=0.01, lam_d=None, base=None, centrar=None):
    """Regressão logística bilinear (modelo de pontos ideais / IRT 2PL multidimensional):
        P(Sim) = σ(a_j + g_{grupo(obs)} + b_j · x_i)
    i, j: índices de linha (legislador) e coluna (votação) de cada voto observado.
    grupos: índice opcional de efeito fixo por observação (ex.: partido×votação).
    base: se dado, x_i = u_base(i) + δ_i, com δ penalizado por lam_d (pontos por período).
    centrar: índice de grupo por linha i; força média zero de x dentro de cada grupo
    (usado com efeitos fixos partido×votação, que já absorvem a posição do partido).
    Estimação por máxima verossimilhança penalizada (priors normais) com L-BFGS."""
    n_g = 0 if grupos is None else grupos.max() + 1
    n_u = 0 if base is None else base.max() + 1
    tam = [n_j, n_j * ndim, n_i * ndim, n_g, n_u * ndim]
    cortes = np.cumsum([0] + tam)

    def desemp(th):
        a = th[cortes[0]:cortes[1]]
        b = th[cortes[1]:cortes[2]].reshape(n_j, ndim)
        d = th[cortes[2]:cortes[3]].reshape(n_i, ndim)
        g = th[cortes[3]:cortes[4]]
        u = th[cortes[4]:cortes[5]].reshape(n_u, ndim)
        x = d + u[base] if base is not None else d
        if centrar is not None:
            x = x - (np.stack([np.bincount(centrar, x[:, k]) for k in range(ndim)], 1) / n_c[:, None])[centrar]
        return a, b, d, g, u, x

    lam_dd = lam_x if base is None else lam_d
    n_c = None if centrar is None else np.bincount(centrar).astype(float)

    def f(th):
        a, b, d, g, u, x = desemp(th)
        z = a[j] + np.einsum("nk,nk->n", b[j], x[i])
        if grupos is not None:
            z = z + g[grupos]
        p = expit(z)
        ll = -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12))
        pen = (lam_a * a @ a + lam_b * np.sum(b * b) + lam_dd * np.sum(d * d)
               + lam_g * g @ g + lam_x * np.sum(u * u))
        r = p - y
        ga = np.bincount(j, r, n_j) + 2 * lam_a * a
        gb = np.stack([np.bincount(j, r * x[i, k], n_j) for k in range(ndim)], 1) + 2 * lam_b * b
        gx = np.stack([np.bincount(i, r * b[j, k], n_i) for k in range(ndim)], 1)
        if centrar is not None:   # projeção (centragem) é simétrica: aplica-se ao gradiente
            gx = gx - (np.stack([np.bincount(centrar, gx[:, k]) for k in range(ndim)], 1) / n_c[:, None])[centrar]
        gd = gx + 2 * lam_dd * d
        gg = (np.bincount(grupos, r, n_g) + 2 * lam_g * g) if grupos is not None else np.zeros(0)
        gu = np.zeros((n_u, ndim))
        if base is not None:
            for k in range(ndim):
                gu[:, k] = np.bincount(base, gx[:, k], n_u)
            gu += 2 * lam_x * u
        return ll + pen, np.concatenate([ga, gb.ravel(), gd.ravel(), gg, gu.ravel()])

    th0 = RNG.normal(0, 0.1, cortes[-1])
    res = minimize(f, th0, jac=True, method="L-BFGS-B", options={"maxiter": 15000, "maxfun": 30000})
    if not res.success:
        print("    aviso: otimização não convergiu:", res.message)
    a, b, d, g, u, x = desemp(res.x)
    return dict(a=a, b=b, d=d, g=g, u=u, x=x, convergiu=res.success, nll=res.fun)


def rotacionar(x_ref, *outros):
    """Centraliza e gira para eixos principais (dim1 = maior variância)."""
    mu = x_ref.mean(0)
    _, _, vt = np.linalg.svd(x_ref - mu, full_matrices=False)
    return [(m - mu) @ vt.T for m in (x_ref,) + outros], vt


def preparar_votos(pasta, min_minoria=0.025):
    v = pd.read_parquet(pasta / "votos.parquet")
    mapa = {"Sim": 1.0, "Não": 0.0, "Obstrução": 0.0}   # obstrução = oposição à matéria
    v = v[v["voto"].isin(mapa)].copy()
    v["y"] = v["voto"].map(mapa)
    # remove votações quase unânimes (pouca informação, como no NOMINATE)
    minoria = v.groupby("idVotacao")["y"].agg(lambda s: min(s.mean(), 1 - s.mean()))
    v = v[v["idVotacao"].isin(minoria[minoria >= min_minoria].index)]
    v["deputado_id"] = v["deputado_id"].astype(int)
    return v


def acuracia(p, y):
    return float(np.mean((p > 0.5) == (y > 0.5)))


def logloss(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def predizer(m, i, j, grupos=None):
    z = m["a"][j] + np.einsum("nk,nk->n", m["b"][j], m["x"][i])
    if grupos is not None:
        z = z + m["g"][grupos]
    return expit(z)


def emb_votos(pasta, deputados, saida, ndim=2):
    v = preparar_votos(pasta)
    print(f"  {len(v):,} votos, {v['idVotacao'].nunique()} votações, {v['deputado_id'].nunique()} deputados")
    # linhas = deputado×partido (período de filiação); x = u_deputado + δ_período
    v["periodo"] = v["deputado_id"].astype(str) + "|" + v["deputado_siglaPartido"]
    i, periodos = pd.factorize(v["periodo"])
    j, votacoes = pd.factorize(v["idVotacao"])
    base_dep, deps = pd.factorize(periodos.str.split("|").str[0].astype(int))
    grp, _ = pd.factorize(v["deputado_siglaPartido"] + "|" + v["idVotacao"])
    part_periodo, _ = pd.factorize(periodos.str.split("|").str[1])
    y = v["y"].to_numpy()
    n_i, n_j = len(periodos), len(votacoes)

    # ---- validação: 10% dos votos fora do ajuste
    teste = RNG.random(len(y)) < 0.10
    tr = ~teste
    aval = {}
    m = ajustar_irt(i[tr], j[tr], y[tr], n_i, n_j, ndim, base=base_dep, lam_d=4.0)
    aval["irt_acuracia"] = acuracia(predizer(m, i[teste], j[teste]), y[teste])
    aval["irt_logloss"] = logloss(predizer(m, i[teste], j[teste]), y[teste])
    m1 = ajustar_irt(i[tr], j[tr], y[tr], n_i, n_j, 1, base=base_dep, lam_d=4.0)
    aval["irt_1d_acuracia"] = acuracia(predizer(m1, i[teste], j[teste]), y[teste])
    # baselines: maioria da votação; orientação do partido do deputado
    maioria = pd.Series(y[tr]).groupby(j[tr]).mean().reindex(range(n_j)).fillna(0.5).to_numpy()
    aval["base_maioria_acuracia"] = acuracia(maioria[j[teste]], y[teste])
    ori = v["orientacao_partido"].map({"Sim": 1.0, "Não": 0.0, "Obstrução": 0.0}).to_numpy()
    ori = np.where(np.isnan(ori), maioria[j], ori)
    aval["base_orientacao_partido_acuracia"] = acuracia(ori[teste], y[teste])
    mg = ajustar_irt(i[tr], j[tr], y[tr], n_i, n_j, ndim, grupos=grp[tr], base=base_dep, lam_d=4.0,
                     centrar=part_periodo)
    aval["irt_intrapartido_acuracia"] = acuracia(predizer(mg, i[teste], j[teste], grp[teste]), y[teste])
    print("  validação:", {k: round(x, 3) for k, x in aval.items()})

    # ---- ajuste final com todos os votos
    resultados = {}
    for nome, grupos in [("votos", None), ("votos_intra", grp)]:
        m = ajustar_irt(i, j, y, n_i, n_j, ndim, grupos=grupos, base=base_dep, lam_d=4.0,
                        centrar=None if grupos is None else part_periodo)
        if grupos is None:
            u_dep = m["u"]
        else:   # ponto do deputado = média dos seus períodos (já centrados no partido)
            u_dep = np.stack([np.bincount(base_dep, m["x"][:, k]) for k in range(ndim)], 1) \
                / np.bincount(base_dep)[:, None]
        (u, x), _ = rotacionar(u_dep, m["x"])
        # sentido: dim1 positivo = mais governista
        gov = (v.assign(s=v["seguiu_orientacao_governo"].astype(float))
               .groupby("deputado_id")["s"].mean().reindex(deps).to_numpy())
        ok = ~np.isnan(gov)
        if np.corrcoef(u[ok, 0], gov[ok])[0, 1] < 0:
            u[:, 0] *= -1
            x[:, 0] *= -1
        nvot = np.bincount(base_dep[i], minlength=len(deps))
        df = pd.DataFrame(u, columns=[f"dim{k + 1}" for k in range(ndim)])
        df.insert(0, "deputado_id", deps)
        df["n_votos"] = nvot
        df["confiavel"] = nvot >= 50
        resultados[nome] = (df, x, periodos)
        salvar_emb(df, nome, deputados, saida)

    # taxas de alinhamento (atributos interpretáveis)
    taxas = (v.assign(gov=v["seguiu_orientacao_governo"].astype(float),
                      par=v["seguiu_orientacao_partido"].astype(float))
             .groupby("deputado_id")[["gov", "par"]].mean()
             .rename(columns={"gov": "taxa_alinhamento_governo", "par": "taxa_alinhamento_partido"}))
    return resultados, aval, taxas


# =================================================================== trajetória
def trajetoria(pasta, res_votos, deputados, saida):
    _, x, periodos = res_votos
    per = pd.DataFrame(x, columns=["dim1", "dim2"])
    per["deputado_id"] = periodos.str.split("|").str[0].astype(int)
    per["partido"] = periodos.str.split("|").str[1]
    f = pd.read_parquet(pasta / "deputados_partidos.parquet")
    f["id"] = f["id"].astype(int)
    linhas = []
    for dep, g in f.sort_values("dataInicio").groupby("id"):
        partidos = g["siglaPartido"].tolist()
        p = per[per["deputado_id"] == dep].set_index("partido")
        desloc = np.nan
        if len(partidos) > 1 and partidos[0] in p.index and partidos[-1] in p.index:
            desloc = p.loc[partidos[-1], "dim1"] - p.loc[partidos[0], "dim1"]
        linhas.append({"deputado_id": dep, "n_trocas": len(partidos) - 1,
                       "sequencia_partidos": " > ".join(partidos),
                       "primeiro_partido": partidos[0], "ultimo_partido": partidos[-1],
                       "deslocamento_dim1": desloc})
    t = pd.DataFrame(linhas)
    # posição média de cada partido (dim1) para medir o "salto" ideológico da troca
    pos = per.groupby("partido")["dim1"].median()
    t["salto_partidario_dim1"] = t["ultimo_partido"].map(pos) - t["primeiro_partido"].map(pos)
    t = deputados[["id", "nome"]].rename(columns={"id": "deputado_id"}).merge(t, on="deputado_id", how="right")
    t.to_parquet(saida / "trajetoria_partidaria.parquet", index=False)
    print(f"  -> trajetoria_partidaria: {len(t)} deputados, {(t.n_trocas > 0).sum()} com troca")
    return t


# =============================================================== temas / frentes
def emb_temas(pasta, deputados, saida):
    a = pd.read_parquet(pasta / "proposicoes_autores.parquet")
    t = pd.read_parquet(pasta / "proposicoes_temas.parquet")
    p = pd.read_parquet(pasta / "proposicoes.parquet", columns=["id", "siglaTipo"])
    peso_tipo = {"PL": 1.0, "PLP": 1.0, "PEC": 1.0, "PDL": 1.0, "PRC": 1.0,
                 "RIC": 0.3, "INC": 0.3, "PFC": 0.3, "SIT": 0.3}
    a["w_aut"] = 1 / a.groupby("idProposicao")["idDeputadoAutor"].transform("size")  # autoria fracionada
    t["w_tema"] = 1 / t.groupby("idProposicao")["codTema"].transform("size")
    x = (a.merge(p.rename(columns={"id": "idProposicao"}), on="idProposicao")
         .merge(t[["idProposicao", "tema", "w_tema"]], on="idProposicao"))
    x["w"] = x["w_aut"] * x["w_tema"] * x["siglaTipo"].map(peso_tipo).fillna(0.3)
    m = x.pivot_table(index="idDeputadoAutor", columns="tema", values="w", aggfunc="sum", fill_value=0)
    vol = m.sum(axis=1)
    prop = m.div(vol, axis=0)
    # embedding de Hellinger: distância euclidiana entre sqrt(proporções) = distância de Hellinger
    emb = np.sqrt(prop)
    df = pd.DataFrame(emb.to_numpy(), columns=[f"t_{c}" for c in prop.columns])
    df.insert(0, "deputado_id", m.index.astype(int))
    df["volume_ponderado"] = vol.to_numpy()
    df["confiavel"] = df["volume_ponderado"] >= 3
    salvar_emb(df, "temas", deputados, saida)
    return df


def emb_frentes(pasta, deputados, saida, ndim=16):
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfTransformer
    f = pd.read_parquet(pasta / "frentes_deputados.parquet")
    f["w"] = np.where(f["cargo"].str.startswith("Coord"), 3.0, 1.0)
    m = f.pivot_table(index="deputado_id", columns="idFrente", values="w", aggfunc="max", fill_value=0)
    tf = TfidfTransformer(sublinear_tf=False).fit_transform(m.to_numpy())
    svd = TruncatedSVD(ndim, random_state=0)
    z = svd.fit_transform(tf)
    df = pd.DataFrame(z, columns=[f"dim{k + 1}" for k in range(ndim)])
    df.insert(0, "deputado_id", m.index.astype(int))
    df["n_frentes"] = (m > 0).sum(axis=1).to_numpy()
    df["confiavel"] = df["n_frentes"] >= 5
    salvar_emb(df, "frentes", deputados, saida)
    print(f"  variância explicada (SVD {ndim}): {svd.explained_variance_ratio_.sum():.2f}")
    return df



# =================================================================== discursos
PESO_TIPO_DISCURSO = {"PELA ORDEM": 0.5, "DISCURSO ENCAMINHADO": 1.0}


def emb_discursos(pasta, deputados, saida, modelo="intfloat/multilingual-e5-small", ndim=32):
    """Embeddings de sentença (modelo multilíngue) de cada discurso, agregados por deputado.
    Duas visões: 'discursos_tema' (sumário + palavras-chave, redigidos pela Câmara: assunto)
    e 'discursos_fala' (transcrição: palavras do próprio deputado, retórica/posicionamento).
    Agregação: média ponderada -> remoção da média global (os embeddings são anisotrópicos)
    -> PCA (ndim) -> normalização L2."""
    from sentence_transformers import SentenceTransformer
    from sklearn.decomposition import PCA
    d = pd.read_parquet(pasta / "discursos.parquet")
    d["deputado_id"] = d["deputado_id"].astype(int)
    d = d[d["transcricao"].fillna("").str.len() > 50].reset_index(drop=True)
    st = SentenceTransformer(modelo)
    st.max_seq_length = 512
    textos = {
        "discursos_tema": ("passage: " + d["sumario"].fillna("") + " " + d["keywords"].fillna("")).tolist(),
        "discursos_fala": ("passage: " + d["transcricao"].str.replace(r"^O SR?A?\. [^)]*\)\s*-\s*", "",
                                                                    regex=True)).tolist(),
    }
    w = d["tipoDiscurso"].map(PESO_TIPO_DISCURSO).fillna(1.0).to_numpy()
    res = {}
    for nome, txt in textos.items():
        cache = saida / f"vetores_{nome}.npy"
        if cache.exists() and len(np.load(cache, mmap_mode="r")) == len(d):
            e = np.load(cache).astype(np.float32)
        else:
            # transcrições: primeiros 256 tokens (custo ~4x menor em CPU; a abertura do
            # discurso concentra assunto e posicionamento); sumários: até 512
            st.max_seq_length = 256 if nome == "discursos_fala" else 512
            print(f"  codificando {len(txt):,} textos ({nome})...", flush=True)
            e = st.encode(txt, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
            np.save(cache, e.astype(np.float16))
        e = e - e.mean(0)                                   # remove componente comum
        ids, inv = np.unique(d["deputado_id"].to_numpy(), return_inverse=True)
        agg = np.zeros((len(ids), e.shape[1]))
        np.add.at(agg, inv, e * w[:, None])
        agg /= np.bincount(inv, w)[:, None]
        z = PCA(ndim, random_state=0).fit_transform(agg)
        z /= np.linalg.norm(z, axis=1, keepdims=True)
        df = pd.DataFrame(z, columns=[f"e_{k + 1}" for k in range(ndim)])
        df.insert(0, "deputado_id", ids)
        df["n_discursos"] = np.bincount(inv)
        df["confiavel"] = df["n_discursos"] >= 10
        salvar_emb(df, nome, deputados, saida)
        res[nome] = df
    return res


# ===================================================== avaliação / similaridade
VISOES = ["votos", "votos_intra", "temas", "frentes", "discursos_tema", "discursos_fala"]


def carregar_visoes(saida, so_confiaveis=True):
    out = {}
    for v in VISOES:
        arq = saida / f"emb_{v}.parquet"
        if arq.exists():
            df = pd.read_parquet(arq)
            out[v] = df[df["confiavel"]] if so_confiaveis else df
    return out


def distancias(X, metrica):
    from sklearn.metrics import pairwise_distances
    return pairwise_distances(X, metric=metrica)


METRICA = {"votos": "euclidean", "votos_intra": "euclidean", "temas": "euclidean",
           "frentes": "cosine", "discursos_tema": "cosine", "discursos_fala": "cosine"}


def avaliar(visoes, saida):
    """O quanto cada visão captura (a) o partido e (b) a posição governo×oposição nas votações."""
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import cross_val_predict, cross_val_score
    from sklearn.neighbors import KNeighborsClassifier
    alvo = visoes["votos"].set_index("deputado_id")["dim1"]
    aval = {}
    for v, df in visoes.items():
        ids, X = matriz(df)
        part = df["siglaPartido"].to_numpy()
        comuns = pd.Series(part).value_counts()
        ok = pd.Series(part).isin(comuns[comuns >= 5].index).to_numpy()
        knn = KNeighborsClassifier(5, metric=METRICA[v])
        acc = cross_val_score(knn, X[ok], part[ok], cv=5).mean()
        r = {"n_deputados": int(len(ids)), "knn5_acerta_partido": round(float(acc), 3),
             "acerto_partido_ao_acaso": round(float((comuns / comuns.sum()).max()), 3)}
        if v != "votos":
            y = alvo.reindex(ids).to_numpy()
            m = ~np.isnan(y)
            pred = cross_val_predict(RidgeCV(alphas=np.logspace(-3, 3, 13)), X[m], y[m], cv=5)
            r["r2_preve_dim1_votos"] = round(float(1 - np.mean((pred - y[m]) ** 2) / np.var(y[m])), 3)
        aval[v] = r
    return aval


def snf(Ws, K=20, t=20):
    """Similarity Network Fusion (Wang et al., 2014, Nature Methods)."""
    def norm(W):
        W = W.copy()
        np.fill_diagonal(W, 0)
        P = W / (2 * W.sum(1, keepdims=True))
        np.fill_diagonal(P, 0.5)
        return P

    def knn(W):
        S = np.zeros_like(W)
        idx = np.argsort(-W, axis=1)[:, 1:K + 1]
        rows = np.arange(len(W))[:, None]
        S[rows, idx] = W[rows, idx]
        return S / S.sum(1, keepdims=True)

    Ps = [norm(W) for W in Ws]
    Ss = [knn(W) for W in Ws]
    for _ in range(t):
        novos = []
        for v in range(len(Ps)):
            outros = sum(Ps[u] for u in range(len(Ps)) if u != v) / (len(Ps) - 1)
            P = Ss[v] @ outros @ Ss[v].T
            novos.append(norm((P + P.T) / 2))
        Ps = novos
    F = sum(Ps) / len(Ps)
    return (F + F.T) / 2


def afinidade(D, K=20, mu=0.5):
    ordenado = np.sort(D, axis=1)[:, 1:K + 1].mean(1)
    eps = (ordenado[:, None] + ordenado[None, :] + D) / 3
    return np.exp(-(D ** 2) / (mu * eps ** 2 + 1e-12))


def fusao(visoes, deputados, saida):
    """Tabela de pares: proximidade em cada visão (percentil: 1 = par mais próximo possível,
    0 = mais distante) + média das visões + SNF (fusão não linear) entre deputados que têm
    todas as visões."""
    todos = sorted(set().union(*[set(df["deputado_id"]) for df in visoes.values()]))
    pos = {d: k for k, d in enumerate(todos)}
    n = len(todos)
    iu = np.triu_indices(n, 1)
    pares = pd.DataFrame({"deputado_a": np.array(todos)[iu[0]], "deputado_b": np.array(todos)[iu[1]]})
    afins, comuns = [], set(todos)
    for v, df in visoes.items():
        ids, X = matriz(df)
        D = distancias(X, METRICA[v])
        full = np.full((n, n), np.nan)
        k = np.array([pos[i] for i in ids])
        full[np.ix_(k, k)] = D
        dv = full[iu]
        pct = pd.Series(dv).rank(pct=True, ascending=False).to_numpy()
        pares[f"prox_{v}"] = np.round(pct, 4)
        comuns &= set(ids)
    pares["prox_media"] = pares[[c for c in pares if c.startswith("prox_")]].mean(axis=1, skipna=False).round(4)
    # SNF nos deputados presentes em todas as visões
    comuns = sorted(comuns)
    for v, df in visoes.items():
        df = df.set_index("deputado_id").loc[comuns].reset_index()
        _, X = matriz(df)
        afins.append(afinidade(distancias(X, METRICA[v])))
    F = snf(afins)
    s = pd.DataFrame(F, index=comuns, columns=comuns).stack().rename("snf").reset_index()
    s.columns = ["deputado_a", "deputado_b", "snf"]
    s = s[s["deputado_a"] < s["deputado_b"]]
    s["prox_snf"] = s["snf"].rank(pct=True).round(4)
    pares = pares.merge(s[["deputado_a", "deputado_b", "prox_snf"]], on=["deputado_a", "deputado_b"], how="left")
    nomes = deputados.set_index("id")["nome"]
    pares.insert(1, "nome_a", pares["deputado_a"].map(nomes))
    pares.insert(3, "nome_b", pares["deputado_b"].map(nomes))
    pares.to_parquet(saida / "similaridades.parquet", index=False)
    np.save(saida / "snf_matriz.npy", F)
    pd.Series(comuns, name="deputado_id").to_frame().to_parquet(saida / "snf_ids.parquet", index=False)
    print(f"  -> similaridades: {len(pares):,} pares; SNF com {len(comuns)} deputados em todas as visões")
    return pares


def consultar(saida, nome, aspecto="media", k=10):
    p = pd.read_parquet(saida / "similaridades.parquet")
    col = f"prox_{aspecto}"
    m = p[p["nome_a"].str.contains(nome, case=False) | p["nome_b"].str.contains(nome, case=False)].copy()
    alvo = m["nome_a"].where(m["nome_a"].str.contains(nome, case=False), m["nome_b"]).mode()[0]
    m = m[(m["nome_a"] == alvo) | (m["nome_b"] == alvo)].copy()
    m["outro"] = np.where(m["nome_a"] == alvo, m["nome_b"], m["nome_a"])
    cols = ["outro"] + [c for c in p.columns if c.startswith("prox_")]
    print(f"Mais próximos de {alvo} por '{aspecto}':")
    print(m.sort_values(col, ascending=False)[cols].head(k).to_string(index=False))

# ======================================================================== util
def salvar_emb(df, nome, deputados, saida):
    info = deputados[["id", "nome", "siglaPartido", "siglaUf"]].rename(columns={"id": "deputado_id"})
    df = info.merge(df, on="deputado_id", how="right")
    df.to_parquet(saida / f"emb_{nome}.parquet", index=False)
    print(f"  -> emb_{nome}: {len(df)} deputados x {sum(c.startswith(('dim', 't_', 'e_')) for c in df.columns)} dims")


def matriz(df):
    cols = [c for c in df.columns if c.startswith(("dim", "t_", "e_"))]
    return df["deputado_id"].to_numpy(), df[cols].to_numpy(float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legislatura", type=int, default=57)
    ap.add_argument("--dados", default="dados")
    ap.add_argument("--aspectos", nargs="+",
                    default=["votos", "temas", "frentes", "discursos", "fusao"])
    ap.add_argument("--consultar", help="nome do deputado: lista os mais próximos (use com --aspectos nada)")
    ap.add_argument("--aspecto", default="media", help="votos, votos_intra, temas, frentes, "
                    "discursos_tema, discursos_fala, media ou snf")
    args = ap.parse_args()
    pasta = Path(args.dados) / f"leg{args.legislatura}"
    saida = pasta / "embeddings"
    saida.mkdir(exist_ok=True)
    deputados = pd.read_parquet(pasta / "deputados.parquet")
    deputados["id"] = deputados["id"].astype(int)
    aval_arq = saida / "avaliacao.json"
    aval = json.loads(aval_arq.read_text()) if aval_arq.exists() else {}

    if "votos" in args.aspectos:
        print("Votações (pontos ideais)...")
        res, av, taxas = emb_votos(pasta, deputados, saida)
        aval["votos"] = av
        taxas.reset_index().to_parquet(saida / "alinhamento.parquet", index=False)
        trajetoria(pasta, res["votos"], deputados, saida)
    if "temas" in args.aspectos:
        print("Temas das proposições...")
        emb_temas(pasta, deputados, saida)
    if "frentes" in args.aspectos:
        print("Frentes parlamentares...")
        emb_frentes(pasta, deputados, saida)

    if "discursos" in args.aspectos:
        print("Discursos (embeddings de sentença)...")
        emb_discursos(pasta, deputados, saida)
    if "fusao" in args.aspectos:
        print("Avaliação e fusão...")
        visoes = carregar_visoes(saida)
        aval["representacoes"] = avaliar(visoes, saida)
        for v, r in aval["representacoes"].items():
            print(f"  {v:15s} {r}")
        fusao(visoes, deputados, saida)
    aval_arq.write_text(json.dumps(aval, indent=2, ensure_ascii=False))
    if args.consultar:
        consultar(saida, args.consultar, args.aspecto)


if __name__ == "__main__":
    main()
