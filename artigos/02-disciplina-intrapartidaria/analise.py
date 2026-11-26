"""
Artigo 2 — Disciplina partidária, orientação das lideranças e variação intrapartidária
na 57ª Legislatura da Câmara dos Deputados (2023–2026).

Script reprodutível: gera todos os números (resultados.json), tabelas (tabelas/*.md) e
figuras (figuras/*.png) do artigo a partir de dados/leg57. O desenho segue o blueprint
metodológico em pipeline/stage1_blueprint.md.

Uso (da raiz do repositório):
    python artigos/02-disciplina-intrapartidaria/analise.py            # tudo (~11 min em 4 CPUs sem cache; ~2 min com cache)
    python artigos/02-disciplina-intrapartidaria/analise.py --rapido   # menos réplicas de bootstrap
    python artigos/02-disciplina-intrapartidaria/analise.py --secoes descritivo disciplina rice

Ajustes de pontos ideais ficam em cache (dados_aux/cache/); apague a pasta para refazer do zero.
Não altera nada fora desta pasta. Importa (sem modificar) o estimador ajustar_irt de
embeddings_deputados.py.
"""
import argparse
import json
import os
import pickle
import re
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")   # paralelismo por processos, não por threads
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ))
import embeddings_deputados as ED  # noqa: E402

DADOS = RAIZ / "dados" / "leg57"
FIG = AQUI / "figuras"
TAB = AQUI / "tabelas"
AUX = AQUI / "dados_aux"
CACHE = AUX / "cache"
for p in (FIG, TAB, AUX, CACHE):
    p.mkdir(exist_ok=True)

SEMENTE = 20231
R = {}                       # todos os números citados no artigo
MIN_VOTOS_PARTIDO = 3000     # partidos com pelo menos isto de votos no Plenário entram nas tabelas
MIN_DEP_RICE = 3             # bancada mínima (votantes) para calcular o Rice numa votação
LIMIAR_DISPUTA = 0.10        # votação disputada: minoria do plenário >= 10%
MIN_COLEGAS_U = 5            # unidade (U): pelo menos 5 colegas de partido votando
N_BOOT = 1000                # bootstrap de votações para taxas
ARGS = None

ORDEM_PARTIDOS = ["PSOL", "PT", "PCdoB", "PV", "PSB", "PDT", "REDE", "MDB", "PSD", "AVANTE",
                  "SOLIDARIEDADE", "PODE", "UNIÃO", "PP", "REPUBLICANOS", "PSDB", "CIDADANIA",
                  "PRD", "PATRIOTA", "PL", "NOVO"]
OPOSICAO = ["PL", "NOVO"]    # oposição permanente ao Governo Lula (tratada à parte em P5)
# partidos com ministério em ao menos parte do governo Lula 3 (ver pipeline/stage4_bibliografia.md)
BASE_MINISTERIAL = ["PT", "PCdoB", "PSB", "PDT", "PSOL", "REDE", "MDB", "PSD", "UNIÃO", "PP", "REPUBLICANOS"]
FEDERACOES = {"PT": "Fdr PT-PCdoB-PV", "PCdoB": "Fdr PT-PCdoB-PV", "PV": "Fdr PT-PCdoB-PV",
              "PSOL": "Fdr PSOL-REDE", "REDE": "Fdr PSOL-REDE", "PSDB": "Fdr PSDB-CIDADANIA",
              "CIDADANIA": "Fdr PSDB-CIDADANIA"}
FUSOES = {("PSC", "PODE"), ("PATRIOTA", "PRD"), ("PTB", "PRD"), ("PROS", "SOLIDARIEDADE")}
# cadeiras legais por UF (LC 78/1993; distribuição vigente na eleição de 2022)
CADEIRAS_UF = {"SP": 70, "MG": 53, "RJ": 46, "BA": 39, "RS": 31, "PR": 30, "PE": 25, "CE": 22,
               "MA": 18, "GO": 17, "PA": 17, "SC": 16, "PB": 12, "ES": 10, "PI": 10, "AL": 9,
               "AM": 8, "AP": 8, "AC": 8, "DF": 8, "MS": 8, "MT": 8, "RN": 8, "RO": 8, "RR": 8,
               "SE": 8, "TO": 8}
DIR = {"Sim": 1.0, "Não": 0.0, "Obstrução": 0.0}


# =============================================================================== util
def num(chave, valor, nd=6):
    """Guarda um número do artigo em R (arredondado; NaN vira None)."""
    if isinstance(valor, (np.floating, float)):
        valor = None if not np.isfinite(valor) else round(float(valor), nd)
    elif isinstance(valor, (np.integer,)):
        valor = int(valor)
    elif isinstance(valor, (np.bool_,)):
        valor = bool(valor)
    R[chave] = valor
    return valor


def pct(x, nd=1):
    return "–" if x is None or pd.isna(x) else f"{100 * x:.{nd}f}".replace(".", ",").replace("-", "−")


def br(x, nd=2):
    """Decimal com vírgula e sinal de menos tipográfico."""
    return "–" if x is None or pd.isna(x) else f"{x:.{nd}f}".replace(".", ",").replace("-", "−")


def milhar(x):
    return f"{int(x):,}".replace(",", ".")


def tabela_md(df, nome, legenda, nota=None):
    """Salva a tabela em Markdown (tabelas/<nome>.md) com a legenda na primeira linha."""
    linhas = [f"**{legenda}**", "", "| " + " | ".join(map(str, df.columns)) + " |",
              "|" + "|".join(["---"] * len(df.columns)) + "|"]
    for _, r in df.iterrows():
        linhas.append("| " + " | ".join("" if (not isinstance(x, str) and pd.isna(x)) else str(x)
                                        for x in r.values) + " |")
    if nota:
        linhas += ["", f"*{nota}*"]
    (TAB / f"{nome}.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return df


def plt_setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 200, "font.size": 9.5,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
                         "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
                         "font.family": "DejaVu Sans", "legend.frameon": False})
    return plt


# paleta categórica validada (skill dataviz, slots 1–3 na ordem fixa) + neutros de texto
COR = {"s1": "#2a78d6", "s2": "#eb6834", "s3": "#1baf7a", "cinza": "#8a8f98",
       "texto": "#0b0b0b", "texto2": "#52514e", "grade": "#d9d8d4"}


DIGITAL = ""   # impressão digital dos dados do IRT (definida em prep_irt), entra no nome do cache


def em_cache(nome, func, *a, **k):
    """Guarda em dados_aux/cache/<nome>_<digital>.pkl o resultado de func (ajustes de IRT). A
    impressão digital depende do nº de votos, votações, períodos e da soma de y; mudanças nos
    hiperparâmetros exigem apagar a pasta (os nomes já os incluem quando variam)."""
    arq = CACHE / f"{nome}_{DIGITAL}.pkl"
    if arq.exists():
        return pickle.loads(arq.read_bytes())
    res = func(*a, **k)
    arq.write_bytes(pickle.dumps(res))
    return res


def boot_razao(num_m, den_m, B=N_BOOT, seed=SEMENTE):
    """IC 95% por bootstrap de votações da razão sum(num)/sum(den), por coluna.
    num_m, den_m: matrizes votação × grupo."""
    rng = np.random.default_rng(seed)
    n = num_m.shape[0]
    W = np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(B)])
    est = (W @ num_m) / np.where((W @ den_m) == 0, np.nan, W @ den_m)
    return np.nanpercentile(est, 2.5, axis=0), np.nanpercentile(est, 97.5, axis=0)


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


def validar_classificador():
    """Acurácia da regra de tipo de votação contra a codificação manual de uma amostra estratificada
    (20 por classe prevista; dados_aux/validacao_tipo_votacao.csv)."""
    arq = AUX / "validacao_tipo_votacao.csv"
    if not arq.exists():
        return
    t = pd.read_csv(arq, sep=";")
    t = t[t["tipo_manual"] != "indeterminado"]
    num("classif_n", len(t)); num("classif_acuracia", (t["tipo_regra"] == t["tipo_manual"]).mean())
    for c, g in t.groupby("tipo_regra"):
        num(f"classif_precisao_{c}", (g["tipo_regra"] == g["tipo_manual"]).mean())


def bloco_heterogeneo(nome):
    """Bloco que reúne a oposição (PL) e a federação do PT: bloco de Mesa, não de coordenação de voto."""
    s = str(nome)
    return s.startswith("Bl") and bool(re.search(r"Pl", s)) and bool(re.search(r"FdrP[Tt]", s))


def temas_proposicoes(ids):
    """Temas oficiais da Câmara para as proposições votadas (multi-rótulo). Usa
    proposicoes_temas.parquet e completa pela API (/proposicoes/{id}/temas), com cache
    versionado em dados_aux/ (o script roda sem rede se o cache existir)."""
    cache = AUX / "temas_proposicoes_votadas.csv"
    t = pd.read_parquet(DADOS / "proposicoes_temas.parquet", columns=["idProposicao", "tema"])
    t["idProposicao"] = pd.to_numeric(t["idProposicao"], errors="coerce")
    t = t[t["idProposicao"].isin(ids)]
    if cache.exists():
        extra = pd.read_csv(cache, sep=";")
    else:
        import requests
        faltam = sorted(set(ids) - set(t["idProposicao"]))
        linhas, falhas = [], []
        print(f"  baixando temas de {len(faltam)} proposições pela API...", flush=True)
        for pid in faltam:
            for tentativa in range(4):
                try:
                    r = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{pid}/temas",
                                     headers={"Accept": "application/json"}, timeout=30)
                    r.raise_for_status()
                    ds = r.json()["dados"]
                    linhas += [(pid, d["tema"]) for d in ds] or [(pid, "(sem tema)")]
                    break
                except Exception:
                    time.sleep(2 ** tentativa)
            else:
                falhas.append(pid)
        extra = pd.DataFrame(linhas, columns=["idProposicao", "tema"])
        extra.to_csv(cache, sep=";", index=False)
        print(f"  falhas: {len(falhas)}")
    return pd.concat([t, extra]).drop_duplicates()


def periodos_exercicio(dep):
    """Períodos em exercício de cada deputado (de deputados_historico): lista de
    (id, inicio, fim, condicao) em que situacao == 'Exercício'."""
    h = pd.read_parquet(DADOS / "deputados_historico.parquet")
    h = h[h["dataHora"].notna() & (h["dataHora"] != "")].copy()
    h["t"] = pd.to_datetime(h["dataHora"], errors="coerce")
    h = h.dropna(subset=["t"]).sort_values(["id", "t"])
    out = []
    for i, s in h.groupby("id"):
        ini, cond = None, None
        for _, r in s.iterrows():
            em = r["situacao"] == "Exercício"
            if em and ini is None:
                ini, cond = r["t"], r["condicaoEleitoral"]
            elif em and ini is not None and r["condicaoEleitoral"] != cond:
                out.append((int(i), ini, r["t"], cond))
                ini, cond = r["t"], r["condicaoEleitoral"]
            elif (not em) and ini is not None and pd.notna(r["situacao"]):
                out.append((int(i), ini, r["t"], cond))
                ini, cond = None, None
        if ini is not None:
            out.append((int(i), ini, pd.Timestamp("2027-02-01"), cond))
    return pd.DataFrame(out, columns=["deputado_id", "inicio", "fim", "condicao"])


def motivo_suplencia(dep):
    """Para cada posse de suplente, o motivo da saída de um titular da mesma UF em +-10 dias
    (aproximação: a Câmara não liga suplente a titular nos Dados Abertos)."""
    h = pd.read_parquet(DADOS / "deputados_historico.parquet")
    h["t"] = pd.to_datetime(h["dataHora"], errors="coerce")
    h = h.dropna(subset=["t"])
    saidas = h[h["descricaoStatus"].str.startswith("Saída", na=False)].copy()
    saidas["motivo"] = saidas["descricaoStatus"].str.split(" - ").str[-1].str.strip()
    posses = h[h["descricaoStatus"].str.contains("Posse de Suplente|Reassunção", na=False)
               & (h["condicaoEleitoral"] == "Suplente")]
    out = []
    for _, r in posses.iterrows():
        c = saidas[(saidas["siglaUf"] == r["siglaUf"]) & (saidas["id"] != r["id"])
                   & ((saidas["t"] - r["t"]).abs() <= pd.Timedelta(days=10))]
        if len(c):
            c = c.iloc[(c["t"] - r["t"]).abs().argsort()[:1]]
            out.append((int(r["id"]), r["t"], c["motivo"].iloc[0]))
        else:
            out.append((int(r["id"]), r["t"], "não identificado"))
    return pd.DataFrame(out, columns=["deputado_id", "t", "motivo"])


def trocas_partido():
    """Transições de partido com tipo (individual x fusão/incorporação) e data."""
    f = pd.read_parquet(DADOS / "deputados_partidos.parquet").sort_values(["id", "dataInicio"])
    f["origem"] = f.groupby("id")["siglaPartido"].shift()
    t = f[f["origem"].notna()].copy()
    t["fusao"] = [(o, d) in FUSOES for o, d in zip(t["origem"], t["siglaPartido"])]
    t["data"] = pd.to_datetime(t["dataInicio"])
    t = t.rename(columns={"id": "deputado_id", "siglaPartido": "destino"})
    return t[["deputado_id", "origem", "destino", "data", "fusao"]]


def carregar():
    v = pd.read_parquet(DADOS / "votos.parquet")
    vt = pd.read_parquet(DADOS / "votacoes.parquet")
    dep = pd.read_parquet(DADOS / "deputados.parquet")
    dep["id"] = dep["id"].astype(int)
    v["deputado_id"] = v["deputado_id"].astype(int)
    v["dt"] = pd.to_datetime(v["data"])
    v["ano"] = v["dt"].dt.year
    v["semestre"] = v["ano"].astype(str) + "S" + np.where(v["dt"].dt.month <= 6, "1", "2")
    tipo = vt.set_index("idVotacao")["descricao"].map(classificar_votacao)
    v["tipo_votacao"] = v["idVotacao"].map(tipo)
    v["tipo_prop"] = v["proposicao_titulo"].str.split().str[0]
    v["partido"] = v["deputado_siglaPartido"].replace({"S.PART.": np.nan})
    # regras de dados: fora "Artigo 17" (presidente da sessão), voto nulo e sem partido
    num("n_artigo17", int((v["voto"] == "Artigo 17").sum()))
    v = v[v["voto"].isin(["Sim", "Não", "Obstrução", "Abstenção"]) & v["partido"].notna()].copy()
    # camadas da fonte da orientação
    het = v["orientacao_bancada"].map(bloco_heterogeneo).fillna(False)
    v["camada"] = np.select(
        [v["orientacao_fonte"].isin(["partido", "federacao"]), het,
         v["orientacao_fonte"] == "bloco", v["orientacao_fonte"] == "bloco (inferido)"],
        ["própria", "bloco heterogêneo", "bloco", "bloco inferido"], "nenhuma")
    v["diretiva"] = v["orientacao_partido"].isin(["Sim", "Não", "Obstrução"])
    # direção do voto e da orientação (Não = Obstrução = contra a matéria; Abstenção = desvio brando)
    v["vd"] = v["voto"].map({"Sim": 1.0, "Não": 0.0, "Obstrução": 0.0, "Abstenção": np.nan})
    v["od"] = v["orientacao_partido"].map(DIR)
    v["gd"] = v["orientacao_governo"].map(DIR)
    return v, vt, dep


def plenario(v):
    return v[v["siglaOrgao"] == "PLEN"].copy()


def amostra_D(p, camadas=("própria", "bloco", "bloco inferido"), estrita=False, sem_abst=False):
    """Votos com orientação diretiva aplicável (camadas escolhidas; bloco heterogêneo nunca).
    seguiu = direção do voto == direção da orientação (direcional; Abstenção = desvio).
    estrita: voto literalmente igual à orientação (Obstrução != Não)."""
    d = p[p["diretiva"] & p["camada"].isin(camadas)].copy()
    if sem_abst:
        d = d[d["voto"] != "Abstenção"]
    if estrita:
        d["seguiu"] = (d["voto"] == d["orientacao_partido"]).astype(float)
    else:
        d["seguiu"] = (d["vd"] == d["od"]).astype(float)
    return d


def amostra_U(p):
    """Unidade: voto na direção da maioria dos DEMAIS colegas de partido presentes na votação
    (leave-one-out, >= MIN_COLEGAS_U colegas com Sim/Não/Obstrução; empates fora)."""
    p = p.copy()
    p["s"] = (p["vd"] == 1).astype(int)
    p["n_"] = p["vd"].notna().astype(int)
    g = p.groupby(["idVotacao", "partido"])[["s", "n_"]].transform("sum")
    s_out = g["s"] - p["s"]
    n_out = g["n_"] - p["n_"]
    maj = np.where(2 * s_out > n_out, 1.0, np.where(2 * s_out < n_out, 0.0, np.nan))
    p["maj_colegas"] = maj
    p["n_colegas"] = n_out
    u = p[(n_out >= MIN_COLEGAS_U) & ~np.isnan(maj)].copy()
    u["unido"] = (u["vd"] == u["maj_colegas"]).astype(float)
    return u


def principais_partidos(d):
    c = d["partido"].value_counts()
    return [p for p in ORDEM_PARTIDOS if c.get(p, 0) >= MIN_VOTOS_PARTIDO]


# ======================================================================= descritivo
def descritivo(v, vt, dep):
    p = plenario(v)
    num("n_votos_total", len(v))
    num("n_votacoes_total", v["idVotacao"].nunique())
    num("n_votos_plen", len(p))
    num("n_votacoes_plen", p["idVotacao"].nunique())
    pv_all = vt[vt["siglaOrgao"] == "PLEN"]
    num("n_votacoes_plen_todas", len(pv_all))
    num("share_plen_nominais", pv_all["tem_votos_nominais"].mean())
    num("n_deputados_plen", p["deputado_id"].nunique())
    num("data_primeira", p["data"].min())
    num("data_ultima", p["data"].max())
    num("media_votantes_por_votacao", p.groupby("idVotacao").size().mean(), 1)
    for k, c in p["voto"].value_counts().items():
        num(f"plen_voto_{k}", c)
    for k, c in p["orientacao_partido"].fillna("vazia").replace("", "vazia").value_counts(normalize=True).items():
        num(f"plen_orient_share_{k}", c)
    for k, c in p["camada"].value_counts(normalize=True).items():
        num(f"plen_camada_share_{k}", c)
    num("todos_fonte_share_inferido", (v["orientacao_fonte"] == "bloco (inferido)").mean())
    # orientação vazia por ano (cobertura)
    vaz = p.assign(vz=~p["orientacao_partido"].isin(["Sim", "Não", "Obstrução", "Liberado"]))
    for a, x in vaz.groupby("ano")["vz"].mean().items():
        num(f"orient_vazia_{a}", x)
    # megabloco
    mb = p[p["camada"] == "bloco heterogêneo"]
    num("megabloco_n_votos", len(mb))
    num("megabloco_n_votacoes", mb["idVotacao"].nunique())
    num("megabloco_n_votacoes_orientadas", mb.loc[mb["diretiva"], "idVotacao"].nunique())
    num("megabloco_data_ini", mb["data"].min())
    num("megabloco_data_fim", mb["data"].max())
    pt = mb[mb["partido"] == "PT"]
    num("megabloco_PT_votos", len(pt))
    num("megabloco_PT_diretivos", int(pt["diretiva"].sum()))
    num("megabloco_PT_seguiu", (pt.loc[pt["diretiva"], "vd"] == pt.loc[pt["diretiva"], "od"]).mean())
    # tabela 1: votações por tipo e ano
    pv = p.drop_duplicates("idVotacao")
    t = pd.crosstab(pv["tipo_votacao"], pv["ano"], margins=True, margins_name="Total")
    t.columns = [str(c) for c in t.columns]
    t = t.reset_index().rename(columns={"tipo_votacao": "Tipo de votação"})
    tabela_md(t, "tab1_votacoes_tipo_ano",
              f"Tabela 1 – Votações nominais do Plenário por tipo e ano (57ª Legislatura, "
              f"{pd.Timestamp(R['data_primeira']):%d/%m/%Y} a {pd.Timestamp(R['data_ultima']):%d/%m/%Y})",
              nota="Tipo atribuído por regras sobre o texto de votacoes.descricao (ver Método).")
    # trocas, fusões, suplentes
    tr = trocas_partido()
    num("n_transicoes", len(tr))
    num("n_transicoes_fusao", int(tr["fusao"].sum()))
    ind = tr[~tr["fusao"]]
    num("n_transicoes_individuais", len(ind))
    num("n_deputados_troca_individual", ind["deputado_id"].nunique())
    num("n_transicoes_janela2026", int(((ind["data"] >= "2026-03-01") & (ind["data"] < "2026-06-01")).sum()))
    num("n_deputados_total", len(dep))
    num("n_suplentes_ou_efetivados", int(dep["condicaoEleitoral"].isin(["Suplente", "Efetivado"]).sum()))
    n_post = p.loc[p["dt"] >= "2026-04-04", "idVotacao"].nunique()
    num("n_votacoes_pos_janela", n_post)


# ======================================================================= disciplina
def taxa_por(d, por, col):
    g = d.groupby(por)[col].agg(["mean", "size"])
    return g.rename(columns={"mean": "taxa", "size": "n"})


def ic_partidos(d, col, partidos, seed=SEMENTE):
    """IC por bootstrap de votações para a taxa de cada partido."""
    a = d[d["partido"].isin(partidos)]
    nm = a.pivot_table(index="idVotacao", columns="partido", values=col, aggfunc="sum", fill_value=0)
    dn = a.pivot_table(index="idVotacao", columns="partido", values=col, aggfunc="size", fill_value=0)
    nm, dn = nm[partidos], dn[partidos]
    lo, hi = boot_razao(nm.to_numpy(float), dn.to_numpy(float), seed=seed)
    return pd.DataFrame({"lo": lo, "hi": hi}, index=partidos)


def boot_duas_vias(d, col, partidos, B=500, seed=SEMENTE + 3):
    """IC 95% da taxa de cada partido por bootstrap em duas vias: pesos multinomiais
    independentes para votações e para deputados, aplicados ao produto (pigeonhole bootstrap)."""
    from scipy import sparse
    rng = np.random.default_rng(seed)
    jv, nv = pd.factorize(d["idVotacao"]); jd, ndp = pd.factorize(d["deputado_id"])
    Wv = np.stack([np.bincount(rng.integers(0, len(nv), len(nv)), minlength=len(nv)) for _ in range(B)]).astype(float)
    Wd = np.stack([np.bincount(rng.integers(0, len(ndp), len(ndp)), minlength=len(ndp)) for _ in range(B)]).astype(float)
    lo, hi = {}, {}
    for q in partidos:
        m = (d["partido"] == q).to_numpy()
        Nm = sparse.csr_matrix((d[col].to_numpy(float)[m], (jv[m], jd[m])), shape=(len(nv), len(ndp)))
        Dn = sparse.csr_matrix((np.ones(m.sum()), (jv[m], jd[m])), shape=(len(nv), len(ndp)))
        num_ = np.einsum("bj,bj->b", (Nm.T @ Wv.T).T, Wd)
        den_ = np.einsum("bj,bj->b", (Dn.T @ Wv.T).T, Wd)
        est = num_ / np.where(den_ == 0, np.nan, den_)
        lo[q], hi[q] = np.nanpercentile(est, 2.5), np.nanpercentile(est, 97.5)
    return pd.Series(lo), pd.Series(hi)


def disciplina(v):
    p = plenario(v)
    d = amostra_D(p)
    u = amostra_U(p)
    ps = principais_partidos(d)
    num("disc_geral", d["seguiu"].mean())
    num("disc_n", len(d))
    num("disc_geral_estrita", amostra_D(p, estrita=True)["seguiu"].mean())
    num("disc_geral_sem_abst", amostra_D(p, sem_abst=True)["seguiu"].mean())
    num("disc_share_abst_nos_desvios", (d.loc[d["seguiu"] == 0, "voto"] == "Abstenção").mean())
    num("cobertura_D", len(d) / len(p))
    num("unidade_geral", u["unido"].mean())
    num("unidade_n", len(u))
    num("cobertura_U", len(u) / len(p))
    lo, hi = boot_razao(d.groupby("idVotacao")["seguiu"].sum().to_numpy()[:, None].astype(float),
                        d.groupby("idVotacao").size().to_numpy()[:, None].astype(float))
    num("disc_geral_lo", lo[0]); num("disc_geral_hi", hi[0])

    # por camada
    for k, r in taxa_por(amostra_D(p, camadas=("própria", "bloco", "bloco inferido", "bloco heterogêneo")),
                         "camada", "seguiu").iterrows():
        num(f"disc_camada_{k}", r["taxa"]); num(f"n_camada_{k}", int(r["n"]))
    # por partido: D (todas camadas não heterogêneas), D-própria, U, cobertura
    tD = taxa_por(d, "partido", "seguiu").loc[ps]
    dp = amostra_D(p, camadas=("própria",))
    tDp = taxa_por(dp, "partido", "seguiu").reindex(ps)
    tU = taxa_por(u, "partido", "unido").reindex(ps)
    psU = [x for x in ps if x in set(u["partido"])]
    nval = p.groupby("partido").size()
    icD = ic_partidos(d, "seguiu", ps)
    icU = ic_partidos(u, "unido", psU, seed=SEMENTE + 1).reindex(ps)
    camada_dom = p.groupby("partido")["camada"].agg(lambda s: s.value_counts().index[0])
    share_propria = p.assign(pr=p["camada"] == "própria").groupby("partido")["pr"].mean()
    tab = pd.DataFrame({"D": tD["taxa"], "D_lo": icD["lo"], "D_hi": icD["hi"], "nD": tD["n"],
                        "cobD": tD["n"] / nval.loc[ps], "Dp": tDp["taxa"], "nDp": tDp["n"],
                        "vDp": dp.groupby("partido")["idVotacao"].nunique().reindex(ps),
                        "U": tU["taxa"], "U_lo": icU["lo"], "U_hi": icU["hi"],
                        "cobU": tU["n"] / nval.loc[ps], "share_propria": share_propria.loc[ps]})
    for pt_, r in tab.iterrows():
        for c in ["D", "D_lo", "D_hi", "cobD", "Dp", "U", "U_lo", "U_hi", "cobU", "share_propria"]:
            num(f"{c}_{pt_}", r[c])
    # unidade com a federação como grupo (PT-PCdoB-PV, PSOL-REDE, PSDB-CIDADANIA)
    uf_ = amostra_U(p.assign(partido=p["partido"].map(FEDERACOES).fillna(p["partido"])))
    for fd_ in sorted(set(FEDERACOES.values())):
        num(f"U_fed_{fd_}", uf_.loc[uf_["partido"] == fd_, "unido"].mean())
    # IC em duas vias (bootstrap de votações e de deputados, Cameron, Gelbach e Miller 2011)
    for col_, df_, rot_ in [("seguiu", d, "D"), ("unido", u, "U")]:
        lo2, hi2 = boot_duas_vias(df_, col_, [x_ for x_ in ps if x_ in set(df_["partido"])])
        for q in lo2.index:
            num(f"{rot_}_lo2_{q}", lo2[q]); num(f"{rot_}_hi2_{q}", hi2[q])
            tab.loc[q, f"{rot_}_lo2"] = lo2[q]; tab.loc[q, f"{rot_}_hi2"] = hi2[q]
    # por ano / semestre, com cobertura (D e U)
    for a in sorted(p["ano"].unique()):
        num(f"disc_ano_{a}", d.loc[d["ano"] == a, "seguiu"].mean())
        num(f"cobD_ano_{a}", (d["ano"] == a).sum() / (p["ano"] == a).sum())
        num(f"unid_ano_{a}", u.loc[u["ano"] == a, "unido"].mean())
    # D por ano com a composição partidária fixa (pesos = votos de cada partido em D no total)
    pa = d.groupby(["ano", "partido"])["seguiu"].mean().unstack()
    w = d["partido"].value_counts(normalize=True)
    for a in pa.index:
        r = pa.loc[a].dropna()
        num(f"disc_ano_aj_{a}", float((r * w.reindex(r.index)).sum() / w.reindex(r.index).sum()))
    ua = u.groupby("ano")["unido"].mean()
    us = u.groupby("semestre")["unido"].mean()
    num("unid_amplitude_anos", ua.max() - ua.min()); num("unid_amplitude_semestres", us.max() - us.min())
    sem = pd.DataFrame({"D": d.groupby("semestre")["seguiu"].mean(),
                        "cobD": d.groupby("semestre").size() / p.groupby("semestre").size(),
                        "U": u.groupby("semestre")["unido"].mean(),
                        "Dp": dp.groupby("semestre")["seguiu"].mean()})
    taD = d.pivot_table(index="partido", columns="ano", values="seguiu", aggfunc="mean").reindex(ps)
    taU = u.pivot_table(index="partido", columns="ano", values="unido", aggfunc="mean").reindex(ps)
    for q in ["PL", "PT", "PSOL", "UNIÃO", "PSD", "MDB", "PP", "REPUBLICANOS"]:
        if q in taU.index:
            outros = u[(u["partido"] == q) & (u["ano"] != 2025)]["unido"].mean()
            num(f"U_2025_{q}", taU.loc[q, 2025]); num(f"U_outros_{q}", outros)
            num(f"U_queda2025_{q}", outros - taU.loc[q, 2025])
    # por tipo de orientação
    for k, r in taxa_por(d, "orientacao_partido", "seguiu").iterrows():
        num(f"disc_orient_{k}", r["taxa"]); num(f"n_orient_{k}", int(r["n"]))
    de = amostra_D(p, estrita=True)
    num("disc_orient_estrita_Obstrução", de.loc[de["orientacao_partido"] == "Obstrução", "seguiu"].mean())
    for k, x in d.loc[d["orientacao_partido"] == "Obstrução", "voto"].value_counts(normalize=True).items():
        num(f"obstrucao_voto_{k}", x)
    # Liberado: o partido racha quando libera? Unidade e Rice nas liberadas vs. orientadas
    u_lib = u[u["orientacao_partido"] == "Liberado"]
    u_ori = u[u["diretiva"]]
    num("unid_liberado", u_lib["unido"].mean()); num("n_unid_liberado", len(u_lib))
    num("unid_orientado", u_ori["unido"].mean())
    # unidade dentro dos mesmos partidos: diferença média por partido (ponderada)
    dif = (u_ori.groupby("partido")["unido"].mean() - u_lib.groupby("partido")["unido"].mean()).dropna()
    num("unid_lib_vs_ori_partidos_menor", int((dif > 0).sum())); num("unid_lib_vs_ori_partidos_total", len(dif))
    return dict(p=p, d=d, u=u, ps=ps, tab=tab, sem=sem, taD=taD, taU=taU)


def disciplina_recortes(v, base):
    """D e U por tipo de votação, tipo de proposição e tema: médias brutas (IC bootstrap)
    e diferenças ajustadas por partido×ano (MPL com efeitos fixos, EP agrupado por votação)."""
    p, d, u = base["p"], base["d"], base["u"]
    linhas = []
    for nome, col, cats in [("Tipo de votação", "tipo_votacao", None),
                            ("Tipo de proposição", "tipo_prop", ["PEC", "PLP", "PL", "MPV", "PDL"])]:
        dd = d if cats is None else d[d[col].isin(cats)]
        uu = u if cats is None else u[u[col].isin(cats)]
        catl = sorted(dd[col].dropna().unique())
        # ajustado: efeito do recorte com FE partido×ano (ref = primeira categoria)
        adjD = efeitos_categoria(dd, col, "seguiu")
        adjU = efeitos_categoria(uu, col, "unido")
        for c in catl:
            a = dd[dd[col] == c]
            b = uu[uu[col] == c]
            linhas.append(dict(recorte=nome, categoria=c, votacoes=a["idVotacao"].nunique(),
                               D=a["seguiu"].mean(), U=b["unido"].mean(),
                               D_aj=adjD.get(c, np.nan), U_aj=adjU.get(c, np.nan)))
            num(f"rec_D_{col}_{c}", a["seguiu"].mean()); num(f"rec_U_{col}_{c}", b["unido"].mean())
            num(f"rec_Daj_{col}_{c}", adjD.get(c, np.nan)); num(f"rec_Uaj_{col}_{c}", adjU.get(c, np.nan))
    t = pd.DataFrame(linhas)
    return t


def efeitos_categoria(d, col, y):
    """Média ajustada por categoria: MPL y ~ C(col) + FE partido×ano; devolve a média prevista
    de cada categoria com a composição partido×ano da amostra toda."""
    x = d[[col, y, "partido", "ano"]].dropna()
    if x[col].nunique() < 2:
        return {}
    pa = x["partido"] + "|" + x["ano"].astype(str)
    D = pd.get_dummies(x[col], dtype=float)
    yy = x[y].to_numpy(float)
    # demean por partido×ano (FE) e regressão sem intercepto nas dummies-centradas
    gm = lambda a: a - pd.DataFrame(a).groupby(pa.to_numpy()).transform("mean").to_numpy()
    Dc = gm(D.to_numpy())
    yc = gm(yy[:, None])[:, 0]
    beta = np.linalg.lstsq(Dc[:, 1:], yc, rcond=None)[0]
    efe = np.r_[0, beta]
    base = yy.mean() - D.to_numpy().mean(0) @ efe
    return {c: base + e for c, e in zip(D.columns, efe)}


def disciplina_temas(v, base):
    p, d, u = base["p"], base["d"], base["u"]
    ids = p["proposicao_id"].dropna().astype(str).str.split(",").explode().str.strip().astype(int).unique()
    t = temas_proposicoes(ids)
    t = t[t["tema"] != "(sem tema)"]
    num("temas_n_proposicoes_votadas", len(ids))
    num("temas_cobertura", t["idProposicao"].nunique() / len(ids))
    # votação -> temas (peso 1/k) via a 1ª proposição afetada
    pv = p.drop_duplicates("idVotacao")[["idVotacao", "proposicao_id"]].dropna()
    pv["pid"] = pv["proposicao_id"].astype(str).str.split(",").str[0].astype(int)
    vt = pv.merge(t, left_on="pid", right_on="idProposicao")
    vt["peso"] = 1 / vt.groupby("idVotacao")["tema"].transform("size")
    contagem = vt.groupby("tema")["peso"].sum()
    grandes = contagem[vt.groupby("tema")["idVotacao"].nunique() >= 15].index
    vt["tema"] = np.where(vt["tema"].isin(grandes), vt["tema"], "Outros temas")
    vt = vt.groupby(["idVotacao", "tema"], as_index=False)["peso"].sum()
    num("temas_votacoes_com_tema", vt["idVotacao"].nunique())
    out = []
    for nome, df, y in [("D", d, "seguiu"), ("U", u, "unido")]:
        a = df[["idVotacao", "partido", y]].merge(vt, on="idVotacao")
        g = a.groupby("tema").apply(lambda s: np.average(s[y], weights=s["peso"]), include_groups=False)
        n = vt.groupby("tema")["idVotacao"].nunique()
        out.append(g.rename(nome))
    tt = pd.concat(out, axis=1).join(vt.groupby("tema")["idVotacao"].nunique().rename("votacoes"))
    tt = tt.sort_values("U")
    for k, r in tt.iterrows():
        num(f"tema_D_{k}", r["D"]); num(f"tema_U_{k}", r["U"]); num(f"tema_n_{k}", int(r["votacoes"]))
    return tt, vt


# ================================================== orientações faladas (notas taquigráficas)
NOMES_FALA = {"PL": "PL", "PT": "PT", "PP": "PP", "PSD": "PSD", "MDB": "MDB", "REPUBLICANOS": "REPUBLICANOS",
              "UNIÃO": "UNIÃO", "UNIÃO BRASIL": "UNIÃO", "UNIAO": "UNIÃO", "PODEMOS": "PODE", "PODE": "PODE",
              "PSB": "PSB", "PDT": "PDT", "PSDB": "PSDB", "PSOL": "PSOL", "NOVO": "NOVO", "AVANTE": "AVANTE",
              "SOLIDARIEDADE": "SOLIDARIEDADE", "PCDOB": "PCdoB", "PC DO B": "PCdoB", "PV": "PV",
              "CIDADANIA": "CIDADANIA", "PRD": "PRD", "REDE": "REDE"}
BANCADA_REGISTRO = {"PL": "PL", "PT": "Fdr PT-PCdoB-PV", "PSOL": "Fdr PSOL-REDE", "NOVO": "Novo", "PSB": "PSB",
                    "PDT": "PDT", "PP": "PP", "PSD": "PSD", "MDB": "MDB", "UNIÃO": "União",
                    "REPUBLICANOS": "Republican", "PODE": "Podemos", "AVANTE": "Avante",
                    "SOLIDARIEDADE": "Solidaried", "PRD": "PRD"}


def orientacoes_faladas(p):
    """Reconstrói orientações de bancada a partir das transcrições dos discursos ("o PL orienta
    'sim'"), associando cada fala à primeira votação nominal do Plenário registrada até 45 min
    depois. Valida contra o registro oficial onde ele existe e mede D no período do megabloco,
    em que o registro traz só a linha (quase sempre vazia) do bloco."""
    d = pd.read_parquet(DADOS / "discursos.parquet", columns=["dataHoraInicio", "tipoDiscurso", "transcricao"])
    vt = pd.read_parquet(DADOS / "votacoes.parquet", columns=["idVotacao", "dataHoraRegistro", "siglaOrgao", "tem_votos_nominais"])
    vt = vt[(vt["siglaOrgao"] == "PLEN") & vt["tem_votos_nominais"].astype(bool)].copy()
    vt["tv"] = pd.to_datetime(vt["dataHoraRegistro"])
    vt = vt.dropna(subset=["tv"]).sort_values("tv")
    alt = "|".join(sorted(map(re.escape, NOMES_FALA), key=len, reverse=True))
    pat = re.compile(r"\b(?:o|a)\s+(%s)\s+(orienta|vota|encaminha)\s+[\"“'‘]?\s*(sim|não|nao|obstrução|obstrucao|liberado|liberada)" % alt, re.I)
    linhas = []
    for t, txt in zip(d["dataHoraInicio"], d["transcricao"].fillna("")):
        for m in pat.finditer(txt[:600]):      # a orientação vem no início da fala
            linhas.append((pd.Timestamp(t), NOMES_FALA[m.group(1).upper()], m.group(3).lower(), m.group(2).lower() == "orienta"))
    f = pd.DataFrame(linhas, columns=["t", "partido", "ori", "estrito"]).drop_duplicates()
    f["ori"] = f["ori"].map({"sim": "Sim", "não": "Não", "nao": "Não", "obstrução": "Obstrução",
                             "obstrucao": "Obstrução", "liberado": "Liberado", "liberada": "Liberado"})
    f = pd.merge_asof(f.sort_values("t"), vt[["tv", "idVotacao"]], left_on="t", right_on="tv",
                      direction="forward", tolerance=pd.Timedelta("45min")).dropna(subset=["idVotacao"])
    f = f.drop_duplicates(["idVotacao", "partido"], keep="last")
    num("fala_n_extraidas", len(linhas)); num("fala_n_associadas", len(f))
    # validação: concordância com a orientação própria registrada
    o = pd.read_parquet(DADOS / "votacoes_orientacoes.parquet")
    f["banc"] = f["partido"].map(BANCADA_REGISTRO)
    mm = f.merge(o, left_on=["idVotacao", "banc"], right_on=["idVotacao", "siglaBancada"], how="left")
    ok = mm["orientacao"].isin(["Sim", "Não", "Obstrução", "Liberado"])
    num("fala_val_n", int(ok.sum()))
    num("fala_val_concorda", (mm.loc[ok, "ori"] == mm.loc[ok, "orientacao"]).mean())
    num("fala_val_concorda_dir", (mm.loc[ok, "ori"].replace("Obstrução", "Não") == mm.loc[ok, "orientacao"].replace("Obstrução", "Não")).mean())
    fd = f[f["ori"].isin(["Sim", "Não", "Obstrução"])][["idVotacao", "partido", "ori", "estrito"]]
    # conferência manual de 50 associações (dados_aux/validacao_falas.csv)
    arq = AUX / "validacao_falas.csv"
    if arq.exists():
        vm = pd.read_csv(arq, sep=";")
        num("fala_manual_n", len(vm)); num("fala_manual_corretas", int((vm["avaliacao"] == "correta").sum()))
        num("fala_manual_incertas", int((vm["avaliacao"] == "incerta").sum()))
    # período do megabloco
    mb = p[p["camada"] == "bloco heterogêneo"]
    x = mb.merge(fd, on=["idVotacao", "partido"])
    x["od2"] = x["ori"].map(DIR)
    num("fala_mb_votos", len(x)); num("fala_mb_votos_total", len(mb))
    num("fala_mb_votacoes", x["idVotacao"].nunique()); num("fala_mb_votacoes_total", mb["idVotacao"].nunique())
    num("fala_mb_D", (x["vd"] == x["od2"]).mean())
    num("fala_mb_D_estrito", (x.loc[x["estrito"], "vd"] == x.loc[x["estrito"], "od2"]).mean())
    num("fala_mb_n_estrito", int(x["estrito"].sum()))
    # nas mesmas votações e partidos: D pela fala x unidade (U)
    u = amostra_U(p)
    xu = x.merge(u[["idVotacao", "deputado_id", "unido"]], on=["idVotacao", "deputado_id"])
    num("fala_mb_U_mesmos", xu["unido"].mean())
    for q in ["PL", "PT", "UNIÃO", "PSD", "MDB"]:
        s_ = xu[xu["partido"] == q]
        num(f"fala_mb_U_{q}", s_["unido"].mean())
    for q in ["PL", "PT", "UNIÃO", "PSD", "MDB"]:
        s_ = x[x["partido"] == q]
        num(f"fala_mb_D_{q}", (s_["vd"] == s_["od2"]).mean()); num(f"fala_mb_vot_{q}", s_["idVotacao"].nunique())
    # fora do megabloco, nos mesmos votos: D pela fala vs. pelo registro (mede o ruído da associação)
    y = p[p["diretiva"] & p["camada"].isin(["própria", "bloco", "bloco inferido"])].merge(fd, on=["idVotacao", "partido"])
    y["od2"] = y["ori"].map(DIR)
    num("fala_fora_votos", len(y))
    num("fala_fora_D_registro", (y["vd"] == y["od"]).mean()); num("fala_fora_D_fala", (y["vd"] == y["od2"]).mean())
    uf_ = y.merge(u[["idVotacao", "deputado_id", "unido"]], on=["idVotacao", "deputado_id"])
    num("fala_fora_U_mesmos", uf_["unido"].mean())
    # registro: o que a Câmara grava nas votações do megabloco
    vmb = mb["idVotacao"].unique()
    om = o[o["idVotacao"].isin(vmb)]
    num("reg_mb_linhas_partido_PL_PT", int(om["siglaBancada"].isin(["PL", "Fdr PT-PCdoB-PV"]).sum()))
    num("reg_mb_linhas_oposicao", int((om["siglaBancada"] == "Oposição").sum()))
    lb = om[om["siglaBancada"].str.startswith("Bl PlFdrP")]
    num("reg_mb_linhas", len(lb)); num("reg_mb_vazias", int(lb["orientacao"].isna().sum() + (lb["orientacao"] == "").sum()))
    num("fala_ruido_pp", R["fala_fora_D_registro"] - R["fala_fora_D_fala"])
    num("fala_erro_assoc", 1 - R["fala_val_concorda"])
    return f


# ============================================================================ Rice
def rice_esperado_sub(s, n, m):
    """E[Rice] numa subamostra sem reposição de tamanho m de uma bancada com s 'Sim' entre n."""
    from scipy.stats import hypergeom
    k = np.arange(0, m + 1)
    pk = hypergeom(n, s, m).pmf(k)
    return float(np.sum(pk * np.abs(2 * k - m) / m))


def rice_aleatorio(m, q):
    """E[Rice] de m votantes que votam Sim independentemente com prob. q (linha de base 'sem partido')."""
    from scipy.stats import binom
    k = np.arange(0, m + 1)
    return float(np.sum(binom(m, q).pmf(k) * np.abs(2 * k - m) / m))


def rice(v, limiar=LIMIAR_DISPUTA, sufixo="", ms=(10, 5, 3)):
    p = plenario(v)
    p = p[p["vd"].notna()].copy()
    p["s"] = (p["vd"] == 1).astype(int)
    q = p.groupby("idVotacao")["s"].mean()
    minoria = np.minimum(q, 1 - q)
    disputadas = minoria[minoria >= limiar].index
    num(f"n_votacoes_disputadas{sufixo}", len(disputadas))
    g = p.groupby(["idVotacao", "partido"])["s"].agg(["sum", "size"]).reset_index()
    g = g[g["size"] >= MIN_DEP_RICE]
    g["q"] = g["idVotacao"].map(q)
    g["rice"] = (2 * g["sum"] - g["size"]).abs() / g["size"]
    g["peso_carey"] = 1 - (2 * g["q"] - 1).abs()
    cache = {}
    for m in ms:
        vals, base = [], []
        for s_, n_, q_ in zip(g["sum"], g["size"], g["q"]):
            if n_ < m:
                vals.append(np.nan); base.append(np.nan)
                continue
            k = (s_, n_, m)
            if k not in cache:
                cache[k] = rice_esperado_sub(s_, n_, m)
            vals.append(cache[k])
            kq = ("q", round(q_, 3), m)
            if kq not in cache:
                cache[kq] = rice_aleatorio(m, q_)
            base.append(cache[kq])
        g[f"rice_m{m}"] = vals
        g[f"base_m{m}"] = base
    g["disputada"] = g["idVotacao"].isin(disputadas)
    g["racha"] = g["rice"] < 0.5          # menos de 75% da bancada no mesmo lado
    gd = g[g["disputada"]]
    agg = {"rice": "mean", "rice_m10": "mean", "rice_m5": "mean", "rice_m3": "mean", "base_m10": "mean",
           "base_m3": "mean", "racha": "mean"}
    rp = gd.groupby("partido").agg(agg)
    rp["rice_todas"] = g.groupby("partido")["rice"].mean()
    rp["rice_carey"] = g.groupby("partido").apply(lambda s: np.average(s["rice"], weights=s["peso_carey"])
                                                  if s["peso_carey"].sum() > 0 else np.nan, include_groups=False)
    rp["mediana_votantes"] = g.groupby("partido")["size"].median()
    # partidos com mediana de votantes < m não recebem Rice padronizado
    for m in ms:
        rp.loc[rp["mediana_votantes"] < m, f"rice_m{m}"] = np.nan
    for pt_, r in rp.iterrows():
        for c in ["rice", "rice_m10", "rice_m5", "rice_m3", "base_m3", "base_m10", "racha", "rice_todas", "rice_carey"]:
            num(f"{c}_{pt_}{sufixo}", r[c])
    num(f"rice_media_disputadas{sufixo}", gd["rice"].mean())
    num(f"rice_media_todas{sufixo}", g["rice"].mean())
    num(f"base_m10_media_disputadas{sufixo}", gd["base_m10"].mean())
    return g, rp


def rice_estabilidade(rp, rp20, ps):
    """Correlação de postos entre rankings de coesão: m=10 vs m=5; disputadas 10% vs 20%; Carey."""
    from scipy.stats import spearmanr
    a = rp.loc[[x for x in ps if x in rp.index]]
    ok = a[["rice_m10", "rice_m5"]].dropna()
    num("rice_spearman_m10_m5", spearmanr(ok["rice_m10"], ok["rice_m5"])[0])
    b = rp20.reindex(a.index)
    num("rice_spearman_disp10_disp20", spearmanr(a["rice"], b["rice"], nan_policy="omit")[0])
    num("rice_spearman_disp_carey", spearmanr(a["rice"], a["rice_carey"])[0])
    num("rice_spearman_disp_todas", spearmanr(a["rice"], a["rice_todas"])[0])
    ok2 = a[["rice", "rice_m10"]].dropna()
    num("rice_spearman_bruto_m10", spearmanr(ok2["rice"], ok2["rice_m10"])[0])
    num("rice_n_sem_m10", int(a["rice_m10"].isna().sum()))
    ok3 = a[["rice", "rice_m3"]].dropna()
    num("rice_spearman_bruto_m3", spearmanr(ok3["rice"], ok3["rice_m3"])[0]); num("rice_n_m3", len(ok3))
    ok4 = a[["rice_m3", "rice_m10"]].dropna()
    num("rice_spearman_m3_m10", spearmanr(ok4["rice_m3"], ok4["rice_m10"])[0])


# ================================================================ pontos ideais (IRT)
def prep_irt(p, min_minoria=0.025):
    """Arrays do modelo de pontos ideais só com o Plenário. y: Sim = 1; Não/Obstrução = 0
    (Abstenção fora). Remove votações quase unânimes. Linhas = períodos deputado×partido."""
    x = p[p["vd"].notna()].copy()
    x["y"] = x["vd"]
    q = x.groupby("idVotacao")["y"].mean()
    ok = np.minimum(q, 1 - q) >= min_minoria
    x = x[x["idVotacao"].isin(ok[ok].index)].reset_index(drop=True)
    x["periodo"] = x["deputado_id"].astype(str) + "|" + x["partido"]
    i, periodos = pd.factorize(x["periodo"])
    j, votacoes = pd.factorize(x["idVotacao"])
    base, deps = pd.factorize(periodos.str.split("|").str[0].astype(int))
    grp, celulas = pd.factorize(x["partido"] + "|" + x["idVotacao"])
    part_per, partidos = pd.factorize(periodos.str.split("|").str[1])
    global DIGITAL
    if not DIGITAL:   # o primeiro prep_irt é o da amostra completa do Plenário
        DIGITAL = f"{len(x)}_{len(votacoes)}_{len(periodos)}_{int(x['y'].sum())}"
    return dict(df=x, i=i, j=j, y=x["y"].to_numpy(), base=base, grp=grp, part_per=part_per,
                periodos=periodos, votacoes=votacoes, deps=deps, partidos=partidos, celulas=celulas,
                n_i=len(periodos), n_j=len(votacoes))


def ajustar(A, m, modelo, ndim=2, lam_d=4.0, lam_g=0.01, seed=SEMENTE):
    """Ajusta um modelo na máscara m de observações. modelo: global | intra | fe (só efeitos
    partido×votação: intra com variância individual ~0)."""
    ED.RNG = np.random.default_rng(seed)
    i, j, y = A["i"][m], A["j"][m], A["y"][m]
    if modelo == "global":
        f = ED.ajustar_irt(i, j, y, A["n_i"], A["n_j"], ndim, base=A["base"], lam_d=lam_d)
    elif modelo == "intra":
        f = _intra(A, m, ndim, lam_d, lam_g)
    elif modelo == "fe":
        f = _intra(A, m, 1, 1e4, lam_g, lam_x=1e4)
    else:
        raise ValueError(modelo)
    f = {k: f[k] for k in ("a", "b", "g", "u", "x", "convergiu", "nll")}
    return f


def _intra(A, m, ndim, lam_d, lam_g, lam_x=1.0):
    """Modelo intrapartidário: efeito fixo partido×votação (g) e pontos centrados no partido.
    O vetor g tem uma posição por célula partido×votação de TODA a amostra (células ausentes
    do treino ficam em 0 pela penalização)."""
    n_g = A["grp"].max() + 1
    grp = A["grp"][m].copy()
    # ajustar_irt dimensiona g por grupos.max()+1: garante o tamanho total com um voto fantasma? Não:
    # reindexa só as células presentes e devolve g no índice global.
    cel, inv = np.unique(grp, return_inverse=True)
    f = ED.ajustar_irt(A["i"][m], A["j"][m], A["y"][m], A["n_i"], A["n_j"], ndim, grupos=inv,
                       base=A["base"], lam_d=lam_d, lam_g=lam_g, lam_x=lam_x, centrar=A["part_per"])
    g = np.zeros(n_g)
    g[cel] = f["g"]
    f["g"] = g
    return f


def prever(f, A, m, grupos=True):
    z = f["a"][A["j"][m]] + np.einsum("nk,nk->n", f["b"][A["j"][m]], f["x"][A["i"][m]])
    if grupos and f["g"] is not None and len(f["g"]):
        z = z + f["g"][A["grp"][m]]
    from scipy.special import expit
    return expit(z)


def orientar(A, f, mask=None):
    """Pontos por deputado (u) e por período (x), rotacionados (dim1 = maior variância) e com
    sinal: dim1 positivo = mais governista (correlação com a taxa de voto com o Governo)."""
    df = A["df"]
    if mask is None:
        mask = np.ones(len(df), bool)
    ndim = f["x"].shape[1]
    if f["u"].shape[0] == len(A["deps"]) and np.abs(f["u"]).sum() > 0 and not f.get("intra", False):
        u_dep = f["u"]
    else:
        u_dep = np.stack([np.bincount(A["base"], f["x"][:, k], len(A["deps"])) for k in range(ndim)], 1) \
            / np.maximum(np.bincount(A["base"], minlength=len(A["deps"])), 1)[:, None]
    (u, x), vt = ED.rotacionar(u_dep, f["x"])
    gov = (df[mask].assign(s=(df["vd"] == df["gd"]).astype(float).where(df["gd"].notna()))
           .groupby("deputado_id")["s"].mean().reindex(A["deps"]).to_numpy(float))
    ok = ~np.isnan(gov)
    if np.corrcoef(u[ok, 0], gov[ok])[0, 1] < 0:
        u[:, 0] *= -1; x[:, 0] *= -1
    nv_dep = np.bincount(A["base"][A["i"][mask]], minlength=len(A["deps"]))
    nv_per = np.bincount(A["i"][mask], minlength=A["n_i"])
    U = pd.DataFrame(u, columns=[f"dim{k + 1}" for k in range(ndim)])
    U.insert(0, "deputado_id", A["deps"]); U["n_votos"] = nv_dep
    X = pd.DataFrame(x, columns=[f"dim{k + 1}" for k in range(ndim)])
    X.insert(0, "periodo", A["periodos"]); X["deputado_id"] = A["deps"][A["base"]]
    X["partido"] = A["periodos"].str.split("|").str[1]; X["n_votos"] = nv_per
    return U, X


# ------------------------------------------------- M2: lealdade individual não espacial
def ajustar_lealdade(A, m, maj_cel, offset, lam_r=1.0):
    """M2 = M1 + propensão individual de desvio sem conteúdo espacial:
    P(Sim) = σ(z_M1 + r_dep · d_cel), d_cel = +1 se a maioria de treino da célula partido×votação
    é Não, −1 se é Sim (0 se empate). r > 0 = tendência a votar contra a maioria do próprio
    partido em qualquer direção. z_M1 (offset) é o logit do M1 ajustado na mesma dobra, de modo
    que M2 contém M1 e só a lealdade é estimada."""
    from scipy.optimize import minimize
    from scipy.special import expit
    n_d = len(A["deps"])
    dd_, y, off = A["base"][A["i"][m]], A["y"][m], offset[m]
    dcel = np.where(np.isnan(maj_cel), 0.0, 1 - 2 * np.nan_to_num(maj_cel))
    s = dcel[A["grp"][m]]

    def f(r):
        p = expit(off + r[dd_] * s)
        ll = -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12))
        return ll + lam_r * r @ r, np.bincount(dd_, (p - y) * s, n_d) + 2 * lam_r * r

    res = minimize(f, np.zeros(n_d), jac=True, method="L-BFGS-B", options={"maxiter": 5000})
    return dict(r=res.x, dcel=dcel, convergiu=res.success)


def ajustar_lealdade_b(A, m, maj_cel, offset, lam_r=1.0, lam_s=0.04, seed=SEMENTE):
    """M2b = M1 + lealdade com a MESMA estrutura de parâmetros de M3, mas sem direção:
    P(Sim) = σ(z_M1 + s_j · ρ_r · d_cel): ρ por período deputado×partido, escala s_j por votação,
    sinal dado pela maioria de treino da célula (d_cel). Difere de M3 (σ(a_j + g + b_j x_r)) só
    porque a "direção" do desvio é sempre contra a maioria do próprio partido."""
    from scipy.optimize import minimize
    from scipy.special import expit
    n_i, n_j = A["n_i"], A["n_j"]
    ii, jj, y, off = A["i"][m], A["j"][m], A["y"][m], offset[m]
    dcel = np.where(np.isnan(maj_cel), 0.0, 1 - 2 * np.nan_to_num(maj_cel))
    dd = dcel[A["grp"][m]]

    def f(th):
        r, sj = th[:n_i], th[n_i:]
        z = off + sj[jj] * r[ii] * dd
        p = expit(z)
        ll = -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12))
        e = p - y
        gr = np.bincount(ii, e * sj[jj] * dd, n_i) + 2 * lam_r * r
        gs = np.bincount(jj, e * r[ii] * dd, n_j) + 2 * lam_s * sj
        return ll + lam_r * r @ r + lam_s * sj @ sj, np.r_[gr, gs]

    rng = np.random.default_rng(seed)
    th0 = np.r_[rng.normal(0, 0.1, n_i), np.full(n_j, 0.5)]
    res = minimize(f, th0, jac=True, method="L-BFGS-B", options={"maxiter": 15000, "maxfun": 30000})
    return dict(r=res.x[:n_i], s=res.x[n_i:], dcel=dcel, convergiu=res.success)


def prever_lealdade_b(f, A, m, offset):
    from scipy.special import expit
    return expit(offset[m] + f["s"][A["j"][m]] * f["r"][A["i"][m]] * f["dcel"][A["grp"][m]])


def prever_lealdade(f, A, m, offset):
    from scipy.special import expit
    return expit(offset[m] + f["r"][A["base"][A["i"][m]]] * f["dcel"][A["grp"][m]])


# ------------------------------------------------------------- validação cruzada
_A = None


def _job(arg):
    """Executa um ajuste (para multiprocessing)."""
    nome, k, modelo, ndim, lam_d, lam_g = arg
    A = _A
    m = A["fold"] != k if k is not None else np.ones(len(A["y"]), bool)
    t = time.time()
    f = ajustar(A, m, modelo, ndim=ndim, lam_d=lam_d, lam_g=lam_g, seed=SEMENTE + (k or 0))
    return nome, k, f, time.time() - t


def rodar_jobs(A, jobs, procs=4):
    global _A
    _A = A
    import multiprocessing as mp
    with mp.get_context("fork").Pool(procs) as pool:
        out = pool.map(_job, jobs, chunksize=1)
    return {(n, k): (f, dt) for n, k, f, dt in out}


def dobras(A, K=5, seed=SEMENTE):
    """Validação cruzada em K dobras sobre células deputado×votação, estratificada por votação."""
    rng = np.random.default_rng(seed)
    ordem = rng.permutation(len(A["y"]))
    rank = pd.Series(ordem).groupby(A["j"][ordem]).cumcount().to_numpy()
    fold = np.empty(len(A["y"]), int)
    fold[ordem] = rank % K
    return fold


def stats_celula(A, m):
    """Estatísticas de treino por célula partido×votação: maioria, nº de votos, nº de desvios."""
    n_c = A["grp"].max() + 1
    s = np.bincount(A["grp"][m], A["y"][m], n_c)
    n = np.bincount(A["grp"][m], minlength=n_c).astype(float)
    maj = np.where(n == 0, np.nan, np.where(2 * s > n, 1.0, np.where(2 * s < n, 0.0, np.nan)))
    minoria = np.where(n > 0, np.minimum(s, n - s) / np.maximum(n, 1), np.nan)
    return maj, n, minoria


def regra_orientacao(A, m_tr, m_te, maj_cel):
    """M0: orientação diretiva (camadas não heterogêneas); se ausente, maioria de treino do
    partido na votação; se ausente, maioria de treino da votação. Probabilidade calibrada pela
    taxa de acerto da regra no treino."""
    df = A["df"]
    ori = np.where(df["camada"].isin(["própria", "bloco", "bloco inferido"]).to_numpy(), df["od"].to_numpy(), np.nan)
    qv = pd.Series(A["y"][m_tr]).groupby(A["j"][m_tr]).mean().reindex(range(A["n_j"])).to_numpy()
    regra = np.where(~np.isnan(ori), ori, maj_cel[A["grp"]])
    regra = np.where(np.isnan(regra), (qv[A["j"]] > 0.5).astype(float), regra)
    acc = np.mean(regra[m_tr] == A["y"][m_tr])
    pr = np.where(regra == 1, acc, 1 - acc)
    # versão calibrada por fonte da regra × partido (taxa de acerto no treino de cada estrato)
    fonte = np.where(~np.isnan(ori), df["camada"].to_numpy(), np.where(~np.isnan(maj_cel[A["grp"]]), "maioria partido", "maioria votação"))
    estrato = pd.Series(fonte).astype(str) + "|" + df["partido"].astype(str).to_numpy()
    acerto = pd.Series((regra == A["y"]).astype(float))
    acc_e = acerto[m_tr].groupby(estrato[m_tr]).agg(["sum", "size"])
    acc_e = (acc_e["sum"] + 1) / (acc_e["size"] + 2)
    a_e = estrato.map(acc_e).fillna(acc).to_numpy()
    prc = np.where(regra == 1, a_e, 1 - a_e)
    return pr[m_te], acc, prc[m_te]


def metricas(y, p):
    from sklearn.metrics import roc_auc_score  # noqa: F401
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return dict(logloss=float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
                brier=float(np.mean((p - y) ** 2)), acuracia=float(np.mean((p > 0.5) == (y > 0.5))))


MODELOS_CV = [("M1", "fe", 1, 1e4), ("M3", "intra", 1, 4.0), ("M4", "intra", 2, 4.0), ("M5", "global", 2, 4.0)]
NOMES_M = {"M0": "M0 orientação do líder", "M0c": "M0c orientação, calibrada por partido e fonte",
           "M1": "M1 só partido×votação", "M2": "M2 = M1 + lealdade individual",
           "M2b": "M2b = M1 + lealdade por período × escala por votação", "M3emb": "M3 com posições embaralhadas no partido",
           "M3": "M3 intra 1D", "M3L": "M3L = M3 + lealdade individual", "M4": "M4 intra 2D",
           "M5": "M5 global 2D (sem partido)"}


def validacao_cruzada(A, K=5):
    """Compara M0–M5 fora da amostra (P2/P4). Devolve as previsões de teste por modelo."""
    A["fold"] = dobras(A, K)
    jobs = [(n, k, mod, nd, ld, 0.01) for k in range(K) for n, mod, nd, ld in MODELOS_CV]
    # sensibilidade à penalização (só na dobra 0)
    jobs += [("M3_lamd1", 0, "intra", 1, 1.0, 0.01), ("M3_lamd16", 0, "intra", 1, 16.0, 0.01),
             ("M1_lamg1", 0, "fe", 1, 1e4, 1.0), ("M3_lamg1", 0, "intra", 1, 4.0, 1.0)]
    fits = em_cache(f"cv_K{K}", rodar_jobs, A, jobs)
    n = len(A["y"])
    P = {k: np.full(n, np.nan) for k in ["M0", "M0c", "M1", "M2", "M2b", "M3", "M3L", "M3emb", "M4", "M5"]}
    P_sens = {}
    info = dict(maj=np.full(n, np.nan), n_tr=np.full(n, np.nan), min_tr=np.full(n, np.nan))
    for k in range(K):
        tr, te = A["fold"] != k, A["fold"] == k
        maj, ncel, minoria = stats_celula(A, tr)
        info["maj"][te] = maj[A["grp"][te]]
        info["n_tr"][te] = ncel[A["grp"][te]]
        info["min_tr"][te] = minoria[A["grp"][te]]
        P["M0"][te], _, P["M0c"][te] = regra_orientacao(A, tr, te, maj)
        from scipy.special import logit
        z1 = logit(np.clip(prever(fits[("M1", k)][0], A, np.ones(n, bool)), 1e-9, 1 - 1e-9))
        fl = em_cache(f"cv_lealdade_{k}", ajustar_lealdade, A, tr, maj, z1)
        P["M2"][te] = prever_lealdade(fl, A, te, z1)
        flb = em_cache(f"cv_lealdade_b_{k}", ajustar_lealdade_b, A, tr, maj, z1)
        P["M2b"][te] = prever_lealdade_b(flb, A, te, z1)
        # teste de posições embaralhadas: M3 com os pontos permutados entre períodos do mesmo partido
        f3 = dict(fits[("M3", k)][0])
        rng = np.random.default_rng(SEMENTE + 100 + k)
        perm = np.arange(A["n_i"])
        for g_ in np.unique(A["part_per"]):
            idx = np.flatnonzero(A["part_per"] == g_)
            perm[idx] = rng.permutation(idx)
        f3["x"] = f3["x"][perm]
        P["M3emb"][te] = prever(f3, A, te)
        z3 = logit(np.clip(prever(fits[("M3", k)][0], A, np.ones(n, bool)), 1e-9, 1 - 1e-9))
        fl3 = em_cache(f"cv_lealdade_M3_{k}", ajustar_lealdade, A, tr, maj, z3)
        P["M3L"][te] = prever_lealdade(fl3, A, te, z3)
        if k == 0:
            num("m2_r_sd", float(np.std(fl["r"])))
        for nome, mod, nd, ld in MODELOS_CV:
            f = fits[(nome, k)][0]
            P[nome][te] = prever(f, A, te, grupos=(mod != "global"))
        if k == 0:
            for nome in ["M3_lamd1", "M3_lamd16", "M1_lamg1", "M3_lamg1"]:
                P_sens[nome] = prever(fits[(nome, 0)][0], A, te)
    tempos = {f"{n}": dt for (n, k), (f, dt) in fits.items()}
    return P, P_sens, info, tempos


def avaliar_cv(A, P, P_sens, info, B=1000):
    from sklearn.metrics import average_precision_score
    y = A["y"]
    desvio = (~np.isnan(info["maj"])) & (y != info["maj"])
    subs = {"todas": np.ones(len(y), bool),
            "disputadas_intra": (info["min_tr"] > 0) & (info["n_tr"] >= MIN_COLEGAS_U),
            "celulas_5mais": info["n_tr"] >= MIN_COLEGAS_U,
            "minoria10": (info["min_tr"] >= 0.10) & (info["n_tr"] >= MIN_COLEGAS_U)}
    linhas = []
    for sn, sm in subs.items():
        for mn, pr in P.items():
            me = metricas(y[sm], pr[sm])
            ok = sm & ~np.isnan(info["maj"])
            score = np.where(info["maj"][ok] == 1, 1 - pr[ok], pr[ok])
            me["auc_pr_desvio"] = float(average_precision_score(desvio[ok], score))
            me["taxa_desvio"] = float(desvio[ok].mean())
            linhas.append(dict(amostra=sn, modelo=mn, n=int(sm.sum()), **me))
            for kk, x in me.items():
                num(f"cv_{sn}_{mn}_{kk}", x)
        num(f"cv_{sn}_n", int(sm.sum())); num(f"cv_{sn}_share", float(sm.mean()))
    tab = pd.DataFrame(linhas)
    # IC das diferenças de log-loss por bootstrap de deputados (nas células disputadas internamente)
    sm = subs["disputadas_intra"]
    dep = A["base"][A["i"]][sm]
    nd = len(A["deps"])
    cont = np.bincount(dep, minlength=nd)
    perdas, perdas_obs = {}, {}
    for mn, pr in P.items():
        pp = np.clip(pr[sm], 1e-6, 1 - 1e-6)
        ll = -(y[sm] * np.log(pp) + (1 - y[sm]) * np.log(1 - pp))
        perdas[mn] = np.bincount(dep, ll, nd)
        perdas_obs[mn] = ll
    rngv = np.random.default_rng(SEMENTE + 9)
    Wv = np.stack([np.bincount(rngv.integers(0, A["n_j"], A["n_j"]), minlength=A["n_j"]) for _ in range(B)])
    rng = np.random.default_rng(SEMENTE)
    W = np.stack([np.bincount(rng.integers(0, nd, nd), minlength=nd) for _ in range(B)])
    pares = [("M0", "M1"), ("M0c", "M1"), ("M0", "M0c"), ("M1", "M2"), ("M1", "M2b"), ("M2b", "M3"), ("M3emb", "M3"),
             ("M2", "M3"), ("M2", "M3L"), ("M3", "M3L"),
             ("M3", "M4"), ("M1", "M3"), ("M5", "M4"), ("M0", "M4")]
    difs = []
    for a, b in pares:
        est = (perdas[a] - perdas[b]).sum() / cont.sum()
        bo = (W @ (perdas[a] - perdas[b])) / (W @ cont)
        difs.append(dict(par=f"{a} − {b}", dif=est, lo=np.percentile(bo, 2.5), hi=np.percentile(bo, 97.5)))
        # bootstrap de votações (unidade de dependência alternativa)
        vj = A["j"][sm]
        pv_ = np.bincount(vj, perdas_obs[a] - perdas_obs[b], A["n_j"]); cv_ = np.bincount(vj, minlength=A["n_j"])
        bv = (Wv @ pv_) / (Wv @ cv_)
        num(f"cvdif_{a}_{b}_vlo", np.percentile(bv, 2.5), 5); num(f"cvdif_{a}_{b}_vhi", np.percentile(bv, 97.5), 5)
        num(f"cvdif_{a}_{b}", est, 5); num(f"cvdif_{a}_{b}_lo", np.percentile(bo, 2.5), 5)
        num(f"cvdif_{a}_{b}_hi", np.percentile(bo, 97.5), 5)
    # por tamanho de bancada (células disputadas)
    faixas = pd.cut(info["n_tr"], [0, 4, 19, 49, 1e9], labels=["<5", "5–19", "20–49", "≥50"])
    fx = []
    for fa in ["<5", "5–19", "20–49", "≥50"]:
        mm = (faixas == fa) & (info["min_tr"] > 0)
        for mn in ["M1", "M2", "M3", "M4"]:
            fx.append(dict(faixa=fa, modelo=mn, n=int(mm.sum()), **metricas(y[mm], P[mn][mm])))
            num(f"cvfaixa_{fa}_{mn}_logloss", fx[-1]["logloss"])
    # sensibilidade (dobra 0, células disputadas)
    te0 = (A["fold"] == 0) & sm
    s0 = (A["fold"] == 0)
    for nome, pr in P_sens.items():
        num(f"cvsens_{nome}_logloss", metricas(y[te0], pr[te0[s0]])["logloss"])
    for mn in ["M1", "M3"]:
        num(f"cvsens_{mn}_base_logloss", metricas(y[te0], P[mn][te0])["logloss"])
    return tab, pd.DataFrame(difs), pd.DataFrame(fx)


# ================================================== regressões com efeitos fixos (MPL)
def demean(M, grupos, tol=1e-8, it_max=500):
    """Projeções alternadas: remove médias de cada fator de efeitos fixos (lista de arrays int)."""
    M = np.asarray(M, float).copy()
    if M.ndim == 1:
        M = M[:, None]
    cont = [np.bincount(g).astype(float) for g in grupos]
    for _ in range(it_max):
        ant = M.copy()
        for g, c in zip(grupos, cont):
            med = np.stack([np.bincount(g, M[:, k], len(c)) for k in range(M.shape[1])], 1) / np.maximum(c, 1)[:, None]
            M -= med[g]
        if len(grupos) == 1 or np.max(np.abs(M - ant)) < tol:
            break
    return M


def ols_fe(y, X, fes, clusters, nomes):
    """MPL com efeitos fixos (projeções alternadas) e EP agrupados em duas vias
    (Cameron, Gelbach & Miller 2011): V = V_c1 + V_c2 − V_c1∩c2."""
    Z = demean(np.column_stack([y, X]), fes)
    yt, Xt = Z[:, 0], Z[:, 1:]
    # colunas que somem depois de retirar os efeitos fixos não são identificadas: saem
    norma0 = np.linalg.norm(np.asarray(X, float), axis=0)
    ok = np.linalg.norm(Xt, axis=0) > 1e-6 * np.maximum(norma0, 1e-12)
    if not ok.all():
        print(f"    aviso: colunas não identificadas removidas: {[n for n, k in zip(nomes, ok) if not k]}")
    Xt, nomes = Xt[:, ok], [n for n, k in zip(nomes, ok) if k]
    # remove, em ordem, colunas linearmente dependentes das anteriores (não identificadas em conjunto)
    manter = []
    for k in range(Xt.shape[1]):
        cand = manter + [k]
        if np.linalg.matrix_rank(Xt[:, cand], tol=1e-8 * np.linalg.norm(Xt[:, cand])) == len(cand):
            manter = cand
    if len(manter) < Xt.shape[1]:
        print(f"    aviso: colunas colineares removidas: {[nomes[k] for k in range(len(nomes)) if k not in manter]}")
    Xt, nomes = Xt[:, manter], [nomes[k] for k in manter]
    XtX_inv = np.linalg.inv(Xt.T @ Xt)
    b = XtX_inv @ Xt.T @ yt
    e = yt - Xt @ b

    def meat(c):
        S = np.stack([np.bincount(c, Xt[:, k] * e) for k in range(Xt.shape[1])], 1)
        return S.T @ S

    c1, c2 = clusters
    inter = pd.factorize(pd.Series(c1).astype(str) + "_" + pd.Series(c2).astype(str))[0]
    V = XtX_inv @ (meat(c1) + meat(c2) - meat(inter)) @ XtX_inv
    ep = np.sqrt(np.clip(np.diag(V), 0, None))
    return pd.DataFrame({"coef": b, "ep": ep, "lo": b - 1.96 * ep, "hi": b + 1.96 * ep}, index=nomes), V, e


def wald(b, V, idx):
    from scipy.stats import chi2
    bb, VV = b[idx], V[np.ix_(idx, idx)]
    w = float(bb @ np.linalg.pinv(VV) @ bb)
    return w, len(idx), 1 - chi2.cdf(w, len(idx))


def painel_exercicio(dep, p):
    """Painel de presença: para cada votação, deputados em exercício (valida contra 513)."""
    per = periodos_exercicio(dep)
    datas = p.drop_duplicates("dt")[["idVotacao", "dt"]]
    out = []
    for _, r in datas.iterrows():
        em = per[(per["inicio"] <= r["dt"] + pd.Timedelta(hours=23)) & (per["fim"] > r["dt"])]
        out.append((r["idVotacao"], len(em["deputado_id"].unique())))
    c = pd.DataFrame(out, columns=["idVotacao", "n_exercicio"])
    num("presenca_n_datas", len(c))
    num("presenca_media_em_exercicio", c["n_exercicio"].mean(), 1)
    num("presenca_share_datas_513_mais_menos_5", ((c["n_exercicio"] - 513).abs() <= 5).mean())
    num("presenca_min", int(c["n_exercicio"].min())); num("presenca_max", int(c["n_exercicio"].max()))
    return per, c


def covariaveis_voto(x, dep, per):
    """Covariáveis por voto: suplente em exercício (variável no tempo) e motivo do afastamento do
    titular; mulher; idade (décadas); log das cadeiras legais da UF."""
    x = x.copy()
    per = per.sort_values("inicio")
    x = x.sort_values("dt")
    x = pd.merge_asof(x, per[["deputado_id", "inicio", "condicao"]], left_on="dt", right_on="inicio",
                      by="deputado_id", direction="backward")
    fin = dep.set_index("id")["condicaoEleitoral"]
    x["condicao"] = x["condicao"].fillna(x["deputado_id"].map(fin))
    x["suplente"] = (x["condicao"] == "Suplente").astype(float)
    ms = motivo_suplencia(dep).sort_values("t")
    x = pd.merge_asof(x, ms.rename(columns={"t": "t_posse"}), left_on="dt", right_on="t_posse",
                      by="deputado_id", direction="backward")
    mot = x["motivo"].fillna("não identificado")
    x["sup_ministro"] = x["suplente"] * mot.str.contains("Ministro").astype(float)
    x["sup_secretario"] = x["suplente"] * mot.str.contains("Secretário").astype(float)
    x["sup_outro"] = x["suplente"] - x["sup_ministro"] - x["sup_secretario"]
    info = dep.set_index("id")
    x["mulher"] = (x["deputado_id"].map(info["sexo"]) == "F").astype(float)
    nasc = pd.to_datetime(x["deputado_id"].map(info["dataNascimento"]), errors="coerce")
    x["idade10"] = (pd.Timestamp("2023-02-01") - nasc).dt.days / 3652.5
    x["log_cadeiras_uf"] = np.log(x["deputado_siglaUf"].map(CADEIRAS_UF))
    return x


def distancia_fora_periodo(p, A_full):
    """Distância de cada deputado à mediana do seu partido na dim1 global, estimada com as
    votações do OUTRO biênio (2023–24 explica 2025–26 e vice-versa), para não ser circular.
    Devolve também a posição relativa com sinal (positivo = mais governista que o partido)."""
    res = {}
    for nome, cond in [("b1", p["ano"] <= 2024), ("b2", p["ano"] >= 2025)]:
        A = prep_irt(p[cond])
        f = em_cache(f"global_{nome}", ajustar, A, np.ones(len(A["y"]), bool), "global")
        U, X = orientar(A, f)
        X = X[X["n_votos"] >= 30]
        med = X.groupby("partido")["dim1"].median()
        # padroniza pelo DP da dim1 entre os períodos do ajuste (as escalas dos dois ajustes diferem)
        X["rel"] = (X["dim1"] - X["partido"].map(med)) / X["dim1"].std()
        num(f"dist_dp_dim1_{nome}", X["dim1"].std())
        U = U.set_index("deputado_id")
        res[nome] = (X.set_index(["deputado_id", "partido"])["rel"], U)
    return res


def anexar_distancia(x, dist):
    """Para votos de 2025–26 usa o ajuste de 2023–24 e vice-versa (deputado×partido; se o deputado
    não tem período naquele partido no outro biênio, fica ausente)."""
    rel = np.full(len(x), np.nan)
    for alvo, fonte in [(x["ano"] >= 2025, "b1"), (x["ano"] <= 2024, "b2")]:
        s = dist[fonte][0]
        k = pd.MultiIndex.from_arrays([x["deputado_id"], x["partido"]])
        r = s.reindex(k).to_numpy()
        rel = np.where(alvo.to_numpy(), r, rel)
    x["rel_gov_fora"] = rel
    x["dist_fora"] = np.abs(rel)
    return x


def regressao_desvio(base, dep, per, dist):
    """P3: quem desvia. Desfechos: desvio da orientação (D) e da maioria dos colegas (U).
    MPL com EF partido×votação; EP em duas vias (deputado, votação)."""
    tr = trocas_partido()
    troca_ind = set(tr.loc[~tr["fusao"], "deputado_id"])
    out = {}
    for nome, df, y in [("D", base["d"], "seguiu"), ("U", base["u"], "unido")]:
        x = covariaveis_voto(df, dep, per)
        x = anexar_distancia(x, dist)
        t1 = trocas_partido()
        t1 = t1[~t1["fusao"]].drop_duplicates("deputado_id").set_index("deputado_id")["data"]
        tt_ = x["deputado_id"].map(t1)
        x["trocou_antes"] = (tt_.notna() & (x["dt"] < tt_)).astype(float)
        x["trocou_depois"] = (tt_.notna() & (x["dt"] >= tt_)).astype(float)
        x["desvio"] = 1 - x[y]
        cov = ["sup_ministro", "sup_secretario", "sup_outro", "mulher", "idade10", "log_cadeiras_uf",
               "trocou_antes", "trocou_depois", "dist_fora"]
        z = x.dropna(subset=cov + ["desvio"]).reset_index(drop=True)
        fe = pd.factorize(z["partido"] + "|" + z["idVotacao"])[0]
        c1 = pd.factorize(z["deputado_id"])[0]
        c2 = pd.factorize(z["idVotacao"])[0]
        Xm = z[cov].to_numpy(float)
        tab, V, e = ols_fe(z["desvio"].to_numpy(float), Xm, [fe], (c1, c2), cov)
        num(f"reg_{nome}_n", len(z)); num(f"reg_{nome}_n_dep", z["deputado_id"].nunique())
        num(f"reg_{nome}_media_desvio", z["desvio"].mean())
        num(f"reg_{nome}_share_sem_dist", 1 - len(z) / len(x.dropna(subset=cov[:-1] + ["desvio"])))
        for k, r in tab.iterrows():
            for c in ["coef", "ep", "lo", "hi"]:
                num(f"reg_{nome}_{k}_{c}", r[c], 5)
        # UF: teste conjunto (Wald com V em duas vias), 26 dummies
        ufd = pd.get_dummies(z["deputado_siglaUf"], dtype=float)
        ufd = ufd.drop(columns=ufd.columns[0])
        X2 = np.column_stack([Xm[:, [0, 1, 2, 3, 4, 6, 7, 8]], ufd.to_numpy()])
        tab2, V2, _ = ols_fe(z["desvio"].to_numpy(float), X2, [fe], (c1, c2),
                             [cov[k] for k in [0, 1, 2, 3, 4, 6, 7, 8]] + list(ufd.columns))
        w, gl, pv = wald(tab2["coef"].to_numpy(), V2, list(range(8, X2.shape[1])))
        num(f"reg_{nome}_uf_wald", w, 2); num(f"reg_{nome}_uf_gl", gl); num(f"reg_{nome}_uf_p", pv)
        # decomposição da variância das taxas brutas de desvio entre deputados (>= 50 votos):
        # variância total = sinal + ruído binomial; fração do sinal entre partidos (partido modal)
        zz = pd.DataFrame({"dep": z["deputado_id"], "obs": z["desvio"], "partido": z["partido"]})
        g = zz.groupby("dep").agg(obs=("obs", "mean"), n=("obs", "size"),
                                  partido=("partido", lambda s: s.value_counts().index[0]))
        g = g[g["n"] >= 50]
        total = g["obs"].var()
        ruido = (g["obs"] * (1 - g["obs"]) / g["n"]).mean()
        sinal = total - ruido
        entre = g.groupby("partido")["obs"].transform("mean").var()
        num(f"var_{nome}_total", total, 6); num(f"var_{nome}_sinal", sinal, 6)
        num(f"var_{nome}_share_sinal", sinal / total)
        num(f"var_{nome}_share_sinal_compl", 1 - sinal / total)
        num(f"var_{nome}_share_partido_no_sinal", entre / sinal)
        num(f"var_{nome}_share_intra_no_sinal", 1 - entre / sinal)
        # versão ajustada: excesso de desvio sobre a média da célula partido×votação
        cm = z.groupby(fe)["desvio"].transform("mean").to_numpy()
        za = pd.DataFrame({"dep": z["deputado_id"], "exc": z["desvio"] - cm, "v": cm * (1 - cm)})
        ga = za.groupby("dep").agg(exc=("exc", "mean"), v=("v", "sum"), n=("exc", "size"))
        ga = ga[ga["n"] >= 50]
        ta = ga["exc"].var()
        num(f"var_{nome}_aj_share_ruido", (ga["v"] / ga["n"] ** 2).mean() / ta)
        out[nome] = (tab, g, z)
    return out


def estudo_evento(base, dep):
    """Troca de partido: desvio_ij = α_i + γ_{partido×votação} + Σ θ_k 1[t − T_i ∈ k]
    (trocas individuais; fusões como grupo placebo). EP em duas vias."""
    tr = trocas_partido()
    tr = tr[tr["data"] >= "2023-04-01"].sort_values("data")
    ind = tr[~tr["fusao"]].drop_duplicates("deputado_id").set_index("deputado_id")["data"]
    fus = tr[tr["fusao"]].drop_duplicates("deputado_id").set_index("deputado_id")["data"]
    fus = fus[~fus.index.isin(ind.index)]
    janelas = [(-99, -13, "≤−13"), (-12, -7, "−12 a −7"), (-6, -4, "−6 a −4"), (-3, -1, "−3 a −1"),
               (0, 3, "0 a 3"), (4, 99, "≥4")]
    ref = "−12 a −7"
    res = {}
    # versões: principal (todas as trocas individuais; fusões à parte) e só a coorte da janela de 2026
    # (Sun e Abraham, 2021: com adoção escalonada, tratados antigos não devem servir de controle;
    # aqui os demais trocadores são retirados da amostra e os controles são os que nunca trocaram)
    ind26 = ind[(ind >= "2026-03-01") & (ind < "2026-06-01")]
    # controles da coorte: só quem nunca trocou individualmente (inclusive antes de abril de 2023)
    todos_ind = set(trocas_partido().query("~fusao")["deputado_id"])
    excl26 = (todos_ind | set(ind.index)) - set(ind26.index) | set(fus.index)
    num("ev_c26_n_coorte", len(ind26))
    versoes = [("", ind, fus, set()), ("_c26", ind26, fus.iloc[:0], excl26)]
    for suf, ind_v, fus_v, excl in versoes:
      for nome, df, y in [("U", base["u"], "unido"), ("D", base["d"], "seguiu")]:
          x = df[~df["deputado_id"].isin(excl)].reset_index(drop=True).copy()
          x["desvio"] = 1 - x[y]
          cols, nomes = [], []
          for grupo, T in [("ind", ind_v), ("fus", fus_v)]:
              if len(T) == 0:
                  continue
              t0 = x["deputado_id"].map(T)
              meses = np.floor((x["dt"] - t0).dt.days / 30.44)
              n_pre = int((meses < 0).sum())
              num(f"ev{suf}_{nome}_{grupo}_n_pre", n_pre)
              if n_pre == 0:      # sem votos antes do evento: efeitos pós-evento não identificados
                  continue
              for lo, hi, rot in janelas:
                  if rot == ref:
                      continue
                  cols.append(((meses >= lo) & (meses <= hi)).fillna(False).astype(float).to_numpy())
                  nomes.append(f"{grupo}:{rot}")
          X = np.column_stack(cols)
          keep = X.sum(0) > 0
          X, nomes = X[:, keep], [n for n, k in zip(nomes, keep) if k]
          fe1 = pd.factorize(x["deputado_id"])[0]
          fe2 = pd.factorize(x["partido"] + "|" + x["idVotacao"])[0]
          if "ind" in [n_.split(":")[0] for n_ in nomes]:
              t0r = x["deputado_id"].map(ind_v)
              mr = np.floor((x["dt"] - t0r).dt.days / 30.44)
              num(f"ev{suf}_{nome}_desvio_ref", float(x.loc[(mr >= -12) & (mr <= -7), "desvio"].mean()))
          for nm_, col in zip(nomes, X.T):
              num(f"ev{suf}_{nome}_{nm_}_nvotos", int(col.sum()))
              num(f"ev{suf}_{nome}_{nm_}_ndep", int(x.loc[col > 0, "deputado_id"].nunique()))
          tab, V, _ = ols_fe(x["desvio"].to_numpy(float), X, [fe1, fe2],
                             (fe1, pd.factorize(x["idVotacao"])[0]), nomes)
          for nm_ in nomes:
              num(f"ev{suf}_{nome}_{nm_}_identificado", nm_ in tab.index)
          # teste conjunto de pré-tendência (coeficientes anteriores à troca individual = 0)
          pre = [k for k, nm_ in enumerate(tab.index) if nm_ in ("ind:≤−13", "ind:−6 a −4", "ind:−3 a −1")]
          if pre:
              w, gl, pv = wald(tab["coef"].to_numpy(), V, pre)
              num(f"ev{suf}_{nome}_pre_wald", w); num(f"ev{suf}_{nome}_pre_gl", gl); num(f"ev{suf}_{nome}_pre_p", pv)
          for k, r in tab.iterrows():
              for c in ["coef", "lo", "hi"]:
                  num(f"ev{suf}_{nome}_{k}_{c}", r[c], 5)
              # versão negada (queda do desvio), com o IC invertido
              num(f"ev{suf}_{nome}_{k}_negcoef", -r["coef"], 5)
              num(f"ev{suf}_{nome}_{k}_neglo", -r["hi"], 5)
              num(f"ev{suf}_{nome}_{k}_neghi", -r["lo"], 5)
          if not suf:
              res[nome] = tab
    num("ev_U_subida_pre", R["ev_U_ind:−3 a −1_coef"] - R["ev_U_ind:≤−13_coef"])
    num("ev_n_trocadores_ind", int(ind.index.isin(base["u"]["deputado_id"]).sum()))
    num("ev_n_fusao", int(fus.index.isin(base["u"]["deputado_id"]).sum()))
    num("ev_n_fusao_D", int(fus.index.isin(base["d"]["deputado_id"]).sum()))
    num("ev_n_mais_de_uma_troca", int((tr[~tr["fusao"]].groupby("deputado_id").size() > 1).sum()))
    for o, d_ in [("PSC", "PODE"), ("PATRIOTA", "PRD")]:
        dd = tr[(tr["origem"] == o) & (tr["destino"] == d_)]["data"]
        num(f"fusao_data_{o}", dd.min().strftime("%Y-%m-%d") if len(dd) else None)
    return res, janelas


def selecao_troca(X):
    """Seleção ou influência? Para quem trocou de partido individualmente e tem pontos (dim1 global,
    >= 30 votos) nos dois partidos: o destino estava mais perto da posição anterior do deputado do
    que a origem? E quanto a posição do deputado mudou entre os dois períodos?"""
    tr = trocas_partido()
    tr = tr[~tr["fusao"]].drop_duplicates("deputado_id")
    Xc = X[X["n_votos"] >= 30]
    med = Xc.groupby("partido")["dim1"].median()
    sd = Xc.groupby("partido")["dim1"].std()
    pts = Xc.set_index(["deputado_id", "partido"])["dim1"]
    linhas = []
    for _, r in tr.iterrows():
        k0, k1 = (r["deputado_id"], r["origem"]), (r["deputado_id"], r["destino"])
        if k0 in pts.index and k1 in pts.index and r["destino"] in med.index:
            x0, x1 = pts[k0], pts[k1]
            dirv = np.sign(med[r["destino"]] - med[r["origem"]])
            linhas.append((abs(x0 - med[r["destino"]]) < abs(x0 - med[r["origem"]]), abs(x1 - x0),
                           abs(med[r["destino"]] - med[r["origem"]]),
                           np.sign(x0 - med[r["origem"]]) == dirv,      # já do lado do destino (seleção)
                           np.sign(x1 - x0) == dirv,                    # moveu-se rumo ao destino (ajuste)
                           (x1 - x0) * dirv))
    t = pd.DataFrame(linhas, columns=["destino_mais_perto", "mudanca_pos", "dist_medianas",
                                      "lado_destino", "moveu_rumo_destino", "mov_dir"])
    num("sel_lado_destino", t["lado_destino"].mean())
    num("sel_moveu_rumo_destino", t["moveu_rumo_destino"].mean())
    num("sel_mov_dir_mediana", float(t["mov_dir"].median()))
    num("sel_n", len(t)); num("sel_destino_mais_perto", t["destino_mais_perto"].mean())
    num("sel_mudanca_pos_mediana", float(t["mudanca_pos"].median()))
    num("sel_dist_medianas_mediana", float(t["dist_medianas"].median()))
    num("sel_sd_tipico_partido", float(sd.median()))
    return t


def antes_depois_troca(d):
    """Descritivo (apêndice): disciplina com o partido antigo vs. o novo, sem controles."""
    t = d.groupby(["deputado_id", "partido"]).agg(n=("seguiu", "size"), taxa=("seguiu", "mean"),
                                                  ini=("data", "min")).reset_index()
    t = t[t["n"] >= 30]
    multi = t.groupby("deputado_id").filter(lambda s: len(s) >= 2).sort_values(["deputado_id", "ini"])
    pares = multi.groupby("deputado_id").agg(antes=("taxa", "first"), depois=("taxa", "last"))
    num("troca_bruto_n", len(pares))
    num("troca_bruto_antes", pares["antes"].mean()); num("troca_bruto_depois", pares["depois"].mean())
    return pares


# ============================================= dispersão, pivôs, dissidentes (IRT global)
def _job_boot(arg):
    b, idx = arg
    A = _A
    # reamostra votações com reposição: cada cópia vira uma nova coluna j
    sel = np.concatenate([A["por_votacao"][k] for k in idx])
    novo_j = np.concatenate([np.full(len(A["por_votacao"][k]), r) for r, k in enumerate(idx)])
    B = dict(A)
    B.update(i=A["i"][sel], j=novo_j, y=A["y"][sel], grp=A["grp"][sel], n_j=len(idx), df=A["df"].iloc[sel])
    f = ajustar(B, np.ones(len(sel), bool), "global", seed=SEMENTE + 1000 + b)
    return b, f["u"], f["x"]


def bootstrap_global(A, f_full, B=100, procs=4):
    """Bootstrap de votações (com reposição) com reajuste do IRT global e alinhamento de
    Procrustes (rotação+reflexão) dos pontos de cada réplica aos do ajuste completo."""
    from scipy.linalg import orthogonal_procrustes
    global _A
    A["por_votacao"] = [np.flatnonzero(A["j"] == k) for k in range(A["n_j"])]
    _A = A
    rng = np.random.default_rng(SEMENTE)
    jobs = [(b, rng.integers(0, A["n_j"], A["n_j"])) for b in range(B)]

    def rodar():
        import multiprocessing as mp
        with mp.get_context("fork").Pool(procs) as pool:
            return pool.map(_job_boot, jobs, chunksize=1)
    out = em_cache(f"boot_global_B{B}", rodar)
    ref_u, ref_x = f_full["u_rot"], f_full["x_rot"]
    mu_u = f_full["u"].mean(0)
    Us, Xs = [], []
    for b, u, x in out:
        uc = u - u.mean(0)
        Rm, _ = orthogonal_procrustes(uc, ref_u)
        Us.append(uc @ Rm); Xs.append((x - u.mean(0)) @ Rm)
    return np.stack(Us), np.stack(Xs)


def dispersao_pivos(A, base_p, dep, per):
    m = np.ones(len(A["y"]), bool)
    f = em_cache("global_full", ajustar, A, m, "global")
    U, X = orientar(A, f)
    f["u_rot"], f["x_rot"] = U[["dim1", "dim2"]].to_numpy(), X[["dim1", "dim2"]].to_numpy()
    nomes = dep.set_index("id")["nome"]
    X["nome"] = X["deputado_id"].map(nomes)
    U["nome"] = U["deputado_id"].map(nomes)
    # conferência com emb_votos do repositório (que inclui comissões)
    ev = pd.read_parquet(DADOS / "embeddings" / "emb_votos.parquet")
    ev["deputado_id"] = ev["deputado_id"].astype(int)
    mm = U.merge(ev[["deputado_id", "dim1"]], on="deputado_id", suffixes=("", "_repo"))
    num("conf_corr_dim1_repo", np.corrcoef(mm["dim1"], mm["dim1_repo"])[0, 1])
    # dispersão por partido: períodos com >= 100 votos
    Xc = X[X["n_votos"] >= 100]
    disp = Xc.groupby("partido")["dim1"].agg(["std", "size"])
    disp["iqr"] = Xc.groupby("partido")["dim1"].quantile(0.75) - Xc.groupby("partido")["dim1"].quantile(0.25)
    disp = disp[disp["size"] >= 5]
    for pt_, r in disp.iterrows():
        num(f"disp_{pt_}", r["std"], 3); num(f"disp_iqr_{pt_}", r["iqr"], 3); num(f"disp_n_{pt_}", int(r["size"]))
    # o mesmo cálculo com os pontos do repositório (por deputado, partido atual NÃO: partido modal na legislatura)
    pm = base_p.groupby(["deputado_id", "partido"]).size().reset_index().sort_values(0)
    pm = pm.drop_duplicates("deputado_id", keep="last").set_index("deputado_id")["partido"]
    ev["partido"] = ev["deputado_id"].map(pm)
    evc = ev[ev["n_votos"] >= 100]
    for pt_ in ["PDT", "PT", "PSOL", "PL", "MDB", "PODE"]:
        num(f"disp_repo_{pt_}", evc.loc[evc["partido"] == pt_, "dim1"].std(), 3)
    # reprodução exata dos números prévios do projeto: emb_votos (Plenário + comissões), deputados
    # com >= 50 votos, agrupados pelo partido ATUAL (deputados.siglaPartido, pós-janela de 2026)
    evp = ev[ev["confiavel"]].copy()
    medp_ = evp["dim1"].median()
    evp["dmed"] = (evp["dim1"] - medp_).abs()
    num("prev_pivos", ", ".join(evp.nsmallest(5, "dmed")["nome"]))
    plp = evp[evp["siglaPartido"] == "PL"].copy()
    plp["rel"] = plp["dim1"] - plp["dim1"].median()
    num("prev_diss_pl", ", ".join(plp.nlargest(3, "rel")["nome"]))
    al = pd.read_parquet(DADOS / "embeddings" / "alinhamento.parquet").merge(
        ev[["deputado_id", "siglaPartido", "confiavel"]], on="deputado_id")
    al = al[al["confiavel"]]
    ap = al.groupby("siglaPartido")["taxa_alinhamento_partido"].mean()
    for pt_ in ["PT", "PSOL", "NOVO", "UNIÃO", "PP", "PSD", "MDB", "REPUBLICANOS"]:
        num(f"prev_alinh_{pt_}", ap.get(pt_))
    for pt_ in ["PDT", "PT", "PSOL", "PL", "MDB", "PODE"]:
        num(f"disp_prev_{pt_}", evp.loc[evp["siglaPartido"] == pt_, "dim1"].std(), 2)
    # posição, entre os mais próximos da mediana (>= 100 votos), dos pivôs citados antes no projeto
    Uc0 = U[U["n_votos"] >= 100].copy()
    Uc0["d"] = (Uc0["dim1"] - Uc0["dim1"].median()).abs()
    Uc0 = Uc0.sort_values("d").reset_index(drop=True)
    for nm_ in ["Luiz Carlos Hauly", "João Leão", "Luiz Gastão", "José Rocha", "Marx Beltrão"]:
        k = Uc0.index[Uc0["nome"] == nm_]
        num(f"pivo_prev_rank_{nm_}", int(k[0]) + 1 if len(k) else None)
    for nm_ in ["Bosco Costa", "Henrique Júnior", "Daniel José"]:
        num(f"diss_prev_nvotos_{nm_}", int(X.loc[X["nome"] == nm_, "n_votos"].sum()))
    # bootstrap
    Bn = 20 if ARGS and ARGS.rapido else 100
    Ub, Xb = bootstrap_global(A, f, B=Bn)
    num("boot_B_global", Bn)
    Xb1 = Xb[:, :, 0]
    sel = (X["n_votos"] >= 100).to_numpy()
    sds = []
    for pt_ in disp.index:
        mk = sel & (X["partido"] == pt_).to_numpy()
        s = Xb1[:, mk].std(axis=1, ddof=1)
        est = disp.loc[pt_, "std"]
        # IC bootstrap básico (2θ − quantis): corrige o deslocamento para cima da reamostragem
        lo_, hi_ = max(0.0, 2 * est - np.percentile(s, 97.5)), 2 * est - np.percentile(s, 2.5)
        sds.append((pt_, lo_, hi_, np.mean(s) - est, np.std(s, ddof=1)))
        num(f"disp_ep_{pt_}", np.std(s, ddof=1), 3)
        num(f"disp_lo_{pt_}", lo_, 3); num(f"disp_hi_{pt_}", hi_, 3); num(f"disp_vies_{pt_}", np.mean(s) - est, 3)
    disp = disp.join(pd.DataFrame(sds, columns=["partido", "lo", "hi", "vies", "ep"]).set_index("partido"))
    num("disp_vies_mediano", float(disp["vies"].median()))
    # mediana do plenário na legislatura: deputados com >= 100 votos, 5 mais próximos
    Uc = U[U["n_votos"] >= 100].copy()
    med = Uc["dim1"].median()
    Uc["dist_med"] = (Uc["dim1"] - med).abs()
    top = Uc.nsmallest(5, "dist_med")
    num("pivos_mediana_legislatura", ", ".join(top["nome"]))
    selU = (U["n_votos"] >= 100).to_numpy()
    cont = np.zeros(len(U))
    for b in range(Ub.shape[0]):
        d1 = Ub[b, :, 0]
        mb = np.median(d1[selU])
        dd = np.where(selU, np.abs(d1 - mb), np.inf)
        cont[np.argsort(dd)[:5]] += 1
    U["p_top5_mediana"] = cont / Ub.shape[0]
    tp = U.sort_values("p_top5_mediana", ascending=False).head(8)
    num("pivos_boot_max", float(tp["p_top5_mediana"].max()))
    num("pivos_boot_top", "; ".join(f"{n} ({pct(q, 0)}%)" for n, q in zip(tp["nome"], tp["p_top5_mediana"])))
    # pivôs por semestre entre os deputados em exercício na data de referência
    filiacao = pd.read_parquet(DADOS / "deputados_partidos.parquet")
    filiacao["ini"] = pd.to_datetime(filiacao["dataInicio"]); filiacao["fim"] = pd.to_datetime(filiacao["dataFim"]).fillna(pd.Timestamp("2027-02-01"))
    pts = X.set_index("periodo")
    linhas = []
    for sem, dt in [("2023S1", "2023-05-15"), ("2023S2", "2023-10-15"), ("2024S1", "2024-05-15"),
                    ("2024S2", "2024-10-15"), ("2025S1", "2025-05-15"), ("2025S2", "2025-10-15"),
                    ("2026S1", "2026-05-15"), ("2026S2", "2026-09-15")]:
        dt = pd.Timestamp(dt)
        em = per[(per["inicio"] <= dt) & (per["fim"] > dt)]["deputado_id"].unique()
        fi = filiacao[(filiacao["ini"] <= dt) & (filiacao["fim"] > dt) & filiacao["id"].isin(em)]
        chaves = fi["id"].astype(str) + "|" + fi["siglaPartido"]
        pp = pts.reindex(chaves).dropna(subset=["dim1"])
        pp = pp[pp["n_votos"] >= 30].sort_values("dim1")
        n = len(pp)
        k_med, k_40, k_60 = n // 2, int(round(0.4 * n)), int(round(0.6 * n))
        linhas.append(dict(semestre=sem, n_em_exercicio=len(em), n_com_ponto=n,
                           mediana=f"{pp['nome'].iloc[k_med]} ({pp['partido'].iloc[k_med]})",
                           pivo_40=f"{pp['nome'].iloc[k_40]} ({pp['partido'].iloc[k_40]})",
                           pivo_60=f"{pp['nome'].iloc[k_60]} ({pp['partido'].iloc[k_60]})",
                           partido_mediana=pp["partido"].iloc[k_med]))
    piv = pd.DataFrame(linhas)
    for _, r in piv.iterrows():
        num(f"piv_{r['semestre']}_mediana", r["mediana"]); num(f"piv_{r['semestre']}_n", int(r["n_com_ponto"]))
        num(f"piv_{r['semestre']}_em_exercicio", int(r["n_em_exercicio"]))
    # dissidentes sistemáticos: posição relativa à mediana do partido (período >= 100 votos) com IC bootstrap
    medp = Xc.groupby("partido")["dim1"].median()
    X["rel"] = X["dim1"] - X["partido"].map(medp)
    rel_b = Xb1 - np.stack([pd.Series(Xb1[b][sel]).groupby(X["partido"].to_numpy()[sel]).median()
                            .reindex(X["partido"]).to_numpy() for b in range(Xb1.shape[0])])
    X["rel_lo"] = np.percentile(rel_b, 2.5, axis=0); X["rel_hi"] = np.percentile(rel_b, 97.5, axis=0)
    X["sd_partido"] = X["partido"].map(disp["std"])
    X["rel_z"] = X["rel"] / X["sd_partido"]
    diss = X[(X["n_votos"] >= 100) & X["partido"].isin(disp.index) & ((X["rel_lo"] > 0) | (X["rel_hi"] < 0))]
    atual = dep.set_index("id")["siglaPartido"]
    pl = X[(X["partido"] == "PL") & (X["n_votos"] >= 100)].copy()
    pl["saiu"] = pl["deputado_id"].map(atual) != "PL"
    gov_pl = pl[pl["rel_z"] > 1]
    num("pl_gov_n", len(gov_pl)); num("pl_gov_saiu", int(gov_pl["saiu"].sum()))
    num("pl_resto_share_saiu", pl.loc[pl["rel_z"] <= 1, "saiu"].mean())
    num("pl_gov_share_saiu", gov_pl["saiu"].mean())
    num("diss_n_ic_exclui_0", len(diss)); num("diss_n_elegiveis", int(((X["n_votos"] >= 100) & X["partido"].isin(disp.index)).sum()))
    num("diss_n_z2", int((diss["rel_z"].abs() >= 2).sum()))
    return dict(f=f, U=U, X=X, disp=disp, piv=piv, Ub=Ub, Xb=Xb)


def tabela_dissidentes(X, k=6):
    """Os deputados mais distantes da mediana do partido em cada sentido (IC exclui 0)."""
    x = X[(X["n_votos"] >= 100) & X["sd_partido"].notna() & ((X["rel_lo"] > 0) | (X["rel_hi"] < 0))
          & (X["rel_z"].abs() >= 2)].copy()
    gov = x.nlargest(k, "rel_z")
    opo = x.nsmallest(k, "rel_z")
    linhas = []
    for lado, t in [("mais governista que o partido", gov), ("mais oposicionista que o partido", opo)]:
        for _, r in t.iterrows():
            linhas.append({"Sentido": lado, "Deputado": r["nome"], "Partido": r["partido"],
                           "Votos": int(r["n_votos"]), "Posição relativa (DP do partido)": br(r["rel_z"], 1),
                           "IC 95% (DP do partido)": f"[{br(r['rel_lo'] / r['sd_partido'], 1)}; {br(r['rel_hi'] / r['sd_partido'], 1)}]"})
    for i, (_, r) in enumerate(gov.iterrows()):
        num(f"diss_gov_{i}", f"{r['nome']} ({r['partido']})")
    for i, (_, r) in enumerate(opo.iterrows()):
        num(f"diss_opo_{i}", f"{r['nome']} ({r['partido']})")
    return pd.DataFrame(linhas)


# ================================================== dimensões intrapartidárias (P2)
def frentes_membros(nomes_regex):
    fr = pd.read_parquet(DADOS / "frentes.parquet")
    fd = pd.read_parquet(DADOS / "frentes_deputados.parquet")
    out = {}
    for rot, rx in nomes_regex.items():
        ids = fr.loc[fr["titulo"].str.contains(rx, case=False, regex=True, na=False), "id"]
        out[rot] = set(fd.loc[fd["idFrente"].isin(ids), "deputado_id"].astype(int))
    return out


def interpretar_intra(A, vt, dep, glob, temas_vt):
    """Ajuste intrapartidário completo (1D e 2D), cargas das votações, correlatos externos e
    validação preditiva (troca de partido na janela de 2026)."""
    m = np.ones(len(A["y"]), bool)
    out = {}
    for nd in (1, 2):
        f = em_cache(f"intra_full_{nd}d", ajustar, A, m, "intra", ndim=nd)
        f["intra"] = True
        U, X = orientar(A, f)
        out[nd] = (f, U, X)
    f1, U1, X1 = out[1]
    # carga das votações na dim1 intra (sinal coerente com a orientação de x)
    sgn = np.sign(np.corrcoef(f1["x"][:, 0], X1["dim1"])[0, 1])
    b = f1["b"][:, 0] * sgn
    vv = pd.DataFrame({"idVotacao": A["votacoes"], "carga": b})
    info = vt.set_index("idVotacao")
    vv["descricao"] = vv["idVotacao"].map(info["descricao"])
    vv["proposicao"] = vv["idVotacao"].map(info["proposicao_titulo"])
    vv["ementa"] = vv["idVotacao"].map(info["proposicao_ementa"])
    vv["aprovada"] = pd.to_numeric(vv["idVotacao"].map(info["aprovacao"]), errors="coerce")
    dl = vv["descricao"].str.lower()
    vv.loc[vv["aprovada"].isna() & dl.str.startswith(("mantido", "mantida", "mantidos")), "aprovada"] = 2
    vv.loc[vv["aprovada"].isna() & dl.str.startswith(("suprimido", "suprimida")), "aprovada"] = 3
    vv["data"] = vv["idVotacao"].map(info["data"])
    vv["tipo"] = vv["descricao"].map(classificar_votacao)
    og = A["df"].drop_duplicates("idVotacao").set_index("idVotacao")
    for c in ["orientacao_governo", "orientacao_oposicao", "orientacao_maioria", "orientacao_minoria"]:
        vv[c] = vv["idVotacao"].map(og[c])
    # associação da carga com a orientação do Governo: carga > 0 => os mais "governistas relativos"
    # votam Sim; se a dim1 intra é governismo, carga e orientação do Governo têm o mesmo sinal
    for c in ["orientacao_governo", "orientacao_oposicao"]:
        s = vv[c].map({"Sim": 1, "Não": -1, "Obstrução": -1})
        ok = s.notna()
        num(f"intra1_corr_carga_{c}", np.corrcoef(vv.loc[ok, "carga"], s[ok])[0, 1])
        top = vv[ok].reindex(vv[ok]["carga"].abs().sort_values(ascending=False).index).head(100)
        num(f"intra1_top100_concorda_{c}", (np.sign(top["carga"]) == s[top.index]).mean())
    num("intra1_share_gov_orientou", vv["orientacao_governo"].isin(["Sim", "Não", "Obstrução"]).mean())
    # dim2 (modelo 2D): mesma leitura
    f2, U2, X2 = out[2]
    _, vt2 = ED.rotacionar(np.stack([np.bincount(A["base"], f2["x"][:, k], len(A["deps"])) for k in range(2)], 1)
                           / np.bincount(A["base"], minlength=len(A["deps"]))[:, None])
    b2 = f2["b"] @ vt2.T
    for k in range(2):
        s = vv["orientacao_governo"].map({"Sim": 1, "Não": -1, "Obstrução": -1})
        ok = s.notna()
        num(f"intra2_dim{k + 1}_abscorr_carga_gov", abs(np.corrcoef(b2[ok.to_numpy(), k], s[ok])[0, 1]))
    num("intra2_corr_dim1_1d", abs(np.corrcoef(U2["dim1"], U1["dim1"])[0, 1]))
    # temas das votações de maior carga (top 100 por |carga|) vs. todas
    tv = temas_vt.groupby("idVotacao").apply(lambda s: s.loc[s["peso"].idxmax(), "tema"], include_groups=False)
    vv["tema"] = vv["idVotacao"].map(tv)
    vv["abs"] = vv["carga"].abs()
    top = vv.nlargest(100, "abs")
    comp = pd.DataFrame({"top100": top["tipo"].value_counts(normalize=True),
                         "todas": vv["tipo"].value_counts(normalize=True)}).fillna(0)
    for k, r in comp.iterrows():
        num(f"intra1_tipo_top100_{k}", r["top100"]); num(f"intra1_tipo_todas_{k}", r["todas"])
    compt = pd.DataFrame({"top100": top["tema"].value_counts(normalize=True),
                          "todas": vv["tema"].value_counts(normalize=True)}).fillna(0)
    compt["razao"] = compt["top100"] / compt["todas"]
    # correlatos externos (dentro do partido): posição relativa global, alinhamento ao Governo, frentes
    nomes = dep.set_index("id")["nome"]
    Xg = glob["X"].set_index("periodo")
    Xi = X1.set_index("periodo").join(Xg[["rel"]], how="left")
    Xi = Xi[Xi["n_votos"] >= 100]
    num("intra1_corr_rel_global", np.corrcoef(Xi["dim1"], Xi["rel"])[0, 1])
    df = A["df"]
    gov = df.assign(s=(df["vd"] == df["gd"]).astype(float).where(df["gd"].notna())).groupby("periodo")["s"].mean()
    Xi["gov"] = gov.reindex(Xi.index)
    Xi["gov_rel"] = Xi["gov"] - Xi.groupby("partido")["gov"].transform("mean")
    num("intra1_corr_gov_rel", np.corrcoef(Xi["dim1"], Xi["gov_rel"])[0, 1])
    fr = frentes_membros({"agropecuaria": r"agropecu", "evangelica": r"evang[eé]lic",
                          "seguranca": r"seguran[cç]a p[uú]blica", "ambientalista": r"ambientalista"})
    linhas = []
    for rot, ids in fr.items():
        z = Xi["deputado_id"].isin(ids).astype(float)
        zc = z - z.groupby(Xi["partido"]).transform("mean")
        for k, X_ in [(1, Xi["dim1"])]:
            c = np.corrcoef(X_ - X_.groupby(Xi["partido"]).transform("mean"), zc)[0, 1] if zc.std() > 0 else np.nan
            num(f"intra1_corr_frente_{rot}", c)
            linhas.append((rot, len(ids), c))
    # 2D: dim2 intra vs frentes
    Xi2 = X2.set_index("periodo")
    Xi2 = Xi2[Xi2["n_votos"] >= 100]
    for rot, ids in fr.items():
        z = Xi2["deputado_id"].isin(ids).astype(float)
        zc = z - z.groupby(Xi2["partido"]).transform("mean")
        c = np.corrcoef(Xi2["dim2"], zc)[0, 1] if zc.std() > 0 else np.nan
        num(f"intra2_dim2_corr_frente_{rot}", c)
        R["intra2_dim2_max_abs_frente"] = max(R.get("intra2_dim2_max_abs_frente", 0), round(abs(c), 6))
    # validação preditiva: posição intra antes de 2026 prevê troca na janela e a direção
    pre = (A["df"]["dt"] < "2026-01-01").to_numpy()
    fpre = em_cache("intra_pre2026_1d", ajustar, A, pre, "intra", ndim=1)
    fpre["intra"] = True
    Upre, Xpre = orientar(A, fpre, mask=pre)
    fgp = em_cache("global_pre2026", ajustar, A, pre, "global")
    Ugp, Xgp = orientar(A, fgp, mask=pre)
    med_part = Xgp[Xgp["n_votos"] >= 30].groupby("partido")["dim1"].median()
    tr = trocas_partido()
    jan = tr[(~tr["fusao"]) & (tr["data"] >= "2026-03-01") & (tr["data"] < "2026-06-01")].drop_duplicates("deputado_id")
    # partido de origem = partido do último período antes de 2026 com >= 100 votos
    Xp = Xpre[Xpre["n_votos"] >= 100].copy()
    ult = A["df"][pre].groupby("periodo")["dt"].max()
    Xp["ult"] = Xp["periodo"].map(ult)
    Xp = Xp.sort_values("ult").drop_duplicates("deputado_id", keep="last")
    Xp = Xp[Xp["ult"] >= "2025-07-01"]       # ainda ativos no 2º semestre de 2025
    Xp["trocou"] = Xp["deputado_id"].isin(jan["deputado_id"]).astype(int)
    Xp = Xp.merge(jan[["deputado_id", "origem", "destino"]], on="deputado_id", how="left")
    from sklearn.metrics import roc_auc_score
    num("pred_n", len(Xp)); num("pred_n_trocaram", int(Xp["trocou"].sum()))
    auc = roc_auc_score(Xp["trocou"], Xp["dim1"].abs())
    rng = np.random.default_rng(SEMENTE)
    bs = []
    for _ in range(1000):
        s = Xp.sample(len(Xp), replace=True, random_state=int(rng.integers(1e9)))
        if s["trocou"].nunique() == 2:
            bs.append(roc_auc_score(s["trocou"], s["dim1"].abs()))
    num("pred_auc_abs", auc); num("pred_auc_abs_lo", np.percentile(bs, 2.5)); num("pred_auc_abs_hi", np.percentile(bs, 97.5))
    t = Xp[(Xp["trocou"] == 1) & (Xp["origem"] == Xp["partido"])].copy()
    t["dir_destino"] = t["destino"].map(med_part) - t["origem"].map(med_part)
    t = t.dropna(subset=["dir_destino"])
    t = t[t["dir_destino"].abs() > 0.05]
    acerto = (np.sign(t["dim1"]) == np.sign(t["dir_destino"])).mean()
    from scipy.stats import binomtest
    num("pred_dir_n", len(t)); num("pred_dir_acerto", acerto)
    num("pred_dir_p", binomtest(int((np.sign(t["dim1"]) == np.sign(t["dir_destino"])).sum()), len(t)).pvalue)
    num("pred_dir_corr", np.corrcoef(t["dim1"], t["dir_destino"])[0, 1])
    # global também (comparação): posição relativa global pré-2026 prevê a direção?
    Xgp_ = Xgp[Xgp["n_votos"] >= 100].copy()
    Xgp_["rel"] = Xgp_["dim1"] - Xgp_["partido"].map(med_part)
    t2 = t.merge(Xgp_[["periodo", "rel"]], on="periodo", how="left").dropna(subset=["rel"])
    num("pred_dir_global_acerto", (np.sign(t2["rel"]) == np.sign(t2["dir_destino"])).mean())
    return dict(vv=vv, comp=comp, compt=compt, U1=U1, X1=X1, U2=U2, X2=X2, Xi=Xi, pred=Xp, dirs=t)


def tabela_cargas(vv, k=8):
    linhas = []
    for lado, t in [("+ (governistas relativos votam Sim)", vv.nlargest(k, "carga")),
                    ("− (governistas relativos votam Não)", vv.nsmallest(k, "carga"))]:
        for _, r in t.iterrows():
            d = re.sub(r"\s+", " ", str(r["ementa"]))
            d = d if len(d) <= 120 else d[:117] + "..."
            linhas.append({"Sinal": lado, "Data": str(r["data"])[:10], "Proposição": str(r["proposicao"]).split(",")[0],
                           "Tipo": r["tipo"], "Ementa": d, "Gov.": r["orientacao_governo"] or "–",
                           "Resultado": {1: "aprovada", 0: "rejeitada", 2: "texto mantido", 3: "texto suprimido"}.get(r["aprovada"], "–"),
                           "Carga": br(r["carga"], 2)})
    return pd.DataFrame(linhas)


# ===================================================== P5: partido x Governo divergentes
def partido_vs_governo(base, cvP, A, dep, per, dist, camadas=("própria", "bloco", "bloco inferido"), sufixo=""):
    p = base["p"]
    x = p[p["camada"].isin(camadas) & p["od"].notna() & p["gd"].notna() & (p["od"] != p["gd"])].copy()
    x["segue_partido"] = (x["vd"] == x["od"]).astype(float)
    x["segue_governo"] = (x["vd"] == x["gd"]).astype(float)
    x["base_gov"] = x["partido"].isin(BASE_MINISTERIAL)
    num(f"div_indep_n{sufixo}", int((~x["partido"].isin(BASE_MINISTERIAL + OPOSICAO)).sum()))
    xi = x[~x["partido"].isin(BASE_MINISTERIAL + OPOSICAO)]
    num(f"div_indep_segue_partido{sufixo}", xi["segue_partido"].mean())
    num(f"div_n_votos{sufixo}", len(x)); num(f"div_n_votacoes{sufixo}", x["idVotacao"].nunique())
    for rot, s in [("base", x[x["base_gov"]]), ("oposicao", x[x["partido"].isin(OPOSICAO)])]:
        num(f"div_{rot}_n{sufixo}", len(s))
        num(f"div_{rot}_segue_partido{sufixo}", s["segue_partido"].mean())
        num(f"div_{rot}_segue_governo{sufixo}", s["segue_governo"].mean())
    # robustez: base datada (PP e REPUBLICANOS a partir de 13/09/2023; UNIÃO e PP fora a partir de 02/09/2025)
    dat = x["base_gov"] & ~((x["partido"].isin(["PP", "REPUBLICANOS"])) & (x["dt"] < "2023-09-13")) \
        & ~((x["partido"].isin(["UNIÃO", "PP"])) & (x["dt"] >= "2025-09-02"))
    num(f"div_base_datada_n{sufixo}", int(dat.sum())); num(f"div_base_datada_segue_partido{sufixo}", x.loc[dat, "segue_partido"].mean())
    xb = x[x["base_gov"]]
    c = xb["partido"].value_counts()
    ps = [q for q in ORDEM_PARTIDOS if c.get(q, 0) >= 300]
    t = xb.groupby("partido").agg(n=("segue_partido", "size"), votacoes=("idVotacao", "nunique"),
                                  partido_=("segue_partido", "mean"), governo=("segue_governo", "mean")).loc[ps]
    ic = ic_partidos(xb, "segue_partido", ps, seed=SEMENTE + 7)
    t["lo"], t["hi"] = ic["lo"], ic["hi"]
    for q, r in t.iterrows():
        num(f"div_{q}_votacoes{sufixo}", int(r["votacoes"])); num(f"div_{q}_lo{sufixo}", r["lo"]); num(f"div_{q}_hi{sufixo}", r["hi"])
    for q, r in t.iterrows():
        num(f"div_{q}_segue_partido{sufixo}", r["partido_"]); num(f"div_{q}_n{sufixo}", int(r["n"]))
    if sufixo:
        return x, t
    for k, s in xb.groupby("camada"):
        num(f"div_base_camada_{k}_segue_partido", s["segue_partido"].mean()); num(f"div_base_camada_{k}_n", len(s))
    for q in ["PSB", "PDT"]:
        s = xb[xb["partido"] == q]
        num(f"div_{q}_share_inferido", (s["camada"] == "bloco inferido").mean())
        num(f"div_{q}_propria_segue_partido", s.loc[s["camada"] == "própria", "segue_partido"].mean())
        num(f"div_{q}_propria_n", int((s["camada"] == "própria").sum()))
        num(f"div_{q}_inferido_segue_partido", s.loc[s["camada"] == "bloco inferido", "segue_partido"].mean())
    for k, s in xb.groupby("tipo_votacao"):
        num(f"div_base_tipo_{k}_segue_partido", s["segue_partido"].mean())
    # quem a orientação 'Liberado' deixa seguir o Governo
    lib = p[(p["orientacao_partido"] == "Liberado") & p["gd"].notna() & p["vd"].notna() & ~p["partido"].isin(OPOSICAO)]
    num("liberado_base_segue_governo", (lib["vd"] == lib["gd"]).mean()); num("liberado_base_n", len(lib))
    # linha de base contrafactual: previsão fora da amostra do M5 (global, sem partido)
    key = A["df"]["idVotacao"] + "|" + A["df"]["deputado_id"].astype(str)
    p5 = pd.Series(cvP["M5"], index=key)
    xb = xb.assign(k=xb["idVotacao"] + "|" + xb["deputado_id"].astype(str))
    xb["p_sim"] = xb["k"].map(p5)
    z = xb.dropna(subset=["p_sim"])
    z["p_partido"] = np.where(z["od"] == 1, z["p_sim"], 1 - z["p_sim"])
    num("div_cf_n", len(z))
    num("div_cf_observado", z["segue_partido"].mean())
    num("div_cf_previsto", z["p_partido"].mean())
    num("div_cf_excesso", z["segue_partido"].mean() - z["p_partido"].mean())
    exc = (z.groupby("idVotacao")["segue_partido"].sum() - z.groupby("idVotacao")["p_partido"].sum())
    nn = z.groupby("idVotacao").size()
    lo, hi = boot_razao(exc.to_numpy()[:, None], nn.to_numpy()[:, None].astype(float))
    num("div_cf_excesso_lo", lo[0]); num("div_cf_excesso_hi", hi[0])
    cf = z.groupby("partido").agg(obs=("segue_partido", "mean"), prev=("p_partido", "mean"), n=("k", "size"))
    cf = cf[cf["n"] >= 300]
    for q, r in cf.iterrows():
        num(f"div_cf_{q}_obs", r["obs"]); num(f"div_cf_{q}_prev", r["prev"])
    # robustez: M5 reestimado sem os votos dos partidos da base nas células divergentes
    # (as cargas das votações vêm dos demais deputados; os pontos, das outras votações)
    cel_div = set(xb["partido"] + "|" + xb["idVotacao"])
    chave_cel = (A["df"]["partido"] + "|" + A["df"]["idVotacao"]).to_numpy()
    fora = np.isin(chave_cel, list(cel_div))
    f_sd = em_cache("global_sem_divergentes", ajustar, A, ~fora, "global")
    p_sd = pd.Series(prever(f_sd, A, np.ones(len(A["y"]), bool), grupos=False), index=key)
    z["p_sim_sd"] = z["k"].map(p_sd)
    z["p_partido_sd"] = np.where(z["od"] == 1, z["p_sim_sd"], 1 - z["p_sim_sd"])
    num("div_cf_previsto_sd", z["p_partido_sd"].mean())
    num("div_cf_excesso_sd", z["segue_partido"].mean() - z["p_partido_sd"].mean())
    exc = (z.groupby("idVotacao")["segue_partido"].sum() - z.groupby("idVotacao")["p_partido_sd"].sum())
    lo, hi = boot_razao(exc.to_numpy()[:, None], nn.to_numpy()[:, None].astype(float))
    num("div_cf_excesso_sd_lo", lo[0]); num("div_cf_excesso_sd_hi", hi[0])
    esq = ["PT", "PCdoB", "PSOL", "REDE", "PSB", "PDT"]
    zz = z[~z["partido"].isin(esq)]
    num("div_cf_excesso_sem_esq", zz["segue_partido"].mean() - zz["p_partido"].mean())
    num("div_cf_excesso_sd_sem_esq", zz["segue_partido"].mean() - zz["p_partido_sd"].mean())
    num("div_cf_n_sem_esq", len(zz))
    cf["prev_sd"] = z.groupby("partido")["p_partido_sd"].mean().reindex(cf.index)
    cf["excesso"] = cf["obs"] - cf["prev"]
    for q, r in cf.iterrows():
        num(f"div_cf_{q}_prev_sd", r["prev_sd"]); num(f"div_cf_{q}_excesso", r["excesso"])
    # quem segue o Governo contra o partido (mesma votação, mesmo partido)
    w = covariaveis_voto(xb, dep, per)
    w = anexar_distancia(w, dist)
    cov = ["sup_ministro", "sup_secretario", "sup_outro", "mulher", "idade10", "log_cadeiras_uf", "rel_gov_fora"]
    w = w.dropna(subset=cov).reset_index(drop=True)
    fe = pd.factorize(w["partido"] + "|" + w["idVotacao"])[0]
    tab, V, _ = ols_fe(w["segue_governo"].to_numpy(float), w[cov].to_numpy(float), [fe],
                       (pd.factorize(w["deputado_id"])[0], pd.factorize(w["idVotacao"])[0]), cov)
    for k, r in tab.iterrows():
        for cc in ["coef", "lo", "hi"]:
            num(f"div_reg_{k}_{cc}", r[cc], 5)
    num("div_reg_n", len(w))
    return x, t, cf, tab


# ============================================================================ robustez
def robustez(v, base):
    p = base["p"]
    ps = base["ps"]
    linhas = []
    variantes = {
        "Principal (direcional; própria + bloco + inferido)": amostra_D(p),
        "Sem orientações inferidas de bloco": amostra_D(p, camadas=("própria", "bloco")),
        "Só orientação própria (partido/federação)": amostra_D(p, camadas=("própria",)),
        "Incluindo o bloco heterogêneo (2025)": amostra_D(p, camadas=("própria", "bloco", "bloco inferido", "bloco heterogêneo")),
        "Sem fev.–out./2025": amostra_D(p[(p["dt"] < "2025-02-01") | (p["dt"] > "2025-10-31")]),
        "Estrita (Obstrução ≠ Não)": amostra_D(p, estrita=True),
        "Sem abstenções": amostra_D(p, sem_abst=True),
        "Plenário + comissões": amostra_D(v),
    }
    for nome, d in variantes.items():
        lin = {"Variante": nome, "Geral": d["seguiu"].mean(), "Cobertura": len(d) / (len(p) if "comissões" not in nome else len(v))}
        for q in ps:
            lin[q] = d.loc[d["partido"] == q, "seguiu"].mean()
        linhas.append(lin)
        num(f"rob_{nome}_geral", lin["Geral"])
    t = pd.DataFrame(linhas)
    from scipy.stats import spearmanr
    ref = t.iloc[0][ps].astype(float)
    for i in range(1, len(t)):
        r = spearmanr(ref, t.iloc[i][ps].astype(float), nan_policy="omit")[0]
        num(f"rob_spearman_{t.iloc[i]['Variante']}", r)
        t.loc[i, "ρ (ranking)"] = r
    t.loc[0, "ρ (ranking)"] = 1.0
    sem_inf = amostra_D(p, camadas=("própria", "bloco"))
    for q in ps:
        num(f"rob_seminf_{q}", sem_inf.loc[sem_inf["partido"] == q, "seguiu"].mean())
    return t


def ausencia_geral(p, per):
    """Limite inferior de D tratando como desvio toda ausência de membro em exercício do partido
    nas votações com orientação diretiva do partido (pior caso: ausência não ignorável)."""
    filiacao = pd.read_parquet(DADOS / "deputados_partidos.parquet")
    filiacao["ini"] = pd.to_datetime(filiacao["dataInicio"])
    filiacao["fim"] = pd.to_datetime(filiacao["dataFim"]).fillna(pd.Timestamp("2027-02-01"))
    bruto = pd.read_parquet(DADOS / "votos.parquet", columns=["idVotacao", "deputado_id", "voto"])
    presid = bruto[bruto["voto"] == "Artigo 17"].assign(deputado_id=lambda x: x["deputado_id"].astype(int)) \
        .groupby("idVotacao")["deputado_id"].apply(set)
    d = amostra_D(p)
    cont = d.groupby(["idVotacao", "partido"]).agg(seg=("seguiu", "sum"), pres=("seguiu", "size")).reset_index()
    datas = p.drop_duplicates("idVotacao").set_index("idVotacao")["dt"]
    aus = []
    for vid, s_ in cont.groupby("idVotacao"):
        dt = datas[vid]
        em = set(per[(per["inicio"] <= dt + pd.Timedelta(hours=23)) & (per["fim"] > dt)]["deputado_id"])
        fi = filiacao[(filiacao["ini"] <= dt + pd.Timedelta(hours=23)) & (filiacao["fim"] > dt) & filiacao["id"].isin(em)]
        pres = set(p.loc[p["idVotacao"] == vid, "deputado_id"]) | presid.get(vid, set())
        aus_p = fi[~fi["id"].isin(pres)].groupby("siglaPartido").size()
        for q in s_["partido"]:
            aus.append(int(aus_p.get(q, 0)))
    cont["aus"] = aus
    num("aus_D_presentes", cont["seg"].sum() / cont["pres"].sum())
    num("aus_D_limite_inferior", cont["seg"].sum() / (cont["pres"] + cont["aus"]).sum())
    num("aus_share_ausentes", cont["aus"].sum() / (cont["pres"] + cont["aus"]).sum())
    g = cont.groupby("partido")[["seg", "pres", "aus"]].sum()
    for q, r in g.iterrows():
        num(f"aus_D_li_{q}", r["seg"] / (r["pres"] + r["aus"]) if (r["pres"] + r["aus"]) else np.nan)
    from scipy.stats import spearmanr
    ps = principais_partidos(d)
    li = (g["seg"] / (g["pres"] + g["aus"])).reindex(ps)
    pr = (g["seg"] / g["pres"]).reindex(ps)
    num("aus_spearman_ranking", spearmanr(li, pr)[0])
    return cont


def ausencia_pec(p, per):
    """Sensibilidade: em PEC (mérito) com orientação Sim do partido, ausência entre os em
    exercício conta como desvio (quórum de 308)."""
    filiacao = pd.read_parquet(DADOS / "deputados_partidos.parquet")
    filiacao["ini"] = pd.to_datetime(filiacao["dataInicio"])
    filiacao["fim"] = pd.to_datetime(filiacao["dataFim"]).fillna(pd.Timestamp("2027-02-01"))
    pec = p[(p["tipo_votacao"] == "PEC (mérito)")]
    bruto = pd.read_parquet(DADOS / "votos.parquet", columns=["idVotacao", "deputado_id", "voto"])
    presid = bruto[bruto["voto"] == "Artigo 17"].assign(deputado_id=lambda x: x["deputado_id"].astype(int)) \
        .groupby("idVotacao")["deputado_id"].apply(set)
    linhas = []
    for vid, s in pec.groupby("idVotacao"):
        dt = s["dt"].iloc[0]
        em = per[(per["inicio"] <= dt + pd.Timedelta(hours=23)) & (per["fim"] > dt)]["deputado_id"].unique()
        fi = filiacao[(filiacao["ini"] <= dt + pd.Timedelta(hours=23)) & (filiacao["fim"] > dt) & filiacao["id"].isin(em)]
        ori = s[s["diretiva"] & s["camada"].isin(["própria", "bloco", "bloco inferido"])].groupby("partido")["od"].first()
        for q, o in ori.items():
            if o != 1:
                continue
            membros = set(fi.loc[fi["siglaPartido"] == q, "id"])
            pres = s[s["partido"] == q]
            seg = (pres["vd"] == 1).sum()
            aus = len(membros - set(pres["deputado_id"]) - presid.get(vid, set()))
            linhas.append((vid, q, seg, len(pres), aus))
    t = pd.DataFrame(linhas, columns=["idVotacao", "partido", "seguiu", "presentes", "ausentes"])
    num("pec_n_votacoes", t["idVotacao"].nunique())
    num("pec_disc_presentes", t["seguiu"].sum() / t["presentes"].sum())
    num("pec_disc_com_ausencia", t["seguiu"].sum() / (t["presentes"] + t["ausentes"]).sum())
    num("pec_share_ausentes", t["ausentes"].sum() / (t["presentes"] + t["ausentes"]).sum())
    return t


# ====================================================== montagem do manuscrito
FORMATOS = {
    "pct": lambda x: pct(x, 1), "pct0": lambda x: pct(x, 0), "pct2": lambda x: pct(x, 2),
    "pp": lambda x: br(100 * x, 1), "pp2": lambda x: br(100 * x, 2),
    "d1": lambda x: br(x, 1), "d2": lambda x: br(x, 2), "d3": lambda x: br(x, 3), "d4": lambda x: br(x, 4),
    "int": lambda x: milhar(x), "raw": lambda x: str(x),
    "data": lambda x: pd.Timestamp(x).strftime("%d/%m/%Y"),
    # formatos em inglês (Abstract)
    "pcten": lambda x: f"{100 * x:.1f}", "pct0en": lambda x: f"{100 * x:.0f}", "ppen": lambda x: f"{100 * x:.1f}",
    "inten": lambda x: f"{int(x):,}", "dataen": lambda x: pd.Timestamp(x).strftime("%d %B %Y"),
}


def montar_artigo():
    """Gera artigo.md a partir de artigo_fonte.md: {{fmt:chave}} vira o número de R formatado e
    {{tab:nome}} vira a tabela tabelas/<nome>.md. Chave ausente interrompe a execução."""
    fonte = (AQUI / "artigo_fonte.md").read_text(encoding="utf-8")
    faltam = []

    def sub(m):
        fmt, chave = m.group(1), m.group(2)
        if fmt == "tab":
            return (TAB / f"{chave}.md").read_text(encoding="utf-8").strip()
        if chave not in R or R[chave] is None:
            faltam.append(chave)
            return "??"
        return FORMATOS[fmt](R[chave])
    txt = re.sub(r"\{\{(\w+):([^}]+)\}\}", sub, fonte)
    if faltam:
        raise KeyError(f"chaves ausentes em resultados.json: {sorted(set(faltam))}")
    cab = ("<!-- Arquivo gerado por analise.py a partir de artigo_fonte.md; não edite à mão. -->\n")
    (AQUI / "artigo.md").write_text(cab + txt, encoding="utf-8")


# ============================================================================ figuras
def fig_disciplina(tab):
    plt = plt_setup()
    t = tab.iloc[::-1]
    y = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(7, 5.6))
    ax.hlines(y + 0.15, t["D_lo2"] * 100, t["D_hi2"] * 100, color=COR["s1"], lw=2)
    ax.plot(t["D"] * 100, y + 0.15, "o", ms=6, color=COR["s1"], label="D: segue a orientação da liderança")
    ax.hlines(y - 0.15, t["U_lo2"] * 100, t["U_hi2"] * 100, color=COR["s2"], lw=2)
    ax.plot(t["U"] * 100, y - 0.15, "s", ms=5.5, color=COR["s2"], label="U: vota com a maioria dos colegas de partido")
    for yy, (_, r) in zip(y, t.iterrows()):
        ax.text(101.2, yy, f"{pct(r['share_propria'], 0)}%", va="center", ha="left", fontsize=8, color=COR["texto2"])
    ax.text(101.2, len(t) - 0.2, "orientação\nprópria", fontsize=7.5, color=COR["texto2"], va="bottom")
    ax.set_yticks(y, t.index)
    ax.set_xlim(min(76, np.floor(np.nanmin(t[["D_lo2", "U_lo2"]].to_numpy()) * 100) - 1), 100.5)
    ax.set_xlabel("% dos votos (IC 95%, bootstrap em duas vias: votações e deputados)")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Disciplina à liderança (D) e unidade partidária (U), Plenário")
    fig.tight_layout()
    fig.savefig(FIG / "fig2_disciplina_unidade.png", bbox_inches="tight")
    plt.close(fig)


def fig_serie(sem):
    plt = plt_setup()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7, 5.2), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]})
    x = np.arange(len(sem))
    ok = (sem["cobD"] >= 0.2).to_numpy()
    for col, cor, mk, rot in [("D", COR["s1"], "o", "D (todas as camadas)"), ("Dp", COR["s3"], "^", "D (só orientação própria)"),
                              ("U", COR["s2"], "s", "U (maioria dos colegas)")]:
        yv = (sem[col] * 100).to_numpy()
        if col != "U":
            yv = np.where(ok, yv, np.nan)      # D omitido onde a cobertura < 20%
        a1.plot(x, yv, marker=mk, ms=6, lw=2, color=cor, label=rot)
    a1.set_ylabel("% dos votos")
    a1.set_ylim(84, 99.5)
    a1.legend(fontsize=7.5, loc="lower left", ncol=3)
    a1.set_title("Disciplina (D) e unidade (U) por semestre; D omitido com cobertura < 20%")
    a2.bar(x, sem["cobD"] * 100, color=COR["cinza"], width=0.6)
    for xx, c in zip(x, sem["cobD"]):
        a2.text(xx, c * 100 + 3, f"{pct(c, 0)}%", ha="center", fontsize=8, color=COR["texto2"])
    a2.set_ylim(0, 115)
    a2.set_ylabel("Cobertura de D (%)")
    a2.set_xticks(x, sem.index)
    fig.tight_layout()
    fig.savefig(FIG / "fig1_serie_semestral.png", bbox_inches="tight")
    plt.close(fig)


def fig_rice(rp, ps):
    plt = plt_setup()
    t = rp.reindex([q for q in ps if q in rp.index]).iloc[::-1]
    y = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(6.6, 5))
    ax.plot(t["rice"], y, "o", ms=6, color=COR["s1"], label="Rice bruto (votações disputadas)")
    ax.plot(t["rice_m10"], y, "D", ms=5, mfc="none", mew=1.6, color=COR["s2"], label="Rice padronizado (m = 10)")
    ax.axvline(np.nanmean(t["base_m10"]), color=COR["cinza"], ls="--", lw=1.2)
    ax.text(np.nanmean(t["base_m10"]) + 0.01, len(t) - 0.6, "voto aleatório\n(m = 10)", fontsize=8, color=COR["texto2"])
    ax.set_yticks(y, t.index)
    ax.set_xlim(0.4, 1.0)
    ax.set_xlabel("Índice de Rice médio")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Coesão nas votações disputadas (minoria ≥ 10%)")
    fig.tight_layout()
    fig.savefig(FIG / "fig3_rice.png", bbox_inches="tight")
    plt.close(fig)


def fig_validacao(difs):
    plt = plt_setup()
    rot = {"M0c − M1": "posição do partido na votação além da\norientação registrada (M0c→M1)",
           "M1 − M2b": "lealdade individual sem direção\n(M1→M2b)",
           "M2b − M3": "direção individual além da lealdade\ncom a mesma estrutura (M2b→M3)",
           "M3 − M4": "2ª dimensão intrapartidária\n(M3→M4)"}
    t = difs[difs["par"].isin(rot)].iloc[::-1]
    y = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.hlines(y, t["lo"], t["hi"], color=COR["s1"], lw=2.2)
    ax.plot(t["dif"], y, "o", ms=7, color=COR["s1"])
    ax.axvline(0, color=COR["texto2"], lw=1)
    for yy, (_, r) in zip(y, t.iterrows()):
        ax.text(r["hi"] + 0.004, yy, br(r["dif"], 3), va="center", fontsize=8, color=COR["texto2"])
    ax.set_yticks(y, [rot[p] for p in t["par"]], fontsize=8)
    ax.set_xlabel("Redução da log-loss por voto (fora da amostra; IC 95% por bootstrap de deputados)")
    ax.set_title("O que cada componente acrescenta: células com divisão interna")
    fig.tight_layout()
    fig.savefig(FIG / "fig4_validacao_cruzada.png", bbox_inches="tight")
    plt.close(fig)


def fig_evento(ev, janelas):
    plt = plt_setup()
    rots = [r for _, _, r in janelas]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    t = ev["U"]
    for grupo, cor, mk, off, rot in [("ind", COR["s1"], "o", -0.08, "troca individual"), ("fus", COR["s2"], "s", 0.08, "fusão de partidos (placebo)")]:
        if not any(f"{grupo}:{r}" in t.index for r in rots):
            continue      # grupo sem coeficientes identificados (fusões em U)
        xs, ys, lo, hi = [], [], [], []
        for k, r in enumerate(rots):
            if r == "−12 a −7":
                xs.append(k + off); ys.append(0); lo.append(0); hi.append(0)
                continue
            nm = f"{grupo}:{r}"
            if nm in t.index:
                xs.append(k + off); ys.append(t.loc[nm, "coef"] * 100); lo.append(t.loc[nm, "lo"] * 100); hi.append(t.loc[nm, "hi"] * 100)
        ax.vlines(xs, lo, hi, color=cor, lw=2)
        ax.plot(xs, ys, mk, ms=6, color=cor, label=rot)
    ax.axhline(0, color=COR["texto2"], lw=1)
    ax.axvline(3.5, color=COR["cinza"], ls=":", lw=1)
    ax.set_xticks(range(len(rots)), [r + "\nmeses" for r in rots], fontsize=8)
    ax.set_ylabel("Δ desvio da maioria dos\ncolegas (pontos percentuais)")
    ax.legend(fontsize=8, loc="upper left")
    ax.set_title("Desvio em torno da troca individual de partido (ref.: −12 a −7 meses)")
    fig.tight_layout()
    fig.savefig(FIG / "fig6_troca_partido.png", bbox_inches="tight")
    plt.close(fig)


def fig_pontos(X, ps):
    plt = plt_setup()
    x = X[(X["n_votos"] >= 100) & X["partido"].isin(ps)]
    ordem = x.groupby("partido")["dim1"].median().sort_values().index
    fig, ax = plt.subplots(figsize=(7, 5.4))
    rng = np.random.default_rng(1)
    for k, q in enumerate(ordem):
        s = x[x["partido"] == q]["dim1"]
        ax.plot(s, k + rng.uniform(-0.18, 0.18, len(s)), "o", ms=3.2, alpha=0.55, color=COR["s1"], mec="none")
        ax.plot([s.median()], [k], "|", ms=14, mew=2.4, color=COR["texto"])
    allx = x["dim1"]
    ax.axvline(allx.quantile(0.5), color=COR["s2"], ls="-", lw=1.4, label="mediana dos períodos")
    ax.axvline(allx.quantile(0.4), color=COR["s2"], ls=":", lw=1.3, label="quantis de 40% e 60% (pivôs de 3/5)")
    ax.axvline(allx.quantile(0.6), color=COR["s2"], ls=":", lw=1.3)
    ax.plot([], [], "|", ms=10, mew=2.4, color=COR["texto"], label="mediana do partido")
    ax.legend(fontsize=7.5, loc="lower right")
    ax.set_yticks(range(len(ordem)), ordem)
    ax.set_xlabel("dim1 global: oposição (−) × governo (+)")
    ax.set_title("Pontos ideais por partido (períodos deputado×partido com ≥ 100 votos)")
    fig.tight_layout()
    fig.savefig(FIG / "fig5_pontos_ideais.png", bbox_inches="tight")
    plt.close(fig)


def fig_governo(t, cf):
    plt = plt_setup()
    tt = t.join(cf[["prev"]], how="left").iloc[::-1]
    y = np.arange(len(tt))
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.hlines(y, tt["lo"] * 100, tt["hi"] * 100, color=COR["s1"], lw=2)
    ax.plot(tt["partido_"] * 100, y, "o", ms=7, color=COR["s1"], label="segue o partido (observado, IC 95%)")
    ax.plot(tt["governo"] * 100, y, "s", ms=6, color=COR["s2"], label="segue o Governo (observado)")
    ax.plot(tt["prev"] * 100, y, "D", ms=6, mfc="none", mew=1.6, color=COR["texto2"],
            label="segue o partido (previsto pelas preferências, M5)")
    for yy, (_, r) in zip(y, tt.iterrows()):
        ax.text(101, yy, f"{milhar(r['n'])} ({int(r['votacoes'])})", va="center", fontsize=7.5, color=COR["texto2"])
    ax.set_yticks(y, tt.index)
    ax.set_xlim(0, 112)
    ax.set_xlabel("% dos votos quando a orientação do partido e a do Governo são opostas")
    ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=2)
    ax.text(101, len(tt) - 0.4, "votos (votações)", fontsize=7.5, color=COR["texto2"])
    ax.set_title("Partidos da base: partido ou Governo?")
    fig.tight_layout()
    fig.savefig(FIG / "fig7_partido_governo.png", bbox_inches="tight")
    plt.close(fig)


# ============================================================================ tabelas
def tabela_partidos(tab, taD, taU, rp):
    t = pd.DataFrame({"Partido": tab.index,
                      "D (IC 95%)": [f"{pct(r['D'])} [{pct(r['D_lo2'])}; {pct(r['D_hi2'])}]" for _, r in tab.iterrows()],
                      "Cob. D": tab["cobD"].map(lambda x: pct(x, 0)),
                      "D própria (votações)": [f"{pct(r['Dp'])} ({int(r['vDp'])})" if pd.notna(r["Dp"]) and r["vDp"] >= 10
                                               else (f"– ({int(r['vDp'])})" if pd.notna(r["vDp"]) else "–") for _, r in tab.iterrows()],
                      "U (IC 95%)": [f"{pct(r['U'])} [{pct(r['U_lo2'])}; {pct(r['U_hi2'])}]" if pd.notna(r["U"]) else "–"
                                     for _, r in tab.iterrows()]})
    for a in [2023, 2024, 2025, 2026]:
        t[f"U {a}"] = [pct(taU.loc[q, a]) if a in taU.columns else "–" for q in tab.index]
    t = t.drop(columns=["Cob. D"]).assign(**{"Cob. D": tab["cobD"].map(lambda x: pct(x, 0)).to_numpy()})
    t["Rice disp."] = [br(rp.loc[q, "rice"], 2) if q in rp.index else "–" for q in tab.index]
    t["Rice m=3"] = [br(rp.loc[q, "rice_m3"], 2) if q in rp.index else "–" for q in tab.index]
    t["Rice m=10"] = [br(rp.loc[q, "rice_m10"], 2) if q in rp.index else "–" for q in tab.index]
    t["% racha"] = [pct(rp.loc[q, "racha"], 0) if q in rp.index else "–" for q in tab.index]
    tabela_md(t, "tab2_disciplina_partidos",
              "Tabela 2 – Disciplina à liderança (D), unidade (U) e coesão (Rice) por partido, Plenário",
              nota="D: voto na direção da orientação diretiva da bancada (Não = Obstrução; Abstenção = desvio), "
                   "camadas própria, bloco e bloco inferido, sem o bloco heterogêneo de 2025. Cob. D: % dos votos "
                   "do partido com orientação diretiva aplicável. U: voto na direção da maioria dos demais colegas "
                   "(≥ 5). Rice em votações com minoria ≥ 10%; m = 3 e m = 10: padronização de Desposato; '% racha': "
                   "votações disputadas com Rice < 0,5. IC por bootstrap em duas vias (votações e deputados, 500 réplicas). "
                   "D própria: só votos sob orientação do próprio partido ou federação, com o nº de votações entre parênteses; "
                   "omitida com menos de 10 votações.")
    return t


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--secoes", nargs="+", default=["tudo"])
    ARGS = ap.parse_args()
    tudo = "tudo" in ARGS.secoes
    sec = lambda s: tudo or s in ARGS.secoes
    t0 = time.time()
    v, vt, dep = carregar()
    descritivo(v, vt, dep)
    validar_classificador()
    base = disciplina(v)
    ps = base["ps"]
    rec = disciplina_recortes(v, base)
    rec_fmt = rec.assign(D=rec["D"].map(pct), U=rec["U"].map(pct), D_aj=rec["D_aj"].map(pct), U_aj=rec["U_aj"].map(pct))
    rec_fmt.columns = ["Recorte", "Categoria", "Votações", "D", "U", "D ajust.", "U ajust."]
    tabela_md(rec_fmt, "tab3_recortes", "Tabela 3 – Disciplina (D) e unidade (U) por tipo de votação e de proposição, Plenário",
              nota="'Ajust.': média prevista de cada categoria com efeitos fixos de partido×ano (composição partidária da amostra toda). "
                   "Votações: só as que têm orientação diretiva aplicável (por isso as contagens diferem das da Tabela 1).")
    orientacoes_faladas(base["p"])
    tt, temas_vt = disciplina_temas(v, base)
    tt_fmt = tt.reset_index().rename(columns={"tema": "Tema", "votacoes": "Votações"})
    tt_fmt["D"] = tt_fmt["D"].map(pct); tt_fmt["U"] = tt_fmt["U"].map(pct)
    tabela_md(tt_fmt[["Tema", "Votações", "D", "U"]], "tab4_temas",
              "Tabela A1 – Disciplina (D) e unidade (U) por tema da proposição votada (ordem crescente de U)",
              nota="Temas oficiais da Câmara (multi-rótulo, peso 1/k); temas com < 15 votações em 'Outros temas'.")
    g, rp = rice(v)
    g20, rp20 = rice(v, limiar=0.2, sufixo="_d20")
    rice_estabilidade(rp, rp20, ps)
    tabela_partidos(base["tab"], base["taD"], base["taU"], rp)
    fig_disciplina(base["tab"]); fig_serie(base["sem"]); fig_rice(rp, ps)
    p = base["p"]
    per, pres = painel_exercicio(dep, p)
    ausencia_pec(p, per)
    ausencia_geral(p, per)
    rob = robustez(v, base)
    rob_fmt = rob.copy()
    for c in ["Geral", "Cobertura"] + ps:
        rob_fmt[c] = rob_fmt[c].map(pct)
    rob_fmt["ρ (ranking)"] = rob_fmt["ρ (ranking)"].map(lambda x: br(x, 2))
    tabela_md(rob_fmt[["Variante", "Geral", "Cobertura", "ρ (ranking)"] + ps], "tab9_robustez",
              "Tabela 8 – Robustez da disciplina (D) a decisões de medida, Plenário",
              nota="ρ: correlação de Spearman entre o ranking dos partidos na variante e na medida principal.")
    antes_depois_troca(base["d"])
    # números prévios do projeto (avaliacao.json de embeddings_deputados.py; Plenário + comissões)
    av = json.loads((DADOS / "embeddings" / "avaliacao.json").read_text())
    num("prev_irt_intra_acuracia", av["votos"]["irt_intrapartido_acuracia"])
    num("prev_irt_global_acuracia", av["votos"]["irt_acuracia"])
    num("prev_base_orientacao_acuracia", av["votos"]["base_orientacao_partido_acuracia"])
    num("prev_intra_knn5_partido", av["representacoes"]["votos_intra"]["knn5_acerta_partido"])
    num("prev_intra_acaso_partido", av["representacoes"]["votos_intra"]["acerto_partido_ao_acaso"])
    if sec("irt"):
        A = prep_irt(p)
        num("irt_n_votos", len(A["y"])); num("irt_n_votacoes", A["n_j"]); num("irt_n_periodos", A["n_i"])
        num("irt_n_celulas", int(A["grp"].max() + 1))
        ncel = np.bincount(A["grp"])
        num("irt_celulas_mediana_votantes", float(np.median(ncel))); num("irt_celulas_share_menos5", (ncel < 5).mean())
        P, P_sens, info, tempos = validacao_cruzada(A)
        tab_cv, difs, fx = avaliar_cv(A, P, P_sens, info)
        fig_validacao(difs)
        tc = tab_cv[tab_cv["amostra"].isin(["disputadas_intra"]) & (tab_cv["modelo"] != "M3emb")].copy()
        tc["Modelo"] = tc["modelo"].map(NOMES_M)
        tc["Amostra"] = tc["amostra"].map({"todas": "todas as células", "disputadas_intra": "células com divisão interna"})
        tc = tc.assign(**{"Log-loss": tc["logloss"].map(lambda x: br(x, 4)), "Brier": tc["brier"].map(lambda x: br(x, 4)),
                          "Acurácia": tc["acuracia"].map(lambda x: pct(x, 2)),
                          "AUC-PR (desvio)": tc["auc_pr_desvio"].map(lambda x: br(x, 3))})
        tabela_md(tc[["Modelo", "Log-loss", "Brier", "Acurácia", "AUC-PR (desvio)"]], "tab5_validacao",
                  "Tabela 4 – Desempenho fora da amostra nas células com divisão interna (validação cruzada em 5 dobras de células deputado×votação)",
                  nota="Células com divisão interna: partido×votação com ≥ 5 colegas no treino e ao menos um voto "
                       "contra a maioria do partido no treino. AUC-PR: precisão média ao ranquear os votos contra a "
                       "maioria de treino da célula.")
        glob = dispersao_pivos(A, p, dep, per)
        fig_pontos(glob["X"], ps)
        diss = tabela_dissidentes(glob["X"])
        tabela_md(diss, "tab7_dissidentes", "Tabela A2 – Dissidentes sistemáticos: maiores distâncias à mediana do próprio partido (dim1 global)",
                  nota=f"Períodos deputado×partido com ≥ 100 votos, a pelo menos 2 desvios-padrão da mediana do partido "
                       f"e com IC 95% (bootstrap de votações, {R['boot_B_global']} réplicas, Procrustes) que exclui essa mediana.")
        piv = glob["piv"].drop(columns=["partido_mediana"]).rename(columns={
            "semestre": "Semestre", "n_em_exercicio": "Em exercício", "n_com_ponto": "Com ponto ideal",
            "mediana": "Mediano", "pivo_40": "Pivô 40%", "pivo_60": "Pivô 60%"})
        tabela_md(piv, "tab8_pivos", "Tabela A3 – Deputado mediano e pivôs de 3/5 por semestre (dim1 global)",
                  nota="Deputados em exercício na data de referência do semestre, com ≥ 30 votos no período "
                       "deputado×partido vigente. Pivô 60%: o 308º de 513 a partir da oposição; pivô 40%: o 308º a partir do governo.")
        dt_ = glob["disp"].reindex([q for q in ps if q in glob["disp"].index])
        tabela_md(pd.DataFrame({"Partido": dt_.index, "Períodos": dt_["size"].astype(int),
                                "DP dim1 (EP)": [f"{br(r['std'])} ({br(r['ep'])})" for _, r in dt_.iterrows()],
                                "Viés bootstrap": dt_["vies"].map(lambda x: br(x, 3)),
                                "IIQ dim1": dt_["iqr"].map(br)}),
                  "tab6_dispersao", "Tabela 7 – Dispersão interna dos partidos no eixo governo × oposição (dim1 global, Plenário)",
                  nota="Períodos deputado×partido com ≥ 100 votos; partidos com ≥ 5 períodos. EP e viés por bootstrap de votações com reajuste e alinhamento de Procrustes; o viés (média bootstrap menos estimativa) mostra quanto a reamostragem infla a dispersão, sobretudo em bancadas pequenas.")
        dist = distancia_fora_periodo(p, A)
        reg = regressao_desvio(base, dep, per, dist)
        linhas = []
        rot = {"sup_ministro": "Suplente (titular ministro)", "sup_secretario": "Suplente (titular secretário)",
               "sup_outro": "Suplente (outro motivo)", "mulher": "Mulher", "idade10": "Idade (décadas)",
               "log_cadeiras_uf": "log cadeiras da UF", "trocou_antes": "Trocará de partido (votos antes da troca)",
               "trocou_depois": "Trocou de partido (votos depois da troca)",
               "dist_fora": "Distância espacial à mediana do partido (outro biênio, em DP)"}
        for k in rot:
            linhas.append({"Variável": rot[k],
                           **{f"Desvio de {n} (p.p.)": f"{br(reg[n][0].loc[k, 'coef'] * 100)} [{br(reg[n][0].loc[k, 'lo'] * 100)}; {br(reg[n][0].loc[k, 'hi'] * 100)}]"
                              for n in ["D", "U"]}})
        linhas.append({"Variável": "UF (Wald, 26 g.l.)", **{f"Desvio de {n} (p.p.)": f"χ² = {br(R[f'reg_{n}_uf_wald'], 1)}; p = {br(R[f'reg_{n}_uf_p'], 3)}" for n in ["D", "U"]}})
        linhas.append({"Variável": "N votos (deputados)", **{f"Desvio de {n} (p.p.)": f"{milhar(R[f'reg_{n}_n'])} ({R[f'reg_{n}_n_dep']})" for n in ["D", "U"]}})
        tabela_md(pd.DataFrame(linhas), "tab10_regressao",
                  "Tabela 6 – Correlatos do desvio individual: MPL com efeitos fixos partido×votação",
                  nota="Coeficientes em pontos percentuais (IC 95%, EP agrupados por deputado e por votação). "
                       "Distância medida na dim1 global estimada com as votações do outro biênio.")
        ev, janelas = estudo_evento(base, dep)
        selecao_troca(glob["X"])
        fig_evento(ev, janelas)
        intra = interpretar_intra(A, vt, dep, glob, temas_vt)
        tabela_md(tabela_cargas(intra["vv"]), "tab11_cargas",
                  "Tabela 5 – Votações com maior carga na dimensão intrapartidária (modelo intra 1D)",
                  nota="Carga positiva: os deputados mais governistas que o próprio partido tendem a votar Sim.")
        x5, t5, cf, tab5 = partido_vs_governo(base, P, A, dep, per, dist)
        partido_vs_governo(base, P, A, dep, per, dist, camadas=("própria", "bloco"), sufixo="_seminf")
        fig_governo(t5, cf)
    import platform, scipy, sklearn, matplotlib
    R["versoes"] = (f"Python {platform.python_version()}; numpy {np.__version__}; pandas {pd.__version__}; "
                    f"scipy {scipy.__version__}; scikit-learn {sklearn.__version__}; matplotlib {matplotlib.__version__}")
    R["tempo_execucao_s"] = round(time.time() - t0)
    R["n_chaves"] = len(R) + 1
    (AQUI / "resultados.json").write_text(json.dumps(R, indent=1, ensure_ascii=False, allow_nan=False))
    if tudo and (AQUI / "artigo_fonte.md").exists():
        montar_artigo()
    print(f"{len(R)} números em resultados.json; tempo: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
