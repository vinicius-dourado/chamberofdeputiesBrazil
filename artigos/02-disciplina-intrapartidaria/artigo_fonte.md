# Disciplina à liderança, unidade partidária e dissidência estruturada na Câmara dos Deputados (57ª Legislatura, 2023–2026)

**Resumo.** Quanta disciplina partidária há na Câmara dos Deputados da 57ª Legislatura, onde ela falha e se a indisciplina é ruído ou tem estrutura? Analisamos os {{int:n_votos_plen}} votos nominais dados em {{int:n_votacoes_plen}} votações do Plenário entre {{data:data_primeira}} e {{data:data_ultima}}, cruzados com a orientação das lideranças. Mostramos primeiro um problema de medida: a "orientação do partido" publicada pela Câmara é, na maior parte dos votos do centro e da centro-direita, orientação de **bloco**, e em 2025 um megabloco de Mesa que reunia o PL e a federação do PT praticamente deixou de orientar, de modo que a disciplina medida no 1º semestre de 2025 sobe por artefato de cobertura. Por isso distinguimos a disciplina à liderança (D: voto na direção da orientação aplicável) da unidade partidária (U: voto com a maioria dos demais colegas). A disciplina é alta, {{pct:disc_geral}}% (U: {{pct:unidade_geral}}%), quase total em PSOL, PT, PCdoB e NOVO e mais baixa em União, PSDB e PP; a variação temporal real (em U) é pequena. Em validação cruzada de 5 dobras, um modelo de pontos ideais intrapartidário (efeito fixo partido×votação mais pontos centrados no partido) reduz a log-loss fora da amostra em relação a um modelo só com a posição do partido e a um modelo com propensão individual de desvio sem direção; o ganho é pequeno, mas o intervalo exclui zero. A dimensão de dissidência é interpretável: é governismo relativo (a carga das votações tem o sinal da orientação do Governo em {{pct0:intra1_top100_concorda_orientacao_governo}}% das 100 votações mais carregadas) e a posição intrapartidária anterior a 2026 antecipa a direção de {{pct0:pred_dir_acerto}}% das trocas de partido na janela de 2026. A distância ideológica ao partido, medida no outro biênio, domina os correlatos do desvio; suplência, sexo, idade e tamanho da bancada estadual não se associam a ele. Depois de uma troca individual de partido o desvio cai cerca de {{pp:ev_U_ind:0 a 3_negcoef}} pontos percentuais, sem pré-tendência. Quando o partido da base e o Governo orientam em sentidos opostos, {{pct:div_base_segue_partido}}% dos votos seguem o partido, {{pp:div_cf_excesso}} pontos acima do que as preferências espaciais preveem.

**Palavras-chave:** disciplina partidária; orientação de bancada; pontos ideais; Câmara dos Deputados; presidencialismo de coalizão; votações nominais.

**Abstract.** How much party discipline is there in the 57th Legislature of the Brazilian Chamber of Deputies, where does it break down, and is indiscipline noise or structure? We analyze {{int:n_votos_plen}} roll-call votes cast in {{int:n_votacoes_plen}} floor votes ({{data:data_primeira}}–{{data:data_ultima}}) matched to leadership vote recommendations. We first document a measurement problem: for most centrist and centre-right deputies the recorded "party" recommendation is a **bloc** recommendation, and in 2025 a heterogeneous bloc formed for the Speaker's election (joining PL and the PT federation) almost stopped issuing recommendations, so measured discipline in early 2025 rises as an artefact of coverage. We therefore separate discipline to the leadership (D) from party unity (U: voting with the majority of one's other party colleagues). Discipline is high ({{pct:disc_geral}}%; U {{pct:unidade_geral}}%), nearly complete in PSOL, PT, PCdoB and NOVO and lowest in União, PSDB and PP; genuine change over time (in U) is small. In 5-fold cross-validation, an intra-party ideal-point model (party-by-vote fixed effects plus party-centred ideal points) lowers out-of-sample log-loss relative to a party-position-only model and to a model with a non-directional individual propensity to defect; the gain is small but its interval excludes zero. The dissent dimension is interpretable as relative pro-government voting (vote loadings carry the sign of the government's recommendation in {{pct0:intra1_top100_concorda_orientacao_governo}}% of the 100 highest-loading votes), and pre-2026 intra-party positions anticipate the direction of {{pct0:pred_dir_acerto}}% of the party switches in the 2026 switching window. Ideological distance from the party, measured in the other half of the term, dominates the correlates of defection, while alternate status, sex, age and state delegation size do not. Defection drops by about {{pp:ev_U_ind:0 a 3_negcoef}} percentage points after an individual party switch, with no pre-trend. When a coalition party and the government recommend opposite votes, {{pct:div_base_segue_partido}}% of votes follow the party, {{pp:div_cf_excesso}} points more than spatial preferences predict.

**Keywords:** party discipline; party leadership recommendations; ideal points; Brazilian Chamber of Deputies; coalitional presidentialism; roll-call votes.

---

## 1. Introdução

A disciplina partidária na Câmara dos Deputados é um dos temas mais estudados da ciência política brasileira desde que Figueiredo e Limongi (1999) mostraram, contra a expectativa de partidos fracos e deputados individualistas (Mainwaring, 1999; Ames, 2001), que os deputados votam, em regra, com a orientação dos seus líderes. Este artigo revisita a pergunta na 57ª Legislatura (2023–2027), sob o terceiro governo Lula, com uma estratégia que combina medidas descritivas de disciplina e coesão com modelos de pontos ideais avaliados fora da amostra. As perguntas são quatro: (P1) quanta disciplina há e onde ela falha — por partido, ano, tipo de orientação, tipo de votação e tema; (P2) a indisciplina é ruído ou tem estrutura, isto é, existe uma dimensão intrapartidária de baixa dimensão e interpretável; (P3) quem são os dissidentes sistemáticos e que características se associam ao desvio; e (P4) o que o voto individual acrescenta à orientação do líder — inclusive quando a orientação do partido diverge da do Governo.

O artigo faz quatro contribuições. A primeira é de **medida**. A Câmara publica a orientação de cada bancada — partido, federação ou bloco — e a prática corrente é tratar a orientação aplicável ao deputado como "orientação do partido". Mostramos que, na 57ª Legislatura, a bancada que orienta é o próprio partido ou federação em só {{pct:plen_camada_share_própria}}% dos votos do Plenário; no restante, é um bloco ({{pct:plen_camada_share_bloco}}%), de blocos atribuídos por inferência porque a Câmara trunca seus nomes ({{pct:plen_camada_share_bloco inferido}}%) ou de um bloco heterogêneo formado em 2025 para a eleição da Mesa, que reunia o PL e a federação do PT ({{pct:plen_camada_share_bloco heterogêneo}}%). Esse megabloco orientou em apenas {{int:megabloco_n_votacoes_orientadas}} das {{int:megabloco_n_votacoes}} votações em que foi a bancada aplicável, e a orientação vazia chegou a {{pct:orient_vazia_2025}}% dos votos em 2025. A consequência é que a série temporal da disciplina "à orientação" é, em 2025, um artefato de cobertura. Propomos medir lado a lado a disciplina à liderança (D), estratificada pela fonte da orientação, e a unidade partidária (U), definida pela maioria dos demais colegas, que não depende de registros de orientação.

A segunda contribuição é um **teste explícito de "ruído versus estrutura"** para a indisciplina. Modelos de pontos ideais com efeitos fixos partido×votação já foram usados para separar preferência e pressão partidária (Snyder e Groseclose, 2000; McCarty, Poole e Rosenthal, 2001; Zucco e Lauderdale, 2011), mas a pergunta sobre se o que sobra dentro do partido tem estrutura raramente é posta como um problema de previsão fora da amostra contra linhas de base adequadas. Comparamos seis modelos aninhados, da regra "segue a orientação" a um modelo intrapartidário de duas dimensões, e isolamos o valor de uma propensão individual de desvio sem direção (lealdade) do valor da direção espacial da dissidência.

A terceira é **interpretar** a dimensão intrapartidária pelas votações que mais a carregam, por correlatos externos (alinhamento ao Governo, frentes parlamentares) e por uma validação preditiva: se a posição de um deputado dentro do partido for substantiva, ela deve antecipar quem trocará de partido na janela de 2026 e em que direção. A quarta é tratar a **troca de partido** como estudo de evento com efeitos fixos de deputado e de partido×votação, e a **divergência entre partido e Governo** com uma linha de base contrafactual dada pelas preferências estimadas fora da amostra.

Os resultados sustentam uma leitura de disciplina alta, mas não de deputados indistinguíveis: a maior parte da previsibilidade do voto está na posição coletiva do partido em cada votação, a indisciplina restante não é ruído puro, e sua estrutura é a do eixo governo × oposição recortado dentro de cada partido. Este artigo é um de sete trabalhos irmãos de um mesmo projeto sobre a 57ª Legislatura; os demais tratam de outros blocos (representações dos deputados por temas, frentes e discursos, trajetórias partidárias, entre outros) e são citados aqui apenas como trabalhos relacionados do projeto.

## 2. Duas tradições

### 2.1 Disciplina e coesão no presidencialismo de coalizão

A medida clássica de coesão de um grupo legislativo é o índice de Rice (Rice, 1925), a diferença absoluta entre as proporções de votos Sim e Não do grupo numa votação. O índice tem dois problemas conhecidos. Ele é inflado em grupos pequenos, porque a variabilidade amostral de proporções em bancadas de poucos membros produz valores altos mesmo sem coesão real; Desposato (2005) propõe padronizar o índice pelo valor esperado numa subamostra de tamanho fixo. E ele confunde coesão com consenso: em votações quase unânimes, todo partido parece coeso. Por isso a literatura comparada restringe a análise a votações disputadas ou pondera pela disputa (Carey, 2007; 2009). Carey também distingue *unidade* (votar junto) de *disciplina* (votar com o líder contra a própria preferência), e mostra que a unidade é menor onde há "principais concorrentes" — eleitores, governadores, o presidente — que disputam a lealdade do legislador.

No Brasil, Figueiredo e Limongi (1999) mostraram que a centralização dos trabalhos nos líderes e os poderes de agenda do Executivo produzem disciplina alta e previsível; a orientação do líder é o melhor preditor do voto. A leitura oposta (Mainwaring, 1999; Ames, 2001) enfatizava lista aberta, federalismo e patronagem como fontes de indisciplina. Nicolau (2000) documentou disciplina e base parlamentar no primeiro governo Fernando Henrique a partir das votações nominais. Zucco (2009) e Zucco e Lauderdale (2011) mostraram que o comportamento dos deputados brasileiros responde a influências do Executivo além da ideologia, e Power e Zucco (2009) forneceram âncoras de ideologia partidária. Kam (2009) e Cox e McCubbins (2005) lembram duas cautelas: a dissidência responde ao desalinhamento entre preferência e partido, e a coesão observada é em parte produto do controle de agenda, que evita votações que dividiriam a bancada. Carrubba, Gabel e Hug (2008) acrescentam que votações nominais não são amostra aleatória das decisões, o que vale com força para a Câmara: só {{pct:share_plen_nominais}}% das {{int:n_votacoes_plen_todas}} votações de Plenário da legislatura tiveram votos nominais.

### 2.2 Modelos espaciais: preferência ou partido?

A segunda tradição estima posições latentes dos legisladores a partir das votações (Poole e Rosenthal, 1997; Clinton, Jackman e Rivers, 2004). Krehbiel (1993) argumenta que coesão partidária não prova influência do partido: legisladores com preferências parecidas votam juntos sem pressão alguma. Snyder e Groseclose (2000) propuseram identificar a pressão partidária comparando votações em que ela atuaria com votações lopsided, e McCarty, Poole e Rosenthal (2001) modelaram linhas de corte específicas por partido, concluindo que a segunda linha melhora pouco o ajuste. Black (1948) e Krehbiel (1998) dão a razão para olhar o legislador mediano e os pivôs de maioria qualificada: são eles que decidem o resultado sob regras de maioria. Bafumi et al. (2005) e Lauderdale (2010) discutem identificação e votantes imprevisíveis em modelos de pontos ideais, ponto relevante quando o objeto é justamente o desvio.

Das duas tradições derivamos expectativas e o que as contrariaria. **E1** (Figueiredo e Limongi): disciplina alta (em torno de 90%) e estável; contrariada por variação temporal grande em U. **E2** (Desposato; Carey): o ranking de coesão entre partidos é estável a correções de tamanho e de disputa; contrariada por inversões. **E3** (Krehbiel; Clinton, Jackman e Rivers): se a dissidência for preferência individual estruturada, um modelo com direção espacial intrapartidária prevê melhor que um modelo de lealdade sem direção; contrariada por ganho nulo fora da amostra. **E4** (Zucco): a direção da dissidência é o governismo relativo; contrariada por cargas sem padrão. **E5** (Carey, principais concorrentes): na divergência entre partido e Governo, o partido prevalece além das preferências; contrariada por "excesso de lealdade" nulo.

## 3. Dados

Os dados são os Dados Abertos da Câmara dos Deputados para a 57ª Legislatura, coletados até 11/11/2026 pelos scripts do projeto (`baixar_legislatura.py`). A base de votos tem {{int:n_votos_total}} votos válidos em {{int:n_votacoes_total}} votações nominais (Plenário e comissões), dos quais {{int:n_votos_plen}} em {{int:n_votacoes_plen}} votações do Plenário, dadas por {{int:n_deputados_plen}} deputados (titulares e suplentes), em média {{d1:media_votantes_por_votacao}} votantes por votação. A análise principal usa só o Plenário; comissões entram como robustez. Excluímos os {{int:n_artigo17}} registros "Artigo 17" (o presidente da sessão não vota), votos sem registro e deputados sem partido. A Tabela 1 distribui as votações por tipo — classificado por regras sobre o texto da votação — e ano.

{{tab:tab1_votacoes_tipo_ano}}

**Partido na data.** Usamos o partido do deputado na data de cada votação. O partido "atual" do cadastro reflete a janela partidária de março–abril de 2026, quando ocorreram {{int:n_transicoes_janela2026}} das {{int:n_transicoes_individuais}} trocas individuais de partido da legislatura; usá-lo atribuiria a 2023 filiações de 2026. Das {{int:n_transicoes}} transições registradas, {{int:n_transicoes_fusao}} são fusões ou incorporações (PSC→PODE, PATRIOTA→PRD, PTB→PRD, PROS→SOLIDARIEDADE), não decisões individuais, e são tratadas à parte.

**Orientações.** Para cada voto, o projeto associa a orientação da bancada aplicável ao partido do deputado na data — o próprio partido; senão, a federação; senão, o bloco — e as orientações de Governo, Maioria, Minoria e Oposição. Como a Câmara publica nomes de blocos abreviados e truncados, partidos sem orientação própria são atribuídos ao bloco truncado por inferência (cerca de {{pct0:todos_fonte_share_inferido}}% de todos os votos). Classificamos cada voto em quatro camadas: orientação **própria** (partido ou federação), **bloco** explícito, **bloco inferido** e **bloco heterogêneo** — o bloco que reuniu o PL e a federação PT-PCdoB-PV entre {{data:megabloco_data_ini}} e {{data:megabloco_data_fim}}, um bloco de Mesa e não de coordenação de voto. Orientações desse bloco não contam como orientação do partido. A orientação "Liberado" e a orientação vazia (a liderança não orientou) ficam fora da medida de disciplina.

**Exercício do mandato.** A partir do histórico de situação dos deputados reconstruímos os períodos de exercício e a condição (titular ou suplente) em cada data. O painel valida bem: em média há {{d1:presenca_media_em_exercicio}} deputados em exercício nas datas de votação, e em {{pct:presenca_share_datas_513_mais_menos_5}}% das datas o total fica a no máximo cinco de 513. Isso permite marcar a suplência como variável no tempo, aproximar o motivo do afastamento do titular (ministro, secretário de estado ou de capital, outro) e computar pivôs entre os deputados efetivamente em exercício.

## 4. Método

### 4.1 Disciplina, unidade e coesão

Seja $v_{ij}$ o voto do deputado $i$ na votação $j$, com direção $s(v_{ij})=1$ para Sim e $0$ para Não ou Obstrução (a obstrução é um instrumento de quórum da bancada: um Não de quem recebeu ordem de obstruir não é dissidência quanto ao mérito). Seja $o_{p j}$ a orientação diretiva (Sim, Não ou Obstrução) da bancada aplicável ao partido $p$ do deputado. A **disciplina à liderança** é

$$D = \frac{\sum_{(i,j)\in\mathcal{O}} \mathbf{1}[s(v_{ij}) = s(o_{p(i)j})]}{|\mathcal{O}|},$$

em que $\mathcal{O}$ é o conjunto de votos (Sim, Não, Obstrução ou Abstenção) com orientação diretiva nas camadas própria, bloco ou bloco inferido. Abstenção conta como desvio; a versão estrita (Obstrução ≠ Não) e a versão sem abstenções são robustez. Toda taxa é reportada com sua **cobertura**, $|\mathcal{O}|$ dividido pelos votos válidos.

A **unidade partidária** compara o deputado à maioria dos demais colegas presentes:

$$U = \frac{1}{|\mathcal{U}|}\sum_{(i,j)\in\mathcal{U}} \mathbf{1}\big[s(v_{ij}) = m_{-i,j}\big],\qquad m_{-i,j}=\mathbf{1}\Big[\textstyle\sum_{k\in p(i),k\neq i} s(v_{kj}) > \tfrac{1}{2}n_{-i,j}\Big],$$

definida quando há pelo menos cinco colegas votando e não há empate. U não depende do registro de orientação e cobre {{pct:cobertura_U}}% dos votos (D cobre {{pct:cobertura_D}}%).

A **coesão** de um partido numa votação é o índice de Rice, $R_{pj}=|S_{pj}-N_{pj}|/(S_{pj}+N_{pj})$, calculado em células com pelo menos três votantes. Para corrigir a inflação em bancadas pequenas, usamos o valor esperado do índice numa subamostra sem reposição de $m$ membros (Desposato, 2005), calculado exatamente pela distribuição hipergeométrica:

$$\tilde R_{pj}(m)=\sum_{k=0}^{m}\frac{\binom{S}{k}\binom{N}{m-k}}{\binom{S+N}{m}}\,\frac{|2k-m|}{m},$$

com $m=10$ (principal) e $m=5$; partidos com mediana de votantes abaixo de $m$ não recebem o índice padronizado. A linha de base "sem partido" é o Rice esperado de $m$ votantes independentes que votam Sim com a probabilidade do Plenário naquela votação. Restringimos a média a votações **disputadas** (minoria do Plenário ≥ 10%; {{int:n_votacoes_disputadas}} votações) e, como robustez, a ≥ 20% e ao Rice ponderado pela disputa, $w_j = 1-|2q_j-1|$ (Carey, 2007).

Comparações por tipo de votação, tipo de proposição e tema (temas oficiais da Câmara, multirrótulo com peso $1/k$; cobertura de {{pct0:temas_cobertura}}% das proposições votadas) são feitas em médias brutas e em médias ajustadas por efeitos fixos de partido×ano, porque a composição partidária das votações difere entre categorias.

### 4.2 Pontos ideais: global e intrapartidário

Usamos o estimador de pontos ideais do projeto (regressão logística bilinear penalizada, da família IDEAL/NOMINATE; Clinton, Jackman e Rivers, 2004), sem modificá-lo. Para o voto Sim ($y_{ij}=1$) ou Não/Obstrução ($y_{ij}=0$) do deputado $i$, no período $r(i)$ de filiação a um partido $p$, na votação $j$:

$$\Pr(y_{ij}=1)=\sigma\big(a_j + g_{p j} + \mathbf{b}_j^\top \mathbf{x}_{r}\big),\qquad \mathbf{x}_r=\mathbf{u}_{i}+\boldsymbol{\delta}_r,$$

com penalidades gaussianas (priors) em todos os parâmetros, estimação por máxima verossimilhança penalizada (L-BFGS) e votações com minoria abaixo de 2,5% excluídas. O modelo **global** omite $g$; o **intrapartidário** inclui o efeito fixo partido×votação $g_{pj}$, que absorve a posição do partido em cada votação, e centra os pontos $\mathbf{x}_r$ dentro de cada partido, de modo que sobra só a variação individual. A amostra do modelo tem {{int:irt_n_votos}} votos, {{int:irt_n_votacoes}} votações, {{int:irt_n_periodos}} períodos deputado×partido e {{int:irt_n_celulas}} células partido×votação (mediana de {{d1:irt_celulas_mediana_votantes}} votantes por célula; {{pct0:irt_celulas_share_menos5}}% com menos de cinco).

### 4.3 Ruído ou estrutura: seis modelos fora da amostra

Comparamos, nas mesmas dobras, seis modelos aninhados:

- **M0** — a regra "segue a orientação": a orientação diretiva aplicável; na ausência, a maioria de treino do partido na votação; na ausência, a maioria de treino da votação. A probabilidade é calibrada pela taxa de acerto da regra no treino.
- **M1** — só $a_j+g_{pj}$: a posição coletiva do partido em cada votação (o modelo intrapartidário com variância individual levada a zero por penalidade alta, para manter a mesma penalização de $g$).
- **M2** — M1 mais uma **lealdade individual sem direção**: $\sigma(z^{M1}_{ij}+\rho_i\,d_{pj})$, com $d_{pj}=+1$ se a maioria de treino da célula votou Não e $-1$ se votou Sim; $\rho_i>0$ é a propensão de votar contra a maioria do próprio partido, em qualquer direção.
- **M3** e **M4** — o modelo intrapartidário com uma e duas dimensões.
- **M5** — o modelo global de duas dimensões, sem partido.

M1→M2 mede o valor da lealdade; M2→M3, o valor da **direção** da dissidência; M3→M4, o de uma segunda dimensão; M5→M4, o do partido além das preferências espaciais. A validação cruzada é em cinco dobras sobre células deputado×votação, estratificada por votação (cada votação contribui com cerca de 20% dos seus votos para cada dobra, o que mantém $a_j$, $\mathbf{b}_j$ e $g_{pj}$ estimáveis). A métrica principal é a log-loss; reportamos também Brier, acurácia e a precisão média (AUC-PR) ao ranquear os votos contra a maioria de treino da célula. A acurácia é pouco informativa quando a taxa-base de seguir o partido passa de 88%. Avaliamos em todas as células e nas **células com divisão interna**: partido×votação com pelo menos cinco colegas no treino e pelo menos um voto contra a maioria do partido no treino (definidas só com informação de treino, para não selecionar pela variável dependente). Os intervalos das diferenças de log-loss vêm de bootstrap de deputados (1.000 réplicas) sobre as perdas de teste.

### 4.4 Correlatos do desvio, troca de partido e divergência com o Governo

**Quem desvia.** Ao nível do voto, estimamos um modelo de probabilidade linear

$$\text{desvio}_{ij} = \boldsymbol{\beta}^\top \mathbf{z}_{i}(t) + \gamma_{p(i,t)\,j} + \varepsilon_{ij},$$

em que $\gamma_{pj}$ (efeito fixo partido×votação) absorve a orientação, o conteúdo da votação, o momento e o grau de racha do partido, de modo que $\boldsymbol\beta$ compara deputados do mesmo partido na mesma votação. As covariáveis são suplência em exercício (por motivo do afastamento do titular), sexo, idade, log das cadeiras legais da UF, um indicador de troca individual de partido na legislatura e a distância à mediana do partido na dimensão governo × oposição **estimada com as votações do outro biênio** (2023–24 para votos de 2025–26 e vice-versa), para não usar o desfecho na medida de preferência. Os erros-padrão são agrupados em duas vias, por deputado e por votação (V = V<sub>dep</sub> + V<sub>vot</sub> − V<sub>dep∩vot</sub>). O efeito da UF é testado conjuntamente (Wald, 26 g.l.). Decompomos ainda a variância das taxas brutas de desvio entre deputados em sinal e ruído binomial e na parte entre partidos.

**Troca de partido.** Para os deputados com troca individual, estimamos um estudo de evento

$$\text{desvio}_{ij}=\alpha_i+\gamma_{p(i,t)j}+\sum_{k\neq k_0}\theta_k\,\mathbf{1}[t_j-T_i\in k]+\varepsilon_{ij},$$

com janelas em meses relativos à troca (≤ −13, −12 a −7 [referência], −6 a −4, −3 a −1, 0 a 3, ≥ 4). O efeito fixo de deputado retira a propensão individual, e o de partido×votação retira a tendência geral e o fato de o grupo de referência mudar com a troca. As fusões entram como grupo placebo (troca sem escolha). O desfecho principal é o desvio de U, definido dos dois lados da troca.

**Partido × Governo.** Selecionamos os votos em que a orientação diretiva do partido e a do Governo são opostas, separando os partidos da base dos de oposição permanente (PL e NOVO). Como os líderes escolhem onde divergir, a taxa de "segue o partido" mede ao mesmo tempo autoridade do líder e acompanhamento da bancada. Comparamos então o observado com a probabilidade de seguir o partido prevista, fora da amostra, pelo modelo global sem partido (M5, previsões de validação cruzada): o **excesso de lealdade** é a diferença. Dentro de cada partido×votação, um modelo de probabilidade linear indica quem segue o Governo contra o partido.

### 4.5 Incerteza e reprodutibilidade

Taxas e excessos têm intervalos por bootstrap de votações (1.000 réplicas). Dispersões, pivôs e dissidentes usam bootstrap de votações com reajuste do modelo global ({{int:boot_B_global}} réplicas), com cada réplica alinhada ao ajuste completo por rotação de Procrustes. Todos os números, tabelas e figuras são gerados por `analise.py` a partir de `dados/leg57`; o próprio manuscrito é montado a partir de um modelo em que cada número é uma referência a `resultados.json`.

## 5. Resultados

### 5.1 Quanta disciplina

A disciplina à liderança no Plenário é de {{pct:disc_geral}}% (IC 95%: {{pct:disc_geral_lo}}–{{pct:disc_geral_hi}}), e a unidade partidária, de {{pct:unidade_geral}}%. A Tabela 2 e a Figura 1 mostram a distribuição por partido. PT ({{pct:D_PT}}%), PSOL ({{pct:D_PSOL}}%), PCdoB ({{pct:D_PCdoB}}%) e NOVO ({{pct:D_NOVO}}%) votam quase sempre com a liderança; União ({{pct:D_UNIÃO}}%) e PSDB ({{pct:D_PSDB}}%) estão no outro extremo; PP, PSD, MDB, PODE e AVANTE ficam entre 88% e 90%, REPUBLICANOS em {{pct:D_REPUBLICANOS}}% e o PL em {{pct:D_PL}}%. Esses números reproduzem a ordem de grandeza das taxas prévias do projeto (cerca de 98% em PT, PSOL e NOVO e de 83% a 92% no centrão).

{{tab:tab2_disciplina_partidos}}

![Figura 1](figuras/fig1_disciplina_unidade.png)

*Figura 1 – Disciplina à liderança (D) e unidade (U) por partido, com IC 95% por bootstrap de votações. À direita, a parcela dos votos do partido sob orientação própria (partido ou federação); para os partidos do centro, a orientação é quase toda de bloco. NOVO não tem U porque a bancada nunca reúne cinco colegas votando.*

A fonte da orientação importa. A disciplina é de {{pct:disc_camada_própria}}% quando a orientação é do próprio partido ou federação, {{pct:disc_camada_bloco}}% sob orientação de bloco e {{pct:disc_camada_bloco inferido}}% sob bloco inferido. A orientação própria é a regra só em PSOL, PT, PCdoB, PV, PL e NOVO (e em parte de PSB e PDT); em União, PP, PSD, MDB, REPUBLICANOS, PODE e PSDB, menos de 2% dos votos estão sob orientação do próprio partido. Para esses partidos, o que se chama de disciplina partidária é, na prática, **disciplina ao líder do bloco**. Quando se restringe D à orientação própria, os poucos votos desses partidos sob orientação do próprio partido mostram taxas maiores (por exemplo, PP {{pct:Dp_PP}}%, MDB {{pct:Dp_MDB}}%), coerentes com a ideia de que o partido orienta quando está unido.

A Figura 2 mostra a série semestral. Em D, a disciplina sobe para {{pct:disc_ano_2025}}% em 2025 contra {{pct:disc_ano_2023}}% em 2023. Mas a cobertura de D cai a {{pct0:cobD_ano_2025}}% em 2025 (contra {{pct0:cobD_ano_2023}}% em 2023), porque a liderança aplicável — sobretudo o megabloco — deixou de orientar. Em U, que não depende do registro, 2025 é o ano de **menor** unidade ({{pct:unid_ano_2025}}%, contra {{pct:unid_ano_2023}}% em 2023 e {{pct:unid_ano_2026}}% em 2026). A alta de 2025 é um artefato de cobertura; a variação real no tempo é de cerca de um ponto percentual, compatível com E1.

![Figura 2](figuras/fig2_serie_semestral.png)

*Figura 2 – Disciplina (D, todas as camadas e só orientação própria) e unidade (U) por semestre; abaixo, a cobertura de D (parcela dos votos com orientação diretiva aplicável).*

### 5.2 Onde a disciplina falha

**Tipo de orientação.** A disciplina é maior quando a orientação é Sim ({{pct:disc_orient_Sim}}%) do que quando é Não ({{pct:disc_orient_Não}}%). Sob orientação de Obstrução, a adesão literal é de {{pct:disc_orient_estrita_Obstrução}}%: dos que não obstruíram, a maioria votou Não ({{pct:obstrucao_voto_Não}}% dos votos) — mesma direção, sem aderir à tática — e só {{pct:obstrucao_voto_Sim}}% votaram Sim, contra a bancada. Na medida direcional, a disciplina sob obstrução é de {{pct:disc_orient_Obstrução}}%.

**Liberação.** Quando o partido libera a bancada, a unidade cai de {{pct:unid_orientado}}% (votações orientadas) para {{pct:unid_liberado}}%, e isso ocorre em {{int:unid_lib_vs_ori_partidos_menor}} dos {{int:unid_lib_vs_ori_partidos_total}} partidos analisados. A liberação sinaliza racha, mas não o produz sozinha: mesmo liberados, cerca de quatro em cada cinco deputados votam com a maioria dos colegas.

**Tipo de votação e de proposição.** A Tabela 3 mostra que a disciplina é maior em PECs ({{pct:rec_D_tipo_votacao_PEC (mérito)}}% no mérito) e no mérito de projetos ({{pct:rec_D_tipo_votacao_Mérito (texto principal)}}%) do que em destaques ({{pct:rec_D_tipo_votacao_Destaque (texto)}}%), emendas ({{pct:rec_D_tipo_votacao_Emenda / destaque de emenda}}%) e requerimentos procedimentais ({{pct:rec_D_tipo_votacao_Requerimento procedimental}}%). O ajuste por partido×ano quase não altera os números. Entre tipos de proposição, os projetos de decreto legislativo (PDL) são os mais disciplinados ({{pct:rec_D_tipo_prop_PDL}}%). Na PEC, porém, a ausência é uma forma de desvio, porque a aprovação exige 308 votos Sim. Contando como desvio os membros em exercício ausentes nas {{int:pec_n_votacoes}} votações de mérito de PEC com orientação Sim do partido, a disciplina cai de {{pct:pec_disc_presentes}}% para {{pct:pec_disc_com_ausencia}}% ({{pct:pec_share_ausentes}}% dos membros em exercício estavam ausentes).

{{tab:tab3_recortes}}

**Tema.** A Tabela 4 mostra que a unidade varia de {{pct:tema_U_Homenagens e Datas Comemorativas}}% (homenagens e datas comemorativas, votações de baixo custo para o desvio) e {{pct:tema_U_Política, Partidos e Eleições}}% (política, partidos e eleições, em que interesses eleitorais individuais estão em jogo) a {{pct:tema_U_Agricultura, Pecuária, Pesca e Extrativismo}}% (agricultura) e {{pct:tema_U_Estrutura Fundiária}}% (estrutura fundiária). Uma leitura possível é que nos temas de maior unidade a linha de divisão coincide com a fronteira entre partidos (governo × oposição na questão fundiária e agrícola), enquanto nos de menor unidade há interesses que cortam as bancadas; a análise não testa esse mecanismo.

{{tab:tab4_temas}}

### 5.3 Coesão corrigida

Nas {{int:n_votacoes_disputadas}} votações disputadas, o Rice médio é de {{d2:rice_media_disputadas}}, contra {{d2:base_m10_media_disputadas}} esperados de dez votantes independentes (Figura 3). A correção de Desposato muda pouco os valores e nada o ordenamento: a correlação de postos entre os rankings com m = 10 e m = 5 é {{d2:rice_spearman_m10_m5}}; entre os limiares de disputa de 10% e 20%, {{d2:rice_spearman_disp10_disp20}}; entre o Rice em disputadas e o ponderado por disputa, {{d2:rice_spearman_disp_carey}}. A expectativa E2 se sustenta. O União é o caso extremo: Rice de {{d2:rice_UNIÃO}} nas disputadas, com a bancada rachada (menos de 75% num lado) em {{pct0:racha_UNIÃO}}% delas; PSDB ({{pct0:racha_PSDB}}%), MDB ({{pct0:racha_MDB}}%) e PP ({{pct0:racha_PP}}%) vêm em seguida, enquanto PT e PSOL racham em cerca de 1%.

![Figura 3](figuras/fig3_rice.png)

*Figura 3 – Rice médio nas votações disputadas, bruto e padronizado (m = 10; partidos com mediana de votantes menor que 10 sem valor), e a linha de base de voto aleatório.*

### 5.4 Ruído ou estrutura

A Tabela 5 e a Figura 4 resumem a validação cruzada. Em todas as células, a regra "segue a orientação" (M0) acerta {{pct:cv_todas_M0_acuracia}}% dos votos; a posição coletiva do partido em cada votação (M1) acerta {{pct:cv_todas_M1_acuracia}}%; o modelo intrapartidário de duas dimensões (M4), {{pct:cv_todas_M4_acuracia}}% — valor próximo dos {{pct:prev_irt_intra_acuracia}}% obtidos antes no projeto com Plenário e comissões. Em log-loss, nas células com divisão interna, onde a taxa de desvio da maioria é de {{pct:cv_disputadas_intra_M0_taxa_desvio}}%:

- **M0→M1** reduz a log-loss em {{d3:cvdif_M0_M1}} (IC {{d3:cvdif_M0_M1_lo}}–{{d3:cvdif_M0_M1_hi}}). A posição do partido em cada votação contém muito mais do que a orientação registrada, inclusive onde não há orientação.
- **M1→M2** (lealdade individual sem direção) reduz em {{d3:cvdif_M1_M2}} (IC {{d3:cvdif_M1_M2_lo}}–{{d3:cvdif_M1_M2_hi}}). Alguns deputados desviam sistematicamente mais do que outros.
- **M2→M3** (direção da dissidência) reduz em {{d3:cvdif_M2_M3}} (IC {{d3:cvdif_M2_M3_lo}}–{{d3:cvdif_M2_M3_hi}}). Saber *para que lado* o deputado costuma desviar acrescenta informação além de saber *quanto* ele desvia.
- **M3→M4** (segunda dimensão) acrescenta {{d3:cvdif_M3_M4}} (IC {{d3:cvdif_M3_M4_lo}}–{{d3:cvdif_M3_M4_hi}}).
- **M5→M4** — o modelo global sem partido prevê pior que o intrapartidário em {{d3:cvdif_M5_M4}} (IC {{d3:cvdif_M5_M4_lo}}–{{d3:cvdif_M5_M4_hi}}). Isso é compatível com a existência de um componente partidário além das preferências espaciais, mas não o prova, porque $g_{pj}$ também absorve preferências partidárias específicas de cada votação.

A indisciplina, portanto, não é ruído puro (E3 se sustenta), mas a estrutura é modesta em comparação com o que a posição do partido explica. Os ganhos não dependem de bancadas pequenas: nas células com 50 ou mais votantes, em que $g_{pj}$ não está saturado, a log-loss cai de {{d4:cvfaixa_≥50_M1_logloss}} (M1) para {{d4:cvfaixa_≥50_M2_logloss}} (M2), {{d4:cvfaixa_≥50_M3_logloss}} (M3) e {{d4:cvfaixa_≥50_M4_logloss}} (M4). A exceção são as células com menos de cinco votantes, em que M3 não melhora M2 ({{d4:cvfaixa_<5_M3_logloss}} contra {{d4:cvfaixa_<5_M2_logloss}}). São insensíveis à penalização dos pontos individuais: com $\lambda_d$ de 1 ou 16, em vez de 4, a log-loss de M3 na dobra 0 vai a {{d4:cvsens_M3_lamd1_logloss}} e {{d4:cvsens_M3_lamd16_logloss}}, contra {{d4:cvsens_M3_base_logloss}}. Com penalização forte do efeito fixo partido×votação ($\lambda_g=1$), M1 piora muito ({{d4:cvsens_M1_lamg1_logloss}}, contra {{d4:cvsens_M1_base_logloss}}) e M3 menos ({{d4:cvsens_M3_lamg1_logloss}}): os pontos individuais compensam parte da informação partidária retirada, de modo que a vantagem de M3 sobre M1 não depende de efeitos fixos irrestritos.

{{tab:tab5_validacao}}

![Figura 4](figuras/fig4_validacao_cruzada.png)

*Figura 4 – Redução da log-loss fora da amostra (por voto) ao acrescentar cada componente, nas células partido×votação com divisão interna. IC 95% por bootstrap de deputados.*

### 5.5 O que é a dimensão intrapartidária

A dimensão intrapartidária de um modelo de 1D é o **governismo relativo**. A correlação entre a carga das votações e a orientação do Governo (Sim = +1, Não = −1) é {{d2:intra1_corr_carga_orientacao_governo}}, e entre as 100 votações de maior carga o sinal coincide com o da orientação do Governo em {{pct0:intra1_top100_concorda_orientacao_governo}}%. A posição intrapartidária dos deputados correlaciona {{d2:intra1_corr_rel_global}} com a sua posição relativa à mediana do partido na dimensão global e {{d2:intra1_corr_gov_rel}} com a taxa de voto com o Governo descontada a média do partido. As votações que mais carregam a dimensão (Tabela 11) não são de um tema só. No polo positivo estão votações em que o Governo orientou Sim: a medida provisória sobre a Agência Nacional de Proteção de Dados, a autorização para o Banco do Nordeste criar subsidiárias, a depreciação acelerada e a manutenção do texto em destaques de projetos do Executivo. No polo negativo estão requerimentos procedimentais rejeitados com orientação Não do Governo, uma emenda ao regime de transição da desoneração da folha e o projeto sobre "invasores de propriedades". A dissidência intrapartidária é o eixo governo × oposição recortado dentro de cada partido, o que confirma E4 (Zucco, 2009). Requerimentos procedimentais são {{pct0:intra1_tipo_top100_Requerimento procedimental}}% das 100 votações de maior carga, contra {{pct0:intra1_tipo_todas_Requerimento procedimental}}% do total.

{{tab:tab11_cargas}}

A segunda dimensão do modelo 2D não tem leitura clara: a correlação das suas cargas com a orientação do Governo é {{d2:intra2_dim2_abscorr_carga_gov}} (em módulo), e a associação com a filiação a frentes parlamentares é fraca (por exemplo, {{d2:intra2_dim2_corr_frente_agropecuaria}} com a frente agropecuária e {{d2:intra2_dim2_corr_frente_ambientalista}} com a ambientalista). Na primeira dimensão, dentro do partido, os membros das frentes evangélica ({{d2:intra1_corr_frente_evangelica}}), agropecuária ({{d2:intra1_corr_frente_agropecuaria}}) e de segurança pública ({{d2:intra1_corr_frente_seguranca}}) são menos governistas, e os da ambientalista, mais ({{d2:intra1_corr_frente_ambientalista}}).

**Validação preditiva.** Ajustamos o modelo intrapartidário só com as votações anteriores a 2026 e perguntamos se a posição de cada deputado antecipa a janela de março–maio de 2026. A magnitude da posição (distância ao centro do partido) prevê *quem* troca com AUC de {{d2:pred_auc_abs}} (IC {{d2:pred_auc_abs_lo}}–{{d2:pred_auc_abs_hi}}; {{int:pred_n_trocaram}} trocas entre {{int:pred_n}} deputados), um poder discriminante modesto. O sinal da posição prevê a **direção** da troca — para um partido mais governista ou mais oposicionista que o de origem, segundo as medianas pré-2026 — em {{pct:pred_dir_acerto}}% dos {{int:pred_dir_n}} casos (teste binomial, p = {{d3:pred_dir_p}}), percentual semelhante ao da posição relativa no modelo global ({{pct:pred_dir_global_acerto}}%). A dimensão intrapartidária carrega informação sobre decisões futuras de filiação, mas não muito além do que a posição global relativa já contém.

### 5.6 Quem desvia

A Tabela 10 traz os correlatos do desvio dentro do mesmo partido e da mesma votação. A distância ideológica à mediana do partido, medida no outro biênio, domina: cada unidade de distância na dimensão governo × oposição está associada a {{pp:reg_D_dist_fora_coef}} pontos percentuais a mais de desvio da orientação (IC {{pp:reg_D_dist_fora_lo}}–{{pp:reg_D_dist_fora_hi}}). Os deputados que trocaram de partido individualmente desviam {{pp:reg_U_trocou_ind_coef}} ponto a mais da maioria dos colegas (IC {{pp:reg_U_trocou_ind_lo}}–{{pp:reg_U_trocou_ind_hi}}). Suplência — inclusive a de titulares nomeados ministros —, sexo, idade e o tamanho da bancada estadual não têm associação distinguível de zero ao nível de 5% (o intervalo dos suplentes de secretários toca o zero). As UFs, em conjunto, importam (χ² = {{d1:reg_D_uf_wald}}, 26 g.l.), o que é compatível com principais estaduais concorrentes (Carey, 2009), mas os dados não permitem identificar o mecanismo. A expectativa krehbieliana de que a preferência domina se confirma, mas não esgota o desvio: a disciplina não é só preferência.

{{tab:tab10_regressao}}

A variância das taxas de desvio entre deputados é quase toda sinal — o ruído binomial responde por apenas {{pct0:var_U_share_sinal_compl}}% dela, dado o número de votos por deputado — e {{pct0:var_U_share_intra_no_sinal}}% desse sinal está **dentro** dos partidos ({{pct0:var_D_share_intra_no_sinal}}% para D). Os partidos diferem na disciplina média, mas a maior parte da heterogeneidade está entre colegas de partido.

**Dispersão e dissidentes.** No eixo governo × oposição (Tabela 6, Figura 6), PDT ({{d2:disp_PDT}}), PSB ({{d2:disp_PSB}}), PSOL ({{d2:disp_PSOL}}) e PT ({{d2:disp_PT}}) são compactos; MDB ({{d2:disp_MDB}}), União ({{d2:disp_UNIÃO}}), PP ({{d2:disp_PP}}), PODE ({{d2:disp_PODE}}) e PL ({{d2:disp_PL}}) são dispersos. Os valores diferem dos números prévios do projeto (PDT {{d2:disp_prev_PDT}}, PT {{d2:disp_prev_PT}}, PSOL {{d2:disp_prev_PSOL}}, PL {{d2:disp_prev_PL}}, MDB {{d2:disp_prev_MDB}}, PODE {{d2:disp_prev_PODE}}), que reproduzimos exatamente: aqueles agrupavam os deputados pelo partido **atual**, posterior à janela de 2026, e incluíam comissões. Com o partido na data, o PL fica mais disperso do que se pensava: dos {{int:pl_gov_n}} períodos no PL mais de um desvio-padrão acima da mediana do partido (mais governistas), {{int:pl_gov_saiu}} são de deputados que já não estão no PL ({{pct0:pl_gov_share_saiu}}%, contra {{pct0:pl_resto_share_saiu}}% dos demais). Os intervalos bootstrap dos desvios-padrão tendem a ficar acima da estimativa pontual, porque a reamostragem acrescenta ruído aos pontos; servem para comparar partidos, não como intervalos centrados.

{{tab:tab6_dispersao}}

![Figura 6](figuras/fig6_pontos_ideais.png)

*Figura 6 – Pontos ideais na dimensão governo × oposição por partido (períodos deputado×partido com ≥ 100 votos no Plenário), com a mediana de cada partido, a mediana geral e os quantis de 40% e 60%.*

Entre os {{int:diss_n_elegiveis}} períodos com pelo menos 100 votos, {{int:diss_n_ic_exclui_0}} têm posição cujo IC exclui a mediana do próprio partido. Os mais distantes estão na Tabela 7. No PL, João Carlos Bacelar, Junior Lourenço, Tiririca, Robinson Faria e Júnior Mano são mais governistas que o partido. No sentido oposto estão Sargento Fahur (PSD), Zucco e Messias Donato (REPUBLICANOS), Mauricio Marcon (PODE), Evair Vieira de Melo (PP) e Pezenti (MDB). Entre os nomes apontados antes no projeto, João Carlos Bacelar, Evair Vieira de Melo e Pezenti se confirmam. Bosco Costa, Henrique Júnior e Daniel José são suplentes com {{int:diss_prev_nvotos_Bosco Costa}}, {{int:diss_prev_nvotos_Henrique Júnior}} e {{int:diss_prev_nvotos_Daniel José}} votos no Plenário, abaixo do nosso limiar de 100. Classificar alguém como dissidente com tão poucos votos seria temerário.

{{tab:tab7_dissidentes}}

**Pivôs.** Na legislatura inteira, os cinco deputados mais próximos da mediana são {{raw:pivos_mediana_legislatura}}. José Rocha e Marx Beltrão, apontados antes no projeto, estão entre os mais próximos ({{int:pivo_prev_rank_José Rocha}}º e {{int:pivo_prev_rank_Marx Beltrão}}º); Luiz Gastão e João Leão, em {{int:pivo_prev_rank_Luiz Gastão}}º e {{int:pivo_prev_rank_João Leão}}º; Luiz Carlos Hauly, só em {{int:pivo_prev_rank_Luiz Carlos Hauly}}º. A identidade do mediano é instável: nas réplicas bootstrap, nenhum deputado está entre os cinco mais próximos em mais de {{pct0:pivos_boot_max}}% das vezes ({{raw:pivos_boot_top}}). O que é estável é o **partido** do pivô. Calculados entre os deputados em exercício em cada semestre (Tabela 8), o mediano e os pivôs de 3/5 estão sempre em partidos do centro — REPUBLICANOS, PSD, PP, MDB, PODE, União, PSDB ou SOLIDARIEDADE. Os votos decisivos sob maioria simples e sob quórum de emenda constitucional estão no centro, não nos partidos da base programática do Governo (Black, 1948; Krehbiel, 1998).

{{tab:tab8_pivos}}

### 5.7 Troca de partido

A Figura 5 mostra o estudo de evento para {{int:ev_n_trocadores_ind}} deputados com troca individual. Antes da troca não há tendência: os coeficientes de −6 a −4 meses ({{pp:ev_U_ind:−6 a −4_coef}} p.p.) e de −3 a −1 meses ({{pp:ev_U_ind:−3 a −1_coef}} p.p.) não se distinguem de zero. Não há, portanto, sinal de "saída anunciada" no voto. Depois da troca, o desvio da maioria dos colegas cai {{pp:ev_U_ind:0 a 3_negcoef}} pontos nos primeiros três meses (IC {{pp:ev_U_ind:0 a 3_neglo}}–{{pp:ev_U_ind:0 a 3_neghi}}) e {{pp:ev_U_ind:≥4_negcoef}} pontos depois (IC {{pp:ev_U_ind:≥4_neglo}}–{{pp:ev_U_ind:≥4_neghi}}); em D, as quedas são de {{pp:ev_D_ind:0 a 3_negcoef}} e {{pp:ev_D_ind:≥4_negcoef}} pontos. Os deputados migram para partidos mais próximos de como já votavam. A troca é sobretudo uma correção da filiação à preferência, não uma mudança de comportamento induzida pelo novo partido.

O grupo placebo (fusões) tem só {{int:ev_n_fusao}} deputados com votos nos dois lados da janela de comparação, porque as fusões de PSC e PATRIOTA ocorreram antes de abril de 2023. Por isso não serve de teste: os coeficientes em U são próximos de zero, mas com intervalos largos. A comparação bruta antes/depois, sem controles ({{pct:troca_bruto_antes}}% para {{pct:troca_bruto_depois}}% de disciplina entre {{int:troca_bruto_n}} trocadores), superestimaria o efeito, por confundir a troca com a queda de cobertura de 2025 e a recuperação de 2026.

![Figura 5](figuras/fig5_troca_partido.png)

*Figura 5 – Desvio da maioria dos colegas (U) em torno da troca de partido, relativo à janela de −12 a −7 meses. Efeitos fixos de deputado e de partido×votação; IC 95% com erros agrupados por deputado e por votação.*

### 5.8 Partido ou Governo?

Há {{int:div_n_votos}} votos, em {{int:div_n_votacoes}} votações, em que a orientação do partido e a do Governo são opostas; {{int:div_base_n}} são de deputados de partidos que não o PL e o NOVO. Nesses votos, {{pct:div_base_segue_partido}}% seguem o partido e {{pct:div_base_segue_governo}}% o Governo (Figura 7). O padrão varia muito. União ({{pct:div_UNIÃO_segue_partido}}%), PP ({{pct:div_PP_segue_partido}}%), REPUBLICANOS ({{pct:div_REPUBLICANOS_segue_partido}}%) e MDB ({{pct:div_MDB_segue_partido}}%) quase sempre ficam com o partido. No PSB ({{pct:div_PSB_segue_partido}}%) e no PDT ({{pct:div_PDT_segue_partido}}%), partidos da base programática, a bancada parece dividir-se ao meio. Mas a maior parte desses votos está sob orientação de bloco **inferido** ({{pct0:div_PSB_share_inferido}}% no PSB e {{pct0:div_PDT_share_inferido}}% no PDT), e a adesão sob essa camada é baixa ({{pct:div_PSB_inferido_segue_partido}}% e {{pct:div_PDT_inferido_segue_partido}}%). Quando a orientação contrária ao Governo é do próprio partido, a adesão sobe para {{pct:div_PSB_propria_segue_partido}}% no PSB ({{int:div_PSB_propria_n}} votos) e {{pct:div_PDT_propria_segue_partido}}% no PDT ({{int:div_PDT_propria_n}} votos). O "racha" desses partidos diante do Governo é, em boa parte, um artefato da atribuição a blocos truncados. A camada importa: a adesão ao partido é de {{pct:div_base_camada_própria_segue_partido}}% quando a orientação é própria, {{pct:div_base_camada_bloco_segue_partido}}% quando é de bloco e {{pct:div_base_camada_bloco inferido_segue_partido}}% quando é de bloco inferido.

As preferências espaciais (M5, fora da amostra) já preveem que {{pct:div_cf_previsto}}% desses votos sigam o partido; o observado é {{pct:div_cf_observado}}%. O **excesso de lealdade** é de {{pp:div_cf_excesso}} pontos (IC {{pp:div_cf_excesso_lo}}–{{pp:div_cf_excesso_hi}}), o que confirma E5: o partido prevalece além das preferências, mas a maior parte da lealdade nas divergências é congruência de preferências. O excesso é maior no PSOL ({{pct:div_cf_PSOL_obs}}% observado contra {{pct:div_cf_PSOL_prev}}% previsto), cuja orientação é sempre da própria federação: quando diverge do Governo, a bancada acompanha o partido mesmo onde as preferências estimadas indicariam alguns votos com o Governo. PSB ({{pct:div_cf_PSB_obs}}% contra {{pct:div_cf_PSB_prev}}%) e PDT ({{pct:div_cf_PDT_obs}}% contra {{pct:div_cf_PDT_prev}}%) também mostram excesso, com a ressalva de atribuição feita acima. Quando o partido libera a bancada, os deputados da base seguem o Governo em {{pct:liberado_base_segue_governo}}% dos votos.

Dentro do mesmo partido e da mesma votação, quem é mais governista que o partido no outro biênio segue mais o Governo contra o partido: {{pp:div_reg_rel_gov_fora_coef}} pontos por unidade de posição relativa (IC {{pp:div_reg_rel_gov_fora_lo}}–{{pp:div_reg_rel_gov_fora_hi}}). Suplentes de titulares ministros não seguem mais o Governo ({{pp:div_reg_sup_ministro_coef}} pontos; IC {{pp:div_reg_sup_ministro_lo}}–{{pp:div_reg_sup_ministro_hi}}), contra a hipótese de que o ministro "empresta" ao Governo o voto do seu suplente.

![Figura 7](figuras/fig7_partido_governo.png)

*Figura 7 – Partidos da base: parcela dos votos que segue o partido e o Governo quando as orientações são opostas, e parcela que seguiria o partido segundo as preferências espaciais estimadas fora da amostra (M5). À direita, número de votos.*

## 6. Robustez

A Tabela 9 refaz a disciplina sob oito decisões de medida. Sem as orientações inferidas de blocos, a disciplina geral passa de {{pct:rob_Principal (direcional; própria + bloco + inferido)_geral}}% para {{pct:rob_Sem orientações inferidas de bloco_geral}}%, e a correlação de postos entre partidos é {{d2:rob_spearman_Sem orientações inferidas de bloco}}. As maiores mudanças estão em PSB e PDT (de {{pct:D_PSB}}% para {{pct:rob_seminf_PSB}}% e de {{pct:D_PDT}}% para {{pct:rob_seminf_PDT}}%), cuja orientação inferida vinha de blocos de que não eram o eixo, e no AVANTE (de {{pct:D_AVANTE}}% para {{pct:rob_seminf_AVANTE}}%). O ranking só se altera de forma relevante quando se restringe a medida à orientação própria (ρ = {{d2:rob_spearman_Só orientação própria (partido/federação)}}), que cobre {{pct0:plen_camada_share_própria}}% dos votos e deixa os partidos do centro com amostras pequenas e selecionadas. Incluir o bloco heterogêneo, excluir fevereiro–outubro de 2025, usar a definição estrita, excluir abstenções ou incluir comissões muda a disciplina geral em menos de meio ponto, com ρ ≥ {{d2:rob_spearman_Estrita (Obstrução ≠ Não)}}.

{{tab:tab9_robustez}}

Na análise partido × Governo, sem orientações inferidas, a adesão ao partido nos partidos da base vai de {{pct:div_base_segue_partido}}% para {{pct:div_base_segue_partido_seminf}}%. O Rice é estável a m, ao limiar de disputa e à ponderação (seção 5.3), e a validação cruzada, à penalização (seção 5.4). Os pontos ideais globais estimados só com o Plenário correlacionam {{d3:conf_corr_dim1_repo}} com os do projeto, que incluíam comissões.

## 7. Limitações

**Só votações nominais.** Só {{pct:share_plen_nominais}}% das votações do Plenário foram nominais, e a escolha de quais votações são nominais é estratégica (Carrubba, Gabel e Hug, 2008): votações simbólicas em que a bancada estava unida, ou em que o líder preferiu não expor a divisão, ficam fora. Nossas taxas valem para o universo nominal.

**Ausências.** O voto nominal registra só quem votou. O painel de exercício permite contar quem estava em exercício e não votou, mas não o motivo. A análise de PEC mostra que, onde a ausência tem efeito de voto, ela é relevante ({{pct:pec_share_ausentes}}% dos membros em exercício). Não estimamos ausência seletiva em geral.

**Orientação registrada não é pressão.** A orientação é o sinal público do líder; negociação, sanções e recompensas (cargos, emendas) não são observadas. Para os partidos do centro, a orientação é de bloco, e a atribuição a blocos truncados é mecânica. A orientação vazia significa que a liderança não orientou. A unidade U contorna a dependência do registro, mas não distingue disciplina de coesão de preferências (Krehbiel, 1993). A distância medida no outro biênio e o contrafactual de M5 atenuam esse problema sem eliminá-lo.

**Retrato estático.** Os pontos ideais são fixos por período deputado×partido. A posição de um deputado que não trocou de partido não pode variar ao longo de quatro anos, e o modelo intrapartidário assume um mesmo vetor de cargas para todos os partidos.

**Desenho causal limitado.** O estudo de evento compara o deputado com ele mesmo e com os colegas na mesma votação, mas a decisão de trocar é endógena, e o período pós-janela tem só {{int:n_votacoes_pos_janela}} votações, em ano eleitoral. O grupo placebo de fusões é pequeno demais para servir de teste. A associação com a suplência usa um pareamento aproximado entre suplente e titular (mesma UF, ±10 dias), porque os Dados Abertos não ligam um ao outro.

**Classificação de votações.** O tipo de votação vem de regras sobre o texto da descrição, sem validação manual sistemática. Os temas cobrem {{pct0:temas_cobertura}}% das proposições votadas.

## 8. Discussão

O quadro que emerge é compatível com a tese de Figueiredo e Limongi: a disciplina é alta e estável, e a orientação coletiva (aqui, a posição do partido em cada votação) é de longe a melhor informação sobre o voto de um deputado. Mas dois achados qualificam essa leitura.

O primeiro é de medida, com consequência substantiva. Na Câmara de 2023–2026, a orientação aplicável à maioria dos deputados do centro não é do partido, e sim do bloco. A orientação de partido é a regra só nas pontas (PT e federação, PSOL, PL, NOVO). Os partidos do centro delegam a orientação ao líder do bloco e, quando orientam por conta própria, orientam onde estão unidos. Os blocos formados para a eleição da Mesa — o de 2025 reunia governo e oposição — mostram que a "bancada" que orienta é, por vezes, uma ficção regimental. Estudos de disciplina que tomem a orientação registrada como orientação do partido, sem estratificar pela fonte e sem reportar a cobertura, arriscam medir a organização dos blocos e o calendário da Mesa, e não a disciplina.

O segundo é que a indisciplina tem uma estrutura que a literatura espacial prevê. Ela tem direção e não é só ruído ou idiossincrasia: dentro de cada partido, deputados se ordenam de forma estável entre mais e menos governistas. Essa ordem prevê o voto fora da amostra, antecipa a direção das trocas de partido e explica quem segue o Governo contra o partido. O eixo é o mesmo que separa os partidos entre si; a dissidência intrapartidária é o eixo interpartidário visto de dentro. É isso que torna os partidos do centro — União, PP, PSD, MDB, REPUBLICANOS — ao mesmo tempo os mais heterogêneos e os pivôs da Casa. A heterogeneidade interna permite ao Governo construir maiorias votação a votação com parte de suas bancadas, e o mediano e os pivôs de 3/5 estão sempre nesses partidos.

Os limites também são claros. O ganho preditivo da dimensão individual é pequeno perto do da posição partidária. A distância ideológica explica o desvio muito mais do que a suplência ou o estado, e o "excesso de lealdade" nas divergências com o Governo é de poucos pontos. A autoridade dos líderes, no sentido de Krehbiel, existe, mas atua sobre uma margem estreita, porque a maior parte do trabalho de alinhamento já foi feita pela seleção — de quem entra em cada partido, de quais votações são nominais e de onde o líder escolhe divergir.

## 9. Conclusão

Na 57ª Legislatura, os deputados votam com a liderança em cerca de nove de cada dez votos nominais, e a variação real ao longo do tempo é pequena. A disciplina medida pela orientação registrada, porém, depende de quem orienta: para o centro, o bloco; em 2025, quase ninguém. A unidade com os colegas é a medida estável. A indisciplina restante tem estrutura de baixa dimensão — governismo relativo dentro de cada partido —, prevê o voto fora da amostra e antecipa trocas de partido. A troca reduz o desvio, como correção da filiação à preferência, e, quando partido e Governo divergem, os deputados da base seguem o partido um pouco além do que suas preferências preveriam. Ficam pendentes a extensão a outras legislaturas, para separar o que é próprio do terceiro governo Lula e da era dos megablocos, a incorporação de dados eleitorais e de emendas para testar os mecanismos do voto pessoal e um modelo dinâmico de pontos ideais.

## Referências

AMES, Barry. *The Deadlock of Democracy in Brazil*. Ann Arbor: University of Michigan Press, 2001.

BAFUMI, Joseph; GELMAN, Andrew; PARK, David K.; KAPLAN, Noah. Practical Issues in Implementing and Understanding Bayesian Ideal Point Estimation. *Political Analysis*, v. 13, n. 2, p. 171–187, 2005.

BLACK, Duncan. On the Rationale of Group Decision-making. *Journal of Political Economy*, v. 56, n. 1, p. 23–34, 1948.

CAMERON, A. Colin; GELBACH, Jonah B.; MILLER, Douglas L. Robust Inference with Multiway Clustering. *Journal of Business & Economic Statistics*, v. 29, n. 2, p. 238–249, 2011.

CAREY, John M. Competing Principals, Political Institutions, and Party Unity in Legislative Voting. *American Journal of Political Science*, v. 51, n. 1, p. 92–107, 2007.

CAREY, John M. *Legislative Voting and Accountability*. Cambridge: Cambridge University Press, 2009.

CARRUBBA, Clifford J.; GABEL, Matthew; HUG, Simon. Legislative Voting Behavior, Seen and Unseen: A Theory of Roll-Call Vote Selection. *Legislative Studies Quarterly*, v. 33, n. 4, p. 543–572, 2008.

CLINTON, Joshua; JACKMAN, Simon; RIVERS, Douglas. The Statistical Analysis of Roll Call Data. *American Political Science Review*, v. 98, n. 2, p. 355–370, 2004.

COX, Gary W.; McCUBBINS, Mathew D. *Setting the Agenda: Responsible Party Government in the U.S. House of Representatives*. Cambridge: Cambridge University Press, 2005.

DESPOSATO, Scott W. Correcting for Small Group Inflation of Roll-Call Cohesion Scores. *British Journal of Political Science*, v. 35, n. 4, p. 731–744, 2005.

FIGUEIREDO, Argelina Cheibub; LIMONGI, Fernando. *Executivo e Legislativo na nova ordem constitucional*. Rio de Janeiro: Editora FGV, 1999.

KAM, Christopher J. *Party Discipline and Parliamentary Politics*. Cambridge: Cambridge University Press, 2009.

KREHBIEL, Keith. Where's the Party? *British Journal of Political Science*, v. 23, n. 2, p. 235–266, 1993.

KREHBIEL, Keith. *Pivotal Politics: A Theory of U.S. Lawmaking*. Chicago: University of Chicago Press, 1998.

LAUDERDALE, Benjamin E. Unpredictable Voters in Ideal Point Estimation. *Political Analysis*, v. 18, n. 2, p. 151–171, 2010.

MAINWARING, Scott P. *Rethinking Party Systems in the Third Wave of Democratization: The Case of Brazil*. Stanford: Stanford University Press, 1999.

McCARTY, Nolan; POOLE, Keith T.; ROSENTHAL, Howard. The Hunt for Party Discipline in Congress. *American Political Science Review*, v. 95, n. 3, p. 673–687, 2001.

NICOLAU, Jairo. Disciplina partidária e base parlamentar na Câmara dos Deputados no primeiro governo Fernando Henrique Cardoso (1995-1998). *Dados*, v. 43, n. 4, 2000. [verificar páginas]

POOLE, Keith T.; ROSENTHAL, Howard. *Congress: A Political-Economic History of Roll Call Voting*. New York: Oxford University Press, 1997.

POWER, Timothy J.; ZUCCO, Cesar. Estimating Ideology of Brazilian Legislative Parties, 1990–2005: A Research Communication. *Latin American Research Review*, v. 44, n. 1, p. 218–245, 2009.

RICE, Stuart A. The Behavior of Legislative Groups: A Method of Measurement. *Political Science Quarterly*, v. 40, n. 1, p. 60–72, 1925.

SNYDER, James M.; GROSECLOSE, Tim. Estimating Party Influence in Congressional Roll-Call Voting. *American Journal of Political Science*, v. 44, n. 2, p. 193–211, 2000.

ZUCCO, Cesar. Ideology or What? Legislative Behavior in Multiparty Presidential Settings. *The Journal of Politics*, v. 71, n. 3, p. 1076–1092, 2009.

ZUCCO, Cesar; LAUDERDALE, Benjamin E. Distinguishing Between Influences on Brazilian Legislative Behavior. *Legislative Studies Quarterly*, v. 36, n. 3, p. 363–396, 2011.

## Apêndice A – Reprodutibilidade

`python artigos/02-disciplina-intrapartidaria/analise.py` (da raiz do repositório) lê `dados/leg57/*.parquet`, `dados/leg57/embeddings/` (só para conferência) e o cache de temas em `dados_aux/temas_proposicoes_votadas.csv`, baixado uma vez da API da Câmara. A partir disso grava `resultados.json` ({{int:n_chaves}} números), `tabelas/*.md` e `figuras/*.png` e monta este `artigo.md` a partir de `artigo_fonte.md`. Os ajustes de pontos ideais ficam em cache em `dados_aux/cache/` (fora do git). A primeira execução completa leva da ordem de 15 minutos em 4 núcleos; as seguintes, cerca de {{int:tempo_execucao_s}} segundos. As sementes são fixas. O desenho das análises foi registrado antes da execução em `pipeline/stage1_blueprint.md`.
