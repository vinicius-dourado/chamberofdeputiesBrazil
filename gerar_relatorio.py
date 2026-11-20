"""Gera a página HTML da replicação a partir de resultados/replicacao/resultados.json.

Uso: python gerar_relatorio.py   (depois de python replicar_artigo.py)
Saída: resultados/replicacao/relatorio.html
"""
import html
import json
import math
from pathlib import Path

R = json.loads(Path("resultados/replicacao/resultados.json").read_text())
SAIDA = Path("resultados/replicacao/relatorio.html")
ROT = R["rotulos"]

def esc(x):
    return html.escape(str(x))


def estrelas(p):
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return ""
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


def num(x, d=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    if abs(x) >= 10000:
        return f"{x:,.0f}".replace(",", ".")
    return f"{x:.{d}f}".replace(".", ",")


def rot(v):
    return ROT.get(v, v)


def coef_de(tab, eq, var):
    for c in tab["coefs"]:
        if c.get("equacao") == eq and c["variavel"] == var:
            return c
    return None


def celula(c):
    if c is None:
        return '<td class="n vazio">–</td>'
    s = estrelas(c["p"])
    cls = "n sig" if s else "n"
    return (f'<td class="{cls}">{num(c["coef"])}<sup>{s}</sup>'
            f'<span class="ep">({num(c["ep"])})</span></td>')


# ------------------------------------------------------------------ Tabela 6 do artigo (1998)
def tabela6_artigo():
    import csv
    linhas = [l for l in Path("dados/manual/artigo_1998_tabela6.csv").read_text().splitlines() if not l.startswith("#")]
    nomes = {"concentracao": "concentracao_2022", "ausencia": "ausencia_pct"}
    coefs = []
    for r in csv.DictReader(linhas, delimiter=";"):
        if r["variavel"] in ("emendas", "pork", "media_execucao"):
            continue
        c, z = float(r["coef"]), float(r["z"])
        coefs.append({"equacao": r["equacao"], "variavel": nomes.get(r["variavel"], r["variavel"]), "coef": c,
                      "ep": abs(c / z) if z else float("nan"), "z": z, "p": float(r["p"])})
    at, at_ep = 0.6641988, 0.6641988 / 1.11
    return {"coefs": coefs, "n": 536, "n_selecionados": 430, "n_reeleitos": "–", "rho": math.tanh(at),
            "rho_ic95": [math.tanh(at - 1.96 * at_ep), math.tanh(at + 1.96 * at_ep)], "lr_rho0": 1.14,
            "p_lr_rho0": 0.2855, "loglik": -493.0925}


ART6 = tabela6_artigo()


def concorda(a, b):
    """1 se os dois coeficientes têm a mesma leitura (ambos n.s., ou ambos significativos com o mesmo sinal)."""
    if a is None or b is None:
        return None
    sa, sb = a["p"] < 0.1, b["p"] < 0.1
    return int(sa == sb and (not sa or (a["coef"] > 0) == (b["coef"] > 0)))


ROTULO_VEREDITO = {"confirma": "Confirma", "parcial": "Em parte", "diverge": "Diverge"}


VAL = Path("resultados/validacao_1998/resultados.json")
# diagnóstico de cada divergência, com base no modelo reduzido estimado para 1998 e 2026
DIAG = [
    ("Seleção (ρ)", "rho", "ρ ≈ 0,58, z = 1,11; independência não rejeitada (p = 0,29)", "nt",
     "ρ vai a um dos limites conforme a especificação, em 1998 e em 2026. O próprio artigo estima ρ com muita "
     "imprecisão. Não dá para atribuir a diferença ao cenário."),
    ("Concentração (seleção)", "concentracao_ant", "Positiva na seleção (0,007**, em p.p.)", "cenario",
     "Em 1998 o nosso código reproduz o sinal positivo; em 2026 é negativa: quem concentrou votos concorre menos."),
    ("Histexec", "histexec", "Negativa na seleção (−0,17*) e no resultado (−0,29**)", "cenario",
     "Em 1998 o nosso código reproduz as duas (−0,27*** e −0,23**); em 2026 segue negativa na seleção e passa a "
     "positiva no resultado."),
    ("SairCoalizão", "sair_coalizao", "Negativa no resultado (−0,95**); n.s. na seleção", "cenario",
     "Em 1998 o nosso código reproduz o artigo (−0,84*); em 2026 não tem efeito. Ressalva: a planilha do Ipea termina "
     "em abr/2024."),
    ("Senior", "senior", "Não significativa", "cenario",
     "Não significativa em 1998, como no artigo; em 2026 reduz a chance de concorrer."),
    ("Histleg, Burocracia, EntrarCoalizão", "burocracia", "Não significativas", "ok",
     "Não significativas em 1998, como no artigo (Burocracia mostrada)."),
    ("MesmaBase, Governador (resultado)", "mesma_base", "Não significativas", "ok",
     "Não significativas em 1998 (MesmaBase mostrada). Em 2026 MesmaBase passa a negativa."),
    ("Ausência", None, "Proporção; −1,02* no resultado, n.s. na seleção", "corrigido",
     "Usávamos o número de faltas; corrigido para proporção. Em 2026 reduz a chance de concorrer, não a de se "
     "reeleger. Sem votos nominais de 1995-1998 para testar."),
    ("Burocracia, Governador, EntrarCoalizão (medidas)", None, "Médias das Tabelas 2 e 3", "corrigido",
     "Corrigidas com as tabelas do artigo: ocupações em órgãos públicos, coligações de 1994 do TSE e troca de fora "
     "para dentro da coalizão."),
    ("Projetos, Esquerda, Governador e Empresa na seleção", None, "Não significativas", "limite",
     "Diferem em 1998 por limite dos dados da época: situação atual das proposições; ideologia da onda de 2018 de "
     "Bolognesi; coligações de 1994 incompletas."),
    ("Gastos por eleitor", None, "Perdedores gastam mais por eleitor", "limite",
     "Não há prestação de contas de 1998 nos dados abertos do TSE."),
]
ROT_DIAG = {"metodo": ("diverge", "Método ou medida"), "cenario": ("confirma", "Cenário mudou"),
            "ok": ("confirma", "Reproduz o artigo"), "nt": ("parcial", "Inconclusivo"),
            "corrigido": ("parcial", "Erro nosso, corrigido"), "limite": ("parcial", "Limite dos dados de 1998")}
ARTIGO_MEDIAS = Path("dados/manual/artigo_1998_tabelas.csv")
# variável do artigo -> (coluna em medias_1998, coluna nas tabelas 2-3 de 2026, multiplicador)
MAPA_MEDIAS = {
    "concentracao_94": ("concentracao_ant", "concentracao_2022", 100), "concentracao_98": ("concentracao_atual", "concentracao_2026", 100),
    "competicao": ("competicao_atual", "competicao_2026", 1), "governador_94": ("governador", "governador", 1),
    "mesma_base": ("mesma_base", "mesma_base", 1), "projetos": ("projetos", "projetos", 1),
    "ausencia": (None, "ausencia_pct", 1), "mesa": (None, "mesa", 1), "permanente": (None, "permanente", 1),
    "especial": (None, "especial", 1), "histleg": ("histleg", "histleg", 1), "histexec": ("histexec", "histexec", 1),
    "burocracia": ("burocracia", "burocracia", 1), "empresa": ("empresa", "empresa", 1),
    "entrar_coalizao": ("entrar_coalizao", "entrar_coalizao", 1), "sair_coalizao": ("sair_coalizao", "sair_coalizao", 1),
    "indice": (None, "indice", 1),
}
NOMES_MEDIAS = {"concentracao_94": "Concentração 94 / 22 (%)", "concentracao_98": "Concentração 98 / 26 (%)",
                "competicao": "Competição", "governador_94": "Governador", "mesma_base": "MesmaBase",
                "projetos": "Projetos", "ausencia": "Ausência (proporção)", "mesa": "Mesa", "permanente": "Permanente",
                "especial": "Especial", "histleg": "Histleg", "histexec": "Histexec", "burocracia": "Burocracia",
                "empresa": "Empresa", "entrar_coalizao": "EntrarCoalizão", "sair_coalizao": "SairCoalizão",
                "indice": "Índice"}


def tabela_medias_comparadas(v):
    import csv
    art = {r["variavel"]: r for r in csv.DictReader(
        (l for l in ARTIGO_MEDIAS.read_text().splitlines() if not l.startswith("#")), delimiter=";")}
    m98 = {r["variavel"]: r for r in v["medias_1998"]}
    m26 = {r["variavel"]: r for r in R["tabela2"] + R["tabela3"]}

    def trio(r, k, chave_n, chave_r):
        if r is None:
            return '<td class="n vazio">–</td>' * 3
        return (f'<td class="n">{num(k * float(r[chave_n]), 2)}</td><td class="n">{num(k * float(r[chave_r]), 2)}</td>'
                f'<td class="n">{num(float(r["z"]), 2)}<sup>{estrelas(2 * (1 - __import__("scipy").stats.norm.cdf(abs(float(r["z"])))))}</sup></td>')
    linhas = []
    for var, (c98, c26, k) in MAPA_MEDIAS.items():
        a = art.get(var)
        ca = trio(a, 1, "media_nao_reeleitos", "media_reeleitos") if a else '<td class="n vazio">–</td>' * 3
        c1 = trio(m98.get(c98), k, "media_nao_reeleitos", "media_reeleitos") if c98 else '<td class="n vazio">–</td>' * 3
        c2 = trio(m26.get(c26), k, "media_nao_reeleitos", "media_reeleitos")
        linhas.append(f'<tr><th scope="row">{NOMES_MEDIAS[var]}</th>{ca}{c1}{c2}</tr>')
    cab = "".join(f'<th scope="col" colspan="3">{t}</th>' for t in ("Artigo, 1998", "Nosso código, 1998", "Nosso código, 2026"))
    sub = '<th scope="col">Não reel.</th><th scope="col">Reel.</th><th scope="col">Z</th>' * 3
    return (f'<table class="larga"><thead><tr><th></th>{cab}</tr><tr><th scope="col">Variável</th>{sub}</tr></thead>'
            f'<tbody>{"".join(linhas)}</tbody></table>')


def secao_validacao():
    if not VAL.exists():
        return ""
    v = json.loads(VAL.read_text())

    def coefs(ano, var):
        m = v["modelos"][ano]
        if var == "rho":
            return f"ρ = {num(m['rho'], 2)}; LR p = {num(m['p_lr_rho0'], 3)}"
        out = []
        for eq, nome in (("seleção", "sel."), ("resultado", "res.")):
            c = next((c for c in m["coefs"] if c["equacao"] == eq and c["variavel"] == var), None)
            if c:
                out.append(f"{nome} {num(c['coef'], 2)}{estrelas(c['p']) or ' n.s.'}")
        return "; ".join(out)
    linhas = []
    for nome, var, artigo, tipo, texto in DIAG:
        cls, rotulo = ROT_DIAG[tipo]
        c98 = coefs("1998", var) if var else "–"
        c26 = coefs("2026", var) if var else "–"
        linhas.append(f'<tr><th scope="row">{esc(nome)}</th><td>{esc(artigo)}</td><td class="n">{esc(c98)}</td>'
                      f'<td class="n">{esc(c26)}</td><td><span class="chip {cls}">{rotulo}</span>'
                      f'<span class="ep">{esc(texto)}</span></td></tr>')
    a = v["amostra_1998"]
    return f"""<section aria-labelledby="s-val">
  <h2 id="s-val">Validação com os dados de 1998</h2>
  <p>Para separar falha de dados de mudança de cenário, o mesmo código foi aplicado à 50ª legislatura (1995-1999) e à
  eleição de 1998, o caso do artigo. A Câmara não tem votações nominais, Mesa, comissões nem lideranças antes de 2003,
  então o teste usa a estrutura da Tabela 6 do artigo só com as variáveis que existem nos dois períodos (Concentração,
  Histleg, Burocracia e Empresa só na seleção; MesmaBase só no resultado), estimada igual para 1998 e 2026.</p>
  <div class="numeros">
    <div class="numero"><b>{a['painel']}</b><span>deputados da 50ª legislatura</span></div>
    <div class="numero"><b>{a['analise']}</b><span>na análise de 1998</span></div>
    <div class="numero"><b>{a['concorreram']}</b><span>tentaram a reeleição (artigo: 446)</span></div>
    <div class="numero"><b>{a['reeleitos']}</b><span>se reelegeram (artigo: 288)</span></div>
  </div>
  <p class="nota">Taxa de sucesso: {num(100 * a['reeleitos'] / a['concorreram'], 1)}% nos nossos dados, 64,6% no artigo.
  Como no artigo, o TSE não tem votação por município do DF em 1998.</p>
  <div class="rolagem"><table class="larga"><thead><tr><th scope="col">Variável</th><th scope="col">Artigo (1998)</th>
  <th scope="col">Nosso código, 1998</th><th scope="col">Nosso código, 2026</th><th scope="col">Diagnóstico</th></tr></thead>
  <tbody>{"".join(linhas)}</tbody></table></div>
  <p class="nota">Coeficientes do probit com seleção reduzido (sel. = concorrer; res. = reeleger-se). Projetos aprovados
  de 1995-1998 usam a situação atual das proposições, por isso não servem de teste.</p>
  <h3>Médias de reeleitos e não reeleitos: Tabelas 2 e 3 do artigo, número a número</h3>
  <div class="rolagem">{tabela_medias_comparadas(v)}</div>
  <p class="nota">Valores do artigo transcritos de <code>dados/manual/artigo_1998_tabelas.csv</code>. Competição: o
  artigo não normaliza pelo eleitorado. Mesa, comissões e liderança usam escalas próprias em cada período, então só a
  direção é comparável. Na Tabela 1 do artigo, Concentração94 explica Concentração98 com coeficiente 0,77 e R² ajustado
  de 0,78; em 2026, Concentração 2022 explica a de 2026 com 0,80 e R² de 0,80.</p>
</section>"""


def secao_comparacao():
    """Artigo (Tabela 6) x 2026 (mesma especificação), equação a equação."""
    m = R["tabela6"]["artigo"]
    vars_ = []
    for c in ART6["coefs"]:
        if c["variavel"] != "const" and c["variavel"] not in vars_:
            vars_.append(c["variavel"])

    def f(c):
        return "–" if c is None else f"{num(c['coef'], 2)}{estrelas(c['p']) or ' n.s.'}"
    linhas = []
    for v in vars_:
        a_s, a_r = coef_de(ART6, "seleção", v), coef_de(ART6, "resultado", v)
        n_s, n_r = coef_de(m, "seleção", v), coef_de(m, "resultado", v)
        acordos = [x for x in (concorda(a_s, n_s), concorda(a_r, n_r)) if x is not None]
        ver = "confirma" if all(acordos) else ("diverge" if not any(acordos) else "parcial")
        linhas.append(f'<tr><th scope="row">{esc(rot(v))}</th><td class="n">{f(a_s)}</td><td class="n">{f(a_r)}</td>'
                      f'<td class="n">{f(n_s)}</td><td class="n">{f(n_r)}</td>'
                      f'<td><span class="chip {ver}">{ROTULO_VEREDITO[ver]}</span></td></tr>')
    linhas.append(f'<tr><th scope="row">ρ (LR, ρ = 0)</th><td class="n" colspan="2">{num(ART6["rho"], 2)} (p = '
                  f'{num(ART6["p_lr_rho0"], 3)})</td><td class="n" colspan="2">{num(m["rho"], 2)} (p = '
                  f'{num(m["p_lr_rho0"], 3)})</td><td><span class="chip parcial">Instável</span></td></tr>')
    return "\n".join(linhas)


def tabela_heck():
    specs = [("art1998", "Artigo, 1998"), ("artigo", "2026, especificação do artigo"),
             ("controles", "2026, com controles de mandato"), ("titulares", "2026, só titulares de fev/2023")]
    T6 = dict(R["tabela6"], art1998=ART6)
    ordem = []
    for eq in ("seleção", "resultado"):
        vs = []
        for k, _ in specs:
            for c in T6[k]["coefs"]:
                if c["equacao"] == eq and c["variavel"] not in vs:
                    vs.append(c["variavel"])
        vs = [v for v in vs if v != "const"] + ["const"]
        ordem.append((eq, vs))
    cab = "".join(f'<th scope="col" colspan="2">{esc(t)}</th>' for _, t in specs)
    sub = "".join('<th scope="col">Concorrer</th><th scope="col">Reeleger-se</th>' for _ in specs)
    todas = []
    for _, vs in ordem:
        for v in vs:
            if v not in todas:
                todas.append(v)
    corpo = []
    for v in todas:
        cels = "".join(celula(coef_de(T6[k], "seleção", v)) + celula(coef_de(T6[k], "resultado", v))
                       for k, _ in specs)
        corpo.append(f'<tr><th scope="row">{esc(rot(v))}</th>{cels}</tr>')
    rod = []
    for rotulo, f in (
        ("N (seleção / concorreram)", lambda m: f"{m['n']} / {m['n_selecionados']}"),
        ("Reeleitos", lambda m: f"{m['n_reeleitos']}"),
        ("ρ (IC 95%)", lambda m: f"{num(m['rho'], 2)} ({num(m['rho_ic95'][0], 2)}; {num(m['rho_ic95'][1], 2)})"),
        ("LR χ²(1) para ρ = 0", lambda m: f"{num(m['lr_rho0'], 2)}{estrelas(m['p_lr_rho0'])} (p = {num(m['p_lr_rho0'], 3)})"),
        ("Log-verossimilhança", lambda m: num(m["loglik"], 1)),
    ):
        cels = "".join(f'<td class="n" colspan="2">{esc(f(T6[k]))}</td>' for k, _ in specs)
        rod.append(f'<tr><th scope="row">{rotulo}</th>{cels}</tr>')
    return (f'<table class="larga t6"><thead><tr><th></th>{cab}</tr><tr><th scope="col">Variável</th>{sub}</tr></thead>'
            f'<tbody>{"".join(corpo)}</tbody><tfoot>{"".join(rod)}</tfoot></table>')


def tabela_perfil():
    specs = ["artigo", "controles", "titulares"]
    rhos = [x["rho"] for x in R["tabela6"]["artigo"]["perfil_rho"]]
    cab = "".join(f'<th scope="col">{num(r, 3)}</th>' for r in rhos)
    nomes = {"artigo": "Artigo", "controles": "Com controles", "titulares": "Titulares fev/2023"}
    corpo = []
    for k in specs:
        m = R["tabela6"][k]
        cels = "".join(f'<td class="n">{num(x["loglik"], 2)}</td>' for x in m["perfil_rho"])
        corpo.append(f'<tr><th scope="row">{nomes[k]}</th>{cels}<td class="n sig">{num(m["loglik"], 2)}</td></tr>')
    return (f'<table><thead><tr><th scope="col">ρ fixado em</th>{cab}<th scope="col">Máximo</th></tr></thead>'
            f'<tbody>{"".join(corpo)}</tbody></table>')


def tabela_probit():
    m = R["probit_simples"]
    corpo = []
    for c in m["coefs"]:
        if c["variavel"] == "const":
            continue
        corpo.append(f'<tr><th scope="row">{esc(rot(c["variavel"]))}</th>{celula(c)}<td class="n">{num(c["z"], 2)}</td></tr>')
    return (f'<table><thead><tr><th scope="col">Variável</th><th scope="col">Coeficiente (EP)</th>'
            f'<th scope="col">z</th></tr></thead><tbody>{"".join(corpo)}</tbody>'
            f'<tfoot><tr><th scope="row">N / pseudo-R²</th><td class="n" colspan="2">{m["n"]} / {num(m["pseudo_r2"], 3)}</td></tr></tfoot></table>')


def tabela1():
    deps = [("concentracao_2026", "Concentração 2026"), ("competicao_2026", "Competição 2026")]
    vs = []
    for x in R["tabela1"]:
        if x["variavel"] not in vs:
            vs.append(x["variavel"])
    vs = [v for v in vs if v != "const"] + ["const"]
    idx = {(x["dependente"], x["variavel"]): x for x in R["tabela1"]}
    corpo = []
    for v in vs:
        cels = "".join(celula(idx.get((d, v))) for d, _ in deps)
        corpo.append(f'<tr><th scope="row">{esc(rot(v))}</th>{cels}</tr>')
    rod = "".join(f'<td class="n">{idx[(d, "const")]["n"]} / {num(idx[(d, "const")]["r2"], 3)}</td>' for d, _ in deps)
    cab = "".join(f'<th scope="col">{t}</th>' for _, t in deps)
    return (f'<table><thead><tr><th scope="col">Variável</th>{cab}</tr></thead><tbody>{"".join(corpo)}</tbody>'
            f'<tfoot><tr><th scope="row">N / R²</th>{rod}</tr></tfoot></table>')


def tabela_medias(chave):
    corpo = []
    for x in R[chave]:
        s = estrelas(x["p"])
        corpo.append(
            f'<tr><th scope="row">{esc(rot(x["variavel"]))}</th>'
            f'<td class="n">{num(x["media_reeleitos"])}</td><td class="n">{num(x["dp_reeleitos"])}</td>'
            f'<td class="n">{num(x["media_nao_reeleitos"])}</td><td class="n">{num(x["dp_nao_reeleitos"])}</td>'
            f'<td class="n {"sig" if s else ""}">{num(x["z"], 2)}<sup>{s}</sup></td></tr>')
    n1 = R[chave][0]["n_reeleitos"]
    n2 = R[chave][0]["n_nao_reeleitos"]
    return (f'<table><thead><tr><th scope="col">Variável</th><th scope="col">Média reeleitos</th><th scope="col">DP</th>'
            f'<th scope="col">Média não reeleitos</th><th scope="col">DP</th><th scope="col">Z</th></tr></thead>'
            f'<tbody>{"".join(corpo)}</tbody><tfoot><tr><th scope="row">N</th><td class="n" colspan="2">{n1}</td>'
            f'<td class="n" colspan="2">{n2}</td><td></td></tr></tfoot></table>')


def tabela_gastos():
    corpo = []
    nomes = {"gastos_2026": "Gasto total (R$)", "gastos_por_eleitor_2026": "Gasto por eleitor apto da UF (R$)"}
    for x in R["tabelas4_5"]:
        d = 0 if x["variavel"] == "gastos_2026" else 3
        corpo.append(
            f'<tr><th scope="row">{nomes[x["variavel"]]}</th><td>{esc(x["grupo"])}</td>'
            f'<td class="n">{x["n"]}</td><td class="n">{num(100 * x["pct_declarou"], 1)}%</td>'
            f'<td class="n">{num(x["media"], d)}</td><td class="n">{num(x["mediana"], d)}</td>'
            f'<td class="n">{num(x["dp"], d)}</td><td class="n">{num(x["cv"], 2)}</td></tr>')
    return ('<table><thead><tr><th scope="col">Medida</th><th scope="col">Grupo</th><th scope="col">N</th>'
            '<th scope="col">Declarou</th><th scope="col">Média</th><th scope="col">Mediana</th>'
            '<th scope="col">Desvio-padrão</th><th scope="col">CV</th></tr></thead>'
            f'<tbody>{"".join(corpo)}</tbody></table>')


def amostra():
    a = R["amostra"]
    ex = "".join(f"<li>{esc(k)}: <strong>{v}</strong></li>" for k, v in a["exclusoes"].items() if v)
    cargos = "".join(f"<tr><td>{esc(k.capitalize())}</td><td class='n'>{v}</td></tr>"
                     for k, v in a["cargo_disputado"].items())
    return a, ex, cargos


a, ex, cargos = amostra()
art = R["tabela6"]["artigo"]

PAGINA = f"""<title>Reeleição na Câmara 2026</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: relatório de uma coluna, tabelas largas roláveis; verde-plenário como acento, neutros frios */
:root {{
  --bg: #f6f8f7; --surface: #ffffff; --fg: #17201d; --muted: #5a6762; --line: #d9e1de;
  --accent: #0b6b4c; --accent-soft: #e2f1eb;
  --ok: #1d7a4f; --ok-bg: #e3f3ea; --warn: #8a5a00; --warn-bg: #fbf0d9; --bad: #a3312b; --bad-bg: #f9e3e1;
  --display: "Space Grotesk", "Segoe UI", system-ui, sans-serif;
  --body: "Inter", "Segoe UI", system-ui, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #0f1513; --surface: #161e1b; --fg: #e4ebe8; --muted: #9aa8a2; --line: #2a3531;
  --accent: #5cc79c; --accent-soft: #173229;
  --ok: #6fd3a0; --ok-bg: #16301f; --warn: #e6b45c; --warn-bg: #33270f; --bad: #f08a82; --bad-bg: #3a1a18;
  color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #0f1513; --surface: #161e1b; --fg: #e4ebe8; --muted: #9aa8a2; --line: #2a3531;
  --accent: #5cc79c; --accent-soft: #173229;
  --ok: #6fd3a0; --ok-bg: #16301f; --warn: #e6b45c; --warn-bg: #33270f; --bad: #f08a82; --bad-bg: #3a1a18;
  color-scheme: dark; }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.6 var(--body); }}
.pagina {{ max-width: 1080px; margin: 0 auto; padding-block: 40px 72px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 48px; }}
header {{ display: grid; gap: 12px; }}
.sobre {{ font: 500 12px/1.4 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--accent); }}
h1 {{ font: 600 clamp(28px, 4.4vw, 42px)/1.12 var(--display); margin: 0; text-wrap: balance; }}
h2 {{ font: 600 22px/1.25 var(--display); margin: 0; text-wrap: balance; }}
h3 {{ font: 600 16px/1.3 var(--display); margin: 0; }}
p {{ margin: 0; max-width: 68ch; }}
.lead {{ font-size: 17px; color: var(--muted); }}
section {{ display: grid; gap: 16px; min-width: 0; }}
.ref {{ font-size: 13px; color: var(--muted); }}
.numeros {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }}
.numero {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; display: grid; gap: 2px; }}
.numero b {{ font: 600 26px/1.1 var(--display); font-variant-numeric: tabular-nums; }}
.numero span {{ font-size: 13px; color: var(--muted); }}
.achados {{ margin: 0; padding-left: 20px; display: grid; gap: 8px; max-width: 72ch; }}
.rolagem {{ overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; }}
th, td {{ padding: 7px 12px; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); }}
thead th {{ font: 600 12px/1.3 var(--body); color: var(--muted); letter-spacing: .02em; background: var(--bg); white-space: nowrap; }}
tbody th {{ font-weight: 500; white-space: nowrap; }}
tfoot th, tfoot td {{ background: var(--bg); font-size: 12.5px; }}
td.n {{ font: 13px/1.5 var(--mono); font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }}
td.n.sig {{ color: var(--accent); font-weight: 500; }}
td.vazio {{ color: var(--muted); }}
sup {{ font-size: 10px; margin-left: 1px; }}
.ep {{ display: block; color: var(--muted); font-size: 11.5px; font-weight: 400; }}
table.larga {{ min-width: 860px; }}
table.t6 {{ min-width: 1100px; }}
.comparacao td:nth-child(2), .comparacao td:nth-child(3) {{ min-width: 220px; }}
.chip {{ display: inline-block; font: 600 11.5px/1 var(--body); padding: 5px 9px; border-radius: 999px; white-space: nowrap; }}
.chip.confirma {{ color: var(--ok); background: var(--ok-bg); }}
.chip.parcial {{ color: var(--warn); background: var(--warn-bg); }}
.chip.diverge {{ color: var(--bad); background: var(--bad-bg); }}
.duas {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }}
.duas > * {{ min-width: 0; display: grid; gap: 10px; align-content: start; }}
.nota {{ font-size: 13px; color: var(--muted); max-width: 80ch; }}
.aviso {{ background: var(--warn-bg); color: var(--fg); border-radius: 8px; padding: 14px 16px; font-size: 14px; display: grid; gap: 6px; }}
.aviso strong {{ color: var(--warn); }}
ul.lista {{ margin: 0; padding-left: 20px; display: grid; gap: 4px; }}
code {{ font: 12.5px var(--mono); background: var(--accent-soft); padding: 1px 5px; border-radius: 4px; }}
a {{ color: var(--accent); }}
a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
</style>

<div class="pagina">
<header>
  <div class="sobre">Replicação · 57ª legislatura · eleição de 4/10/2026</div>
  <h1>O que é que o reeleito tem, em 2026?</h1>
  <p class="lead">Os modelos de Pereira &amp; Rennó (2001) para a eleição de 1998, reestimados para os deputados federais
  que exerceram mandato entre 2023 e 2026. As variáveis de emendas orçamentárias (Emendas, Pork, MédiaExecução)
  ficaram de fora desta versão.</p>
  <p class="ref">Pereira, C. &amp; Rennó, L. (2001). O que é que o reeleito tem? Dinâmicas político-institucionais locais
  e nacionais nas eleições de 1998 para a Câmara dos Deputados. <i>Dados</i>, 44(2).
  Dados: API e arquivos da Câmara dos Deputados, TSE (2022 e 2026), gabinetes do Ipea, ideologia de Bolognesi, Codato, Ribeiro &amp; Silva (2025, onda de 2022).</p>
</header>

<section aria-labelledby="s-amostra">
  <h2 id="s-amostra">Amostra</h2>
  <div class="numeros">
    <div class="numero"><b>{a['painel']}</b><span>deputados que exerceram mandato</span></div>
    <div class="numero"><b>{a['analise']}</b><span>na análise, após exclusões</span></div>
    <div class="numero"><b>{a['concorreram']}</b><span>tentaram a reeleição</span></div>
    <div class="numero"><b>{a['reeleitos']}</b><span>se reelegeram</span></div>
  </div>
  <div class="duas">
    <div><h3>Exclusões (nota 17 do artigo)</h3><ul class="lista">{ex}</ul>
    <p class="nota">Titulares e suplentes entram juntos, como no artigo. A variável Líder (listas de influentes) não
    foi coletada; no artigo ela é endógena e fica fora do modelo principal.</p></div>
    <div><h3>O que disputaram em 2026</h3><div class="rolagem"><table><tbody>{cargos}</tbody></table></div></div>
  </div>
</section>

<section aria-labelledby="s-comp">
  <h2 id="s-comp">Comparação com 1998</h2>
  <p>Coeficientes da Tabela 6 do artigo e do mesmo modelo estimado para 2026, sem as variáveis de emendas
  (* p&lt;0,10, ** p&lt;0,05, *** p&lt;0,01). Seleção = concorrer à reeleição; resultado = reeleger-se. "Confirma"
  quando as duas equações têm a mesma leitura (ambas não significativas, ou significativas com o mesmo sinal).
  Concentração em proporção aqui e em pontos percentuais no artigo.</p>
  <div class="rolagem"><table class="larga"><thead><tr><th scope="col">Variável</th>
  <th scope="col">Artigo: seleção</th><th scope="col">Artigo: resultado</th><th scope="col">2026: seleção</th>
  <th scope="col">2026: resultado</th><th scope="col">Leitura</th></tr></thead>
  <tbody>{secao_comparacao()}</tbody></table></div>
  <ul class="achados">
    <li><strong>Confirmado em 2026:</strong> cargos na hierarquia do partido (Partpos) e em comissões permanentes
    aumentam a chance de concorrer, e Partpos também a de se reeleger; lealdade ao governo (Índice) aumenta a chance
    de concorrer; Projetos, Governador, Especial e EntrarCoalizão não têm efeito; Histexec reduz a chance de
    concorrer.</li>
    <li><strong>Mudou em 2026</strong> (a validação com 1998 reproduz o artigo com o mesmo código, então a diferença
    é do período): quem concentrou votos em 2022 tem menos chance de concorrer, quando em 1998 tinha mais; Histexec
    passa a aumentar a chance de reeleição, quando em 1998 reduzia; SairCoalizão deixa de punir; Senior passa a
    reduzir a chance de concorrer; manter a mesma base municipal passa a reduzir a chance de reeleição.</li>
    <li><strong>Diferenças sem teste com 1998</strong> (sem votos nominais nem cargos da época na API): Ausência reduz
    a chance de concorrer, não a de se reeleger; Índice reduz a chance de reeleição; Mesa a aumenta.</li>
    <li><strong>ρ não é estável.</strong> No artigo ρ ≈ 0,58 com z = 1,11. Nas nossas estimativas ele vai a um dos
    limites (−1 em 2026; +1 na validação de 1998) conforme a especificação. Em 2026 a Concentração tem efeito direto
    forte na reeleição; deixá-la só na seleção, como o artigo, joga esse efeito em ρ. Os coeficientes do probit simples
    (nota 24) confirmam as leituras acima.</li>
  </ul>
</section>

{secao_validacao()}

<section aria-labelledby="s-t6">
  <h2 id="s-t6">Tabela 6 · Probit com seleção de Heckman</h2>
  <p>Equação de seleção: o deputado concorre a deputado federal em 2026. Equação de resultado: é reeleito, dado que
  concorreu. Como na Tabela 6 do artigo: Concentração da eleição anterior, Histleg, Burocracia e Empresa só na seleção;
  MesmaBase só no resultado; Direita é a referência da ideologia. Coeficientes com erro-padrão entre parênteses (no
  artigo, calculado a partir do z publicado). Ausência em proporção das votações.</p>
  <div class="rolagem">{tabela_heck()}</div>
  <div class="aviso"><strong>ρ no limite do intervalo</strong>
  <p>Na especificação do artigo, a verossimilhança de 2026 cresce em direção a ρ = −1 (tabela abaixo). A Concentração
  2022 entra só na seleção, como no artigo, mas em 2026 ela tem efeito direto forte sobre a reeleição; esse efeito
  passa para ρ. Os erros-padrão na fronteira são pouco confiáveis, por isso o probit simples (nota 24) é o teste de
  robustez mais importante.</p></div>
  <div class="rolagem">{tabela_perfil()}</div>
</section>

<section aria-labelledby="s-p">
  <h2 id="s-p">Probit simples de reeleição (nota 24)</h2>
  <p>Só entre os {R['probit_simples']['n']} que concorreram, mesmas variáveis da equação de resultado.</p>
  <div class="rolagem">{tabela_probit()}</div>
</section>

<section aria-labelledby="s-t1">
  <h2 id="s-t1">Tabela 1 · Endogeneidade da distribuição de votos</h2>
  <p>MQO com erros robustos, entre os que concorreram. Como no artigo, a concentração de 2026 é explicada pela de 2022
  e pela atuação no mandato (projetos e ausência reduzem a concentração), por isso Concentração e Competição de 2026
  ficam fora do modelo principal. A competição de 2026 é pouco explicada (R² baixo).</p>
  <div class="rolagem">{tabela1()}</div>
</section>

<section aria-labelledby="s-t23">
  <h2 id="s-t23">Tabelas 2 e 3 · Diferença de médias entre reeleitos e não reeleitos</h2>
  <p>Teste Z para a diferença de médias, entre os que concorreram (nota 20 do artigo).</p>
  <h3>Variáveis locais</h3>
  <div class="rolagem">{tabela_medias("tabela2")}</div>
  <h3>Variáveis nacionais</h3>
  <div class="rolagem">{tabela_medias("tabela3")}</div>
</section>

<section aria-labelledby="s-t45">
  <h2 id="s-t45">Tabelas 4 e 5 · Gastos de campanha</h2>
  <p>Despesas contratadas declaradas ao TSE em 2026. Estatísticas sobre quem declarou gasto. Como no artigo, os gastos
  ficam fora do modelo multivariado. Diferente de 1998, quase todos declararam.</p>
  <div class="rolagem">{tabela_gastos()}</div>
</section>

<section aria-labelledby="s-notas">
  <h2 id="s-notas">Notas de método</h2>
  <ul class="lista nota">
    <li>Concentração e MesmaBase usam a eleição de 2022 como "eleição anterior"; Concentração e Competição de 2026
    são endógenas (Tabela 1) e só entram nos testes de médias.</li>
    <li>Atuação na Câmara (ausência, índice, projetos, cargos) medida até a véspera da eleição.</li>
    <li>Coalizão: partidos com ministério no gabinete vigente (Ipea); o último gabinete da planilha é o Lula 3-4 (abr/2024).</li>
    <li>Ideologia: nota média dos especialistas (onda 2022); Esquerda é a categoria de referência.</li>
    <li>Amapá: eleito/suplente vem da página de resultados do TSE, porque os arquivos oficiais ainda não trazem a
    totalização proporcional do estado.</li>
    <li>O probit com seleção foi estimado por máxima verossimilhança (equivalente ao <code>heckprobit</code> do Stata).
    Código: <code>replicar_artigo.py</code>; dicionário das variáveis: <code>DICIONARIO_REELEICAO.md</code>.</li>
  </ul>
</section>
</div>
"""

SAIDA.write_text(PAGINA, encoding="utf-8")
print(f"página gravada em {SAIDA}")
