"""
Complementa os dados de uma legislatura (gerados por baixar_legislatura.py) com informações
da API da Câmara necessárias para modelos de carreira/reeleição (ex.: Pereira & Rennó 2007).

Saídas (em dados/leg<N>/):
  deputados_complemento        - cpf_hash (SHA-256 do CPF; chave para ligar ao TSE), nome civil, nascimento e
                                 legislaturas anteriores em que o deputado exerceu mandato
                                 na Câmara (senioridade)
  deputados_orgaos             - participação em órgãos durante a legislatura: Mesa Diretora,
                                 comissões permanentes, especiais, CPIs... com cargo (titular,
                                 suplente, presidente, vice...) e tipo do órgão
  deputados_mandatos_externos  - mandatos fora da Câmara (vereador, prefeito, dep. estadual,
                                 governador, senador...) declarados ao TSE/Câmara
  deputados_ocupacoes          - ocupações/cargos declarados (empresário, diretor, secretário...)
  deputados_profissoes         - profissões declaradas
  lideres                      - líderes e vice-líderes de partidos, blocos e bancadas
                                 (Governo, Maioria, Minoria, Oposição) com período
  mesa                         - composição da Mesa Diretora com período
  deputados_exercicio          - períodos de cada deputado por situação (Exercício, Licença,
                                 Suplência, Convocado, Fim de mandato...), reconstruídos de
                                 deputados_historico: quem estava em exercício em cada data

Uso:
  python baixar_camara_complementar.py                       # legislaturas 55, 56 e 57
  python baixar_camara_complementar.py --legislaturas 56
  python baixar_camara_complementar.py --so-exercicio      # só deputados_exercicio (sem API)
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from baixar_legislatura import API, api_paginada, get, salvar
from baixar_tse import cpf_hash, nome_nasc_hash


def dados(endpoint, params=None):
    r = get(f"{API}/{endpoint}", params)
    return (r.json().get("dados") or []) if r is not None else []


def tipos_orgaos(ids):
    """id do órgão -> (codTipoOrgao, tipoOrgao); lista geral + consulta individual dos que faltam."""
    lista = pd.DataFrame(api_paginada("orgaos"))
    mapa = {int(o["id"]): (o.get("codTipoOrgao"), o.get("tipoOrgao"), o.get("sigla")) for _, o in lista.iterrows()}
    faltam = [i for i in ids if i not in mapa]
    with ThreadPoolExecutor(6) as ex:
        for i, d in zip(faltam, ex.map(lambda i: dados(f"orgaos/{i}"), faltam)):
            if d:
                mapa[i] = (d.get("codTipoOrgao"), d.get("tipoOrgao"), d.get("sigla"))
    return mapa


def periodos_exercicio(hist, ini, fim):
    """Converte o histórico de status em períodos [dataInicio, dataFim) por situação.
    Cada registro vale até o seguinte; registros sem situação (nome/partido no início da
    legislatura) herdam a anterior. O último período termina no fim da legislatura."""
    h = hist.copy()
    h["t"] = pd.to_datetime(h["dataHora"], errors="coerce")
    fim_ts = pd.Timestamp(fim) + pd.Timedelta(days=1)
    h = h[(h["t"] < fim_ts)].sort_values(["id", "t"])
    h["situacao"] = h.groupby("id")["situacao"].ffill()
    h["condicaoEleitoral"] = h.groupby("id")["condicaoEleitoral"].ffill()
    h["siglaPartido"] = h.groupby("id")["siglaPartido"].ffill()
    h = h.dropna(subset=["situacao"])
    h["situacao"] = h["situacao"].replace({"FIM_MANDATO": "Fim de mandato", "SUPLENCIA": "Suplência",
                                           "CONVOCADO": "Convocado", "VACANCIA": "Vacância"})
    chave = h["situacao"] + "|" + h["siglaPartido"].fillna("") + "|" + h["condicaoEleitoral"].fillna("")
    h["novo"] = chave != chave.groupby(h["id"]).shift()
    h = h[h["novo"]]
    h["dataFim"] = h.groupby("id")["t"].shift(-1).fillna(fim_ts)
    h = h.rename(columns={"t": "dataInicio"})
    h["dias"] = (h["dataFim"] - h["dataInicio"]).dt.total_seconds() / 86400
    h["em_exercicio"] = h["situacao"].eq("Exercício")
    return h[["id", "nome", "situacao", "em_exercicio", "condicaoEleitoral", "siglaPartido",
              "dataInicio", "dataFim", "dias", "descricaoStatus"]].reset_index(drop=True)


def so_exercicio(id_leg):
    saida = Path("dados") / f"leg{id_leg}"
    leg = dados(f"legislaturas/{id_leg}")
    ex = periodos_exercicio(pd.read_parquet(saida / "deputados_historico.parquet"),
                            leg["dataInicio"], leg["dataFim"])
    salvar(ex, "deputados_exercicio", saida)


def processa(id_leg):
    saida = Path("dados") / f"leg{id_leg}"
    if not (saida / "deputados.parquet").exists():
        raise SystemExit(f"Rode antes: python baixar_legislatura.py --legislatura {id_leg}")
    leg = dados(f"legislaturas/{id_leg}")
    ini, fim = leg["dataInicio"], leg["dataFim"]
    ids = pd.read_parquet(saida / "deputados.parquet")["id"].astype(int).tolist()
    print(f"Legislatura {id_leg} ({ini} a {fim}): {len(ids)} deputados")

    def por_deputado(i):
        det = dados(f"deputados/{i}")
        hist = dados(f"deputados/{i}/historico")
        org = api_paginada(f"deputados/{i}/orgaos", {"dataInicio": ini, "dataFim": fim})
        return (i, det, hist, org, dados(f"deputados/{i}/mandatosExternos"),
                dados(f"deputados/{i}/ocupacoes"), dados(f"deputados/{i}/profissoes"))

    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(por_deputado, ids))

    comp = []
    for i, det, hist, *_ in res:
        legs = sorted({h["idLegislatura"] for h in hist})
        # exerceu mandato numa legislatura anterior = tem registro de status em "Exercício"
        exerc = sorted({h["idLegislatura"] for h in hist
                        if h["idLegislatura"] < id_leg and h.get("situacao") == "Exercício"})
        comp.append({"id": i, "cpf": str(det.get("cpf") or "").zfill(11), "nomeCivil": det.get("nomeCivil"),
                     "dataNascimento": det.get("dataNascimento"),
                     "legislaturas_camara": ",".join(map(str, legs)),
                     "legislaturas_anteriores_exercicio": ",".join(map(str, exerc)),
                     "n_legislaturas_anteriores": len(exerc)})
    comp = pd.DataFrame(comp)
    comp.insert(1, "cpf_hash", cpf_hash(comp.pop("cpf")))
    comp.insert(2, "nome_nasc_hash", nome_nasc_hash(comp["nomeCivil"], comp["dataNascimento"]))
    salvar(comp, "deputados_complemento", saida)

    org = pd.DataFrame([dict(o, id=i) for i, _, _, os_, *_ in res for o in os_])
    if not org.empty:
        mapa = tipos_orgaos(sorted(org["idOrgao"].astype(int).unique()))
        org["codTipoOrgao"] = org["idOrgao"].astype(int).map(lambda x: (mapa.get(x) or (None,) * 3)[0])
        org["tipoOrgao"] = org["idOrgao"].astype(int).map(lambda x: (mapa.get(x) or (None,) * 3)[1])
        org = org[["id", "idOrgao", "siglaOrgao", "nomeOrgao", "nomePublicacao", "codTipoOrgao",
                   "tipoOrgao", "titulo", "codTitulo", "dataInicio", "dataFim"]]
    salvar(org, "deputados_orgaos", saida)

    for k, nome in [(4, "deputados_mandatos_externos"), (5, "deputados_ocupacoes"), (6, "deputados_profissoes")]:
        salvar(pd.DataFrame([dict(x, id=r[0]) for r in res for x in r[k]]), nome, saida)

    lid = pd.json_normalize(api_paginada(f"legislaturas/{id_leg}/lideres"))
    lid = lid.rename(columns=lambda c: c.replace("parlamentar.", "deputado_").replace("bancada.", "bancada_"))
    salvar(lid, "lideres", saida)

    mesa = pd.DataFrame(dados(f"legislaturas/{id_leg}/mesa", {"dataInicio": ini, "dataFim": fim}))
    salvar(mesa, "mesa", saida)
    so_exercicio(id_leg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legislaturas", type=int, nargs="*", default=[53, 54, 55, 56, 57])
    ap.add_argument("--so-exercicio", action="store_true",
                    help="gera apenas deputados_exercicio a partir de deputados_historico")
    args = ap.parse_args()
    for n in args.legislaturas:
        so_exercicio(n) if args.so_exercicio else processa(n)
    print("Concluído.")


if __name__ == "__main__":
    main()
