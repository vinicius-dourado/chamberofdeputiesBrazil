"""Cadeiras em exercício por partido na Câmara (57ª legislatura), mês a mês.

Usa o histórico de status de cada deputado (dados/leg57/deputados_historico.parquet,
gerado por baixar_legislatura.py). Um deputado conta para o partido em que estava
na data de referência (dia 15 de cada mês) se a situação vigente for "Exercício".
"""
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent


def cadeiras_mensais(inicio="2023-01-01", fim="2026-12-15", legislatura=57, posse="2023-02-15"):
    """legislatura/posse permitem reutilizar a função com dados/leg55 e dados/leg56
    (posse = dia 15 do mês de posse; antes dele vale a composição desse dia)."""
    h = pd.read_parquet(RAIZ / f"dados/leg{legislatura}/deputados_historico.parquet")
    h["dataHora"] = pd.to_datetime(h["dataHora"])
    h = h.sort_values(["id", "dataHora"])
    # eventos sem situação (marcadores de início de legislatura) herdam a anterior
    h["situacao"] = h.groupby("id")["situacao"].ffill()
    datas = pd.date_range(inicio, fim, freq="MS") + pd.Timedelta(days=14)
    linhas = []
    for t in datas:
        # antes da posse (1º/02) usa a composição do dia 15 do mês de posse
        ref = max(t, pd.Timestamp(posse))
        ult = h[h.dataHora <= ref].groupby("id").tail(1)
        ex = ult[ult.situacao == "Exercício"]
        cont = ex.siglaPartido.value_counts()
        for p, n in cont.items():
            linhas.append({"t": t, "partido": p, "cadeiras": int(n)})
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    c = cadeiras_mensais()
    piv = c.pivot(index="t", columns="partido", values="cadeiras").fillna(0).astype(int)
    print(piv.sum(axis=1).describe())
    print(piv.loc[:, ["PT", "MDB", "PSD", "UNIÃO", "PSB", "PCdoB", "PSOL", "REDE", "PDT", "PP", "REPUBLICANOS", "PL"]].iloc[[0, 8, 12, 15, 30, 39, 46]])
