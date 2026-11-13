"""Recodifica os discursos com o texto corrigido (sem cabeçalho de orador/oradora e sem marcas de
gênero do sumário) e guarda um vetor por discurso em cache/ (não versionado).
Uso: python artigos/07-multivisao-fusao/codificar_discursos.py   (~30-40 min em CPU)"""
import re
from pathlib import Path
import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
CACHE = AQUI / "cache"
CACHE.mkdir(exist_ok=True)
CAB = re.compile(r"^\s*(O|A) SRA?\.\s.*?\)\s*-\s*", re.S)
CAB_ENC = re.compile(r"^\s*DISCURSO NA [ÍI]NTEGRA ENCAMINHADO PEL[OA] SRA?\.? DEPUTAD[OA] .*?\)\.?\s*", re.S)


def limpar_fala(t):
    return CAB_ENC.sub("", CAB.sub("", t, count=1), count=1)


def limpar_sumario(t):
    t = re.sub(r"\bA Deputada\b", "O Deputado", t)
    t = re.sub(r"\ba Deputada\b", "o Deputado", t)
    t = re.sub(r"\bDeputada\b", "Deputado", t)
    t = re.sub(r"\bdeputada\b", "deputado", t)
    t = re.sub(r"\b([Aa]) oradora\b", lambda m: ("O" if m.group(1) == "A" else "o") + " orador", t)
    t = re.sub(r"\boradora\b", "orador", t)
    t = re.sub(r"\bEla\b", "Ele", t)
    t = re.sub(r"\bela\b", "ele", t)
    return t


def textos():
    d = pd.read_parquet(RAIZ / "dados/leg57/discursos.parquet",
                        columns=["id_discurso", "deputado_id", "dataHoraInicio", "tipoDiscurso",
                                 "keywords", "sumario", "transcricao"])
    d = d[d["transcricao"].fillna("").str.len() > 50].reset_index(drop=True)
    d["fala"] = "passage: " + d["transcricao"].map(limpar_fala)
    d["tema"] = "passage: " + (d["sumario"].fillna("") + " " + d["keywords"].fillna("")).map(limpar_sumario)
    return d


def main():
    from sentence_transformers import SentenceTransformer
    import torch
    torch.set_num_threads(max(1, torch.get_num_threads()))
    d = textos()
    d[["id_discurso", "deputado_id", "dataHoraInicio", "tipoDiscurso", "keywords"]].to_parquet(
        CACHE / "discursos_meta.parquet", index=False)
    st = SentenceTransformer("intfloat/multilingual-e5-small")
    for nome, col, L in [("tema", "tema", 512), ("fala", "fala", 256)]:
        arq = CACHE / f"vet_{nome}.npy"
        if arq.exists() and len(np.load(arq, mmap_mode="r")) == len(d):
            continue
        st.max_seq_length = L
        e = st.encode(d[col].tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=False)
        np.save(arq, e.astype(np.float16))
        print(nome, e.shape, flush=True)


if __name__ == "__main__":
    main()
