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
* Ideologia partidária (opcional): dados_brutos/ideologia_partidos.csv
  (colunas partido;ano;ideologia - estimativas de Power & Zucco, BLS).

Medidas (mês a mês, dia 15)
---------------------------
* coalescencia: índice de Amorim Neto (2006), medida usada no artigo:
  100 * (1 - 1/2 * sum_i |S_i - M_i|), S_i = fração de cadeiras do partido i entre os
  partidos do gabinete, M_i = fração de ministérios; os não partidários entram como um
  grupo com 0 cadeiras.
* prop_kd_v1 / prop_kd_v2: cosseno de Koppel & Diskin (2009), medida de Almeida (np em
  grupo / individualmente). Reproduz exatamente Prop_v1 e Prop_v2 da planilha.
* tamanho: nº de partidos com ao menos um ministério.
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

MANDATOS = [  # (rótulo, início, fim exclusivo)
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

TABELA1_ARTIGO = pd.DataFrame(
    [("Cardoso 1", 59.6, 2.8, 4.1, 0.3, 21.5, 1.5),
     ("Cardoso 2", 61.7, 1.8, 4.3, 0.8, 19.6, 1.4),
     ("Lula 1", 49.3, 0.9, 7.7, 0.7, 48.2, 3.4),
     ("Lula 2", 52.1, 4.7, 9.1, 0.9, 42.2, 0.9),
     ("Rousseff 1", 43.7, 1.5, 7.8, 0.7, 45.8, 0.9)],
    columns=["mandato", "prop_media", "prop_dp", "tam_media", "tam_dp", "het_media", "het_dp"])


# ----------------------------------------------------------------------------- medidas
def coalescencia(comp):
    """comp: lista de (partido, ministros, cadeiras); 'np' com cadeiras = 0."""
    M = sum(m for _, m, _ in comp)
    S = sum(s for _, _, s in comp)
    if S == 0:
        return 0.0  # gabinete sem partidos
    return 100 * (1 - 0.5 * sum(abs(s / S - m / M) for _, m, s in comp))


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


def carregar_ideologia():
    f = BRUTOS / "ideologia_partidos.csv"
    if not f.exists():
        return None
    ide = pd.read_csv(f, sep=";")
    ide["partido"] = ide["partido"].replace(NORM)
    return ide


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
    for t in pd.date_range("1995-01-01", FIM, freq="MS") + pd.Timedelta(days=14):
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
            het, sem_ide = heterogeneidade(partidos, t.year, ide)
            linhas.append({
                "data": t.date(), "mandato": mand, "versao": v, "gabinete": nome,
                "n_ministerios": sum(m for _, m, _ in comp),
                "ministros_np": sum(m for p, m, _ in comp if p == "np"),
                "tamanho": len(partidos),
                "coalescencia": coalescencia(comp),
                "prop_kd_v1": koppel_diskin(comp, True),
                "prop_kd_v2": koppel_diskin(comp, False),
                "heterogeneidade": het,
                "partidos_sem_ideologia": sem_ide,
                "cadeiras_coalizao": sum(s for _, _, s in comp),
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
        kd_v1_media=("prop_kd_v1", "mean"), kd_v1_dp=("prop_kd_v1", "std"),
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
    alt = tabela_por_mandato(painel, "alt")
    alt[alt.mandato == "Lula 3"].to_csv(SAIDA / "lula3_sensibilidade.csv", sep=";", index=False)
    l3 = painel[(painel.mandato == "Lula 3") & (painel.versao == "base")]
    l3["periodo"] = pd.cut(pd.to_datetime(l3.data), [pd.Timestamp("2023-01-01"), SAIDA_UNIAO_PP,
                           pd.Timestamp("2026-04-01"), pd.Timestamp("2027-01-01")],
                           labels=["jan/23-ago/25", "set/25-mar/26", "abr/26-nov/26"])
    sub = l3.groupby("periodo", observed=True)[["coalescencia", "tamanho", "prop_kd_v1", "ministros_np"]].mean().round(1)
    sub.to_csv(SAIDA / "lula3_subperiodos.csv", sep=";")
    print("\nLula 3 por subperíodo:\n", sub)
    val = validar_lula3()
    val.to_csv(SAIDA / "validacao_lula3_almeida.csv", sep=";", index=False)
    pd.set_option("display.width", 200)
    print(tab.to_string(index=False))
    print("\nLula 3, versão alternativa:\n", alt[alt.mandato == "Lula 3"].to_string(index=False))
    print("\nValidação:\n", val.to_string(index=False))
