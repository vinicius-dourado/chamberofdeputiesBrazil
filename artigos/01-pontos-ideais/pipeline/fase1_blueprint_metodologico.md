# Fase 1: Blueprint metodológico do Artigo 1 (pontos ideais, 57ª Legislatura)

Papel: `research-architect-agent` (ARS, Fase 1, Scoping). Data: 13/11/2026.
Base: `analise.py` (commit `5f224df`), `NOTAS_PASSAGEM.md`, auditoria metodológica anterior e `referencias.bib`.
Este documento não redige o artigo. Ele fixa o desenho, as hipóteses e os critérios de decisão *antes* da leitura dos resultados da execução completa. A execução completa terminou durante a redação; das saídas, só os nomes das chaves foram conferidos, nunca os valores (ver "Verificação de testabilidade").

---

## Methodology Blueprint

### 0. Perguntas de pesquisa e tipo de pergunta

| RQ | Pergunta | Tipo (árvore de decisão) | Estatuto neste artigo |
|---|---|---|---|
| RQ1 | Qual a estrutura dimensional do voto nominal na 57ª Legislatura (1D, 2D ou 3D)? | Descritiva / de mensuração | Confirmatória (H2), com critério de seleção de modelo fixado aqui |
| RQ2 | O eixo principal é governo × oposição ou esquerda × direita? | Comparativa entre interpretações rivais de um construto latente | Confirmatória (H1), derivada da literatura sobre presidencialismo multipartidário |
| RQ3 | O que é a segunda dimensão? | Descritiva / interpretativa | **Exploratória**, com testes rivais estruturados (E1) e critérios de estabilidade (H3) |
| RQ4 | Quanto as coordenadas acrescentam à orientação partidária na previsão do voto? | Correlacional / preditiva (estimação de uma magnitude) | Estimação com estimandos fixados (H4), sem limiar de "sucesso" |

Nenhuma RQ é causal. O artigo **não** afirma que a posição de governo *causa* o voto, nem que os pontos ideais *são* preferências. Ele afirma que as coordenadas resumem o padrão de votos e que esse resumo se alinha mais a um critério (governo) do que a outro (campo ideológico).

### Research Paradigm

**Selected**: pós-positivista, com leitura instrumental (não realista ingênua) das coordenadas latentes.

**Justification**:
- RQ1, RQ2 e RQ4 pedem medidas replicáveis e comparações com critérios externos, testáveis contra dados observados. Isso é pós-positivista: a realidade (o padrão de votação) existe independentemente do analista, mas só é acessível por um modelo de mensuração falível.
- A leitura é instrumental porque o modelo espacial identifica *direções de variação conjunta dos votos*, e não preferências sinceras. Votos nominais misturam preferência, disciplina partidária, barganha com o Executivo e tática de plenário. Por isso, "dim1 = governo × oposição" é uma afirmação sobre **a estrutura do comportamento revelado**, e não sobre ideologia íntima (cf. a discussão de Zucco, 2009, e Zucco & Lauderdale, 2011, sobre separar influências no voto brasileiro).
- RQ3 tem componente interpretativo: dar nome a uma dimensão é um ato de interpretação. Isso não muda o paradigma, mas obriga a declarar a interpretação como exploratória e a submetê-la a hipóteses rivais (E1).

### Method

**Type**: quantitativo.

**Specific Method**: estimação de pontos ideais por IRT logístico 2PL multidimensional (família dos modelos espaciais de votação nominal: Poole & Rosenthal, 1985, 1997; Jackman, 2001; Clinton, Jackman & Rivers, 2004; Bafumi et al., 2005; Imai, Lo & Olmsted, 2016), comparado em validação cruzada com baselines partidárias e com uma fatoração SVD (Koren, Bell & Volinsky, 2009).

**Justification por RQ**:

| Escolha | RQ que a exige | Por quê | Alternativa considerada |
|---|---|---|---|
| Modelo espacial com K dimensões livres (1–4) | RQ1 | A dimensionalidade é a própria pergunta; deve ser escolhida pelos dados fora da amostra, não fixada. | W-NOMINATE (exige software externo e só dá 2D estável); ficar só no scree de SVD (não diz nada fora da amostra). |
| 2PL logístico, P(Sim) = σ(a_j + b_j·x_i) | RQ1–RQ3 | Cargas b_j por votação permitem ler *quem fica de que lado* em cada votação (t6, t7, t8*), o que é necessário para nomear os eixos (RQ2, RQ3). | Modelo de utilidade quadrática (NOMINATE): mais fiel à proximidade, mas não altera a dimensionalidade de forma relevante em legislaturas com polos claros. A ressalva é a ferradura (ver E1). |
| MAP com priors normais (λx = 1, λb = 0,04, λa = 0,01) e L-BFGS | RQ1, RQ4 | Matriz esparsa (≈ 433 mil votos em 831 × 1.470) e milhares de parâmetros. O MAP é rápido o bastante para a CV de 10 partições × 4 dimensões e para o bootstrap de 200 réplicas, que são o núcleo da evidência. | MCMC bayesiano completo (Jackman, 2001): melhor quantificação da incerteza, mas inviável com CV e bootstrap; a incerteza fica com o bootstrap por proposição. |
| x = u_deputado + δ_período, λδ = 4 | RQ2 | Trocas de partido (janela de 2024/2026, fusões no PRD) são parte do fenômeno governo × oposição. δ permite que o ponto mude com a filiação sem criar um deputado novo. | Um ponto por deputado (λδ = 64, na robustez); períodos independentes (λδ = 0,25, na robustez). |
| Obstrução = Não | RQ2 | Obstrução é uma forma de se opor ao objeto. Tratá-la como ausência descartaria sobretudo votos de oposição. | "Obstrução como ausência" e "obstrução e abstenção como Não" (robustez). **Ameaça específica:** obstrução é uma tática típica da oposição contra a pauta do governo. Codificá-la como Não pode *reforçar mecanicamente* a dim1 governo × oposição. Por isso, H1 deve sobreviver à configuração "obstrução como ausência" (critério abaixo). |
| Descartar votações com minoria < 2,5% | RQ1 | Votações quase unânimes não informam a posição (b_j ≈ 0) e inflam a acurácia de qualquer modelo. | 0%, 5%, 10% e 20% na robustez, com a acurácia nas **células comuns** para comparar. |
| Rotação por PCA dos u confiáveis (≥ 50 votos); sinal da dim1 pelo alinhamento ao Governo; sinal da dim2 pelo PSOL | RQ2, RQ3 | O modelo é invariante a rotações; algum referencial canônico é necessário. A PCA é estatística e não substantiva. **Consequência:** a resposta à RQ2 não pode depender só de "o eixo 1 correlaciona com o governo". Ela precisa de testes invariantes à rotação (ângulos, H1b) e do *split-half* (H1c). | Rotação para um critério externo (Procrustes alvo): seria circular para a RQ2. |
| Baselines: maioria da votação (0D), orientação da bancada, maioria do partido na votação, IRT 2D com um ponto por partido | RQ4 | "Acrescentar à orientação" só tem sentido contra um contrafactual partidário. A maioria do partido é a baseline **simétrica** (também interpola com os colegas na mesma votação); a orientação é **ex ante** (assimétrica). | Efeito fixo partido × votação no IRT (recomendado como opcional, item 4 da seção final). |

### Data Strategy

**Data Type**: secundários, administrativos e públicos (Dados Abertos da Câmara dos Deputados), obtidos por `baixar_legislatura.py` e versionados em `dados/leg57/*.parquet`.

**Sources**: `votos.parquet` (voto nominal, partido na data, orientação da bancada e do Governo, `orientacao_fonte`), `votacoes.parquet` (órgão, descrição, objeto, proposição), `votacoes_orientacoes.parquet` (Governo, Oposição, PL, NOVO, federações), `deputados.parquet`.

**Sampling**: censo de todas as votações nominais da legislatura até a data da extração (plenário e comissões), sem amostragem. A unidade de análise é a célula deputado-período × votação. Exclusões: votos diferentes de Sim/Não/Obstrução (abstenção, ausência, artigo 17); votações com minoria < 2,5%. A população de inferência é **o conjunto de votações nominais desta legislatura**, e não "todas as decisões da Câmara". As votações simbólicas ficam fora por construção (ver Limitações).

**Time Frame**: 57ª Legislatura, de fevereiro/2023 até a data da última votação extraída. Relatar `dados.data_min` e `dados.data_max` de `resultados.json` e a data da extração. A legislatura ainda não terminou; os resultados são de uma legislatura **incompleta**, e o texto deve dizer isso.

**Fluxograma a relatar** (adaptação do item "participantes" do STROBE): `dados.votacoes_total` → `votacoes_nominais` → votações após o corte de minoria (`dados.votacoes`) → votos brutos (`registros_voto_brutos`, por tipo em `tipos_voto_brutos`) → votos analisados (`dados.votos`) → deputados, períodos e deputados confiáveis (`deputados`, `periodos`, `deputados_confiaveis`).

### Analytical Framework

**Technique**: IRT 2PL multidimensional (MAP), validação cruzada por células, bootstrap em blocos por proposição com partida fria e pipeline completo, testes de alinhamento invariantes à rotação, análise de cargas por votação, recortes por padrão de orientação e análises de sensibilidade.

**Steps** (em ordem; a etapa de `analise.py` vem entre parênteses):
1. Descrição dos dados e fluxograma (`dados` → `t1`).
2. Reprodução da implementação original na mesma partição (`reproducao`). Critério de aceite: `reproducao.concordancia_previsoes` ≥ 0,99 e |`reimpl_acuracia` − `original_acuracia`| < 0,001.
3. **RQ1**: CV de 10 partições, 1–4D, com baselines (`cv` → `t2`, `fig2`); ajuste dentro da amostra (`final` → `t2b`); scree da SVD (`svd` → `t12`).
4. **RQ2**: ajuste final 2D girado; estrutura (`estrutura` → `t5`, `t6`, `t7`, `fig3`); *split-half* e recortes por orientação (`recortes` → `t7b`).
5. **RQ3**: cargas e perfil das votações (`dim2` → `t8`, `t8a`–`t8d`, `votacoes_cargas.csv`, `fig4`), regressão u2 ~ u1 + u1² (`estrutura`).
6. **RQ4**: ganhos sobre as baselines (`cv` → `t2`, `t3`, `t4`, `t9a`; `RES["dissidencia"]`).
7. Incerteza: bootstrap por proposição, B = 200, partida fria (`bootstrap` → `t11`, `fig5`, `fig6`, `pontos_ideais_deputados.csv`).
8. Sensibilidade e generalização interna: hiperparâmetros, corte e codificação (`robustez` → `t10`); plenário × comissões (`orgaos` → `t9`, `fig7`); por ano (`anos` → `t13*`); SVD (`svd` → `t12`).
9. Aplicação dos critérios de decisão abaixo, **na ordem e com os limiares fixados aqui**, e relato de todas as hipóteses, inclusive as não sustentadas.

**Tools**: Python 3 (numpy, scipy L-BFGS-B, pandas, matplotlib), script único `analise.py` com cache, sementes explícitas (partição de CV `default_rng(2026)`, bootstrap `1000 + b`, robustez com partição por *hash*).

---

### Hipóteses confirmatórias e análises exploratórias, com critérios de decisão

Convenções:
- `RES.x.y` designa a chave `y` do bloco `x` em `resultados.json`.
- "pp" significa pontos percentuais de acurácia.
- Os limiares foram fixados neste documento **depois** de conhecida a acurácia 2D de 91,94% (`avaliacao.json`), mas **antes** da leitura da execução completa (ver Pré-registro).
- Com cerca de 433 mil votos, qualquer diferença será "estatisticamente significativa" se a dependência for ignorada. Por isso, os critérios combinam (i) um IC que respeita a dependência por proposição e (ii) um limiar de magnitude substantiva.

#### Verificação de testabilidade contra as saídas da execução completa (feita às cegas)

A execução completa terminou depois da primeira versão deste blueprint. Conferi a **existência e o tipo** de cada chave e coluna citada, por um script que lista os nomes **sem imprimir valores**. Nenhum limiar foi calibrado com os resultados, de propósito. Ajustar limiares depois de ver os números transformaria os critérios em descrição *post hoc* e anularia o plano datado (ver Pré-registro).

| Critério | Chaves/colunas presentes? | Observação |
|---|---|---|
| H1a | Sim: `bootstrap.dif_PP_PL_dim1`, `dif_REPUBLICANOS_PL_dim1` (dif + ic); `estrutura.fracao_distancia_direita_interna` | **Falta `dif_UNIÃO_PL_dim1`.** Até o item 2 ser feito, H1a se decide com PP e REPUBLICANOS; UNIÃO é lida descritivamente em `t11` (os IC por partido existem, mas o IC da diferença não). |
| H1b | Sim: `estrutura.r2_dim1_{campo,governo,ambos}`, `angulo_governo`, `angulo_campo`, `direita_r_dim1_governo` | θ_g e θ_c se calculam à mão a partir dos dois ângulos. Ainda não há IC (item 2). |
| H1c | Sim: `recortes.metades_r_dim1_gov`, `metades_r_dim2_gov`, `metades_n` | — |
| H1d | Sim: `robustez[config="obstrução como ausência"]["r dim1"]` | — |
| Complementar t7b | Sim: as 3 linhas de `recortes.recortes` com `r com dim1/dim2 completa` | — |
| H2a | Parcial: `cv.ganho_1D_2D.{media,min}`, `cv["IRT kD"]["log-loss"]` | **IC por proposição inexistente** (item 1). Sem ele, H2a fica "sustentada só por magnitude e consistência entre *folds*", e o texto deve dizer isso. |
| H2b | Sim: `cv.ganho_2D_3D`, `ganho_3D_4D` | — |
| H2c | Sim: `robustez[*]["ganho 1D→2D"]` (13 configurações), `anos[*]["ganho 1D→2D"]`, `t9` colunas `IRT 1D`/`IRT 2D` | — |
| H2d / E4.1 | Parcial: `cv.ganho_2D_vs_maioria_partido` | IC por proposição inexistente (item 1). |
| H3 | Sim: `bootstrap.angulo_eixos_p95_abs`, `confiabilidade_dim2`, `r_replica_dim2_mediana`, `convergiram`, `B`; `estrutura.autovalores_u`; `robustez[*]["r dim2 (Procrustes)"]`; `t9`/`anos` `r dim2 (Procrustes)` | Totalmente testável. |
| E1(a) | Parcial: `estrutura.r2_dim2_em_dim1_{linear,quadratico}`, `coef_quadratico` | **CV do 1D quadrático inexistente** (item 3): só a assinatura descritiva é avaliável. |
| E1(b)–(d) | Sim: `bootstrap.dif_PSOL_PT_dim2`, `dif_NOVO_PL_dim2`, `dif_PSOL_NOVO_dim2`; `dim2.perfil`, `classes`, `tipos`, `proposicoes_dim2`, `top` | — |
| E4.2–E4.4 | Sim: `cv["Orientação da bancada"]`, `cv["IRT 2D, um ponto por partido"]`, `dissidencia.*`, `estrutura.eta2_partido_d{1,2}`, `por_fonte` | — |
| Reprodução (passo 2) | Sim: `reproducao.*` | — |

Em resumo: H1c, H1d, H2b, H2c, H3 e E4.2–E4.4 já são decidíveis com as saídas atuais. H1a, H1b, H2a, H2d/E4.1 e E1(a) são decidíveis só parcialmente até os itens 1–3.

#### H1 (RQ2, confirmatória): o eixo principal é governo × oposição, e não esquerda × direita

Fundamentação: em presidencialismos multipartidários com coalizão, o conflito entre governo e oposição organiza o voto ao menos tanto quanto a ideologia (Figueiredo & Limongi, 1999; Zucco, 2009; Zucco & Lauderdale, 2011; Hix & Noury, 2016). Sob Lula 3, esquerda e governo coincidem. Por isso, **a única variação que discrimina entre as duas leituras está dentro da direita**, entre a direita de oposição (PL, NOVO) e a direita que integra a coalizão ou o ministério (PP, REPUBLICANOS, UNIÃO).

| Sub-hipótese | Previsão se a dim1 = governo × oposição | Chaves / tabelas | Critério de decisão |
|---|---|---|---|
| **H1a** Separação dentro da direita | PP, REPUBLICANOS e UNIÃO ficam bem mais governistas na dim1 que PL e NOVO | `RES.bootstrap.dif_PP_PL_dim1`, `dif_REPUBLICANOS_PL_dim1` (dif e IC 95%); `RES.estrutura.fracao_distancia_direita_interna`; `t11` | **Sustentada** se os dois IC 95% estiverem inteiramente acima de 0 **e** `fracao_distancia_direita_interna` ≥ 0,33 (a direita do centrão fica a pelo menos 1/3 do caminho entre a oposição de direita e a esquerda). **Refutada** se algum IC incluir 0 **ou** a fração for ≤ 0,10. Entre 0,10 e 0,33: "misto", com ambas as leituras declaradas. |
| **H1b** Incremento invariante à rotação | O alinhamento ao Governo explica a dim1 além do campo ideológico, mas o contrário não ocorre | `RES.estrutura.r2_dim1_campo`, `r2_dim1_governo`, `r2_dim1_ambos`; `angulo_governo`, `angulo_campo`; `direita_r_dim1_governo` | **Sustentada** se `r2_dim1_ambos − r2_dim1_campo` ≥ 0,10 **e** `r2_dim1_ambos − r2_dim1_governo` ≤ 0,05 **e** `direita_r_dim1_governo` ≥ 0,5. Ângulos: calcular θ_g = desvio de `angulo_governo` em relação ao eixo 1 e θ_c = desvio de `angulo_campo` em relação a 180° (os dois reduzidos a [0°, 90°] como direções de reta). O esperado é θ_g < θ_c. **Atenção:** `angulo_entre_governo_e_campo` no script é \|diferença\| sem redução módulo 180°; não usar diretamente (ver item 2 dos aperfeiçoamentos). |
| **H1c** Não circularidade | A associação dim1–governo não decorre de o sinal e o alinhamento virem dos mesmos votos | `RES.recortes.metades_r_dim1_gov` (u nas votações pares, alinhamento nas ímpares), `metades_n` | **Sustentada** se `metades_r_dim1_gov` ≥ 0,80 **e** \|`metades_r_dim2_gov`\| ≤ 0,30. |
| **H1d** Robustez à codificação da obstrução | A dim1 não é um artefato de obstrução = Não | `t10`, linha "obstrução como ausência": `r dim1`, `ganho 1D→2D` | **Sustentada** se `r dim1` ≥ 0,95 nessa configuração. Se ficar entre 0,90 e 0,95, reestimar H1a nessa configuração antes de afirmar H1. |

**Regra agregada para H1**: o artigo afirma "o eixo principal é governo × oposição" só se H1a **e** H1c forem sustentadas e H1b e H1d não forem refutadas. Se H1a for "misto", a formulação passa a ser "o eixo principal mistura governo × oposição e campo ideológico, com peso X" (reportar os R² parciais).

**Teste complementar (exploratório, `t7b`)**: no recorte "Governo e PL orientam igual", se a dimensão principal desse recorte correlacionar mais com a dim2 completa do que com a dim1 completa (`r com dim2 completa` > `r com dim1 completa` em módulo), isso mostra que, retirado o conflito governo × oposição, sobra o conflito que define a dim2. Esse teste apoia H1 e informa E1, mas não entra na regra agregada, porque o recorte foi definido depois de ver as cargas.

#### H2 (RQ1, confirmatória): duas dimensões são necessárias e suficientes

| Sub-hipótese | Chaves / tabelas | Critério de decisão |
|---|---|---|
| **H2a** 2D melhora sobre 1D fora da amostra | `RES.cv.ganho_1D_2D` (media, min); `RES.cv["IRT 1D"]["log-loss"]`, `RES.cv["IRT 2D"]["log-loss"]`; IC por proposição (item 1 dos aperfeiçoamentos) | **Sustentada** se `ganho_1D_2D.media` ≥ 0,003 (0,3 pp) **e** `ganho_1D_2D.min` > 0 (as 10 partições) **e** o log-loss 2D for menor que o 1D **e** o IC 95% por proposição do ganho excluir 0. |
| **H2b** 3D não acrescenta de forma relevante | `RES.cv.ganho_2D_3D`, `ganho_3D_4D` | **"2D suficiente"** se `ganho_2D_3D.media` < 0,003 **ou** < 1/3 de `ganho_1D_2D.media`. Caso contrário, a resposta à RQ1 passa a ser 3D, e a dim3 entra como exploratória. |
| **H2c** A dimensionalidade não é artefato da amostra | `t10` (`ganho 1D→2D` por configuração, `acurácia 2D (células comuns)`); `t13` (`ganho 1D→2D` por ano); `t9` (`IRT 2D` − `IRT 1D` no plenário) | **Sustentada** se `ganho 1D→2D` > 0 em todas as configurações de `t10`, em todos os anos com ≥ 100 votações em `t13` e no plenário isolado. |
| **H2d** 2D supera a informação partidária simétrica | `RES.cv.ganho_2D_vs_maioria_partido` | **Sustentada** se a média for > 0 **e** o IC 95% por proposição excluir 0. (A comparação com a orientação da bancada fica em H4, porque é assimétrica.) |

Evidência secundária, não decisória: APRE e GMP dentro da amostra (`t2b`); `RES.svd.var_explicada` (scree); acurácia da SVD (`t12`) como verificação de que a conclusão não depende da forma logística.

#### H3 (RQ3, confirmatória quanto à *estabilidade*, não ao *significado*): a segunda dimensão é estável

Antes de interpretar a dim2, é preciso mostrar que ela não é ruído de rotação ou de amostra.

| Critério | Chaves | Limiar |
|---|---|---|
| Estabilidade dos eixos | `RES.bootstrap.angulo_eixos_p95_abs` | ≤ 15° (com autovalores próximos, os eixos girariam de réplica para réplica) |
| Confiabilidade | `RES.bootstrap.confiabilidade_dim2`, `r_replica_dim2_mediana` | ≥ 0,70 e ≥ 0,90 |
| Separação dos autovalores | `RES.estrutura.autovalores_u` | relatar a razão λ1/λ2; se < 1,5, a ordem "dim1/dim2" é frágil e o texto deve dizer isso |
| Invariância a especificação | `t10` `r dim2 (Procrustes)`; `t9` `r dim2 (Procrustes)` plenário; `t13` `r dim2 (Procrustes)` | ≥ 0,90 em todas as configurações de `t10`; relatar `t9` e `t13` sem limiar (as amostras são menores) |
| Convergência | `RES.bootstrap.convergiram` / `B` | ≥ 95% das réplicas; as não convergidas já são excluídas, e o número deve ser relatado |

Se H3 falhar, a RQ3 é respondida como "existe ganho preditivo na 2ª dimensão (H2), mas a sua orientação não é estável o bastante para receber um nome", e E1 é relatada apenas descritivamente.

#### E1 (RQ3, exploratória): o que é a segunda dimensão

Interpretações rivais, cada uma com uma assinatura observável **a declarar como exploratória**, porque os rótulos ("centrão × polos") foram sugeridos pelos dados (README e eixos da `fig1` já os usam):

| Interpretação rival | Assinatura que a apoia | Chaves / tabelas |
|---|---|---|
| (a) **Ferradura / proximidade em um eixo** (extremos contra o meio; artefato do 2PL linear quando a utilidade é de proximidade; Duck-Mayr & Montgomery [verificar]) | u2 bem descrito por u1²; um 1D quadrático empata com o 2D na CV | `RES.estrutura.r2_dim2_em_dim1_quadratico` − `r2_dim2_em_dim1_linear` ≥ 0,25 e `coef_quadratico` com sinal "polos +"; **CV 1D quadrático vs 2D (item 3; hoje inexistente)**: diferença < 0,1 pp ⇒ (a) |
| (b) **Polos programáticos contra o centrão** (PSOL e NOVO juntos contra o centro fisiológico) | PSOL > PT e NOVO > PL na dim2; nas votações de dim2 dominante, \|PSOL−NOVO\| é pequeno e \|centrão−PT\| é grande | `RES.bootstrap.dif_PSOL_PT_dim2`, `dif_NOVO_PL_dim2` (IC > 0), `dif_PSOL_NOVO_dim2`; `t8a` |
| (c) **Procedimento / agenda** (votos sobre pauta, urgência e adiamento, e não sobre o mérito) | `prop. dim2 dominante` concentrada em requerimentos | `t8b` (atenção ao erro conhecido da classificação de objeto; ver Limitações), `t8c`, `t8d` |
| (d) **Tema específico** (poucas proposições concentram a dim2) | poucas proposições somam a maior parte das votações de dim2 dominante | `t8d`, `t8_top_dim2` |

(a) e (b) não se excluem totalmente: (b) pode ser a forma substantiva de (a). A distinção decisiva é a CV do 1D quadrático. Sem ela, o texto **não pode** afirmar que a dim2 é um conflito independente; pode apenas descrever quem fica de que lado. Leitura recomendada: relatar as quatro assinaturas, escolher a interpretação com mais assinaturas favoráveis e declarar explicitamente quais testes foram desenhados depois de ver as cargas.

#### H4 (RQ4, estimação): o que as coordenadas acrescentam ao partido

A RQ4 pede uma **magnitude**, e não uma decisão binária. Os estimandos são fixados aqui para evitar a escolha *a posteriori* da comparação mais favorável:

| Estimando | Definição | Chaves | Leitura |
|---|---|---|---|
| E4.1 Ganho sobre a informação partidária simétrica (estimando principal) | acc(IRT 2D) − acc(maioria do partido na votação), CV | `RES.cv.ganho_2D_vs_maioria_partido` + IC por proposição | É o "acréscimo das coordenadas individuais ao partido", em condições iguais de interpolação |
| E4.2 Ganho sobre a orientação ex ante | acc(IRT 2D) − acc(orientação da bancada) | `RES.cv["IRT 2D"]["acurácia"]` − `RES.cv["Orientação da bancada"]["acurácia"]` | **Limite superior** do acréscimo, porque o IRT usa os votos dos colegas na mesma votação e a orientação não. Relatar sempre com essa ressalva. |
| E4.3 Onde o ganho está | acerto entre dissidentes e entre votos não orientados | `RES.dissidencia.irt2d_acerta_dissidentes` vs `maioria_partido_acerta_dissidentes`; `irt2d_nao_orientados` vs `maioria_nao_orientados`; `t3` por fonte da orientação | Mostra se as coordenadas captam a dissidência ou apenas reproduzem a disciplina |
| E4.4 Variação individual vs partidária | IRT 2D com um ponto por deputado vs um ponto por partido | `RES.cv["IRT 2D"]` vs `RES.cv["IRT 2D, um ponto por partido"]`; `RES.estrutura.eta2_partido_d1`, `eta2_partido_d2` | Fração da estrutura espacial que é partidária |

Previsão direcional (fraca, para registro): E4.1 > 0, mas menor que 2 pp; E4.3 com o IRT acertando claramente mais dissidentes que a maioria do partido. Não há limiar de "sucesso". O texto relata as magnitudes com IC.

---

### Validity Criteria

| Critério | Ameaça principal neste desenho | Estratégia (já implementada = ✔; a implementar = ◻) |
|---|---|---|
| **Validade de construto: o que é a dim1** | A rotação PCA e o sinal pelo Governo tornam "dim1 ≈ governo" parcialmente mecânico | ✔ teste invariante à rotação (`angulo_*`, `r2_dim1_*`); ✔ *split-half* (`metades_r_dim1_gov`); ✔ separação dentro da direita (H1a); ◻ IC bootstrap dos ângulos e R² (item 2) |
| **Validade de construto: o que é a dim2** | Rótulo a posteriori; ferradura; classificação de objeto imperfeita | ✔ u2 ~ u1 + u1²; ✔ perfis `t8a`–`t8d`; ◻ CV 1D quadrático (item 3); declarar E1 como exploratória |
| **Validade de construto: o critério externo "campo"** | Codificação ordinal grosseira, escolhida pelos autores; escores BRC não conferidos | ✔ uso só ordinal; o ponto decisivo (PL, NOVO, PP, REPUBLICANOS e UNIÃO todos à direita) independe de nuances; relatar a codificação completa em apêndice; (opcional) reintroduzir os escores BRC só como evidência descritiva, se conferidos [verificar] |
| **Validade de conclusão estatística** | Dependência entre votações da mesma proposição; folds aleatórios por célula subestimam a variância; muitos testes | ✔ bootstrap em blocos por proposição, partida fria, pipeline completo; ◻ IC por proposição para os ganhos da CV (item 1); limiares substantivos fixados aqui; relatar todas as hipóteses |
| **Validade interna (das comparações de modelos)** | Assimetria da CV (o IRT interpola, a orientação é ex ante); configurações de robustez com conjuntos diferentes | ✔ baseline simétrica (maioria do partido); ✔ partição por *hash* e acurácia em células comuns (`t10`); declarar a assimetria em E4.2; ◻ (opcional) IRT com efeito fixo partido × votação (item 4) |
| **Confiabilidade das estimativas** | Encolhimento MAP para deputados com poucos votos; dim2 mais encolhida | ✔ `confiabilidade_dim1/2`, `ep_mediano_*`, `rho_ep_nvotos_*`, `largura_ic_rank_dim1_mediana`; inferências substantivas só com deputados ≥ 50 votos; importância das dimensões pela CV, e não por `var_dim1_share` (que depende de λ) |
| **Confiabilidade computacional / reprodutibilidade** | Ótimos locais; dependência de `fork`; cache desatualizado | ✔ `reproducao` (critério no passo 2); ✔ sementes explícitas; ✔ `convergiu` relatado e réplicas não convergidas excluídas; executar com `--refazer` na versão final e registrar o *hash* do commit e as versões dos pacotes |
| **Validade externa (generalização)** | Uma legislatura sob um governo de esquerda: governo e esquerda são observacionalmente equivalentes fora da direita | ✔ variação por ano (`t13`) e por arena (`t9`); a validade externa para "presidencialismo de coalizão" **não** é sustentada por este artigo; ◻ (opcional, mais forte) replicação na 56ª Legislatura, sob Bolsonaro (item 5) |
| **Validade ecológica / de seleção** | Só votações nominais, pedidas estrategicamente; comissões com composição escolhida pelas lideranças | Declarar; comparar plenário × comissões (`t9`); relatar a proporção de votações nominais sobre o total (`dados.votacoes_nominais` / `votacoes_total`) |

### Limitations (By Design)

1. **Equivalência observacional sob Lula 3.** Esquerda e governo coincidem; a identificação de H1 vem só da direita (≈ 10 partidos, com alguns grandes). *Mitigação:* H1a com IC por partido; declarar que o teste definitivo é a 56ª Legislatura (item 5).
2. **A CV é interpolação, não previsão de votações novas.** As células de teste estão em votações cujos parâmetros a_j e b_j foram estimados com os votos dos colegas. Nenhum resultado diz quão bem se preveem votações futuras. *Mitigação:* chamar a métrica de "reconstrução de votos retidos"; a comparação justa é com a maioria do partido.
3. **Seleção das votações nominais** (Carrubba et al., 2006 [verificar]; Hug, 2010 [verificar]). As votações simbólicas, que são a maioria, ficam fora. *Mitigação:* declarar; relatar a razão nominais/total; restringir a inferência ao "voto nominal".
4. **Obstrução e ausência estratégicas.** Codificar obstrução como Não mistura posição e tática; a ausência é tratada como ignorável (MAR), o que provavelmente não é. *Mitigação:* H1d; configurações de `t10`.
5. **Orientação "bloco (inferido)" (≈ 18% dos votos).** É erro de medida na baseline E4.2. *Mitigação:* `t3` por fonte; E4.1 não depende da orientação.
6. **Interpretação a posteriori da dim2** e classificação de objeto com erro conhecido (destaques e emendas confundidos com texto principal, PECs; já corrigido em parte em `classe_objeto`). *Mitigação:* E1 declarada exploratória; amostra manual de, por exemplo, 50 votações de `t8_top_dim2` conferida contra a descrição.
7. **Encolhimento MAP e dependência de priors.** Escalas e distâncias absolutas dependem de λ. *Mitigação:* comparar posições relativas e ordens; relatar `t10` com λx, λb e λδ variados.
8. **Partidos pequenos** (NOVO ≈ 5, REDE ≈ 8, MISSÃO = 1 deputado). Diferenças na dim2 com IC largo. *Mitigação:* `t11` com IC; não interpretar partidos com menos de 3 períodos confiáveis.
9. **Trocas de partido suavizadas** por λδ = 4. *Mitigação:* configurações λδ = 0,25 e λδ = 64.
10. **Escolha do corte de minoria com todos os votos** (inclusive os de teste). O efeito é desprezível, mas deve ser declarado.
11. **Inferência no nível do deputado com dependência intrapartidária.** Correlações e R² entre ~500 deputados exageram a precisão quando a variação é sobretudo partidária. *Mitigação:* apoiar H1 nas diferenças partidárias com IC bootstrap (H1a) e relatar `t5` por partido.
12. **Legislatura incompleta.** O ano eleitoral de 2026 e a janela partidária podem mudar o quadro; relatar a data de corte.

### Ethical Considerations

- Dados públicos, agregados e de acesso aberto, sobre atos oficiais de parlamentares no exercício do mandato (votos nominais registrados pela Câmara). Não há recrutamento, intervenção nem coleta de dados pessoais além do que a Câmara publica sobre o mandato.
- Cuidado com afirmações individuais: o CSV `pontos_ideais_deputados.csv` nomeia deputados. O texto não deve rotular deputados individualmente ("ideológico", "fisiológico") sem o IC, e deve evitar *rankings* individuais quando `largura_ic_rank_dim1_mediana` for grande.
- Os rótulos de eixos ("centrão", "polos") têm carga política; usá-los como descrições operacionais definidas no texto.

### Human-Subjects Administrative Status

- **Não se aplica.** O estudo usa dados públicos e agregados de votações nominais de parlamentares no exercício do mandato, sem sujeitos humanos recrutados, sem interação ou intervenção e sem dados privados identificáveis. Não há protocolo para submissão; nenhuma determinação institucional foi solicitada ou é afirmada aqui.
- Review pathway: não acionado (não se aplica).
- Submission readiness / Authorization status: não aplicável.

> **Human-subjects boundary:** This output does not authorize recruitment, consent, access to identifiable data, intervention, or data collection.

### Reporting Standard

- **Recommended guideline: Other.** Nenhuma diretriz EQUATOR cobre a estimação de modelos de mensuração latente sobre dados legislativos. O guia de rotas do ARS manda não forçar a diretriz "mais parecida".
- **O que usar:**
  1. **STROBE adaptado** (estudo observacional transversal sobre registros administrativos), só pelos itens que se transferem: fonte e período dos dados, critérios de elegibilidade e fluxograma (ver Data Strategy), definição das variáveis (voto, orientação, campo, alinhamento ao Governo), viés e dados faltantes (ausência, obstrução), métodos estatísticos e análises de sensibilidade, limitações e generalização. Na mesma linha, os princípios do **RECORD** (extensão do STROBE para dados coletados rotineiramente) [verificar aplicabilidade fora da saúde] para a codificação e a limpeza de dados administrativos.
  2. **Elementos do TRIPOD** como inspiração (não conformidade) para a parte preditiva: desenho da partição (células, 10 *folds*, semente), métricas (acurácia, log-loss, APRE, GMP), comparadores e ausência de avaliação em dados novos.
  3. **Normas de transparência da ciência política**: DA-RT/JETS [verificar] e o padrão de "replicação computacional" da revista-alvo: *script*, *hash* do commit, versões dos pacotes e dados versionados.
- **O que relatar obrigatoriamente**: o fluxograma de dados; a codificação de votos (tabela Sim/Não/Obstrução/Abstenção → y); os hiperparâmetros e a sua origem (herdados do projeto e não ajustados por CV, o que deve ser dito); a identificação (rotação, sinais, MIN_VOTOS); a convergência; a reprodução da implementação original; a CV com as quatro baselines e a ressalva da interpolação; todas as hipóteses H1–H4 e E1 com o resultado de cada critério, inclusive as não sustentadas; a tabela completa de robustez; IC por proposição; os desvios em relação a este blueprint (seção "Desvios" no apêndice).

### Preregistration

- **Recommended:** Sim, para o que ainda é possível pré-registrar de verdade (ver abaixo). Para o Artigo 1 em si, um pré-registro estrito não é mais possível.
- **Status honesto:** **não pré-registrado.** É uma análise secundária de dados já explorados: o modelo, os hiperparâmetros, os rótulos dos eixos (README, `fig1`) e a acurácia 2D (91,94%, `avaliacao.json`) eram conhecidos antes deste blueprint, e tabelas parciais de uma execução abortada foram geradas e versionadas (commit `e53f967`). Os limiares das H1–H4 foram escritos depois disso.
- **O que fazer, em vez de alegar pré-registro:**
  1. *Plano de análise datado.* A execução completa já terminou (`resultados.json` existe). Este blueprint foi escrito **sem ler os valores**: só os nomes das chaves foram conferidos. Fazer o commit **já** (*hash* + data), antes que alguém consulte os números para redigir, e citar esse *hash* no artigo como "plano de análise fixado antes da leitura dos resultados finais, não pré-registro". Se alguém do projeto já tiver lido os valores antes do commit, declarar isso no artigo. Opcional: depositar o mesmo arquivo no OSF como *timestamped analysis plan* (não como *preregistration*).
  2. Usar no artigo a declaração de "não pré-registrado" do `preregistration_guide.md` (§5), com a lista explícita do que era conhecido antes.
  3. *Pré-registro genuíno, possível agora:* replicar H1 na 56ª Legislatura (governo Bolsonaro), cujos dados ainda **não** foram baixados nem analisados neste projeto. Previsão a registrar: se a dim1 é governo × oposição, o polo governista passa para a direita e o PT fica no polo de oposição, junto com o PSOL, enquanto o centrão fica do lado do governo. Plataforma: OSF Registries (ou AsPredicted, por ser mais simples).
- Platform: OSF (plano datado e, se for feito, o pré-registro da 56ª).
- Completed artifact declaration: `not_provided`.
- Companion handle: none.
- Sidecar ownership: dispatching layer only; do not populate a digest here.

### Design-Freeze Checkpoint Audit

Não acionado: `ARS_CROSS_MODEL` não está definido nesta sessão. Este blueprint passou apenas pela revisão de um modelo.

---

## Aperfeiçoamentos recomendados ao `analise.py`

Prioridade decrescente. **N** = necessário para sustentar as conclusões como formuladas acima; **O** = opcional (fortalece, mas o artigo se sustenta com a ressalva correspondente). Nenhum dos itens N exige reajustar o modelo principal: os itens 1 e 2 reaproveitam o cache (`cv.pkl`, `bootstrap.pkl`).

| # | Tipo | O que mudar | Por quê | Custo |
|---|---|---|---|---|
| 1 | **N** | Em `resumo_cv`: IC 95% por **bootstrap de proposições** (reamostrar `_G["cluster"]` dos votos, B ≈ 1000, sem reajuste) para as diferenças pareadas de acurácia **e log-loss**: 1D→2D, 2D→3D, 2D vs maioria do partido, 2D vs orientação. Gravar como `RES.cv.ic_ganho_*`. | Os critérios H2a, H2d e E4.1 exigem um IC que respeite a dependência entre votações da mesma proposição. O `dp` entre *folds* aleatórios por célula não faz isso. | Baixo: ~20 linhas; segundos a minutos; usa `pred` do cache. |
| 2 | **N** | Em `etapa_estrutura` / `resumo_bootstrap`: (a) substituir `angulo_entre_governo_e_campo` pelo ângulo entre direções reduzido a [0°, 90°] (e gravar θ_g e θ_c de H1b); (b) recalcular `direcao()`, `r2_dim1_*`, `fracao_distancia_direita_interna` e um novo `dif_UNIÃO_PL_dim1` em cada réplica `U` do bootstrap (com `m["gov"]` fixo) e gravar os IC. No mesmo passe, corrigir o eixo da `fig5`, que diz "bootstrap por votação", mas o bootstrap é por proposição. | Sem a redução módulo 180°, o ângulo atual pode ser lido errado (p. ex., 350° = 10°). H1a e H1b precisam de incerteza; hoje só as diferenças partidárias têm IC. UNIÃO é um dos três partidos-chave de H1a e não tem `dif_*`. | Baixo: ~30 linhas; segundos (U e X já estão no cache). |
| 3 | **N** (para afirmar que a dim2 é um conflito independente) | Acrescentar a `ajustar` um termo quadrático opcional, σ(a_j + b_j·x + c_j·x²) com 1D e prior em c_j, e incluir "1D quadrático" na CV (`DIMS`/`_cv_tarefa`, `t2`) e no IC do item 1. | É o único teste que discrimina E1(a), a ferradura, de E1(b), o conflito independente. Hoje há só a regressão u2 ~ u1 + u1², que é sugestiva, mas não preditiva. Sem ele, a RQ3 só pode ser respondida descritivamente. | Médio: ~25 linhas (função objetivo e gradiente); tempo ≈ uma linha da CV 1D (10 ajustes, minutos). Testar o gradiente com `scipy.optimize.check_grad` no `TESTE_RAPIDO`. |
| 4 | O | IRT 2D com **efeito fixo partido × votação** e pontos centrados no partido (equivalente a `grupos`/`centrar` de `embeddings_deputados.ajustar_irt`) na CV, contra `maioria_partido`. | É a medida mais limpa de "o que as coordenadas individuais acrescentam ao partido" (RQ4). E4.1 com a maioria do partido já responde de forma aproximada. | Médio: reaproveitar a função original; +10 ajustes na CV (~10–15 min). |
| 5 | O (alto valor, fora do escopo mínimo) | Rodar o mesmo `analise.py` parametrizado por legislatura (`--legislatura 56`, `DADOS` variável) depois de **pré-registrar** a previsão de H1 para a 56ª (ver Pré-registro). | É o único teste que quebra a equivalência observacional entre esquerda e governo, a maior ameaça à RQ2. Pode virar uma seção de "validação externa" ou um artigo à parte. | Médio-alto: ~3 min de download + uma execução completa (~1 h); poucas mudanças no código (caminho dos dados; listas `CAMPO`/`DIREITA_OPOS` revistas para 2019–2022, PSL/DEM etc.). |

**Não recomendado agora:** mudar hiperparâmetros, MIN_VOTOS, o corte de minoria ou a regra de rotação depois de ver os resultados. Qualquer mudança desse tipo deve ir para "Desvios" com a justificativa e com os resultados das duas versões.
