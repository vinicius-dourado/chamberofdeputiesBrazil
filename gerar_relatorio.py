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

# Resultado do artigo (1998) segundo o texto de Pereira & Rennó (2001), para comparação.
# (variável, o que o artigo encontrou, chave para buscar o nosso resultado)
ARTIGO = [
    ("Concentração", "Quem dispersa votos tem mais chance de se reeleger (endógena; fora do modelo principal)",
     "concentracao_2022"),
    ("Competição", "Quem enfrenta menos competição no reduto tem mais chance (endógena)", "competicao_2026"),
    ("MesmaBase", "Não significativa, sinal negativo", "mesma_base"),
    ("Gastos", "Reeleitos gastam mais na média, mas a variância dos perdedores é muito maior; "
               "per capita, os perdedores gastam mais. Fora do modelo", "gastos"),
    ("Governador", "Sem efeito direto na reeleição; afeta a distribuição de votos", "governador"),
    ("Projetos", "Não significativa", "projetos"),
    ("Ausência", "Reduz a chance de reeleição (10%); não afeta a decisão de concorrer", "ausencia"),
    ("Permanente", "Cargos em comissões permanentes aumentam a chance de concorrer e de ganhar",
     "permanente"),
    ("Partpos", "Cargos na hierarquia do partido aumentam a chance de concorrer e de ganhar", "partpos"),
    ("Senior", "Não significativa", "senior"),
    ("Histexec", "Reduz a chance de concorrer e de ganhar", "histexec"),
    ("Burocracia / Empresa", "Só na seleção; não significativas", "burocracia"),
    ("SairCoalizão", "Reduz a chance de reeleição; não afeta a decisão de concorrer", "sair_coalizao"),
    ("Índice", "Aumenta a chance de concorrer; não afeta o resultado", "indice"),
    ("Seleção (ρ)", "Equações independentes: hipótese de ρ = 0 não rejeitada", "rho"),
]


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


# --------------------------------------------------------------------------- nosso resultado
def nosso(chave):
    a = R["tabela6"]["artigo"]
    if chave == "rho":
        return (f"ρ = {num(a['rho'], 2)} (no limite do intervalo); LR χ² = {num(a['lr_rho0'], 2)}, "
                f"p = {num(a['p_lr_rho0'], 3)}: independência rejeitada", "diverge")
    if chave == "gastos":
        g = {(x["variavel"], x["grupo"]): x for x in R["tabelas4_5"]}
        r, n = g[("gastos_2026", "reeleitos")], g[("gastos_2026", "não reeleitos")]
        rp, np_ = g[("gastos_por_eleitor_2026", "reeleitos")], g[("gastos_por_eleitor_2026", "não reeleitos")]
        return (f"Reeleitos gastam mais (R$ {num(r['media'] / 1e6, 2)} mi × {num(n['media'] / 1e6, 2)} mi) e a "
                f"dispersão dos perdedores é maior (CV {num(n['cv'], 2)} × {num(r['cv'], 2)}); "
                f"por eleitor, os reeleitos também gastam mais ({num(rp['media'], 2)} × {num(np_['media'], 2)})",
                "parcial")
    if chave in ("competicao_2026",):
        t = {x["variavel"]: x for x in R["tabela2"]}[chave]
        return (f"Reeleitos enfrentam menos competição: médias {num(t['media_reeleitos'])} × "
                f"{num(t['media_nao_reeleitos'])} (Z = {num(t['z'], 2)}{estrelas(t['p'])})", "confirma")
    s = coef_de(a, "seleção", chave)
    o = coef_de(a, "resultado", chave)

    def f(c):
        return "–" if c is None else f"{num(c['coef'])}{estrelas(c['p']) or ' (n.s.)'}"
    texto = f"seleção {f(s)}; resultado {f(o)}"
    sig_o = o is not None and o["p"] < 0.1
    sig_s = s is not None and s["p"] < 0.1
    veredito = {
        "concentracao_2022": "confirma" if sig_o and o["coef"] < 0 else "diverge",
        "mesma_base": "confirma" if not sig_o else "diverge",
        "governador": "confirma" if not sig_o else "diverge",
        "projetos": "confirma" if not sig_o and not sig_s else "diverge",
        "ausencia": "diverge" if not (sig_o and o["coef"] < 0) else "confirma",
        "permanente": "confirma" if sig_o and sig_s and o["coef"] > 0 and s["coef"] > 0 else "parcial",
        "partpos": "confirma" if sig_o and sig_s and o["coef"] > 0 and s["coef"] > 0 else "parcial",
        "senior": "confirma" if not sig_o else "diverge",
        "histexec": ("confirma" if sig_o and sig_s else "parcial") if (s and s["coef"] < 0) else "diverge",
        "burocracia": "confirma" if not sig_s else "diverge",
        "sair_coalizao": "confirma" if sig_o and o["coef"] < 0 else "diverge",
        "indice": "confirma" if sig_s and s["coef"] > 0 and not sig_o else "parcial",
    }.get(chave, "parcial")
    return texto, veredito


ROTULO_VEREDITO = {"confirma": "Confirma", "parcial": "Em parte", "diverge": "Diverge"}


def secao_comparacao():
    linhas = []
    for nome, artigo, chave in ARTIGO:
        texto, v = nosso(chave)
        linhas.append(f'<tr><th scope="row">{esc(nome)}</th><td>{esc(artigo)}</td><td>{esc(texto)}</td>'
                      f'<td><span class="chip {v}">{ROTULO_VEREDITO[v]}</span></td></tr>')
    return "\n".join(linhas)


def tabela_heck():
    specs = [("artigo", "Especificação do artigo"), ("controles", "Com controles de mandato"),
             ("titulares", "Só titulares de fev/2023")]
    ordem = []
    for eq in ("seleção", "resultado"):
        vs = []
        for k, _ in specs:
            for c in R["tabela6"][k]["coefs"]:
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
        cels = "".join(celula(coef_de(R["tabela6"][k], "seleção", v)) + celula(coef_de(R["tabela6"][k], "resultado", v))
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
        cels = "".join(f'<td class="n" colspan="2">{esc(f(R["tabela6"][k]))}</td>' for k, _ in specs)
        rod.append(f'<tr><th scope="row">{rotulo}</th>{cels}</tr>')
    return (f'<table class="larga"><thead><tr><th></th>{cab}</tr><tr><th scope="col">Variável</th>{sub}</tr></thead>'
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
  <p>Cada linha resume o achado do artigo e o resultado correspondente aqui, na especificação do artigo
  (coeficientes do probit com seleção; * p&lt;0,10, ** p&lt;0,05, *** p&lt;0,01).</p>
  <div class="rolagem"><table class="comparacao larga"><thead><tr><th scope="col">Variável</th>
  <th scope="col">Artigo (1998)</th><th scope="col">Esta replicação (2026)</th><th scope="col">Leitura</th></tr></thead>
  <tbody>{secao_comparacao()}</tbody></table></div>
  <ul class="achados">
    <li><strong>Dispersar votos continua decisivo.</strong> Quem concentrou votos em um município em 2022 teve chance
    bem menor de se reeleger, em todas as especificações.</li>
    <li><strong>Posição hierárquica conta; produção legislativa não.</strong> Liderança partidária (Partpos) e cargos em
    comissões permanentes aumentam a chance de concorrer e de ganhar; projetos aprovados não fazem diferença.</li>
    <li><strong>Lealdade ao governo pesa na decisão de concorrer, não no resultado</strong>, como em 1998.</li>
    <li><strong>A seleção não é aleatória em 2026.</strong> Ao contrário do artigo, a correlação entre as equações vai
    ao limite (ρ → 1) e a independência é rejeitada. Concentração, Partpos e Permanente mantêm o sinal e a significância
    no probit simples; Índice e Mesa não.</li>
    <li><strong>Diferenças:</strong> senioridade reduz a chance de reeleição; mudar de partido para a oposição
    (SairCoalizão) não tem efeito; a ausência medida em número de faltas tem sinal positivo, efeito mecânico do tempo
    de mandato (em % das votações não há diferença).</li>
  </ul>
</section>

<section aria-labelledby="s-t6">
  <h2 id="s-t6">Tabela 6 · Probit com seleção de Heckman</h2>
  <p>Equação de seleção: o deputado concorre a deputado federal em 2026. Equação de resultado: é reeleito, dado que
  concorreu. Burocracia e Empresa entram só na seleção (restrições de exclusão), como no artigo. Coeficientes com
  erro-padrão entre parênteses. Na versão com controles, a ausência entra em % das votações.</p>
  <div class="rolagem">{tabela_heck()}</div>
  <div class="aviso"><strong>ρ no limite do intervalo</strong>
  <p>Nas três especificações a verossimilhança cresce até ρ → 1 (tabela abaixo). A estimativa na fronteira indica que
  as restrições de exclusão identificam pouco a correlação; os erros-padrão dessa estimativa são pouco confiáveis.
  Por isso o probit simples (nota 24 do artigo) é o teste de robustez mais importante aqui.</p></div>
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
