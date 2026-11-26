<!-- Arquivo gerado por analise.py a partir de artigo_fonte.md; não edite à mão. -->
# Disciplina à liderança, unidade partidária e dissidência estruturada na Câmara dos Deputados (57ª Legislatura, 2023–2026)

**Resumo.** Analisamos 454.829 votos nominais em 1.126 votações do Plenário da Câmara dos Deputados (14/03/2023 a 14/10/2026) para medir a disciplina partidária e testar se a indisciplina tem estrutura. Primeiro, mostramos um problema de medida: para os partidos de centro, a orientação registrada é a do bloco, e em 2025 o registro de um megabloco que reunia o PL e a federação do PT ficou quase sempre vazio, embora as notas taquigráficas mostrem os partidos orientando em Plenário. A disciplina à liderança medida pelo registro sobe em 2025 por artefato; a unidade com a maioria dos colegas, que não depende do registro, cai em quatro partidos de centro (PSD, MDB, PP e União). Por isso usamos, ao lado da disciplina à liderança (D, 90,9%), a unidade (U, 89,5%). Segundo, em validação cruzada, a direção individual da dissidência melhora a previsão do voto além de uma propensão individual de desvio com a mesma estrutura de parâmetros; o ganho é pequeno, mas o intervalo exclui zero. A dimensão de dissidência é o eixo governo–oposição recortado dentro de cada partido. A distância espacial ao partido domina os correlatos do desvio; depois de trocar de partido, o deputado passa a votar mais com os novos colegas; e, quando partido e Governo divergem, a base segue o partido além do que preveem as preferências estimadas.

**Palavras-chave:** disciplina partidária; orientação de bancada; blocos parlamentares; pontos ideais; Câmara dos Deputados; votações nominais.

**Abstract.** We analyse 454,829 roll-call votes in 1,126 floor votes of the Brazilian Chamber of Deputies (14 March 2023 to 14 October 2026) to measure party discipline and test whether indiscipline is structured. First, we document a measurement problem: for centrist parties the recorded recommendation is the bloc's, and in 2025 the record of a mega-bloc joining PL and the PT federation was almost always empty, although the floor transcripts show the parties issuing recommendations. Discipline measured from the record rises in 2025 as an artefact, while unity with the majority of one's colleagues, which does not depend on the record, falls in four centrist parties (PSD, MDB, PP and União). We therefore report, next to discipline to the leadership (D, 90.9%), party unity (U, 89.5%). Second, in cross-validation, the individual direction of dissent improves vote prediction beyond an individual propensity to defect with the same parameter structure; the gain is small but its interval excludes zero. The dissent dimension is the government–opposition axis within each party. Spatial distance from the party dominates the correlates of defection; after switching parties, deputies vote more with their new colleagues; and when party and government disagree, coalition deputies follow the party beyond what estimated preferences predict.

**Keywords:** party discipline; party recommendations; legislative blocs; ideal points; Brazilian Chamber of Deputies; roll-call votes.

---

## 1. Introdução

Desde Figueiredo e Limongi (1999), sabe-se que os deputados brasileiros votam, em regra, com a orientação de seus líderes, contra a expectativa de partidos fracos e deputados individualistas (Mainwaring, 1999; Ames, 2001). Este artigo revisita a questão na 57ª Legislatura (2023–2027), sob o terceiro governo Lula, com duas perguntas. A primeira é de **medida**: quanta disciplina há, e o que a orientação registrada pela Câmara de fato mede? A segunda é de **estrutura**: a indisciplina é ruído ou tem uma direção individual estável e interpretável, que acrescenta algo à posição coletiva do partido? Duas perguntas derivadas completam a análise: quem desvia e o que acontece quando o partido e o Governo orientam em sentidos opostos.

A contribuição de medida parte de uma constatação sobre o registro. A Câmara publica a orientação de cada bancada — partido, federação ou bloco —, e a prática é tratar a orientação aplicável ao deputado como "orientação do partido". Na 57ª Legislatura, a bancada aplicável é o próprio partido ou federação em só 33,9% dos votos; nos demais, é um bloco. Entre fevereiro e agosto de 2025, a bancada aplicável à maioria dos deputados foi um megabloco formado em fevereiro de 2025, no início do biênio da nova Mesa, que reunia o PL e a federação do PT. A linha desse bloco no registro ficou vazia em 199 das 227 votações, e não houve nenhuma linha própria do PL ou da federação do PT (0 linhas). As notas taquigráficas, porém, mostram os partidos orientando ("o PL orienta 'sim'"). Reconstruímos essas orientações faladas para mostrar que houve orientação onde o registro está vazio, e mostramos que a disciplina medida pelo registro sobe em 2025 por artefato, enquanto a unidade com os colegas cai em quatro partidos de centro. Propomos reportar lado a lado a disciplina à liderança (D), estratificada pela fonte da orientação e acompanhada da cobertura, e a unidade partidária (U), definida pela maioria dos demais colegas, que não depende do registro.

A contribuição de estrutura é um teste fora da amostra. Comparamos uma sequência de modelos, da regra "segue a orientação" a modelos de pontos ideais intrapartidários, e isolamos o valor da **direção** individual da dissidência do valor de uma **propensão** individual a desviar com a mesma estrutura de parâmetros. Interpretamos a dimensão resultante pelas votações que mais a carregam e por uma validação externa: as trocas de partido de 2026. Tratamos a troca de partido como estudo de evento e a divergência entre partido e Governo com contrafactuais dados pelas preferências estimadas.

## 2. Literatura e expectativas

**Disciplina, coesão e agenda.** O índice de Rice (Rice, 1925) mede a coesão de um grupo numa votação. Ele é inflado em grupos pequenos (Desposato, 2005) e confunde coesão com consenso, o que leva a restringir a análise a votações disputadas ou a ponderar pela disputa. Carey (2007; 2009) mostra que a unidade de voto é menor onde "principais concorrentes" — eleitores, governadores, o presidente — disputam a lealdade do legislador; seguindo Krehbiel (1993), distinguimos *unidade* (votar junto) de *disciplina* no sentido estrito (votar com o líder contra a própria preferência). A medida D adiante é adesão à orientação; só o excesso de lealdade da seção 5.8 aproxima o componente contra a preferência. No Brasil, Figueiredo e Limongi (1999) atribuem a disciplina à centralização dos trabalhos no Colégio de Líderes combinada aos poderes de agenda do Executivo, como medidas provisórias e pedidos de urgência (resumo de fontes secundárias; a lista completa dos instrumentos no original fica [verificar]). Amorim Neto, Cox e McCubbins (2003) analisam o poder de agenda das coalizões na Câmara. Pereira e Mueller (2004) ligam o voto com o Governo à execução de emendas orçamentárias. Cheibub, Figueiredo e Limongi (2009) discutem partidos e governadores como determinantes do comportamento legislativo. Nicolau (2000) documenta a disciplina no primeiro governo Fernando Henrique. A coesão observada é também produto da agenda (Cox e McCubbins, 2005) e da seleção de quais votações são nominais (Carrubba, Gabel e Hug, 2008): só 16,5% das 6.855 votações de Plenário da legislatura tiveram votos nominais.

**Preferência ou partido.** Krehbiel (1993) argumenta que coesão não prova influência do partido. Snyder e Groseclose (2000) comparam votações disputadas e lopsided para estimar a pressão partidária, e McCarty, Poole e Rosenthal (2001) modelam linhas de corte por partido. Clinton, Jackman e Rivers (2004) formalizam a estimação de pontos ideais; Bafumi et al. (2005) e Lauderdale (2010) tratam de identificação e de votantes imprevisíveis. Zucco (2009) e Zucco e Lauderdale (2011) mostram que o comportamento dos deputados brasileiros responde a influências do Executivo além da ideologia; Power e Zucco (2009) fornecem âncoras de ideologia partidária. Minozzi e Volden (2013) estudam quem atende ao chamado do partido. Sobre trocas de partido, Desposato (2006) explica as migrações na Câmara por ambição e ideologia, Heller e Mershon (2005) as estudam na Itália, e Nokken (2000) estuda a dinâmica da lealdade e da defecção de legisladores no Congresso americano, inclusive dos que trocam de partido. Black (1948) e Krehbiel (1998) justificam olhar o mediano e os pivôs de maioria qualificada.

**Expectativas e critérios de falha.** O plano de análise foi escrito depois da análise descritiva preliminar. Por isso E1 e E2 são leituras descritivas, e E3 a E5 foram especificadas antes das análises que as testam (Apêndice B). Os **limiares numéricos de falha**, porém, foram fixados na revisão, depois de conhecidos os resultados, e devem ser lidos como critérios declarados, não pré-registrados.

- **E1** (Figueiredo e Limongi): disciplina alta e estável. *Falha* se a diferença entre o ano de maior e o de menor unidade (U) passar de 3 pontos percentuais.
- **E2** (Desposato; Carey): o ordenamento dos partidos por coesão não depende de tamanho nem de disputa. *Falha* se a correlação de postos entre o Rice bruto e o padronizado, ou entre limiares de disputa, ficar abaixo de 0,8.
- **E3** (Krehbiel; Clinton, Jackman e Rivers): se a dissidência é preferência individual estruturada, a direção individual prevê melhor que uma propensão a desviar com a mesma estrutura de parâmetros. *Falha* se o IC da redução de log-loss de M2b para M3 incluir zero.
- **E4** (Zucco): a dimensão de dissidência é o eixo governo–oposição. *Falha* se a correlação entre a carga das votações e a orientação do Governo ficar abaixo de 0,5.
- **E5** (Figueiredo e Limongi contra Carey): quando partido e Governo divergem, a liderança do partido prevalece além das preferências (excesso de lealdade positivo); os principais concorrentes de Carey preveem excesso menor onde a orientação vem do bloco. *Falha* se o IC do excesso incluir zero nos dois contrafactuais.

## 3. Dados

Os dados são os Dados Abertos da Câmara para a 57ª Legislatura, coletados até 11/11/2026: 471.314 votos válidos em 1.602 votações nominais, dos quais 454.829 em 1.126 votações do Plenário, de 644 deputados (titulares e suplentes). Excluímos os 1.045 registros "Artigo 17" (o presidente da sessão não vota), votos sem registro e deputados sem partido. Usamos o partido do deputado **na data** de cada votação. O cadastro "atual" reflete a janela partidária de 2026: entre março e maio de 2026 ocorreram 139 das 191 trocas individuais de partido. Das 210 transições registradas, 19 são fusões ou incorporações (PSC→PODE, PATRIOTA→PRD, PTB→PRD, PROS→SOLIDARIEDADE), tratadas à parte. A Tabela 1 distribui as votações por tipo e ano. O tipo é atribuído por regras sobre o texto da votação; numa amostra estratificada de 120 votações codificadas pelo assistente de IA que conduziu a análise, a partir da leitura das descrições, sem segundo codificador (das quais 119 codificáveis), as regras acertam 94,1%, e os erros se concentram em recursos e emendas de redação.

**Tabela 1 – Votações nominais do Plenário por tipo e ano (57ª Legislatura, 14/03/2023 a 14/10/2026)**

| Tipo de votação | 2023 | 2024 | 2025 | 2026 | Total |
|---|---|---|---|---|---|
| Destaque (texto) | 53 | 41 | 83 | 16 | 193 |
| Emenda / destaque de emenda | 49 | 45 | 38 | 13 | 145 |
| Mérito (texto principal) | 55 | 51 | 100 | 24 | 230 |
| PEC (mérito) | 5 | 6 | 11 | 8 | 30 |
| Requerimento procedimental | 74 | 71 | 148 | 31 | 324 |
| Urgência | 64 | 59 | 48 | 33 | 204 |
| Total | 300 | 273 | 428 | 125 | 1126 |

*Tipo atribuído por regras sobre o texto de votacoes.descricao (ver Método).*

**Orientações registradas.** Para cada voto, associamos a orientação da bancada aplicável ao partido do deputado na data — o próprio partido; senão, a federação; senão, o bloco — e as orientações do Governo, da Maioria, da Minoria e da Oposição. Como a Câmara publica nomes de blocos truncados, partidos sem orientação própria são atribuídos ao bloco por inferência (cerca de 18% de todos os votos). Classificamos cada voto em camadas, com as parcelas dos votos do Plenário:

- **própria** (partido ou federação): 33,9%;
- **bloco**: 36,8%;
- **bloco inferido**: 11,2%;
- **bloco heterogêneo**: 18,1%. É o megabloco de 11/02/2025 a 19/08/2025, que não conta como orientação do partido.

"Liberado" e orientação vazia ficam fora da medida de disciplina.

**Orientações faladas.** Extraímos das transcrições dos discursos as orientações anunciadas em Plenário ("o PL orienta 'sim'") e associamos cada uma à primeira votação nominal registrada até 45 minutos depois. Foram 939 orientações associadas a votações (6.216 dos votos no megabloco vêm de falas com o verbo "orienta"). Onde há registro oficial da orientação do próprio partido (563 casos), fala e registro coincidem em 94,1%. Numa conferência de 50 associações sorteadas, feita pelo mesmo assistente de IA a partir da leitura das falas e das votações, sem segundo codificador, o objeto da fala (retirada de pauta, destaque, urgência, mérito) é compatível com a votação associada em 47 e incerto em 3. O método tem vieses conhecidos. Capta só a fórmula "o partido orienta/vota ‘x’", não as orientações dadas de outro modo ou só no painel. Pode associar a fala à votação errada quando há várias votações em sequência. E sobrerrepresenta partidos cujos líderes falam mais. Por isso a usamos como evidência de que houve orientação, e não como medida do nível de disciplina.

**Exercício do mandato.** A partir do histórico de situação dos deputados, reconstruímos os períodos de exercício e a condição (titular ou suplente) em cada data. Nas 242 datas com votação nominal há em média 513,2 deputados em exercício, e em 99,2% delas o total fica a no máximo cinco de 513.

## 4. Método

### 4.1 Disciplina, unidade e coesão

Seja $s(v_{ij})=1$ para Sim e $0$ para Não ou Obstrução no voto do deputado $i$ na votação $j$, e $o_{pj}$ a orientação diretiva da bancada aplicável ao partido $p$. A obstrução é um instrumento de quórum: um Não de quem recebeu ordem de obstruir não é dissidência quanto ao mérito. A **disciplina à liderança** é

$$D = \frac{1}{|\mathcal{O}|}\sum_{(i,j)\in\mathcal{O}} \mathbf{1}[s(v_{ij}) = s(o_{p(i)j})],$$

em que $\mathcal{O}$ reúne os votos (Sim, Não, Obstrução ou Abstenção) com orientação diretiva nas camadas própria, bloco ou bloco inferido. Abstenção conta como desvio, e toda taxa vem com sua **cobertura** ($|\mathcal{O}|$ dividido pelos votos válidos). A **unidade partidária** compara o deputado à maioria dos demais colegas presentes:

$$U = \frac{1}{|\mathcal{U}|}\sum_{(i,j)\in\mathcal{U}} \mathbf{1}[s(v_{ij}) = m_{-i,j}],\qquad m_{-i,j}=\mathbf{1}\Big[\textstyle\sum_{k\in p(i),k\neq i} s(v_{kj}) > \tfrac{1}{2}n_{-i,j}\Big],$$

definida quando há pelo menos cinco colegas votando e não há empate; a abstenção do deputado conta como desvio. U cobre 94,6% dos votos; D, 66,7%.

O índice de Rice, $R_{pj}=|S_{pj}-N_{pj}|/(S_{pj}+N_{pj})$, é calculado em células com pelo menos três votantes. Para corrigir a inflação em bancadas pequenas, usamos o valor esperado numa subamostra sem reposição de $m$ membros (Desposato, 2005), calculado exatamente pela distribuição hipergeométrica, com $m = 3$ (todos os partidos) e $m = 10$. A linha de base é o Rice de votantes independentes. As médias se restringem às 894 votações **disputadas** (minoria do Plenário ≥ 10%). Os intervalos das taxas por partido vêm de bootstrap em duas vias (votações e deputados).

### 4.2 Pontos ideais

Usamos o estimador de pontos ideais do projeto (regressão logística bilinear penalizada; Clinton, Jackman e Rivers, 2004), sem modificá-lo. Para o voto Sim ($y_{ij}=1$) ou Não/Obstrução ($y_{ij}=0$) do deputado $i$, no período $r$ de filiação a um partido $p$:

$$\Pr(y_{ij}=1)=\sigma\big(a_j + g_{pj} + \mathbf{b}_j^\top \mathbf{x}_{r}\big),\qquad \mathbf{x}_r=\mathbf{u}_{i}+\boldsymbol{\delta}_r,$$

com penalidades gaussianas (as do estimador do projeto; $\lambda_d = 4$ para os desvios por período) e excluídas as votações com minoria abaixo de 2,5%. O modelo **global** omite $g$. O **intrapartidário** inclui o efeito fixo partido×votação $g_{pj}$, que absorve a posição do partido em cada votação, e centra os pontos dentro de cada partido. A amostra tem 417.832 votos, 1.039 votações, 828 períodos deputado×partido e 20.759 células partido×votação, com mediana de 11,0 votantes por célula e 27% delas com menos de cinco.

### 4.3 Ruído ou estrutura

Os modelos abaixo são comparados na previsão de votos retirados: validação cruzada em cinco dobras sobre células deputado×votação, estratificada por votação, isto é, um exercício de **imputação** de votos.

- **M0**: a regra "segue a orientação" (sem orientação, a maioria de treino do partido ou da votação), com probabilidade calibrada pelo acerto no treino; **M0c** calibra por partido e fonte.
- **M1**: só $a_j+g_{pj}$, a posição coletiva do partido em cada votação, estimada com os votos dos colegas na mesma votação.
- **M2**: M1 mais uma lealdade individual sem direção, $\sigma(z^{M1}+\rho_i d_{pj})$, com $d_{pj}=\pm1$ conforme a maioria de treino da célula.
- **M2b**: lealdade por período com escala por votação, $\sigma(z^{M1}+s_j\rho_r d_{pj})$, com penalidades $\lambda_\rho = 1$ e $\lambda_s = 0{,}04$. Tem a mesma estrutura de parâmetros de M3, mas a direção do desvio é fixada como "contra a maioria do próprio partido".
- **M3** e **M4**: o modelo intrapartidário com uma e duas dimensões. **M3L** acrescenta a M3 o termo $\rho_i d_{pj}$.
- **M5**: o modelo global de duas dimensões, sem partido.

A comparação central de E3 é M2b→M3. A métrica principal é a log-loss nas **células com divisão interna**: partido×votação com pelo menos cinco colegas no treino e pelo menos um voto contra a maioria do partido no treino. São definidas só com o treino e cobrem 64% dos votos. Reportamos também Brier, acurácia e AUC-PR para os votos contra a maioria. Os intervalos das diferenças vêm de bootstrap de deputados sobre as perdas de teste.

### 4.4 Correlatos, troca de partido e divergência com o Governo

**Quem desvia.** Um modelo de probabilidade linear (MPL) ao nível do voto, $\text{desvio}_{ij}=\boldsymbol\beta^\top\mathbf z_i(t)+\gamma_{p(i,t)j}+\varepsilon_{ij}$, com efeito fixo partido×votação, compara deputados do mesmo partido na mesma votação. As covariáveis são:

- suplência em exercício, por motivo do afastamento do titular (pareado por UF e data);
- sexo e idade;
- log das cadeiras da unidade da federação (UF);
- troca individual de partido, antes e depois da troca;
- a distância à mediana do partido no eixo governo–oposição, estimada com as votações do **outro biênio** e expressa em desvios-padrão da dimensão.

Os erros-padrão (EP) são agrupados por deputado e por votação (Cameron, Gelbach e Miller, 2011).

**Troca de partido.** Estudo de evento com efeitos fixos de deputado e de partido×votação e janelas em meses relativos à primeira troca individual (≤ −13, −12 a −7 [referência], −6 a −4, −3 a −1, 0 a 3, ≥ 4). Como as trocas ocorrem em datas diferentes, estimamos também a versão só com a coorte da janela de 2026, com os deputados que nunca trocaram como controles (Sun e Abraham, 2021; Callaway e Sant'Anna, 2021). A pré-tendência é testada em conjunto. Para separar seleção de ajuste, comparamos a posição do deputado antes da troca com as medianas de origem e destino.

**Partido × Governo.** Selecionamos os votos em que a orientação diretiva do partido e a do Governo são opostas, entre os partidos com ministério em ao menos parte do governo: PT, PCdoB, PSB, PDT, PSOL, REDE, MDB, PSD, União, PP e REPUBLICANOS (Apêndice C). O **excesso de lealdade** é o observado menos o previsto pelo modelo global sem partido, de duas formas:

- (i) previsões de validação cruzada de M5. Como seus parâmetros já usam votos disciplinados da mesma votação, dão um **limite inferior**;
- (ii) M5 reestimado sem os votos desses partidos nas células divergentes. Tende a **superestimar** o excesso, porque as cargas dessas votações passam a vir só dos outros partidos.

## 5. Resultados

### 5.1 O que a orientação registrada mede

A disciplina é de 94,9% sob orientação própria, 87,2% sob bloco e 88,0% sob bloco inferido. Para União, PP, PSD, MDB, REPUBLICANOS, PODE e PSDB, menos de 2% dos votos estão sob orientação do próprio partido (Figura 2, coluna à direita): o que se chama de disciplina partidária, nesses partidos, é disciplina ao líder do bloco.

O registro de 2025 é o caso extremo. Em D, a disciplina sobe para 92,9% em 2025, contra 90,1% em 2023, mas a cobertura de D cai a 32%, contra 89% (Figura 1). Nas votações do megabloco, o registro sempre traz as linhas de Governo, Maioria, Minoria e Oposição (227 linhas de Oposição em 227 votações), mas nenhuma linha própria do PL ou da federação do PT. As transcrições, porém, mostram esses partidos orientando: as orientações faladas cobrem 138 das 227 votações do megabloco. Orientação vazia, portanto, nem sempre quer dizer que a liderança não orientou; pode ser um limite do registro.

As falas não servem para medir o *nível* da disciplina nesse período. Nas votações e partidos do megabloco que elas cobrem, a disciplina pela fala é de 81,8% (80,3% só com o verbo "orienta"), mas a unidade com os colegas nos mesmos votos é de 89,2%. No PT, a diferença é de 91,2% contra 98,4%; no PL, de 80,5% contra 91,1%. Fora do megabloco, nos mesmos votos, a disciplina pela fala é de 87,4%, contra 91,4% pelo registro: a medida pela fala tem um viés de −4,1 pontos fora do megabloco e um erro ainda maior dentro dele.

A evidência sobre o nível vem, então, de U. Nos mesmos votos, U é de 89,2% no megabloco e de 91,6% fora dele, e no conjunto de 2025 U é a menor da legislatura (88,7%, contra 89,8% em 2023 e 90,0% em 2026). A queda se concentra nos partidos de centro, comparando 2025 com os demais anos:

- PSD: −4,9 pontos;
- MDB: −4,7;
- PP: −3,1;
- União: −2,7.

PL (90,3% em 2025, contra 88,7%), PT e REPUBLICANOS ficam estáveis. Fixando a composição partidária, D em 2025 ainda fica em 92,0%, contra 90,5% em 2023. Cerca de metade da alta registrada vem da composição dos votos com orientação; o restante vem de quais votações tiveram orientação registrada. Para comparar partidos, usamos U como medida comparável e D sempre com sua cobertura.

![Figura 1](figuras/fig1_serie_semestral.png)

*Figura 1 – Disciplina (D, todas as camadas e só orientação própria) e unidade (U) por semestre; D é omitido onde a cobertura é inferior a 20%. Abaixo, a cobertura de D.*

### 5.2 Quanta disciplina

A disciplina à liderança no Plenário é de 90,9% (IC 95% por bootstrap de votações: 90,4–91,3), e a unidade, de 89,5% (Tabela 2, Figura 2).

- **Extremo mais coeso:** PT, PSOL, PCdoB e NOVO votam quase sempre com a liderança, e os três primeiros, também com os colegas (NOVO não tem U) (U de 98,3% no PT e 97,9% no PSOL).
- **Extremo menos coeso:** União (U 80,5%) e PSDB (84,1%).
- **Meio:** MDB (84,9%), PP (86,0%), PSD (87,3%) e PODE (87,9%).

Tomando a federação como grupo, a unidade é de 98,1% na PT-PCdoB-PV, 97,5% na PSOL-REDE e 82,1% na PSDB-CIDADANIA. Em U, o ano de maior e o de menor unidade diferem em 1,6 ponto percentual (entre semestres, até 5,0). E1 se sustenta.

**Tabela 2 – Disciplina à liderança (D), unidade (U) e coesão (Rice) por partido, Plenário**

| Partido | D (IC 95%) | D própria (votações) | U (IC 95%) | U 2023 | U 2024 | U 2025 | U 2026 | Cob. D | Rice disp. | Rice m=3 | Rice m=10 | % racha |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PSOL | 98,3 [97,1; 99,3] | 98,3 (957) | 97,9 [96,7; 98,9] | 97,3 | 97,1 | 98,5 | 99,3 | 86 | 0,98 | 0,98 | 0,98 | 1 |
| PT | 98,7 [98,3; 99,0] | 98,7 (877) | 98,3 [98,0; 98,7] | 97,9 | 98,6 | 98,2 | 99,2 | 79 | 0,97 | 0,97 | 0,97 | 1 |
| PCdoB | 97,6 [96,4; 98,6] | 97,6 (877) | 98,7 [97,8; 99,3] | 98,7 | 98,9 | 98,9 | 97,7 | 77 | 0,98 | 0,98 | – | 1 |
| PV | 96,7 [94,5; 98,3] | 96,7 (877) | 96,0 [91,9; 99,0] | 95,8 | 95,2 | – | 97,1 | 80 | 0,93 | 0,93 | – | 5 |
| PSB | 91,0 [88,6; 93,2] | 95,1 (365) | 92,9 [90,2; 94,9] | 93,4 | 95,5 | 90,7 | 94,0 | 56 | 0,85 | 0,88 | 0,85 | 9 |
| PDT | 90,2 [87,5; 92,4] | 96,4 (163) | 94,6 [92,6; 96,2] | 95,2 | 94,2 | 93,8 | 97,0 | 61 | 0,88 | 0,90 | 0,89 | 8 |
| MDB | 89,0 [84,3; 93,0] | – (1) | 84,9 [80,1; 88,9] | 87,4 | 87,2 | 82,0 | 83,8 | 60 | 0,64 | 0,73 | 0,65 | 24 |
| PSD | 89,5 [85,9; 92,4] | – (1) | 87,3 [83,5; 90,5] | 91,0 | 87,8 | 84,3 | 88,2 | 60 | 0,70 | 0,77 | 0,71 | 18 |
| AVANTE | 88,6 [83,8; 93,9] | 92,7 (11) | 87,0 [80,2; 93,8] | 84,6 | 91,0 | 86,6 | 85,9 | 55 | 0,74 | 0,77 | – | 19 |
| PODE | 88,3 [81,4; 93,1] | – (1) | 87,9 [80,7; 92,9] | 87,0 | 88,5 | 88,1 | 87,8 | 60 | 0,72 | 0,76 | 0,73 | 14 |
| UNIÃO | 82,4 [78,3; 86,3] | 90,1 (13) | 80,5 [76,7; 84,4] | 82,5 | 80,2 | 78,9 | 82,2 | 64 | 0,54 | 0,68 | 0,56 | 48 |
| PP | 88,3 [84,2; 92,4] | 94,9 (12) | 86,0 [81,5; 90,0] | 88,2 | 87,1 | 84,1 | 84,5 | 64 | 0,66 | 0,74 | 0,67 | 22 |
| REPUBLICANOS | 92,8 [89,5; 95,6] | – (1) | 92,4 [89,1; 95,1] | 91,5 | 93,8 | 92,5 | 90,5 | 59 | 0,82 | 0,84 | 0,82 | 5 |
| PSDB | 82,3 [75,8; 88,6] | 89,4 (11) | 84,1 [77,1; 91,0] | 83,3 | 86,7 | 81,5 | 88,4 | 64 | 0,65 | 0,72 | 0,65 | 26 |
| PL | 90,5 [88,7; 92,0] | 90,3 (758) | 89,3 [87,3; 91,0] | 87,1 | 89,9 | 90,3 | 89,9 | 71 | 0,77 | 0,82 | 0,78 | 14 |
| NOVO | 99,4 [98,8; 99,8] | 99,4 (1085) | – | – | – | – | – | 96 | 0,98 | 0,99 | – | 1 |

*D: voto na direção da orientação diretiva da bancada (Não = Obstrução; Abstenção = desvio), camadas própria, bloco e bloco inferido, sem o bloco heterogêneo de 2025. Cob. D: % dos votos do partido com orientação diretiva aplicável. U: voto na direção da maioria dos demais colegas (≥ 5). Rice em votações com minoria ≥ 10%; m = 3 e m = 10: padronização de Desposato; '% racha': votações disputadas com Rice < 0,5. IC por bootstrap em duas vias (votações e deputados, 500 réplicas). D própria: só votos sob orientação do próprio partido ou federação, com o nº de votações entre parênteses; omitida com menos de 10 votações.*

![Figura 2](figuras/fig2_disciplina_unidade.png)

*Figura 2 – Disciplina à liderança (D) e unidade (U) por partido, com IC 95% por bootstrap em duas vias (votações e deputados). À direita, a parcela dos votos do partido sob orientação própria. NOVO não tem U porque a bancada nunca reúne cinco colegas votando.*

**Ausências.** O voto nominal registra só quem votou. No pior caso de ausência não ignorável, toda ausência de membro em exercício do partido, nas votações com orientação diretiva, conta como desvio. Nesse caso, D cai de 90,9% para 73,1%, já que 19,6% dos membros em exercício não votaram. O ordenamento dos partidos se mantém (correlação de postos de 0,91). O caso da PEC é mais nítido, porque a aprovação exige 308 votos Sim e a ausência equivale a voto contra. Nas 28 votações de mérito de PEC com orientação Sim, a disciplina vai de 94,9% para 83,8%.

### 5.3 Onde a disciplina falha

**Obstrução.** Sob orientação de Obstrução, a adesão literal é de 75,0%. A maioria dos que não obstruíram votou Não (13,6% dos votos), na mesma direção; só 10,4% votaram Sim.

**Liberação.** Quando o partido libera a bancada, a unidade cai de 91,6% para 79,4%, o que ocorre em 16 dos 16 partidos.

**Tipo de votação.** A disciplina é maior no mérito de PECs (94,3%) e de projetos (92,5%) do que em destaques (89,5%), emendas (88,9%) e requerimentos procedimentais (90,4%). O ajuste por partido×ano quase não muda os números (Tabela 3).

**Tema.** A unidade vai de 84,4% (homenagens) e 86,1% (política, partidos e eleições) a 93,9% (agricultura) e 94,6% (estrutura fundiária) (Tabela A1, no Apêndice D).

**Tabela 3 – Disciplina (D) e unidade (U) por tipo de votação e de proposição, Plenário**

| Recorte | Categoria | Votações | D | U | D ajust. | U ajust. |
|---|---|---|---|---|---|---|
| Tipo de votação | Destaque (texto) | 193 | 89,5 | 88,0 | 89,4 | 88,1 |
| Tipo de votação | Emenda / destaque de emenda | 144 | 88,9 | 89,0 | 89,0 | 88,9 |
| Tipo de votação | Mérito (texto principal) | 227 | 92,5 | 90,4 | 92,4 | 90,4 |
| Tipo de votação | PEC (mérito) | 29 | 94,3 | 94,1 | 94,3 | 94,2 |
| Tipo de votação | Requerimento procedimental | 318 | 90,4 | 89,0 | 90,3 | 89,1 |
| Tipo de votação | Urgência | 204 | 91,9 | 90,6 | 92,0 | 90,4 |
| Tipo de proposição | MPV | 75 | 91,0 | 90,5 | 91,1 | 90,5 |
| Tipo de proposição | PDL | 42 | 93,9 | 93,4 | 93,6 | 93,9 |
| Tipo de proposição | PEC | 103 | 90,2 | 89,5 | 90,5 | 89,5 |
| Tipo de proposição | PL | 703 | 90,9 | 89,2 | 90,8 | 89,2 |
| Tipo de proposição | PLP | 170 | 90,8 | 90,1 | 90,9 | 90,0 |

*'Ajust.': média prevista de cada categoria com efeitos fixos de partido×ano (composição partidária da amostra toda). Votações: só as que têm orientação diretiva aplicável (por isso as contagens diferem das da Tabela 1).*

**Coesão.** Nas votações disputadas, o Rice médio é de 0,78, contra 0,47 esperados de dez votantes independentes (Figura 3). A correção de Desposato com m = 3, que inclui todos os 16 partidos da Tabela 2, preserva o ordenamento do Rice bruto (correlação de postos de 0,99). Entre m = 3 e m = 10 a correlação é de 0,99, e entre os limiares de disputa de 10% e 20%, de 1,00. E2 se sustenta. O União tem Rice de 0,54 e racha (menos de 75% num lado) em 48% das votações disputadas; vêm em seguida PSDB (26%), MDB (24%) e PP (22%). PT e PSOL racham em cerca de 1%.

![Figura 3](figuras/fig3_rice.png)

*Figura 3 – Rice médio nas votações disputadas, bruto e padronizado (m = 10), e a linha de base de voto aleatório.*

### 5.4 Ruído ou estrutura

A Tabela 4 e a Figura 4 resumem a validação cruzada nas células com divisão interna, em que 15,2% dos votos contrariam a maioria do partido. A posição do partido em cada votação (M1) reduz a log-loss da regra calibrada (M0c) em 0,146 (IC 0,128–0,164). Esse ganho reflete o uso dos votos dos colegas na mesma votação, e não só a orientação registrada.

- **Propensão a desviar (M1→M2b):** 0,025 (IC 0,022–0,029). Alguns deputados desviam sistematicamente mais que outros.
- **Direção da dissidência além da propensão, com a mesma estrutura de parâmetros (M2b→M3):** 0,006 (IC 0,003–0,009 por bootstrap de deputados; 0,004–0,007 por bootstrap de votações).
- **Lealdade somada a M3 (M2→M3L):** 0,015 (IC 0,012–0,018).
- **Segunda dimensão (M3→M4):** 0,008 (IC 0,006–0,010).

E3 se sustenta: a indisciplina não é ruído puro. Mas a parte atribuível à direção individual é pequena perto da posição do partido e da propensão a desviar.

O resultado resiste a três checagens:

- **Células grandes.** Os ganhos aparecem também nas células com 50 ou mais votantes no treino, em que $g_{pj}$ não está saturado: log-loss de 0,2509 em M1 e 0,2171 em M3.
- **Minoria interna.** Nas células com minoria interna de treino de pelo menos 10% (37% dos votos), a ordem é a mesma: M2b 0,333, M3 0,322 e M4 0,312.
- **Penalização.** Com $\lambda_d$ de 1 ou 16, a log-loss de M3 na dobra 0 vai a 0,2493 e 0,2491, contra 0,2491.

O modelo global sem partido (M5) prevê pior que o intrapartidário de duas dimensões, em 0,021. Isso não prova um efeito do partido, porque os dois modelos não são aninhados e $g_{pj}$ também absorve preferências partidárias específicas de cada votação.

**Tabela 4 – Desempenho fora da amostra nas células com divisão interna (validação cruzada em 5 dobras de células deputado×votação)**

| Modelo | Log-loss | Brier | Acurácia | AUC-PR (desvio) |
|---|---|---|---|---|
| M0 orientação do líder | 0,4475 | 0,1359 | 84,08 | 0,167 |
| M0c orientação, calibrada por partido e fonte | 0,4298 | 0,1312 | 84,05 | 0,228 |
| M1 só partido×votação | 0,2838 | 0,0831 | 88,94 | 0,677 |
| M2 = M1 + lealdade individual | 0,2641 | 0,0780 | 89,46 | 0,695 |
| M2b = M1 + lealdade por período × escala por votação | 0,2583 | 0,0765 | 89,68 | 0,703 |
| M3 intra 1D | 0,2525 | 0,0730 | 90,31 | 0,723 |
| M3L = M3 + lealdade individual | 0,2491 | 0,0727 | 90,24 | 0,725 |
| M4 intra 2D | 0,2447 | 0,0707 | 90,56 | 0,738 |
| M5 global 2D (sem partido) | 0,2655 | 0,0792 | 89,21 | 0,695 |

*Células com divisão interna: partido×votação com ≥ 5 colegas no treino e ao menos um voto contra a maioria do partido no treino. AUC-PR: precisão média ao ranquear os votos contra a maioria de treino da célula.*

![Figura 4](figuras/fig4_validacao_cruzada.png)

*Figura 4 – Redução da log-loss fora da amostra (por voto) ao acrescentar cada componente, nas células com divisão interna. IC 95% por bootstrap de deputados.*

### 5.5 O que é a dimensão intrapartidária

A dimensão intrapartidária do modelo de 1D é o **eixo governo–oposição recortado dentro de cada partido**. O sinal foi fixado de modo que valores positivos indiquem quem vota mais com o Governo; a interpretação vem das cargas. Nas votações em que o Governo orientou (77% do total), a correlação entre a carga e a orientação do Governo é de 0,90. Entre as 100 votações de maior carga, o sinal coincide com o da orientação do Governo em 100%. E4 se sustenta, no sentido de compatibilidade. Sob um governo de esquerda, porém, o eixo governo–oposição não se separa de um eixo esquerda–direita, e o rótulo deve ser lido com essa ressalva.

A dimensão é quase a posição relativa do deputado no eixo global: as duas correlacionam 0,94. A estrutura intrapartidária é, portanto, o eixo que separa os partidos, visto de dentro. O que vai além dele é pequeno. A segunda dimensão acrescenta 0,008 de log-loss, e suas cargas quase não se associam à orientação do Governo (0,10) nem à filiação a frentes parlamentares (no máximo 0,13 em módulo).

As votações de maior carga (Tabela 5) ilustram isso:

- **Polo positivo:** votações em que o Governo orientou Sim, como a medida provisória da Agência Nacional de Proteção de Dados, a autorização para o Banco do Nordeste criar subsidiárias, a depreciação acelerada e textos mantidos em destaques.
- **Polo negativo:** requerimentos procedimentais com orientação Não do Governo e o projeto sobre "invasores de propriedades".

Requerimentos procedimentais são 38% das 100 votações de maior carga, contra 31% do total.

**Tabela 5 – Votações com maior carga na dimensão intrapartidária (modelo intra 1D)**

| Sinal | Data | Proposição | Tipo | Ementa | Gov. | Resultado | Carga |
|---|---|---|---|---|---|---|---|
| + (governistas relativos votam Sim) | 2026-02-09 | MPV 1317/2025 | Mérito (texto principal) | Altera a Lei nº 13.709, de 14 de agosto de 2018, para tratar da Agência Nacional de Proteção de Dados, a Lei nº 10.87... | Sim | aprovada | 6,57 |
| + (governistas relativos votam Sim) | 2025-11-05 | PL 2809/2024 | Destaque (texto) | Altera a Lei nº 7.797, de 10 de julho de 1989, a Lei nº 9.795, de 27 de abril de 1999, e a Lei nº 12.187, de 29 de de... | Sim | texto mantido | 6,53 |
| + (governistas relativos votam Sim) | 2025-04-29 | PL 3469/2024 | Destaque (texto) | Altera a Lei nº 7.565, de 19 de dezembro de 1986 – Código Brasileiro de Aeronáutica, e a Lei nº 7.957, de 20 de dezem... | Sim | texto mantido | 6,49 |
| + (governistas relativos votam Sim) | 2025-05-26 | PL 1708/2025 | Mérito (texto principal) | Autoriza o Banco do Nordeste do Brasil S.A. a constituir subsidiárias integrais ou controladas. | Sim | aprovada | 5,88 |
| + (governistas relativos votam Sim) | 2024-12-17 | PL 3802/2024 | Urgência | Altera a Lei nº 14.467, de 16 de novembro de 2022, que dispõe sobre o tratamento tributário aplicável às perdas incor... | Sim | rejeitada | 5,84 |
| + (governistas relativos votam Sim) | 2025-08-19 | PL 3181/2025 | Destaque (texto) | Dispõe sobre a criação de funções comissionadas no Quadro de Pessoal do Superior Tribunal de Justiça. | Sim | texto mantido | 5,65 |
| + (governistas relativos votam Sim) | 2024-03-19 | PL 2/2024 | Destaque (texto) | Autoriza a concessão de quotas diferenciadas de depreciação acelerada para máquinas, equipamentos, aparelhos e instru... | Sim | texto mantido | 5,51 |
| + (governistas relativos votam Sim) | 2025-06-25 | PL 3118/2024 | Destaque (texto) | Altera a Lei nº 12.858, de 9 de setembro de 2013, para incluir as políticas de assistência aos estudantes da educação... | Sim | texto mantido | 5,47 |
| − (governistas relativos votam Não) | 2025-05-26 | PL 1708/2025 | Requerimento procedimental | Autoriza o Banco do Nordeste do Brasil S.A. a constituir subsidiárias integrais ou controladas. | Não | rejeitada | −5,90 |
| − (governistas relativos votam Não) | 2025-04-29 | PL 3469/2024 | Requerimento procedimental | Altera a Lei nº 7.565, de 19 de dezembro de 1986 – Código Brasileiro de Aeronáutica, e a Lei nº 7.957, de 20 de dezem... | Não | rejeitada | −5,72 |
| − (governistas relativos votam Não) | 2025-04-28 | PL 363/2025 | Requerimento procedimental | Altera a Lei nº 14.399, de 8 de julho de 2022, que institui a Política Nacional Aldir Blanc de Fomento à Cultura. | Não | rejeitada | −5,67 |
| − (governistas relativos votam Não) | 2025-07-09 | PL 769/2024 | Requerimento procedimental | Dispõe sobre a criação de funções comissionadas no Quadro de Pessoal do Supremo Tribunal Federal. | Não | rejeitada | −5,62 |
| − (governistas relativos votam Não) | 2026-04-22 | PL 3025/2023 | Requerimento procedimental | Dispõe sobre normas de controle de origem, compra, venda e transporte de ouro no território nacional e altera a Lei n... | Não | rejeitada | −5,36 |
| − (governistas relativos votam Não) | 2024-05-21 | PL 709/2023 | Mérito (texto principal) | Dispõe sobre impedimentos aplicados aos ocupantes e invasores de propriedades em todo território nacional. NOVA EMENT... | Não | aprovada | −5,32 |
| − (governistas relativos votam Não) | 2024-09-11 | PL 1847/2024 | Emenda / destaque de emenda | Estabelece regime de transição para a contribuição substitutiva prevista nos arts. 7º e 8º da Lei nº 12.546, de 14 de... | Não | rejeitada | −5,27 |
| − (governistas relativos votam Não) | 2026-04-22 | PL 3025/2023 | Requerimento procedimental | Dispõe sobre normas de controle de origem, compra, venda e transporte de ouro no território nacional e altera a Lei n... | Não | rejeitada | −5,18 |

*Carga positiva: os deputados mais governistas que o próprio partido tendem a votar Sim.*

**Validação externa.** Com o modelo ajustado só com votações anteriores a 2026, a distância ao centro do partido prevê *quem* troca de partido na janela, com AUC de 0,59 (IC 0,54–0,65; 129 trocas entre 525 deputados). O sinal da posição prevê a **direção** da troca em 61,8% das 110 trocas classificáveis (teste binomial, p = 0,017), contra 64,5% da posição relativa no modelo global. A direção é definida pelas medianas pré-2026 do próprio modelo global. É evidência modesta, que não vai além do que o eixo global já contém.

### 5.6 Quem desvia

A Tabela 6 traz os correlatos do desvio dentro do mesmo partido e da mesma votação.

- **Distância espacial ao partido:** é o correlato dominante. Cada desvio-padrão de distância, medida no outro biênio, está associado a 22,1 pontos percentuais a mais de desvio da orientação (IC 19,2–25,0) e a 24,5 pontos a mais de desvio da maioria dos colegas. Chamamos essa medida de distância espacial, e não de preferência, porque ela vem do próprio comportamento de voto, ainda que de outro período.
- **Troca de partido:** os deputados que trocariam de partido desviam mais antes da troca (2,1 ponto em U; IC 0,6–3,7), mas não depois (−0,3; IC −3,1 a 2,5).
- **Sem associação distinguível de zero ao nível de 5%:** suplência (inclusive a de titulares ministros), sexo, idade e tamanho da bancada estadual.
- **UFs:** em conjunto, importam (χ² = 73,2, 26 g.l.). Isso é compatível com principais estaduais concorrentes (Carey, 2009), mas o mecanismo não é identificado.

**Tabela 6 – Correlatos do desvio individual: MPL com efeitos fixos partido×votação**

| Variável | Desvio de D (p.p.) | Desvio de U (p.p.) |
|---|---|---|
| Suplente (titular ministro) | −0,74 [−2,21; 0,72] | −0,32 [−3,13; 2,49] |
| Suplente (titular secretário) | 1,75 [−0,04; 3,54] | 1,82 [−0,35; 4,00] |
| Suplente (outro motivo) | −0,42 [−2,72; 1,88] | −0,12 [−2,23; 1,99] |
| Mulher | −0,36 [−1,89; 1,17] | −0,47 [−1,97; 1,04] |
| Idade (décadas) | −0,23 [−0,65; 0,19] | −0,02 [−0,42; 0,39] |
| log cadeiras da UF | 0,23 [−0,58; 1,04] | 0,20 [−0,54; 0,93] |
| Trocará de partido (votos antes da troca) | 1,69 [0,04; 3,34] | 2,14 [0,62; 3,65] |
| Trocou de partido (votos depois da troca) | 0,54 [−1,99; 3,08] | −0,31 [−3,10; 2,49] |
| Distância espacial à mediana do partido (outro biênio, em DP) | 22,10 [19,22; 24,99] | 24,52 [22,05; 26,99] |
| UF (Wald, 26 g.l.) | χ² = 73,2; p = 0,000 | χ² = 76,5; p = 0,000 |
| N votos (deputados) | 275.452 (528) | 395.806 (520) |

*Coeficientes em pontos percentuais (IC 95%, EP agrupados por deputado e por votação). Distância medida na dim1 global estimada com as votações do outro biênio.*

A variância das taxas brutas de desvio entre deputados é quase toda sinal: o ruído binomial responde por 1% dela (1% na versão ajustada pela célula partido×votação). Desse sinal, 80% está **dentro** dos partidos. Parte dele reflete agendas diferentes; suplentes, por exemplo, votam em períodos distintos.

**Dispersão e dissidentes.** No eixo governo–oposição (Tabela 7, Figura 5), PDT (0,17), PSB (0,20), PSOL (0,21) e PT (0,23) são compactos. MDB (0,57), União (0,54), PP (0,54), PODE (0,50) e PL (0,48) são dispersos. Entre os 595 períodos com pelo menos 100 votos, 32 estão a pelo menos dois desvios-padrão da mediana do partido, com IC que a exclui. Os mais extremos estão na Tabela A2 (Apêndice D). No PL, há deputados mais governistas que o partido: João Carlos Bacelar, Junior Lourenço e Tiririca. No sentido oposto estão Sargento Fahur (PSD), Zucco (REPUBLICANOS), Mauricio Marcon (PODE), Evair Vieira de Melo (PP) e Pezenti (MDB).

**Tabela 7 – Dispersão interna dos partidos no eixo governo × oposição (dim1 global, Plenário)**

| Partido | Períodos | DP dim1 (EP) | Viés bootstrap | IIQ dim1 |
|---|---|---|---|---|
| PSOL | 14 | 0,21 (0,04) | 0,034 | 0,19 |
| PT | 70 | 0,23 (0,03) | 0,047 | 0,36 |
| PCdoB | 9 | 0,24 (0,06) | 0,030 | 0,29 |
| PV | 6 | 0,35 (0,05) | 0,017 | 0,46 |
| PSB | 17 | 0,20 (0,02) | 0,010 | 0,26 |
| PDT | 20 | 0,17 (0,02) | 0,012 | 0,22 |
| MDB | 48 | 0,57 (0,02) | 0,005 | 0,63 |
| PSD | 56 | 0,44 (0,02) | 0,003 | 0,49 |
| AVANTE | 8 | 0,56 (0,03) | 0,006 | 0,44 |
| PODE | 19 | 0,50 (0,02) | 0,007 | 0,30 |
| UNIÃO | 69 | 0,54 (0,01) | 0,004 | 0,79 |
| PP | 58 | 0,54 (0,02) | 0,004 | 0,65 |
| REPUBLICANOS | 53 | 0,42 (0,02) | 0,008 | 0,31 |
| PSDB | 15 | 0,47 (0,02) | 0,003 | 0,32 |
| PL | 108 | 0,48 (0,01) | 0,006 | 0,52 |
| NOVO | 5 | 0,08 (0,04) | 0,023 | 0,11 |

*Períodos deputado×partido com ≥ 100 votos; partidos com ≥ 5 períodos. EP e viés por bootstrap de votações com reajuste e alinhamento de Procrustes; o viés (média bootstrap menos estimativa) mostra quanto a reamostragem infla a dispersão, sobretudo em bancadas pequenas.*

![Figura 5](figuras/fig5_pontos_ideais.png)

*Figura 5 – Pontos ideais no eixo governo–oposição por partido (períodos deputado×partido com ≥ 100 votos), com a mediana de cada partido, a mediana geral e os quantis de 40% e 60%.*

**Pivôs.** A identidade do deputado mediano é instável: nas réplicas bootstrap, nenhum deputado está entre os cinco mais próximos da mediana em mais de 20% das vezes. O que é estável é o partido. Calculados entre os deputados em exercício em cada semestre (Tabela A3, Apêndice D), o mediano e os pivôs de 3/5 estão sempre em partidos do centro: REPUBLICANOS, PSD, PP, MDB, PODE, União, PSDB ou SOLIDARIEDADE.

### 5.7 Troca de partido

A Figura 6 mostra o estudo de evento para 173 deputados com troca individual.

- **Antes da troca:** na janela de referência, os futuros trocadores contrariam a maioria dos colegas em 20,6% dos votos. Nenhum coeficiente anterior se distingue de zero individualmente (−1,7, −0,9 e 1,4 pontos), mas o teste conjunto é limítrofe (p = 0,10). A estimativa de −3 a −1 meses fica 3,1 pontos acima da de 13 meses ou mais antes: há uma pré-tendência fraca, compatível com saída anunciada.
- **Depois da troca:** o desvio em relação à maioria dos novos colegas cai 11,1 pontos nos primeiros três meses (IC 6,5–15,6) na versão com todas as trocas.
- **Só a coorte da janela de 2026** (129 deputados, com controles que nunca trocaram): a queda é de 6,5 pontos (IC 2,4–10,6), com teste conjunto de pré-tendência também limítrofe (p = 0,11). É a estimativa preferível, porque evita usar trocadores antigos como controles; a da versão completa é maior. Nessa versão, o coeficiente de −6 a −4 meses é negativo (−2,1 pontos), o que não sustenta a leitura de saída anunciada. Em D, nessa coorte, a queda (3,1 pontos) não se distingue de zero.
- **Fusões:** não servem de placebo. Em U, as bancadas pré-fusão nunca reuniam cinco colegas votando, e os coeficientes não são identificados.

**Seleção ou ajuste?** Estes números vêm dos 145 deputados com pontos nos dois partidos:

- **Seleção:** 67,6% já estavam, antes da troca, do lado do partido de origem voltado para o destino.
- **Ajuste:** 69,7% se moveram em direção ao destino depois da troca (deslocamento mediano de 0,13).
- **Contra a seleção pura:** a mediana do destino estava mais perto da posição anterior do deputado do que a da origem em só 44,8% dos casos.

Os dados são compatíveis com os dois mecanismos. O desenho não separa ajuste sincero de comportamento estratégico.

![Figura 6](figuras/fig6_troca_partido.png)

*Figura 6 – Desvio da maioria dos colegas (U) em torno da troca individual de partido, relativo à janela de −12 a −7 meses. Efeitos fixos de deputado e de partido×votação; IC 95% com EP agrupados por deputado e votação.*

### 5.8 Partido ou Governo?

Nos partidos com ministério, há 15.404 votos em que a orientação do partido e a do Governo são opostas. Neles, 90,8% seguem o partido e 9,0% o Governo (Figura 7). Com a base datada (PP e REPUBLICANOS só a partir de 13/09/2023; União e PP fora a partir de 02/09/2025), a adesão é de 89,7%. Nos partidos sem ministério que não são de oposição (PSDB, PODE, AVANTE e outros), é de 81,6%. A Figura 7 traz o IC 95% e o número de votações de cada partido.

A fonte da orientação importa, como Carey prevê. A adesão é de 95,6% quando a orientação é própria, 92,8% quando é de bloco e 81,6% quando é de bloco inferido. No PSB e no PDT a bancada parece dividida (52,4% e 53,1% de adesão), mas sob orientação própria a adesão é de 85,3% e 92,5%. O "racha", portanto, é em boa parte artefato da atribuição a blocos inferidos. O PT diverge do Governo em só 9 votações.

O excesso de lealdade fica entre os dois contrafactuais:

- **(i), limite inferior:** 4,2 pontos (IC 3,2–5,3);
- **(ii):** 17,1 pontos (IC 14,8–19,6);
- **sem os partidos de esquerda**, para os quais o contrafactual (ii) é pouco crível: de 2,6 a 11,2 pontos.

Os intervalos excluem zero nos dois contrafactuais, e E5 se sustenta. Dentro do mesmo partido e da mesma votação, quem é mais governista que o partido no outro biênio segue mais o Governo: 8,5 pontos por desvio-padrão (IC 5,3–11,7). Suplentes de titulares ministros não seguem mais o Governo (1,1 pontos; IC −4,3 a 6,6).

![Figura 7](figuras/fig7_partido_governo.png)

*Figura 7 – Partidos com ministério: parcela dos votos que segue o partido e o Governo quando as orientações são opostas, e parcela que seguiria o partido segundo as preferências estimadas fora da amostra (M5). À direita, número de votos.*

## 6. Robustez

A Tabela 8 refaz a disciplina sob sete variantes de medida. Sem as orientações inferidas de blocos, a disciplina geral vai de 90,9% para 91,3%, e a correlação de postos entre partidos é de 0,97. As maiores mudanças estão no PSB (91,0% para 95,1%) e no PDT (90,2% para 96,4%). O ordenamento só muda de forma relevante quando a medida se restringe à orientação própria (ρ = 0,85), que cobre poucos votos dos partidos do centro. As demais variantes mudam a disciplina geral em menos de meio ponto. Sem orientações inferidas, a adesão ao partido nas divergências com o Governo vai de 90,8% para 93,3%.

**Tabela 8 – Robustez da disciplina (D) a decisões de medida, Plenário**

| Variante | Geral | Cobertura | ρ (ranking) | PSOL | PT | PCdoB | PV | PSB | PDT | MDB | PSD | AVANTE | PODE | UNIÃO | PP | REPUBLICANOS | PSDB | PL | NOVO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Principal (direcional; própria + bloco + inferido) | 90,9 | 66,7 | 1,00 | 98,3 | 98,7 | 97,6 | 96,7 | 91,0 | 90,2 | 89,0 | 89,5 | 88,6 | 88,3 | 82,4 | 88,3 | 92,8 | 82,3 | 90,5 | 99,4 |
| Sem orientações inferidas de bloco | 91,3 | 58,8 | 0,97 | 98,3 | 98,7 | 97,6 | 96,7 | 95,1 | 96,4 | 89,4 | 89,5 | 83,7 | 87,8 | 82,4 | 88,3 | 93,0 | 80,7 | 90,5 | 99,4 |
| Só orientação própria (partido/federação) | 94,9 | 30,9 | 0,85 | 98,3 | 98,7 | 97,6 | 96,7 | 95,1 | 96,4 | 94,1 | 90,2 | 92,7 | 92,3 | 90,1 | 94,9 | 100,0 | 89,4 | 90,3 | 99,4 |
| Incluindo o bloco heterogêneo (2025) | 90,9 | 68,3 | 0,99 | 98,3 | 98,6 | 97,4 | 96,7 | 91,2 | 90,4 | 89,1 | 89,6 | 88,8 | 88,3 | 82,6 | 88,5 | 92,9 | 82,5 | 90,2 | 99,4 |
| Sem fev.–out./2025 | 90,6 | 62,0 | 0,99 | 98,1 | 98,8 | 97,8 | 96,9 | 90,9 | 89,6 | 89,0 | 90,0 | 89,4 | 88,2 | 82,2 | 88,1 | 92,8 | 82,7 | 90,2 | 99,4 |
| Estrita (Obstrução ≠ Não) | 90,6 | 66,7 | 0,98 | 98,2 | 98,6 | 97,3 | 96,7 | 91,0 | 90,2 | 89,0 | 89,5 | 88,6 | 88,3 | 82,4 | 88,3 | 92,8 | 82,3 | 88,9 | 98,9 |
| Sem abstenções | 91,1 | 66,6 | 1,00 | 99,0 | 98,7 | 97,7 | 96,8 | 91,2 | 90,4 | 89,3 | 89,7 | 88,8 | 88,6 | 82,6 | 88,4 | 92,9 | 82,5 | 90,7 | 99,4 |
| Plenário + comissões | 91,0 | 66,7 | 1,00 | 98,1 | 98,5 | 97,4 | 96,6 | 91,2 | 90,3 | 89,0 | 89,5 | 88,7 | 88,3 | 82,7 | 88,4 | 92,7 | 82,5 | 90,7 | 99,4 |

*ρ: correlação de Spearman entre o ranking dos partidos na variante e na medida principal.*

## 7. Limitações

**Votações nominais e registro.** Só 16,5% das votações do Plenário foram nominais, e a escolha delas é estratégica (Carrubba, Gabel e Hug, 2008). O registro de orientações tem lacunas. A reconstrução pelas falas mostra que houve orientação onde o registro está vazio, mas é uma medida ruidosa do nível de disciplina, com 6% de discordância com o registro onde os dois existem.

**Ausências.** O limite inferior de D com ausências mostra que o nível de disciplina depende muito do tratamento da ausência; o ordenamento dos partidos, não.

**Medidas comportamentais.** A orientação é o sinal público do líder; negociação, sanções e recompensas (cargos, emendas) não são observadas. A distância espacial vem de votos, ainda que de outro período, e U não distingue disciplina de coesão de preferências (Krehbiel, 1993).

**Modelo.** Os pontos ideais são fixos por período deputado×partido, e o modelo intrapartidário assume cargas comuns a todos os partidos. A validação é de imputação de votos, não de previsão temporal de votações futuras.

**Desenho causal.** O estudo de evento compara o deputado consigo mesmo e com os colegas na mesma votação, mas a troca é endógena. O período pós-janela tem só 66 votações, em ano eleitoral, e o pareamento entre suplente e titular é aproximado (mesma UF, ±10 dias).

## 8. Discussão

O primeiro achado é de medida. Na Câmara de 2023–2026, a orientação aplicável à maioria dos deputados do centro é a do bloco, e o registro da Câmara não guarda as orientações que os partidos dão em Plenário quando a bancada formal é um bloco. Em 2025, o resultado foi um registro quase vazio para a maior parte da Casa e uma disciplina "medida" que sobe justamente quando a unidade de quatro partidos de centro cai. Quem usa os dados públicos deve, por isso, estratificar pela fonte da orientação, reportar a cobertura e complementar o registro com uma medida que não dependa dele. Para a própria Câmara, registrar as orientações partidárias dentro dos blocos, que os líderes anunciam em Plenário, tornaria os dados abertos mais fiéis ao processo que pretendem descrever.

O segundo achado é que a indisciplina tem estrutura, mas pouca. A posição do partido em cada votação é de longe a melhor informação sobre o voto, e a propensão individual a desviar acrescenta mais do que a direção do desvio. A direção, porém, conta: prevê o voto fora da amostra além da propensão a desviar. Ela coincide com o eixo governo–oposição que separa os partidos entre si. Por isso os partidos do centro são, ao mesmo tempo, os mais heterogêneos e os pivôs da Casa: uma hipótese, que não testamos, é que essa heterogeneidade permita ao Governo construir maiorias votação a votação com parte de suas bancadas. A influência do partido além das preferências existe, porque o excesso de lealdade nas divergências com o Governo é positivo nos dois contrafactuais; sua magnitude, porém, depende de como se mede a preferência. A troca de partido mostra sinais tanto de seleção quanto de ajuste aos novos colegas.

## 9. Conclusão

Os deputados da 57ª Legislatura votam com a liderança em cerca de nove de cada dez votos nominais, e a unidade com os colegas varia pouco no tempo. A disciplina medida pela orientação registrada, porém, depende de quem orienta e do que a Câmara registra: para o centro, o bloco; no período do megabloco de 2025, quase sempre nada. A indisciplina restante tem uma direção individual, o eixo governo–oposição dentro de cada partido, pequena perto da posição do partido, mas distinguível de ruído.

Ficam pendentes:

- a extensão a outras legislaturas, para separar o que é próprio do terceiro governo Lula e da era dos megablocos;
- a reconstrução sistemática das orientações faladas;
- a incorporação de dados de emendas e cargos, para testar mecanismos;
- modelos dinâmicos de pontos ideais com validação temporal.

## Referências

AMES, Barry. *The Deadlock of Democracy in Brazil*. Ann Arbor: University of Michigan Press, 2001.

AMORIM NETO, Octavio; COX, Gary W.; McCUBBINS, Mathew D. Agenda Power in Brazil's Câmara dos Deputados, 1989–98. *World Politics*, v. 55, n. 4, p. 550–578, 2003.

BAFUMI, Joseph; GELMAN, Andrew; PARK, David K.; KAPLAN, Noah. Practical Issues in Implementing and Understanding Bayesian Ideal Point Estimation. *Political Analysis*, v. 13, n. 2, p. 171–187, 2005.

BLACK, Duncan. On the Rationale of Group Decision-making. *Journal of Political Economy*, v. 56, n. 1, p. 23–34, 1948.

CALLAWAY, Brantly; SANT'ANNA, Pedro H. C. Difference-in-Differences with Multiple Time Periods. *Journal of Econometrics*, v. 225, n. 2, p. 200–230, 2021.

CAMERON, A. Colin; GELBACH, Jonah B.; MILLER, Douglas L. Robust Inference with Multiway Clustering. *Journal of Business & Economic Statistics*, v. 29, n. 2, p. 238–249, 2011.

CAREY, John M. Competing Principals, Political Institutions, and Party Unity in Legislative Voting. *American Journal of Political Science*, v. 51, n. 1, p. 92–107, 2007.

CAREY, John M. *Legislative Voting and Accountability*. Cambridge: Cambridge University Press, 2009.

CARRUBBA, Clifford J.; GABEL, Matthew; HUG, Simon. Legislative Voting Behavior, Seen and Unseen: A Theory of Roll-Call Vote Selection. *Legislative Studies Quarterly*, v. 33, n. 4, p. 543–572, 2008.

CHEIBUB, José Antonio; FIGUEIREDO, Argelina; LIMONGI, Fernando. Political Parties and Governors as Determinants of Legislative Behavior in Brazil's Chamber of Deputies, 1988–2006. *Latin American Politics and Society*, v. 51, n. 1, p. 1–30, 2009.

CLINTON, Joshua; JACKMAN, Simon; RIVERS, Douglas. The Statistical Analysis of Roll Call Data. *American Political Science Review*, v. 98, n. 2, p. 355–370, 2004.

COX, Gary W.; McCUBBINS, Mathew D. *Setting the Agenda: Responsible Party Government in the U.S. House of Representatives*. Cambridge: Cambridge University Press, 2005.

DESPOSATO, Scott W. Correcting for Small Group Inflation of Roll-Call Cohesion Scores. *British Journal of Political Science*, v. 35, n. 4, p. 731–744, 2005.

DESPOSATO, Scott W. Parties for Rent? Ambition, Ideology, and Party Switching in Brazil's Chamber of Deputies. *American Journal of Political Science*, v. 50, n. 1, p. 62–80, 2006.

FIGUEIREDO, Argelina Cheibub; LIMONGI, Fernando. *Executivo e Legislativo na nova ordem constitucional*. Rio de Janeiro: Editora FGV, 1999.

HELLER, William B.; MERSHON, Carol. Party Switching in the Italian Chamber of Deputies, 1996–2001. *The Journal of Politics*, v. 67, n. 2, p. 536–559, 2005.

KREHBIEL, Keith. Where's the Party? *British Journal of Political Science*, v. 23, n. 2, p. 235–266, 1993.

KREHBIEL, Keith. *Pivotal Politics: A Theory of U.S. Lawmaking*. Chicago: University of Chicago Press, 1998.

LAUDERDALE, Benjamin E. Unpredictable Voters in Ideal Point Estimation. *Political Analysis*, v. 18, n. 2, p. 151–171, 2010.

MAINWARING, Scott P. *Rethinking Party Systems in the Third Wave of Democratization: The Case of Brazil*. Stanford: Stanford University Press, 1999.

McCARTY, Nolan; POOLE, Keith T.; ROSENTHAL, Howard. The Hunt for Party Discipline in Congress. *American Political Science Review*, v. 95, n. 3, p. 673–687, 2001.

MINOZZI, William; VOLDEN, Craig. Who Heeds the Call of the Party in Congress? *The Journal of Politics*, v. 75, n. 3, p. 787–802, 2013.

NICOLAU, Jairo. Disciplina partidária e base parlamentar na Câmara dos Deputados no primeiro governo Fernando Henrique Cardoso (1995-1998). *Dados*, v. 43, n. 4, p. 709–735, 2000. [verificar páginas]

NOKKEN, Timothy P. Dynamics of Congressional Loyalty: Party Defection and Roll-Call Behavior, 1947–97. *Legislative Studies Quarterly*, v. 25, n. 3, p. 417–444, 2000.

PEREIRA, Carlos; MUELLER, Bernardo. The Cost of Governing: Strategic Behavior of the President and Legislators in Brazil's Budgetary Process. *Comparative Political Studies*, v. 37, n. 7, p. 781–815, 2004.

POWER, Timothy J.; ZUCCO, Cesar. Estimating Ideology of Brazilian Legislative Parties, 1990–2005: A Research Communication. *Latin American Research Review*, v. 44, n. 1, p. 218–245, 2009.

RICE, Stuart A. The Behavior of Legislative Groups: A Method of Measurement. *Political Science Quarterly*, v. 40, n. 1, p. 60–72, 1925.

SNYDER, James M.; GROSECLOSE, Tim. Estimating Party Influence in Congressional Roll-Call Voting. *American Journal of Political Science*, v. 44, n. 2, p. 193–211, 2000.

SUN, Liyang; ABRAHAM, Sarah. Estimating Dynamic Treatment Effects in Event Studies with Heterogeneous Treatment Effects. *Journal of Econometrics*, v. 225, n. 2, p. 175–199, 2021.

ZUCCO, Cesar. Ideology or What? Legislative Behavior in Multiparty Presidential Settings. *The Journal of Politics*, v. 71, n. 3, p. 1076–1092, 2009.

ZUCCO, Cesar; LAUDERDALE, Benjamin E. Distinguishing Between Influences on Brazilian Legislative Behavior. *Legislative Studies Quarterly*, v. 36, n. 3, p. 363–396, 2011.

## Apêndice A – Reprodutibilidade e disponibilidade

Rodado da raiz do repositório, `python artigos/02-disciplina-intrapartidaria/analise.py` lê:

- `dados/leg57/*.parquet`;
- os embeddings do projeto, usados só para a reconciliação do Apêndice C;
- o cache de temas da API (`dados_aux/temas_proposicoes_votadas.csv`);
- as codificações feitas pelo assistente de IA para validar o classificador de tipo de votação (`dados_aux/validacao_tipo_votacao.csv`) e as associações fala→votação (`dados_aux/validacao_falas.csv`).

Com isso, grava `resultados.json` (2.146 números), `tabelas/*.md` e `figuras/*.png`, e monta este `artigo.md` a partir de `artigo_fonte.md`: cada número calculado no texto é uma referência a `resultados.json`; os poucos números escritos à mão (limiares, parâmetros de método) estão definidos no próprio texto ou no código. Os ajustes de pontos ideais ficam em cache em `dados_aux/cache/`, fora do git. Sem cache, a execução levou cerca de 11 minutos em 4 núcleos numa reexecução de verificação (Stage 2.5); com cache, 174 segundos. As sementes são fixas. Versões usadas: Python 3.13.18; numpy 2.5.3; pandas 3.0.5; scipy 1.18.1; scikit-learn 1.9.1; matplotlib 3.11.2.

Dados e código estão no repositório do projeto. Este artigo é um de sete trabalhos do mesmo projeto sobre a 57ª Legislatura; os demais tratam de outras dimensões dos deputados (temas, frentes, discursos, trajetórias). O plano de análise está em `pipeline/stage1_blueprint.md`, a verificação de integridade em `pipeline/stage2_5_integridade.md` e a revisão por pares em `pipeline/stage3_revisao.md`.

## Apêndice B – Desvios em relação ao plano de análise

O plano (`pipeline/stage1_blueprint.md`) foi escrito depois da análise descritiva preliminar (a disciplina por partido e ano) e antes das análises de estrutura, troca de partido e partido × Governo.

- **Confirmatórios**, no sentido de especificados antes de executados: a comparação M1→M2→M3→M4, a interpretação pelas cargas, a validação pelas trocas de 2026, o estudo de evento e o excesso de lealdade.
- **Exploratórios**, todos acrescentados depois da revisão por pares: as orientações faladas, M2b, a versão por coorte, a base datada e os limites com ausência. O teste com posições embaralhadas (M3emb), feito sem reajustar o modelo, foi retirado do texto por não ser informativo.

As mudanças marcadas com † foram feitas **depois** de ver resultados de validação cruzada.

| Plano | O que foi feito | Motivo |
|---|---|---|
| D só com orientação própria como medida principal | D com as camadas própria, bloco e bloco inferido; D própria como recorte; U como medida comparável | A orientação própria cobre poucos votos do centro |
| Bloco heterogêneo pela amplitude das medianas | Regra pelo nome (contém PL e a federação do PT) | Mais simples; só o megabloco a satisfaz |
| Validação manual do classificador (200) | Amostra estratificada de 120 (119 codificáveis; acurácia na seção 3) | Tempo |
| Ausência seletiva em PEC e PLP | Limite inferior geral e PEC | — |
| Recortes em regressão ao nível do voto | Médias ajustadas por partido×ano (tipos); tema só com médias brutas | Simplificação |
| Primeiro mandato, liderança, governador; logit misto | Não incluídos | Dados indisponíveis |
| M2 como logit do desvio com intercepto de célula† | M2 com *offset* de M1; M2b com a estrutura de M3; M0c, M3L e M3emb acrescentados | A forma original não continha M1; a revisão pediu um comparador com a mesma estrutura |
| Subamostras (b) e (c) separadas† | Células com divisão interna (b e c combinadas) e subamostra com minoria ≥ 10% | Robustez |
| Penalizações em todas as dobras | Sensibilidade na dobra 0 | Tempo |
| Modelos intra por partido; log-loss só nos desvios | Não feitos | Premissa de cargas comuns declarada (seção 7) |
| Cargas: top 20 e razões de chances por tema | Top 8 por sinal e composição por tipo | Simplificação |
| Contrafactual sem as votações divergentes | Dois contrafactuais (validação cruzada e M5 sem as células divergentes) | Votações excluídas por inteiro não teriam cargas estimáveis |
| Estudo de evento por coorte | Feito (coorte de 2026) | — |
| Decomposição da variância do desvio ajustado | Taxas brutas e parcela de ruído ajustada | Ambas reportadas |

## Apêndice C – Reconciliação com resultados prévios do projeto e fontes externas

O projeto já havia calculado taxas de alinhamento, dispersões, pivôs e dissidentes a partir dos embeddings dos deputados (`dados/leg57/embeddings/`), com Plenário e comissões e com o partido **atual**, posterior à janela de 2026. Reproduzimos esses números exatamente e explicamos as diferenças:

- **Alinhamento ao partido.** Em `alinhamento.parquet`, a taxa é de 98,4% no PT, 97,2% no PSOL e 97,0% no NOVO, e vai de 86,3% (PP) a 89,7% (REPUBLICANOS) no centro. É a mesma ordem de grandeza de D.
- **Dispersão no eixo global.** O projeto tinha PDT 0,17, PT 0,20, PSOL 0,25, PL 0,38, MDB 0,50 e PODE 0,55; os valores atuais estão na Tabela 7. Com o partido na data, o PL fica mais disperso: dos 20 períodos no PL a mais de um desvio-padrão acima da mediana do partido, 11 são de deputados que deixaram o PL.
- **Pivôs.** Os cinco mais próximos da mediana no painel do projeto eram Luiz Carlos Hauly, João Leão, Luiz Gastão, José Rocha, Marx Beltrão. Aqui, José Rocha e Marx Beltrão estão em 1º e 2º, Luiz Gastão e João Leão em 6º e 8º, e Luiz Carlos Hauly em 42º.
- **Dissidentes.** O painel destacava no PL João Carlos Bacelar, Henrique Júnior, Bosco Costa. Bosco Costa e Henrique Júnior são suplentes com 67 e 86 votos no Plenário, abaixo do limiar de 100, assim como Daniel José (57).
- **Validação.** O modelo intrapartidário do projeto acertava 92,9% dos votos fora da amostra, com Plenário e comissões; aqui, M4 acerta 92,8% em todas as células do Plenário. Os pontos globais correlacionam 0,998 com os do projeto.
- **Base ministerial.** Em 1/1/2023, formaram o governo PT, PSB, MDB, PSD, União, PDT, PCdoB, PSOL e REDE; PP e REPUBLICANOS entraram em 13/09/2023. Houve saídas e rompimentos em 2025–2026: União e PP anunciaram a saída em setembro de 2025, e ministros deixaram os cargos em abril de 2026 para disputar eleições. Usamos a filiação em qualquer momento do período (fontes em `pipeline/stage4_bibliografia.md`; datas finas [verificar]).

## Apêndice D – Tabelas complementares

**Tabela A1 – Disciplina (D) e unidade (U) por tema da proposição votada (ordem crescente de U)**

| Tema | Votações | D | U |
|---|---|---|---|
| Homenagens e Datas Comemorativas | 32 | 85,7 | 84,4 |
| Política, Partidos e Eleições | 44 | 88,9 | 86,1 |
| Comunicações | 32 | 85,4 | 86,3 |
| Direito e Justiça | 51 | 90,9 | 86,3 |
| Direito e Defesa do Consumidor | 18 | 86,9 | 87,2 |
| Administração Pública | 330 | 89,9 | 87,3 |
| Processo Legislativo e Atuação Parlamentar | 40 | 92,0 | 87,8 |
| Cidades e Desenvolvimento Urbano | 25 | 88,6 | 88,1 |
| Finanças Públicas e Orçamento | 427 | 89,4 | 88,7 |
| Arte, Cultura e Religião | 38 | 92,5 | 88,8 |
| Outros temas | 11 | 91,8 | 89,1 |
| Esporte e Lazer | 17 | 88,8 | 89,3 |
| Economia | 163 | 90,1 | 89,6 |
| Viação, Transporte e Mobilidade | 59 | 90,8 | 90,0 |
| Trabalho e Emprego | 87 | 91,7 | 90,2 |
| Energia, Recursos Hídricos e Minerais | 60 | 91,4 | 90,3 |
| Relações Internacionais e Comércio Exterior | 57 | 90,8 | 90,3 |
| Direitos Humanos e Minorias | 178 | 91,2 | 90,4 |
| Ciência, Tecnologia e Inovação | 34 | 90,0 | 90,4 |
| Meio Ambiente e Desenvolvimento Sustentável | 119 | 91,8 | 90,7 |
| Defesa e Segurança | 86 | 93,8 | 90,7 |
| Direito Constitucional | 23 | 92,4 | 91,4 |
| Direito Penal e Processual Penal | 95 | 92,7 | 91,8 |
| Indústria, Comércio e Serviços | 72 | 91,5 | 91,9 |
| Educação | 64 | 93,6 | 92,0 |
| Direito Civil e Processual Civil | 32 | 92,2 | 92,2 |
| Previdência e Assistência Social | 41 | 93,4 | 93,0 |
| Saúde | 76 | 94,8 | 93,4 |
| Agricultura, Pecuária, Pesca e Extrativismo | 43 | 94,8 | 93,9 |
| Estrutura Fundiária | 45 | 94,8 | 94,6 |

*Temas oficiais da Câmara (multi-rótulo, peso 1/k); temas com < 15 votações em 'Outros temas'.*

**Tabela A2 – Dissidentes sistemáticos: maiores distâncias à mediana do próprio partido (dim1 global)**

| Sentido | Deputado | Partido | Votos | Posição relativa (DP do partido) | IC 95% (DP do partido) |
|---|---|---|---|---|---|
| mais governista que o partido | João Carlos Bacelar | PL | 560 | 4,2 | [3,9; 4,5] |
| mais governista que o partido | Junior Lourenço | PL | 514 | 3,4 | [3,2; 3,7] |
| mais governista que o partido | Tiririca | PL | 664 | 3,4 | [3,1; 3,7] |
| mais governista que o partido | Robinson Faria | PL | 631 | 2,7 | [2,5; 3,0] |
| mais governista que o partido | Júnior Mano | PL | 194 | 2,7 | [2,3; 3,1] |
| mais governista que o partido | Florentino Neto | PT | 867 | 2,6 | [1,7; 3,6] |
| mais oposicionista que o partido | Sargento Fahur | PSD | 947 | −4,6 | [−5,4; −4,1] |
| mais oposicionista que o partido | Zucco | REPUBLICANOS | 278 | −3,8 | [−4,8; −3,1] |
| mais oposicionista que o partido | Mauricio Marcon | PODE | 839 | −3,8 | [−4,3; −3,5] |
| mais oposicionista que o partido | Evair Vieira de Melo | PP | 817 | −3,5 | [−4,0; −3,1] |
| mais oposicionista que o partido | Messias Donato | REPUBLICANOS | 910 | −3,1 | [−3,3; −2,7] |
| mais oposicionista que o partido | Pezenti | MDB | 944 | −2,9 | [−3,2; −2,6] |

*Períodos deputado×partido com ≥ 100 votos, a pelo menos 2 desvios-padrão da mediana do partido e com IC 95% (bootstrap de votações, 100 réplicas, Procrustes) que exclui essa mediana.*

**Tabela A3 – Deputado mediano e pivôs de 3/5 por semestre (dim1 global)**

| Semestre | Em exercício | Com ponto ideal | Mediano | Pivô 40% | Pivô 60% |
|---|---|---|---|---|---|
| 2023S1 | 512 | 510 | Márcio Marinho (REPUBLICANOS) | Ricardo Silva (PSD) | Lula da Fonte (PP) |
| 2023S2 | 513 | 513 | Luiz Gastão (PSD) | Fred Linhares (REPUBLICANOS) | Igor Timo (PODE) |
| 2024S1 | 512 | 511 | José Nelto (PP) | Paulo Alexandre Barbosa (PSDB) | Igor Timo (PODE) |
| 2024S2 | 513 | 512 | Julio Arcoverde (PP) | Julio Cesar Ribeiro (REPUBLICANOS) | Pedro Paulo (PSD) |
| 2025S1 | 512 | 512 | Gutemberg Reis (MDB) | Danilo Forte (UNIÃO) | Mersinho Lucena (PP) |
| 2025S2 | 512 | 512 | Aureo Ribeiro (SOLIDARIEDADE) | Marcos Pereira (REPUBLICANOS) | Mersinho Lucena (PP) |
| 2026S1 | 513 | 503 | Amom Mandel (REPUBLICANOS) | Beto Preto (PSD) | Mersinho Lucena (PSD) |
| 2026S2 | 512 | 498 | Robinson Faria (PP) | Marcos Pereira (REPUBLICANOS) | Ricardo Ayres (REPUBLICANOS) |

*Deputados em exercício na data de referência do semestre, com ≥ 30 votos no período deputado×partido vigente. Pivô 60%: o 308º de 513 a partir da oposição; pivô 40%: o 308º a partir do governo.*
