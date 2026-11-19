"""Cargos e trajetória dos deputados de uma legislatura (API e arquivos de Dados Abertos da Câmara).

Variáveis de Pereira & Rennó (2001) que saem daqui: Mesa, Permanente, Especial, Partpos, Senior,
Burocracia/Empresa (profissões e ocupações) e o CPF para ligar com o TSE.

Saídas em dados/leg{N}/:
  deputados_ident     - id, CPF, nome civil, data de nascimento
  deputados_profissoes, deputados_ocupacoes, deputados_mandatos_externos (Histleg/Histexec)
  cargos_mesa         - /legislaturas/{N}/mesa
  cargos_lideres      - /legislaturas/{N}/lideres (líder/vice-líder de partido, bloco, governo...)
  cargos_orgaos       - arquivo orgaosDeputados-L{N}: cargo de cada deputado em cada órgão, com tipo do órgão
  senioridade         - legislaturas anteriores (1 a N-1) em que o deputado exerceu mandato

Uso: python baixar_cargos.py [--legislatura 57]
"""
import argparse
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from baixar_legislatura import API, ARQ, api_paginada, get, id_da_uri, salvar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legislatura", type=int, default=57)
    ap.add_argument("--saida", default="dados")
    ap.add_argument("--atualizar", action="store_true", help="refaz também a etapa de deputados")
    args = ap.parse_args()
    leg = args.legislatura
    saida = Path(args.saida) / f"leg{leg}"
    ids = sorted(pd.read_parquet(saida / "deputados.parquet", columns=["id"])["id"].astype(int))
    print(f"Legislatura {leg}: {len(ids)} deputados")

    # ------------------------------------------------ identificação, profissões e ocupações
    print("Deputados: CPF, profissões, ocupações, mandatos externos...")

    if (saida / "deputados_mandatos_externos.parquet").exists() and not args.atualizar:
        print("  (já baixado; use --atualizar para refazer)")
    else:
        falhas = []

        def lista(i, recurso):
            """Sub-recurso de /deputados/{id}; alguns respondem erro 500 de forma persistente."""
            try:
                r = get(f"{API}/deputados/{i}/{recurso}", tentativas=3)
                return r.json()["dados"] if r is not None else []
            except RuntimeError:
                falhas.append((i, recurso))
                return []

        def detalhe(i):
            d = get(f"{API}/deputados/{i}").json()["dados"]
            return d, lista(i, "profissoes"), lista(i, "ocupacoes"), lista(i, "mandatosExternos")

        with ThreadPoolExecutor(6) as ex:
            res = list(ex.map(detalhe, ids))
        if falhas:
            print(f"  sub-recursos que falharam ({len(falhas)}): {falhas[:10]}")
        salvar(pd.DataFrame([{"id": d["id"], "cpf": d.get("cpf"), "nomeCivil": d.get("nomeCivil"),
                              "dataNascimento": d.get("dataNascimento"), "ufNascimento": d.get("ufNascimento")}
                             for d, *_ in res]), "deputados_ident", saida)
        salvar(pd.DataFrame([dict(p, id=d["id"]) for d, ps, _, _ in res for p in ps if p.get("titulo")]),
               "deputados_profissoes", saida)
        salvar(pd.DataFrame([dict(o, id=d["id"]) for d, _, os_, _ in res for o in os_
                             if any(v for k, v in o.items() if k != "id")]),
               "deputados_ocupacoes", saida)
        salvar(pd.DataFrame([dict(m, id=d["id"]) for d, _, _, ms in res for m in ms]),
               "deputados_mandatos_externos", saida)

    # ------------------------------------------------------------------ Mesa e lideranças
    print("Mesa e lideranças...")
    mesa = pd.DataFrame(get(f"{API}/legislaturas/{leg}/mesa").json()["dados"])
    salvar(mesa[["id", "nome", "siglaPartido", "siglaUf", "titulo", "codTitulo", "dataInicio", "dataFim"]],
           "cargos_mesa", saida)
    lid = api_paginada(f"legislaturas/{leg}/lideres")
    salvar(pd.DataFrame([{
        "id": x["parlamentar"]["id"], "nome": x["parlamentar"]["nome"],
        "siglaPartido": x["parlamentar"].get("siglaPartido"), "titulo": x["titulo"],
        "bancada_tipo": x["bancada"]["tipo"], "bancada_nome": x["bancada"]["nome"],
        "dataInicio": x.get("dataInicio"), "dataFim": x.get("dataFim"),
    } for x in lid]), "cargos_lideres", saida)

    # ---------------------------------------------------------------------- comissões
    print("Órgãos (arquivos)...")
    orgaos = pd.read_csv(io.BytesIO(get(f"{ARQ}/orgaos/csv/orgaos.csv").content), sep=";", dtype=str,
                         encoding="utf-8-sig")
    orgaos["idOrgao"] = id_da_uri(orgaos["uri"])
    membros = pd.read_csv(io.BytesIO(get(f"{ARQ}/orgaosDeputados/csv/orgaosDeputados-L{leg}.csv").content),
                          sep=";", dtype=str, encoding="utf-8-sig")
    membros["idOrgao"] = id_da_uri(membros["uriOrgao"])
    membros["id"] = id_da_uri(membros["uriDeputado"]).astype("Int64")
    membros = membros.merge(orgaos[["idOrgao", "codTipoOrgao", "tipoOrgao"]], on="idOrgao", how="left")
    salvar(membros[["id", "nomeDeputado", "siglaPartido", "idOrgao", "siglaOrgao", "nomeOrgao",
                    "codTipoOrgao", "tipoOrgao", "cargo", "dataInicio", "dataFim"]], "cargos_orgaos", saida)

    # --------------------------------------------------------------------- senioridade
    print(f"Senioridade (legislaturas 1 a {leg - 1})...")
    alvo = set(ids)

    def membros_leg(k):
        return [(k, int(d["id"])) for d in api_paginada("deputados", {"idLegislatura": k})
                if int(d["id"]) in alvo]

    with ThreadPoolExecutor(6) as ex:
        pares = [p for lst in ex.map(membros_leg, range(1, leg)) for p in lst]
    salvar(pd.DataFrame(pares, columns=["idLegislatura", "id"]).sort_values(["id", "idLegislatura"]),
           "senioridade", saida)
    print("ok")


if __name__ == "__main__":
    main()
