"""Utilidades para os scripts das pastas de desenho (que não são pacotes importáveis)."""
from pathlib import Path

import pandas as pd


def cache(arquivo_script):
    p = Path(arquivo_script).resolve().parent / "cache"
    p.mkdir(exist_ok=True)
    return p


def ler_painel(arquivo_script, nome):
    f = cache(arquivo_script) / f"{nome}.parquet"
    if not f.exists():
        raise FileNotFoundError(f"{f} não existe: rode antes o paineis.py desta pasta.")
    return pd.read_parquet(f)


def gravar_painel(arquivo_script, nome, df):
    f = cache(arquivo_script) / f"{nome}.parquet"
    df.to_parquet(f, index=False)
    return f


def descrever(df, por, col_id="deputado_id", col_vot="idVotacao"):
    """Tamanhos de amostra (nunca médias do desfecho): deputados, votações e linhas por grupo."""
    return df.groupby(por).agg(deputados=(col_id, "nunique"), votacoes=(col_vot, "nunique"),
                               linhas=(col_vot, "size")).reset_index()
