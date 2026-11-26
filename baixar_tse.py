"""
Baixa e organiza dados eleitorais do TSE (Repositório de Dados Eleitorais,
https://dadosabertos.tse.jus.br) necessários para replicar modelos de reeleição de
deputados federais (ex.: Pereira & Rennó 2007).

Saídas (em dados/tse/), Parquet (+ CSV ; UTF-8 gerado localmente, ignorado pelo git):
  candidatos_gerais        - todas as candidaturas das eleições gerais (presidente, governador,
                             senador, dep. federal/estadual/distrital), com cpf_hash, data de
                             nascimento, ocupação e situação final (eleito/não eleito/suplente)
  candidatos_municipais    - candidaturas a prefeito e vice-prefeito (eleições municipais)
  votacao_depfed_municipio - votos nominais de cada candidato a deputado federal por município
                             (soma das zonas)
  depfed_resumo            - uma linha por candidato a dep. federal: votação total, nº de
                             candidatos na UF, município-reduto, concentração e dominância,
                             receitas (total, FEFC, fundo partidário, próprios, pessoas
                             físicas) e despesas contratadas/pagas

Uso:
  python baixar_tse.py                             # gerais 2018 2022 2026, municipais 2020 2024
  python baixar_tse.py --gerais 2022 --municipais 2020

CPF: as tabelas trazem apenas `cpf_hash` (SHA-256 do CPF com 11 dígitos, 16 primeiros hex),
mesma chave de deputados_complemento - não publicamos CPF/título de eleitor de candidatos.
Os ZIPs brutos ficam em dados/brutos/tse/ (cache; ~3 GB para os anos padrão).
"""
import argparse
import hashlib
import re
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
CARGO_DEPFED = "6"
CARGOS_MUNICIPAIS = {"11", "12"}           # prefeito, vice-prefeito
UFS = ("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO").split()


# --------------------------------------------------------------------------- download
def baixar(sub, nome, destino: Path):
    caminho = destino / nome
    if caminho.exists() and zipfile.is_zipfile(caminho):
        return caminho
    url = f"{CDN}/{sub}/{nome}"
    tmp = caminho.with_suffix(".part")
    for tentativa in range(6):
        try:
            print(f"  baixando {nome} ...", flush=True)
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 22):
                        f.write(chunk)
            tmp.rename(caminho)
            return caminho
        except requests.RequestException as e:
            print(f"  falha ({e}); tentando de novo...", flush=True)
            time.sleep(2 ** tentativa)
    raise RuntimeError(f"Falha ao baixar {url}")


def membros_uf(z: zipfile.ZipFile, prefixo):
    """Arquivos por UF dentro do ZIP (ignora o _BRASIL.csv, que duplica tudo)."""
    pad = re.compile(rf"{re.escape(prefixo)}_([A-Z]{{2}})\.csv$")
    return [n for n in z.namelist() if (m := pad.search(n)) and m.group(1) != "BR"]


def ler(z, membro, usecols=None, filtro=None, chunksize=500_000):
    """Lê um CSV do TSE (latin1, ;) dentro do zip, opcionalmente filtrando por chunks."""
    partes = []
    with z.open(membro) as f:
        for ch in pd.read_csv(f, sep=";", encoding="latin1", dtype=str, usecols=usecols,
                              chunksize=chunksize, keep_default_na=False, na_values=[""]):
            partes.append(filtro(ch) if filtro else ch)
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=usecols)


def num(s):
    return pd.to_numeric(s.astype(str).str.replace(".", "", regex=False)
                         .str.replace(",", ".", regex=False), errors="coerce")


def cpf_hash(s):
    """Pseudonimiza o CPF (SHA-256, 16 hex) - chave para ligar TSE x Câmara sem publicar o CPF.
    Mesma função em baixar_camara_complementar.py."""
    return s.map(lambda c: hashlib.sha256(c.encode()).hexdigest()[:16]
                 if isinstance(c, str) and c.isdigit() and len(c) == 11 else pd.NA)


def limpa_nulos(df):
    return df.replace({"#NULO": pd.NA, "#NULO#": pd.NA, "#NE": pd.NA, "-1": pd.NA, "-3": pd.NA,
                       "-4": pd.NA})


# ------------------------------------------------------------------------ candidatos
COLS_CAND = ["ANO_ELEICAO", "NR_TURNO", "SG_UF", "SG_UE", "NM_UE", "CD_CARGO", "DS_CARGO",
             "SQ_CANDIDATO", "NR_CANDIDATO", "NM_CANDIDATO", "NM_URNA_CANDIDATO",
             "NR_CPF_CANDIDATO", "DT_NASCIMENTO",
             "DS_SITUACAO_CANDIDATURA", "NR_PARTIDO", "SG_PARTIDO", "SG_FEDERACAO",
             "NM_COLIGACAO", "DS_COMPOSICAO_COLIGACAO", "DS_GENERO", "DS_GRAU_INSTRUCAO",
             "DS_COR_RACA", "CD_OCUPACAO", "DS_OCUPACAO", "DS_SIT_TOT_TURNO"]


def candidatos(ano, brutos, cargos=None):
    z = zipfile.ZipFile(baixar("consulta_cand", f"consulta_cand_{ano}.zip", brutos))
    membros = membros_uf(z, f"consulta_cand_{ano}")
    cab = pd.read_csv(z.open(membros[0]), sep=";", encoding="latin1", nrows=0).columns
    cols = [c for c in COLS_CAND if c in cab]
    filtro = (lambda d: d[d["CD_CARGO"].isin(cargos)]) if cargos else None
    df = pd.concat([ler(z, m, cols, filtro) for m in membros], ignore_index=True)
    df = limpa_nulos(df)
    df["eleito"] = df["DS_SIT_TOT_TURNO"].str.startswith("ELEITO", na=False)
    df.insert(df.columns.get_loc("NR_CPF_CANDIDATO"), "cpf_hash",
              cpf_hash(df["NR_CPF_CANDIDATO"].str.zfill(11)))
    df = df.drop(columns="NR_CPF_CANDIDATO")
    # 2º turno gera nova linha para o mesmo candidato: mantém a última (resultado final)
    df = (df.sort_values(["SQ_CANDIDATO", "NR_TURNO"])
          .drop_duplicates("SQ_CANDIDATO", keep="last"))
    print(f"  candidatos {ano}: {len(df):,}")
    return df


# --------------------------------------------------------------------------- votação
def votacao_depfed(ano, brutos):
    z = zipfile.ZipFile(baixar("votacao_candidato_munzona", f"votacao_candidato_munzona_{ano}.zip",
                               brutos))
    cols = ["ANO_ELEICAO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "CD_CARGO", "SQ_CANDIDATO",
            "QT_VOTOS_NOMINAIS"]
    partes = []
    for m in membros_uf(z, f"votacao_candidato_munzona_{ano}"):
        d = ler(z, m, cols, lambda d: d[d["CD_CARGO"] == CARGO_DEPFED])
        d["QT_VOTOS_NOMINAIS"] = pd.to_numeric(d["QT_VOTOS_NOMINAIS"])
        partes.append(d.groupby(["ANO_ELEICAO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO",
                                 "SQ_CANDIDATO"], as_index=False)["QT_VOTOS_NOMINAIS"].sum())
    v = pd.concat(partes, ignore_index=True).rename(columns={"QT_VOTOS_NOMINAIS": "votos"})
    v = v[v["votos"] > 0]
    print(f"  votação dep. federal {ano}: {len(v):,} candidato x município")
    return v


def indicadores_votacao(v):
    """Por candidato: total, reduto, concentração (Pereira & Rennó), dominância (Ames), HHI."""
    tot_mun = v.groupby(["ANO_ELEICAO", "CD_MUNICIPIO"])["votos"].sum().rename("votos_mun")
    v = v.join(tot_mun, on=["ANO_ELEICAO", "CD_MUNICIPIO"])
    v["tot_cand"] = v.groupby("SQ_CANDIDATO")["votos"].transform("sum")
    v["s"] = v["votos"] / v["tot_cand"]
    red = v.sort_values("votos", ascending=False).drop_duplicates("SQ_CANDIDATO")
    r = pd.DataFrame({
        "SQ_CANDIDATO": red["SQ_CANDIDATO"],
        "votos_total": red["tot_cand"],
        "reduto_cd_municipio": red["CD_MUNICIPIO"], "reduto_nm_municipio": red["NM_MUNICIPIO"],
        "reduto_votos": red["votos"],
        # concentração = votos no município com mais votos / votos totais (Pereira & Rennó)
        "concentracao": red["votos"] / red["tot_cand"],
        # dominância no reduto = participação do candidato no total de votos de dep. federal do município
        "dominancia_reduto": red["votos"] / red["votos_mun"],
    }).set_index("SQ_CANDIDATO")
    r["n_municipios_com_voto"] = v.groupby("SQ_CANDIDATO").size()
    r["hhi_municipios"] = v.assign(s2=v["s"] ** 2).groupby("SQ_CANDIDATO")["s2"].sum()
    # dominância média de Ames: média ponderada da participação do candidato nos municípios
    v["dom"] = v["votos"] / v["votos_mun"]
    r["dominancia_media"] = (v["dom"] * v["s"]).groupby(v["SQ_CANDIDATO"]).sum()
    return r.reset_index()


# ------------------------------------------------------------------------- finanças
def categoria_receita(fonte, origem):
    """Categorias mutuamente exclusivas: fonte (FEFC / Fundo Partidário / outros) e, para
    'outros recursos', a origem (próprios, pessoas físicas, financiamento coletivo...)."""
    f, o = fonte.fillna("").str.upper(), origem.fillna("").str.upper()
    cat = pd.Series("receita_outras", index=f.index)
    outros = ~f.str.contains("FUNDO")
    cat[outros & o.str.contains("PARTIDO POL|OUTROS CANDIDATOS")] = "receita_partidos_candidatos"
    cat[outros & o.str.contains("COLETIVO|INTERNET")] = "receita_financiamento_coletivo"
    cat[outros & o.str.contains("PESSOAS F")] = "receita_pessoas_fisicas"
    cat[outros & o.str.contains("PRÓPRIOS|PROPRIOS")] = "receita_proprios"
    cat[f.str.contains("FUNDO PARTID")] = "receita_fundo_partidario"
    cat[f.str.contains("FUNDO ESPECIAL")] = "receita_fefc"
    return cat


def financas_depfed(ano, brutos):
    z = zipfile.ZipFile(baixar("prestacao_contas", f"prestacao_de_contas_eleitorais_candidatos_{ano}.zip",
                               brutos))
    so_depfed = lambda d: d[d["CD_CARGO"] == CARGO_DEPFED]
    res = []
    rec = pd.concat([ler(z, m, ["CD_CARGO", "SQ_CANDIDATO", "SQ_PRESTADOR_CONTAS", "DS_FONTE_RECEITA",
                                "DS_ORIGEM_RECEITA", "DS_NATUREZA_RECEITA", "VR_RECEITA"], so_depfed)
                     for m in membros_uf(z, f"receitas_candidatos_{ano}")], ignore_index=True)
    rec["v"] = num(rec["VR_RECEITA"])
    rec["cat"] = categoria_receita(rec["DS_FONTE_RECEITA"], rec["DS_ORIGEM_RECEITA"])
    r = pd.DataFrame({"receita_total": rec.groupby("SQ_CANDIDATO")["v"].sum()})
    r["receita_financeira"] = rec[rec["DS_NATUREZA_RECEITA"].str.upper().eq("FINANCEIRO")] \
        .groupby("SQ_CANDIDATO")["v"].sum()
    r = r.join(rec.pivot_table(index="SQ_CANDIDATO", columns="cat", values="v", aggfunc="sum"))
    res.append(r)

    con = pd.concat([ler(z, m, ["CD_CARGO", "SQ_CANDIDATO", "SQ_PRESTADOR_CONTAS", "VR_DESPESA_CONTRATADA"],
                         so_depfed) for m in membros_uf(z, f"despesas_contratadas_candidatos_{ano}")])
    con["v"] = num(con["VR_DESPESA_CONTRATADA"])
    res.append(con.groupby("SQ_CANDIDATO")["v"].sum().rename("despesas_contratadas").to_frame())

    # despesas pagas só trazem o SQ_PRESTADOR_CONTAS: mapeia prestador -> candidato
    prest = (pd.concat([rec[["SQ_PRESTADOR_CONTAS", "SQ_CANDIDATO"]], con[["SQ_PRESTADOR_CONTAS", "SQ_CANDIDATO"]]])
             .drop_duplicates("SQ_PRESTADOR_CONTAS").set_index("SQ_PRESTADOR_CONTAS")["SQ_CANDIDATO"])
    pag = pd.concat([ler(z, m, ["SQ_PRESTADOR_CONTAS", "VR_PAGTO_DESPESA"],
                         lambda d: d[d["SQ_PRESTADOR_CONTAS"].isin(prest.index)])
                     for m in membros_uf(z, f"despesas_pagas_candidatos_{ano}")])
    pag["SQ_CANDIDATO"] = pag["SQ_PRESTADOR_CONTAS"].map(prest)
    pag["v"] = num(pag["VR_PAGTO_DESPESA"])
    res.append(pag.groupby("SQ_CANDIDATO")["v"].sum().rename("despesas_pagas").to_frame())
    f = pd.concat(res, axis=1).fillna(0).reset_index().rename(columns={"index": "SQ_CANDIDATO"})
    print(f"  finanças dep. federal {ano}: {len(f):,} candidatos")
    return f


# ------------------------------------------------------------------------------ main
def salvar(df, nome, saida: Path):
    df.to_csv(saida / f"{nome}.csv", sep=";", index=False, encoding="utf-8")
    df.to_parquet(saida / f"{nome}.parquet", index=False, compression="zstd")
    print(f"  -> {nome}: {len(df):,} linhas")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gerais", type=int, nargs="*", default=[2018, 2022, 2026])
    ap.add_argument("--municipais", type=int, nargs="*", default=[2020, 2024])
    ap.add_argument("--saida", default="dados")
    args = ap.parse_args()
    saida, brutos = Path(args.saida) / "tse", Path(args.saida) / "brutos" / "tse"
    saida.mkdir(parents=True, exist_ok=True)
    brutos.mkdir(parents=True, exist_ok=True)

    print("Candidatos (eleições gerais)...")
    cg = pd.concat([candidatos(a, brutos) for a in args.gerais], ignore_index=True)
    salvar(cg, "candidatos_gerais", saida)

    print("Candidatos (eleições municipais: prefeito/vice)...")
    cm = pd.concat([candidatos(a, brutos, CARGOS_MUNICIPAIS) for a in args.municipais], ignore_index=True)
    salvar(cm, "candidatos_municipais", saida)

    print("Votação e prestação de contas (deputado federal)...")
    votos, resumo = [], []
    for ano in args.gerais:
        v = votacao_depfed(ano, brutos)
        votos.append(v)
        ind = indicadores_votacao(v)
        fin = financas_depfed(ano, brutos)
        c = cg[(cg["ANO_ELEICAO"] == str(ano)) & (cg["CD_CARGO"] == CARGO_DEPFED)]
        c = c[["ANO_ELEICAO", "SG_UF", "SQ_CANDIDATO", "NR_CANDIDATO", "NM_CANDIDATO",
               "NM_URNA_CANDIDATO", "cpf_hash", "DT_NASCIMENTO", "SG_PARTIDO",
               "DS_SITUACAO_CANDIDATURA", "DS_SIT_TOT_TURNO", "eleito", "DS_OCUPACAO"]]
        c = c.merge(ind, on="SQ_CANDIDATO", how="left").merge(fin, on="SQ_CANDIDATO", how="left")
        # competição: nº de candidatos (com votos) na UF e votação média
        aptos = c["votos_total"].fillna(0) > 0
        c["n_candidatos_uf"] = c[aptos].groupby("SG_UF")["SQ_CANDIDATO"].transform("count")
        c["n_candidatos_uf"] = c.groupby("SG_UF")["n_candidatos_uf"].transform("max")
        c["votos_total_uf"] = c.groupby("SG_UF")["votos_total"].transform("sum")
        c["share_votos_uf"] = c["votos_total"] / c["votos_total_uf"]
        resumo.append(c)
    salvar(pd.concat(votos, ignore_index=True), "votacao_depfed_municipio", saida)
    salvar(pd.concat(resumo, ignore_index=True), "depfed_resumo", saida)
    print("Concluído.")


if __name__ == "__main__":
    main()
