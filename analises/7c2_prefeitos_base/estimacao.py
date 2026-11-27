"""7-c.2: estimação pré-registrada. Uso (da raiz): python analises/7c2_prefeitos_base/estimacao.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analises.comum import emendas, estimacao as E, script  # noqa: E402

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import paineis as P  # noqa: E402

JANELA_EVENTO = (-9, 5)
REF = -4


def did(v, formula="y1 ~ delta_pos | deputado_id + idVotacao"):
    return E.feols(formula, v)


def empilhado(paineis):
    v = pd.concat(paineis, ignore_index=True)
    v["dep_rep"] = v["deputado_id"] + "_" + v["replica"].astype(str)
    v["vot_rep"] = v["idVotacao"] + "_" + v["replica"].astype(str)
    return E.feols("y1 ~ delta_pos | dep_rep + vot_rep", v, vcov={"CRV1": "dep_rep+vot_rep"}), v


def estudo_evento(v):
    v = v.copy()
    v, nomes = E.dummies_evento(v, "mes_rel", JANELA_EVENTO, ref=REF)
    for n in nomes:
        v[n] = v[n] * v["delta"]
    m = E.feols(f"y1 ~ {' + '.join(nomes)} | deputado_id + idVotacao", v)
    pre = [n for n in nomes if n.startswith("ev_m") and int(n[4:]) >= 5]
    teste = m.wald_test(R=np.eye(len(nomes))[[nomes.index(n) for n in pre]]) if pre else None
    return m, nomes, teste


def mediacao_emendas(v, ano):
    """H3 (depende da L6): parcela das emendas RP6 do deputado para municípios de prefeito aliado,
    antes e depois da posse. Devolve None enquanto dados/emendas/ estiver vazio."""
    if not emendas.disponivel("emendas", "ligacao_autor", "municipios_tse_ibge"):
        return {"status": "L6 ausente"}
    raise NotImplementedError("Implementar quando a L6 chegar: ver PREREG.md, H3.")


def main():
    res, principais = {}, []
    for ano in P.REPLICAS:
        v = script.ler_painel(__file__, f"replica_{ano}")
        principal = v[v["periodo"] != "transicao"]
        principais.append(principal)
        r = {"did": E.coeficientes(did(principal), ["delta_pos"]).to_dict("records")}
        med = principal["hhi_municipios"].median()
        for nome, sub in (("hhi_alto", principal[principal["hhi_municipios"] > med]),
                          ("hhi_baixo", principal[principal["hhi_municipios"] <= med])):
            r[nome] = E.coeficientes(did(sub), ["delta_pos"]).to_dict("records")
        me, nomes, teste = estudo_evento(v)
        r["estudo_evento"] = E.coeficientes(me, nomes).to_dict("records")
        r["teste_pre"] = None if teste is None else teste.to_dict()
        r["com_transicao"] = E.coeficientes(did(v.assign(delta_pos=v["delta"] * (v["periodo"] == "pos"))),
                                            ["delta_pos"]).to_dict("records")
        v2 = principal.assign(pres_pos=principal["partido_pres_camara"] * principal["pos"])
        r["controle_pres_camara"] = E.coeficientes(did(v2, "y1 ~ delta_pos + pres_pos | deputado_id + idVotacao"),
                                                   ["delta_pos", "pres_pos"]).to_dict("records")
        r["mediacao_emendas"] = mediacao_emendas(principal, ano)
        res[str(ano)] = r
    m, _ = empilhado(principais)
    res["empilhado"] = E.coeficientes(m, ["delta_pos"]).to_dict("records")
    print(E.salvar_resultados(AQUI, res))


if __name__ == "__main__":
    main()
