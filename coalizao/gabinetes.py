"""Indicadores de gerência da coalizão por GABINETE (subgabinetes), 1985-2026.

Segue a unidade de análise da planilha de Almeida (Ipea, NT 53/2021): um novo gabinete
começa com A = inauguração de presidente; B = mudança no conjunto de partidos do gabinete;
C = mudança relevante de ministro (que altera a distribuição de recursos/influência entre
os partidos da base ou a direção de política-chave). As cadeiras são as da data de início.

* Sarney-1 a Lula 3-4 (mar/1985 a jun/2024): composição e cadeiras de Almeida.
* Lula 3-5 em diante: gabinetes identificados aqui com os mesmos critérios, a partir de
  dados_brutos/lula3_gabinete_2023_2026.csv e das cadeiras mensais da 57ª legislatura.
  A classificação dos eventos C é nossa (Almeida não cobre o período).

Saída: resultados/gabinetes_1985_2026.csv
Uso:   python coalizao/gabinetes.py
"""
import pandas as pd

import indicadores_coalizao as ic
from cadeiras_leg57 import cadeiras_mensais

# Gabinetes de Lula 3 após o último de Almeida (Lula 3-4, abr/2024)
EXTENSAO_LULA3 = [
    ("Lula 3-5", "C", "2024-09-27", "Macaé Evaristo (PT) assume Direitos Humanos no lugar de Silvio Almeida (np)"),
    ("Lula 3-6", "C", "2025-03-10", "Padilha (PT) assume a Saúde no lugar de Nísia Trindade (np); Gleisi Hoffmann (PT) assume a SRI"),
    ("Lula 3-7", "B", "2025-09-02", "União Brasil e PP deixam o governo; seus ministros passam a não partidários"),
    ("Lula 3-8", "C", "2025-10-21", "Boulos (PSOL) assume a Secretaria-Geral no lugar de Márcio Macêdo (PT)"),
    ("Lula 3-9", "B", "2026-04-01", "desincompatibilizações: MDB e Rede deixam de ter ministros; 17 trocas"),
]

def _ideologia_partidos(comp, inicio):
    return ic.partidos_ideologia([p for p, _, _ in comp if p != "np"], inicio)


def tabela_gabinetes():
    ide = ic.carregar_ideologia()
    alm = ic.comp_almeida().reset_index(drop=True)
    gab = pd.read_csv(ic.BRUTOS / "lula3_gabinete_2023_2026.csv", sep=";", parse_dates=["inicio", "fim"])
    cad = cadeiras_mensais(fim=ic.FIM)
    cad["partido"] = cad.partido.replace(ic.NORM)
    cad = cad.groupby(["t", "partido"], as_index=False).cadeiras.sum()

    linhas = []
    for _, g in alm.iterrows():
        linhas.append(dict(gabinete=g.gabinete, evento=g.evento, inicio=g.inicio, comp=g.comp,
                           fonte="Almeida (Ipea)", descricao=""))
    for nome, ev, ini, desc in EXTENSAO_LULA3:
        ini = pd.Timestamp(ini)
        t_cad = ini.to_period("M").to_timestamp() + pd.Timedelta(days=14)
        # composição no dia de início; cadeiras do mês de início
        ativos_comp, _ = ic.comp_lula3(ini, gab, cad.assign(t=cad.t), "partido")
        seats = cad[cad.t == t_cad].set_index("partido").cadeiras
        comp = [(p, m, 0 if p == "np" else int(seats.get(p, 0))) for p, m, _ in ativos_comp]
        linhas.append(dict(gabinete=nome, evento=ev, inicio=ini, comp=comp,
                           fonte="extensão própria", descricao=desc))

    tab = pd.DataFrame(linhas).sort_values("inicio").reset_index(drop=True)
    tab["fim"] = tab.inicio.shift(-1).fillna(pd.Timestamp(ic.FIM))
    # fim de mandato encerra o gabinete
    fins_mandato = {"Sarney": "1990-03-15", "Collor": "1992-10-02", "Itamar": "1995-01-01"}
    for pres, f in fins_mandato.items():
        m = tab.gabinete.str.startswith(pres + "-")
        ultimo = tab[m].index.max()
        tab.loc[ultimo, "fim"] = pd.Timestamp(f)
    tab["meses"] = ((tab.fim - tab.inicio).dt.days / 30.44).round(1)

    out = []
    for _, r in tab.iterrows():
        comp = r.comp
        partidos = _ideologia_partidos(comp, r.inicio)
        het, sem = ic.heterogeneidade(partidos, r.inicio.year, ide)
        out.append({
            "gabinete": r.gabinete, "evento": r.evento, "inicio": r.inicio.date(), "fim": r.fim.date(),
            "meses": r.meses,
            "n_cargos": sum(m for _, m, _ in comp),
            "ministros_np": sum(m for p, m, _ in comp if p == "np"),
            "tamanho": sum(p != "np" for p, _, _ in comp),
            "cadeiras_coalizao": sum(s for _, _, s in comp),
            "cadeiras_coalizao_pct": round(100 * sum(s for _, _, s in comp) / ic.tamanho_camara(r.inicio), 1),
            "proporcionalidade": round(ic.coalescencia(comp), 1),
            "proporc_np_grupo": round(ic.coalescencia(comp, np_em_grupo=True), 1),
            "heterogeneidade": round(het, 1) if het == het else None,
            "partidos_sem_ideologia": sem,
            "prop_v1_kd": round(ic.koppel_diskin(comp, True), 1),
            "prop_v2_kd": round(ic.koppel_diskin(comp, False), 1),
            "composicao": " ".join(f"{p}({m},{s})" for p, m, s in comp),
            "fonte": r.fonte, "descricao": r.descricao,
        })
    return pd.DataFrame(out)


if __name__ == "__main__":
    ic.SAIDA.mkdir(exist_ok=True)
    t = tabela_gabinetes()
    t.to_csv(ic.SAIDA / "gabinetes_1985_2026.csv", sep=";", index=False)
    pd.set_option("display.width", 250)
    print(t.drop(columns=["composicao", "descricao", "fonte"]).to_string(index=False))
