"""
Baixa e organiza os dados da legislatura atual da Câmara dos Deputados
(Dados Abertos: https://dadosabertos.camara.leg.br).

Saídas (em dados/leg<N>/), em CSV (; e UTF-8) e Parquet:
  deputados                  - deputados que exerceram mandato na legislatura (+ detalhes)
  deputados_partidos         - histórico de filiação/partido de cada deputado na legislatura
  partidos                   - partidos com representação na legislatura (+ líder)
  proposicoes                - proposições de autoria de deputados da legislatura
  proposicoes_autores        - (proposição, deputado autor, ordem de assinatura, proponente)
  proposicoes_temas          - temas de cada proposição
  deputados_temas            - nº de proposições por deputado x tema (resumo)
  frentes                    - frentes parlamentares da legislatura
  frentes_deputados          - membros das frentes (deputado, cargo na frente)
  votacoes                   - votações (data, órgão, descrição, resultado, proposição)
  votacoes_orientacoes       - orientações das lideranças (partidos, blocos, Governo...)
  votos                      - voto de cada deputado em cada votação, com a proposição,
                               a orientação do partido/bloco do deputado e a do Governo

Uso:
  python baixar_legislatura.py               # legislatura atual
  python baixar_legislatura.py --legislatura 56
"""
import argparse
import io
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

API = "https://dadosabertos.camara.leg.br/api/v2"
ARQ = "https://dadosabertos.camara.leg.br/arquivos"

SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json", "User-Agent": "dados-camara-script"})


# --------------------------------------------------------------------------- HTTP
def get(url, params=None, tentativas=6, stream=False):
    for i in range(tentativas):
        try:
            r = SESSION.get(url, params=params, timeout=120, stream=stream)
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                return None
        except requests.RequestException:
            pass
        time.sleep(2 ** i)
    raise RuntimeError(f"Falha ao acessar {url} {params or ''}")


def api_paginada(endpoint, params=None):
    params = dict(params or {}, itens=100, pagina=1)
    dados = []
    while True:
        js = get(f"{API}/{endpoint}", params).json()
        dados.extend(js["dados"])
        if not any(l["rel"] == "next" for l in js.get("links", [])):
            return dados
        params["pagina"] += 1


def baixar_arquivo(nome, ano, destino: Path):
    """Baixa arquivo em massa (CSV) com cache local."""
    arq = f"{nome}-{ano}.csv" if ano else f"{nome}.csv"
    caminho = destino / arq
    if not caminho.exists():
        print(f"  baixando {arq} ...", flush=True)
        r = get(f"{ARQ}/{nome}/csv/{arq}", stream=True)
        if r is None:
            print(f"  (não disponível: {arq})")
            return None
        tmp = caminho.with_suffix(".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
        tmp.rename(caminho)
    return caminho


def ler_csv(caminho):
    return pd.read_csv(caminho, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False,
                       na_values=[""])


def ler_anos(nome, anos, destino):
    partes = [ler_csv(p) for a in anos if (p := baixar_arquivo(nome, a, destino))]
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


def id_da_uri(serie):
    return serie.str.extract(r"/(\d+)$")[0]


def salvar(df, nome, saida: Path, compressao="snappy"):
    df.to_csv(saida / f"{nome}.csv", sep=";", index=False, encoding="utf-8")
    df.to_parquet(saida / f"{nome}.parquet", index=False, compression=compressao)
    print(f"  -> {nome}: {len(df):,} linhas")


# --------------------------------------------------------------- orientação x partido
def norm(txt):
    s = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode().upper().strip()
    return {"GOV.": "GOVERNO"}.get(s, s)  # 2019-2022: a bancada do Governo vem como "GOV."


# nomes de bancada abreviados/truncados -> sigla normalizada
ALIAS = {"PODEMOS": "PODE", "SOLIDARIED": "SOLIDARIEDADE", "REPUBLICAN": "REPUBLICANOS",
         "CIDADAN": "CIDADANIA", "MISSAO": "MISSAO"}
# abreviações usadas nos nomes de blocos ("Bl UniPpFdrPsdbCid...")
ABREV_BLOCO = {"UNI": ["UNIAO"], "PP": ["PP"], "PSDB": ["PSDB"], "CID": ["CIDADANIA"],
               "PT": ["PT", "PCDOB", "PV"], "PSOL": ["PSOL"], "REDE": ["REDE"], "MDB": ["MDB"],
               "PSD": ["PSD"], "REP": ["REPUBLICANOS"], "PODE": ["PODE"], "PSC": ["PSC"],
               "AVAN": ["AVANTE"], "SOLID": ["SOLIDARIEDADE"], "PRD": ["PRD"], "PL": ["PL"],
               "PSB": ["PSB"], "PDT": ["PDT"], "NOVO": ["NOVO"], "PATRI": ["PATRIOTA"],
               "PTB": ["PTB"], "PROS": ["PROS"], "FDR": []}
BANCADAS_ESPECIAIS = {"GOVERNO", "MAIORIA", "MINORIA", "OPOSICAO"}


def sigla_partido(s):
    s = norm(s)
    return ALIAS.get(s, s)


def partidos_da_bancada(sigla):
    """-> (tipo, conjunto de partidos, truncado?)"""
    s = norm(sigla)
    if s in BANCADAS_ESPECIAIS:
        return "especial", set(), False
    truncado = s.endswith("...") or s == "BLOCO PARLAMENTAR"
    if s.startswith("BL"):
        corpo = re.sub(r"^(BLOCO PARLAMENTAR|BL)\s*", "", s).rstrip(". ")
        if "," in corpo or " " in corpo:          # nome por extenso: "UNIÃO, PP, PSD..."
            partes = re.split(r"[,\s]+", corpo.replace("FEDERACAO", ""))
            return "bloco", {sigla_partido(p) for p in partes if p}, truncado
        toks, chaves = set(), sorted(ABREV_BLOCO, key=len, reverse=True)
        while corpo:
            k = next((k for k in chaves if corpo.startswith(k)), None)
            if k is None:                         # abreviação desconhecida
                truncado = True
                break
            toks.update(ABREV_BLOCO[k])
            corpo = corpo[len(k):]
        return "bloco", toks, truncado
    if s.startswith(("FDR", "FED")):
        partes = re.split(r"[\s\-/]+", re.sub(r"^(FDR|FEDERACAO|FED)\s*", "", s))
        return "federacao", {sigla_partido(p) for p in partes if p}, False
    return "partido", {sigla_partido(s)}, False


def mapear_orientacoes(orient, votos, blocos_completos=()):
    """Para cada (votação, partido do deputado) encontra a orientação aplicável.
    Prioridade: o próprio partido > federação que o contém > bloco que o contém.
    Nomes de blocos vêm truncados ("Bl UniPpFdrPsdbCid..."); nesse caso, os partidos
    que votaram e não tiveram orientação própria nem estão em outra bancada da votação
    são atribuídos ao bloco truncado (fonte = 'bloco (inferido)'), desde que só exista
    um bloco truncado na votação."""
    prioridade = {"partido": 0, "federacao": 1, "bloco": 2}
    partidos_por_vot = (votos.assign(p=votos["deputado_siglaPartido"].map(sigla_partido))
                        .groupby("idVotacao")["p"].agg(set).to_dict())
    linhas = []
    for idv, g in orient.groupby("idVotacao"):
        cobertos, truncados = set(), []
        for sigla, orientacao in zip(g["siglaBancada"], g["orientacao"]):
            tipo, toks, trunc = partidos_da_bancada(sigla)
            if tipo == "especial":
                continue
            if trunc and frozenset(toks) in blocos_completos:
                trunc = False
            cobertos |= toks
            for t in toks:
                linhas.append((idv, t, orientacao, sigla, tipo, prioridade[tipo]))
            if trunc:
                truncados.append((sigla, orientacao))
        if len(truncados) == 1:
            sigla, orientacao = truncados[0]
            for t in partidos_por_vot.get(idv, set()) - cobertos - {"S.PART."}:
                linhas.append((idv, t, orientacao, sigla, "bloco (inferido)", 3))
    m = pd.DataFrame(linhas, columns=["idVotacao", "partido_norm", "orientacao_partido",
                                      "orientacao_bancada", "orientacao_fonte", "_p"])
    m = m.sort_values("_p").drop_duplicates(["idVotacao", "partido_norm"]).drop(columns="_p")
    v = votos.assign(partido_norm=votos["deputado_siglaPartido"].map(sigla_partido))
    v = v.merge(m, on=["idVotacao", "partido_norm"], how="left").drop(columns="partido_norm")

    esp = orient.assign(b=orient["siglaBancada"].map(norm))
    esp = esp[esp["b"].isin(BANCADAS_ESPECIAIS)]
    esp = esp.pivot_table(index="idVotacao", columns="b", values="orientacao", aggfunc="first")
    esp.columns = [f"orientacao_{c.lower()}" for c in esp.columns]
    for c in ["orientacao_governo", "orientacao_maioria", "orientacao_minoria", "orientacao_oposicao"]:
        if c not in esp:
            esp[c] = pd.NA
    return v.merge(esp.reset_index(), on="idVotacao", how="left")


def seguiu(voto, orientacao):
    if pd.isna(orientacao) or orientacao in ("Liberado", "Liberado ") or pd.isna(voto):
        return pd.NA
    if orientacao not in ("Sim", "Não", "Obstrução", "Abstenção"):
        return pd.NA
    return voto == orientacao


# ------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legislatura", type=int, help="padrão: a atual")
    ap.add_argument("--saida", default="dados")
    args = ap.parse_args()

    if args.legislatura:
        leg = get(f"{API}/legislaturas/{args.legislatura}").json()["dados"]
    else:
        leg = get(f"{API}/legislaturas", {"ordem": "DESC", "ordenarPor": "id", "itens": 1}).json()["dados"][0]
    id_leg, ini, fim = leg["id"], leg["dataInicio"], leg["dataFim"]
    anos = list(range(int(ini[:4]), min(int(fim[:4]), pd.Timestamp.today().year) + 1))
    print(f"Legislatura {id_leg}: {ini} a {fim} (anos {anos})")

    saida = Path(args.saida) / f"leg{id_leg}"
    brutos = Path(args.saida) / "brutos"
    saida.mkdir(parents=True, exist_ok=True)
    brutos.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- deputados
    print("Deputados (API)...")
    lista = pd.DataFrame(api_paginada("deputados", {"idLegislatura": id_leg, "ordem": "ASC",
                                                     "ordenarPor": "nome"}))
    ids = sorted(lista["id"].unique())

    def detalhe(i):
        d = get(f"{API}/deputados/{i}").json()["dados"]
        st = d.pop("ultimoStatus", {}) or {}
        gab = st.pop("gabinete", {}) or {}
        hist = get(f"{API}/deputados/{i}/historico").json()["dados"]
        return d, st, gab, hist

    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(detalhe, ids))
    deputados = pd.DataFrame([{
        "id": d["id"], "nome": st.get("nome"), "nomeCivil": d.get("nomeCivil"),
        "siglaPartido": st.get("siglaPartido"), "siglaUf": st.get("siglaUf"),
        "situacao": st.get("situacao"), "condicaoEleitoral": st.get("condicaoEleitoral"),
        "sexo": d.get("sexo"), "dataNascimento": d.get("dataNascimento"),
        "ufNascimento": d.get("ufNascimento"), "municipioNascimento": d.get("municipioNascimento"),
        "escolaridade": d.get("escolaridade"), "email": st.get("email"),
        "urlFoto": st.get("urlFoto"), "redeSocial": ", ".join(d.get("redeSocial") or []),
        "gabinete_predio": gab.get("predio"), "gabinete_sala": gab.get("sala"),
        "gabinete_telefone": gab.get("telefone"),
    } for d, st, gab, _ in res])
    salvar(deputados, "deputados", saida)

    hist = pd.DataFrame([dict(h, id=d["id"]) for d, _, _, hs in res for h in hs])
    hist = hist[hist["idLegislatura"] == id_leg].sort_values(["id", "dataHora"])
    hist = hist[["id", "nome", "dataHora", "siglaPartido", "siglaUf", "situacao",
                 "condicaoEleitoral", "descricaoStatus"]]
    salvar(hist, "deputados_historico", saida)
    # períodos de filiação partidária dentro da legislatura
    h = hist.dropna(subset=["siglaPartido"]).copy()
    h["mudou"] = h["siglaPartido"] != h.groupby("id")["siglaPartido"].shift()
    h["bloco"] = h.groupby("id")["mudou"].cumsum()
    filia = (h.groupby(["id", "bloco"])
             .agg(nome=("nome", "last"), siglaPartido=("siglaPartido", "first"),
                  dataInicio=("dataHora", "first"))
             .reset_index().drop(columns="bloco"))
    filia["dataFim"] = filia.groupby("id")["dataInicio"].shift(-1)
    salvar(filia, "deputados_partidos", saida)

    # ----------------------------------------------------------------- partidos
    print("Partidos (API)...")
    partidos = api_paginada("partidos", {"idLegislatura": id_leg, "ordem": "ASC", "ordenarPor": "sigla"})
    with ThreadPoolExecutor(6) as ex:
        det = list(ex.map(lambda p: get(f"{API}/partidos/{p['id']}").json()["dados"], partidos))
    salvar(pd.DataFrame([{
        "id": p["id"], "sigla": p["sigla"], "nome": p["nome"],
        "situacao": (p.get("status") or {}).get("situacao"),
        "totalMembros": (p.get("status") or {}).get("totalMembros"),
        "lider_id": id_da_uri(pd.Series([((p.get("status") or {}).get("lider") or {}).get("uri") or ""]))[0],
        "lider_nome": ((p.get("status") or {}).get("lider") or {}).get("nome"),
        "lider_uf": ((p.get("status") or {}).get("lider") or {}).get("uf"),
        "numeroEleitoral": p.get("numeroEleitoral"),
    } for p in det]), "partidos", saida)

    ids_dep = set(map(str, ids))

    # --------------------------------------------------------------- proposições
    print("Proposições (arquivos)...")
    autores = ler_anos("proposicoesAutores", anos, brutos)
    autores = autores[autores["idDeputadoAutor"].isin(ids_dep)]
    props = ler_anos("proposicoes", anos, brutos)
    props = props[props["id"].isin(autores["idProposicao"])
                  & (props["dataApresentacao"].str[:10] >= ini)
                  & (props["dataApresentacao"].str[:10] <= fim)]
    autores = autores[autores["idProposicao"].isin(props["id"])]
    salvar(props[["id", "siglaTipo", "numero", "ano", "descricaoTipo", "ementa", "ementaDetalhada",
                  "keywords", "dataApresentacao", "ultimoStatus_descricaoSituacao",
                  "ultimoStatus_dataHora", "ultimoStatus_siglaOrgao", "urlInteiroTeor"]],
           "proposicoes", saida)
    salvar(autores[["idProposicao", "idDeputadoAutor", "nomeAutor", "siglaPartidoAutor",
                    "siglaUFAutor", "ordemAssinatura", "proponente"]], "proposicoes_autores", saida)

    temas = ler_anos("proposicoesTemas", anos, brutos)
    temas["idProposicao"] = id_da_uri(temas["uriProposicao"])
    temas = temas[temas["idProposicao"].isin(props["id"])]
    temas = temas[["idProposicao", "siglaTipo", "numero", "ano", "codTema", "tema", "relevancia"]]
    salvar(temas, "proposicoes_temas", saida)

    dt = autores.merge(temas[["idProposicao", "codTema", "tema"]], on="idProposicao")
    dt = (dt.groupby(["idDeputadoAutor", "nomeAutor", "codTema", "tema"])
          .agg(n_proposicoes=("idProposicao", "nunique"),
               n_como_primeiro_autor=("ordemAssinatura", lambda s: (s == "1").sum()))
          .reset_index().sort_values(["idDeputadoAutor", "n_proposicoes"], ascending=[True, False]))
    salvar(dt, "deputados_temas", saida)

    # ------------------------------------------------------------------- frentes
    print("Frentes parlamentares (arquivos)...")
    frentes = ler_csv(baixar_arquivo("frentes", None, brutos))
    frentes = frentes[frentes["idLegislatura"] == str(id_leg)]
    salvar(frentes[["id", "titulo", "dataCriacao", "idLegislatura", "situacao", "keywords",
                    "telefone", "email", "urlWebsite", "coordenador_id", "coordenador_nome",
                    "coordenador_siglaPartido", "coordenador_siglaUf"]], "frentes", saida)
    fd = ler_csv(baixar_arquivo("frentesDeputados", None, brutos))
    fd = fd[fd["id"].isin(frentes["id"])]
    fd = fd.rename(columns=lambda c: c.replace("deputado_.", "deputado_"))
    fd = fd.rename(columns={"id": "idFrente", "titulo": "tituloFrente", "deputado_titulo": "cargo"})
    salvar(fd[["idFrente", "tituloFrente", "deputado_id", "deputado_nome", "deputado_siglaUf",
               "cargo", "dataInicio", "dataFim"]], "frentes_deputados", saida)

    # ------------------------------------------------------------------ votações
    print("Votações (arquivos)...")
    vot = ler_anos("votacoes", anos, brutos)
    vot = vot[(vot["data"] >= ini) & (vot["data"] <= fim)]
    vprop = ler_anos("votacoesProposicoes", anos, brutos)
    vobj = ler_anos("votacoesObjetos", anos, brutos)
    orient = ler_anos("votacoesOrientacoes", anos, brutos)
    votos = ler_anos("votacoesVotos", anos, brutos)
    votos = votos[votos["idVotacao"].isin(vot["id"])]
    orient = orient[orient["idVotacao"].isin(vot["id"])]

    # proposição associada a cada votação: objeto da votação (o que foi votado: projeto,
    # requerimento, emenda...) e a(s) proposição(ões) afetada(s)
    def agrega(df, pref):
        df = df.drop_duplicates(["idVotacao", "proposicao_id"])
        return (df.groupby("idVotacao")
                .agg(**{f"{pref}_id": ("proposicao_id", lambda s: ", ".join(s.dropna())),
                        f"{pref}_titulo": ("proposicao_titulo", lambda s: ", ".join(s.dropna())),
                        f"{pref}_ementa": ("proposicao_ementa", lambda s: " || ".join(s.dropna()))})
                .reset_index())

    vot = (vot[["id", "data", "dataHoraRegistro", "siglaOrgao", "idEvento", "aprovacao", "votosSim",
                "votosNao", "votosOutros", "descricao", "ultimaApresentacaoProposicao_descricao"]]
           .rename(columns={"id": "idVotacao"})
           .merge(agrega(vobj, "objeto"), on="idVotacao", how="left")
           .merge(agrega(vprop, "proposicao"), on="idVotacao", how="left"))
    vot["tem_votos_nominais"] = vot["idVotacao"].isin(votos["idVotacao"])
    vot["tem_orientacao"] = vot["idVotacao"].isin(orient["idVotacao"])
    salvar(vot, "votacoes", saida)
    salvar(orient[["idVotacao", "siglaOrgao", "siglaBancada", "orientacao"]], "votacoes_orientacoes", saida)

    v = votos[["idVotacao", "dataHoraVoto", "deputado_id", "deputado_nome", "deputado_siglaPartido",
               "deputado_siglaUf", "voto"]]
    blocos = api_paginada("blocos", {"idLegislatura": id_leg})
    blocos_completos = {frozenset(sigla_partido(p) for p in re.split(r",\s*", b["nome"].replace("Federação ", "")))
                        for b in blocos}
    v = mapear_orientacoes(orient, v, blocos_completos)
    v = v.merge(vot[["idVotacao", "data", "siglaOrgao", "descricao", "aprovacao",
                     "objeto_titulo", "proposicao_id", "proposicao_titulo", "proposicao_ementa"]],
                on="idVotacao", how="left")
    v["seguiu_orientacao_partido"] = [seguiu(a, b) for a, b in zip(v["voto"], v["orientacao_partido"])]
    v["seguiu_orientacao_governo"] = [seguiu(a, b) for a, b in zip(v["voto"], v["orientacao_governo"])]
    # textos longos (descrição da votação, ementas) ficam em `votacoes` (join por idVotacao)
    cols = ["idVotacao", "data", "siglaOrgao", "aprovacao",
            "proposicao_id", "proposicao_titulo",
            "deputado_id", "deputado_nome", "deputado_siglaPartido", "deputado_siglaUf",
            "dataHoraVoto", "voto", "orientacao_bancada", "orientacao_fonte", "orientacao_partido",
            "seguiu_orientacao_partido", "orientacao_governo", "seguiu_orientacao_governo",
            "orientacao_maioria", "orientacao_minoria", "orientacao_oposicao"]
    salvar(v[cols].sort_values(["data", "idVotacao", "deputado_nome"]), "votos", saida)
    print("Concluído.")


if __name__ == "__main__":
    main()
