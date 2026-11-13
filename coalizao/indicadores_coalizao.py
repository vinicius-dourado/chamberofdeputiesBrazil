"""Estratégias de gerência da coalizão por mandato, 1995-2026.

Estende a Tabela 1 de Bertholini & Pereira (RAP, 2017) - proporcionalidade, tamanho e
heterogeneidade ideológica da coalizão - até o governo Lula 3.

Fontes
------
* 1995-2022: gabinetes de Acir Almeida (Ipea, NT 53/2021), planilha
  dados_brutos/almeida_ipea_gabinetes.xlsx - composição partidária de cada gabinete
  (nº de ministros e cadeiras na Câmara de cada partido; "np" = não partidário).
* 2023-2026: dados_brutos/lula3_gabinete_2023_2026.csv (codificação ministro a ministro
  seguindo os critérios de Almeida) + cadeiras mensais em exercício na Câmara
  (cadeiras_leg57.py, a partir de dados/leg57).
* Ideologia partidária: Zucco & Power (2023), série 1990-2021 do Atlas do Estado Brasileiro
  (dados_brutos/atlas_ipea_ideologia_partidos.xlsx), reescalada para a escala de
  Power & Zucco (2012) usada no artigo (dados_brutos/ideologia_power_zucco_2012.csv).

Medidas (mês a mês, dia 15)
---------------------------
* coalescencia (PROPORCIONALIDADE DA TABELA 1): índice de coalescência de Amorim Neto
  (2006, p. 426), CABINET = 1 - 1/2 * sum_i |S_i - M_i|, x100, somando sobre os partidos
  do gabinete. M_i = % de todos os cargos com status de ministério que o partido i ocupa
  (os não partidários entram só no denominador); S_i = % de cadeiras do partido i no total
  de cadeiras dos partidos do gabinete. É a operacionalização de Pereira & Bertholini
  (2017, cap. "Coalition Management in Multiparty Presidential Regimes", tab. 1 e nota 2),
  que revisa a Tabela 1 da RAP (2017). Com ela, 2003-2016 fica a <= 1 ponto da tabela
  revisada (Lula 1: 64,9 vs 65,5; Lula 2: 69,3 vs 69,1; Rousseff 1: 69,9 vs 68,9;
  Rousseff 2: 75,6 vs 75,6).
  coalescencia_np_grupo: variante com os não partidários como um grupo com S = 0
  (cada ponto de ministros não partidários reduz o índice em 1 ponto) - sensibilidade.
* prop_kd_v1 / prop_kd_v2: cosseno de Koppel & Diskin (2009), medida de Almeida (np em
  grupo / individualmente). Reproduz exatamente Prop_v1 e Prop_v2 da planilha.
* tamanho: nº de partidos com ao menos um ministério.
* cadeiras_coalizao_pct: % das cadeiras da Câmara com os partidos do gabinete.
* heterogeneidade: coeficiente de variação (x100) da ideologia dos partidos do gabinete.

Uso:  python coalizao/indicadores_coalizao.py
"""
from pathlib import Path
import re

import numpy as np
import pandas as pd

from cadeiras_leg57 import cadeiras_mensais

AQUI = Path(__file__).resolve().parent
BRUTOS = AQUI / "dados_brutos"
SAIDA = AQUI / "resultados"

FIM = "2026-11-15"  # último mês observado
SAIDA_UNIAO_PP = pd.Timestamp("2025-09-02")  # federação União Progressista deixa o governo

# nomes de partido harmonizados (sucessões de sigla)
NORM = {"PMDB": "MDB", "PFL": "DEM", "PPB": "PP", "PR": "PL", "PRB": "REP",
        "REPUBLICANOS": "REP", "União": "UNIAO", "UNIÃO": "UNIAO", "Rede": "REDE"}

# tamanho da Câmara dos Deputados (a partir da data)
TAMANHO_CAMARA = [("1983-02-01", 479), ("1987-02-01", 487), ("1991-02-01", 503), ("1995-01-01", 513)]


def tamanho_camara(t):
    """Nº de cadeiras da Câmara na data t. A partir de 1995-01-01 usa 513 (o 1º gabinete de
    FHC, na planilha de Almeida, já traz as bancadas da legislatura eleita em 1994)."""
    return [n for d, n in TAMANHO_CAMARA if pd.Timestamp(d) <= pd.Timestamp(t)][-1]


MANDATOS = [  # (rótulo, início, fim exclusivo)
    ("Sarney", "1985-03-15", "1990-03-15"),
    ("Collor", "1990-03-15", "1992-10-02"),
    ("Itamar", "1992-10-02", "1995-01-01"),
    ("Cardoso 1", "1995-01-01", "1999-01-01"),
    ("Cardoso 2", "1999-01-01", "2003-01-01"),
    ("Lula 1", "2003-01-01", "2007-01-01"),
    ("Lula 2", "2007-01-01", "2011-01-01"),
    ("Rousseff 1", "2011-01-01", "2015-01-01"),
    ("Rousseff 2", "2015-01-01", "2016-05-12"),
    ("Temer", "2016-05-12", "2019-01-01"),
    ("Bolsonaro", "2019-01-01", "2023-01-01"),
    ("Lula 3", "2023-01-01", "2027-01-01"),
]

# Tabela 1 revisada: Pereira & Bertholini (2017), "Coalition Management in Multiparty
# Presidential Regimes" (fonte: Bertholini 2017); Temer = mai-dez/2016.
TABELA1_BERTHOLINI_2017 = pd.DataFrame(
    [("Cardoso 1", 71.4, 2.28, 4.6, 0.65, 31.0, 5.51),
     ("Cardoso 2", 73.8, 2.47, 4.0, 0.68, 30.5, 5.24),
     ("Lula 1", 65.5, 2.37, 7.7, 0.72, 48.1, 3.46),
     ("Lula 2", 69.1, 2.32, 9.1, 0.94, 42.2, 0.88),
     ("Rousseff 1", 68.9, 1.44, 7.8, 0.63, 45.4, 1.07),
     ("Rousseff 2", 75.6, 3.21, 7.9, 0.25, 37.7, 0.74),
     ("Temer", 80.4, 0.21, 10.0, 0.0, 27.1, 0.0)],
    columns=["mandato", "prop_media", "prop_dp", "tam_media", "tam_dp", "het_media", "het_dp"])

# Tabela 1 original da RAP (2017); a proporcionalidade não é reproduzível (ver diagnósticos).
TABELA1_ARTIGO = pd.DataFrame(
    [("Cardoso 1", 59.6, 2.8, 4.1, 0.3, 21.5, 1.5),
     ("Cardoso 2", 61.7, 1.8, 4.3, 0.8, 19.6, 1.4),
     ("Lula 1", 49.3, 0.9, 7.7, 0.7, 48.2, 3.4),
     ("Lula 2", 52.1, 4.7, 9.1, 0.9, 42.2, 0.9),
     ("Rousseff 1", 43.7, 1.5, 7.8, 0.7, 45.8, 0.9)],
    columns=["mandato", "prop_media", "prop_dp", "tam_media", "tam_dp", "het_media", "het_dp"])


# ----------------------------------------------------------------------------- medidas
def coalescencia(comp, np_em_grupo=False):
    """Coalescência de Amorim Neto. comp: lista de (partido, ministros, cadeiras), com o
    grupo de não partidários como ('np', n, 0). Por padrão soma só os partidos (os np
    pesam apenas no total de cargos); np_em_grupo=True inclui o termo |0 - M_np|."""
    M = sum(m for _, m, _ in comp)
    S = sum(s for _, _, s in comp)
    if S == 0:
        return 0.0  # gabinete sem partidos
    return 100 * (1 - 0.5 * sum(abs(s / S - m / M) for p, m, s in comp if np_em_grupo or p != "np"))


def koppel_diskin(comp, np_em_grupo=True):
    m, s = [], []
    for p, mi, si in comp:
        if p == "np" and not np_em_grupo:
            m += [1] * mi
            s += [0] * mi
        else:
            m.append(mi)
            s.append(si)
    m, s = np.array(m, float), np.array(s, float)
    if s.sum() == 0:
        return 0.0
    m, s = m / m.sum(), s / s.sum()
    return 100 * (s * m).sum() / np.sqrt((s ** 2).sum() * (m ** 2).sum())


ATLAS_PARA_SIGLA = {"PCB/PPS/CID": "PPS", "PFL/DEM": "DEM", "PMDB/MDB": "MDB", "PL/PR/PL": "PL",
                    "PDS/PPR/PPB/PP": "PP", "PRB/REP": "REP", "SD": "SD"}


def carregar_ideologia():
    """Série de Zucco & Power (2023), via Atlas do Estado Brasileiro (Ipea), 1990-2021.

    Essa série está numa escala de -1 a 1, centrada em zero, onde o coeficiente de variação
    não faz sentido. Como ela é uma transformação linear da escala de Power & Zucco (2012),
    usada no artigo (r = 0,9998 nas 72 observações comuns de 1990 a 2009), a série é levada
    para a escala de 2012 pela regressão estimada nessas observações.
    União Brasil (fusão DEM + PSL, 2022) recebe a média de DEM e PSL na onda de 2021.
    """
    at = pd.read_excel(BRUTOS / "atlas_ipea_ideologia_partidos.xlsx", sheet_name="dados")
    at["partido"] = at.partido.replace(ATLAS_PARA_SIGLA)
    pz = pd.read_csv(BRUTOS / "ideologia_power_zucco_2012.csv", sep=";")
    m = at.merge(pz, on=["partido", "ano"], suffixes=("_atlas", "_pz"))
    b, a = np.polyfit(m.ideologia_atlas, m.ideologia_pz, 1)
    at["ideologia"] = a + b * at.ideologia
    w21 = at[at.ano == 2021].set_index("partido").ideologia
    at = pd.concat([at, pd.DataFrame([{"ano": 2021, "partido": "UNIAO",
                                       "ideologia": (w21["DEM"] + w21["PSL"]) / 2}])])
    at["partido"] = at["partido"].replace(NORM)
    return at[["ano", "partido", "ideologia"]]


def partidos_ideologia(partidos, t):
    """Antes de 1995, 'PP' na planilha de Almeida é o PP de 1993-95 ('PPold' na série de
    ideologia) e PDS/PPR são antecessores do PP atual."""
    if t >= pd.Timestamp("1995-01-01"):
        return partidos
    return ["PPold" if p == "PP" else {"PDS": "PP", "PPR": "PP"}.get(p, p) for p in partidos]


def heterogeneidade(partidos, ano, ide):
    """CV (x100, desvio-padrão amostral) da ideologia dos partidos do gabinete.

    Usa, para cada partido, a onda do BLS mais recente <= ano (ou a mais próxima, se o
    partido só foi medido depois). Partidos nunca medidos são omitidos; a função devolve
    também quantos foram omitidos. Com essa regra, 1995-2013 fica próximo da Tabela 1
    do artigo (Lula 1: 50,3 vs 48,2; Lula 2: 42,1 vs 42,2; Rousseff 1: 45,4 vs 45,8).
    """
    if ide is None:
        return np.nan, np.nan
    vals, faltam = [], 0
    for p in partidos:
        x = ide[ide.partido == p]
        if x.empty:
            faltam += 1
            continue
        antes = x[x.ano <= ano]
        linha = antes.loc[antes.ano.idxmax()] if not antes.empty else x.loc[(x.ano - ano).abs().idxmin()]
        vals.append(linha.ideologia)
    if len(vals) < 2:
        return np.nan, faltam
    vals = np.array(vals, float)
    return 100 * vals.std(ddof=1) / vals.mean(), faltam


# ----------------------------------------------------------------------- composições
def comp_almeida():
    a = pd.read_excel(BRUTOS / "almeida_ipea_gabinetes.xlsx", sheet_name="dados").dropna(subset=["Gabinete"])
    a.columns = ["gabinete", "evento", "inicio", "prop_v1_almeida", "prop_v2_almeida", "comp_txt"]
    a["comp"] = a.comp_txt.map(
        lambda c: [(NORM.get(p, p), int(m), int(s)) for p, m, s in re.findall(r"([\wÀ-ú]+)\((\d+),(\d+)\)", c)])
    return a.sort_values("inicio")


def comp_lula3(t, gab, cad, coluna="partido", saida_uniao_pp=True):
    ativos = gab[(gab.inicio <= t) & (gab.fim.isna() | (gab.fim > t))].drop_duplicates("pasta", keep="last")
    part = ativos[coluna].replace(NORM)
    if saida_uniao_pp and t >= SAIDA_UNIAO_PP:
        part = part.replace({"UNIAO": "np", "PP": "np"})
    cont = part.value_counts()
    seats = cad[cad.t == t].set_index("partido").cadeiras
    return [(p, int(n), 0 if p == "np" else int(seats.get(p, 0))) for p, n in cont.items()], len(ativos)


def painel_mensal():
    ide = carregar_ideologia()
    alm = comp_almeida()
    gab = pd.read_csv(BRUTOS / "lula3_gabinete_2023_2026.csv", sep=";", parse_dates=["inicio", "fim"])
    cad = cadeiras_mensais(fim=FIM)
    cad["partido"] = cad.partido.replace(NORM)
    cad = cad.groupby(["t", "partido"], as_index=False).cadeiras.sum()

    linhas = []
    for t in pd.date_range("1985-04-01", FIM, freq="MS") + pd.Timedelta(days=14):
        mand = next(n for n, i, f in MANDATOS if pd.Timestamp(i) <= t < pd.Timestamp(f))
        versoes = {}
        if t < pd.Timestamp("2023-01-01"):
            g = alm[alm.inicio <= t].iloc[-1]
            versoes["base"] = (g.comp, g.gabinete)
        else:
            versoes["base"] = (comp_lula3(t, gab, cad)[0], "Lula 3 (extensão)")
            versoes["alt"] = (comp_lula3(t, gab, cad, "partido_alt", saida_uniao_pp=False)[0], "Lula 3 (alternativa)")
        for v, (comp, nome) in versoes.items():
            partidos = [p for p, _, _ in comp if p != "np"]
            het, sem_ide = heterogeneidade(partidos_ideologia(partidos, t), t.year, ide)
            linhas.append({
                "data": t.date(), "mandato": mand, "versao": v, "gabinete": nome,
                "n_ministerios": sum(m for _, m, _ in comp),
                "ministros_np": sum(m for p, m, _ in comp if p == "np"),
                "tamanho": len(partidos),
                "coalescencia": coalescencia(comp),
                "coalescencia_np_grupo": coalescencia(comp, np_em_grupo=True),
                "prop_kd_v1": koppel_diskin(comp, True),
                "prop_kd_v2": koppel_diskin(comp, False),
                "heterogeneidade": het,
                "partidos_sem_ideologia": sem_ide,
                "cadeiras_coalizao": sum(s for _, _, s in comp),
                "cadeiras_coalizao_pct": 100 * sum(s for _, _, s in comp) / tamanho_camara(t),
                "composicao": " ".join(f"{p}({m},{s})" for p, m, s in comp),
            })
    return pd.DataFrame(linhas)


def tabela_por_mandato(painel, versao="base"):
    p = painel[painel.versao == versao] if versao == "base" else pd.concat(
        [painel[(painel.versao == "base") & (painel.mandato != "Lula 3")], painel[painel.versao == "alt"]])
    ordem = [m for m, _, _ in MANDATOS]
    t = p.groupby("mandato").agg(
        meses=("data", "size"),
        prop_media=("coalescencia", "mean"), prop_dp=("coalescencia", "std"),
        tam_media=("tamanho", "mean"), tam_dp=("tamanho", "std"),
        het_media=("heterogeneidade", "mean"), het_dp=("heterogeneidade", "std"),
        cad_media=("cadeiras_coalizao_pct", "mean"), cad_dp=("cadeiras_coalizao_pct", "std"),
    ).reindex(ordem).round(1).reset_index()
    return t


def validar_lula3(painel_alm=None):
    """Compara a codificação própria de Lula 3 com os 4 gabinetes de Almeida (2023-2024)."""
    alm = comp_almeida()
    gab = pd.read_csv(BRUTOS / "lula3_gabinete_2023_2026.csv", sep=";", parse_dates=["inicio", "fim"])
    cad = cadeiras_mensais(fim=FIM)
    cad["partido"] = cad.partido.replace(NORM)
    out = []
    for _, g in alm[alm.gabinete.str.startswith("Lula 3")].iterrows():
        t = (g.inicio + pd.Timedelta(days=20)).to_period("M").to_timestamp() + pd.Timedelta(days=14)
        comp, _ = comp_lula3(t, gab, cad)
        out.append({"gabinete": g.gabinete, "almeida": g.comp_txt,
                    "propria": " ".join(f"{p}({m},{s})" for p, m, s in comp),
                    "kd_v1_almeida": round(g.prop_v1_almeida, 1), "kd_v1_propria": round(koppel_diskin(comp), 1)})
    return pd.DataFrame(out)


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    painel = painel_mensal()
    painel.to_csv(SAIDA / "painel_mensal_1995_2026.csv", sep=";", index=False, float_format="%.2f")
    tab = tabela_por_mandato(painel)
    tab.to_csv(SAIDA / "tabela1_estendida.csv", sep=";", index=False)
    extra = painel[painel.versao == "base"].groupby("mandato")[
        ["coalescencia_np_grupo", "prop_kd_v1", "prop_kd_v2"]].agg(["mean", "std"]).round(1)
    extra.columns = [f"{a}_{'media' if b == 'mean' else 'dp'}" for a, b in extra.columns]
    extra.reindex([m for m, _, _ in MANDATOS]).to_csv(SAIDA / "proporcionalidade_medidas_alternativas.csv", sep=";")
    comp17 = tab.merge(TABELA1_BERTHOLINI_2017, on="mandato", how="left", suffixes=("", "_b2017"))
    comp17.to_csv(SAIDA / "comparacao_bertholini_2017.csv", sep=";", index=False)
    alt = tabela_por_mandato(painel, "alt")
    alt[alt.mandato == "Lula 3"].to_csv(SAIDA / "lula3_sensibilidade.csv", sep=";", index=False)
    l3 = painel[(painel.mandato == "Lula 3") & (painel.versao == "base")]
    l3["periodo"] = pd.cut(pd.to_datetime(l3.data), [pd.Timestamp("2023-01-01"), SAIDA_UNIAO_PP,
                           pd.Timestamp("2026-04-01"), pd.Timestamp("2027-01-01")],
                           labels=["jan/23-ago/25", "set/25-mar/26", "abr/26-nov/26"])
    sub = l3.groupby("periodo", observed=True)[["coalescencia", "tamanho", "cadeiras_coalizao_pct", "prop_kd_v1", "ministros_np"]].mean().round(1)
    sub.to_csv(SAIDA / "lula3_subperiodos.csv", sep=";")
    print("\nLula 3 por subperíodo:\n", sub)
    val = validar_lula3()
    val.to_csv(SAIDA / "validacao_lula3_almeida.csv", sep=";", index=False)
    pd.set_option("display.width", 200)
    print(tab.to_string(index=False))
    print("\nLula 3, versão alternativa:\n", alt[alt.mandato == "Lula 3"].to_string(index=False))
    print("\nValidação:\n", val.to_string(index=False))
