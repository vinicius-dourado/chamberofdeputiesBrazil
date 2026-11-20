"""Gera a página HTML a partir da validação com 1998 e da replicação de 2026.

Uso: python validar_1998.py && python replicar_artigo.py && python gerar_relatorio.py
Saída: resultados/replicacao/relatorio.html
"""
import csv
import html
import json
import math
from pathlib import Path

from replicar_artigo import PARA_2026

V = json.loads(Path("resultados/validacao_1998/variaveis_validadas.json").read_text())
R = json.loads(Path("resultados/replicacao/resultados.json").read_text())
SAIDA = Path("resultados/replicacao/relatorio.html")
M = Path("dados/manual")


def ler_csv(nome):
    linhas = [l for l in (M / nome).read_text().splitlines() if not l.startswith("#")]
    return list(csv.DictReader(linhas, delimiter=";"))


ART_MED = {r["variavel"]: r for r in ler_csv("artigo_1998_tabelas.csv")}
ART_T6 = {(r["equacao"], r["variavel"]): r for r in ler_csv("artigo_1998_tabela6.csv")}
NOME_ART = {"concentracao_ant": ("concentracao_94", "concentracao"), "concentracao_atual": ("concentracao_98", None),
            "competicao_atual": ("competicao", None), "mesma_base": ("mesma_base", "mesma_base"),
            "senior": (None, "senior"), "histleg": ("histleg", "histleg"), "histexec": ("histexec", "histexec"),
            "sair_coalizao": ("sair_coalizao", "sair_coalizao")}
ROT = {"concentracao_ant": "Concentração da eleição anterior (94 / 2022)",
       "concentracao_atual": "Concentração da eleição atual (98 / 2026)",
       "competicao_atual": "Competição no reduto", "mesma_base": "MesmaBase", "senior": "Senior",
       "histleg": "Histleg", "histexec": "Histexec", "sair_coalizao": "SairCoalizão", "governador": "Governador",
       "projetos": "Projetos", "burocracia": "Burocracia", "empresa": "Empresa", "entrar_coalizao": "EntrarCoalizão",
       "ideologia": "Esquerda / Centro", "const": "Constante"}
ROT_26 = {PARA_2026[k]: v for k, v in ROT.items() if k in PARA_2026}
ROT_26["const"] = "Constante"


def esc(x):
    return html.escape(str(x))


def estrelas(p):
    return "" if p is None or (isinstance(p, float) and math.isnan(p)) else (
        "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else "")


def num(x, d=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def p_z(z):
    return math.erfc(abs(z) / math.sqrt(2))


def leitura(coef, p):
    return ("+" if coef > 0 else "−") if p < 0.10 else "n.s."


def fmt(coef, p, d=2):
    return f"{num(coef, d)}<sup>{estrelas(p)}</sup>" if coef is not None else "–"


def coef(lista, eq, var):
    return next((c for c in lista if c.get("equacao") == eq and c["variavel"] == var), None)


# ------------------------------------------------------------------------- dados por estatística
def estatisticas(v):
    """Para uma variável aprovada: [(estatística, artigo(coef,p), nosso1998(coef,p), 2026(coef,p))]."""
    med, t6 = NOME_ART[v]
    v26 = PARA_2026[v]
    out = []
    if med:
        za = float(ART_MED[med]["z"])
        z98 = next((c["nosso_1998"] for c in V["checagens_finais"] if c["variavel"] == v
                    and c["estatistica"].startswith("Tabela 2/3")), None)
        z26 = next((r["z"] for r in R["tabelas2_3"] if r["variavel"] == v26), None)
        out.append(("Médias: Z (reeleitos − não reeleitos)", (za, p_z(za)),
                    (z98, p_z(z98)) if z98 is not None else None, (z26, p_z(z26)) if z26 is not None else None))
    if t6:
        for eq, nome in (("seleção", "Tabela 6: concorrer"), ("resultado", "Tabela 6: reeleger-se")):
            a = ART_T6.get((eq, t6))
            if not a:
                continue
            c98 = coef(V["modelo_1998"]["coefs"], eq, v)
            c26 = coef(R["tabela6"]["coefs"], eq, v26)
            out.append((nome, (float(a["coef"]), float(a["p"])), (c98["coef"], c98["p"]) if c98 else None,
                        (c26["coef"], c26["p"]) if c26 else None))
    if v == "concentracao_ant":
        t98 = V["tabela1_1998"]
        c26 = coef(R["tabela1"], None, "concentracao_2022") or next(r for r in R["tabela1"] if r["variavel"] == "concentracao_2022")
        out.append(("Tabela 1: explica a concentração atual", (0.77, 0.0005), (t98["coef"], t98["p"]),
                    (c26["coef"], c26["p"])))
    return out


def secao_status():
    linhas = []
    for v in V["aprovadas"]:
        n = len([c for c in V["checagens_finais"] if c["variavel"] == v])
        n = n + (1 if v == "concentracao_ant" else 0)
        linhas.append((ROT[v], "confirma", "Aprovada", f"{n} estatística(s) do artigo reproduzida(s) com os dados de 1998"))
    for v, falhas in V["reprovadas"].items():
        txt = "; ".join(f'{f["estatistica"]}: artigo {f["leitura_artigo"]}, nosso 1998 {f["leitura_nossa"]}'
                        for f in falhas)
        linhas.append((ROT.get(v, v), "diverge", "Reprovada", txt))
    nomes_sem = {"ausencia": "Ausência", "indice": "Índice", "mesa": "Mesa", "permanente": "Permanente",
                 "especial": "Especial", "partpos": "Partpos (Partido)", "lider": "Líder", "gastos": "Gastos"}
    for v, motivo in V["sem_dados_1998"].items():
        linhas.append((nomes_sem[v], "parcial", "Sem dados de 1998", motivo))
    linhas.append(("Emendas, Pork, MédiaExecução", "parcial", "Fora do escopo", "variáveis de emendas orçamentárias"))
    return "".join(f'<tr><th scope="row">{esc(a)}</th><td><span class="chip {c}">{b}</span></td><td>{esc(d)}</td></tr>'
                   for a, c, b, d in linhas)


def secao_comparativo():
    linhas, mudou, igual = [], [], []
    for v in V["aprovadas"]:
        for i, (nome, art, n98, n26) in enumerate(estatisticas(v)):
            la = leitura(*art)
            l26 = leitura(*n26) if n26 else "–"
            ok = la == l26
            (igual if ok else mudou).append((v, nome, la, l26))
            primeira = f'<th scope="row" rowspan="{len(estatisticas(v))}">{esc(ROT[v])}</th>' if i == 0 else ""
            linhas.append(f'<tr>{primeira}<td>{esc(nome)}</td><td class="n">{fmt(*art)}</td>'
                          f'<td class="n">{fmt(*n98) if n98 else "–"}</td><td class="n">{fmt(*n26) if n26 else "–"}</td>'
                          f'<td><span class="chip {"confirma" if ok else "diverge"}">{"Igual" if ok else "Mudou"}</span></td></tr>')
    m98, m26 = V["modelo_1998"], R["tabela6"]
    linhas.append(f'<tr><th scope="row">ρ (correlação das equações)</th><td>LR, ρ = 0</td>'
                  f'<td class="n">0,58 (p = 0,29)</td><td class="n">{num(m98["rho"])} (p = {num(m98["p_lr_rho0"], 3)})</td>'
                  f'<td class="n">{num(m26["rho"])} (p = {num(m26["p_lr_rho0"], 3)})</td>'
                  f'<td><span class="chip parcial">Não validado</span></td></tr>')
    return "".join(linhas), igual, mudou


def tabela6():
    vars_ = []
    for c in R["tabela6"]["coefs"]:
        if c["variavel"] not in vars_:
            vars_.append(c["variavel"])
    vars_ = [x for x in vars_ if x != "const"] + ["const"]
    inv = {v26: v for v, v26 in PARA_2026.items()}
    linhas = []

    def cel(c):
        if c is None:
            return '<td class="n vazio">–</td>'
        return f'<td class="n{" sig" if estrelas(c[1]) else ""}">{fmt(c[0], c[1], 3)}</td>'
    for v26 in vars_:
        v = inv.get(v26, v26)
        nome_t6 = NOME_ART.get(v, (None, "const"))[1] if v != "const" else "const"
        cels = ""
        for eq in ("seleção", "resultado"):
            a = ART_T6.get((eq, nome_t6))
            c98 = coef(V["modelo_1998"]["coefs"], eq, v)
            c26 = coef(R["tabela6"]["coefs"], eq, v26)
            cels += cel((float(a["coef"]), float(a["p"])) if a else None) + cel((c98["coef"], c98["p"]) if c98 else None) \
                + cel((c26["coef"], c26["p"]) if c26 else None)
        linhas.append(f'<tr><th scope="row">{esc(ROT_26.get(v26, v26))}</th>{cels}</tr>')
    m98, m26 = V["modelo_1998"], R["tabela6"]
    rod = (f'<tr><th scope="row">N / concorreram</th><td class="n" colspan="2">536 / 430 (artigo)</td>'
           f'<td class="n" colspan="2">{m98["n"]} / {m98["n_selecionados"]} (1998)</td>'
           f'<td class="n" colspan="2">{m26["n"]} / {m26["n_selecionados"]} (2026)</td></tr>')
    cab = ('<tr><th></th><th scope="col" colspan="3">Concorrer à reeleição</th><th scope="col" colspan="3">Reeleger-se</th></tr>'
           '<tr><th scope="col">Variável</th>' + '<th scope="col">Artigo 1998</th><th scope="col">Nosso 1998</th>'
           '<th scope="col">2026</th>' * 2 + '</tr>')
    return (f'<table class="larga"><thead>{cab}</thead><tbody>{"".join(linhas)}</tbody>'
            f'<tfoot>{rod}</tfoot></table>')


def tabela_medias():
    linhas = []
    for v in V["aprovadas"]:
        med = NOME_ART[v][0]
        if not med:
            continue
        a = ART_MED[med]
        k = 100 if "concentracao" in v else 1
        c98 = next((r for r in V.get("medias_1998", []) if r["variavel"] == v), None)
        r26 = next((r for r in R["tabelas2_3"] if r["variavel"] == PARA_2026[v]), None)
        linhas.append(f'<tr><th scope="row">{esc(ROT[v])}</th>'
                      f'<td class="n">{num(float(a["media_nao_reeleitos"]))}</td><td class="n">{num(float(a["media_reeleitos"]))}</td>'
                      f'<td class="n">{num(k * r26["media_nao_reeleitos"]) if r26 else "–"}</td>'
                      f'<td class="n">{num(k * r26["media_reeleitos"]) if r26 else "–"}</td></tr>')
    return ('<table><thead><tr><th scope="col">Variável</th><th scope="col">Artigo: não reeleitos</th>'
            '<th scope="col">Artigo: reeleitos</th><th scope="col">2026: não reeleitos</th><th scope="col">2026: reeleitos</th>'
            f'</tr></thead><tbody>{"".join(linhas)}</tbody></table>')


def tabela_probit():
    linhas = "".join(
        f'<tr><th scope="row">{esc(ROT_26.get(c["variavel"], c["variavel"]))}</th>'
        f'<td class="n{" sig" if estrelas(c["p"]) else ""}">{fmt(c["coef"], c["p"], 3)}<span class="ep">({num(c["ep"], 3)})</span></td></tr>'
        for c in R["probit_simples"]["coefs"] if c["variavel"] != "const")
    return (f'<table><thead><tr><th scope="col">Variável</th><th scope="col">Coeficiente (EP)</th></tr></thead>'
            f'<tbody>{linhas}</tbody><tfoot><tr><th scope="row">N</th><td class="n">{R["probit_simples"]["n"]}</td></tr></tfoot></table>')


def frase(v, nome, l):
    if nome.startswith("Médias"):
        return {"+": "maior entre os reeleitos", "−": "menor entre os reeleitos", "n.s.": "igual entre reeleitos e não reeleitos"}[l]
    if "concorrer" in nome:
        return {"+": "aumenta a chance de concorrer", "−": "reduz a chance de concorrer", "n.s.": "não afeta a decisão de concorrer"}[l]
    if "reeleger" in nome:
        return {"+": "aumenta a chance de se reeleger", "−": "reduz a chance de se reeleger", "n.s.": "não afeta a reeleição"}[l]
    return {"+": "explica positivamente a concentração atual", "−": "explica negativamente", "n.s.": "não explica"}[l]


comp, IGUAL, MUDOU = secao_comparativo()
a26, a98 = R["amostra"], V["amostra_1998"]
li_mudou = "".join(f"<li><strong>{esc(ROT[v])}</strong>: em 1998 {frase(v, n, la)}; em 2026 {frase(v, n, l26)}.</li>"
                   for v, n, la, l26 in MUDOU)
CURTO = lambda n: "teste de médias" if n.startswith("Médias") else n.split(":")[0]  # noqa: E731
li_igual = "".join(f"<li><strong>{esc(ROT[v])}</strong>: {frase(v, n, la)} nos dois períodos ({esc(CURTO(n))}).</li>"
                   for v, n, la, l26 in IGUAL)
excl = "".join(f"<li>{esc(k)}: <strong>{v}</strong></li>" for k, v in a26["exclusoes"].items() if v)
t1_26 = next(r for r in R["tabela1"] if r["variavel"] == "concentracao_2022")

PAGINA = """<title>Reeleição na Câmara 2026</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: relatório de uma coluna, tabelas largas roláveis; verde-plenário como acento, neutros frios */
""" + ':root {\n  --bg: #f6f8f7; --surface: #ffffff; --fg: #17201d; --muted: #5a6762; --line: #d9e1de;\n  --accent: #0b6b4c; --accent-soft: #e2f1eb;\n  --ok: #1d7a4f; --ok-bg: #e3f3ea; --warn: #8a5a00; --warn-bg: #fbf0d9; --bad: #a3312b; --bad-bg: #f9e3e1;\n  --display: "Space Grotesk", "Segoe UI", system-ui, sans-serif;\n  --body: "Inter", "Segoe UI", system-ui, sans-serif;\n  --mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;\n}\n@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {\n  --bg: #0f1513; --surface: #161e1b; --fg: #e4ebe8; --muted: #9aa8a2; --line: #2a3531;\n  --accent: #5cc79c; --accent-soft: #173229;\n  --ok: #6fd3a0; --ok-bg: #16301f; --warn: #e6b45c; --warn-bg: #33270f; --bad: #f08a82; --bad-bg: #3a1a18;\n  color-scheme: dark; } }\n:root[data-theme="dark"] {\n  --bg: #0f1513; --surface: #161e1b; --fg: #e4ebe8; --muted: #9aa8a2; --line: #2a3531;\n  --accent: #5cc79c; --accent-soft: #173229;\n  --ok: #6fd3a0; --ok-bg: #16301f; --warn: #e6b45c; --warn-bg: #33270f; --bad: #f08a82; --bad-bg: #3a1a18;\n  color-scheme: dark; }\nbody { background: var(--bg); color: var(--fg); font: 15px/1.6 var(--body); }\n.pagina { max-width: 1080px; margin: 0 auto; padding-block: 40px 72px;\n  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));\n  display: grid; gap: 48px; }\nheader { display: grid; gap: 12px; }\n.sobre { font: 500 12px/1.4 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--accent); }\nh1 { font: 600 clamp(28px, 4.4vw, 42px)/1.12 var(--display); margin: 0; text-wrap: balance; }\nh2 { font: 600 22px/1.25 var(--display); margin: 0; text-wrap: balance; }\nh3 { font: 600 16px/1.3 var(--display); margin: 0; }\np { margin: 0; max-width: 68ch; }\n.lead { font-size: 17px; color: var(--muted); }\nsection { display: grid; gap: 16px; min-width: 0; }\n.ref { font-size: 13px; color: var(--muted); }\n.numeros { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }\n.numero { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; display: grid; gap: 2px; }\n.numero b { font: 600 26px/1.1 var(--display); font-variant-numeric: tabular-nums; }\n.numero span { font-size: 13px; color: var(--muted); }\n.achados { margin: 0; padding-left: 20px; display: grid; gap: 8px; max-width: 72ch; }\n.rolagem { overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; }\ntable { border-collapse: collapse; width: 100%; font-size: 13.5px; }\nth, td { padding: 7px 12px; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); }\nthead th { font: 600 12px/1.3 var(--body); color: var(--muted); letter-spacing: .02em; background: var(--bg); white-space: nowrap; }\ntbody th { font-weight: 500; white-space: nowrap; }\ntfoot th, tfoot td { background: var(--bg); font-size: 12.5px; }\ntd.n { font: 13px/1.5 var(--mono); font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }\ntd.n.sig { color: var(--accent); font-weight: 500; }\ntd.vazio { color: var(--muted); }\nsup { font-size: 10px; margin-left: 1px; }\n.ep { display: block; color: var(--muted); font-size: 11.5px; font-weight: 400; }\ntable.larga { min-width: 860px; }\ntable.t6 { min-width: 1100px; }\n.comparacao td:nth-child(2), .comparacao td:nth-child(3) { min-width: 220px; }\n.chip { display: inline-block; font: 600 11.5px/1 var(--body); padding: 5px 9px; border-radius: 999px; white-space: nowrap; }\n.chip.confirma { color: var(--ok); background: var(--ok-bg); }\n.chip.parcial { color: var(--warn); background: var(--warn-bg); }\n.chip.diverge { color: var(--bad); background: var(--bad-bg); }\n.duas { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }\n.duas > * { min-width: 0; display: grid; gap: 10px; align-content: start; }\n.nota { font-size: 13px; color: var(--muted); max-width: 80ch; }\n.aviso { background: var(--warn-bg); color: var(--fg); border-radius: 8px; padding: 14px 16px; font-size: 14px; display: grid; gap: 6px; }\n.aviso strong { color: var(--warn); }\nul.lista { margin: 0; padding-left: 20px; display: grid; gap: 4px; }\ncode { font: 12.5px var(--mono); background: var(--accent-soft); padding: 1px 5px; border-radius: 4px; }\na { color: var(--accent); }\na:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }' + """
tbody th[rowspan] { vertical-align: top; }
</style>
""" + f"""
<div class="pagina">
<header>
  <div class="sobre">Replicação validada · eleições de 1998 e 2026</div>
  <h1>O que é que o reeleito tem, em 2026?</h1>
  <p class="lead">Pereira &amp; Rennó (2001) explicaram a reeleição para a Câmara em 1998. Aqui, o mesmo modelo é
  aplicado à eleição de 2026, mas só com as variáveis que passaram por uma validação: com os dados de 1994 e 1998,
  o nosso cálculo precisa chegar ao mesmo resultado do artigo.</p>
  <p class="ref">Pereira, C. &amp; Rennó, L. (2001). O que é que o reeleito tem? Dinâmicas político-institucionais locais
  e nacionais nas eleições de 1998 para a Câmara dos Deputados. <i>Dados</i>, 44(2). Dados: TSE (1994, 1998, 2022,
  2026), API e arquivos da Câmara dos Deputados, gabinetes do Ipea.</p>
</header>

<section aria-labelledby="s-val">
  <h2 id="s-val">1. Validação com 1998</h2>
  <p>Regra: uma variável segue para 2026 só se, com os dados de 1994/1998, o nosso cálculo chega ao mesmo resultado
  do artigo (mesmo sinal e mesma significância a 10%) em todas as estatísticas que o artigo publica para ela
  (Tabelas 1, 2, 3 e 6). Variáveis sem dados de 1998 ficam de fora. Como a Tabela 6 é um modelo conjunto, ela foi
  reestimada sem as reprovadas até nenhuma falhar ({len(V["rodadas"])} rodadas).</p>
  <div class="numeros">
    <div class="numero"><b>{a98["concorreram"]}</b><span>concorreram em 1998, nossos dados (artigo: 446)</span></div>
    <div class="numero"><b>{a98["reeleitos"]}</b><span>reeleitos em 1998, nossos dados (artigo: 288)</span></div>
    <div class="numero"><b>{len(V["aprovadas"])}</b><span>variáveis aprovadas</span></div>
    <div class="numero"><b>{len(V["reprovadas"]) + len(V["sem_dados_1998"])}</b><span>variáveis fora</span></div>
  </div>
  <div class="rolagem"><table class="larga"><thead><tr><th scope="col">Variável do artigo</th><th scope="col">Situação</th>
  <th scope="col">Motivo</th></tr></thead><tbody>{secao_status()}</tbody></table></div>
  <p class="nota">Reprovadas costumam ter um limite da fonte de 1998: Projetos usa a situação atual das proposições;
  a ideologia vem do survey de 2018; a composição das coligações de 1994 é incompleta; Burocracia, Empresa e
  EntrarCoalizão não têm a mesma definição do artigo. A correlação entre as equações da Tabela 6 (ρ) também não
  reproduz o artigo em 1998 e não é interpretada.</p>
</section>

<section aria-labelledby="s-comp">
  <h2 id="s-comp">2. Comparativo 1998 × 2026</h2>
  <p>Só variáveis aprovadas. Para cada estatística: o valor do artigo, o nosso cálculo para 1998 (que reproduz o artigo)
  e o mesmo cálculo para 2026. "Mudou" quando a leitura de 2026 (sinal e significância) difere da do artigo.
  Coeficientes da Tabela 6 com seleção de Heckman; * p&lt;0,10, ** p&lt;0,05, *** p&lt;0,01. Concentração em pontos
  percentuais no artigo e em proporção nos nossos cálculos.</p>
  <div class="rolagem"><table class="larga"><thead><tr><th scope="col">Variável</th><th scope="col">Estatística</th>
  <th scope="col">Artigo 1998</th><th scope="col">Nosso 1998</th><th scope="col">2026</th><th scope="col">Leitura</th>
  </tr></thead><tbody>{comp}</tbody></table></div>
  <div class="duas">
    <div><h3>O que mudou em 2026</h3><ul class="achados">{li_mudou}</ul></div>
    <div><h3>O que se mantém</h3><ul class="achados">{li_igual}</ul></div>
  </div>
</section>

<section aria-labelledby="s-t6">
  <h2 id="s-t6">3. Tabela 6 com as variáveis aprovadas</h2>
  <p>Mesmo modelo nas três colunas: Concentração da eleição anterior e Histleg só na equação de concorrer; MesmaBase
  só na de reeleger-se. Os coeficientes do artigo vêm do modelo completo, com as variáveis que aqui ficaram de fora.</p>
  <div class="rolagem">{tabela6()}</div>
  <h3>Probit simples de reeleição em 2026 (nota 24 do artigo)</h3>
  <p class="nota">Sem a equação de seleção, entre os que concorreram. Confirma as leituras da equação de reeleger-se.</p>
  <div class="rolagem">{tabela_probit()}</div>
</section>

<section aria-labelledby="s-t1">
  <h2 id="s-t1">4. Tabela 1: a concentração de votos se repete</h2>
  <p>No artigo, a concentração de 1994 explica a de 1998 com coeficiente 0,77 (R² ajustado 0,78). Nos nossos dados,
  {num(V["tabela1_1998"]["coef"])} em 1998 (R² ajustado {num(V["tabela1_1998"]["r2_ajustado"])}) e
  {num(t1_26["coef"])} entre 2022 e 2026 (R² ajustado {num(t1_26["r2_ajustado"])}). A equação de Competição da
  Tabela 1 ficou de fora: nenhum dos regressores dela foi aprovado.</p>
</section>

<section aria-labelledby="s-t23">
  <h2 id="s-t23">5. Médias de reeleitos e não reeleitos</h2>
  <div class="rolagem">{tabela_medias()}</div>
  <p class="nota">Competição: o artigo e nós ponderamos de forma diferente, por isso só a direção é comparável.</p>
</section>

<section aria-labelledby="s-notas">
  <h2 id="s-notas">Amostra e notas</h2>
  <ul class="lista nota">
    <li>2026: {a26["painel"]} deputados que exerceram mandato na 57ª legislatura; {a26["analise"]} na análise;
    {a26["concorreram"]} concorreram à reeleição e {a26["reeleitos"]} se reelegeram. Exclusões (nota 17 do artigo):</li>
    {excl}
    <li>1998: {a98["painel"]} deputados da 50ª legislatura; {a98["analise"]} na análise.</li>
    <li>SairCoalizão: partidos com ministério no gabinete vigente (Ipea); a planilha termina em abr/2024.</li>
    <li>Amapá 2026: eleito/suplente pela página de resultados do TSE (totalização ainda não publicada nos arquivos).</li>
    <li>Código: <code>validar_1998.py</code>, <code>replicar_artigo.py</code>, <code>gerar_relatorio.py</code>.
    Valores do artigo em <code>dados/manual/artigo_1998_*.csv</code>.</li>
  </ul>
</section>
</div>
"""

SAIDA.write_text(PAGINA, encoding="utf-8")
print(f"página gravada em {SAIDA}")
