"""
Gera artigo.pdf (diagramação para leitura/submissão) a partir de artigo.md.

    python artigos/01-pontos-ideais/gerar_pdf.py

Pipeline: Markdown --(pré-processamento)--> pandoc (HTML5 + MathML) --> Chromium/Playwright (PDF A4).
Requer pandoc, node/npm e o Chromium do Playwright; não requer LaTeX. As fórmulas são renderizadas
com KaTeX 0.16.11, instalado via npm em cache/node na primeira execução.

O pré-processamento só afeta a versão diagramada:
- junta cada imagem à sua legenda ("**Figura N.** ...") num <figure>;
- agrupa "**Tabela N.** ..." + tabela + nota num bloco que não se parte entre páginas;
- retira os ponteiros de rastreabilidade para arquivos do repositório (`tabelas/...`, `resultados.json`),
  que permanecem na versão Markdown.
"""
import re
import subprocess
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NODE = AQUI / "cache" / "node"
KATEX = NODE / "node_modules" / "katex" / "dist"
MD, HTML, PDF = AQUI / "artigo.md", AQUI / "artigo.html", AQUI / "artigo.pdf"

CSS = r"""
@page { size: A4; margin: 25mm 22mm 24mm 22mm; }
html { font-size: 10.5pt; }
body { font-family: "Liberation Serif", "Times New Roman", serif; line-height: 1.45; color: #111;
       text-align: justify; hyphens: auto; -webkit-hyphens: auto; margin: 0; background: #fff; }
p { margin: 0 0 0.55em 0; orphans: 3; widows: 3; }
h1 { font-size: 17pt; line-height: 1.25; text-align: center; font-weight: bold; margin: 0 0 0.6em 0; }
h2 { font-size: 12.5pt; margin: 1.3em 0 0.5em 0; break-after: avoid; }
h3 { font-size: 11pt; font-style: italic; font-weight: bold; margin: 1em 0 0.4em 0; break-after: avoid; }
.meta { text-align: center; font-size: 9.5pt; color: #333; margin-bottom: 1.2em; }
.meta p { margin: 0.15em 0; text-align: center; }
.katex { font-size: 1.05em; }
.katex-display { margin: 0.7em 0; }
.resumo { border-top: 0.8pt solid #111; border-bottom: 0.8pt solid #111; padding: 0.4em 0 0.6em 0;
          margin: 0.8em 0 1em 0; font-size: 9.6pt; line-height: 1.38; }
.resumo h2 { font-size: 10.5pt; margin: 0.5em 0 0.3em 0; text-transform: uppercase; letter-spacing: 0.04em; }
.resumo p:last-child { margin-bottom: 0.2em; }
hr { display: none; }
ul, ol { margin: 0.2em 0 0.6em 1.4em; padding: 0; }
li { margin-bottom: 0.25em; }
table.estreita { width: auto; min-width: 60%; }
table { hyphens: manual; -webkit-hyphens: manual; }
td:first-child { min-width: 24mm; }
table.larga td:first-child { min-width: 30mm; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.3pt; }
figure { margin: 0.9em 0 1em 0; break-inside: avoid; text-align: center; }
figure img { max-width: 100%; max-height: 120mm; }
figcaption { font-size: 9pt; text-align: justify; line-height: 1.35; margin-top: 0.35em; }
.tabela { break-inside: avoid; margin: 0.9em 0 1em 0; }
.tabela .cap { font-size: 9pt; margin-bottom: 0.25em; text-align: left; }
.tabela .nota { font-size: 8.3pt; color: #222; margin-top: 0.25em; text-align: justify; }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt; line-height: 1.25;
        border-top: 1pt solid #111; border-bottom: 1pt solid #111; }
thead th { border-bottom: 0.6pt solid #111; font-weight: bold; padding: 3px 4px; vertical-align: bottom; }
td { padding: 2px 4px; vertical-align: top; }
td, th { text-align: right; }
td:first-child, th:first-child { text-align: left; }
table.larga { font-size: 7.4pt; }
.refs p { padding-left: 1.6em; text-indent: -1.6em; text-align: left; font-size: 9.6pt; margin-bottom: 0.45em; }
.declaracoes p, .apendice p, .apendice li { font-size: 9.8pt; }
"""


def preprocessar(md: str) -> str:
    # ponteiros de rastreabilidade (só na versão diagramada)
    md = re.sub(r"Fonte: elaboração própria a partir de Dados Abertos da Câmara \(`[^`]+`\)\.",
                "Fonte: elaboração própria, a partir de Dados Abertos da Câmara dos Deputados.", md)
    md = re.sub(r"Fonte: `[^`]+`(?:\s*\([^)]*\))?\.", "Fonte: elaboração própria.", md)
    md = re.sub(r"Fonte: `resultados\.json` \([^)]*\)\.", "Fonte: elaboração própria.", md)
    md = re.sub(r" \((?:`[^`]+`(?:, )?)+\)", "", md)               # " (`a`, `b`)"
    md = re.sub(r"; `[^`]+`\)", ")", md)                           # "(1 período; `x`)"
    md = re.sub(r", `[^`]+`\)", ")", md)                           # "(..., `x`)"
    md = re.sub(r"\(`tabelas/[^`]+`(?:, `[^`]+`)*\)", "", md)
    md = md.replace("(`resultados.json`, `dim2.coalizoes_*`)", "")
    # bloco de metadados do topo
    md = re.sub(r"^(# .+?\n)\n(\*\*Autoria:\*\*.*?)\n\n---\n",
                lambda m: m.group(1) + '\n<div class="meta">\n\n' + m.group(2).replace("\n", "\n\n") + "\n\n</div>\n", md,
                count=1, flags=re.S)
    # resumo + abstract numa caixa
    md = re.sub(r"(## Resumo\n.*?)\n---\n", r'<div class="resumo">\n\n\1\n</div>\n', md, count=1, flags=re.S)
    # figuras: imagem + legenda
    md = re.sub(r"!\[[^\]]*\]\(([^)]+)\)\n\n\*\*(Figura \d+\.)\*\* ([^\n]+)",
                lambda m: f'<figure><img src="{m.group(1)}"/><figcaption><b>{m.group(2)}</b> {m.group(3)}'
                          f"</figcaption></figure>", md)
    # tabelas: legenda + tabela + nota/fonte
    def tab(m):
        cap, corpo, nota = m.group(1), m.group(2), m.group(3) or ""
        ncol = corpo.split("\n", 1)[0].count("|") - 1
        cls = "tabela larga" if ncol >= 11 else "tabela"
        if ncol <= 5:
            corpo = corpo  # largura ajustada via classe no HTML (ver pós-processamento)
            cls += " poucas-colunas"
        nota_html = f'<div class="nota">\n\n{nota.strip()}\n\n</div>' if nota else ""
        return f'<div class="{cls}">\n<div class="cap">\n\n{cap}\n\n</div>\n\n{corpo}\n{nota_html}\n</div>\n'
    md = re.sub(r"(\*\*Tabela \d+\.\*\*[^\n]*)\n\n((?:\|[^\n]*\n)+)\n?(\*(?:Nota|Fonte)[^\n]*\*\n)?", tab, md)
    # seções finais com estilos próprios
    md = re.sub(r"(## Apêndice A\..*?)(?=\n## Declarações)", r'<div class="apendice">\n\n\1\n</div>\n', md, flags=re.S)
    md = re.sub(r"(## Declarações.*?)(?=\n## Referências)", r'<div class="declaracoes">\n\n\1\n</div>\n', md, flags=re.S)
    md = re.sub(r"(## Referências\n)(.*)$", r'\1<div class="refs">\n\n\2\n</div>\n', md, flags=re.S)
    return md


def garantir_katex():
    if not KATEX.exists():
        NODE.mkdir(parents=True, exist_ok=True)
        subprocess.run(["npm", "install", "--silent", "--prefix", str(NODE), "katex@0.16.11"], check=True)


def main():
    garantir_katex()
    md = preprocessar(MD.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        src, css = Path(tmp) / "a.md", Path(tmp) / "a.css"
        src.write_text(md, encoding="utf-8")
        css.write_text(CSS, encoding="utf-8")
        titulo = re.search(r"^# (.+)$", md, flags=re.M).group(1)
        subprocess.run(["pandoc", str(src), "-f", "markdown+tex_math_dollars-implicit_figures", "-t", "html5",
                        "--standalone", f"--katex={KATEX.as_uri()}/", "--embed-resources", "--resource-path", str(AQUI),
                        "--css", str(css), "--metadata", f"pagetitle={titulo}", "--metadata", "lang=pt-BR",
                        "-o", str(HTML)], check=True)
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://{HTML}', {{ waitUntil: 'load' }});
  await p.evaluate(() => document.querySelectorAll('.poucas-colunas table').forEach(t => t.classList.add('estreita')));
  await p.waitForFunction(() => document.querySelectorAll('.math').length === document.querySelectorAll('.math .katex').length);
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({{ path: '{PDF}', format: 'A4', printBackground: true, displayHeaderFooter: true,
    margin: {{ top: '25mm', bottom: '24mm', left: '22mm', right: '22mm' }},
    headerTemplate: '<div style="font-family:Liberation Serif,serif;font-size:7.5pt;color:#555;width:100%;padding:0 22mm;text-align:right;font-style:italic">Um eixo ou dois? O voto nominal no governo Lula 3</div>',
    footerTemplate: '<div style="font-family:Liberation Serif,serif;font-size:8.5pt;color:#333;width:100%;text-align:center"><span class="pageNumber"></span></div>' }});
  await b.close();
}})();
"""
    subprocess.run(["node", "-e", js], check=True)
    HTML.unlink()
    print("ok ->", PDF)


if __name__ == "__main__":
    main()
