# Notas de passagem — Artigo 1 (pontos ideais)

Estado em 13/11/2026, ao pausar esta sessão para continuar numa sessão com o plugin `ars`.

## Pronto
- `analise.py`: script reprodutível com todas as etapas (dados, reprodução do modelo original,
  validação cruzada 10 partições 1–4D + baselines, ajuste dentro da amostra/APRE/GMP, estrutura
  dim1 × governo/campo ideológico (teste invariante à rotação), interpretação da dim2 pelas cargas
  das votações, recortes por orientação (Governo = PL etc.) e metade/metade, robustez
  (λ, corte de minoria, obstrução) com partição por hash e acurácia em células comuns, bootstrap por
  proposição com partida fria e pipeline completo, plenário × comissões, SVD, ajustes por ano, figuras).
- **Passou no teste rápido** (`TESTE_RAPIDO=<pasta> python analise.py --etapas dados cv final estrutura dim2 recortes robustez bootstrap orgaos svd anos figuras`
  → amostra de 10% das votações, saídas fora do repo, ~1 min). A etapa `reproducao` só funciona com dados completos.
- Reprodução conferida: a acurácia fora da amostra de 91,94% em 2D bate com `avaliacao.json` (mesma partição).
- `referencias.bib`: 12 referências com metadados conferidos na web (volume, número, páginas, DOI).
- Auditoria metodológica (subagente) aplicada; ver "Correções feitas".

## Falta
1. **Rodar a análise completa**: `python artigos/01-pontos-ideais/analise.py` (estimativa de 40–60 min em 4 núcleos;
   o bootstrap com 200 réplicas de partida fria é a parte mais cara; para encurtar, reduza `N_BOOT`). O cache fica em `cache/` (ignorado pelo git).
   As tabelas versionadas hoje em `tabelas/` são parciais, de uma execução abortada; serão sobrescritas.
2. Escrever `artigo.md` com todos os números lidos de `resultados.json` e `tabelas/*.md`.
3. Conferir as figuras (`figuras/*.png`) visualmente (rótulos sobrepostos, legendas).

## Problemas conhecidos / decisões
- **Bug do 0D (corrigido)**: `DIMS` continha 0 e `ajustar(ndim=0)` quebrava, o que derrubou a execução em curso. Agora `DIMS = [1, 2, 3, 4]`; o "0D" é a baseline da maioria.
- **Escala de especialistas BRC (Bolognesi, Ribeiro e Codato, 2023)**: os escores por partido NÃO foram conferidos
  (o host scielo.br está bloqueado na rede da sessão) e a correspondência de siglas de 2018 (p.ex. PL = PR) era frágil.
  Foram removidos; usamos uma codificação ordinal grosseira `CAMPO` (esquerda/centro/direita). Se scielo.br for liberado,
  dá para reintroduzir os escores só como evidência descritiva (com e sem PL/UNIÃO/PRD, retirando um partido de cada vez).
- A validação cruzada por células é **interpolação** (o IRT usa os votos dos colegas na mesma votação; a orientação é ex ante): o texto precisa dizer isso.
- A rotação é por PCA dos pontos dos deputados com ≥ 50 votos; o sinal da dim1 vem do alinhamento ao Governo (a correlação
  com ele é, portanto, mecânica no sinal, mas não na magnitude). O teste "metades" (u estimado nas votações pares e alinhamento medido nas ímpares) mitiga a circularidade.
- Ameaças a declarar: sob Lula 3, esquerda e governo coincidem (o teste definitivo seria a 56ª Legislatura); seleção
  estratégica das votações nominais; obstrução tática; orientação "bloco (inferido)" em ~18% dos votos; composição não aleatória das comissões; partidos pequenos (NOVO, REDE, MISSÃO); interpretação a posteriori da dim2; encolhimento do MAP; trocas de partido suavizadas por λδ.
- Sugestões da auditoria ainda não implementadas: comparar o IRT com efeito fixo partido×votação contra a maioria do partido; um modelo 1D quadrático na validação cruzada contra o 2D (hoje só há a regressão u2 ~ u1 + u1²).
