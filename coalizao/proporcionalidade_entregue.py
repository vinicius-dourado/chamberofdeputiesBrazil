"""Proporcionalidade por votos POTENCIAIS x votos EFETIVOS.

A coalescência de Amorim Neto (indicadores_coalizao.coalescencia) compara a fração de
ministérios de cada partido (M_i) com a sua fração de cadeiras na coalizão (S_i), isto é,
com os seus VOTOS POTENCIAIS (lei de Gamson: cada deputado aliado = um voto do governo).
Aqui S_i passa a ser a fração de VOTOS EFETIVOS, os votos que o partido de fato deu ao governo:

    votos efetivos_i = cadeiras_i x governismo_i
    S_i^e = votos efetivos_i / soma_j(votos efetivos_j)   (j no gabinete)

e M_i fica igual (mesmos gabinetes e mesmos não partidários da versão base).

Governismo (taxa de apoio ao governo) por partido, a partir de dados/leg<N>/votos.parquet
------------------------------------------------------------------------------------------
* só votações nominais do plenário (siglaOrgao == 'PLEN');
* só votações em que o líder do Governo orientou "Sim" ou "Não" (fora "Liberado",
  "Obstrução" do governo e votações sem orientação do governo);
* voto válido: Sim, Não, Obstrução ou Abstenção. Conta como apoio só o voto igual à
  orientação. Obstrução e Abstenção contam como NÃO apoio: com orientação Sim/Não, obstruir
  nega quórum e abster-se nega o voto. "Artigo 17" (presidente da Casa) e ausências ficam
  fora. taxa_estrita (só Sim/Não no denominador) fica como sensibilidade;
* taxa = soma dos votos alinhados / soma dos votos válidos do partido (agregado, não média
  de deputados), no mês e em janelas móveis de 3 e 6 meses (dentro do mandato);
* sensibilidade "disputadas": só votações em que a Oposição (ou a Minoria) orientou
  diferente do governo, para retirar as votações consensuais (por gabinete);
* variante com ausência: entrega = alinhados / (cadeiras em exercício x nº de votações),
  isto é, taxa entre os presentes x fração de presença.

Unidades
--------
* mensal (dia 15): composição do painel base (comp_lula3 / comp_almeida) e governismo da
  janela móvel de 6 meses que termina no mês (meses sem votos na janela recebem o primeiro
  valor observado no mandato ou, na falta dele, a taxa do mandato);
* gabinete: composição e cadeiras de gabinetes.tabela_gabinetes() e governismo de todas as
  votações do período do gabinete.

Legislaturas 55 (Rousseff 2, Temer) e 56 (Bolsonaro) entram quando dados/leg55 e dados/leg56
existem (python baixar_legislatura.py --legislatura 55 / 56); senão o script as pula.

Saídas (resultados/):
  governismo_partidos.csv                       partido x mês (taxas, presença, entrega)
  proporcionalidade_entregue_mensal.csv         painel mensal: potencial x efetivo
  proporcionalidade_entregue_gabinetes.csv      por gabinete: potencial x efetivo
  proporcionalidade_entregue_partidos.csv       por gabinete x partido: pesos e retorno
  proporcionalidade_entregue_resumo.csv         médias, DP e diferença por (sub)período

Uso:  python coalizao/proporcionalidade_entregue.py
"""
from pathlib import Path
import re

import numpy as np
import pandas as pd

import indicadores_coalizao as ic
import gabinetes as gb
from cadeiras_leg57 import cadeiras_mensais

RAIZ = ic.AQUI.parent
JANELA = 6  # meses da janela móvel principal
VOTOS_VALIDOS = ["Sim", "Não", "Obstrução", "Abstenção"]
# siglas dos votos -> siglas da planilha de Almeida / do CSV de Lula 3
NORM_VOTOS = {**ic.NORM, "SOLIDARIEDADE": "SD", "PTN": "PODE", "PODEMOS": "PODE", "MISSÃO": "MISSAO"}

# legislatura: (mandatos cobertos, mês de posse)
LEGISLATURAS = {
    55: (["Rousseff 2", "Temer"], "2015-02-15"),
    56: (["Bolsonaro"], "2019-02-15"),
    57: (["Lula 3"], "2023-02-15"),
}
MANDATO = {m: (pd.Timestamp(i), pd.Timestamp(f)) for m, i, f in ic.MANDATOS}
SUBPERIODOS_LULA3 = [("jan/23-ago/25", "2023-01-01", ic.SAIDA_UNIAO_PP),
                     ("set/25-mar/26", ic.SAIDA_UNIAO_PP, "2026-04-01"),
                     ("abr/26-nov/26", "2026-04-01", "2027-01-01")]


def mandato_de(t):
    return next((m for m, (i, f) in MANDATO.items() if i <= t < f), None)


# --------------------------------------------------------------------------- dados
def carregar_votos(leg):
    arq = RAIZ / f"dados/leg{leg}/votos.parquet"
    if not arq.exists():
        return None
    v = pd.read_parquet(arq, columns=["idVotacao", "data", "siglaOrgao", "deputado_siglaPartido",
                                      "voto", "orientacao_governo", "orientacao_oposicao",
                                      "orientacao_minoria"])
    for c in ["orientacao_governo", "orientacao_oposicao", "orientacao_minoria"]:
        v[c] = v[c].str.strip()
    v = v[(v.siglaOrgao == "PLEN") & v.orientacao_governo.isin(["Sim", "Não"]) & v.voto.isin(VOTOS_VALIDOS)].copy()
    v["data"] = pd.to_datetime(v.data)
    v["mes"] = v.data.dt.to_period("M").dt.to_timestamp()
    v["partido"] = v.deputado_siglaPartido.replace(NORM_VOTOS)
    v["alinhado"] = v.voto == v.orientacao_governo
    v["sim_nao"] = v.voto.isin(["Sim", "Não"])
    # votação disputada: Oposição (ou, na falta, Minoria) orientou diferente do governo
    contra = v.orientacao_oposicao.where(v.orientacao_oposicao.isin(VOTOS_VALIDOS), v.orientacao_minoria)
    v["disputada"] = contra.isin(VOTOS_VALIDOS) & (contra != v.orientacao_governo)
    v["mandato"] = v.data.map(mandato_de)
    return v[v.mandato.notna()]


def carregar_cadeiras(leg, fim):
    posse = LEGISLATURAS[leg][1]
    ini = min(MANDATO[m][0] for m in LEGISLATURAS[leg][0])
    if not (RAIZ / f"dados/leg{leg}/deputados_historico.parquet").exists():
        return None
    c = cadeiras_mensais(inicio=str(ini.date()), fim=fim, legislatura=leg, posse=posse)
    c["partido"] = c.partido.replace(NORM_VOTOS)
    c = c.groupby(["t", "partido"], as_index=False).cadeiras.sum()
    c["mes"] = c.t - pd.Timedelta(days=14)
    return c


# ---------------------------------------------------------------------- governismo
def governismo_mensal(v, cad):
    """Partido x mês, com janelas móveis de 3 e JANELA meses dentro de cada mandato."""
    nvot = v.groupby("mes").idVotacao.nunique().rename("n_votacoes")
    agg = v.groupby(["mandato", "partido", "mes"]).agg(
        validos=("alinhado", "size"), alinhados=("alinhado", "sum"), validos_sn=("sim_nao", "sum")).reset_index()
    grades = []
    for mand, g in agg.groupby("mandato"):
        i, f = MANDATO[mand]
        meses = pd.date_range(i, min(f, pd.Timestamp(ic.FIM)), freq="MS")
        grades.append(pd.MultiIndex.from_product([[mand], g.partido.unique(), meses],
                                                 names=["mandato", "partido", "mes"]).to_frame(index=False))
    d = pd.concat(grades).merge(agg, how="left").fillna({"validos": 0, "alinhados": 0, "validos_sn": 0})
    d = d.merge(nvot, left_on="mes", right_index=True, how="left").fillna({"n_votacoes": 0})
    if cad is not None:
        d = d.merge(cad[["mes", "partido", "cadeiras"]], how="left").fillna({"cadeiras": 0})
        d["oportunidades"] = d.cadeiras * d.n_votacoes
    else:
        d["cadeiras"], d["oportunidades"] = np.nan, np.nan
    d = d.sort_values(["mandato", "partido", "mes"]).reset_index(drop=True)

    def taxas(sufixo, k):
        r = d.groupby(["mandato", "partido"])[["validos", "alinhados", "validos_sn", "oportunidades"]] \
             .rolling(k, min_periods=1).sum().reset_index(drop=True)
        d[f"taxa{sufixo}"] = r.alinhados / r.validos.replace(0, np.nan)
        d[f"taxa_estrita{sufixo}"] = r.alinhados / r.validos_sn.replace(0, np.nan)
        d[f"presenca{sufixo}"] = (r.validos / r.oportunidades.replace(0, np.nan)).clip(upper=1)
        d[f"entrega{sufixo}"] = d[f"taxa{sufixo}"] * d[f"presenca{sufixo}"]

    taxas("_mes", 1)
    taxas("_3m", 3)
    taxas(f"_{JANELA}m", JANELA)
    tot = d.groupby(["mandato", "partido"])[["validos", "alinhados", "oportunidades"]].transform("sum")
    d["taxa_mandato"] = tot.alinhados / tot.validos.replace(0, np.nan)
    d["entrega_mandato"] = tot.alinhados / tot.oportunidades.replace(0, np.nan)
    # g usado no painel mensal: janela principal; meses sem votos na janela recebem o primeiro
    # valor observado (início de mandato) e, na falta, a taxa do mandato
    for base, col in [("taxa", "g"), ("entrega", "g_presenca")]:
        x = d.groupby(["mandato", "partido"])[f"{base}_{JANELA}m"].bfill()
        d[col] = x.fillna(d[f"{base}_mandato"])
    return d


def governismo_periodo(v, cad, ini, fim, so_disputadas=False):
    """Taxa agregada de todas as votações em [ini, fim) e entrega com presença."""
    x = v[(v.data >= ini) & (v.data < fim) & (v.disputada | (not so_disputadas))]
    g = x.groupby("partido").agg(validos=("alinhado", "size"), alinhados=("alinhado", "sum"))
    g["taxa"] = g.alinhados / g.validos
    if cad is not None and len(x):
        nv = x.groupby("mes").idVotacao.nunique()
        op = cad[cad.mes.isin(nv.index)].assign(op=lambda c: c.cadeiras * c.mes.map(nv)).groupby("partido").op.sum()
        g["entrega"] = (g.alinhados / op.reindex(g.index)).clip(upper=1)
        g["presenca"] = (g.validos / op.reindex(g.index)).clip(upper=1)
    return g


# ------------------------------------------------------------------------- índices
def ponderar(comp, g, fallback=None):
    """comp com cadeiras x governismo (np intacto). Partido sem taxa recebe fallback
    (ou mantém as cadeiras, se não houver fallback)."""
    out = []
    for p, m, s in comp:
        if p == "np":
            out.append((p, m, 0))
            continue
        gi = g.get(p, np.nan)
        if not gi == gi and fallback is not None:
            gi = fallback.get(p, np.nan)
        out.append((p, m, s * (gi if gi == gi else 1.0)))
    return out


def pesos_partidos(comp, comp_e):
    part = [(p, m, s) for p, m, s in comp if p != "np"]
    M, Mp = sum(m for _, m, _ in comp), sum(m for _, m, _ in part)
    S, Se = sum(s for _, _, s in part), sum(s for p, _, s in comp_e if p != "np")
    se = dict((p, s) for p, _, s in comp_e)
    linhas = []
    for p, m, s in part:
        s_pot, s_ent = s / S if S else np.nan, se[p] / Se if Se else np.nan
        linhas.append({"partido": p, "ministros": m, "cadeiras": s, "M_total": m / M, "M_partidario": m / Mp,
                       "S_potencial": s_pot, "S_efetivo": s_ent,
                       "dif_S_pp": 100 * (s_ent - s_pot),
                       "retorno_potencial": (m / Mp) / s_pot if s_pot else np.nan,
                       "retorno_efetivo": (m / Mp) / s_ent if s_ent else np.nan})
    return linhas


def fmt(comp):
    return " ".join(f"{p}({m},{s:.1f})" if isinstance(s, float) else f"{p}({m},{s})" for p, m, s in comp)


def parse_comp(txt):
    return [(p, int(m), int(s)) for p, m, s in re.findall(r"([\wÀ-ú]+)\((\d+),(\d+)\)", txt)]


# ------------------------------------------------------------------------- execução
def main():
    ic.SAIDA.mkdir(exist_ok=True)
    votos, cads, govs = {}, {}, []
    for leg, (mands, _) in LEGISLATURAS.items():
        v = carregar_votos(leg)
        if v is None:
            print(f"leg{leg}: dados/leg{leg}/votos.parquet não encontrado - {', '.join(mands)} ficam de fora "
                  f"(rode: python baixar_legislatura.py --legislatura {leg})")
            continue
        v = v[v.mandato.isin(mands)]
        if v.empty:
            print(f"leg{leg}: nenhuma votação de plenário com orientação Sim/Não do governo")
            continue
        cad = carregar_cadeiras(leg, ic.FIM)
        votos[leg], cads[leg] = v, cad
        govs.append(governismo_mensal(v, cad).assign(legislatura=leg))
        print(f"leg{leg}: {v.idVotacao.nunique()} votações, {len(v):,} votos válidos ({v.data.min().date()} a {v.data.max().date()})")
    gov = pd.concat(govs, ignore_index=True)
    gov.to_csv(ic.SAIDA / "governismo_partidos.csv", sep=";", index=False, float_format="%.4f")
    mand_cobertos = set(gov.mandato)

    # ----------------------------------------------------------------- painel mensal
    alm = ic.comp_almeida()
    gab_l3 = pd.read_csv(ic.BRUTOS / "lula3_gabinete_2023_2026.csv", sep=";", parse_dates=["inicio", "fim"])
    cad57 = cadeiras_mensais(fim=ic.FIM)
    cad57["partido"] = cad57.partido.replace(ic.NORM)
    cad57 = cad57.groupby(["t", "partido"], as_index=False).cadeiras.sum()
    lk = {k: (x.set_index("partido").g, x.set_index("partido").g_presenca)
          for k, x in gov.groupby(["mandato", "mes"])}
    vazio = (pd.Series(dtype=float), pd.Series(dtype=float))
    taxa_mand = gov.groupby(["mandato", "partido"]).taxa_mandato.first()
    mens = []
    for t in pd.date_range("2015-01-01", ic.FIM, freq="MS") + pd.Timedelta(days=14):
        mand = mandato_de(t)
        if mand not in mand_cobertos:
            continue
        comp = ic.comp_lula3(t, gab_l3, cad57)[0] if mand == "Lula 3" else alm[alm.inicio <= t].iloc[-1].comp
        mes = t - pd.Timedelta(days=14)
        g, gp = lk.get((mand, mes), vazio)
        fb = taxa_mand.loc[mand] if mand in taxa_mand.index else None
        ce, cp = ponderar(comp, g, fb), ponderar(comp, gp, fb)
        mens.append({"data": t.date(), "mandato": mand,
                     "gabinete": "Lula 3" if mand == "Lula 3" else alm[alm.inicio <= t].iloc[-1].gabinete,
                     "tamanho": sum(p != "np" for p, _, _ in comp),
                     "ministros_np": sum(m for p, m, _ in comp if p == "np"),
                     "prop_potencial": ic.coalescencia(comp), "prop_efetivo": ic.coalescencia(ce),
                     "prop_efetivo_presenca": ic.coalescencia(cp),
                     "governismo_coalizao": sum(s for p, _, s in ce if p != "np") / max(1, sum(s for p, _, s in comp if p != "np")),
                     "composicao_potencial": fmt(comp), "composicao_efetiva": fmt(ce)})
    mens = pd.DataFrame(mens)
    mens["dif"] = mens.prop_efetivo - mens.prop_potencial
    mens["dif_presenca"] = mens.prop_efetivo_presenca - mens.prop_potencial
    mens.to_csv(ic.SAIDA / "proporcionalidade_entregue_mensal.csv", sep=";", index=False, float_format="%.2f")

    # ------------------------------------------------------------------ resumo
    def resumo(df, rotulo):
        return {"periodo": rotulo, "meses": len(df),
                "potencial_media": df.prop_potencial.mean(), "potencial_dp": df.prop_potencial.std(),
                "efetivo_media": df.prop_efetivo.mean(), "efetivo_dp": df.prop_efetivo.std(),
                "efetivo_presenca_media": df.prop_efetivo_presenca.mean(),
                "efetivo_presenca_dp": df.prop_efetivo_presenca.std(),
                "dif_media": df.dif.mean(), "dif_presenca_media": df.dif_presenca.mean(),
                "governismo_coalizao": df.governismo_coalizao.mean()}
    res = [resumo(mens[mens.mandato == m], m) for m, _, _ in ic.MANDATOS if m in mand_cobertos]
    d = pd.to_datetime(mens.data)
    res += [resumo(mens[(d >= pd.Timestamp(i)) & (d < pd.Timestamp(f))], f"Lula 3 {r}") for r, i, f in SUBPERIODOS_LULA3]
    res = pd.DataFrame(res).round(2)
    res.to_csv(ic.SAIDA / "proporcionalidade_entregue_resumo.csv", sep=";", index=False)

    # --------------------------------------------------------------- por gabinete
    tg = gb.tabela_gabinetes()
    tg["inicio"], tg["fim"] = pd.to_datetime(tg.inicio), pd.to_datetime(tg.fim)
    tg["mandato"] = tg.inicio.map(mandato_de)
    tg = tg[tg.mandato.isin(mand_cobertos)]
    leg_de = {m: leg for leg, (ms, _) in LEGISLATURAS.items() for m in ms}
    gabs, parts = [], []
    for _, r in tg.iterrows():
        leg = leg_de[r.mandato]
        comp = parse_comp(r.composicao)
        gp = governismo_periodo(votos[leg], cads[leg], r.inicio, r.fim)
        fb = taxa_mand.loc[r.mandato]
        ce = ponderar(comp, gp.taxa, fb)
        cp = ponderar(comp, gp.entrega, None) if "entrega" in gp else ce
        gd = governismo_periodo(votos[leg], cads[leg], r.inicio, r.fim, so_disputadas=True)
        cd = ponderar(comp, gd.taxa, fb)
        n_vot = votos[leg][(votos[leg].data >= r.inicio) & (votos[leg].data < r.fim)].idVotacao.nunique()
        gabs.append({"gabinete": r.gabinete, "mandato": r.mandato, "evento": r.evento, "inicio": r.inicio.date(),
                     "fim": r.fim.date(), "meses": r.meses, "n_votacoes": n_vot, "tamanho": r.tamanho,
                     "ministros_np": r.ministros_np,
                     "prop_potencial": round(ic.coalescencia(comp), 1),
                     "prop_efetivo": round(ic.coalescencia(ce), 1),
                     "prop_efetivo_presenca": round(ic.coalescencia(cp), 1),
                     "prop_efetivo_disputadas": round(ic.coalescencia(cd), 1),
                     "dif": round(ic.coalescencia(ce) - ic.coalescencia(comp), 1),
                     "governismo_coalizao": round(sum(s for p, _, s in ce if p != "np") / max(1, sum(s for p, _, s in comp if p != "np")), 3),
                     "composicao_potencial": fmt(comp), "composicao_efetiva": fmt(ce)})
        for l in pesos_partidos(comp, ce):
            l.update(gabinete=r.gabinete, mandato=r.mandato, meses=r.meses,
                     governismo=gp.taxa.get(l["partido"], np.nan),
                     governismo_disputadas=gd.taxa.get(l["partido"], np.nan),
                     presenca=gp.presenca.get(l["partido"], np.nan) if "presenca" in gp else np.nan)
            parts.append(l)
    gabs = pd.DataFrame(gabs)
    gabs.to_csv(ic.SAIDA / "proporcionalidade_entregue_gabinetes.csv", sep=";", index=False)
    parts = pd.DataFrame(parts)[["gabinete", "mandato", "meses", "partido", "ministros", "cadeiras", "governismo",
                                 "governismo_disputadas", "presenca", "M_total", "M_partidario", "S_potencial", "S_efetivo", "dif_S_pp",
                                 "retorno_potencial", "retorno_efetivo"]]
    parts.to_csv(ic.SAIDA / "proporcionalidade_entregue_partidos.csv", sep=";", index=False, float_format="%.4f")

    # ---------------------------------------------------------------- impressão
    pd.set_option("display.width", 220)
    print("\nPor gabinete:\n", gabs.drop(columns=["composicao_potencial", "composicao_efetiva", "evento"]).to_string(index=False))
    print("\nResumo:\n", res.to_string(index=False))
    for mand in sorted(mand_cobertos, key=lambda m: MANDATO[m][0]):
        p = parts[parts.mandato == mand]
        w = p.assign(w=p.meses).groupby("partido").apply(
            lambda x: pd.Series({c: np.average(x[c], weights=x.w) for c in
                                 ["governismo", "S_potencial", "S_efetivo", "dif_S_pp", "retorno_potencial", "retorno_efetivo"]}
                                | {"meses": x.w.sum()}), include_groups=False)
        print(f"\n{mand} - partidos (média ponderada pela duração dos gabinetes em que tiveram ministério):\n",
              w.sort_values("dif_S_pp").round(3).to_string())


if __name__ == "__main__":
    main()
