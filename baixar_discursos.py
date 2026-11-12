"""
Baixa todos os discursos (com transcrição) dos deputados da legislatura
via API de Dados Abertos da Câmara: /deputados/{id}/discursos?idLegislatura=N

Saída: dados/leg<N>/discursos.parquet (+ .csv)
  id_discurso, deputado_id, deputado_nome, deputado_siglaPartido, deputado_siglaUf,
  dataHoraInicio, tipoDiscurso, faseEvento_titulo, keywords, sumario, transcricao, urlTexto

As respostas brutas ficam em dados/brutos/discursos_leg<N>/<id>.json (cache): se a
execução for interrompida, rodar de novo continua de onde parou. Use --atualizar
para baixar tudo de novo.

Uso:
  python baixar_discursos.py                  # legislatura atual
  python baixar_discursos.py --legislatura 56
"""
import argparse
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from baixar_legislatura import API, api_paginada, get, salvar


def limpar(txt):
    if not isinstance(txt, str):
        return txt
    txt = html.unescape(txt).replace("\xa0", " ")
    return re.sub(r"<[^>]+>", "", txt).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legislatura", type=int, help="padrão: a atual")
    ap.add_argument("--saida", default="dados")
    ap.add_argument("--atualizar", action="store_true", help="ignora o cache e baixa de novo")
    ap.add_argument("--threads", type=int, default=6)
    args = ap.parse_args()

    if args.legislatura:
        id_leg = args.legislatura
    else:
        id_leg = get(f"{API}/legislaturas", {"ordem": "DESC", "ordenarPor": "id", "itens": 1}).json()["dados"][0]["id"]
    saida = Path(args.saida) / f"leg{id_leg}"
    cache = Path(args.saida) / "brutos" / f"discursos_leg{id_leg}"
    saida.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)

    deputados = pd.DataFrame(api_paginada("deputados", {"idLegislatura": id_leg, "ordem": "ASC",
                                                         "ordenarPor": "nome"}))
    deputados = deputados.drop_duplicates("id")
    print(f"Legislatura {id_leg}: {len(deputados)} deputados")

    def baixar(dep_id):
        arq = cache / f"{dep_id}.json"
        if arq.exists() and not args.atualizar:
            return
        dados = api_paginada(f"deputados/{dep_id}/discursos",
                             {"idLegislatura": id_leg, "ordenarPor": "dataHoraInicio", "ordem": "ASC"})
        tmp = arq.with_suffix(".part")
        tmp.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        tmp.rename(arq)

    with ThreadPoolExecutor(args.threads) as ex:
        futs = {ex.submit(baixar, i): i for i in deputados["id"]}
        for n, f in enumerate(as_completed(futs), 1):
            f.result()
            if n % 50 == 0 or n == len(futs):
                print(f"  {n}/{len(futs)} deputados", flush=True)

    linhas = []
    for dep in deputados.itertuples():
        for d in json.loads((cache / f"{dep.id}.json").read_text(encoding="utf-8")):
            fase = d.get("faseEvento") or {}
            linhas.append({
                "deputado_id": dep.id, "deputado_nome": dep.nome,
                "dataHoraInicio": d.get("dataHoraInicio"),
                "tipoDiscurso": d.get("tipoDiscurso"), "faseEvento_titulo": fase.get("titulo"),
                "keywords": limpar(d.get("keywords")), "sumario": limpar(d.get("sumario")),
                "transcricao": limpar(d.get("transcricao")),
                "urlTexto": d.get("urlTexto"),
            })
    disc = pd.DataFrame(linhas)

    # partido/UF do deputado na data do discurso (a partir de deputados_partidos, se existir)
    filia_arq = saida / "deputados_partidos.parquet"
    disc["deputado_siglaUf"] = disc["deputado_id"].map(deputados.set_index("id")["siglaUf"])
    disc["deputado_siglaPartido"] = pd.NA
    if filia_arq.exists():
        f = pd.read_parquet(filia_arq)
        f = f.assign(dataInicio=pd.to_datetime(f["dataInicio"], errors="coerce")).dropna(subset=["dataInicio"])
        f = f.sort_values("dataInicio")
        d = disc.reset_index().assign(_dt=pd.to_datetime(disc["dataHoraInicio"], errors="coerce"))
        d = d.dropna(subset=["_dt"]).sort_values("_dt")
        d = pd.merge_asof(d, f[["id", "dataInicio", "siglaPartido"]].rename(columns={"id": "deputado_id"}),
                          left_on="_dt", right_on="dataInicio", by="deputado_id",
                          direction="backward")
        d = d.set_index("index").reindex(disc.index)
        # discursos anteriores ao 1º registro do histórico: usa o 1º partido
        primeiro = f.groupby("id")["siglaPartido"].first()
        disc["deputado_siglaPartido"] = d["siglaPartido"].fillna(disc["deputado_id"].map(primeiro))
    else:
        disc["deputado_siglaPartido"] = disc["deputado_id"].map(deputados.set_index("id")["siglaPartido"])

    disc = disc.sort_values(["dataHoraInicio", "deputado_nome"]).reset_index(drop=True)
    disc.insert(0, "id_discurso", range(1, len(disc) + 1))
    cols = ["id_discurso", "deputado_id", "deputado_nome", "deputado_siglaPartido", "deputado_siglaUf",
            "dataHoraInicio", "tipoDiscurso", "faseEvento_titulo", "keywords", "sumario",
            "transcricao", "urlTexto"]
    # dataHoraFim, uriEvento, urlAudio e urlVideo vêm sempre vazios na API; descartados
    salvar(disc[cols], "discursos", saida, compressao="zstd")
    print("Concluído.")


if __name__ == "__main__":
    main()
