"""
Análise do artigo "Ideologia ou especialização? A agenda temática dos deputados federais
na 57ª Legislatura" (artigos/04-agenda-tematica).

Gera, a partir de dados/leg57 (e de dois arquivos auxiliares em dados_aux/, baixados da API
de Dados Abertos da Câmara e guardados em cache), todos os números, tabelas e figuras do artigo:
  resultados.json      todos os números citados no texto
  tabelas/*.md         tabelas em Markdown
  figuras/*.png        figuras

Uso (a partir da raiz do repositório):
  python artigos/04-agenda-tematica/analise.py            # ~5–10 min em CPU
  python artigos/04-agenda-tematica/analise.py --rapido   # menos permutações (teste)

Não altera embeddings_deputados.py nem os dados versionados: o perfil temático é
reimplementado aqui (com parâmetros para as variantes de sensibilidade) e a versão de
referência é conferida contra dados/leg57/embeddings/emb_temas.parquet.
"""
import argparse
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse, stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "dados" / "leg57"
EMB = PASTA / "embeddings"
AQUI = Path(__file__).resolve().parent
AUX, FIG, TAB = AQUI / "dados_aux", AQUI / "figuras", AQUI / "tabelas"
for p in (AUX, FIG, TAB):
    p.mkdir(exist_ok=True)

ap = argparse.ArgumentParser()
ap.add_argument("--rapido", action="store_true")
ARGS = ap.parse_args()
NPERM = 99 if ARGS.rapido else 999      # permutações
NSIM = 50 if ARGS.rapido else 300       # simulações dos nulos de especialização
NBOOT = 200 if ARGS.rapido else 2000    # bootstrap de deputados
SEED = 20231101
RNG = np.random.default_rng(SEED)

R = {}   # todos os números do artigo


def guarda(chave, valor):
    """Armazena número arredondado em R (chave com pontos = hierarquia)."""
    if isinstance(valor, (np.floating, float)):
        valor = round(float(valor), 4)
    elif isinstance(valor, (np.integer,)):
        valor = int(valor)
    d = R
    partes = chave.split(".")
    for p in partes[:-1]:
        d = d.setdefault(p, {})
    d[partes[-1]] = valor
    return valor


def md_tabela(df, nome, floatfmt=3, index=False):
    df = df.copy()
    if index:
        df = df.reset_index()
    def f(x):
        if isinstance(x, (float, np.floating)):
            if np.isnan(x):
                return "–"
            return f"{x:,.{floatfmt}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if isinstance(x, (int, np.integer)):
            return f"{x:,}".replace(",", ".")
        return str(x)
    linhas = ["| " + " | ".join(map(str, df.columns)) + " |",
              "|" + "|".join("---" for _ in df.columns) + "|"]
    for _, r in df.iterrows():
        linhas.append("| " + " | ".join(f(v) for v in r.values) + " |")
    (TAB / f"{nome}.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def sem_acento(t):
    return unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()


# ----------------------------------------------------------------- estilo das figuras
COR = {"azul": "#2a78d6", "laranja": "#eb6834", "aqua": "#1baf7a", "amarelo": "#eda100",
       "magenta": "#e87ba4", "verde": "#008300", "violeta": "#6250d6", "vermelho": "#e34948",
       "tinta": "#0b0b0b", "tinta2": "#52514e", "mudo": "#898781", "grade": "#e1e0d9",
       "eixo": "#c3c2b7", "fundo": "#fcfcfb", "neutro": "#f0efec"}
plt.rcParams.update({
    "figure.facecolor": COR["fundo"], "axes.facecolor": COR["fundo"], "savefig.facecolor": COR["fundo"],
    "axes.edgecolor": COR["eixo"], "axes.labelcolor": COR["tinta2"], "xtick.color": COR["tinta2"],
    "ytick.color": COR["tinta2"], "text.color": COR["tinta"], "axes.grid": True,
    "grid.color": COR["grade"], "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
    "legend.frameon": False, "savefig.dpi": 200, "savefig.bbox": "tight"})


def salva_fig(fig, nome):
    fig.savefig(FIG / f"{nome}.png")
    plt.close(fig)


ABREV = {"Agricultura, Pecuária, Pesca e Extrativismo": "Agricultura e Pecuária",
         "Meio Ambiente e Desenvolvimento Sustentável": "Meio Ambiente",
         "Energia, Recursos Hídricos e Minerais": "Energia e Rec. Hídricos",
         "Relações Internacionais e Comércio Exterior": "Relações Internacionais",
         "Processo Legislativo e Atuação Parlamentar": "Processo Legislativo",
         "Viação, Transporte e Mobilidade": "Viação e Transporte",
         "Direito Penal e Processual Penal": "Direito Penal",
         "Direito Civil e Processual Civil": "Direito Civil",
         "Homenagens e Datas Comemorativas": "Homenagens e Datas",
         "Indústria, Comércio e Serviços": "Indústria e Comércio",
         "Previdência e Assistência Social": "Previdência e Assist. Social",
         "Cidades e Desenvolvimento Urbano": "Cidades",
         "Ciência, Tecnologia e Inovação": "Ciência e Tecnologia",
         "Política, Partidos e Eleições": "Política e Eleições",
         "Direito e Defesa do Consumidor": "Defesa do Consumidor",
         "Finanças Públicas e Orçamento": "Finanças Públicas"}


def ab(t):
    return ABREV.get(t, t)


t0 = time.time()
print("1. Carregando dados...")
P = pd.read_parquet(PASTA / "proposicoes.parquet",
                    columns=["id", "siglaTipo", "ano", "dataApresentacao", "ementa",
                             "ultimoStatus_descricaoSituacao"])
A = pd.read_parquet(PASTA / "proposicoes_autores.parquet")
T = pd.read_parquet(PASTA / "proposicoes_temas.parquet")
D = pd.read_parquet(PASTA / "deputados.parquet")
DP = pd.read_parquet(PASTA / "deputados_partidos.parquet")
EV = pd.read_parquet(EMB / "emb_votos.parquet")
EF = pd.read_parquet(EMB / "emb_frentes.parquet")
ET_REF = pd.read_parquet(EMB / "emb_temas.parquet")
V = pd.read_parquet(PASTA / "votacoes.parquet")

TEMAS = sorted(T["tema"].unique())
K = len(TEMAS)
guarda("dados.n_temas", K)
PROJETOS = {"PL", "PLP", "PEC", "PDL", "PRC"}
FISCAL = {"RIC", "INC", "PFC", "SIT"}
PESO_TIPO = {**{t: 1.0 for t in PROJETOS}, **{t: 0.3 for t in FISCAL}}

# ------------------------------------------------------------------- dados auxiliares
def baixar_aux():
    """Legislatura inicial de cada deputado (arquivo em massa deputados.csv) e temas das
    proposições votadas em plenário que não estão em proposicoes_temas (API /temas).
    Ambos ficam em cache em dados_aux/ (versionados, para reprodutibilidade)."""
    import requests
    s = requests.Session()
    s.headers.update({"Accept": "application/json", "User-Agent": "analise-agenda-tematica"})

    def get(url, **kw):
        for i in range(6):
            try:
                r = s.get(url, timeout=120, **kw)
                if r.status_code == 200:
                    return r
                if r.status_code == 404:
                    return None
            except requests.RequestException:
                pass
            time.sleep(2 ** i)
        raise RuntimeError(url)

    arq = AUX / "deputados_legislatura_inicial.csv"
    if not arq.exists():
        print("   baixando deputados.csv (legislatura inicial)...")
        import io
        r = get("https://dadosabertos.camara.leg.br/arquivos/deputados/csv/deputados.csv")
        dd = pd.read_csv(io.StringIO(r.content.decode("utf-8-sig")), sep=";", dtype=str)
        dd["id"] = dd["uri"].str.rsplit("/", n=1).str[-1].astype(int)
        dd = dd[dd["id"].isin(D["id"])][["id", "idLegislaturaInicial", "idLegislaturaFinal"]]
        dd.to_csv(arq, index=False)

    arq2 = AUX / "temas_pauta_plenario.csv"
    if not arq2.exists():
        ids = pauta_ids()
        falta = sorted(set(ids) - set(T["idProposicao"]))
        print(f"   buscando temas de {len(falta)} proposições votadas na API...")
        linhas = []
        for k, pid in enumerate(falta):
            r = get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{pid}/temas")
            for x in (r.json()["dados"] if r is not None else []):
                linhas.append({"idProposicao": pid, "codTema": x["codTema"], "tema": x["tema"]})
            if r is not None and not r.json()["dados"]:
                linhas.append({"idProposicao": pid, "codTema": None, "tema": None})
        pd.DataFrame(linhas).to_csv(arq2, index=False)


def pauta_ids():
    s = V[(V["siglaOrgao"] == "PLEN") & V["tem_votos_nominais"]].copy()
    return s["proposicao_id"].dropna().str.split(",").str[0].str.strip().tolist()


baixar_aux()
LEGINI = pd.read_csv(AUX / "deputados_legislatura_inicial.csv")
TEMAS_PAUTA_API = pd.read_csv(AUX / "temas_pauta_plenario.csv", dtype={"idProposicao": str})

# ------------------------------------------------------------------- cobertura (Tabela 1)
print("2. Cobertura da classificação temática...")
com_tema = set(T["idProposicao"])
P["tem_tema"] = P["id"].isin(com_tema)
aut_n = A.groupby("idProposicao").size()
cob = (P.groupby("siglaTipo").agg(n=("id", "size"), com_tema=("tem_tema", "sum"))
       .sort_values("n", ascending=False))
cob["pct_tema"] = 100 * cob["com_tema"] / cob["n"]
guarda("dados.n_proposicoes", len(P))
guarda("dados.n_proposicoes_com_tema", int(P["tem_tema"].sum()))
guarda("dados.pct_com_tema", 100 * P["tem_tema"].mean())
guarda("dados.n_tipos", P["siglaTipo"].nunique())
guarda("dados.n_tipos_com_tema", int((cob["com_tema"] > 0).sum()))
guarda("dados.data_min", P["dataApresentacao"].min()[:10])
guarda("dados.data_max", P["dataApresentacao"].max()[:10])
for t in ["PL", "RIC", "INC", "PDL", "PLP", "PRC", "SIT", "PFC", "PEC", "RPD", "PRL", "REQ", "EMC"]:
    guarda(f"dados.tipo.{t}.n", int(cob.loc[t, "n"]))
    guarda(f"dados.tipo.{t}.com_tema", int(cob.loc[t, "com_tema"]))
desc_tipo = P.drop_duplicates("siglaTipo").set_index("siglaTipo")
tab1 = cob[cob["com_tema"] > 0].copy()
outros = cob[cob["com_tema"] == 0].head(6)
tab1 = pd.concat([tab1, outros])
tab1["grupo"] = [("projeto (peso 1)" if t in PROJETOS else "fiscalização (peso 0,3)" if t in FISCAL
                  else ("outro (peso 0,3)" if r.com_tema > 0 else "sem tema")) for t, r in tab1.iterrows()]
tab1 = tab1.reset_index()[["siglaTipo", "grupo", "n", "com_tema", "pct_tema"]]
tab1.columns = ["Tipo", "Grupo / peso", "Proposições", "Com tema", "% com tema"]
md_tabela(tab1, "tab1_cobertura", floatfmt=1)

nt = T.groupby("idProposicao").size()
guarda("qualidade.temas_por_prop_media", nt.mean())
guarda("qualidade.pct_um_tema", 100 * (nt == 1).mean())
guarda("qualidade.pct_3mais_temas", 100 * (nt >= 3).mean())
guarda("qualidade.pct_relevancia_zero", 100 * (T["relevancia"].astype(int) == 0).mean())

# ------------------------------------------------------- base de itens (autoria × proposição)
Pm = P[["id", "siglaTipo", "dataApresentacao"]].rename(columns={"id": "idProposicao"})
IT = A.merge(Pm, on="idProposicao")
IT = IT[IT["idProposicao"].isin(com_tema)].copy()
IT["dep"] = IT["idDeputadoAutor"].astype(int)
IT["n_aut"] = IT["idProposicao"].map(aut_n)
IT["ano"] = IT["dataApresentacao"].str[:4].astype(int)
IT["grupo"] = np.where(IT["siglaTipo"].isin(PROJETOS), "projeto",
                       np.where(IT["siglaTipo"].isin(FISCAL), "fiscal", "outro"))
IT["ordem"] = IT["ordemAssinatura"].astype(int)
IT["prop1"] = IT["proponente"].astype(int)
IT = IT.reset_index(drop=True)
guarda("dados.n_autorias_com_tema", len(IT))
guarda("dados.n_deputados_autores_com_tema", IT["dep"].nunique())

PROPS = sorted(com_tema)
PIDX = {p: i for i, p in enumerate(PROPS)}
TIDX = {t: i for i, t in enumerate(TEMAS)}
IT["pidx"] = IT["idProposicao"].map(PIDX)
_t = T.assign(pi=T["idProposicao"].map(PIDX), ti=T["tema"].map(TIDX))
_t = _t.drop_duplicates(["pi", "ti"])
TP_FRAC = np.zeros((len(PROPS), K))
k_por_prop = _t.groupby("pi").size()
TP_FRAC[_t["pi"], _t["ti"]] = 1.0 / k_por_prop.reindex(_t["pi"]).to_numpy()
TP_INT = (TP_FRAC > 0).astype(float)          # variante: peso integral para cada tema
TIPO_PROP = P.set_index("id").loc[PROPS, "siglaTipo"].to_numpy()

# ------------------------------------------------------------------- perfis temáticos
def pesos_itens(it, fracionar=True, tipos=None, peso_tipo=PESO_TIPO, padrao=0.3,
                so_primeiro=False, so_proponente=False):
    w = np.where(fracionar, 1.0 / it["n_aut"].to_numpy(), 1.0)
    pt = it["siglaTipo"].map(peso_tipo).fillna(padrao).to_numpy() if peso_tipo is not None else 1.0
    w = w * pt
    m = np.ones(len(it), bool)
    if tipos is not None:
        m &= it["siglaTipo"].isin(tipos).to_numpy()
    if so_primeiro:
        m &= (it["ordem"] == 1).to_numpy()
    if so_proponente:
        m &= (it["prop1"] == 1).to_numpy()
    return np.where(m, w, 0.0)


def perfil(it, w, tp=TP_FRAC, excluir=None):
    """Matriz deputado × tema de pesos (W), volume e N efetivo de itens (Kish)."""
    deps, di = np.unique(it["dep"].to_numpy(), return_inverse=True)
    M = sparse.csr_matrix((w, (di, np.arange(len(it)))), shape=(len(deps), len(it)))
    W = np.asarray(M @ tp[it["pidx"].to_numpy()])
    if excluir is not None:
        W[:, [TIDX[e] for e in excluir]] = 0
    vol = W.sum(1)
    s1 = np.bincount(di, w, len(deps))
    s2 = np.bincount(di, w ** 2, len(deps))
    neff = np.divide(s1 ** 2, s2, out=np.zeros_like(s1), where=s2 > 0)
    df = pd.DataFrame(W, index=deps, columns=TEMAS)
    ok = vol > 0
    return df[ok], pd.Series(vol[ok], deps[ok]), pd.Series(neff[ok], deps[ok])


def proporcoes(W):
    return W.div(W.sum(1), axis=0)


def entropia(Pm):
    p = np.asarray(Pm, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        h = -np.nansum(np.where(p > 0, p * np.log(p), 0), axis=-1)
    return h


print("3. Perfil de referência e reprodução de emb_temas...")
w_base = pesos_itens(IT)
W0, VOL0, NEFF0 = perfil(IT, w_base)
P0 = proporcoes(W0)
ref = ET_REF.set_index("deputado_id")
cols_ref = [f"t_{t}" for t in TEMAS]
dif = np.abs(np.sqrt(P0).to_numpy() - ref.loc[P0.index, cols_ref].to_numpy()).max()
guarda("reproducao.max_dif_embedding", float(dif))
guarda("reproducao.max_dif_volume", float(np.abs(VOL0 - ref.loc[VOL0.index, "volume_ponderado"]).max()))
guarda("reproducao.n_deputados_perfil", len(P0))
CONF = VOL0[VOL0 >= 3].index
guarda("reproducao.n_confiaveis", len(CONF))
assert dif < 1e-9, "perfil não reproduz emb_temas"

# covariáveis dos deputados ------------------------------------------------------------
DP["ini"] = pd.to_datetime(DP["dataInicio"].str[:10])
DP["fim"] = pd.to_datetime(DP["dataFim"].fillna("2026-11-11").str[:10])
DP["dias"] = (DP["fim"] - DP["ini"]).dt.days
PART_PRINC = DP.sort_values("dias").groupby("id")["siglaPartido"].last()
REGIAO = {**dict.fromkeys(["AC", "AM", "AP", "PA", "RO", "RR", "TO"], "Norte"),
          **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "Nordeste"),
          **dict.fromkeys(["DF", "GO", "MS", "MT"], "Centro-Oeste"),
          **dict.fromkeys(["ES", "MG", "RJ", "SP"], "Sudeste"),
          **dict.fromkeys(["PR", "RS", "SC"], "Sul")}
COV = D.set_index("id")[["nome", "siglaPartido", "siglaUf", "sexo", "condicaoEleitoral"]].copy()
COV["partido"] = PART_PRINC.reindex(COV.index).fillna(COV["siglaPartido"])
COV["regiao"] = COV["siglaUf"].map(REGIAO)
COV["mulher"] = (COV["sexo"] == "F").astype(int)
COV["suplente"] = (~COV["condicaoEleitoral"].isin(["Titular"])).astype(int)
COV["veterano"] = (LEGINI.set_index("id")["idLegislaturaInicial"].reindex(COV.index) < 57).astype(int)
ev = EV[EV["confiavel"]].set_index("deputado_id")
COV["dim1"] = ev["dim1"].reindex(COV.index)
COV["dim2"] = ev["dim2"].reindex(COV.index)
guarda("dados.n_trocaram_partido", int((DP.groupby("id")["siglaPartido"].nunique() > 1).sum()))

# amostra analítica: confiáveis em temas E com ponto ideal
AM = [d for d in CONF if not np.isnan(COV.loc[d, "dim1"])]
guarda("amostra.n_com_dim1", len(AM))
X0 = np.sqrt(P0.loc[AM].to_numpy())
C = COV.loc[AM].copy()
C["vol"] = VOL0.loc[AM]
C["neff"] = NEFF0.loc[AM]
# participação da fiscalização no volume ponderado
w_fis = pesos_itens(IT, tipos=FISCAL)
Wf, _, _ = perfil(IT, w_fis)
C["frac_fiscal"] = (Wf.sum(1).reindex(AM).fillna(0) / C["vol"]).to_numpy()
q = C["dim1"].quantile([1 / 3, 2 / 3]).to_numpy()
C["lado"] = np.where(C["dim1"] <= q[0], "oposição", np.where(C["dim1"] >= q[1], "base", "centro"))
guarda("amostra.corte_dim1_terco_inferior", q[0])
guarda("amostra.corte_dim1_terco_superior", q[1])
for lado in ["oposição", "centro", "base"]:
    top = C[C["lado"] == lado]["partido"].value_counts(normalize=True).head(4)
    guarda(f"amostra.lado.{lado}.n", int((C["lado"] == lado).sum()))
    guarda(f"amostra.lado.{lado}.partidos", "; ".join(f"{k} {100*v:.0f}%" for k, v in top.items()))
    guarda(f"amostra.lado.{lado}.frac_fiscal_media", C.loc[C["lado"] == lado, "frac_fiscal"].mean())

# descritivos de tema dominante
dom = P0.loc[CONF].idxmax(axis=1).value_counts()
guarda("descr.tema_dominante_1", f"{dom.index[0]} ({dom.iloc[0]})")
guarda("descr.tema_dominante_2", f"{dom.index[1]} ({dom.iloc[1]})")
guarda("descr.tema_dominante_3", f"{dom.index[2]} ({dom.iloc[2]})")
guarda("descr.n_temas_dominantes_distintos", len(dom))

# =========================================================== 4. especialização (nulo)
print("4. Concentração temática e nulo estratificado por tipo...")
H0 = entropia(P0.loc[CONF])
Teff = np.exp(H0)
HHI = (P0.loc[CONF] ** 2).sum(1).to_numpy()
guarda("conc.Teff_mediana", np.median(Teff))
guarda("conc.Teff_p10", np.percentile(Teff, 10))
guarda("conc.Teff_p90", np.percentile(Teff, 90))
guarda("conc.Hnorm_mediana", np.median(H0 / np.log(K)))
guarda("conc.HHI_mediana", np.median(HHI))
guarda("conc.spearman_Teff_logvol", stats.spearmanr(Teff, np.log(VOL0.loc[CONF]))[0])
guarda("conc.pct_tema_dom_maior_50", 100 * (P0.loc[CONF].max(1) > 0.5).mean())

# nulo: cada item do deputado é trocado por proposição sorteada do mesmo tipo (preserva
# volume, pesos, n.º de itens e mix de tipos; multi-rotulação incluída)
it_c = IT[IT["dep"].isin(CONF) & (w_base > 0)].reset_index(drop=True)
w_c = pesos_itens(it_c)
deps_c, di_c = np.unique(it_c["dep"].to_numpy(), return_inverse=True)
Mc = sparse.csr_matrix((w_c, (di_c, np.arange(len(it_c)))), shape=(len(deps_c), len(it_c)))
pools = {t: np.where(TIPO_PROP == t)[0] for t in np.unique(TIPO_PROP)}
tipo_it = it_c["siglaTipo"].to_numpy()
idx_por_tipo = {t: np.where(tipo_it == t)[0] for t in np.unique(tipo_it)}
Hnull = np.zeros((NSIM, len(deps_c)))
for s in range(NSIM):
    novo = np.empty(len(it_c), int)
    for t, ii in idx_por_tipo.items():
        novo[ii] = RNG.choice(pools[t], len(ii))
    Wn = np.asarray(Mc @ TP_FRAC[novo])
    Hnull[s] = entropia(Wn / Wn.sum(1, keepdims=True))
ESP = pd.DataFrame({"Teff": np.exp(entropia(P0.loc[deps_c])),
                    "Teff_nulo": np.exp(Hnull).mean(0),
                    "H": entropia(P0.loc[deps_c]),
                    "H_nulo_sd": Hnull.std(0)}, index=deps_c)
ESP["S"] = ESP["Teff"] / ESP["Teff_nulo"]              # <1: mais concentrado que o acaso
ESP["p_menor"] = (Hnull <= ESP["H"].to_numpy()[None, :]).mean(0)
ESP["neff"] = NEFF0.loc[deps_c]
ESP["vol"] = VOL0.loc[deps_c]
guarda("esp.S_mediana", ESP["S"].median())
guarda("esp.S_p10", ESP["S"].quantile(0.1))
guarda("esp.S_p90", ESP["S"].quantile(0.9))
guarda("esp.pct_S_menor_1", 100 * (ESP["S"] < 1).mean())
guarda("esp.pct_signif_5", 100 * (ESP["p_menor"] < 0.05).mean())
guarda("esp.spearman_S_logneff", stats.spearmanr(ESP["S"], np.log(ESP["neff"]))[0])
guarda("esp.spearman_Teff_logneff", stats.spearmanr(ESP["Teff"], np.log(ESP["neff"]))[0])
guarda("esp.spearman_Tnulo_logneff", stats.spearmanr(ESP["Teff_nulo"], np.log(ESP["neff"]))[0])
guarda("esp.Teff_nulo_mediana", ESP["Teff_nulo"].median())

# especialistas e generalistas (com volume alto, para não premiar o acaso)
alto = ESP[ESP["neff"] >= 20].join(COV[["nome", "partido", "siglaUf"]])
alto["tema_dom"] = P0.loc[alto.index].idxmax(axis=1)
alto["p_dom"] = P0.loc[alto.index].max(axis=1)
guarda("esp.n_neff20", len(alto))
esp_t = alto.nsmallest(10, "S")
gen_t = alto.nlargest(10, "S")
def _fmt(d):
    o = d.reset_index()[["nome", "partido", "siglaUf", "neff", "Teff", "S", "tema_dom", "p_dom"]].copy()
    o["tema_dom"] = o["tema_dom"].map(ab)
    o.columns = ["Deputado(a)", "Partido", "UF", "N efetivo", "Temas efetivos", "S", "Tema dominante", "Proporção"]
    return o
md_tabela(_fmt(esp_t), "tab3a_especialistas", floatfmt=2)
md_tabela(_fmt(gen_t), "tab3b_generalistas", floatfmt=2)
dom_esp = alto.nsmallest(50, "S")["tema_dom"].value_counts().head(5)
guarda("esp.temas_dos_50_mais_especializados", "; ".join(f"{k} ({v})" for k, v in dom_esp.items()))

# Figura 2: temas efetivos x N efetivo, observado vs nulo
fig, axs = plt.subplots(1, 2, figsize=(9, 3.6))
ax = axs[0]
ax.scatter(ESP["neff"], ESP["Teff_nulo"], s=8, color=COR["mudo"], alpha=0.6, lw=0, label="esperado sob o nulo")
ax.scatter(ESP["neff"], ESP["Teff"], s=8, color=COR["azul"], alpha=0.7, lw=0, label="observado")
ax.set_xscale("log")
ax.set_xlabel("N efetivo de itens (Kish, escala log)")
ax.set_ylabel("Temas efetivos, exp(H)")
ax.set_title("A. Diversidade temática e volume")
ax.legend(loc="upper left", markerscale=2)
ax = axs[1]
ax.hist(ESP["S"], bins=40, color=COR["azul"], edgecolor=COR["fundo"], lw=0.5)
ax.axvline(1, color=COR["tinta2"], lw=1, ls="--")
ax.text(1.0, ax.get_ylim()[1] * 0.92, " acaso", color=COR["tinta2"], va="top")
ax.set_xlabel("S = temas efetivos observados / esperados")
ax.set_ylabel("Deputados")
ax.set_title("B. Índice de especialização")
salva_fig(fig, "fig2_especializacao")

# correlatos (OLS, EP robustos HC3)
print("5. Correlatos da especialização...")
import statsmodels.formula.api as smf
E = C.join(ESP[["S"]], how="inner").copy()
E["logS"] = np.log(E["S"])
E["log_neff"] = np.log(E["neff"])
E["abs_dim1"] = E["dim1"].abs()
grandes = E["partido"].value_counts()
E["partido_g"] = np.where(E["partido"].map(grandes) >= 10, E["partido"], "Outros")
E["dim1_dentro"] = E["dim1"] - E.groupby("partido_g")["dim1"].transform("mean")
E["abs_dim1_dentro"] = E["dim1_dentro"].abs()
f1 = "logS ~ log_neff + frac_fiscal + mulher + veterano + suplente + C(regiao, Treatment('Sudeste')) + dim1 + abs_dim1"
f2 = ("logS ~ log_neff + frac_fiscal + mulher + veterano + suplente + C(regiao, Treatment('Sudeste'))"
      " + C(partido_g, Treatment('PL')) + abs_dim1_dentro")
m1 = smf.ols(f1, E).fit(cov_type="HC3")
m2 = smf.ols(f2, E).fit(cov_type="HC3")
guarda("reg.n", int(m1.nobs))
guarda("reg.m1_r2", m1.rsquared)
guarda("reg.m2_r2", m2.rsquared)
from statsmodels.stats.anova import anova_lm  # noqa: E402
m2_sem = smf.ols(f2.replace(" + C(partido_g, Treatment('PL'))", ""), E).fit()
m2_ols = smf.ols(f2, E).fit()
Fp = m2_ols.compare_f_test(m2_sem)
guarda("reg.F_partido", Fp[0])
guarda("reg.p_partido", Fp[1])
nomes = {"log_neff": "log N efetivo", "frac_fiscal": "Fração fiscalização", "mulher": "Mulher",
         "veterano": "Veterano(a)", "suplente": "Suplente/efetivado", "dim1": "dim1 (governo +)",
         "abs_dim1": "|dim1|", "abs_dim1_dentro": "|dim1 − média do partido|"}
linhas = []
for v, rot in nomes.items():
    r_ = []
    for m in (m1, m2):
        if v in m.params:
            r_ += [m.params[v], m.bse[v], m.pvalues[v]]
        else:
            r_ += [np.nan] * 3
    linhas.append([rot] + r_)
for reg in ["Norte", "Nordeste", "Centro-Oeste", "Sul"]:
    v = f"C(regiao, Treatment('Sudeste'))[T.{reg}]"
    linhas.append([f"Região: {reg}"] + sum(([m.params.get(v, np.nan), m.bse.get(v, np.nan), m.pvalues.get(v, np.nan)] for m in (m1, m2)), []))
tabreg = pd.DataFrame(linhas, columns=["Variável", "β (M1)", "EP (M1)", "p (M1)", "β (M2)", "EP (M2)", "p (M2)"])
tabreg.loc[len(tabreg)] = ["Efeitos fixos de partido", np.nan, np.nan, np.nan, np.nan, np.nan, Fp[1]]
tabreg.loc[len(tabreg)] = ["R²", m1.rsquared, np.nan, np.nan, m2.rsquared, np.nan, np.nan]
md_tabela(tabreg, "tab4_correlatos_especializacao", floatfmt=3)
for v in nomes:
    for nm, m in (("m1", m1), ("m2", m2)):
        if v in m.params:
            guarda(f"reg.{nm}.{v}.b", m.params[v])
            guarda(f"reg.{nm}.{v}.p", m.pvalues[v])

# =========================================================== 6. partição da variância
print("6. Partição da variância (PERMANOVA)...")


def ss_total(X):
    return ((X - X.mean(0)) ** 2).sum()


def dummies(lab):
    lab = pd.Series(lab).astype(str)
    return pd.get_dummies(lab, drop_first=True).to_numpy(float)


def ss_explicada(X, Z):
    """SS explicada pela regressão multivariada de X em [1, Z] (PERMANOVA euclidiana)."""
    Z1 = np.column_stack([np.ones(len(X)), Z]) if Z is not None and Z.size else np.ones((len(X), 1))
    B, *_ = np.linalg.lstsq(Z1, X, rcond=None)
    F = Z1 @ B
    return ((F - X.mean(0)) ** 2).sum()


def permanova_seq(X, blocos, nperm=NPERM, rng=RNG):
    """R² sequenciais de blocos de covariáveis, com nulo por permutação das linhas do bloco
    testado (mantendo os anteriores) e R² ajustado pelo nulo."""
    sst = ss_total(X)
    out, Zant = [], np.zeros((len(X), 0))
    ss_ant = ss_explicada(X, Zant)
    for nome, Z in blocos:
        Zc = np.column_stack([Zant, Z])
        ss = ss_explicada(X, Zc) - ss_ant
        nul = np.empty(nperm)
        for b in range(nperm):
            Zp = Z[rng.permutation(len(X))]
            nul[b] = ss_explicada(X, np.column_stack([Zant, Zp])) - ss_ant
        r2, r2n = ss / sst, nul.mean() / sst
        out.append({"bloco": nome, "R2": r2, "R2_nulo": r2n, "R2_aj": (r2 - r2n) / (1 - r2n),
                    "p": (1 + (nul >= ss).sum()) / (nperm + 1), "gl": Z.shape[1]})
        Zant, ss_ant = Zc, ss_explicada(X, Zc)
    return pd.DataFrame(out)


def permanova_um(X, lab, nperm=NPERM):
    return permanova_seq(X, [("g", dummies(lab))], nperm).iloc[0]


part = C["partido"].to_numpy()
Zvol = np.column_stack([np.log(C["neff"]), np.log(C["neff"]) ** 2, C["frac_fiscal"]])
Zdem = np.column_stack([dummies(C["regiao"]), C[["mulher", "veterano", "suplente"]].to_numpy(float)])
seq = permanova_seq(X0, [("volume e instrumento", Zvol), ("partido", dummies(part)),
                         ("UF", dummies(C["siglaUf"])), ("gênero, mandato, suplência", C[["mulher", "veterano", "suplente"]].to_numpy(float))])
for _, r in seq.iterrows():
    k = r["bloco"].split(" ")[0].replace(",", "")
    guarda(f"var.seq.{k}.R2", r["R2"]); guarda(f"var.seq.{k}.R2_aj", r["R2_aj"]); guarda(f"var.seq.{k}.p", r["p"])

# fatores isolados no espaço temático e no espaço de votos (mesmos deputados)
XV = C[["dim1", "dim2"]].to_numpy()
iso = []
for nome, lab in [("partido", part), ("UF", C["siglaUf"]), ("região", C["regiao"]),
                  ("lado (terços de dim1)", C["lado"])]:
    rt = permanova_um(X0, lab)
    rv = permanova_um(XV, lab)
    iso.append([nome, rt["R2"], rt["R2_aj"], rt["p"], rv["R2"], rv["R2_aj"]])
    guarda(f"var.iso.{nome.split(' ')[0]}.temas_R2", rt["R2"])
    guarda(f"var.iso.{nome.split(' ')[0]}.temas_R2_aj", rt["R2_aj"])
    guarda(f"var.iso.{nome.split(' ')[0]}.temas_p", rt["p"])
    guarda(f"var.iso.{nome.split(' ')[0]}.votos_R2", rv["R2"])
    guarda(f"var.iso.{nome.split(' ')[0]}.votos_R2_aj", rv["R2_aj"])
# RDA: variância temática alinhada à posição de voto (dim1, dim2)
rda = permanova_seq(X0, [("ideal", XV)]).iloc[0]
guarda("var.rda_dim12.R2", rda["R2"]); guarda("var.rda_dim12.p", rda["p"])
rda1 = permanova_seq(X0, [("ideal", XV[:, :1])]).iloc[0]
guarda("var.rda_dim1.R2", rda1["R2"])
rda_parc = permanova_seq(X0, [("partido", dummies(part)), ("ideal", XV)]).iloc[1]
guarda("var.rda_dim12_dado_partido.R2", rda_parc["R2"]); guarda("var.rda_dim12_dado_partido.p", rda_parc["p"])

# PERMDISP: dispersão dentro dos partidos (distância ao centróide)
cent = pd.DataFrame(X0).groupby(part).transform("mean").to_numpy()
dist_c = np.sqrt(((X0 - cent) ** 2).sum(1))
grp = [dist_c[part == g] for g in pd.unique(part) if (part == g).sum() >= 5]
Fd, pd_ = stats.f_oneway(*grp)
guarda("var.permdisp_F", Fd); guarda("var.permdisp_p", pd_)

# teto de confiabilidade por divisão aleatória em metades (proposição → metade A ou B)
def split_half(it, w, deps, reps=10, por_ano=False):
    rels, d_ab = [], []
    for r in range(reps if not por_ano else 1):
        if por_ano:
            m = (it["ano"] <= 2024).to_numpy()
        else:
            pa = RNG.random(len(PROPS)) < 0.5
            m = pa[it["pidx"].to_numpy()]
        WA, _, _ = perfil(it, np.where(m, w, 0))
        WB, _, _ = perfil(it, np.where(~m, w, 0))
        ok = [d for d in deps if d in WA.index and d in WB.index and WA.loc[d].sum() >= 1.5 and WB.loc[d].sum() >= 1.5]
        XA, XB = np.sqrt(proporcoes(WA.loc[ok]).to_numpy()), np.sqrt(proporcoes(WB.loc[ok]).to_numpy())
        # variância de ruído do perfil completo ~ E||xA - xB||^2 / 4 (metades têm o dobro do ruído)
        ruido = ((XA - XB) ** 2).sum(1).mean() / 4
        Xf = np.sqrt(P0.loc[ok].to_numpy())
        tot = ss_total(Xf) / len(ok)
        rels.append(1 - ruido / tot)
        d_ab.append((ok, XA, XB))
    return float(np.mean(rels)), d_ab


rel, _ = split_half(IT, w_base, AM, reps=10)
guarda("var.confiabilidade_split_half", rel)
guarda("var.partido_R2_sobre_teto", R["var"]["iso"]["partido"]["temas_R2"] / rel)

tab_iso = pd.DataFrame(iso, columns=["Fator", "R² temas", "R² aj. temas", "p temas", "R² votos", "R² aj. votos"])
md_tabela(tab_iso, "tab5a_variancia_fatores", floatfmt=3)
seqt = seq[["bloco", "gl", "R2", "R2_nulo", "R2_aj", "p"]].copy()
seqt.columns = ["Bloco (entrada sequencial)", "gl", "R²", "R² nulo", "R² ajustado", "p"]
md_tabela(seqt, "tab5b_variancia_sequencial", floatfmt=3)

# R² de partido por tema (ANOVA univariada em sqrt(p)), com FDR
from statsmodels.stats.multitest import multipletests  # noqa: E402
r2t = []
for k, t in enumerate(TEMAS):
    y = X0[:, k]
    if y.std() == 0:
        continue
    gs = [y[part == g] for g in pd.unique(part) if (part == g).sum() >= 3]
    F_, p_ = stats.f_oneway(*gs)
    ssb = sum(len(g) * (g.mean() - y.mean()) ** 2 for g in [y[part == g] for g in pd.unique(part)])
    r2t.append([t, ssb / ((y - y.mean()) ** 2).sum(), p_])
r2t = pd.DataFrame(r2t, columns=["tema", "R2", "p"])
r2t["q"] = multipletests(r2t["p"], method="fdr_bh")[1]
r2t = r2t.sort_values("R2", ascending=False)
guarda("var.tema_maior_R2_partido", f"{r2t.iloc[0]['tema']} ({r2t.iloc[0]['R2']:.3f})")
guarda("var.tema_2_R2_partido", f"{r2t.iloc[1]['tema']} ({r2t.iloc[1]['R2']:.3f})")
guarda("var.tema_3_R2_partido", f"{r2t.iloc[2]['tema']} ({r2t.iloc[2]['R2']:.3f})")
guarda("var.n_temas_q05", int((r2t["q"] < 0.05).sum()))

# Figura 5: partição da variância
fig, ax = plt.subplots(figsize=(7.5, 3.0))
lab_f = ["partido", "UF", "lado (terços de dim1)"]
y_ = np.arange(len(lab_f))
vt = [tab_iso.set_index("Fator").loc[f, "R² aj. temas"] for f in lab_f]
vv = [tab_iso.set_index("Fator").loc[f, "R² aj. votos"] for f in lab_f]
ax.barh(y_ + 0.2, vv, height=0.36, color=COR["laranja"], label="espaço de votos (dim1, dim2)")
ax.barh(y_ - 0.2, vt, height=0.36, color=COR["azul"], label="espaço temático (Hellinger)")
for yy, a, b in zip(y_, vt, vv):
    ax.text(a + 0.01, yy - 0.2, f"{a:.2f}".replace(".", ","), va="center", color=COR["tinta2"])
    ax.text(b + 0.01, yy + 0.2, f"{b:.2f}".replace(".", ","), va="center", color=COR["tinta2"])
ax.set_yticks(y_, lab_f)
ax.invert_yaxis()
ax.set_xlim(0, 1)
ax.set_xlabel("Variância explicada, R² ajustado pelo nulo de permutação")
ax.legend(loc="lower right")
ax.set_title("Quanto cada agrupamento explica da posição de voto e da agenda temática")
salva_fig(fig, "fig5_variancia")

# =========================================================== 7. ideologia: previsão de dim1
print("7. Previsão da posição de voto e do partido...")
from sklearn.linear_model import RidgeCV, LogisticRegression  # noqa: E402
from sklearn.model_selection import KFold, cross_val_predict, cross_val_score, StratifiedKFold  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402
from sklearn.metrics import balanced_accuracy_score  # noqa: E402

# reprodução exata de avaliar() de embeddings_deputados.py
er = ET_REF[ET_REF["confiavel"]]
Xr = er[[c for c in er.columns if c.startswith("t_")]].to_numpy(float)
alvo = EV[EV["confiavel"]].set_index("deputado_id")["dim1"]
yr = alvo.reindex(er["deputado_id"]).to_numpy()
mr = ~np.isnan(yr)
pr = cross_val_predict(RidgeCV(alphas=np.logspace(-3, 3, 13)), Xr[mr], yr[mr], cv=5)
guarda("ideo.reproducao_r2_dim1", 1 - np.mean((pr - yr[mr]) ** 2) / np.var(yr[mr]))
pp = er["siglaPartido"].to_numpy()
cm = pd.Series(pp).value_counts()
okp = pd.Series(pp).isin(cm[cm >= 5].index).to_numpy()
guarda("ideo.reproducao_knn_partido", cross_val_score(KNeighborsClassifier(5, metric="euclidean"), Xr[okp], pp[okp], cv=5).mean())
guarda("ideo.reproducao_acaso_partido", (cm / cm.sum()).max())


def cv_r2(X, y, grupos=None, reps=10, dentro=False, so_grupo=False):
    """R² fora da amostra (5-fold repetido). dentro=True: prevê o desvio de y em relação à
    média do partido (estimada no treino). so_grupo=True: só efeitos de partido."""
    res = []
    for r in range(reps):
        kf = KFold(5, shuffle=True, random_state=SEED + r)
        pred = np.zeros_like(y)
        alvo_res = np.zeros_like(y)
        for tr, te in kf.split(X):
            if grupos is not None:
                mg = pd.Series(y[tr]).groupby(grupos[tr]).mean()
                base_tr = pd.Series(grupos[tr]).map(mg).to_numpy()
                base_te = pd.Series(grupos[te]).map(mg).fillna(y[tr].mean()).to_numpy()
            else:
                base_tr, base_te = np.full(len(tr), y[tr].mean()), np.full(len(te), y[tr].mean())
            if so_grupo:
                pred[te] = base_te
            else:
                m = RidgeCV(alphas=np.logspace(-3, 3, 13)).fit(X[tr], y[tr] - base_tr)
                pred[te] = base_te + m.predict(X[te])
            alvo_res[te] = y[te] - base_te
        if dentro:
            res.append(1 - np.sum((y - pred) ** 2) / np.sum(alvo_res ** 2))
        else:
            res.append(1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))
    return float(np.mean(res)), float(np.std(res))


y1 = C["dim1"].to_numpy()
pg = np.where(C["partido"].map(C["partido"].value_counts()) >= 3, C["partido"], "Outros")
r_perf = cv_r2(X0, y1)
r_part = cv_r2(X0, y1, grupos=pg, so_grupo=True)
r_ambos = cv_r2(X0, y1, grupos=pg)
r_dentro = cv_r2(X0, y1, grupos=pg, dentro=True)
guarda("ideo.r2_dim1_perfil", r_perf[0]); guarda("ideo.r2_dim1_perfil_sd", r_perf[1])
guarda("ideo.r2_dim1_partido", r_part[0])
guarda("ideo.r2_dim1_partido_mais_perfil", r_ambos[0])
guarda("ideo.r2_dim1_incremento", r_ambos[0] - r_part[0])
guarda("ideo.r2_dim1_dentro_partido", r_dentro[0]); guarda("ideo.r2_dim1_dentro_partido_sd", r_dentro[1])
# nulo do R² do perfil: y permutado
nul = [cv_r2(X0, RNG.permutation(y1), reps=1)[0] for _ in range(20 if ARGS.rapido else 100)]
guarda("ideo.r2_dim1_perfil_nulo_p95", np.percentile(nul, 95))
# controle por volume/instrumento: quanto o mix de tipos sozinho prevê
Zmix = np.column_stack([C["frac_fiscal"], np.log(C["neff"])])
guarda("ideo.r2_dim1_so_mix", cv_r2(Zmix, y1)[0])
guarda("ideo.r2_dim1_perfil_mais_mix", cv_r2(np.column_stack([X0, Zmix]), y1)[0])
guarda("ideo.spearman_fracfiscal_dim1", stats.spearmanr(C["frac_fiscal"], y1)[0])

# partido: regressão logística multinomial, acurácia balanceada vs acaso
okc = C["partido"].map(C["partido"].value_counts()) >= 10
Xp, yp = X0[okc.to_numpy()], C["partido"][okc].to_numpy()
skf = StratifiedKFold(5, shuffle=True, random_state=SEED)
lr = LogisticRegression(C=1.0, max_iter=3000)
pp_ = cross_val_predict(lr, Xp, yp, cv=skf)
guarda("ideo.partido_n_classes", len(np.unique(yp)))
guarda("ideo.partido_acc", (pp_ == yp).mean())
guarda("ideo.partido_acc_bal", balanced_accuracy_score(yp, pp_))
guarda("ideo.partido_acaso_bal", 1 / len(np.unique(yp)))
guarda("ideo.partido_majoritaria", pd.Series(yp).value_counts(normalize=True).max())
pv_ = cross_val_predict(LogisticRegression(max_iter=3000), C[["dim1", "dim2"]][okc].to_numpy(), yp, cv=skf)
guarda("ideo.partido_acc_bal_votos", balanced_accuracy_score(yp, pv_))

# =========================================================== 8. issue ownership
print("8. Issue ownership...")


def ownership(Pmat, lado, nboot=NBOOT, nperm=NPERM):
    """Diferença (pontos percentuais) entre a proporção média de cada tema entre deputados
    da oposição e da base; IC por bootstrap de deputados; p por permutação de rótulos; BH."""
    Pm_ = np.asarray(Pmat)
    o, b = lado == "oposição", lado == "base"
    dif = 100 * (Pm_[o].mean(0) - Pm_[b].mean(0))
    io, ib = np.where(o)[0], np.where(b)[0]
    boots = np.empty((nboot, Pm_.shape[1]))
    for s in range(nboot):
        boots[s] = 100 * (Pm_[RNG.choice(io, len(io))].mean(0) - Pm_[RNG.choice(ib, len(ib))].mean(0))
    sub = np.concatenate([io, ib])
    cnt = np.zeros(Pm_.shape[1])
    for s in range(nperm):
        pr_ = RNG.permutation(sub)
        d_ = 100 * (Pm_[pr_[:len(io)]].mean(0) - Pm_[pr_[len(io):]].mean(0))
        cnt += np.abs(d_) >= np.abs(dif)
    pv = (1 + cnt) / (nperm + 1)
    q_ = multipletests(pv, method="fdr_bh")[1]
    return pd.DataFrame({"tema": TEMAS, "dif_pp": dif, "ic_inf": np.percentile(boots, 2.5, 0),
                         "ic_sup": np.percentile(boots, 97.5, 0), "p": pv, "q": q_,
                         "media_op": 100 * Pm_[o].mean(0), "media_base": 100 * Pm_[b].mean(0)})


lado = C["lado"].to_numpy()
OWN = ownership(P0.loc[AM].to_numpy(), lado)

# perfis por instrumento (só deputados com volume mínimo em cada um)
def perfil_variante(**kw):
    w = pesos_itens(IT, **{k: v for k, v in kw.items() if k in ("fracionar", "tipos", "peso_tipo", "padrao", "so_primeiro", "so_proponente")})
    tp = kw.get("tp", TP_FRAC)
    W, vol, neff = perfil(IT, w, tp=tp, excluir=kw.get("excluir"))
    return proporcoes(W), vol, neff


Pproj, Vproj, Nproj = perfil_variante(tipos=PROJETOS)
Pfis, Vfis, Nfis = perfil_variante(tipos=FISCAL, peso_tipo={t: 1.0 for t in FISCAL})
AMp = [d for d in AM if d in Vproj.index and Vproj[d] >= 3]
AMf = [d for d in AM if d in Vfis.index and Vfis[d] >= 3]
OWNp = ownership(Pproj.loc[AMp].to_numpy(), C.loc[AMp, "lado"].to_numpy())
OWNf = ownership(Pfis.loc[AMf].to_numpy(), C.loc[AMf, "lado"].to_numpy())
guarda("own.n_proj", len(AMp)); guarda("own.n_fis", len(AMf))
for nome, O in [("geral", OWN), ("proj", OWNp), ("fis", OWNf)]:
    s_ = O.sort_values("dif_pp")
    guarda(f"own.{nome}.n_q05", int((O["q"] < 0.05).sum()))
    guarda(f"own.{nome}.top_oposicao", "; ".join(f"{r.tema} ({r.dif_pp:+.1f} pp)" for r in s_.iloc[::-1].head(4).itertuples()))
    guarda(f"own.{nome}.top_base", "; ".join(f"{r.tema} ({r.dif_pp:+.1f} pp)" for r in s_.head(4).itertuples()))
    guarda(f"own.{nome}.soma_abs_dif_pp", O["dif_pp"].abs().sum() / 2)
guarda("own.corr_proj_fis", stats.spearmanr(OWNp["dif_pp"], OWNf["dif_pp"])[0])
# quantos deputados de cada lado usam fiscalização
for l_ in ["oposição", "centro", "base"]:
    dd = C[C["lado"] == l_].index
    guarda(f"own.fis_por_dep.{l_}", Wf.sum(1).reindex(dd).fillna(0).mean() / 0.3)
# sobreposição: distância de Hellinger e JSD entre agendas médias, vs nulo de rótulos
def hell(p, q):
    return np.sqrt(0.5 * ((np.sqrt(p) - np.sqrt(q)) ** 2).sum())


def jsd(p, q):
    m = (p + q) / 2
    kl = lambda a, b: np.sum(np.where(a > 0, a * np.log(a / b), 0))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def sobreposicao(Pm_, lado_):
    Pm_ = np.asarray(Pm_)
    o, b = lado_ == "oposição", lado_ == "base"
    obs = jsd(Pm_[o].mean(0), Pm_[b].mean(0))
    sub = np.where(o | b)[0]
    nul = []
    for s in range(NPERM):
        pr_ = RNG.permutation(sub)
        nul.append(jsd(Pm_[pr_[:o.sum()]].mean(0), Pm_[pr_[o.sum():]].mean(0)))
    nul = np.array(nul)
    return obs, nul.mean(), (1 + (nul >= obs).sum()) / (NPERM + 1), hell(Pm_[o].mean(0), Pm_[b].mean(0))


for nome, Pm_, l_ in [("geral", P0.loc[AM], lado), ("proj", Pproj.loc[AMp], C.loc[AMp, "lado"].to_numpy()),
                      ("fis", Pfis.loc[AMf], C.loc[AMf, "lado"].to_numpy())]:
    o_, n_, p_, h_ = sobreposicao(Pm_, l_)
    guarda(f"own.{nome}.jsd", o_); guarda(f"own.{nome}.jsd_nulo", n_); guarda(f"own.{nome}.jsd_p", p_)
    guarda(f"own.{nome}.hellinger_agendas", h_)
    # quanto da diferença é de grau: semelhança de ranking dos temas entre os lados
    oo = np.asarray(Pm_)[l_ == "oposição"].mean(0); bb = np.asarray(Pm_)[l_ == "base"].mean(0)
    guarda(f"own.{nome}.spearman_rank_lados", stats.spearmanr(oo, bb)[0])

tab_own = OWNp[["tema", "media_op", "media_base", "dif_pp", "ic_inf", "ic_sup", "q"]].merge(
    OWNf[["tema", "media_op", "media_base", "dif_pp", "q"]], on="tema", suffixes=(" proj", " fisc"))
tab_own = tab_own.sort_values("dif_pp proj", ascending=False)
tab_own["tema"] = tab_own["tema"].map(ab)
tab_own.columns = ["Tema", "Oposição % (proj.)", "Base % (proj.)", "Dif. pp (proj.)", "IC 2,5%", "IC 97,5%",
                   "q (proj.)", "Oposição % (fisc.)", "Base % (fisc.)", "Dif. pp (fisc.)", "q (fisc.)"]
md_tabela(tab_own, "tab6_ownership", floatfmt=2)

# Figura 3: ownership em projetos e fiscalização
O3 = OWNp.set_index("tema")[["dif_pp", "ic_inf", "ic_sup", "q"]].join(
    OWNf.set_index("tema")[["dif_pp", "ic_inf", "ic_sup", "q"]], rsuffix="_f")
O3 = O3[(O3[["dif_pp", "dif_pp_f"]].abs().max(1) >= 0.3)].sort_values("dif_pp")
fig, ax = plt.subplots(figsize=(7.5, 0.24 * len(O3) + 1.2))
yy = np.arange(len(O3))
ax.axvline(0, color=COR["tinta2"], lw=0.8)
ax.errorbar(O3["dif_pp"], yy + 0.15, xerr=[O3["dif_pp"] - O3["ic_inf"], O3["ic_sup"] - O3["dif_pp"]],
            fmt="o", ms=4.5, color=COR["azul"], ecolor=COR["azul"], elinewidth=1, label="projetos (PL, PLP, PEC, PDL, PRC)")
ax.errorbar(O3["dif_pp_f"], yy - 0.15, xerr=[O3["dif_pp_f"] - O3["ic_inf_f"], O3["ic_sup_f"] - O3["dif_pp_f"]],
            fmt="s", ms=4, color=COR["laranja"], ecolor=COR["laranja"], elinewidth=1, label="fiscalização (RIC, INC, PFC, SIT)")
ax.set_yticks(yy, [ab(t) for t in O3.index])
ax.set_xlabel("Proporção média na agenda da oposição − na da base (pontos percentuais), IC 95%")
ax.text(0.99, -0.06, "mais da oposição →", transform=ax.transAxes, ha="right", va="top", color=COR["tinta2"])
ax.text(0.01, -0.06, "← mais da base", transform=ax.transAxes, ha="left", va="top", color=COR["tinta2"])
ax.legend(loc="lower right")
ax.set_title("Propriedade de temas: oposição × base (terços de dim1)")
salva_fig(fig, "fig3_ownership")

# Figura 4: partido × tema (log da razão em relação à média da Câmara), projetos
grandes_p = C["partido"].value_counts()
gp = grandes_p[grandes_p >= 8].index
ordem_p = C[C["partido"].isin(gp)].groupby("partido")["dim1"].median().sort_values().index
camara = P0.loc[AM].mean(0)
temas_top = camara.sort_values(ascending=False).head(20).index
LR = pd.DataFrame({g: np.log2((P0.loc[C.index[C["partido"] == g]].mean(0) + 0.002) / (camara + 0.002))
                   for g in ordem_p}).T[temas_top]
fig, ax = plt.subplots(figsize=(9, 0.32 * len(ordem_p) + 2.6))
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
cmap = LinearSegmentedColormap.from_list("div", ["#1c5cab", "#86b6ef", COR["neutro"], "#ef9a9a", "#c62f2f"])
im = ax.imshow(LR.to_numpy(), cmap=cmap, vmin=-1.5, vmax=1.5, aspect="auto")
ax.set_xticks(range(len(temas_top)), [ab(t) for t in temas_top], rotation=55, ha="right")
nn = C["partido"].value_counts()
ax.set_yticks(range(len(ordem_p)), [f"{g} (n={nn[g]})" for g in ordem_p])
ax.grid(False)
cb = fig.colorbar(im, ax=ax, shrink=0.8)
cb.set_label("log2(proporção no partido / na Câmara)")
ax.set_title("Agenda dos partidos em relação à média da Câmara\n(partidos ordenados por dim1 mediano: oposição no topo, base embaixo)")
salva_fig(fig, "fig4_partido_tema")

# =========================================================== 9. projetos x fiscalização
print("9. Projetos × fiscalização...")
both = [d for d in AM if d in AMp and d in AMf]
guarda("instr.n_ambos", len(both))
hpf = np.array([hell(Pproj.loc[d].to_numpy(), Pfis.loc[d].to_numpy()) for d in both])
perm_ = RNG.permutation(len(both))
hpf_out = np.array([hell(Pproj.loc[both[i]].to_numpy(), Pfis.loc[both[j]].to_numpy()) for i, j in zip(range(len(both)), perm_)])
guarda("instr.hell_mesmo_dep_mediana", np.median(hpf))
guarda("instr.hell_outro_dep_mediana", np.median(hpf_out))
# agregados
agg_proj = (Pproj.loc[AMp].mean(0)); agg_fis = Pfis.loc[AMf].mean(0)
guarda("instr.hell_agregados", hell(agg_proj.to_numpy(), agg_fis.to_numpy()))
for t in ["Agricultura, Pecuária, Pesca e Extrativismo", "Administração Pública", "Direitos Humanos e Minorias",
          "Saúde", "Educação", "Defesa e Segurança", "Meio Ambiente e Desenvolvimento Sustentável", "Homenagens e Datas Comemorativas"]:
    guarda(f"instr.tema.{ab(t)}.proj", 100 * agg_proj[t]); guarda(f"instr.tema.{ab(t)}.fis", 100 * agg_fis[t])
# sinal ideológico de cada instrumento (mesmos deputados)
yb = C.loc[both, "dim1"].to_numpy(); pgb = pd.Series(pg, index=C.index).loc[both].to_numpy()
Xpb, Xfb = np.sqrt(Pproj.loc[both].to_numpy()), np.sqrt(Pfis.loc[both].to_numpy())
guarda("instr.r2_dim1_proj", cv_r2(Xpb, yb)[0])
guarda("instr.r2_dim1_fis", cv_r2(Xfb, yb)[0])
guarda("instr.r2_dim1_proj_dentro", cv_r2(Xpb, yb, grupos=pgb, dentro=True)[0])
guarda("instr.r2_dim1_fis_dentro", cv_r2(Xfb, yb, grupos=pgb, dentro=True)[0])
pb_ = C.loc[both, "partido"].to_numpy()
guarda("instr.R2aj_partido_proj", permanova_um(Xpb, pb_)["R2_aj"])
guarda("instr.R2aj_partido_fis", permanova_um(Xfb, pb_)["R2_aj"])

# =========================================================== 10. tipos de agenda (k-means)
print("10. Tipos de agenda (k-means) contra nulo...")
from sklearn.cluster import KMeans  # noqa: E402
from sklearn.metrics import silhouette_score, adjusted_rand_score  # noqa: E402
sil, sil_nul = {}, {}
for k in range(2, 11):
    km = KMeans(k, n_init=10, random_state=SEED).fit(X0)
    sil[k] = silhouette_score(X0, km.labels_)
    sn = []
    for r in range(5 if ARGS.rapido else 10):
        Pp = P0.loc[AM].to_numpy().copy()
        for j in range(K):
            Pp[:, j] = Pp[RNG.permutation(len(Pp)), j]
        Pp = Pp / np.where(Pp.sum(1, keepdims=True) > 0, Pp.sum(1, keepdims=True), 1)
        Xn = np.sqrt(Pp)
        sn.append(silhouette_score(Xn, KMeans(k, n_init=5, random_state=r).fit_predict(Xn)))
    sil_nul[k] = float(np.mean(sn))
exc = {k: sil[k] - sil_nul[k] for k in sil}
kbest = max(exc, key=exc.get)
guarda("clus.k_escolhido", kbest)
guarda("clus.silhueta", sil[kbest]); guarda("clus.silhueta_nulo", sil_nul[kbest])
guarda("clus.silhuetas", {str(k): round(v, 3) for k, v in sil.items()})
guarda("clus.silhuetas_nulo", {str(k): round(v, 3) for k, v in sil_nul.items()})
km = KMeans(kbest, n_init=20, random_state=SEED).fit(X0)
lab_k = km.labels_
guarda("clus.ari_partido", adjusted_rand_score(part, lab_k))
guarda("clus.ari_lado", adjusted_rand_score(lado, lab_k))
aris = []
for b in range(20 if ARGS.rapido else 50):
    ii = RNG.choice(len(X0), len(X0))
    kb = KMeans(kbest, n_init=5, random_state=b).fit(X0[ii])
    aris.append(adjusted_rand_score(lab_k, kb.predict(X0)))
guarda("clus.estabilidade_ari", np.mean(aris))
linhas = []
for c_ in range(kbest):
    m_ = lab_k == c_
    prof = P0.loc[AM][m_].mean(0).sort_values(ascending=False)
    pc = C["partido"][m_].value_counts(normalize=True).head(3)
    lc = pd.Series(lado[m_]).value_counts(normalize=True)
    linhas.append([c_ + 1, int(m_.sum()), "; ".join(f"{ab(t)} {100*v:.0f}%" for t, v in prof.head(3).items()),
                   "; ".join(f"{k} {100*v:.0f}%" for k, v in pc.items()),
                   100 * lc.get("oposição", 0), 100 * lc.get("base", 0), C["dim1"][m_].mean()])
tab_clus = pd.DataFrame(linhas, columns=["Tipo", "n", "Temas principais (proporção média)", "Partidos principais",
                                         "% oposição", "% base", "dim1 médio"])
md_tabela(tab_clus, "tab7_tipos_agenda", floatfmt=1)

# =========================================================== 11. divisão do trabalho
print("11. Divisão do trabalho nos partidos...")


def decomp(Pm_):
    Pm_ = np.asarray(Pm_)
    alpha = entropia(Pm_).mean()
    gamma = entropia(Pm_.mean(0))
    return alpha, gamma, gamma - alpha


it_am = IT[IT["dep"].isin(AM) & (w_base > 0)].reset_index(drop=True)
w_am = pesos_itens(it_am)
linhas = []
todos = np.arange(len(AM))
Pam = P0.loc[AM].to_numpy()
for g in C["partido"].value_counts()[lambda s: s >= 8].index:
    membros = list(C.index[C["partido"] == g])
    a_, g_, b_ = decomp(P0.loc[membros])
    # nulo 1: partidos aleatórios do mesmo tamanho
    n1 = np.array([decomp(Pam[RNG.choice(todos, len(membros), replace=False)])[2] for _ in range(200 if ARGS.rapido else 500)])
    # nulo 2: itens embaralhados entre os membros (preserva n.º de itens e volume de cada um)
    sub = it_am[it_am["dep"].isin(membros)].reset_index(drop=True)
    ws = pesos_itens(sub)
    n2 = []
    for _ in range(50 if ARGS.rapido else 200):
        sh = sub.copy()
        perm_i = RNG.permutation(len(sh))
        sh["pidx"] = sh["pidx"].to_numpy()[perm_i]
        sh["n_aut"] = sh["n_aut"].to_numpy()[perm_i]
        sh["siglaTipo"] = sh["siglaTipo"].to_numpy()[perm_i]
        Wsh, _, _ = perfil(sh, pesos_itens(sh))
        n2.append(decomp(proporcoes(Wsh))[2])
    n2 = np.array(n2)
    linhas.append([g, len(membros), C.loc[membros, "dim1"].median(), np.exp(a_), np.exp(g_), b_,
                   n1.mean(), (1 + (n1 <= b_).sum()) / (len(n1) + 1), n2.mean(), b_ - n2.mean(),
                   (1 + (n2 >= b_).sum()) / (len(n2) + 1)])
DL = pd.DataFrame(linhas, columns=["partido", "n", "dim1_med", "alfa_Teff", "gama_Teff", "beta",
                                   "beta_nulo_aleat", "p_menor_aleat", "beta_nulo_embar", "beta_excesso", "p_maior_embar"])
DL = DL.sort_values("dim1_med")
guarda("div.n_partidos", len(DL))
guarda("div.n_beta_menor_aleat_p05", int((DL["p_menor_aleat"] < 0.05).sum()))
guarda("div.n_beta_maior_embar_p05", int((DL["p_maior_embar"] < 0.05).sum()))
guarda("div.spearman_excesso_tamanho", stats.spearmanr(DL["beta_excesso"], DL["n"])[0])
guarda("div.spearman_excesso_tamanho_p", stats.spearmanr(DL["beta_excesso"], DL["n"])[1])
guarda("div.razao_beta_nulo_aleat_mediana", (DL["beta"] / DL["beta_nulo_aleat"]).median())
guarda("div.excesso_sobre_beta_mediana", (DL["beta_excesso"] / DL["beta"]).median())
tdl = DL.copy()
tdl.columns = ["Partido", "n", "dim1 mediano", "Temas efetivos por membro (α)", "Temas efetivos do partido (γ)",
               "β = ln γ − ln α", "β nulo: grupos aleatórios", "p (β menor)", "β nulo: itens embaralhados",
               "Excesso de β", "p (β maior)"]
md_tabela(tdl, "tab8_divisao_trabalho", floatfmt=3)

fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.scatter(DL["n"], DL["beta"], s=26, color=COR["azul"], label="β observado", zorder=3)
ax.scatter(DL["n"], DL["beta_nulo_aleat"], s=22, marker="s", color=COR["mudo"], label="nulo: grupos aleatórios", zorder=2)
ax.scatter(DL["n"], DL["beta_nulo_embar"], s=26, marker="^", color=COR["laranja"], label="nulo: itens embaralhados no partido", zorder=2)
for r in DL.itertuples():
    ax.annotate(r.partido, (r.n, r.beta), xytext=(4, 3), textcoords="offset points", fontsize=7.5, color=COR["tinta2"])
ax.set_xscale("log")
ax.set_xlabel("Deputados do partido na amostra (escala log)")
ax.set_ylabel("β (nats): diversidade entre membros")
ax.legend(loc="lower right", fontsize=8)
ax.set_title("Divisão do trabalho temático dentro dos partidos")
salva_fig(fig, "fig6_divisao_trabalho")

# =========================================================== 12. estabilidade e frentes
print("12. Estabilidade temporal e validação por frentes...")


def reidentificacao(XA, XB):
    Dm = np.sqrt(((XA[:, None, :] - XB[None, :, :]) ** 2).sum(-1))
    proprio = np.diag(Dm)
    rank1 = (Dm.argmin(1) == np.arange(len(XA))).mean()
    outros_ = Dm[~np.eye(len(XA), dtype=bool)].reshape(len(XA), -1)
    return rank1, np.median(proprio) / np.sqrt(2), np.median(outros_) / np.sqrt(2), (outros_ > proprio[:, None]).mean()


_, sp_ano = split_half(IT, w_base, AM, por_ano=True)
ok_a, XA, XB = sp_ano[0]
r1, dp_, do_, auc = reidentificacao(XA, XB)
guarda("estab.n_ano", len(ok_a)); guarda("estab.reid_ano", r1); guarda("estab.hell_proprio_ano", dp_)
guarda("estab.hell_outros_ano", do_); guarda("estab.auc_ano", auc)
_, sp_al = split_half(IT, w_base, AM, reps=1)
ok_r, XAr, XBr = sp_al[0]
r1r, dpr, dor, aucr = reidentificacao(XAr, XBr)
guarda("estab.n_aleat", len(ok_r)); guarda("estab.reid_aleat", r1r); guarda("estab.hell_proprio_aleat", dpr)
guarda("estab.auc_aleat", aucr)
# distância a colegas de partido (metade temporal)
pa_ = C.loc[ok_a, "partido"].to_numpy()
Dm = np.sqrt(((XA[:, None, :] - XB[None, :, :]) ** 2).sum(-1)) / np.sqrt(2)
mesmo = (pa_[:, None] == pa_[None, :]) & ~np.eye(len(pa_), dtype=bool)
guarda("estab.hell_mesmo_partido_ano", np.median(Dm[mesmo]))
guarda("estab.hell_outro_partido_ano", np.median(Dm[(pa_[:, None] != pa_[None, :])]))
guarda("estab.reid_acaso", 1 / len(ok_a))

# frentes: correlação de Mantel entre distâncias temáticas e de frentes
from sklearn.metrics import pairwise_distances  # noqa: E402
ef = EF[EF["confiavel"]].set_index("deputado_id")
cf = [c for c in ef.columns if c.startswith("dim")]
comum = [d for d in AM if d in ef.index]
Dt = pairwise_distances(np.sqrt(P0.loc[comum].to_numpy()))
Df = pairwise_distances(ef.loc[comum, cf].to_numpy(), metric="cosine")
Dv = pairwise_distances(C.loc[comum, ["dim1", "dim2"]].to_numpy())
iu = np.triu_indices(len(comum), 1)
pc_ = C.loc[comum, "partido"].to_numpy()
mp = (pc_[:, None] == pc_[None, :])[iu]


def mantel(D1, D2, mask=None, nperm=199 if not ARGS.rapido else 49):
    a, b = D1[iu], D2[iu]
    if mask is not None:
        a, b = a[mask], b[mask]
    obs = stats.spearmanr(a, b)[0]
    cnt = 0
    for _ in range(nperm):
        pr_ = RNG.permutation(len(comum))
        b2 = D2[np.ix_(pr_, pr_)][iu]
        if mask is not None:
            b2 = b2[mask]
        cnt += stats.spearmanr(a, b2)[0] >= obs
    return obs, (1 + cnt) / (nperm + 1)


guarda("frentes.n", len(comum))
o_, p_ = mantel(Dt, Df); guarda("frentes.mantel_temas_frentes", o_); guarda("frentes.mantel_temas_frentes_p", p_)
o_, p_ = mantel(Dt, Df, mp); guarda("frentes.mantel_temas_frentes_mesmo_partido", o_); guarda("frentes.mantel_temas_frentes_mesmo_partido_p", p_)
o_, p_ = mantel(Dt, Dv); guarda("frentes.mantel_temas_votos", o_); guarda("frentes.mantel_temas_votos_p", p_)
o_, p_ = mantel(Dt, Dv, mp); guarda("frentes.mantel_temas_votos_mesmo_partido", o_)
# validação substantiva: membros de frentes temáticas têm mais do tema?
FD = pd.read_parquet(PASTA / "frentes_deputados.parquet")
FR = pd.read_parquet(PASTA / "frentes.parquet")
tit_col = "titulo" if "titulo" in FR.columns else [c for c in FR.columns if "titulo" in c.lower()][0]
idf_col = "id" if "id" in FR.columns else FR.columns[0]
FR["tnorm"] = FR[tit_col].map(sem_acento)
mapa_frente = {"Agricultura, Pecuária, Pesca e Extrativismo": r"agropecuar",
               "Saúde": r"\bsaude\b", "Educação": r"\beducacao\b",
               "Defesa e Segurança": r"seguranca publica",
               "Meio Ambiente e Desenvolvimento Sustentável": r"ambientalista|meio ambiente",
               "Direitos Humanos e Minorias": r"direitos humanos|lgbt|indigena|antirracis|pessoa com deficiencia",
               "Esporte e Lazer": r"\besporte", "Turismo": r"\bturismo"}
fd_dep = [c for c in FD.columns if "deputado" in c.lower() and "id" in c.lower()][0]
fd_fr = [c for c in FD.columns if "frente" in c.lower()][0]
linhas = []
for tema, rx in mapa_frente.items():
    fids = FR.loc[FR["tnorm"].str.contains(rx, regex=True), idf_col].astype(str)
    memb = set(FD.loc[FD[fd_fr].astype(str).isin(fids), fd_dep].astype(int))
    m_ = np.array([d in memb for d in AM])
    if m_.sum() < 5 or (~m_).sum() < 5:
        continue
    pm = P0.loc[AM, tema].to_numpy()
    u = stats.mannwhitneyu(pm[m_], pm[~m_])
    linhas.append([ab(tema), len(fids), int(m_.sum()), 100 * pm[m_].mean(), 100 * pm[~m_].mean(),
                   u.statistic / (m_.sum() * (~m_).sum()), u.pvalue])
tab_fr = pd.DataFrame(linhas, columns=["Tema", "Frentes", "Membros na amostra", "% tema (membros)",
                                       "% tema (não membros)", "AUC", "p (Mann-Whitney)"])
md_tabela(tab_fr, "tab9_validacao_frentes", floatfmt=3)
guarda("frentes.auc_mediana", tab_fr["AUC"].median())
guarda("frentes.n_temas_testados", len(tab_fr))

# =========================================================== 13. sensibilidade
print("13. Sensibilidade aos pesos...")
variantes = {
    "Referência (autoria fracionada; projeto 1, demais 0,3)": dict(),
    "Sem fracionar a autoria": dict(fracionar=False),
    "Só primeiro signatário": dict(so_primeiro=True),
    "Só proponentes": dict(so_proponente=True),
    "Só projetos": dict(tipos=PROJETOS),
    "Só fiscalização (RIC, INC, PFC, SIT)": dict(tipos=FISCAL),
    "Todos os tipos com peso 1": dict(peso_tipo=None),
    "Peso integral por tema (sem 1/k)": dict(tp=TP_INT),
    "Sem Administração Pública": dict(excluir=["Administração Pública"]),
}
linhas = []
Hbase = pd.Series(entropia(P0.loc[AM]), AM)
for nome, kw in variantes.items():
    Pv, Vv, Nv = perfil_variante(**kw)
    Pv = Pv.fillna(0)
    am_v = [d for d in AM if d in Vv.index and Vv[d] >= 3 and Pv.loc[d].sum() > 0]
    Xv = np.sqrt(Pv.loc[am_v].to_numpy())
    yv = C.loc[am_v, "dim1"].to_numpy()
    pgv = pd.Series(pg, index=C.index).loc[am_v].to_numpy()
    r2v = cv_r2(Xv, yv, reps=3)[0]
    r2d = cv_r2(Xv, yv, grupos=pgv, dentro=True, reps=3)[0]
    pmv = permanova_um(Xv, C.loc[am_v, "partido"].to_numpy(), nperm=199 if not ARGS.rapido else 49)
    Ov = ownership(Pv.loc[am_v].to_numpy(), C.loc[am_v, "lado"].to_numpy(), nboot=10, nperm=10)
    Ov = Ov.sort_values("dif_pp")
    rho = stats.spearmanr(entropia(Pv.loc[am_v]), Hbase.loc[am_v])[0]
    dh = np.median([hell(Pv.loc[d].to_numpy(), P0.loc[d].to_numpy()) for d in am_v])
    linhas.append([nome, len(am_v), r2v, r2d, pmv["R2_aj"], rho, dh,
                   ", ".join(ab(t) for t in Ov["tema"].iloc[::-1].head(3)),
                   ", ".join(ab(t) for t in Ov["tema"].head(3))])
# CLR em vez de Hellinger (mesmo perfil de referência)
Pc = P0.loc[AM].to_numpy()
neffc = C["neff"].to_numpy()[:, None]
Pz = np.where(Pc > 0, Pc, 1 / (2 * np.maximum(neffc, 1)))
Pz = Pz / Pz.sum(1, keepdims=True)
Xclr = np.log(Pz) - np.log(Pz).mean(1, keepdims=True)
linhas.append(["CLR (zeros substituídos por 1/2N) em vez de Hellinger", len(AM), cv_r2(Xclr, y1, reps=3)[0],
               cv_r2(Xclr, y1, grupos=pg, dentro=True, reps=3)[0],
               permanova_um(Xclr, part, nperm=199 if not ARGS.rapido else 49)["R2_aj"], np.nan, np.nan, "=", "="])
SENS = pd.DataFrame(linhas, columns=["Variante", "n", "R² dim1", "R² dim1 dentro do partido", "R² aj. partido",
                                     "ρ entropia × ref.", "Hellinger mediana à ref.", "Temas mais da oposição", "Temas mais da base"])
md_tabela(SENS, "tab10_sensibilidade", floatfmt=3)
for r in SENS.itertuples():
    k = re.sub(r"[^a-z0-9]+", "_", sem_acento(r.Variante))[:30]
    guarda(f"sens.{k}.n", r.n); guarda(f"sens.{k}.r2_dim1", r._3); guarda(f"sens.{k}.r2_dentro", r._4)
    guarda(f"sens.{k}.R2aj_partido", r._5)
guarda("sens.r2_dim1_min", SENS["R² dim1"].min()); guarda("sens.r2_dim1_max", SENS["R² dim1"].max())
guarda("sens.r2_partido_min", SENS["R² aj. partido"].min()); guarda("sens.r2_partido_max", SENS["R² aj. partido"].max())

# =========================================================== 14. pauta votada e tempo
print("14. Pauta votada e evolução anual...")
pids = pauta_ids()
pv_cnt = pd.Series(pids).value_counts()
guarda("pauta.n_votacoes_nominais_plen", int((V["siglaOrgao"].eq("PLEN") & V["tem_votos_nominais"]).sum()))
guarda("pauta.n_proposicoes", len(pv_cnt))
TT = pd.concat([T[["idProposicao", "tema"]], TEMAS_PAUTA_API[["idProposicao", "tema"]]]).dropna().drop_duplicates()
TT = TT[TT["tema"].isin(TEMAS)]
tp_ = TT[TT["idProposicao"].isin(pv_cnt.index)].copy()
tp_["w"] = 1 / tp_.groupby("idProposicao")["tema"].transform("size")
guarda("pauta.n_com_tema", tp_["idProposicao"].nunique())
pauta = tp_.groupby("tema")["w"].sum().reindex(TEMAS).fillna(0)
pauta = pauta / pauta.sum()
tp_["wv"] = tp_["w"] * tp_["idProposicao"].map(pv_cnt)
pauta_v = tp_.groupby("tema")["wv"].sum().reindex(TEMAS).fillna(0)
pauta_v = pauta_v / pauta_v.sum()
# agenda apresentada agregada (cada proposição uma vez)
def agenda_agregada(tipos):
    ids = [PIDX[p] for p in P.loc[P["siglaTipo"].isin(tipos) & P["tem_tema"], "id"]]
    v = TP_FRAC[ids].sum(0)
    return pd.Series(v / v.sum(), TEMAS)


ag_proj = agenda_agregada(PROJETOS)
ag_fis = agenda_agregada(FISCAL)
guarda("pauta.hell_pauta_proj", hell(pauta.to_numpy(), ag_proj.to_numpy()))
guarda("pauta.hell_pauta_fis", hell(pauta.to_numpy(), ag_fis.to_numpy()))
guarda("pauta.hell_proj_fis", hell(ag_proj.to_numpy(), ag_fis.to_numpy()))
razao = (pauta + 1e-3) / (ag_proj + 1e-3)
guarda("pauta.sobre_representados", "; ".join(f"{ab(t)} ({100*pauta[t]:.1f}% × {100*ag_proj[t]:.1f}%)" for t in razao.sort_values(ascending=False).head(4).index))
guarda("pauta.sub_representados", "; ".join(f"{ab(t)} ({100*pauta[t]:.1f}% × {100*ag_proj[t]:.1f}%)" for t in razao[ag_proj > 0.01].sort_values().head(4).index))
# qual lado tem agenda (projetos) mais próxima da pauta?
op_ = Pproj.loc[[d for d in AMp if C.loc[d, "lado"] == "oposição"]]
ba_ = Pproj.loc[[d for d in AMp if C.loc[d, "lado"] == "base"]]
ce_ = Pproj.loc[[d for d in AMp if C.loc[d, "lado"] == "centro"]]
bt = []
for _ in range(NBOOT // 2):
    bt.append(hell(op_.iloc[RNG.integers(0, len(op_), len(op_))].mean(0).to_numpy(), pauta.to_numpy())
              - hell(ba_.iloc[RNG.integers(0, len(ba_), len(ba_))].mean(0).to_numpy(), pauta.to_numpy()))
guarda("pauta.hell_oposicao", hell(op_.mean(0).to_numpy(), pauta.to_numpy()))
guarda("pauta.hell_centro", hell(ce_.mean(0).to_numpy(), pauta.to_numpy()))
guarda("pauta.hell_base", hell(ba_.mean(0).to_numpy(), pauta.to_numpy()))
guarda("pauta.dif_op_menos_base_ic", [round(float(np.percentile(bt, 2.5)), 4), round(float(np.percentile(bt, 97.5)), 4)])

# Figura 1: distribuição temática — projetos, fiscalização, pauta votada
ordem_t = ag_proj.sort_values().index
fig, ax = plt.subplots(figsize=(7.5, 7.2))
yy = np.arange(K)
ax.hlines(yy, 0, np.maximum.reduce([100 * ag_proj[ordem_t], 100 * ag_fis[ordem_t], 100 * pauta[ordem_t]]),
          color=COR["grade"], lw=0.8)
ax.scatter(100 * ag_proj[ordem_t], yy, s=26, color=COR["azul"], label="projetos apresentados", zorder=3)
ax.scatter(100 * ag_fis[ordem_t], yy, s=26, marker="s", color=COR["laranja"], label="fiscalização apresentada (RIC, INC, PFC, SIT)", zorder=3)
ax.scatter(100 * pauta[ordem_t], yy, s=30, marker="D", color=COR["aqua"], label="proposições votadas nominalmente no Plenário", zorder=3, edgecolor=COR["fundo"], lw=0.6)
ax.set_yticks(yy, [ab(t) for t in ordem_t])
ax.set_xlabel("Participação do tema (%), cada proposição com peso 1 dividido entre seus temas")
ax.legend(loc="lower right")
ax.set_title("Distribuição temática da agenda apresentada e da pauta votada")
salva_fig(fig, "fig1_distribuicao_temas")

# evolução anual (projetos, cada proposição uma vez)
anos = [2023, 2024, 2025, 2026]
PA = P[P["siglaTipo"].isin(PROJETOS) & P["tem_tema"]].copy()
PA["ano_"] = PA["dataApresentacao"].str[:4].astype(int)
ev_ano = {}
for a in anos:
    ids = [PIDX[p] for p in PA.loc[PA["ano_"] == a, "id"]]
    v = TP_FRAC[ids].sum(0)
    ev_ano[a] = pd.Series(v / v.sum(), TEMAS)
    guarda(f"tempo.n_projetos.{a}", len(ids))
EVA = pd.DataFrame(ev_ano)
guarda("tempo.hell_2023_2025", hell(EVA[2023].to_numpy(), EVA[2025].to_numpy()))
guarda("tempo.hell_2023_2026", hell(EVA[2023].to_numpy(), EVA[2026].to_numpy()))
guarda("tempo.hell_2025_2026", hell(EVA[2025].to_numpy(), EVA[2026].to_numpy()))
var_ano = (EVA.max(1) - EVA.min(1)).sort_values(ascending=False)
guarda("tempo.maior_variacao", "; ".join(f"{ab(t)} ({100*EVA.loc[t, 2023]:.1f}% → {100*EVA.loc[t, 2026]:.1f}%)" for t in var_ano.head(4).index))
fig, ax = plt.subplots(figsize=(7.5, 3.8))
top_t = var_ano.head(6).index
cores = [COR["azul"], COR["laranja"], COR["aqua"], COR["amarelo"], COR["magenta"], COR["violeta"]]
for t, cr in zip(top_t, cores):
    ax.plot(anos, 100 * EVA.loc[t], marker="o", ms=4, lw=2, color=cr, label=ab(t))
    ax.annotate(ab(t), (2026, 100 * EVA.loc[t, 2026]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=7.5, color=COR["tinta2"])
ax.set_xticks(anos, ["2023", "2024", "2025", "2026*"])
ax.set_xlim(2022.8, 2027.2)
ax.set_ylabel("Participação nos projetos do ano (%)")
ax.set_title("Os seis temas de maior variação anual (projetos apresentados)")
ax.legend(loc="upper left", fontsize=7.5, ncol=2)
ax.text(0, -0.13, "* 2026 até 11/11 (ano eleitoral).", transform=ax.transAxes, color=COR["mudo"], fontsize=7.5)
salva_fig(fig, "fig7_evolucao_anual")

# =========================================================== 15. validade de face
print("15. Validade de face (palavras-chave na ementa)...")
EM = P.set_index("id").loc[PROPS, "ementa"].fillna("").map(sem_acento)
kw = {"Saúde": r"saude|\bsus\b|hospital|medic|doenca|vacina|enfermag",
      "Educação": r"educa|escola|ensino|professor|aluno|universidade",
      "Defesa e Segurança": r"seguranca|policia|arma|crime|criminal|militar",
      "Meio Ambiente e Desenvolvimento Sustentável": r"ambient|florest|clima|desmat|poluic|residuo",
      "Agricultura, Pecuária, Pesca e Extrativismo": r"agric|rural|pecuar|pesca|produtor|agro",
      "Trabalho e Emprego": r"trabalh|emprego|salari|\bclt\b",
      "Esporte e Lazer": r"esport|futebol|atleta",
      "Direitos Humanos e Minorias": r"mulher|crianc|idos|deficiencia|indigen|racis|lgbt|violencia domestica"}
linhas = []
for t, rx in kw.items():
    tem = TP_FRAC[:, TIDX[t]] > 0
    hit = EM.str.contains(rx, regex=True).to_numpy()
    linhas.append([ab(t), int(tem.sum()), 100 * hit[tem].mean(), 100 * hit[~tem].mean(), 100 * tem[hit].mean()])
tab_fv = pd.DataFrame(linhas, columns=["Tema", "Proposições com o tema", "% com palavra-chave (com tema)",
                                       "% com palavra-chave (sem tema)", "% com o tema entre as que têm a palavra"])
md_tabela(tab_fv, "tab2_validade_face", floatfmt=1)
guarda("qualidade.kw_sens_mediana", tab_fv["% com palavra-chave (com tema)"].median())
guarda("qualidade.kw_prec_mediana", tab_fv["% com o tema entre as que têm a palavra"].median())
adm = TP_FRAC[:, TIDX["Administração Pública"]] > 0
guarda("qualidade.pct_admpub", 100 * adm.mean())
guarda("qualidade.pct_admpub_ric", 100 * adm[TIPO_PROP == "RIC"].mean())
guarda("qualidade.pct_admpub_pl", 100 * adm[TIPO_PROP == "PL"].mean())
guarda("qualidade.pct_admpub_unico", 100 * (adm & ((TP_FRAC > 0).sum(1) == 1)).sum() / adm.sum())
# aprovação: quanto da agenda apresentada vira norma
norma = P["ultimoStatus_descricaoSituacao"].eq("Transformado em Norma Jurídica")
guarda("dados.pct_projetos_norma", 100 * norma[P["siglaTipo"].isin(PROJETOS)].mean())
guarda("dados.n_projetos_norma", int(norma[P["siglaTipo"].isin(PROJETOS)].sum()))

R["tempo_execucao_s"] = round(time.time() - t0, 1)
(AQUI / "resultados.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Concluído em {R['tempo_execucao_s']} s. Resultados em resultados.json, tabelas/ e figuras/.")
