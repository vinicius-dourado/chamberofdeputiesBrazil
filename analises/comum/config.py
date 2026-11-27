"""Caminhos, períodos e choques institucionais usados por todos os desenhos.

Regra: toda data ou limiar que afete resultados mora aqui (ou no topo do script do desenho),
com fonte. Choques com ``verificar=True`` ainda não foram conferidos em fonte primária e não
podem entrar na especificação principal de nenhum PREREG até serem confirmados.
"""
from dataclasses import dataclass
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "dados"
ANALISES = RAIZ / "analises"
EMENDAS = DADOS / "emendas"
GABINETES = DADOS / "gabinetes"
TSE = DADOS / "tse"
EXECUTIVO = DADOS / "executivo"

SEMENTE = 20231

# legislaturas com dados de votação no repositório
LEGISLATURAS = {
    53: (date(2007, 2, 1), date(2011, 1, 31)),
    54: (date(2011, 2, 1), date(2015, 1, 31)),
    55: (date(2015, 2, 1), date(2019, 1, 31)),
    56: (date(2019, 2, 1), date(2023, 1, 31)),
    57: (date(2023, 2, 1), date(2027, 1, 31)),
}

# governos (para separar choques de trocas de presidente). Fonte: datas de posse/afastamento.
GOVERNOS = [
    ("Lula 2", date(2007, 1, 1), date(2010, 12, 31)),
    ("Dilma 1", date(2011, 1, 1), date(2014, 12, 31)),
    ("Dilma 2", date(2015, 1, 1), date(2016, 5, 11)),   # afastamento em 12/05/2016
    ("Temer", date(2016, 5, 12), date(2018, 12, 31)),
    ("Bolsonaro", date(2019, 1, 1), date(2022, 12, 31)),
    ("Lula 3", date(2023, 1, 1), date(2026, 12, 31)),
]

# oposição declarada por governo: nunca usada como grupo de "base" nos controles
OPOSICAO_DECLARADA = {"Lula 3": {"PL", "NOVO"}}

# ----------------------------------------------------------------------------- medidas
VOTOS_VALIDOS = ("Sim", "Não", "Obstrução", "Abstenção")
DIRECIONAL = {"Sim": 1.0, "Não": 0.0, "Obstrução": 0.0}   # Abstenção fica fora da medida direcional
MARGEM_APERTADA = 0.10        # votação-chave: margem < 10% do quórum (6-c.1)
LIMIAR_COALIZAO_LEGISLATIVA = 0.70   # partido na coalizão legislativa do mês (6-c.3)
MIN_VOTACOES_DIVERGENTES_MES = 3     # mínimo para calcular a taxa mensal de um partido

# Sílvio Costa Filho (Portos e Aeroportos, set./2023): o CSV o marca "ind" e o Ipea não conta o
# Republicanos no gabinete. Principal = convenção do Ipea; robustez = REPUBLICANOS.
SILVIO_COSTA_FILHO_COMO = "np"


@dataclass(frozen=True)
class Choque:
    data: date
    descricao: str
    fonte: str
    verificar: bool = False
    desenhos: tuple = ()


CHOQUES = {
    "ec86": Choque(date(2015, 3, 17), "EC 86/2015: emendas individuais impositivas",
                   "Promulgação da EC 86 (DOU 18/03/2015)", False, ("4c1", "3c5")),
    "ec100": Choque(date(2019, 6, 26), "EC 100/2019: emendas de bancada impositivas (efeito no orçamento de 2020)",
                    "Promulgação da EC 100", False, ("4c1", "6c2b", "7c3", "3c5")),
    "ec105": Choque(date(2019, 12, 12), "EC 105/2019: transferências especiais",
                    "Promulgação da EC 105", False, ("6c2b", "7c2")),
    "stf_rp9": Choque(date(2022, 12, 19), "STF julga o RP9 inconstitucional (ADPFs 850, 851, 854)",
                      "Julgamento no plenário do STF", False, ("6c2b",)),
    "ec126": Choque(date(2022, 12, 21), "EC 126/2022: redistribui os recursos do RP9",
                    "Promulgação da EC 126", False, ("6c2b",)),
    "entrada_pp_rep": Choque(date(2023, 9, 13), "Posse de Fufuca (PP) e Sílvio Costa Filho (Republicanos)",
                             "dados/gabinetes/ministros.parquet", False, ("6c2a",)),
    "stf_suspende_emendas": Choque(date(2024, 8, 14), "STF (min. Flávio Dino, ADI 7697) suspende a execução de emendas impositivas até haver regras de transparência",
                                   "a conferir: decisão monocrática e referendo do plenário em ago./2024", True, ("4c1", "6c1", "6c2b")),
    "lc_emendas": Choque(date(2024, 11, 25), "Lei complementar sobre emendas (LC 210/2024) sancionada",
                         "a conferir: data de sanção e de liberação dos pagamentos pelo STF", True, ("4c1", "6c1", "6c2b")),
    "posse_prefeitos_2025": Choque(date(2025, 1, 1), "Posse dos prefeitos eleitos em 2024",
                                   "CF art. 29, III", False, ("7c2",)),
    "mesa_2025": Choque(date(2025, 2, 1), "Hugo Motta assume a Presidência da Câmara",
                        "dados/leg57/mesa.parquet", False, ("7c2", "6c3", "3c2")),
    "anuncio_entrada_pp_rep": Choque(date(2023, 8, 4), "Padilha confirma que Fufuca e Sílvio Costa Filho serão ministros",
                                     "Jovem Pan, 04/08/2023; negociação pública desde jul./2023", False, ("6c2a",)),
    "desembarque_uniao_pp": Choque(date(2025, 9, 2), "Federação União Progressista anuncia a saída de União e PP da base (30 dias para os ministros saírem); ministros ficam",
                                   "Congresso em Foco e Estadão, 02/09/2025; executiva do União oficializa em 03/09", False, ("6c2a",)),
    "ultimato_uniao": Choque(date(2025, 9, 18), "Executiva do União (Resolução CEN 19/2025) dá 24 h para filiados deixarem cargos",
                             "Agência Brasil e Congresso em Foco, 18/09/2025", False, ("6c2a",)),
    "federacao_up_tse": Choque(date(2026, 3, 26), "TSE registra a federação União Progressista (União + PP)",
                               "TSE, RFP 0601165-53.2025.6.00.0000", False, ("6c2a",)),
    "volta_uniao": Choque(date(2025, 12, 19), "União volta com Gustavo Feliciano no Turismo",
                          "DOU 19/12/2025 (nomeação); posse 23/12/2025", False, ("6c2a",)),
}

# posses de prefeitos no meio de legislatura (réplicas de 7-c.2)
POSSES_PREFEITOS = {2009: 2008, 2013: 2012, 2017: 2016, 2021: 2020, 2025: 2024}   # ano da posse: ano da eleição


def choque(chave, permitir_nao_verificado=False):
    """Data de um choque. Recusa choques não conferidos, salvo pedido explícito (robustez)."""
    c = CHOQUES[chave]
    if c.verificar and not permitir_nao_verificado:
        raise ValueError(f"Choque '{chave}' ({c.data}) ainda não foi conferido em fonte primária: "
                         f"{c.fonte}. Confirme e marque verificar=False em analises/comum/config.py.")
    return c.data


def governo_na_data(d):
    for nome, ini, fim in GOVERNOS:
        if ini <= d <= fim:
            return nome
    return None


def legislatura_na_data(d):
    for leg, (ini, fim) in LEGISLATURAS.items():
        if ini <= d <= fim:
            return leg
    return None
