"""Interface com os dados de emendas (lacuna L6). Enquanto dados/emendas/ estiver vazio, as
funções levantam ``DadosAusentes`` e os testes marcados ``requer_l6`` são pulados.

Esquema esperado (um parquet por tabela; nomes de colunas em minúsculas):

emendas.parquet (uma linha por emenda × ano; SIOP + Portal da Transparência)
    ano:int, codigo_emenda:str, rp:int (6, 7, 8 ou 9), autor_nome:str,
    autor_tipo:str ('individual' | 'bancada' | 'comissao' | 'relator'), autor_uf:str,
    orgao:str, acao:str, localizador:str, funcao:str, municipio_ibge:str|None, uf_favorecida:str|None,
    transferencia_especial:bool, valor_dotacao, valor_empenhado, valor_liquidado, valor_pago:float

documentos.parquet (cadeia SIAFI/Tesouro Gerencial; uma linha por documento)
    codigo_emenda:str, ano:int, fase:str ('empenho' | 'liquidacao' | 'pagamento'),
    documento:str (NE, NL, OB…), data:date, valor:float, ug:str, favorecido:str|None, municipio_ibge:str|None

ligacao_autor.parquet (autor da emenda individual -> deputado)
    autor_nome:str, autor_uf:str, ano:int, deputado_id:str, metodo:str ('exato' | 'aproximado' | 'manual')

despesa_rp_mes.parquet (para o IDE e o mix de moedas: despesa discricionária por órgão)
    mes:str (AAAA-MM), orgao:str, rp:int (2, 6, 7, 8, 9), empenhado:float, pago:float

municipios_tse_ibge.parquet (correspondência de códigos; o TSE e o IBGE usam códigos diferentes)
    cd_municipio_tse:str, municipio_ibge:str, uf:str

ipca.parquet: mes:str (AAAA-MM), indice:float  (deflação)
"""
import pandas as pd

from . import config

ARQUIVOS = ("emendas", "documentos", "ligacao_autor", "despesa_rp_mes", "municipios_tse_ibge", "ipca")
COLUNAS = {
    "emendas": {"ano", "codigo_emenda", "rp", "autor_nome", "autor_tipo", "autor_uf", "orgao", "acao",
                "municipio_ibge", "uf_favorecida", "transferencia_especial", "valor_empenhado", "valor_pago"},
    "documentos": {"codigo_emenda", "ano", "fase", "documento", "data", "valor", "municipio_ibge"},
    "ligacao_autor": {"autor_nome", "autor_uf", "ano", "deputado_id", "metodo"},
    "despesa_rp_mes": {"mes", "orgao", "rp", "empenhado", "pago"},
    "municipios_tse_ibge": {"cd_municipio_tse", "municipio_ibge", "uf"},
    "ipca": {"mes", "indice"},
}


class DadosAusentes(FileNotFoundError):
    """Os dados de emendas (L6) ainda não estão em dados/emendas/."""


def disponivel(*nomes):
    nomes = nomes or ARQUIVOS
    return all((config.EMENDAS / f"{n}.parquet").exists() for n in nomes)


def ler(nome):
    f = config.EMENDAS / f"{nome}.parquet"
    if not f.exists():
        raise DadosAusentes(f"{f} não existe. Lacuna L6: ver o esquema em analises/comum/emendas.py.")
    df = pd.read_parquet(f)
    faltam = COLUNAS[nome] - set(df.columns)
    if faltam:
        raise ValueError(f"{nome}.parquet sem as colunas {sorted(faltam)}")
    return df


def deflator(base_mes):
    """Fator para levar valores de cada mês a preços de ``base_mes`` (AAAA-MM)."""
    i = ler("ipca").set_index("mes")["indice"]
    return i.loc[base_mes] / i


def emendas_individuais_por_deputado():
    """Emendas RP6 ligadas ao deputado autor; devolve (df, taxa_ligacao_por_valor)."""
    e = ler("emendas")
    e = e[e["autor_tipo"] == "individual"]
    lig = ler("ligacao_autor")
    m = e.merge(lig, on=["autor_nome", "autor_uf", "ano"], how="left")
    taxa = m.loc[m["deputado_id"].notna(), "valor_empenhado"].sum() / m["valor_empenhado"].sum()
    return m, float(taxa)


def painel_p2(base_mes="2026-01"):
    """P2: deputado × dia × RP com valores por fase (empenho, liquidação, pagamento), deflacionados.
    Só emendas individuais; o rateio do RP7 pela bancada é feito em 6c1_momento_pagamentos/paineis.py."""
    doc = ler("documentos")
    emd, _ = emendas_individuais_por_deputado()
    d = doc.merge(emd[["codigo_emenda", "ano", "rp", "deputado_id"]], on=["codigo_emenda", "ano"])
    d["mes"] = pd.to_datetime(d["data"]).dt.strftime("%Y-%m")
    d["valor_real"] = d["valor"] * d["mes"].map(deflator(base_mes))
    return (d.pivot_table(index=["deputado_id", "data", "rp"], columns="fase", values="valor_real",
                          aggfunc="sum", fill_value=0.0).reset_index())
