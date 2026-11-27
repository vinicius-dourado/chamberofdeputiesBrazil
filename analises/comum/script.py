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


def modulo_irmao(arquivo_chamador, nome):
    """Importa paineis.py/estimacao.py/eventos.py da mesma pasta do chamador com um nome único.
    As pastas dos desenhos têm módulos com o mesmo nome; ``import paineis`` pegaria o de outra pasta
    quando os testes rodam juntos."""
    import importlib.util
    import sys
    pasta = Path(arquivo_chamador).resolve().parent
    chave = f"_desenho_{pasta.name}_{nome}"
    if chave in sys.modules:
        return sys.modules[chave]
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))
    spec = importlib.util.spec_from_file_location(chave, pasta / f"{nome}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[chave] = mod
    spec.loader.exec_module(mod)
    return mod
