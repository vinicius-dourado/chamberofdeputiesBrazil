"""Baixa a votação por município/zona do TSE e grava a votação de Deputado Federal por município.

Fonte: https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_{ano}.zip

Saídas em dados/tse/:
  votos_depfed_mun_{ano}.parquet  - votos válidos por candidato a dep. federal x município (zonas somadas)
  candidatos_depfed_{ano}.parquet - 1 linha por candidato a dep. federal: partido, federação, situação, total de votos
  candidatos_{ano}.parquet        - cadastro de candidatos de todos os cargos (com CPF e situação final)
  aptos_mun_{ano}.parquet         - eleitorado apto por município
  contas_depfed_{ano}.parquet     - despesas contratadas/pagas e receitas (total e por fonte) por candidato a dep. federal

Uso:
  python baixar_tse.py               # 2026
  python baixar_tse.py --anos 2022 2026
"""
import argparse
import csv
import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_{ano}.zip"
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB",
       "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
CARGO_DEP_FEDERAL = "6"

ATRIB = ["SQ_CANDIDATO", "NR_CANDIDATO", "NM_CANDIDATO", "NM_URNA_CANDIDATO", "SG_UF",
         "SG_PARTIDO", "NR_PARTIDO", "SG_FEDERACAO", "NM_FEDERACAO", "TP_AGREMIACAO",
         "DS_SITUACAO_CANDIDATURA", "DS_DETALHE_SITUACAO_CAND", "CD_SIT_TOT_TURNO", "DS_SIT_TOT_TURNO"]


def baixar(url: str, ano: int, brutos: Path) -> Path:
    url = url.format(ano=ano)
    destino = brutos / url.rsplit("/", 1)[1]
    if destino.exists():
        return destino
    print(f"Baixando {url} ...")
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        tmp = destino.with_suffix(".part")
        with open(tmp, "wb") as f:
            for bloco in r.iter_content(1 << 20):
                f.write(bloco)
        tmp.rename(destino)
    return destino


def processar(ano: int, zip_path: Path, saida: Path, brutos: Path, cadastro: pd.DataFrame):
    votos = {}   # (sq, cd_mun) -> votos válidos
    munis = {}   # cd_mun -> (uf, nome)
    cands = {}   # sq -> atributos
    with zipfile.ZipFile(zip_path) as z:
        nomes = set(z.namelist())
        for uf in UFS:
            nome = f"votacao_candidato_munzona_{ano}_{uf}.csv"
            if nome not in nomes:
                print(f"  {uf}: arquivo ausente no zip")
                continue
            n = 0
            with z.open(nome) as bruto:
                leitor = csv.DictReader(io.TextIOWrapper(bruto, encoding="latin-1"), delimiter=";")
                for row in leitor:
                    if row["CD_CARGO"] != CARGO_DEP_FEDERAL or row["NR_TURNO"] != "1":
                        continue
                    n += 1
                    sq, mun = row["SQ_CANDIDATO"], row["CD_MUNICIPIO"]
                    votos[(sq, mun)] = votos.get((sq, mun), 0) + int(row["QT_VOTOS_NOMINAIS_VALIDOS"] or 0)
                    munis[mun] = (row["SG_UF"], row["NM_MUNICIPIO"])
                    if sq not in cands:
                        cands[sq] = {k: row[k] for k in ATRIB}
                        cands[sq]["fonte_votos"] = "votacao_candidato_munzona"
            if n == 0:
                vs = votos_secao(ano, uf, brutos)
                cad = cadastro[(cadastro["SG_UF"] == uf) & (cadastro["CD_CARGO"] == CARGO_DEP_FEDERAL)]
                cad = cad.set_index("SQ_CANDIDATO")
                for (sq, mun, nm), v in vs.items():
                    votos[(sq, mun)] = votos.get((sq, mun), 0) + v
                    munis[mun] = (uf, nm)
                    if sq not in cands and sq in cad.index:
                        cands[sq] = {k: (sq if k == "SQ_CANDIDATO" else cad.at[sq, k] if k in cad.columns else None)
                                     for k in ATRIB}
                        cands[sq]["fonte_votos"] = "votacao_secao"
                n = len(vs)
                print(f"  {uf}: sem dep. federal no munzona -> votacao_secao ({n:,} pares candidato x município)")
            else:
                print(f"  {uf}: {n:,} linhas de dep. federal")

    df = pd.DataFrame([(sq, mun, v) for (sq, mun), v in votos.items()],
                      columns=["SQ_CANDIDATO", "CD_MUNICIPIO", "votos"])
    df["SG_UF"] = df["CD_MUNICIPIO"].map(lambda m: munis[m][0])
    df["NM_MUNICIPIO"] = df["CD_MUNICIPIO"].map(lambda m: munis[m][1])
    df = df[["SQ_CANDIDATO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "votos"]]
    df = df.sort_values(["SG_UF", "SQ_CANDIDATO", "CD_MUNICIPIO"]).reset_index(drop=True)
    df.to_parquet(saida / f"votos_depfed_mun_{ano}.parquet", index=False)

    cand = pd.DataFrame(cands.values())
    cand = cand.merge(df.groupby("SQ_CANDIDATO")["votos"].sum().rename("votos_total").reset_index(),
                      on="SQ_CANDIDATO", how="left")

    cand["DS_SIT_TOT_TURNO"] = cand["DS_SIT_TOT_TURNO"].replace({"MÉDIA": "ELEITO POR MÉDIA"})
    cand["fonte_situacao"] = "tse_odsele"
    manual = Path("dados/manual") / f"tse_situacao_ap_depfed_{ano}.csv"
    if manual.exists():
        # AP 2026: arquivos odsele ainda sem totalização proporcional ('#NULO'); usa a página de resultados do TSE
        m = pd.read_csv(manual, sep=";", comment="#", dtype=str).set_index("NR_CANDIDATO")
        alvo = (cand["SG_UF"] == "AP") & cand["DS_SIT_TOT_TURNO"].isin(["#NULO", None])
        achou = alvo & cand["NR_CANDIDATO"].isin(m.index)
        cand.loc[achou, "DS_SIT_TOT_TURNO"] = cand.loc[achou, "NR_CANDIDATO"].map(m["DS_SIT_TOT_TURNO"])
        cand.loc[achou, "fonte_situacao"] = "manual:" + manual.name
        resto = alvo & ~achou
        cand.loc[resto, "DS_SIT_TOT_TURNO"] = "NÃO ELEITO"
        cand.loc[resto, "fonte_situacao"] = "inferido (fora da lista manual)"
        print(f"  AP: situação de {achou.sum()} candidatos pela lista manual, {resto.sum()} inferidos")

    cand.to_parquet(saida / f"candidatos_depfed_{ano}.parquet", index=False)
    eleitos = cand["DS_SIT_TOT_TURNO"].str.startswith("ELEITO").sum()
    print(f"{ano}: {len(cand):,} candidatos a dep. federal, {eleitos} eleitos, "
          f"{len(df):,} pares candidato x município")


URL_CAND = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{ano}.zip"
URL_SECAO = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_{ano}_{uf}.zip"
COLS_CAND = ["ANO_ELEICAO", "NR_TURNO", "SG_UF", "SG_UE", "NM_UE", "CD_CARGO", "DS_CARGO", "SQ_CANDIDATO",
             "NR_CANDIDATO", "NM_CANDIDATO", "NM_URNA_CANDIDATO", "NR_CPF_CANDIDATO",
             "NR_TITULO_ELEITORAL_CANDIDATO", "DT_NASCIMENTO", "DS_GENERO", "DS_GRAU_INSTRUCAO",
             "DS_COR_RACA", "CD_OCUPACAO", "DS_OCUPACAO", "DS_SITUACAO_CANDIDATURA", "TP_AGREMIACAO",
             "NR_PARTIDO", "SG_PARTIDO", "SG_FEDERACAO", "DS_COMPOSICAO_FEDERACAO", "SQ_COLIGACAO",
             "NM_COLIGACAO", "DS_COMPOSICAO_COLIGACAO", "CD_SIT_TOT_TURNO", "DS_SIT_TOT_TURNO"]


def processar_candidatos(ano: int, zip_path: Path, saida: Path) -> pd.DataFrame:
    """Cadastro de candidatos (todos os cargos), com CPF: base da VD 'concorreu' e da ligação com a Câmara."""
    with zipfile.ZipFile(zip_path) as z:
        nome = next(n for n in z.namelist() if n.endswith("_BRASIL.csv"))
        df = pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str)
    df = df[[c for c in COLS_CAND if c in df.columns]]
    df["DS_SIT_TOT_TURNO"] = df["DS_SIT_TOT_TURNO"].replace({"MÉDIA": "ELEITO POR MÉDIA"})  # rótulo antigo (1998)
    df.to_parquet(saida / f"candidatos_{ano}.parquet", index=False)
    print(f"{ano}: {len(df):,} registros de candidatura; "
          f"dep. federal: {df['DS_SIT_TOT_TURNO'][df['CD_CARGO'] == CARGO_DEP_FEDERAL].value_counts().to_dict()}")
    return df


def votos_secao(ano: int, uf: str, brutos: Path):
    """Alternativa para UFs sem dep. federal no arquivo munzona: soma a votação por seção."""
    url = URL_SECAO.replace("{uf}", uf)
    zp = baixar(url, ano, brutos)
    votos = {}
    with zipfile.ZipFile(zp) as z:
        nome = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(nome) as bruto:
            for row in csv.DictReader(io.TextIOWrapper(bruto, encoding="latin-1"), delimiter=";"):
                if (row["CD_CARGO"] != CARGO_DEP_FEDERAL or row["NR_TURNO"] != "1"
                        or len(row["NR_VOTAVEL"]) < 4):   # 2 dígitos = legenda; 95/96 = branco/nulo
                    continue
                k = (row["SQ_CANDIDATO"], row["CD_MUNICIPIO"], row["NM_MUNICIPIO"])
                votos[k] = votos.get(k, 0) + int(row["QT_VOTOS"] or 0)
    return votos


URL_DETALHE = "https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_{ano}.zip"
def processar_aptos(ano: int, brutos: Path, saida: Path):
    """Eleitorado apto por município (1º turno), de detalhe_votacao_munzona."""
    zp = baixar(URL_DETALHE, ano, brutos)
    with zipfile.ZipFile(zp) as z:
        csvs = [n for n in z.namelist() if n.endswith(".csv")]
        nomes = [n for n in csvs if "_BRASIL" in n] or csvs
        partes = [pd.read_csv(z.open(n), sep=";", encoding="latin-1", dtype=str,
                              usecols=["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "CD_CARGO", "QT_APTOS"])
                  for n in nomes]
    d = pd.concat(partes)
    d = d[(d["NR_TURNO"] == "1") & (d["SG_UF"].isin(UFS))]
    d["QT_APTOS"] = d["QT_APTOS"].astype(int)
    # aptos por zona são iguais entre cargos: pega o máximo por zona e soma as zonas do município
    d["CD_MUNICIPIO"] = d["CD_MUNICIPIO"].astype(int).astype(str)
    z = d.groupby(["SG_UF", "CD_MUNICIPIO", "NR_ZONA"])["QT_APTOS"].max().reset_index()
    m = z.groupby(["SG_UF", "CD_MUNICIPIO"])["QT_APTOS"].sum().reset_index()
    m["CD_MUNICIPIO"] = m["CD_MUNICIPIO"].astype(int).astype(str)  # mesmo formato de votos_depfed_mun (sem zeros)
    m.to_parquet(saida / f"aptos_mun_{ano}.parquet", index=False)
    print(f"{ano}: eleitorado apto de {len(m):,} municípios ({m['QT_APTOS'].sum():,} eleitores)")


URL_CONTAS = ("https://cdn.tse.jus.br/estatistica/sead/odsele/prestacao_contas/"
              "prestacao_de_contas_eleitorais_candidatos_{ano}.zip")


def valor(txt):
    return float((txt or "0").replace(".", "").replace(",", ".") or 0)


def somar_contas(z, nome, campo_valor, chave_extra=None, prestadores=None):
    """Soma valores por SQ_CANDIDATO (só dep. federal).

    Se `prestadores` (SQ_PRESTADOR_CONTAS -> SQ_CANDIDATO) for dado, o arquivo não tem cargo/candidato
    (caso de despesas pagas) e a ligação é feita por ele. Devolve (totais, extras, tipo, prestadores).
    """
    tot, extra, tipo, prest = {}, {}, {}, {}
    with z.open(nome) as bruto:
        for row in csv.DictReader(io.TextIOWrapper(bruto, encoding="latin-1"), delimiter=";"):
            if prestadores is None:
                if row["CD_CARGO"] != CARGO_DEP_FEDERAL:
                    continue
                sq = row["SQ_CANDIDATO"]
                prest[row["SQ_PRESTADOR_CONTAS"]] = sq
            else:
                sq = prestadores.get(row["SQ_PRESTADOR_CONTAS"])
                if sq is None:
                    continue
            v = valor(row[campo_valor])
            tot[sq] = tot.get(sq, 0.0) + v
            tipo[sq] = row["TP_PRESTACAO_CONTAS"].upper()
            if chave_extra:
                k = (sq, chave_extra(row))
                extra[k] = extra.get(k, 0.0) + v
    return tot, extra, tipo, prest


def processar_contas(ano: int, zip_path: Path, saida: Path):
    """Totais de despesas e receitas por candidato a dep. federal."""
    with zipfile.ZipFile(zip_path) as z:
        print("  despesas contratadas...")
        contratadas, _, tipo, prest = somar_contas(
            z, f"despesas_contratadas_candidatos_{ano}_BRASIL.csv", "VR_DESPESA_CONTRATADA")
        print("  receitas...")
        receitas, por_fonte, tipo_r, prest_r = somar_contas(
            z, f"receitas_candidatos_{ano}_BRASIL.csv", "VR_RECEITA",
            chave_extra=lambda r: r["DS_FONTE_RECEITA"].upper())
        print("  despesas pagas...")
        pagas, _, _, _ = somar_contas(z, f"despesas_pagas_candidatos_{ano}_BRASIL.csv",
                                      "VR_PAGTO_DESPESA", prestadores={**prest_r, **prest})
    sqs = sorted(set(contratadas) | set(pagas) | set(receitas))
    df = pd.DataFrame({
        "SQ_CANDIDATO": sqs,
        "tipo_prestacao": [tipo.get(s) or tipo_r.get(s) for s in sqs],
        "despesas_contratadas": [contratadas.get(s, 0.0) for s in sqs],
        "despesas_pagas": [pagas.get(s, 0.0) for s in sqs],
        "receitas_total": [receitas.get(s, 0.0) for s in sqs],
    })
    fontes = sorted({f for _, f in por_fonte})
    for f in fontes:
        col = "receitas_" + f.lower().replace(" ", "_")
        df[col] = [por_fonte.get((s, f), 0.0) for s in sqs]
    df.to_parquet(saida / f"contas_depfed_{ano}.parquet", index=False)
    print(f"{ano}: contas de {len(df):,} candidatos a dep. federal "
          f"({(df['tipo_prestacao'] == 'FINAL').sum():,} com prestação final); fontes: {fontes}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anos", type=int, nargs="+", default=[2022, 2026])
    ap.add_argument("--saida", default="dados")
    ap.add_argument("--sem-votos", action="store_true", help="não processa a votação")
    ap.add_argument("--sem-contas", action="store_true", help="não processa a prestação de contas")
    args = ap.parse_args()
    brutos = Path(args.saida) / "brutos" / "tse"
    saida = Path(args.saida) / "tse"
    brutos.mkdir(parents=True, exist_ok=True)
    saida.mkdir(parents=True, exist_ok=True)
    for ano in args.anos:
        cadastro = processar_candidatos(ano, baixar(URL_CAND, ano, brutos), saida)
        if not args.sem_votos:
            processar(ano, baixar(URL, ano, brutos), saida, brutos, cadastro)
        try:
            processar_aptos(ano, brutos, saida)
        except requests.HTTPError as e:
            print(f"{ano}: sem detalhe_votacao_munzona ({e})")
        if not args.sem_contas:
            processar_contas(ano, baixar(URL_CONTAS, ano, brutos), saida)


if __name__ == "__main__":
    main()
