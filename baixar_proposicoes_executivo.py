"""
Proposições de autoria do Poder Executivo na Câmara (PL, PLP, PEC, MPV, PLN, MSC...) com
autoria, tramitação completa e proposições relacionadas - base para o "funil" da agenda do
Executivo (apresentação -> tramitação -> aprovação).

Fonte: arquivos em massa da Câmara (proposicoes-AAAA, proposicoesAutores-AAAA) + API
/proposicoes/{id}/tramitacoes e /relacionadas. Os arquivos em massa proposicoesTramitacoes-AAAA
são incompletos (ex.: PEC 6/2019 tem 13 registros no arquivo e 791 na API), por isso as
tramitações vêm da API, só para os tipos do funil legislativo (TIPOS_FUNIL).

Saídas (em dados/executivo/):
  proposicoes_executivo    - proposições com ao menos um autor do tipo "Órgão do Poder
                             Executivo" (Poder Executivo, Presidência, ministérios...),
                             com o presidente da República na data de apresentação
  autores_executivo        - autoria dessas proposições
  tramitacoes_executivo    - tramitação completa (API) das proposições dos TIPOS_FUNIL
                             (data, órgão, regime, descrição, situação, despacho)
  relacionadas_executivo   - proposições relacionadas/apensadas (API)

Uso:
  python baixar_proposicoes_executivo.py                    # 2007 até o ano atual
  python baixar_proposicoes_executivo.py --anos 2019 2020
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from baixar_legislatura import API, get, id_da_uri, ler_anos, salvar

PRESIDENTES = [  # (início do mandato, presidente)
    ("2003-01-01", "Lula 1-2"), ("2011-01-01", "Dilma 1"), ("2015-01-01", "Dilma 2"),
    ("2016-05-12", "Temer"), ("2019-01-01", "Bolsonaro"), ("2023-01-01", "Lula 3"),
]
TIPOS_FUNIL = {"PL", "PLP", "PEC", "MPV", "PLN", "PDL", "PLV"}


def presidente(datas):
    ini = pd.to_datetime([d for d, _ in PRESIDENTES])
    d = pd.to_datetime(datas.str[:10], errors="coerce")
    idx = ini.searchsorted(d, side="right") - 1
    return pd.Series([PRESIDENTES[i][1] if i >= 0 and pd.notna(x) else None for i, x in zip(idx, d)],
                     index=datas.index)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anos", type=int, nargs="*",
                    default=list(range(2007, pd.Timestamp.today().year + 1)))
    ap.add_argument("--saida", default="dados")
    args = ap.parse_args()
    brutos, saida = Path(args.saida) / "brutos", Path(args.saida) / "executivo"
    brutos.mkdir(parents=True, exist_ok=True)
    saida.mkdir(parents=True, exist_ok=True)

    print("Autores e proposições (arquivos)...")
    aut = ler_anos("proposicoesAutores", args.anos, brutos)
    ids = set(aut.loc[aut["tipoAutor"] == "Órgão do Poder Executivo", "idProposicao"])
    aut = aut[aut["idProposicao"].isin(ids)]
    props = ler_anos("proposicoes", args.anos, brutos)
    props = props[props["id"].isin(ids)].drop_duplicates("id")
    props["presidente"] = presidente(props["dataApresentacao"])
    props["idRelator_ultimo"] = id_da_uri(props["ultimoStatus_uriRelator"].fillna(""))
    props["idPropPrincipal"] = id_da_uri(props["uriPropPrincipal"].fillna(""))
    salvar(props[["id", "siglaTipo", "numero", "ano", "descricaoTipo", "ementa", "keywords",
                  "dataApresentacao", "presidente", "idPropPrincipal", "ultimoStatus_dataHora",
                  "ultimoStatus_siglaOrgao", "ultimoStatus_regime", "ultimoStatus_descricaoTramitacao",
                  "ultimoStatus_descricaoSituacao", "ultimoStatus_apreciacao", "idRelator_ultimo",
                  "urlInteiroTeor"]], "proposicoes_executivo", saida)
    salvar(aut[["idProposicao", "codTipoAutor", "tipoAutor", "nomeAutor", "ordemAssinatura",
                "proponente"]], "autores_executivo", saida)

    alvo = props.loc[props["siglaTipo"].isin(TIPOS_FUNIL), "id"].tolist()
    print(f"Tramitações e relacionadas (API): {len(alvo)} proposições...")

    def baixa(i):
        t = get(f"{API}/proposicoes/{i}/tramitacoes")
        r = get(f"{API}/proposicoes/{i}/relacionadas")
        return ([dict(x, idProposicao=i) for x in (t.json()["dados"] if t is not None else [])],
                [dict(x, idProposicao=i) for x in (r.json()["dados"] if r is not None else [])])

    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(baixa, alvo))
    tram = pd.DataFrame([x for t, _ in res for x in t])
    tram = tram[["idProposicao", "dataHora", "sequencia", "siglaOrgao", "regime", "descricaoTramitacao",
                 "codTipoTramitacao", "descricaoSituacao", "codSituacao", "despacho", "uriUltimoRelator"]]
    tram["idUltimoRelator"] = id_da_uri(tram.pop("uriUltimoRelator").fillna(""))
    salvar(tram.sort_values(["idProposicao", "dataHora", "sequencia"]), "tramitacoes_executivo", saida)

    rels = pd.DataFrame([x for _, r in res for x in r]).rename(columns={"id": "idRelacionada"})
    if not rels.empty:
        rels = rels[["idProposicao", "idRelacionada", "siglaTipo", "numero", "ano", "ementa", "codTipo"]]
    salvar(rels, "relacionadas_executivo", saida)
    print("Concluído.")


if __name__ == "__main__":
    main()
