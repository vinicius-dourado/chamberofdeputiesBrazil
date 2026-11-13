"""
Artigo 2 — Disciplina partidária, orientação das lideranças e variação intrapartidária
na 57ª Legislatura da Câmara dos Deputados.

Script reprodutível: gera todos os números (resultados.json), tabelas (tabelas/*.md) e
figuras (figuras/*.png) do artigo a partir de dados/leg57.

Uso (a partir da raiz do repositório ou desta pasta):
    python artigos/02-disciplina-intrapartidaria/analise.py              # tudo (~25 min em CPU)
    python artigos/02-disciplina-intrapartidaria/analise.py --rapido     # sem bootstrap/validação cruzada pesada
    python artigos/02-disciplina-intrapartidaria/analise.py --secoes descritivo disciplina

Não altera nada fora desta pasta. Reusa (importa) o estimador de pontos ideais de
embeddings_deputados.py (ajustar_irt), sem modificá-lo.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ))
import embeddings_deputados as ED  # noqa: E402

DADOS = RAIZ / "dados" / "leg57"
FIG = AQUI / "figuras"
TAB = AQUI / "tabelas"
AUX = AQUI / "dados_aux"
for p in (FIG, TAB, AUX):
    p.mkdir(exist_ok=True)

SEMENTE = 20231
R = {}                       # todos os números citados no artigo
MIN_VOTOS_PARTIDO = 3000     # partidos com pelo menos isto de votos no plenário entram nas tabelas
MIN_DEP_RICE = 3             # bancada mínima (votantes) para calcular o Rice numa votação
M_RICE = 10                  # tamanho de bancada padronizado (Rice padronizado por subamostragem)
LIMIAR_DISPUTA = 0.10        # votação disputada: minoria do plenário >= 10%

ORDEM_PARTIDOS = ["PSOL", "PT", "PCdoB", "PV", "PSB", "PDT", "REDE", "MDB", "PSD", "AVANTE",
                  "SOLIDARIEDADE", "PODE", "UNIÃO", "PP", "REPUBLICANOS", "PSDB", "CIDADANIA",
                  "PRD", "PATRIOTA", "PL", "NOVO"]


# =============================================================================== util
def num(chave, valor, nd=4):
    """Guarda um número do artigo em R (arredondado)."""
    if isinstance(valor, (np.floating, float)):
        valor = round(float(valor), nd)
    elif isinstance(valor, (np.integer,)):
        valor = int(valor)
    R[chave] = valor
    return valor


def pct(x, nd=1):
    return f"{100 * x:.{nd}f}".replace(".", ",")


def br(x, nd=2):
    if pd.isna(x):
        return "–"
    return f"{x:.{nd}f}".replace(".", ",")


def tabela_md(df, nome, legenda, fmt=None):
    """Salva a tabela em Markdown (tabelas/<nome>.md) com a legenda na primeira linha."""
    d = df.copy()
    fmt = fmt or {}
    for c, f in fmt.items():
        if c in d:
            d[c] = d[c].map(f)
    linhas = [f"**{legenda}**", "", "| " + " | ".join(map(str, d.columns)) + " |",
              "|" + "|".join(["---"] * len(d.columns)) + "|"]
    for _, r in d.iterrows():
        linhas.append("| " + " | ".join("" if pd.isna(x) else str(x) for x in r.values) + " |")
    (TAB / f"{nome}.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return d


def plt_setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 200, "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titlesize": 11, "axes.titleweight": "bold",
                         "axes.grid": True, "grid.alpha": 0.25, "font.family": "DejaVu Sans"})
    return plt


# ============================================================================ dados
def classificar_votacao(desc):
    d = str(desc).lower()
    if "requerimento de urgência" in d or ("urgência" in d and "requerimento" in d):
        return "Urgência"
    if d.startswith(("mantido o texto", "suprimido o texto", "mantida a expressão", "suprimida",
                     "mantidos os", "mantido o dispositivo", "rejeitados os dispositivos",
                     "mantida a")):
        return "Destaque (texto)"
    if "requerimento" in d:
        return "Requerimento procedimental"
    if "proposta de emenda à constituição" in d or "proposta de emenda a constituição" in d:
        return "PEC (mérito)"
    if ("emenda" in d or "subemenda" in d) and "substitutiva global" not in d:
        return "Emenda / destaque de emenda"
    return "Mérito (texto principal)"


def temas_proposicoes(ids):
    """Temas oficiais da Câmara para as proposições votadas. Usa proposicoes_temas.parquet e
    completa pela API (/proposicoes/{id}/temas), com cache em dados_aux/."""
    cache = AUX / "temas_proposicoes_votadas.csv"
    t = pd.read_parquet(DADOS / "proposicoes_temas.parquet", columns=["idProposicao", "tema"])
    t = t[t["idProposicao"].isin(ids)]
    if cache.exists():
        extra = pd.read_csv(cache, sep=";")
    else:
        import requests
        faltam = sorted(set(ids) - set(t["idProposicao"]))
        linhas = []
        print(f"  baixando temas de {len(faltam)} proposições pela API...", flush=True)
        for k, pid in enumerate(faltam):
            for tentativa in range(4):
                try:
                    r = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{pid}/temas",
                                     headers={"Accept": "application/json"}, timeout=30)
                    r.raise_for_status()
                    for d in r.json()["dados"]:
                        linhas.append((pid, d["tema"]))
                    break
                except Exception:
                    time.sleep(2 ** tentativa)
        extra = pd.DataFrame(linhas, columns=["idProposicao", "tema"])
        extra.to_csv(cache, sep=";", index=False)
    return pd.concat([t, extra]).drop_duplicates()


def carregar():
    v = pd.read_parquet(DADOS / "votos.parquet")
    vt = pd.read_parquet(DADOS / "votacoes.parquet")
    dep = pd.read_parquet(DADOS / "deputados.parquet")
    dep["id"] = dep["id"].astype(int)
    v["deputado_id"] = v["deputado_id"].astype(int)
    v["ano"] = v["data"].str[:4].astype(int)
    tipo = vt.set_index("idVotacao")["descricao"].map(classificar_votacao)
    v["tipo_votacao"] = v["idVotacao"].map(tipo)
    v["tipo_prop"] = v["proposicao_titulo"].str.split().str[0]
    v["partido"] = v["deputado_siglaPartido"].replace({"S.PART.": np.nan})
    return v, vt, dep


def amostra_disciplina(v, sem_inferidas=False):
    """Votos válidos (Sim/Não/Obstrução/Abstenção) com orientação diretiva da bancada.
    Exclui 'Artigo 17' (presidente da sessão) e votos sem registro."""
    d = v[v["voto"].isin(["Sim", "Não", "Obstrução", "Abstenção"])
          & v["orientacao_partido"].isin(["Sim", "Não", "Obstrução"])
          & v["partido"].notna()].copy()
    if sem_inferidas:
        d = d[d["orientacao_fonte"] != "bloco (inferido)"]
    d["seguiu"] = (d["voto"] == d["orientacao_partido"]).astype(float)
    # disciplina direcional: Não e Obstrução contam como a mesma direção (contra a matéria)
    dirv = d["voto"].map({"Sim": 1, "Não": 0, "Obstrução": 0, "Abstenção": -1})
    diro = d["orientacao_partido"].map({"Sim": 1, "Não": 0, "Obstrução": 0})
    d["seguiu_dir"] = (dirv == diro).astype(float)
    return d


# ======================================================================= descritivo
def descritivo(v, vt, dep):
    plen = v[v["siglaOrgao"] == "PLEN"]
    num("n_votos_total", len(v))
    num("n_votacoes_total", v["idVotacao"].nunique())
    num("n_votos_plen", len(plen))
    num("n_votacoes_plen", plen["idVotacao"].nunique())
    num("n_deputados_plen", plen["deputado_id"].nunique())
    num("data_primeira", plen["data"].min())
    num("data_ultima", plen["data"].max())
    num("media_votantes_por_votacao", plen.groupby("idVotacao").size().mean(), 1)
    for k, c in plen["voto"].value_counts(dropna=False).items():
        num(f"plen_voto_{k}", c)
    oc = plen["orientacao_partido"].fillna("vazia").value_counts(normalize=True)
    for k, c in oc.items():
        num(f"plen_orient_share_{k}", c)
    fc = plen["orientacao_fonte"].fillna("nenhuma").value_counts(normalize=True)
    for k, c in fc.items():
        num(f"plen_fonte_share_{k}", c)
    fc_all = v["orientacao_fonte"].fillna("nenhuma").value_counts(normalize=True)
    num("todos_fonte_share_inferido", fc_all.get("bloco (inferido)", 0))
    # votações por ano e tipo
    pv = plen.drop_duplicates("idVotacao")
    t = pd.crosstab(pv["tipo_votacao"], pv["ano"], margins=True, margins_name="Total")
    t.columns = [str(c) for c in t.columns]
    t = t.reset_index().rename(columns={"tipo_votacao": "Tipo de votação"})
    tabela_md(t, "tab1_votacoes_tipo_ano",
              "Tabela 1 – Votações nominais do Plenário por tipo e ano (57ª Legislatura, até 4/11/2026)")
    # votos com orientação vazia: sem orientação da bancada aplicável
    num("plen_share_orient_diretiva", plen["orientacao_partido"].isin(["Sim", "Não", "Obstrução"]).mean())
    # trocas de partido e suplentes
    f = pd.read_parquet(DADOS / "deputados_partidos.parquet")
    trocas = f.groupby("id").size() - 1
    num("n_deputados_com_troca", int((trocas > 0).sum()))
    num("n_deputados_total", len(dep))
    num("n_suplentes_ou_efetivados", int(dep["condicaoEleitoral"].isin(["Suplente", "Efetivado"]).sum()))


# ======================================================================= disciplina
def taxa(df, por, col="seguiu"):
    g = df.groupby(por)[col].agg(["mean", "size"])
    return g.rename(columns={"mean": "taxa", "size": "n"})


def principais_partidos(d):
    c = d["partido"].value_counts()
    ps = [p for p in ORDEM_PARTIDOS if c.get(p, 0) >= MIN_VOTOS_PARTIDO]
    return ps


def disciplina(v, sufixo="", sem_inferidas=False, salvar=True):
    plen = v[v["siglaOrgao"] == "PLEN"]
    d = amostra_disciplina(plen, sem_inferidas)
    ps = principais_partidos(d)
    s = sufixo
    num(f"disc_geral{s}", d["seguiu"].mean())
    num(f"disc_geral_dir{s}", d["seguiu_dir"].mean())
    num(f"disc_n{s}", len(d))
    num(f"disc_share_votos_orientados{s}", len(d) / plen["voto"].isin(["Sim", "Não", "Obstrução", "Abstenção"]).sum())

    tp = taxa(d, "partido").join(taxa(d, "partido", "seguiu_dir")[["taxa"]].rename(columns={"taxa": "taxa_dir"}))
    tp = tp.loc[ps]
    for p, r in tp.iterrows():
        num(f"disc_{p}{s}", r["taxa"])
        num(f"disc_dir_{p}{s}", r["taxa_dir"])
    if not salvar:
        return d, tp
    # por ano
    ta = d.pivot_table(index="partido", columns="ano", values="seguiu", aggfunc="mean").loc[ps]
    for a, x in taxa(d, "ano")["taxa"].items():
        num(f"disc_ano_{a}", x)
    # por fonte da orientação
    tf = taxa(plen.pipe(amostra_disciplina), "orientacao_fonte")
    for k, r in tf.iterrows():
        num(f"disc_fonte_{k}", r["taxa"])
        num(f"n_fonte_{k}", int(r["n"]))
    # por tipo de orientação
    to = taxa(d, "orientacao_partido")
    for k, r in to.iterrows():
        num(f"disc_orient_{k}", r["taxa"])
        num(f"disc_orient_dir_{k}", d.loc[d["orientacao_partido"] == k, "seguiu_dir"].mean())
        num(f"n_orient_{k}", int(r["n"]))
    # quem desobedece Obstrução vota o quê
    ob = d[d["orientacao_partido"] == "Obstrução"]["voto"].value_counts(normalize=True)
    for k, x in ob.items():
        num(f"obstrucao_voto_{k}", x)
    # concordância com o Governo? por tipo de votação e de proposição
    tt = taxa(d, "tipo_votacao")
    for k, r in tt.iterrows():
        num(f"disc_tipo_{k}", r["taxa"])
    tpr = taxa(d[d["tipo_prop"].isin(["PL", "PLP", "PEC", "MPV", "PDL"])], "tipo_prop")
    for k, r in tpr.iterrows():
        num(f"disc_prop_{k}", r["taxa"])

    tab = tp.copy()
    tab["taxa_2023"] = ta.get(2023)
    tab["taxa_2024"] = ta.get(2024)
    tab["taxa_2025"] = ta.get(2025)
    tab["taxa_2026"] = ta.get(2026)
    return d, tp, ta, tt, tpr, to


def tabela_disciplina(tp, ta, rice_p, rice_tab_extra):
    t = pd.DataFrame({"Partido": tp.index,
                      "Votos": tp["n"].map(lambda x: f"{x:,}".replace(",", ".")),
                      "Disciplina": tp["taxa"].map(pct),
                      "Disc. direcional": tp["taxa_dir"].map(pct)})
    for a in [2023, 2024, 2025, 2026]:
        t[str(a)] = [pct(ta.loc[p, a]) if a in ta and not pd.isna(ta.loc[p, a]) else "–" for p in tp.index]
    t["Rice (disputadas)"] = [br(rice_p.loc[p, "rice"], 3) if p in rice_p.index else "–" for p in tp.index]
    t["Rice padron. (m=10)"] = [br(rice_p.loc[p, "rice_pad"], 3) if p in rice_p.index else "–" for p in tp.index]
    t["Votações com maioria dividida"] = [pct(rice_tab_extra.loc[p], 1) if p in rice_tab_extra.index else "–"
                                         for p in tp.index]
    tabela_md(t, "tab2_disciplina_partidos",
              "Tabela 2 – Disciplina (voto igual à orientação da bancada) e coesão (Rice) por partido, Plenário")


# ============================================================================ Rice
def rice_esperado_sub(s, n, m):
    """E[Rice] numa subamostra sem reposição de tamanho m de uma bancada com s 'Sim' entre n.
    Rice = |2k - m| / m, k ~ Hipergeométrica(n, s, m)."""
    from scipy.stats import hypergeom
    k = np.arange(0, m + 1)
    pk = hypergeom(n, s, m).pmf(k)
    return float(np.sum(pk * np.abs(2 * k - m) / m))


def rice(v, sem_inferidas=False, sufixo=""):
    plen = v[(v["siglaOrgao"] == "PLEN") & v["voto"].isin(["Sim", "Não", "Obstrução"]) & v["partido"].notna()].copy()
    if sem_inferidas:
        plen = plen[plen["orientacao_fonte"] != "bloco (inferido)"]
    plen["s"] = (plen["voto"] == "Sim").astype(int)
    minoria = plen.groupby("idVotacao")["s"].mean()
    minoria = np.minimum(minoria, 1 - minoria)
    disputadas = minoria[minoria >= LIMIAR_DISPUTA].index
    num(f"n_votacoes_disputadas{sufixo}", len(disputadas))
    g = plen.groupby(["idVotacao", "partido"])["s"].agg(["sum", "size"]).reset_index()
    g = g[g["size"] >= MIN_DEP_RICE]
    g["rice"] = (2 * g["sum"] - g["size"]).abs() / g["size"]
    m = M_RICE
    cache = {}
    vals = []
    for s_, n_ in zip(g["sum"], g["size"]):
        if n_ < m:
            vals.append(np.nan)
            continue
        k = (s_, n_)
        if k not in cache:
            cache[k] = rice_esperado_sub(s_, n_, m)
        vals.append(cache[k])
    g["rice_pad"] = vals
    g["disputada"] = g["idVotacao"].isin(disputadas)
    g["dividida"] = g["rice"] < 0.5        # menos de 75% da bancada no mesmo lado
    gd = g[g["disputada"]]
    rp = gd.groupby("partido")[["rice", "rice_pad"]].mean()
    todas = g.groupby("partido")[["rice"]].mean().rename(columns={"rice": "rice_todas"})
    rp = rp.join(todas)
    div = gd.groupby("partido")["dividida"].mean()
    for p, r in rp.iterrows():
        num(f"rice_{p}{sufixo}", r["rice"])
        num(f"rice_pad_{p}{sufixo}", r["rice_pad"])
        num(f"rice_todas_{p}{sufixo}", r["rice_todas"])
    for p, x in div.items():
        num(f"rice_dividida_{p}{sufixo}", x)
    num(f"rice_media_disputadas{sufixo}", gd["rice"].mean())
    num(f"rice_media_todas{sufixo}", g["rice"].mean())
    return g, rp, div, disputadas


# ===================================================== governo x partido divergentes
def governo_vs_partido(v, sem_inferidas=False, sufixo=""):
    plen = v[(v["siglaOrgao"] == "PLEN") & v["voto"].isin(["Sim", "Não", "Obstrução", "Abstenção"])
             & v["partido"].notna()].copy()
    if sem_inferidas:
        plen = plen[plen["orientacao_fonte"] != "bloco (inferido)"]
    dirs = {"Sim": 1, "Não": 0, "Obstrução": 0}
    plen["op"] = plen["orientacao_partido"].map(dirs)
    plen["og"] = plen["orientacao_governo"].map(dirs)
    plen["vd"] = plen["voto"].map({"Sim": 1, "Não": 0, "Obstrução": 0, "Abstenção": -1})
    x = plen[plen["op"].notna() & plen["og"].notna() & (plen["op"] != plen["og"])].copy()
    x["segue_partido"] = (x["vd"] == x["op"]).astype(float)
    x["segue_governo"] = (x["vd"] == x["og"]).astype(float)
    num(f"div_n_votos{sufixo}", len(x))
    num(f"div_n_votacoes{sufixo}", x["idVotacao"].nunique())
    num(f"div_segue_partido{sufixo}", x["segue_partido"].mean())
    num(f"div_segue_governo{sufixo}", x["segue_governo"].mean())
    ps = principais_partidos(x.assign(partido=x["partido"])) if len(x) else []
    c = x["partido"].value_counts()
    ps = [p for p in ORDEM_PARTIDOS if c.get(p, 0) >= 300]
    t = x.groupby("partido").agg(n=("segue_partido", "size"), votacoes=("idVotacao", "nunique"),
                                 partido=("segue_partido", "mean"), governo=("segue_governo", "mean"))
    t = t.loc[ps]
    # participação de cada partido nas divergências: quantas votações em que o partido diverge do Governo
    for p, r in t.iterrows():
        num(f"div_{p}_segue_partido{sufixo}", r["partido"])
        num(f"div_{p}_n{sufixo}", int(r["n"]))
    # quando o partido está liberado: quanto segue o Governo
    lib = plen[(plen["orientacao_partido"] == "Liberado") & plen["og"].notna()]
    num(f"liberado_segue_governo{sufixo}", (lib["vd"] == lib["og"]).mean())
    num(f"liberado_n{sufixo}", len(lib))
    return x, t


# ===================================================================== deputados
def tabela_deputados(v, dep):
    """Taxa de defecção por deputado e covariáveis."""
    plen = v[v["siglaOrgao"] == "PLEN"]
    d = amostra_disciplina(plen)
    # partido principal = partido com mais votos no plenário
    pp = d.groupby(["deputado_id", "partido"]).size().reset_index(name="n").sort_values("n")
    pp = pp.drop_duplicates("deputado_id", keep="last").set_index("deputado_id")["partido"]
    g = d.groupby("deputado_id").agg(n=("seguiu", "size"), seguiu=("seguiu", "sum"),
                                     seguiu_dir=("seguiu_dir", "sum"))
    g["defeccao"] = 1 - g["seguiu"] / g["n"]
    g["partido"] = pp
    f = pd.read_parquet(DADOS / "deputados_partidos.parquet")
    g["n_trocas"] = (f.groupby("id").size() - 1).reindex(g.index).fillna(0)
    info = dep.set_index("id")
    g["suplente"] = info["condicaoEleitoral"].reindex(g.index).isin(["Suplente", "Efetivado"]).astype(int)
    g["uf"] = info["siglaUf"].reindex(g.index)
    g["mulher"] = (info["sexo"].reindex(g.index) == "F").astype(int)
    nasc = pd.to_datetime(info["dataNascimento"].reindex(g.index), errors="coerce")
    g["idade_2023"] = (pd.Timestamp("2023-02-01") - nasc).dt.days / 365.25
    # tamanho da bancada da UF (cadeiras) e se o deputado é da mesma região do líder... (não usado)
    tam_uf = dep[dep["condicaoEleitoral"] == "Titular"].groupby("siglaUf").size()
    g["cadeiras_uf"] = g["uf"].map(tam_uf)
    g["nome"] = info["nome"].reindex(g.index)
    return g, d


def modelo_defeccao(g, min_votos=50):
    """GLM binomial agregado por deputado (logit), com efeitos fixos de partido e erros-padrão
    robustos (sanduíche) — descritivo, não causal."""
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    x = g[(g["n"] >= min_votos) & g["partido"].notna()].copy()
    c = x["partido"].value_counts()
    x = x[x["partido"].isin(c[c >= 5].index)]
    x["defec"] = x["n"] - x["seguiu"]
    x["troca"] = (x["n_trocas"] > 0).astype(int)
    x["log_cadeiras_uf"] = np.log(x["cadeiras_uf"])
    x["idade10"] = x["idade_2023"] / 10
    form = "defec_frac ~ suplente + troca + log_cadeiras_uf + mulher + idade10 + C(partido)"
    x["defec_frac"] = x["defec"] / x["n"]
    m = smf.glm(form, data=x, family=sm.families.Binomial(), freq_weights=None,
                var_weights=x["n"]).fit(cov_type="HC1")
    num("glm_n_deputados", len(x))
    out = {}
    for k in ["suplente", "troca", "log_cadeiras_uf", "mulher", "idade10"]:
        out[k] = dict(coef=m.params[k], ep=m.bse[k], p=m.pvalues[k], or_=np.exp(m.params[k]))
        num(f"glm_{k}_or", np.exp(m.params[k]), 3)
        num(f"glm_{k}_p", m.pvalues[k], 4)
        num(f"glm_{k}_ic_lo", np.exp(m.params[k] - 1.96 * m.bse[k]), 3)
        num(f"glm_{k}_ic_hi", np.exp(m.params[k] + 1.96 * m.bse[k]), 3)
    # UF: teste conjunto (efeitos fixos de UF adicionados) — razão de verossimilhança via deviance
    m_uf = smf.glm(form + " + C(uf)", data=x, family=sm.families.Binomial(), var_weights=x["n"]).fit()
    m0 = smf.glm(form, data=x, family=sm.families.Binomial(), var_weights=x["n"]).fit()
    # sobredispersão: escala de Pearson para o teste F de UF
    escala = m_uf.pearson_chi2 / m_uf.df_resid
    gl = m0.df_resid - m_uf.df_resid
    F = ((m0.deviance - m_uf.deviance) / gl) / escala
    from scipy.stats import f as fdist
    num("glm_uf_F", F, 3)
    num("glm_uf_gl", int(gl))
    num("glm_uf_p", 1 - fdist.cdf(F, gl, m_uf.df_resid), 4)
    num("glm_sobredispersao", escala, 2)
    # partido explica quanto da variância da defecção entre deputados?
    from statsmodels.formula.api import ols
    num("r2_defeccao_partido", ols("defec_frac ~ C(partido)", data=x, weights=x["n"]).fit().rsquared, 3)
    return m, out, x


def antes_depois_troca(v, d):
    """Para quem trocou de partido: disciplina com o partido antigo vs. com o novo (intra-deputado)."""
    t = d.groupby(["deputado_id", "partido"]).agg(n=("seguiu", "size"), taxa=("seguiu", "mean"),
                                                  ini=("data", "min")).reset_index()
    t = t[t["n"] >= 30]
    multi = t.groupby("deputado_id").filter(lambda s: len(s) >= 2).sort_values(["deputado_id", "ini"])
    pares = multi.groupby("deputado_id").agg(antes=("taxa", "first"), depois=("taxa", "last"))
    num("troca_n_deputados_comparaveis", len(pares))
    if len(pares):
        num("troca_disc_antes", pares["antes"].mean())
        num("troca_disc_depois", pares["depois"].mean())
        from scipy.stats import wilcoxon
        num("troca_wilcoxon_p", wilcoxon(pares["depois"], pares["antes"]).pvalue, 4)
    return pares


# =========================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--secoes", nargs="+", default=["tudo"])
    args = ap.parse_args()
    t0 = time.time()
    v, vt, dep = carregar()
    descritivo(v, vt, dep)
    d, tp, ta, tt, tpr, to = disciplina(v)
    g, rp, div, disp = rice(v)
    tabela_disciplina(tp, ta, rp, div)
    x, tgov = governo_vs_partido(v)
    gdep, dd = tabela_deputados(v, dep)
    m, out, xm = modelo_defeccao(gdep)
    antes_depois_troca(v, dd)
    (AQUI / "resultados.json").write_text(json.dumps(R, indent=1, ensure_ascii=False))
    print(json.dumps(R, indent=0, ensure_ascii=False))
    print(f"tempo: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
