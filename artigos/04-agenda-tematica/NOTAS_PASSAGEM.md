# Notas de passagem — Artigo 4 (agenda temática)

Estado em 13/11/2026, quando a sessão foi interrompida a pedido (troca para uma sessão com o plugin ars).

## Pronto
- `analise.py`: script completo, mas **ainda não executado até o fim** (nenhum número validado). Contém:
  - reimplementação parametrizada do perfil de `emb_temas` com `assert` de reprodução contra `emb_temas.parquet`;
  - cobertura temática por tipo (Tab. 1), validade de face por palavras-chave (Tab. 2);
  - especialização: temas efetivos exp(H), N efetivo de Kish, nulo que troca cada item por uma proposição do mesmo tipo (preserva volume, pesos, mix de tipos e multirrotulação), índice S = observado/esperado (Fig. 2, Tab. 3a/3b);
  - correlatos de S (OLS HC3, com e sem efeitos fixos de partido, |dim1 − média do partido|) (Tab. 4);
  - partição da variância: PERMANOVA sequencial (volume/instrumento → partido → UF → gênero/mandato), R² ajustado pelo nulo, PERMDISP, teto de confiabilidade split-half, comparação com o espaço de votos e RDA de dim1/dim2 (Tab. 5, Fig. 5);
  - ideologia: reprodução exata de `avaliar()` (R² ≈ 0,30; kNN ≈ 0,21), R² CV repetido, incremento sobre efeitos fixos de partido, previsão de dim1 dentro do partido, nulo por permutação, logística multinomial com acurácia balanceada;
  - issue ownership por terços de dim1, separado em projetos × fiscalização, bootstrap + permutação + BH, JSD com nulo (Tab. 6, Figs. 3 e 4);
  - projetos × fiscalização: distância intradeputado, sinal ideológico de cada instrumento;
  - tipos de agenda (k-means) com silhueta contra nulo de colunas permutadas, ARI com partido, estabilidade (Tab. 7);
  - divisão do trabalho: decomposição α/β/γ de Shannon com dois nulos (grupos aleatórios; itens embaralhados dentro do partido) (Tab. 8, Fig. 6);
  - estabilidade 2023–24 × 2025–26 (reidentificação) e validação externa por frentes (Mantel; AUC por frente temática) (Tab. 9);
  - sensibilidade em tabela única (9 variantes de peso + CLR) (Tab. 10);
  - pauta votada no plenário (temas faltantes buscados na API, em cache) e evolução anual (Figs. 1 e 7).
- `dados_aux/deputados_legislatura_inicial.csv` (baixado do arquivo em massa `deputados.csv`; serve para veterano/novato).
- Parecer metodológico de um subagente "arquiteto de pesquisa" (geral, não o do plugin ars). As recomendações dele já estão no desenho acima. Pontos ainda não implementados: modelo Dirichlet-multinomial/encolhimento empírico-bayesiano; Poisson/multinomial com offset para ownership; lado definido por orientação de liderança ao longo do tempo (hoje são terços de dim1); variante de peso por `relevancia`; codificação manual estratificada (n ≈ 200) para validar a classificação.

## Falta
1. Rodar `python artigos/04-agenda-tematica/analise.py --rapido` para depurar e depois rodar sem `--rapido` (~10 min estimados). A primeira execução estava na etapa de busca dos temas da pauta na API (~360 chamadas) quando foi interrompida. `dados_aux/temas_pauta_plenario.csv` ainda não existe.
2. Conferir as figuras (legibilidade) e os números em `resultados.json`.
3. Escrever `artigo.md` (todas as seções pedidas) e `referencias.bib`, com as referências verificadas ou marcadas [verificar].
4. Commit e push no branch `claude/artigo-4-agenda-tematica` (sem PR).

## Problemas conhecidos / riscos
- Ainda não executado: há trechos que podem falhar e precisam de depuração. Os mais frágeis:
  - nomes de colunas de `frentes`/`frentes_deputados` (detectados heuristicamente);
  - as regex de frentes temáticas;
  - `permanova_seq` com muitos dummies de UF (lento com 999 permutações).
- Partido do deputado = filiação mais longa na legislatura (a janela de abril de 2026 gerou muitas trocas).
- Lado governo/oposição = terços de dim1 (individual). Há risco de circularidade parcial com partido, o que está discutido no desenho.
- Os temas de RIC/INC estão confundidos com o instrumento (ex.: Agricultura e Administração Pública muito mais frequentes em RIC). Por isso todas as análises centrais estão separadas por instrumento.

## Sessão de 13/11/2026 (continuação; plugin ars indisponível nesta sessão)
- Corrigido bug de precedência em `qualidade.pct_admpub_unico` (`adm & (... == 1)`).
- `dados_aux/temas_pauta_plenario.csv` agora em cache (temas da API para proposições votadas no Plenário).
- `--rapido` roda as etapas 1–4 e falha na etapa 5: a variável global `C` (covariáveis) sombreia a função `C()`
  do patsy nas fórmulas do statsmodels. Correção pendente: renomear o DataFrame `C` (ex.: `COVA`) em todo o script.
- Referências já conferidas: Petrocik 1996 (AJPS 40(3):825–850); Legendre & Gallagher 2001 (Oecologia 129:271–280);
  Perianes-Rodríguez, Waltman & van Eck 2016 (J. Informetrics 10(4):1178–1195); Alemán et al. 2009 (LSQ 34(1):87–116);
  Fowler 2006 (Political Analysis 14(4):456–487); Grimmer & Stewart 2013 (Political Analysis 21(3):267–297).
  Faltam: Baumgartner & Jones 1993; Figueiredo & Limongi 1999; Amorim Neto & Santos 2003.
