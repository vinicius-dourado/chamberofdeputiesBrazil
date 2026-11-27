"""6-c.2a-ii: lista de eventos (entradas e saídas de partidos do gabinete, 2007–2026) gerada por regra.

A regra é pré-registrada (PREREG.md) e aplicada sobre a L5 (dados/gabinetes), com as convenções de
analises/comum/gabinetes.py (codificação do Ipea). Nenhum dado de voto é usado para escolher eventos,
exceto o mínimo de votações nominais na janela, que não depende do desfecho.
"""
from datetime import date, timedelta

import pandas as pd

from analises.comum import config, gabinetes

JANELA_MESES = 6
MIN_VOTACOES_LADO = 20          # votações com orientação do governo (níveis 1–2) antes e depois
COLAPSO_DIAS = 30               # saída seguida de reentrada em até 30 dias = troca de ministro, não de partido
TRANSICAO_DIAS = 30             # eventos a até 30 dias do início ou do fim de um governo são excluídos
DESINCOMPATIBILIZACAO = [(date(a, 3, 1), date(a, 4, 10)) for a in (2010, 2014, 2018, 2022, 2026)]
IMPEACHMENT_2016 = (date(2016, 3, 1), date(2016, 5, 11))


def mudancas():
    """Todas as entradas e saídas de linhagens da base, por data (sem filtros)."""
    m = gabinetes.ministros()
    datas = sorted({d for d in pd.concat([m["min_inicio"], m["min_fim"]]).dropna() if d.year >= 2007}
                   | {config.choque("desembarque_uniao_pp"), config.choque("volta_uniao")})
    prev, linhas = gabinetes.base_na_data(date(2007, 2, 1)), []
    for d in datas:
        b = gabinetes.base_na_data(d)
        linhas += [(d, "entrada", p) for p in sorted(b - prev)] + [(d, "saida", p) for p in sorted(prev - b)]
        prev = b
    return pd.DataFrame(linhas, columns=["data", "tipo", "partido"])


def _perto_de_transicao(d):
    for _, ini, fim in config.GOVERNOS:
        if abs((d - ini).days) <= TRANSICAO_DIAS or abs((d - fim).days) <= TRANSICAO_DIAS:
            return True
    return False


def classificar(mud=None):
    """Aplica as regras e devolve todos os eventos com a coluna ``grupo``:
    principal | impeachment_2016 | excluido_<motivo>."""
    mud = mudancas() if mud is None else mud.copy()
    mud["grupo"] = "principal"
    # 1) transições de governo primeiro (senão viram "troca de ministro" no colapso abaixo)
    # (as saídas de mar.–mai./2016 vão para o grupo do impeachment, mesmo perto do fim do governo Dilma)
    no_imp = (mud["tipo"] == "saida") & mud["data"].map(lambda d: IMPEACHMENT_2016[0] <= d <= IMPEACHMENT_2016[1])
    mud.loc[mud["data"].map(_perto_de_transicao) & ~no_imp, "grupo"] = "excluido_transicao_de_governo"
    # 2) colapsa saída + reentrada do mesmo partido em até 30 dias (entre os eventos restantes)
    for p, g in mud[mud["grupo"] == "principal"].groupby("partido"):
        g = g.sort_values("data")
        for i, j in zip(g.index[:-1], g.index[1:]):
            if g.at[i, "tipo"] == "saida" and g.at[j, "tipo"] == "entrada" and \
                    (g.at[j, "data"] - g.at[i, "data"]).days <= COLAPSO_DIAS:
                mud.loc[[i, j], "grupo"] = "excluido_troca_de_ministro"
    ok = mud["grupo"] == "principal"
    desinc = mud["data"].map(lambda d: any(a <= d <= b for a, b in DESINCOMPATIBILIZACAO))
    mud.loc[ok & (mud["tipo"] == "saida") & desinc, "grupo"] = "excluido_desincompatibilizacao"
    ok = mud["grupo"] == "principal"
    imp = mud["data"].map(lambda d: IMPEACHMENT_2016[0] <= d <= IMPEACHMENT_2016[1])
    mud.loc[ok & (mud["tipo"] == "saida") & imp, "grupo"] = "impeachment_2016"
    mud["governo"] = mud["data"].map(config.governo_na_data)
    mud["evento"] = [f"{t[:3]}_{p}_{d:%Y%m%d}" for d, t, p in zip(mud["data"], mud["tipo"], mud["partido"])]
    return mud.reset_index(drop=True)


def janela(ev, todos):
    """Janela de ±6 meses, cortada (i) no início/fim do governo, (ii) na legislatura e (iii) em outro
    evento do mesmo partido (entre os eventos que não foram colapsados como troca de ministro)."""
    d = ev["data"]
    ini = (pd.Timestamp(d) - pd.DateOffset(months=JANELA_MESES)).date()
    fim = (pd.Timestamp(d) + pd.DateOffset(months=JANELA_MESES)).date()
    for _, gi, gf in config.GOVERNOS:
        if gi <= d <= gf:
            ini, fim = max(ini, gi), min(fim, gf)
    leg = config.legislatura_na_data(d)
    li, lf = config.LEGISLATURAS[leg]
    ini, fim = max(ini, li), min(fim, lf)
    outros = todos[(todos["partido"] == ev["partido"]) & (todos["data"] != d)
                   & ~todos["grupo"].isin(["excluido_troca_de_ministro", "excluido_transicao_de_governo"])]
    for o in outros["data"]:
        if ini <= o < d:
            ini = o
        if d < o <= fim:
            fim = o - timedelta(days=1)
    return ini, fim


def mudaram_na_janela(ini, fim, todos):
    """Partidos com alguma mudança real de status dentro da janela (sem trocas de ministro e sem as
    transições de governo, que ficam fora das janelas por construção): não servem de controle.
    O status estável de cada controle (sempre fora ou sempre dentro da base) é conferido no painel."""
    reais = ~todos["grupo"].isin(["excluido_troca_de_ministro", "excluido_transicao_de_governo"])
    return set(todos[(todos["data"] >= ini) & (todos["data"] <= fim) & reais]["partido"])
