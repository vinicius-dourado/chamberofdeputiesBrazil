"""Validação do pipeline: refaz a análise para a eleição de 1998 (50ª legislatura, 1995-1999), o caso original
de Pereira & Rennó (2001), e compara com o que o artigo relata.

Ideia: se o nosso código, aplicado aos dados de 1995-1998, reproduz os achados do artigo, as divergências
encontradas em 2026 vêm de mudança de cenário, não de falha nos dados ou nas variáveis.

Limite: a API da Câmara só tem votações nominais, Mesa, comissões, lideranças e histórico de partido a partir
de 2003. Por isso Ausência, Índice, Mesa, Permanente, Especial e Partpos não existem para 1998, e o teste usa um
MODELO REDUZIDO com as variáveis disponíveis nos dois períodos, estimado para 1998 e para 2026.

Fontes de 1998: TSE (candidatos 1994/1998, votação por município, eleitorado), Câmara (deputados da 50ª
legislatura, CPF, mandatos externos, profissões, legislaturas anteriores, proposições 1995-1998), Ipea (gabinetes
FHC 1), Bolognesi et al. (onda 2018, a mais próxima de 1998).

Pré-requisito: python baixar_tse.py --anos 1994 1998 --sem-contas
Uso: python validar_1998.py
Saídas: dados/leg50/*.parquet, resultados/validacao_1998/*.csv e resultados.json
"""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from baixar_legislatura import API, api_paginada, get, ler_anos, salvar
from montar_painel import (ANTECESSORES, OCUPACAO_PUBLICA, gabinetes, gabinete_em, norm, siglas_coligacao)
from replicar_artigo import heckprobit, probit_simples, teste_medias

LEG = 50
ELEICAO, ELEICAO_ANT = "1998-10-04", "1994-10-03"
D = Path(f"dados/leg{LEG}")
T = Path("dados/tse")
M = Path("dados/manual")
SAIDA = Path("resultados/validacao_1998")

# siglas de 1998 -> colunas da onda 2018 de Bolognesi et al.
BOLOGNESI_1998 = {"PFL": "dem", "PPB": "progressistas", "PMDB": "mdb", "PL": "pr", "PCDOB": "p_cdo_b",
                  "PPS": "pps", "PSDB": "psdb", "PT": "pt", "PDT": "pdt", "PSB": "psb", "PTB": "ptb", "PV": "pv",
                  "PSL": "psl", "PSC": "psc", "PMN": "pmn", "PRP": "prp", "PSTU": "pstu", "PCO": "pco", "PCB": "pcb",
                  "PRTB": "prtb", "PTC": "ptc", "PHS": "phs"}
FAIXAS = [(1.5, "esquerda"), (3.0, "esquerda"), (4.5, "esquerda"), (5.5, "centro"), (7.0, "centro"),
          (8.5, "direita"), (10.01, "direita")]

# Modelo reduzido: só variáveis que existem em 1998 e em 2026
SEL = ["concentracao_ant", "governador", "projetos", "senior", "histleg", "histexec",
       "entrar_coalizao", "sair_coalizao", "centro", "direita", "burocracia", "empresa"]
OUT = ["concentracao_ant", "mesma_base", "governador", "projetos", "senior", "histleg", "histexec",
       "entrar_coalizao", "sair_coalizao", "centro", "direita"]

# O que o artigo diz sobre cada variável testável (texto de Pereira & Rennó 2001)
ARTIGO = {
    "concentracao_ant": "dispersar votos favorece a reeleição (Concentração98, endógena; Concentração94 exógena)",
    "mesma_base": "não significativa, sinal negativo",
    "governador": "sem efeito direto na reeleição",
    "projetos": "não significativa",
    "senior": "não significativa",
    "histleg": "não destacada (não significativa)",
    "histexec": "negativa na seleção e no resultado",
    "burocracia": "só na seleção, não significativa",
    "empresa": "só na seleção, não significativa",
    "sair_coalizao": "negativa no resultado, sem efeito na seleção",
    "entrar_coalizao": "troca de partido de fora para dentro da coalizão; esperada positiva (não destacada)",
    "rho": "equações independentes (ρ = 0 não rejeitado)",
}


# ------------------------------------------------------------------ coleta Câmara (50ª legislatura)
def coletar_camara():
    D.mkdir(parents=True, exist_ok=True)
    if (D / "deputados_ident.parquet").exists():
        return
    print("Câmara: deputados da 50ª legislatura...")
    ids = sorted({int(d["id"]) for d in api_paginada("deputados", {"idLegislatura": LEG})})

    def lista(i, recurso):
        try:
            r = get(f"{API}/deputados/{i}/{recurso}", tentativas=3)
            return r.json()["dados"] if r is not None else []
        except RuntimeError:
            return []

    def detalhe(i):
        d = get(f"{API}/deputados/{i}").json()["dados"]
        return d, lista(i, "mandatosExternos"), lista(i, "profissoes"), lista(i, "ocupacoes")

    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(detalhe, ids))
    salvar(pd.DataFrame([{"id": d["id"], "cpf": d.get("cpf"), "nomeCivil": d.get("nomeCivil"),
                          "dataNascimento": d.get("dataNascimento"),
                          "siglaUf": (d.get("ultimoStatus") or {}).get("siglaUf"),
                          "nome": (d.get("ultimoStatus") or {}).get("nomeEleitoral")} for d, *_ in res]),
           "deputados_ident", D)
    salvar(pd.DataFrame([dict(m, id=d["id"]) for d, ms, _, _ in res for m in ms]), "deputados_mandatos_externos", D)
    salvar(pd.DataFrame([dict(p, id=d["id"]) for d, _, ps, _ in res for p in ps if p.get("titulo")]),
           "deputados_profissoes", D)
    salvar(pd.DataFrame([dict(o, id=d["id"]) for d, _, _, os_ in res for o in os_
                         if o.get("titulo") or o.get("entidade")]), "deputados_ocupacoes", D)

    print("Câmara: legislaturas anteriores (senioridade)...")
    alvo = set(ids)

    def membros(k):
        return [(k, int(x["id"])) for x in api_paginada("deputados", {"idLegislatura": k}) if int(x["id"]) in alvo]

    with ThreadPoolExecutor(6) as ex:
        pares = [p for lst in ex.map(membros, range(1, LEG)) for p in lst]
    salvar(pd.DataFrame(pares, columns=["idLegislatura", "id"]), "senioridade", D)

    print("Câmara: proposições 1995-1998...")
    brutos = Path("dados/brutos")
    anos = [1995, 1996, 1997, 1998]
    aut = ler_anos("proposicoesAutores", anos, brutos)
    props = ler_anos("proposicoes", anos, brutos)
    props = props[props["dataApresentacao"].str[:10].between("1995-02-01", ELEICAO)]
    aut = aut[aut["idProposicao"].isin(props["id"]) & aut["idDeputadoAutor"].isin(set(map(str, ids)))]
    salvar(props[["id", "siglaTipo", "dataApresentacao", "ultimoStatus_descricaoSituacao"]], "proposicoes", D)
    salvar(aut[["idProposicao", "idDeputadoAutor", "ordemAssinatura", "proponente"]], "proposicoes_autores", D)


# --------------------------------------------------------------------------------- painel 1998
def concentracao(votos, aptos, sq):
    v = votos[votos["votos"] > 0]
    tot = v.groupby("SQ_CANDIDATO")["votos"].sum()
    top = v.sort_values("votos", ascending=False).groupby("SQ_CANDIDATO").first()
    rank = v.sort_values(["CD_MUNICIPIO", "votos"], ascending=[True, False])
    prim = rank.groupby("CD_MUNICIPIO").nth(0).set_index("CD_MUNICIPIO")
    seg = rank.groupby("CD_MUNICIPIO").nth(1).set_index("CD_MUNICIPIO")
    mun = sq.map(top["CD_MUNICIPIO"])
    proprio = sq.map(top["votos"])
    outro = np.where(mun.map(prim["SQ_CANDIDATO"]) == sq, mun.map(seg["votos"]), mun.map(prim["votos"]))
    ap = aptos.set_index("CD_MUNICIPIO")["QT_APTOS"] if aptos is not None else None
    comp = (proprio - outro) / mun.map(ap) if ap is not None else pd.Series(np.nan, index=sq.index)
    return mun, proprio / sq.map(tot), comp


def ideologia_1998():
    d = pd.read_csv(M / "bolognesi_2018_2022_df_experts.csv", sep=";")
    m = d[[c for c in d.columns if c.startswith("ideol_18_")]].apply(pd.to_numeric, errors="coerce").mean()
    m.index = m.index.str.replace("ideol_18_", "")
    return {sig: m[col] for sig, col in BOLOGNESI_1998.items() if col in m.index}


def montar():
    ident = pd.read_parquet(D / "deputados_ident.parquet")
    p = ident.copy()
    cand98 = pd.read_parquet(T / "candidatos_1998.parquet")
    cand94 = pd.read_parquet(T / "candidatos_1994.parquet")
    dep98 = pd.read_parquet(T / "candidatos_depfed_1998.parquet")
    dep94 = pd.read_parquet(T / "candidatos_depfed_1994.parquet")

    # ---- 1998 por CPF
    c98 = cand98[cand98["NR_CPF_CANDIDATO"].isin(p["cpf"])].copy()
    c98["cargo"] = c98["DS_CARGO"].str.upper()
    ordem = {c: i for i, c in enumerate(["PRESIDENTE", "VICE-PRESIDENTE", "GOVERNADOR", "VICE-GOVERNADOR", "SENADOR",
                                          "DEPUTADO FEDERAL", "1º SUPLENTE", "2º SUPLENTE", "DEPUTADO ESTADUAL"])}
    c98["o"] = c98["cargo"].map(ordem).fillna(99)
    c98 = c98.sort_values(["NR_CPF_CANDIDATO", "o"]).groupby("NR_CPF_CANDIDATO").first()
    p["cargo_disputado_1998"] = p["cpf"].map(c98["cargo"]).fillna("NÃO CONCORREU")
    p["concorreu_reeleicao"] = (p["cargo_disputado_1998"] == "DEPUTADO FEDERAL").astype(int)
    p["partido_1998"] = p["cpf"].map(c98["SG_PARTIDO"])
    p["titulo"] = p["cpf"].map(c98["NR_TITULO_ELEITORAL_CANDIDATO"])
    f98 = cand98[(cand98["CD_CARGO"] == "6") & cand98["NR_CPF_CANDIDATO"].isin(p["cpf"])]
    f98 = f98.groupby("NR_CPF_CANDIDATO").last()
    p["sq_1998"] = p["cpf"].map(f98["SQ_CANDIDATO"])
    sit = dep98.set_index("SQ_CANDIDATO")["DS_SIT_TOT_TURNO"]
    p["reeleito"] = np.where(p["concorreu_reeleicao"] == 1,
                             p["sq_1998"].map(sit).str.startswith("ELEITO", na=False).astype(float), np.nan)
    p["ocupacao_1998"] = p["cpf"].map(c98["DS_OCUPACAO"])

    # ---- 1994 por título de eleitor; depois nome + data de nascimento
    f94 = cand94[cand94["CD_CARGO"] == "6"].copy()
    por_titulo = f94.dropna(subset=["NR_TITULO_ELEITORAL_CANDIDATO"]).groupby("NR_TITULO_ELEITORAL_CANDIDATO").last()
    p["sq_1994"] = p["titulo"].map(por_titulo["SQ_CANDIDATO"])
    f94["chave"] = f94["NM_CANDIDATO"].map(norm) + "|" + pd.to_datetime(
        f94["DT_NASCIMENTO"], dayfirst=True, errors="coerce").dt.strftime("%Y-%m-%d")
    por_nome = f94.groupby("chave").last()
    chave = p["nomeCivil"].map(norm) + "|" + p["dataNascimento"].fillna("")
    p["sq_1994"] = p["sq_1994"].fillna(chave.map(por_nome["SQ_CANDIDATO"]))
    f94i = f94.set_index("SQ_CANDIDATO")
    p["partido_1994"] = p["sq_1994"].map(f94i["SG_PARTIDO"])
    p["uf"] = p["sq_1994"].map(f94i["SG_UF"]).fillna(p["siglaUf"])
    p["eleito_1994"] = p["sq_1994"].map(dep94.set_index("SQ_CANDIDATO")["DS_SIT_TOT_TURNO"]).str.startswith(
        "ELEITO", na=False).astype(int)
    p["ocupacao_1994"] = p["sq_1994"].map(f94i["DS_OCUPACAO"])

    # ---- Concentração, Competição, MesmaBase
    v94 = pd.read_parquet(T / "votos_depfed_mun_1994.parquet")
    v98 = pd.read_parquet(T / "votos_depfed_mun_1998.parquet")
    ap98 = pd.read_parquet(T / "aptos_mun_1998.parquet")
    mun94, p["concentracao_ant"], _ = concentracao(v94, None, p["sq_1994"])
    mun98, p["concentracao_atual"], p["competicao_atual"] = concentracao(v98, ap98, p["sq_1998"])
    p["mesma_base"] = np.where(mun94.notna() & mun98.notna(), (mun94 == mun98).astype(float), np.nan)

    # ---- Governador: partido do deputado em 1994 na coligação do governador eleito em 1994
    # (consulta_cand_1994 não traz a composição; ela vem de consulta_coligacao_1994)
    import zipfile
    zc = zipfile.ZipFile(Path("dados/brutos/tse/consulta_coligacao_1994.zip"))
    col = pd.concat(pd.read_csv(zc.open(n), sep=";", encoding="latin-1", dtype=str)
                    for n in zc.namelist() if n.endswith(".csv"))
    col = col[col["DS_CARGO"].str.upper() == "GOVERNADOR"]
    g = cand94[(cand94["DS_CARGO"].str.upper() == "GOVERNADOR") & cand94["DS_SIT_TOT_TURNO"].str.startswith("ELEITO", na=False)]
    gov = {}
    for r in g.itertuples():
        s_ = set()
        for t in col[(col["SG_UF"] == r.SG_UF) & (col["SG_PARTIDO"] == r.SG_PARTIDO)]["DS_COMPOSICAO_COLIGACAO"]:
            s_ |= siglas_coligacao(t, r.SG_PARTIDO)
        gov[r.SG_UF] = s_ or {norm(r.SG_PARTIDO)}
    p["governador"] = [float(norm(pt) in gov[u]) if u in gov and isinstance(pt, str) else np.nan
                       for u, pt in zip(p["uf"], p["partido_1994"])]

    # ---- Projetos
    props = pd.read_parquet(D / "proposicoes.parquet")
    aut = pd.read_parquet(D / "proposicoes_autores.parquet")
    props = props[props["siglaTipo"].isin(["PL", "PLP", "PEC", "PDC"])]
    props["aprovado"] = props["ultimoStatus_descricaoSituacao"].fillna("").str.contains(
        "Norma Jurídica|Senado Federal|Sanção|Promulgação|Envio ao Executivo")
    aut = aut[aut["ordemAssinatura"].astype(str) == "1"].merge(props, left_on="idProposicao", right_on="id")
    aut["idDeputadoAutor"] = aut["idDeputadoAutor"].astype(int)
    p["projetos"] = p["id"].map(aut.groupby("idDeputadoAutor")["aprovado"].sum()).fillna(0).astype(int)

    # ---- Senior, Histleg, Histexec, prefeitos/vereadores de 1996
    sen = pd.read_parquet(D / "senioridade.parquet")
    p["senior"] = p["id"].map(sen.groupby("id")["idLegislatura"].nunique()).fillna(0).astype(int)
    me = pd.read_parquet(D / "deputados_mandatos_externos.parquet")
    me["ano"] = pd.to_numeric(me["anoInicio"], errors="coerce")
    antes = me[me["ano"] < 1995]
    p["histleg"] = p["id"].map(antes[antes["cargo"].isin(["Deputado(a) Estadual", "Deputado(a) Distrital",
                                                          "Vereador(a)"])].groupby("id").size()).fillna(0).astype(int)
    p["histexec"] = p["id"].map(antes[antes["cargo"].isin(["Prefeito(a)", "Vice-Prefeito(a)", "Governador(a)",
                                                           "Vice-Governador(a)"])].groupby("id").size()).fillna(0).astype(int)
    p["eleito_municipal_1996"] = p["id"].isin(
        me[(me["ano"] == 1997) & me["cargo"].isin(["Prefeito(a)", "Vice-Prefeito(a)", "Vereador(a)"])]["id"]).astype(int)

    # ---- Burocracia / Empresa (ocupação declarada ao TSE antes do mandato, 1994; senão 1998)
    oc = p["ocupacao_1994"].fillna(p["ocupacao_1998"]).fillna("").str.upper()
    prof = pd.read_parquet(D / "deputados_profissoes.parquet")
    ocup = pd.read_parquet(D / "deputados_ocupacoes.parquet")
    ocup_pub = ocup[ocup["entidade"].fillna("").str.contains(OCUPACAO_PUBLICA, case=False, regex=True)]
    p["burocracia"] = (oc.str.contains("SERVIDOR PÚBLICO|SERVIDOR PUBLICO") | p["id"].isin(ocup_pub["id"]) | p["id"].isin(
        prof.loc[prof["titulo"].str.contains("Servidor", case=False), "id"])).astype(int)
    p["empresa"] = (oc.str.contains("EMPRES") | p["id"].isin(
        prof.loc[prof["titulo"].str.contains("Empres", case=False), "id"])).astype(int)

    # ---- Coalizão (Ipea, FHC 1): partido em 1994 x partido em 1998
    gab = gabinetes()

    def base(pt, data):
        if not isinstance(pt, str):
            return None
        alvo = {norm(pt)} | {norm(x) for x in ANTECESSORES.get(norm(pt), ())}
        if norm(pt) in ("PPR", "PP"):        # PPR + PP formaram o PPB em 1995
            alvo |= {"PPB"}
        return bool(alvo & gabinete_em(gab, data)["partidos"])
    trocou = p["partido_1994"].notna() & p["partido_1998"].notna() & (
        p["partido_1994"].map(norm) != p["partido_1998"].map(norm)) & ~(
        p["partido_1994"].map(norm).isin(["PPR", "PP"]) & (p["partido_1998"].map(norm) == "PPB"))
    ob = [base(x, "1995-02-01") for x in p["partido_1994"]]
    db = [base(x, ELEICAO) for x in p["partido_1998"]]
    p["trocou_partido"] = trocou.astype(int)
    p["entrar_coalizao"] = (trocou & pd.Series([o is False and d is True for o, d in zip(ob, db)],
                                               index=p.index)).astype(int)
    p["sair_coalizao"] = (trocou & pd.Series([o is True and d is False for o, d in zip(ob, db)],
                                             index=p.index)).astype(int)

    # ---- Ideologia (Bolognesi et al., onda 2018) do partido na eleição de 1998 (ou 1994)
    ide = ideologia_1998()
    nota = p["partido_1998"].fillna(p["partido_1994"]).map(lambda s: ide.get(norm(s)) if isinstance(s, str) else None)
    p["ideologia_nota"] = pd.to_numeric(nota)
    cat = p["ideologia_nota"].map(lambda x: None if pd.isna(x) else next(n for lim, n in FAIXAS if x < lim))
    p["ideologia"] = cat
    for k in ("esquerda", "centro", "direita"):
        p[k] = np.where(cat.isna(), np.nan, (cat == k).astype(float))

    salvar(p.drop(columns=["cpf", "titulo"]), "reeleicao_painel", D)
    return p


def amostra_1998(p):
    excl = {"Distrito Federal (sem votação por município em 1998)": p["uf"] == "DF",
            "eleito prefeito, vice ou vereador em 1996": p["eleito_municipal_1996"] == 1,
            "sem candidatura a dep. federal em 1994 ligada no TSE": p["sq_1994"].isna(),
            "partido sem nota ideológica": p["ideologia"].isna()}
    fora = pd.Series(False, index=p.index)
    cont = {}
    for k, m in excl.items():
        cont[k] = int((m & ~fora).sum())
        fora |= m
    return p[~fora].copy(), cont


def amostra_2026():
    from replicar_artigo import carregar
    _, a, _ = carregar()
    a = a.rename(columns={"concentracao_2022": "concentracao_ant"})
    return a


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    coletar_camara()
    p = montar()
    a98, excl = amostra_1998(p)
    a26 = amostra_2026()
    print(f"1998: painel {len(p)} -> amostra {len(a98)}; concorreram {int(a98['concorreu_reeleicao'].sum())}, "
          f"reeleitos {int(a98['reeleito'].sum())}")
    res = {"amostra_1998": {"painel": len(p), "analise": len(a98), "exclusoes": excl,
                            "com_candidatura_1998": int((p["cargo_disputado_1998"] != "NÃO CONCORREU").sum()),
                            "concorreram": int(a98["concorreu_reeleicao"].sum()),
                            "reeleitos": int(a98["reeleito"].sum()),
                            "cargo_disputado": a98["cargo_disputado_1998"].value_counts().to_dict()},
           "artigo": ARTIGO, "modelos": {}}
    for nome, a in (("1998", a98), ("2026", a26)):
        print(f"Heckman probit reduzido {nome}...")
        m = heckprobit(a, SEL, OUT)
        pr = probit_simples(a, OUT)
        m["tabela"].to_csv(SAIDA / f"heckprobit_reduzido_{nome}.csv", index=False)
        pr["tabela"].to_csv(SAIDA / f"probit_reduzido_{nome}.csv", index=False)
        res["modelos"][nome] = {**{k: v for k, v in m.items() if k != "tabela"},
                                "coefs": m["tabela"].to_dict("records"),
                                "probit": {"n": pr["n"], "coefs": pr["tabela"].to_dict("records")}}
        print(f"  n={m['n']} sel={m['n_selecionados']} rho={m['rho']:.3f} LR={m['lr_rho0']:.2f} "
              f"p={m['p_lr_rho0']:.3f}")
    medias = teste_medias(a98, ["concentracao_ant", "concentracao_atual", "competicao_atual", "mesma_base",
                                "governador", "projetos", "senior", "histleg", "histexec", "burocracia", "empresa",
                                "entrar_coalizao", "sair_coalizao", "esquerda", "centro", "direita"])
    medias.to_csv(SAIDA / "medias_1998.csv", index=False)
    res["medias_1998"] = medias.to_dict("records")
    (SAIDA / "resultados.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    print(f"resultados em {SAIDA}/")


if __name__ == "__main__":
    main()
