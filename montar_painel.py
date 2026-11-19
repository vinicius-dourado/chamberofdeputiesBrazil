"""Monta o painel de reeleição (1 linha por deputado) com as variáveis de Pereira & Rennó (2001),
exceto as de emendas/pork barrel (Emendas, Pork, MédiaExecução, TotalEmendas).

Caso: 57ª legislatura (2023-2027) -> eleição de 04/10/2026; eleição anterior = 2022.
Medidas de atuação na Câmara são cortadas na data da eleição.

Entradas: dados/leg57/*.parquet (baixar_legislatura.py, baixar_cargos.py),
          dados/tse/*.parquet (baixar_tse.py), dados/manual/*.csv
Saídas:   dados/leg57/reeleicao_painel.parquet (+ .csv local)
          dados/leg57/reeleicao_alinhamento_partidos.parquet (base da definição de coalizão)

Uso: python montar_painel.py
"""
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

LEG, ANO, ANO_ANT = 57, 2026, 2022
ELEICAO = "2026-10-04"
D = Path(f"dados/leg{LEG}")
T = Path("dados/tse")
M = Path("dados/manual")

# fusões/incorporações: a mudança de sigla não é troca voluntária de partido
FUSOES = {("PATRIOTA", "PRD"), ("PTB", "PRD"), ("PSC", "PODE"), ("PROS", "SOLIDARIEDADE")}
# sucessores -> antecessores (para comparar partido de 2026 com coligação de 2022)
ANTECESSORES = {"PRD": {"PTB", "PATRIOTA"}, "PODE": {"PSC"}, "SOLIDARIEDADE": {"PROS"}}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]", "", s)


def siglas_coligacao(txt, partido):
    """'MDB / Federação X (PT / PC do B / PV) / PDT' -> {MDB, PT, PCDOB, PV, PDT}."""
    if not isinstance(txt, str) or txt.strip().upper() in ("#NULO", "PARTIDO ISOLADO", ""):
        return {norm(partido)}
    toks = re.split(r"[/()]", txt)
    return {norm(t) for t in toks if t.strip() and not t.strip().upper().startswith("FEDERA")} | {norm(partido)}


# Bolognesi, Codato, Ribeiro & Silva (2025), Harvard Dataverse doi:10.7910/DVN/MFIXKW, onda de 2022 (0-10)
BOLOGNESI_SIGLAS = {"PCDOB": "p_cdo_b", "CIDADANIA": "cdd", "SOLIDARIEDADE": "sdd", "PP": "progre",
                    "REPUBLICANOS": "rep", "PODE": "podemos", "UNIAO": "uniao", "PATRIOTA": "patri"}
# faixas de Bolognesi, Ribeiro & Codato (2023)
FAIXAS_7 = [(1.5, "extrema-esquerda"), (3.0, "esquerda"), (4.5, "centro-esquerda"), (5.5, "centro"),
            (7.0, "centro-direita"), (8.5, "direita"), (10.01, "extrema-direita")]
# agrupamento para as 3 dummies do artigo
TRES = {"extrema-esquerda": "esquerda", "esquerda": "esquerda", "centro-esquerda": "esquerda",
        "centro": "centro", "centro-direita": "centro", "direita": "direita", "extrema-direita": "direita"}


def ideologia_bolognesi():
    """Média dos especialistas por partido (onda 2022), indexada pela sigla normalizada do partido."""
    d = pd.read_csv(M / "bolognesi_2018_2022_df_experts.csv", sep=";")
    cols = [c for c in d.columns if c.startswith("ideol_22_")]
    m = d[cols].apply(pd.to_numeric, errors="coerce").mean()
    m.index = m.index.str.replace("ideol_22_", "")
    out = {}
    for chave, val in m.items():
        out[norm(chave)] = val
    for sigla, chave in BOLOGNESI_SIGLAS.items():
        out[sigla] = m[chave]
    out["PRD"] = d[["ideol_22_ptb", "ideol_22_patri"]].apply(pd.to_numeric, errors="coerce").stack().mean()  # fusão PTB+Patriota
    return pd.Series(out)


def faixa_7(x):
    if pd.isna(x):
        return None
    return next(nome for lim, nome in FAIXAS_7 if x < lim)


SIGLA_IPEA = {"UNIAO": "UNIAO", "REP": "REPUBLICANOS", "PCDOB": "PCDOB", "REDE": "REDE", "PODEMOS": "PODE"}


def gabinetes():
    """Gabinetes e partidos com ministério (Ipea; planilha 'dados' de dados/manual)."""
    g = pd.read_excel(M / "proporcionalidade_ministerios_cadeiras_ipea.xlsx", sheet_name="dados")
    g = g.dropna(subset=["Gabinete"])
    g["inicio"] = pd.to_datetime(g["Início"]).dt.strftime("%Y-%m-%d")
    g["partidos"] = g["Partido (ministros, cadeiras na CD)"].map(
        lambda t: {SIGLA_IPEA.get(norm(x.split("(")[0]), norm(x.split("(")[0]))
                   for x in str(t).split(";") if x and not x.startswith("np")})
    return g.sort_values("inicio")[["Gabinete", "inicio", "partidos"]].rename(columns={"Gabinete": "gabinete"})


def gabinete_em(gab, data):
    return gab[gab["inicio"] <= data].iloc[-1]


def base_em(gab, partido, data):
    """Partido tinha ministério no gabinete vigente na data? (sucessores herdam de antecessores)"""
    if not isinstance(partido, str):
        return False
    alvo = {norm(partido)} | {norm(x) for x in ANTECESSORES.get(norm(partido), ())}
    return bool(alvo & gabinete_em(gab, data)["partidos"])


def intervalos_exercicio(hist):
    """[inicio, fim) em que cada deputado estava em Exercício, a partir do histórico de status."""
    h = hist.sort_values(["id", "dataHora"]).copy()
    h["ini"] = h["dataHora"].str[:10]
    h["fim"] = h.groupby("id")["ini"].shift(-1).fillna("2099-12-31")
    return h[h["situacao"] == "Exercício"][["id", "ini", "fim"]]


def main():
    dep = pd.read_parquet(D / "deputados.parquet")
    dep["id"] = dep["id"].astype(int)
    ident = pd.read_parquet(D / "deputados_ident.parquet")
    p = dep[["id", "nome", "siglaUf", "sexo", "dataNascimento"]].merge(ident[["id", "cpf"]], on="id")
    p["idade_eleicao"] = (pd.to_datetime(ELEICAO) - pd.to_datetime(p["dataNascimento"])).dt.days // 365

    hist = pd.read_parquet(D / "deputados_historico.parquet")
    hist["id"] = hist["id"].astype(int)
    hist = hist[hist["dataHora"].str[:10] < ELEICAO]
    exe = intervalos_exercicio(hist)
    exe_c = exe.assign(fim=exe["fim"].clip(upper=ELEICAO))
    dias = (pd.to_datetime(exe_c["fim"]) - pd.to_datetime(exe_c["ini"])).dt.days.groupby(exe_c["id"]).sum()
    p["dias_exercicio"] = p["id"].map(dias).fillna(0).astype(int)
    defin = hist[hist["descricaoStatus"].str.contains("Afastamento definitivo", na=False)]
    defin = defin.sort_values("dataHora").groupby("id").last()
    p["saida_definitiva"] = p["id"].map(defin["descricaoStatus"])
    p["saida_definitiva_data"] = p["id"].map(defin["dataHora"].str[:10])

    # ------------------------------------------------------------------ TSE: ligação por CPF
    cand = {a: pd.read_parquet(T / f"candidatos_{a}.parquet") for a in (ANO_ANT, ANO)}
    cdf = {a: pd.read_parquet(T / f"candidatos_depfed_{a}.parquet") for a in (ANO_ANT, ANO)}
    votos = {a: pd.read_parquet(T / f"votos_depfed_mun_{a}.parquet") for a in (ANO_ANT, ANO)}
    aptos = {a: pd.read_parquet(T / f"aptos_mun_{a}.parquet") for a in (ANO_ANT, ANO)}
    contas = {a: pd.read_parquet(T / f"contas_depfed_{a}.parquet") for a in (ANO_ANT, ANO)}

    # VD seleção: o que o deputado disputou em 2026 (prioridade do cargo mais alto)
    c26 = cand[ANO].copy()
    c26["cargo"] = c26["DS_CARGO"].str.upper()
    prioridade = ["PRESIDENTE", "VICE-PRESIDENTE", "GOVERNADOR", "VICE-GOVERNADOR", "SENADOR",
                  "DEPUTADO FEDERAL", "1º SUPLENTE", "2º SUPLENTE", "DEPUTADO ESTADUAL", "DEPUTADO DISTRITAL"]
    c26["ordem"] = c26["cargo"].map({c: i for i, c in enumerate(prioridade)}).fillna(99)
    c26 = c26[c26["NR_CPF_CANDIDATO"].isin(p["cpf"])].sort_values(["NR_CPF_CANDIDATO", "ordem", "NR_TURNO"])
    disp = c26.groupby("NR_CPF_CANDIDATO").first()
    p["cargo_disputado_2026"] = p["cpf"].map(disp["cargo"]).fillna("NÃO CONCORREU")
    p["situacao_candidatura_2026"] = p["cpf"].map(disp["DS_SITUACAO_CANDIDATURA"])
    p["concorreu_reeleicao"] = (p["cargo_disputado_2026"] == "DEPUTADO FEDERAL").astype(int)

    # SQ de dep. federal em cada eleição
    for a in (ANO_ANT, ANO):
        cf = cand[a][(cand[a]["CD_CARGO"] == "6") & cand[a]["NR_CPF_CANDIDATO"].isin(p["cpf"])]
        cf = cf.sort_values("NR_TURNO").groupby("NR_CPF_CANDIDATO").last()
        p[f"sq_{a}"] = p["cpf"].map(cf["SQ_CANDIDATO"])
        p[f"partido_tse_{a}"] = p["cpf"].map(cf["SG_PARTIDO"])
        sit = cdf[a].set_index("SQ_CANDIDATO")
        p[f"situacao_tse_{a}"] = p[f"sq_{a}"].map(sit["DS_SIT_TOT_TURNO"])
        p[f"votos_{a}"] = p[f"sq_{a}"].map(sit["votos_total"])
    p["condicao_2022"] = np.where(p["situacao_tse_2022"].str.startswith("ELEITO", na=False), "eleito", "suplente")
    p["reeleito"] = np.where(p["concorreu_reeleicao"] == 1,
                             p["situacao_tse_2026"].str.startswith("ELEITO", na=False).astype(float), np.nan)
    p["fonte_situacao_2026"] = p["sq_2026"].map(cdf[ANO].set_index("SQ_CANDIDATO")["fonte_situacao"])

    # ------------------------------------------- Concentração, Competição, MesmaBase
    for a in (ANO_ANT, ANO):
        v = votos[a]
        v = v[v["votos"] > 0]
        tot = v.groupby("SQ_CANDIDATO")["votos"].sum()
        top = v.sort_values("votos", ascending=False).groupby("SQ_CANDIDATO").first()
        # melhor outro candidato no município-base
        rank = v.sort_values(["CD_MUNICIPIO", "votos"], ascending=[True, False])
        prim = rank.groupby("CD_MUNICIPIO").nth(0).set_index("CD_MUNICIPIO")
        seg = rank.groupby("CD_MUNICIPIO").nth(1).set_index("CD_MUNICIPIO")
        ap = aptos[a].set_index("CD_MUNICIPIO")["QT_APTOS"]
        sq = p[f"sq_{a}"]
        mun = sq.map(top["CD_MUNICIPIO"])
        proprio = sq.map(top["votos"])
        prim_sq, prim_v = mun.map(prim["SQ_CANDIDATO"]), mun.map(prim["votos"])
        outro = np.where(prim_sq == sq, mun.map(seg["votos"]), prim_v)
        p[f"municipio_base_{a}"] = mun
        p[f"municipio_base_nome_{a}"] = sq.map(top["NM_MUNICIPIO"])
        p[f"concentracao_{a}"] = proprio / sq.map(tot)
        p[f"competicao_{a}"] = (proprio - outro) / mun.map(ap)
        p[f"competicao_bruta_{a}"] = proprio - outro
    p["mesma_base"] = np.where(p["municipio_base_2026"].notna() & p["municipio_base_2022"].notna(),
                               (p["municipio_base_2026"] == p["municipio_base_2022"]).astype(float), np.nan)

    # ------------------------------------------------------------------- Gastos
    for a in (ANO_ANT, ANO):
        k = contas[a].set_index("SQ_CANDIDATO")
        apt_uf = aptos[a].groupby("SG_UF")["QT_APTOS"].sum()
        p[f"gastos_{a}"] = p[f"sq_{a}"].map(k["despesas_contratadas"])
        p[f"gastos_pagos_{a}"] = p[f"sq_{a}"].map(k["despesas_pagas"])
        p[f"receitas_{a}"] = p[f"sq_{a}"].map(k["receitas_total"])
        p[f"gastos_por_eleitor_{a}"] = p[f"gastos_{a}"] / p["siglaUf"].map(apt_uf)

    # ------------------------------------------------------------------- Governador
    g = cand[ANO_ANT]
    g = g[(g["DS_CARGO"].str.upper() == "GOVERNADOR") & g["DS_SIT_TOT_TURNO"].str.startswith("ELEITO", na=False)]
    gov = {r.SG_UF: (r.SG_PARTIDO, siglas_coligacao(r.DS_COMPOSICAO_COLIGACAO, r.SG_PARTIDO))
           for r in g.itertuples()}
    p["governador_2022_partido"] = p["siglaUf"].map(lambda u: gov.get(u, (None,))[0])

    def mesma_colig(uf, partido):
        if uf not in gov or not isinstance(partido, str):
            return np.nan
        alvo = {norm(partido)} | {norm(x) for x in ANTECESSORES.get(norm(partido), ())}
        return float(bool(alvo & gov[uf][1]))
    p["governador"] = [mesma_colig(u, x) for u, x in zip(p["siglaUf"], p["partido_tse_2022"])]
    partido_eleicao = p["partido_tse_2026"]

    # ------------------------------------------------- Plenário: Ausência e Índice
    vot = pd.read_parquet(D / "votacoes.parquet", columns=["idVotacao", "data", "siglaOrgao", "tem_votos_nominais"])
    vot = vot[(vot["siglaOrgao"] == "PLEN") & vot["tem_votos_nominais"].astype(bool) & (vot["data"] < ELEICAO)]
    vs = pd.read_parquet(D / "votos.parquet", columns=["idVotacao", "deputado_id", "voto", "orientacao_governo",
                                                        "deputado_siglaPartido", "data"])
    vs["deputado_id"] = vs["deputado_id"].astype(int)
    vs = vs[vs["idVotacao"].isin(vot["idVotacao"])]
    # votações em que o deputado estava em exercício
    x = exe.merge(vot[["idVotacao", "data"]], how="cross")
    x = x[(x["data"] >= x["ini"]) & (x["data"] < x["fim"])].drop_duplicates(["id", "idVotacao"])
    x = x.merge(vs[["idVotacao", "deputado_id"]].rename(columns={"deputado_id": "id"}).assign(votou=1),
                on=["id", "idVotacao"], how="left")
    agg = x.groupby("id").agg(votacoes_em_exercicio=("idVotacao", "size"), votou=("votou", "sum"))
    p["votacoes_em_exercicio"] = p["id"].map(agg["votacoes_em_exercicio"]).fillna(0).astype(int)
    p["ausencia"] = p["votacoes_em_exercicio"] - p["id"].map(agg["votou"]).fillna(0).astype(int)
    p["ausencia_pct"] = p["ausencia"] / p["votacoes_em_exercicio"].replace(0, np.nan)
    o = vs[vs["orientacao_governo"].isin(["Sim", "Não"]) & vs["voto"].isin(["Sim", "Não", "Obstrução", "Abstenção"])]
    o = o.assign(seg=(o["voto"] == o["orientacao_governo"]))
    idx = o.groupby("deputado_id")["seg"].agg(["mean", "size"])
    p["indice"] = p["id"].map(idx["mean"])
    p["indice_n_votacoes"] = p["id"].map(idx["size"]).fillna(0).astype(int)

    # alinhamento dos partidos com o governo (fidelidade à coalizão; NÃO define a coalizão)
    alin = o.groupby("deputado_siglaPartido")["seg"].agg(["mean", "size"]).rename(
        columns={"mean": "alinhamento_governo", "size": "n_votos"}).reset_index()
    alin = alin.rename(columns={"deputado_siglaPartido": "siglaPartido"})

    # fidelidade partidária: % de votos iguais à orientação da bancada do partido
    fp = pd.read_parquet(D / "votos.parquet", columns=["idVotacao", "deputado_id", "seguiu_orientacao_partido"])
    fp = fp[fp["idVotacao"].isin(vot["idVotacao"]) & fp["seguiu_orientacao_partido"].notna()]
    fp["deputado_id"] = fp["deputado_id"].astype(int)
    p["fidelidade_partidaria"] = p["id"].map(fp.groupby("deputado_id")["seguiu_orientacao_partido"].mean())

    # coalizão = partidos com ministério no gabinete vigente (Ipea, Acir Almeida; dados/manual)
    gab = gabinetes()
    em_base = lambda partido, data: base_em(gab, partido, data)  # noqa: E731
    alin["base_governo_eleicao"] = alin["siglaPartido"].map(lambda s: em_base(s, ELEICAO))
    alin.to_parquet(D / "reeleicao_alinhamento_partidos.parquet", index=False)

    # ------------------------------------------------ trocas de partido (Entrar/SairCoalizão)
    fil = pd.read_parquet(D / "deputados_partidos.parquet")
    fil["id"] = fil["id"].astype(int)
    fil = fil[fil["dataInicio"].str[:10] < ELEICAO].sort_values(["id", "dataInicio"])
    fil["anterior"] = fil.groupby("id")["siglaPartido"].shift()
    tr = fil[fil["anterior"].notna() & (fil["anterior"] != fil["siglaPartido"])].copy()
    tr = tr[~tr.apply(lambda r: (norm(r["anterior"]), norm(r["siglaPartido"])) in
                      {(norm(a), norm(b)) for a, b in FUSOES}, axis=1)]
    tr["orig_base"] = [em_base(a, d[:10]) for a, d in zip(tr["anterior"], tr["dataInicio"])]
    tr["dest_base"] = [em_base(b, d[:10]) for b, d in zip(tr["siglaPartido"], tr["dataInicio"])]
    tr[["id", "nome", "anterior", "siglaPartido", "dataInicio", "orig_base", "dest_base"]].to_parquet(
        D / "reeleicao_trocas_partido.parquet", index=False)
    p["trocas_partido"] = p["id"].map(tr.groupby("id").size()).fillna(0).astype(int)
    p["entrar_coalizao"] = p["id"].isin(tr.loc[tr["dest_base"] == True, "id"]).astype(int)  # noqa: E712
    p["sair_coalizao"] = p["id"].isin(tr.loc[(tr["orig_base"] == True) & (tr["dest_base"] == False), "id"]).astype(int)  # noqa: E712

    # ---------------------------------------------------------------- Projetos
    props = pd.read_parquet(D / "proposicoes.parquet", columns=["id", "siglaTipo", "dataApresentacao",
                                                                "ultimoStatus_descricaoSituacao"])
    aut = pd.read_parquet(D / "proposicoes_autores.parquet")
    props = props[props["siglaTipo"].isin(["PL", "PLP", "PEC", "PDL"]) & (props["dataApresentacao"] < ELEICAO)]
    st = props["ultimoStatus_descricaoSituacao"].fillna("")
    props["norma"] = st.eq("Transformado em Norma Jurídica")
    props["aprovado"] = st.str.contains("Norma Jurídica|Senado Federal|Sanção|Promulgação|Envio ao Executivo")
    aut = aut[aut["ordemAssinatura"].astype(str) == "1"].merge(props, left_on="idProposicao", right_on="id")
    aut["idDeputadoAutor"] = aut["idDeputadoAutor"].astype(int)
    g_ = aut.groupby("idDeputadoAutor")
    p["projetos"] = p["id"].map(g_["aprovado"].sum()).fillna(0).astype(int)
    p["projetos_norma"] = p["id"].map(g_["norma"].sum()).fillna(0).astype(int)
    p["projetos_apresentados"] = p["id"].map(g_.size()).fillna(0).astype(int)

    # -------------------------------------------------------------------- Mesa
    mesa = pd.read_parquet(D / "cargos_mesa.parquet")
    mesa = mesa[mesa["dataInicio"] < ELEICAO]

    def esc_mesa(t):
        t = t or ""
        if t == "Presidente":
            return 5
        if t.startswith("1º Vice"):
            return 4
        if "Vice-Presidente" in t:
            return 3
        if "Suplente" in t:
            return 1
        return 2 if "Secretário" in t else 0
    mesa["esc"] = mesa["titulo"].map(esc_mesa)
    p["mesa"] = p["id"].map(mesa.groupby("id")["esc"].max()).fillna(0).astype(int)

    # ------------------------------------------------------ Permanente / Especial
    org = pd.read_parquet(D / "cargos_orgaos.parquet")
    org = org[org["id"].notna() & (org["dataInicio"].fillna("") < ELEICAO)].copy()
    org["id"] = org["id"].astype(int)
    esc_com = {"Presidente": 4, "Relator": 3, "1º Vice-Presidente": 3, "Vice-Presidente": 3,
               "2º Vice-Presidente": 2, "3º Vice-Presidente": 1, "Relator-Parcial": 1, "Sub-Relator": 1}
    org["esc"] = org["cargo"].map(esc_com).fillna(0)
    for nome, cod in (("permanente", "2"), ("especial", "3"), ("cpi", "4")):
        o_ = org[org["codTipoOrgao"] == cod]
        p[nome] = p["id"].map(o_.groupby("id")["esc"].max()).fillna(0).astype(int)
        p[f"{nome}_n_titular"] = p["id"].map(
            o_[o_["cargo"] != "Suplente"].groupby("id")["idOrgao"].nunique()).fillna(0).astype(int)

    # ------------------------------------------------------------------ Partpos
    lid = pd.read_parquet(D / "cargos_lideres.parquet")
    lid["id"] = lid["id"].astype(int)
    lid = lid[lid["dataInicio"].fillna("") < ELEICAO]
    esc_lid = {"Líder": 3, "Presidente": 3, "1º Vice-Líder": 2, "Vice-Líder": 1, "Líder Administrativo": 1,
               "Representante": 1}
    lid["esc"] = lid["titulo"].map(esc_lid).fillna(0)
    part = lid[lid["bancada_tipo"].isin(["Partido Político", "Bloco Parlamentar"])]
    p["partpos"] = p["id"].map(part.groupby("id")["esc"].max()).fillna(0).astype(int)
    p["lideranca_governo"] = p["id"].isin(lid.loc[lid["bancada_tipo"].str.startswith("Governo"), "id"]).astype(int)
    p["lideranca_oposicao"] = p["id"].isin(
        lid.loc[lid["bancada_tipo"].str.match("Oposição|Minoria"), "id"]).astype(int)

    # ----------------------------------------------------- Senior, Histleg, Histexec
    sen = pd.read_parquet(D / "senioridade.parquet")
    p["senior"] = p["id"].map(sen.groupby("id")["idLegislatura"].nunique()).fillna(0).astype(int)
    me = pd.read_parquet(D / "deputados_mandatos_externos.parquet")
    me["id"] = me["id"].astype(int)
    antes = me[me["anoInicio"].astype(float) < 2023]
    leg_ = antes[antes["cargo"].isin(["Deputado(a) Estadual", "Deputado(a) Distrital", "Vereador(a)"])]
    exe_ = antes[antes["cargo"].isin(["Prefeito(a)", "Vice-Prefeito(a)", "Governador(a)", "Vice-Governador(a)"])]
    p["histleg"] = p["id"].map(leg_.groupby("id").size()).fillna(0).astype(int)
    p["histexec"] = p["id"].map(exe_.groupby("id").size()).fillna(0).astype(int)
    pref24 = me[me["cargo"].isin(["Prefeito(a)", "Vice-Prefeito(a)"]) & (me["anoInicio"].astype(float) == 2025)]
    p["eleito_prefeito_2024"] = p["id"].isin(pref24["id"]).astype(int)

    # ------------------------------------------------------ Burocracia / Empresa
    prof = pd.read_parquet(D / "deputados_profissoes.parquet")
    oc = pd.read_parquet(D / "deputados_ocupacoes.parquet")
    oc_pub = oc[oc["entidade"].fillna("").str.contains(
        r"Secretaria|Minist[ée]rio|Prefeitura|Governo|Fundação Nacional|Ag[êe]ncia|Autarquia|Departamento|"
        r"Instituto Nacional|Superintend[êe]ncia|Tribunal|Pol[íi]cia|Receita|Casa Civil", case=False, regex=True)]
    ocup22 = cand[ANO_ANT].set_index("NR_CPF_CANDIDATO")["DS_OCUPACAO"]
    ocup22 = ocup22[~ocup22.index.duplicated()]
    p["ocupacao_tse_2022"] = p["cpf"].map(ocup22)
    serv = p["ocupacao_tse_2022"].fillna("").str.contains("SERVIDOR PÚBLICO")
    p["burocracia"] = (p["id"].isin(oc_pub["id"]) | p["id"].isin(
        prof.loc[prof["titulo"].str.contains("Servidor", case=False), "id"]) | serv).astype(int)
    p["empresa"] = (p["id"].isin(prof.loc[prof["titulo"].str.contains("Empres", case=False), "id"]) |
                    p["ocupacao_tse_2022"].fillna("").str.contains("EMPRESÁRIO")).astype(int)
    afast = hist[hist["descricaoStatus"].str.contains("Ministro de Estado|Secretário", na=False)]
    p["afastou_para_executivo"] = p["id"].isin(afast["id"]).astype(int)

    # ------------------------------------------------------------- recortes de amostra
    ultimo = hist.sort_values("dataHora").groupby("id").last()["situacao"]
    p["em_exercicio_eleicao"] = (p["id"].map(ultimo) == "Exercício").astype(int)
    posse = hist[hist["descricaoStatus"].str.contains("Posse de Eleito Titular", na=False)
                 & (hist["dataHora"].str[:10] < "2023-03-01")]
    p["titular_posse_fev2023"] = p["id"].isin(posse["id"]).astype(int)

    # ------------------------------------------------------------- partido e ideologia
    fil_el = fil.groupby("id").last()["siglaPartido"]
    p["partido_camara_eleicao"] = p["id"].map(fil_el)
    p["partido_eleicao"] = partido_eleicao.fillna(p["partido_camara_eleicao"])
    ide = ideologia_bolognesi()
    ide.to_frame("ideologia_bolognesi").rename_axis("sigla_norm").reset_index().to_parquet(
        D / "reeleicao_ideologia_partidos.parquet", index=False)
    p["ideologia_bolognesi"] = p["partido_eleicao"].map(lambda s: ide.get(norm(s), np.nan))
    p["ideologia_7"] = p["ideologia_bolognesi"].map(faixa_7)
    p["ideologia"] = p["ideologia_7"].map(TRES)
    for k in ("esquerda", "centro", "direita"):
        p[k] = np.where(p["ideologia"].isna(), np.nan, (p["ideologia"] == k).astype(float))
    p["partido_base_governo"] = p["partido_eleicao"].map(lambda s: em_base(s, ELEICAO)).astype(int)
    p["gabinete_eleicao"] = gabinete_em(gab, ELEICAO)["gabinete"]

    p = p.drop(columns=["cpf", "dataNascimento"])
    p.to_parquet(D / "reeleicao_painel.parquet", index=False)
    p.to_csv(D / "reeleicao_painel.csv", sep=";", index=False)
    print(f"painel: {len(p)} deputados x {p.shape[1]} colunas")
    print(p["cargo_disputado_2026"].value_counts().to_string())
    print("reeleitos:", int(p["reeleito"].sum()), "de", int(p["concorreu_reeleicao"].sum()))
    print("em exercício na eleição:", p["em_exercicio_eleicao"].sum(),
          "| titulares empossados em fev/2023:", p["titular_posse_fev2023"].sum())


if __name__ == "__main__":
    main()
