"""Estimação comum: regressões com efeitos fixos e erros agrupados em duas dimensões, estudos de
evento, dados sintéticos para testar estimadores e gravação de resultados amarrada ao pré-registro.
"""
import json
import math
import subprocess
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from . import config

VCOV_DUPLO = {"CRV1": "deputado_id+idVotacao"}


def feols(formula, dados, vcov=None):
    """pyfixest.feols com erros agrupados por deputado e votação por padrão."""
    import pyfixest as pf
    return pf.feols(formula, data=dados, vcov=vcov or VCOV_DUPLO)


def dummies_evento(df, col_tempo, janela, ref=-1, prefixo="ev"):
    """Cria ev_m3, ev_m2, ev_0, ev_p1… para tempo relativo em ``janela`` (min, max), omitindo ``ref``.
    Valores fora da janela são acumulados nas pontas (binning)."""
    lo, hi = janela
    t = df[col_tempo].clip(lo, hi)
    nomes = []
    for k in range(lo, hi + 1):
        if k == ref:
            continue
        nome = f"{prefixo}_{'m' if k < 0 else 'p'}{abs(k)}"
        df[nome] = (t == k).astype(float)
        nomes.append(nome)
    return df, nomes


def meses_relativos(datas, choque):
    """Meses inteiros desde o choque (0 = do dia do choque até um mês depois; -1 = mês anterior)."""
    d = pd.to_datetime(pd.Series(datas)).reset_index(drop=True)
    c = pd.Timestamp(choque)
    return ((d.dt.year - c.year) * 12 + (d.dt.month - c.month) - (d.dt.day < c.day).astype(int)).to_numpy()


def inferencia_placebo_datas(estimar, datas_placebo, estimativa_real):
    """Inferência por placebo no tempo: reestima com choques fictícios e devolve a distribuição e o
    p-valor bilateral (proporção de |placebo| >= |real|). ``estimar(data) -> float``."""
    dist = np.array([estimar(d) for d in datas_placebo], dtype=float)
    dist = dist[np.isfinite(dist)]
    p = (1 + np.sum(np.abs(dist) >= abs(estimativa_real))) / (1 + len(dist))
    return {"placebos": dist.tolist(), "p_valor": float(p), "n_placebos": int(len(dist))}


# ------------------------------------------------------------------ dados sintéticos
def simular_painel_votos(n_dep=120, n_vot=200, efeito=0.15, frac_tratados=0.3, t_choque=100,
                         dose_continua=False, semente=config.SEMENTE):
    """Painel deputado × votação com efeito conhecido do tratamento após ``t_choque``.
    y = 1(seguiu governo) gerado por modelo de probabilidade linear com efeitos de deputado e votação."""
    rng = np.random.default_rng(semente)
    dep = pd.DataFrame({"deputado_id": [f"d{i}" for i in range(n_dep)],
                        "alfa": rng.normal(0.6, 0.1, n_dep)})
    if dose_continua:
        dep["dose"] = rng.uniform(0, 1, n_dep)
    else:
        dep["dose"] = (rng.uniform(size=n_dep) < frac_tratados).astype(float)
    vot = pd.DataFrame({"idVotacao": [f"v{j}" for j in range(n_vot)], "t": np.arange(n_vot),
                        "gama": rng.normal(0, 0.1, n_vot)})
    df = dep.merge(vot, how="cross")
    df["pos"] = (df["t"] >= t_choque).astype(float)
    p = (df["alfa"] + df["gama"] + efeito * df["dose"] * df["pos"]).clip(0.01, 0.99)
    df["y"] = (rng.uniform(size=len(df)) < p).astype(float)
    df["tratado_pos"] = df["dose"] * df["pos"]
    return df


# ------------------------------------------------------------------ resultados
def _commit_do_prereg(pasta):
    """Hash do último commit do PREREG.md; recusa se houver mudanças não commitadas."""
    pre = Path(pasta) / "PREREG.md"
    st = subprocess.run(["git", "status", "--porcelain", str(pre)], capture_output=True, text=True,
                        cwd=config.RAIZ).stdout.strip()
    if st:
        raise RuntimeError(f"{pre} tem mudanças não commitadas: feche o pré-registro antes de estimar.")
    h = subprocess.run(["git", "log", "-1", "--format=%H", "--", str(pre)], capture_output=True, text=True,
                       cwd=config.RAIZ).stdout.strip()
    if not h:
        raise RuntimeError(f"{pre} nunca foi commitado.")
    return h


def _limpar(x):
    if isinstance(x, dict):
        return {k: _limpar(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_limpar(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if not math.isfinite(float(x)) else float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def salvar_resultados(pasta, resultados, nome="resultados.json", exigir_prereg=True):
    """Grava resultados/<nome> com o hash do pré-registro e a data. NaN vira null."""
    pasta = Path(pasta)
    meta = {"gerado_em": datetime.now().isoformat(timespec="seconds"),
            "prereg_commit": _commit_do_prereg(pasta) if exigir_prereg else None}
    out = pasta / "resultados"
    out.mkdir(exist_ok=True)
    (out / nome).write_text(json.dumps(_limpar({"meta": meta, **resultados}), ensure_ascii=False, indent=2),
                            encoding="utf-8")
    return out / nome


def coeficientes(modelo, termos=None):
    """Tabela com coeficiente, erro padrão, IC 95% e n de um modelo pyfixest."""
    t = modelo.tidy().reset_index().rename(columns={"Coefficient": "termo"})
    if termos is not None:
        t = t[t["termo"].isin(termos)]
    t["n"] = modelo._N
    return t
