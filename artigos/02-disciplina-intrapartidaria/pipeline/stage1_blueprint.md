# Stage 1 — Methodology Blueprint (Fase 1, Scoping)

**Artigo 2:** "Disciplina partidária, orientação das lideranças e variação dentro dos partidos na 57ª Legislatura da Câmara dos Deputados (2023–nov/2026)"
**Papel:** `research_architect_agent` (ARS). Entrega única: este blueprint. Não contém o artigo nem resultados substantivos novos. Os números citados são **checagens de viabilidade/medida** feitas nos dados (`dados/leg57`, 13/11/2026), não achados.
**Base:** rascunho v0 (fim de `NOTAS_PASSAGEM.md`), `analise.py` (parte 1), `embeddings_deputados.py` (`ajustar_irt`, `preparar_votos`, `emb_votos`), `README.md`.
**Fora de escopo, por instrução:** IRB/human subjects (dados públicos agregados de votos nominais de agentes públicos), checkpoint cross-model e inquiry ledger (flags não setadas).

---

## 0. Checagens de viabilidade que mudam o desenho

| # | Checagem | Resultado | Consequência |
|---|---|---|---|
| C1 | Fonte da orientação por partido (Plenário) | UNIÃO e PP: ~99% das orientações vêm de **bloco**; PSD ~80% bloco; MDB, REPUBLICANOS, PSDB, PODE ≈ metade "bloco", metade "bloco (inferido)"; PT/PSOL/PCdoB/PV via federação; PL e NOVO via partido. | "Disciplina partidária" é, para o centrão, **disciplina ao líder do bloco**. Medida principal precisa ser estratificada por fonte e complementada por uma medida que não dependa de orientação (unidade com a maioria do partido). |
| C2 | Megabloco "Bl PlFdrPtUniPp..." (fev–out/2025; duas grafias: `...PtUniPp...`, `...PTUniPp...`) | Contém PL **e** Fdr PT, UNIÃO, PP, REPUBLICANOS, PSD, MDB, PDT, PODE, PSDB, PSB, PCdoB. Recebe 306 votações nominais de Plenário, mas só orienta (Sim/Não/Obstrução) em **38**. Votos do PT atribuídos ao megabloco: 12.422; com orientação diretiva: 1.058 (= **8,5%** de cobertura). Nesses 1.058, o PT seguiu a orientação do megabloco em **94,9%** (1.004); a orientação do megabloco coincidiu com a do Governo em todos os casos com ambas definidas. PL também foi comparado ao megabloco (21.399 votos; 2.800 diretivos; 87,9% de "disciplina"). | **Divergência com a nota do coordenador:** reproduzi os 12.422 e os 1.058, mas o valor de 8% corresponde à *cobertura* (1.058/12.422), não à taxa de disciplina, que é 94,9%. O problema real é outro: (i) a referência "orientação do bloco" para PT e PL simultaneamente não tem sentido substantivo (um bloco de mesa/proporcionalidade, não de coordenação de voto); (ii) as 38 votações orientadas são provavelmente consensuais, logo a "disciplina" medida é trivial. Ver §3.1 e R2. |
| C3 | Orientação vazia por ano (Plenário) | 2023: 1,7%; 2024: 5,4%; **2025: 59,6%** (abr–ago/2025: 78–93%); 2026: 13,3%. | O "aumento" de disciplina em 2025 (89,5% → 92,4%) é estimado sobre um subconjunto pequeno e selecionado de votações. Toda série temporal precisa reportar a **cobertura** e ser refeita com uma medida não dependente de orientação. A comparação antes/depois da troca e qualquer controle por ano herdam esse problema. |
| C4 | Trocas de partido (`deputados_partidos`) | 210 transições; ~140 em mar–mai/2026 (janela partidária). Inclui **fusões/incorporações**, não decisões individuais: PSC→PODE (9), PATRIOTA→PRD (8), também PTB→PRD e PROS→SOLIDARIEDADE. | `n_trocas` do v0 mistura escolha individual com fusão. Recodificar. Período pós-janela tem só ~67 votações de Plenário (2026T2–T4), em ano eleitoral: baixo poder. |
| C5 | Votações por trimestre | Concentração em 2023T4, 2025T2–T4; 2026T3–T4 quase vazio (17). | Bootstrap e comparações por ano devem usar votações como unidade de reamostragem; 2026 pós-janela é pequeno. |
| C6 | Tamanho das células partido×votação (votantes Sim/Não/Obstrução, Plenário) | Mediana 11; 27% das células com < 5 votantes; 9% com ≤ 2. | Confirma o risco do v0: efeitos fixos partido×votação saturados com bancadas pequenas. Ver §4.4. |
| C7 | "Artigo 17" | Arthur Lira (318), Hugo Motta (279), Sóstenes Cavalcante (60, presidência eventual). | Excluir esses registros em todas as medidas (não é voto). O presidente da Câmara fica fora do denominador na votação em que preside. |
| C8 | Pacotes | `statsmodels`, `scipy`, `sklearn` disponíveis; `pyfixest`/`linearmodels` não; 4 CPUs. | Regressões com efeitos fixos de alta dimensão devem ser implementadas por *demeaning* iterativo (projeções alternadas) em numpy dentro de `analise.py` (~60 linhas), com erros-padrão agrupados calculados à mão. |
| C9 | `preparar_votos` de `embeddings_deputados.py` | Lê **todos** os votos (Plenário + comissões). `ajustar_irt` não aceita `ndim=0` (`np.stack` de lista vazia). | O artigo deve preparar seus próprios arrays (só Plenário) e chamar `ajustar_irt` diretamente. Linha de base "só efeito fixo" via `ndim=1` com penalidade alta em x (§4.4). |

---

## Methodology Blueprint

### Research Paradigm
**Selecionado:** pós-positivista / pragmático-quantitativo.
**Justificativa:** as perguntas são de medição (quanta disciplina, onde falha), de estrutura latente (a indisciplina é de baixa dimensão?) e de associação (correlatos do desvio; a quem se obedece quando partido e Governo divergem). Todas se respondem com medidas observáveis de comportamento de voto e modelos de medição probabilísticos, com incerteza explícita. Não há pretensão causal forte: a única estimativa com desenho quase-causal (troca de partido) é tratada como descritiva-condicional, e o texto deve dizer isso.

### Method
**Tipo:** quantitativo, observacional, com dados secundários administrativos (censo das votações nominais do Plenário).
**Método específico:** (i) medidas descritivas de disciplina e coesão com correções de tamanho; (ii) modelos de pontos ideais (IRT bilinear penalizado, família Clinton–Jackman–Rivers/IDEAL) global e intrapartidário, avaliados por **validação cruzada fora da amostra** contra linhas de base hierarquizadas; (iii) regressões ao nível do voto com efeitos fixos de alta dimensão (partido×votação, deputado) e erros agrupados em duas vias; (iv) análise condicional das votações em que partido e Governo divergem.
**Justificativa:** P1 e P3 exigem medidas descritivas robustas a cobertura de orientação e tamanho de bancada; P2 e P4 são perguntas de *informação incremental* e, portanto, de previsão fora da amostra (é o único jeito de distinguir estrutura de sobreajuste num modelo com milhares de parâmetros); P5 é uma comparação dentro da mesma votação e do mesmo partido.

### Data Strategy
**Tipo:** secundário.
**Fontes:** `dados/leg57/votos.parquet` (473.323 votos; Plenário 456.837 em 1.128 votações nominais), `votacoes.parquet`, `votacoes_orientacoes.parquet`, `deputados.parquet`, `deputados_partidos.parquet`, `deputados_historico.parquet`, `proposicoes_temas.parquet` (+ cache da API em `dados_aux/`), `frentes_deputados.parquet`, `dados/leg57/embeddings/emb_votos.parquet` (só para conferência).
**Amostragem:** censo das votações nominais do Plenário de 14/03/2023 a 14/10/2026 (última votação na base). Comissões apenas como robustez (composição selecionada, orientação rara).
**Recorte temporal:** 57ª Legislatura até a extração (nov/2026). Retrato até a data da extração; a legislatura termina em 31/01/2027.

**Regras de dados (obrigatórias, corrigem o v0):**
1. Partido = `deputado_siglaPartido` (partido na data). `deputados.siglaPartido` é o partido atual e **não** pode ser usado para nada além de rótulo final.
2. Excluir `voto == "Artigo 17"` e `voto` nulo; excluir `S.PART.`.
3. Trocas de partido: construir a partir de `deputados_partidos`, marcando como **fusão** (não troca) as transições PSC→PODE, PATRIOTA→PRD, PTB→PRD, PROS→SOLIDARIEDADE (e qualquer outra em que o partido de origem deixa de existir na data; conferir em `deputados_historico`). Ignorar "trocas" com data anterior à primeira votação da legislatura (fev–mar/2023) como reajuste de cadastro, a verificar caso a caso.
4. Suplência como variável **variável no tempo**: a partir de `deputados_historico`, construir os períodos de exercício (posse/reassunção/afastamento) e marcar, para cada voto, se o deputado estava em exercício como titular ou como suplente; registrar, para suplentes, o motivo do afastamento do titular (Ministro de Estado, Secretário de Estado/Capital, licença saúde etc.). `condicaoEleitoral` de `deputados` é o estado final e só serve como robustez.
5. **Painel de presença (novo):** com os mesmos períodos de exercício, montar para cada votação o conjunto de deputados em exercício. Validação: deve somar 513 (±licenças em curso) em cada data. Isso converte "ausência não observada" em "ausência observada entre os em exercício" (sem saber o motivo). Se a validação falhar em mais de 2% das datas, a análise de ausência vira apenas limitação.
6. Tamanho da bancada da UF: usar o número legal de cadeiras por UF (fixo: 8 a 70), não a contagem de titulares em `deputados`.
7. `resultados.json`: serializar NaN como `null`.

### Analytical Framework

Organização por pergunta. Para cada análise: medida/modelo, expectativa teórica (E), resultado que a contrariaria (✗).

#### 1. Definições operacionais (P1) — crítica e decisão

**1.1 Três medidas, não uma.** O v0 só tem "disciplina = voto igual à orientação". Dadas C1–C3, isso mistura três objetos. Definir:

- **Disciplina à liderança (D):** P(voto = orientação | orientação diretiva). Reportada em três camadas por fonte:
  - **D-própria** (principal para inferência sobre partidos): orientação do próprio partido ou da sua federação (`orientacao_fonte ∈ {partido, federacao}`).
  - **D-bloco**: orientação de bloco explícito (`bloco`), excluindo blocos heterogêneos (abaixo).
  - **D-inferida**: `bloco (inferido)`; só robustez.
  - Regra de **bloco heterogêneo**: um bloco é heterogêneo se contém simultaneamente partidos da oposição (PL, NOVO) e da federação do PT; operacionalmente, se a amplitude das medianas dos partidos-membros na dim1 global (ajuste com os votos de 2023–2024, para evitar circularidade) excede a amplitude média dos blocos não heterogêneos em mais de 2 DP. Pelo critério nominal, os dois rótulos `Bl PlFdrPtUniPp...`/`Bl PlFdrPTUniPp...` e `Bl PlUniPpPsd...` devem ser checados; o megabloco de 2025 é excluído por construção. Orientações de blocos heterogêneos **não** contam como orientação do partido (viram "sem orientação aplicável").
- **Unidade partidária (U):** P(voto = voto majoritário do partido do deputado na votação), calculada *leave-one-out* (maioria dos demais colegas do partido presentes, células com ≥ 5 colegas). Não depende de registros de orientação e existe para 100% das votações e partidos; é a medida comparável no tempo e entre partidos (Carey 2007; "party unity"). Permite separar *liderança* (D) de *coesão* (U).
- **Coesão (Rice)**: ver §2.

A diferença D − U, por partido e fonte, é ela própria informativa: se D ≈ U, a orientação apenas registra a posição majoritária; se D < U em blocos, o líder do bloco orienta contra a maioria do partido (bloco como principal concorrente).

**1.2 Tratamento das categorias de voto.**

| Voto \ Orientação | Sim | Não | Obstrução | Liberado / vazia |
|---|---|---|---|---|
| Sim | segue | desvia | desvia | fora de D (entra em U e Rice) |
| Não | desvia | segue | segue (direcional) / desvia (estrita) | idem |
| Obstrução | desvia | segue (direcional) / desvia (estrita) | segue | idem (raríssimo) |
| Abstenção | desvio brando | desvio brando | desvio brando | idem |
| Artigo 17 | excluído | excluído | excluído | excluído |

- **Medida principal: direcional** (Não ≡ Obstrução = "contra a matéria"), porque a obstrução é um instrumento de quórum da bancada e um "Não" de quem recebe ordem de obstruir não é dissidência quanto ao conteúdo (dos que não obstruíram sob orientação de obstrução, 13,6% votaram Não e 10,4% Sim — só estes últimos são dissidência substantiva). A estrita fica como robustez e como indicador de **cumprimento tático** (quem não aderiu à obstrução).
- **Abstenção:** contar como desvio na principal (o líder pediu uma direção) e reportar separadamente a decomposição do desvio em "voto contrário" vs. "abstenção". Robustez: excluir abstenções do denominador.
- **Denominador:** votos de deputados presentes (Sim/Não/Obstrução/Abstenção) em votações com orientação diretiva aplicável (D) ou em células com ≥ 5 colegas (U). Reportar sempre, ao lado de cada taxa, a **cobertura** = votos no denominador / votos válidos, por partido e ano. Nenhuma taxa sem cobertura.
- **"Liberado":** fora de D; analisado à parte como contraste (o partido racha quando libera? U e Rice nas liberadas vs. nas orientadas, mesma bancada).

**1.3 Ausências.** Não há registro de ausência; com o painel de presença (regra 4–5) mede-se a não-participação entre os em exercício. Decisão:
- Principal: condicional à presença (como o v0), dito explicitamente.
- Sensibilidade "ausência como desvio" restrita a **PECs (mérito, 1º e 2º turno) e PLPs**, onde a ausência tem efeito de "Não" (quórum qualificado de 308/257 votos Sim) e é estratégica por construção: D_PEC_ampla = segue / (presentes + ausentes em exercício) quando a orientação é Sim.
- Diagnóstico: taxa de ausência por deputado em votações em que o partido orienta contra a posição prevista do deputado (pelo IRT ajustado sem essas votações) vs. as demais. Se a ausência for maior quando o deputado está "do lado errado", a disciplina condicional à presença está inflada. Isso também é um teste da tese de abstenção estratégica.
- Expectativa (Figueiredo & Limongi; Carey): ausência seletiva existe mas é pequena frente ao desvio aberto. ✗: ausência seletiva da mesma ordem dos desvios abertos.

**1.4 Recortes de P1.** Partido; ano (e semestre); fonte da orientação; tipo de orientação (Sim/Não/Obstrução); tipo de votação (classificador por `descricao` já em `analise.py`: requerimento procedimental, urgência, mérito, destaque, emenda, PEC); tipo de proposição (PEC, PLP, PL, MPV, PDL); tema. Exigências:
- **Validar o classificador de tipo de votação**: amostra aleatória estratificada de 200 descrições codificada manualmente, reportar acurácia por classe; regras de desempate documentadas.
- **Temas:** completar via API com cache (já implementado em `temas_proposicoes`) e fixar o cache no repositório (`dados_aux/`), para reprodutibilidade sem rede. Multi-rótulo: atribuir peso 1/k a cada um dos k temas. Votações de requerimentos herdam o tema da proposição afetada; reportar tema também só em votações de mérito. Temas com < 15 votações agrupados em "outros".
- Comparações por recorte em **regressão ao nível do voto** com efeito fixo de partido (e de ano), não em médias brutas, porque a composição partidária das votações difere por tipo/tema. Apresentar médias brutas com IC por bootstrap de votações e as diferenças ajustadas.
- E (Figueiredo & Limongi; Cheibub, Figueiredo & Limongi 2009): disciplina alta (≈ 90%) e estável; mais alta em mérito/PEC do Executivo, mais baixa em destaques e emendas (onde o custo da defecção é menor e a agenda menos controlada pelo líder). ✗: disciplina em mérito/PEC não maior que em destaques após ajuste por partido; ou variação temporal grande em U (não só em D).

#### 2. Coesão: Rice com correção de tamanho (P1, P3)

- **Rice bruto** por partido×votação: |S − N|/(S + N), Obstrução = Não, Abstenção fora; células com ≥ 3 votantes.
- **Correção de Desposato (2005):** o `analise.py` calcula E[Rice] de subamostra hipergeométrica de tamanho m = 10 — correto e preferível à reamostragem Monte Carlo. Ajustes: (i) reportar m = 10 (principal) e m = 5 (robustez, para incluir bancadas pequenas — PSOL, PCdoB, PV, NOVO, REDE, CIDADANIA); (ii) partidos com mediana de votantes < m não recebem Rice padronizado (marcar "–"), em vez de sumir silenciosamente; (iii) mostrar o Rice esperado sob votação aleatória com p = proporção de Sim do plenário (linha de base "sem partido"), para que o leitor veja quanto da coesão é só o tamanho/consenso.
- **Votações disputadas:** principal = minoria do plenário ≥ 10% (como no v0); robustez com 20% e com o **Rice ponderado por disputa** de Carey (2007), peso = 1 − |2p − 1| da votação. Reportar também a proporção de votações em que o partido "racha" (Rice < 0,5; isto é, < 75% num lado).
- E (Snyder & Groseclose 2000; Krehbiel 1993): a coesão em votações disputadas é a evidência relevante; em votações consensuais a coesão é trivial. Diferença PT/PSOL/NOVO (alta) vs. UNIÃO/PSDB/PP/PSD (menor). ✗: ranking de coesão entre partidos que se inverta entre "todas" e "disputadas" ou entre m = 5 e m = 10 (indicaria artefato de tamanho/agenda).

#### 3. Quem se desvia: regressão do desvio individual (P3)

**Crítica ao v0:** (a) unidade agregada por deputado com efeito fixo de partido ignora que deputados votam conjuntos diferentes de votações (suplentes entram em janelas diferentes; trocadores mudam de partido), logo a taxa individual é comparada contra agendas distintas; (b) `troca` agregada é pós-tratamento e mistura fusões; (c) `suplente` fixo no tempo; (d) R² = 0,998 decorre de `ols(..., weights=...)` com fração agregada e não é a estatística certa; (e) HC1 em GLM com `var_weights` ignora a dependência dentro da votação.

**3.1 Desenho principal (nível do voto):**
Unidade: deputado *i* × votação *j* com orientação diretiva (D-própria + D-bloco não heterogêneo) — e, em paralelo, com U como desfecho (todas as votações).
Modelo de probabilidade linear (MPL) com efeitos fixos de alta dimensão:

  desvio_ij = β·X_i(t) + γ_{p(i,t)×j} + ε_ij

- γ_{p×j} (partido×votação) absorve a orientação, o conteúdo, o contexto temporal e o nível de racha do partido naquela votação: o β compara deputados **do mesmo partido na mesma votação**.
- X_i(t): suplente em exercício (variável no tempo; categorias titular / suplente por titular-ministro / suplente por titular-secretário / outro), mulher, idade (décadas), log cadeiras legais da UF, primeiro mandato (se recuperável de `deputados_historico`; senão, omitir), membro da Mesa/liderança (se houver dado; senão, limitação), *distância ideológica ao partido* = |x_i − mediana do partido| na dim1 global **estimada só com votações de outro período** (2023–2024 para explicar 2025–2026 e vice-versa) para evitar circularidade (Krehbiel: o "desvio" pode ser só preferência).
- UF: teste conjunto de efeitos de UF (Wald com variância agrupada) e, como alternativa substantiva, o indicador "governador da UF do mesmo partido/oposto" se for possível codificar (exige dado externo: anotar como opcional; Cheibub, Figueiredo & Limongi 2009; Carey 2009 competing principals).
- **Erros agrupados em duas vias: deputado e votação** (Cameron, Gelbach & Miller 2011). Com ~20 partidos, *não* agrupar só por partido.
- Implementação: *demeaning* iterativo para γ (≈ 22,6 mil células) em numpy; logit condicional como robustez numa subamostra (ou GLM logit com efeitos fixos de partido×ano + votação, se o tempo permitir).
- Variância entre deputados: substituir o R² pela **decomposição da variância do sinal**: var(taxa de desvio ajustada por deputado) − média das variâncias binomiais de amostragem = variância "verdadeira" entre deputados; reportar a fração explicada por partido (e por X). Alternativa: logit misto com intercepto aleatório de deputado (statsmodels `BinomialBayesMixedGLM`) se convergir em tempo razoável.
- E (Carey; Ames; Cheibub et al.): suplentes, especialmente de titulares-ministros, desviam *menos* do Governo e podem desviar *mais* do partido quando partido e Governo divergem; bancadas de UF grandes (SP, MG, RJ) mais independentes; distância ideológica ao partido é o preditor dominante (Krehbiel). ✗ para a tese "liderança importa além das preferências": se, controlada a distância ideológica medida fora do período, nenhuma característica institucional (suplência, UF, troca futura) se associar ao desvio — aí a disciplina seria preferência pura.

**3.2 Troca de partido (event study intra-deputado):**
- Amostra: votos de Plenário; tratados = deputados com troca **individual** (fusões excluídas; fusões viram um grupo placebo próprio — troca sem escolha).
- Modelo: desvio_ij = α_i + γ_{p(i,t)×j} + Σ_k θ_k·1[t − T_i ∈ k] + ε_ij, com janelas k em meses relativos à troca (−12…−7, −6…−4, −3…−1, 0…3, 4+), referência −12…−7. α_i (efeito fixo de deputado) retira a propensão individual; γ_{p×j} retira tendência temporal geral, agenda e o fato de a referência mudar de partido (o desvio é sempre relativo aos colegas *atuais* na mesma votação) — isso resolve o confundimento com a tendência de 2023→2025 apontado nas notas. Erros agrupados por deputado e votação.
- Com ~2/3 das trocas na janela de abril/2026 (adoção quase simultânea), o estimador de diferenças-em-diferenças com efeitos fixos não sofre o viés de "tratados antigos como controle" de forma relevante; ainda assim reportar a versão restrita à coorte da janela de 2026 com controles nunca tratados (Callaway & Sant'Anna como conceito; implementação simples por coorte).
- Desfechos: D (onde houver orientação aplicável dos dois lados) e U (sempre disponível — **principal**, por C3).
- Leads (θ antes de 0) são substantivos, não só teste de pré-tendência: a hipótese de "sinalização de saída" prevê desvio crescente nos meses pré-janela. Distinguir: pré-tendência suave (sinal de saída) vs. salto em 0 (efeito do novo principal).
- Poder: pós-janela só ~67 votações (ano eleitoral). Reportar IC; não interpretar nulos como ausência de efeito.
- E: desvio maior antes da troca (incongruência com o partido de origem) e menor depois (congruência com o novo; seleção por preferência — Desposato 2006 sobre trocas no Brasil). ✗: nenhuma diferença pré/pós em U com IC estreito; ou queda do desvio também entre os "trocadores por fusão" (indicaria artefato de medida).
- **Remover** o teste de Wilcoxon antes/depois do v0 do texto principal (confundido com o tempo e com C3); manter como descritivo no apêndice, explicitamente rotulado.

#### 4. Ruído vs. estrutura: IRT intrapartidário fora da amostra (P2, P4)

**Crítica ao v0:** (a) a validação existente (intra 92,9% vs. global 91,9%) mede sobretudo o ganho do efeito fixo g_{p×j}, não da dimensão individual; (b) acurácia é pouco sensível quando a taxa-base de seguir o partido é ~90–95% — tem de ser log-loss; (c) não há linha de base que separe "estrutura espacial" de "heterogeneidade de lealdade" (alguns deputados simplesmente desviam mais, em qualquer direção); (d) o modelo intrapartidário assume **o mesmo vetor b_j para todos os partidos** — a dimensão de dissidência do PT seria a mesma do PL; (e) bancadas pequenas saturam g.

**4.1 Dados:** só Plenário; Sim = 1, Não/Obstrução = 0; votações com minoria ≥ 2,5% (como no pacote); pontos por período deputado×partido com `base` e `centrar` como em `emb_votos`.

**4.2 Modelos comparados (mesmas dobras, mesmos hiperparâmetros de penalização onde aplicável):**

| Modelo | Conteúdo | Implementação |
|---|---|---|
| M0 | Orientação diretiva do partido (D-própria/bloco); se ausente, maioria do partido na dobra de treino; se ausente, maioria da votação | regra |
| M1 | Só efeitos a_j + g_{p×j} (posição do partido na votação), sem ponto individual | `ajustar_irt(ndim=1, grupos=grp, centrar=part, base=base_dep, lam_d=1e4, lam_x=1e4)` — idêntico ao M3 exceto pela variância de x, que fica ~0. Assim a penalização de g é a mesma e a comparação isola x. |
| M2 | M1 + **propensão individual de desvio, não espacial**: P(votar contra a maioria do partido) = σ(κ_{p×j} + r_i) | logit penalizado próprio (L-BFGS, ~40 linhas) sobre o desfecho "desvia da maioria de treino da célula"; convertido em P(Sim) para o log-loss. |
| M3 | Intra 1D (`grupos` + `centrar`, `ndim=1`, `lam_d=4`) | `ajustar_irt` |
| M4 | Intra 2D | `ajustar_irt` |
| M5 | Global 2D (sem g), referência | `ajustar_irt` |

Interpretação: M1→M2 = valor da "lealdade" individual; M2→M3 = valor da *direção* (estrutura espacial intrapartidária); M3→M4 = segunda dimensão. "Ruído" = M3 e M4 não melhoram M2 fora da amostra.

**4.3 Protocolo de validação:**
- **Validação cruzada em 5 dobras sobre células deputado×votação**, estratificada por votação (cada votação com ~20% dos votos em cada dobra). É o desenho correto para modelos de completação de matriz; dobras por votação inteira não servem (a_j, b_j, g não seriam estimáveis).
- **Métricas:** log-loss (principal), Brier, acurácia, e para o evento raro "desvio" (votar contra a maioria de treino da célula): **AUC-PR** e log-loss restrito aos votos de desvio vs. não-desvio. Nota: avaliar a capacidade de ranquear desvios (AUC-PR, condicional ao desfecho) é legítimo como métrica de classificador; o que **não** se deve fazer é *restringir a amostra de treino ou de teste* aos votos em que o deputado se desviou (seleção pela variável dependente, que garante ganho espúrio a qualquer modelo com parâmetro individual).
- **Subamostras de avaliação definidas ex ante (só com informação de treino):** (a) todas as células; (b) **células disputadas internamente**: partido×votação com ≥ 1 desvio no treino *ou* minoria interna de treino ≥ 10%; (c) células com ≥ 5 colegas de partido no treino. A subamostra (b) é onde a estrutura, se existir, aparece; (a) é dominada por votos triviais.
- **Contra a inflação por células pequenas:** (i) avaliar só em (c); (ii) reportar por faixa de tamanho de bancada (< 5, 5–19, 20–49, ≥ 50); (iii) robustez com penalização de g mais forte (`lam_g` = 0,1 e 1, encolhendo g para a_j), mesma em M1–M4.
- **Incerteza da comparação:** diferenças pareadas de log-loss por dobra e IC por bootstrap de deputados (reamostrar deputados sobre as perdas de teste já calculadas, sem reajuste: barato).
- **Sensibilidade à penalização:** M3/M4 com `lam_d` ∈ {1, 4, 16}; escolher por log-loss médio e reportar todos.
- **Heterogeneidade por partido (corrige a premissa de b_j comum):** ajustar intra 1D *separadamente* para os 7 maiores partidos (PL, PT, UNIÃO, PP, REPUBLICANOS, PSD, MDB) só com seus votos (rápido: matrizes menores) e (i) comparar o log-loss do modelo comum vs. específico; (ii) correlacionar os b_j específicos entre partidos. Correlação baixa = dissidência específica de cada partido; alta = um eixo comum (provavelmente governo×oposição).
- **Tempo:** 5 dobras × (M1, M3, M4) ≈ 15 ajustes intra × ~106 s ≈ 27 min; M2 e M0 em segundos; M5 5 × 20 s. Por-partido: ~7 × < 30 s. Modo `--rapido`: uma única partição 80/20.
- E (Figueiredo & Limongi; Zucco): a maior parte da previsibilidade está na orientação/posição do partido (M0, M1 ≫ base); a dissidência tem estrutura fraca, concentrada no eixo governo×oposição dentro dos partidos do centrão (Zucco 2009, governismo). Krehbiel prevê M3 ≫ M2 (preferências individuais estruturadas). ✗ para "estrutura": M3 e M4 não reduzem o log-loss de M2 nas células disputadas internamente (IC da diferença inclui 0); ✗ para "partido importa": M5 (sem partido) tão bom quanto M1.

**4.4 P4 — o que o voto individual acrescenta à orientação:** responder com as diferenças M0→M1 (posição coletiva além da orientação registrada), M1→M2 (lealdade individual), M2→M4 (direção), em log-loss e em "desvios corretamente antecipados" (AUC-PR). Esta é a resposta principal de P4; não usar a acurácia agregada como manchete.

#### 5. Interpretação das dimensões intrapartidárias (P2, P3)

- Rotacionar como em `emb_votos` (SVD, sinal de dim1 orientado para governismo). Como a rotação é arbitrária em 2D, interpretar primeiro o **1D** e só depois a 2ª dimensão.
- **Cargas:** listar as 20 votações com maior |b_j| em cada sentido, com descrição, tipo de votação, proposição, tema e orientações (partido, Governo, Oposição); tabular a composição temática das top-50 vs. todas (razão de chances por tema, com IC por bootstrap de votações).
- **Validação convergente (correlatos externos, todos pré-especificados):** (i) distância à mediana do partido na dim1 global (ajuste fora do período, como em §3.1); (ii) taxa de alinhamento ao Governo; (iii) participação em frentes (FPA/agropecuária, evangélica, segurança pública, ambientalista; `frentes_deputados`), via correlação parcial dentro do partido; (iv) temas de autoria (`emb_temas`); (v) UF/região; (vi) suplência.
- **Validação preditiva (nova e forte):** ajustar o intra 1D só com votos **anteriores a 2026** e testar se a posição intrapartidária prevê (a) quem trocará de partido na janela de 2026 e (b) a **direção** da troca (sinal da diferença entre a mediana do partido de destino e a do de origem na dim1 global). Se o eixo intrapartidário for substantivo, os que estão na borda do partido em direção ao destino devem migrar. AUC com IC por bootstrap de deputados.
- E (Zucco; Krehbiel): dim1 intra ≈ governismo relativo dentro do partido (já r ≈ 0,76 com a distância global); dim2, se existir, temática (pauta de costumes/segurança vs. economia). ✗: cargas sem padrão temático ou procedimental reconhecível e nenhuma associação com troca futura (ruído).

#### 6. Dispersão, pivôs e dissidentes sistemáticos (P3)

- Dispersão por partido na dim1 global: DP e amplitude interquartil dos pontos **dos deputados com ≥ 100 votos** (pontos com poucos votos são encolhidos pelo prior e reduzem artificialmente a dispersão de bancadas com muitos suplentes); robustez com todos ponderando por nº de votos.
- **Pivôs — correção do v0:** o 308º e o 257º deputado têm de ser calculados entre os **513 em exercício** numa data, não entre os 644 que votaram na legislatura. Usar o painel de presença: calcular a mediana e o pivô de 3/5 em datas de referência (1º de cada semestre) e por período (2023, 2024, 2025, 2026 pré e pós-janela, usando os pontos por período deputado×partido). Reportar o partido e a identidade dos pivôs com probabilidade bootstrap.
- Dissidentes sistemáticos: deputados com maior |x_intra| (≥ 100 votos) *e* maior taxa de desvio ajustada (§3.1), com IC; listar só os que sobrevivem ao bootstrap (intervalo exclui o centro do partido).
- "Em que votações os partidos racham": votações com Rice < 0,5 em partidos com ≥ 10 votantes, top por partido, com tipo/tema; e contagem por tipo/tema (regressão logística de "racha" ao nível partido×votação com efeito fixo de partido).

#### 7. Incerteza (todas as perguntas)

- **Unidade de reamostragem: votação** (bloco natural de dependência: os votos de uma votação são correlacionados). Para estatísticas por deputado, também reamostragem de deputados quando a inferência é sobre a população de deputados.
- **Taxas, Rice, U:** bootstrap de votações, 1.000 réplicas (segundos).
- **IRT global (pivôs, dispersões, posições):** bootstrap não paramétrico de votações com reajuste; cada réplica alinhada ao ajuste completo por **rotação de Procrustes** (com reflexão) antes de calcular estatísticas. Réplicas: **100** (≈ 35 min a 20 s cada; com 4 CPUs e `multiprocessing` ≈ 10–12 min); `--rapido`: 20. Iniciar cada réplica com os parâmetros do ajuste completo (*warm start* só é possível sem alterar `ajustar_irt` se ele aceitar `th0` — não aceita; então aceitar o custo, ou notar que o RNG do módulo é global e fixar a semente via `ED.RNG = np.random.default_rng(s)` antes de cada réplica, para reprodutibilidade).
- **IRT intra:** bootstrap só para a validação preditiva de §5 e para as cargas principais, 20 réplicas (≈ 35 min, ou ~10 min em paralelo); se faltar tempo, apresentar estabilidade das cargas entre as 5 dobras da validação cruzada (já calculadas) como medida de incerteza.
- Regressões: EP agrupados em duas vias (deputado, votação).
- Comparações múltiplas por partido/tema: apresentar IC, não p-valores em série; onde houver testes, Holm dentro de cada família.

#### 8. P5 — Quando partido e Governo divergem, quem os deputados seguem

- **Amostra:** votos em que a orientação do partido (D-própria preferencialmente; bloco não heterogêneo como camada separada) e a do Governo são diretivas e opostas (direcional: Sim vs. Não/Obstrução). Excluir partidos de oposição permanente (PL, NOVO) da análise principal — para eles divergir do Governo é a regra e "seguir o Governo" é outra pergunta; tratá-los à parte.
- **Problema de seleção:** a divergência não é aleatória: o líder escolhe divergir onde espera que a bancada o siga (ou onde a bancada o força). Logo a taxa "segue o partido" nas divergências é uma cota superior da autoridade do líder e uma medida de quanto o líder *acompanha* a bancada. Estratégias:
  1. Comparação dentro da mesma votação e do mesmo partido: o desfecho é individual (segue partido / segue Governo / outro), com efeito fixo partido×votação; os correlatos individuais (suplente de titular-ministro, distância ideológica fora do período, UF, troca futura) dizem *quem* segue o Governo contra o líder. Isso é imune à seleção das votações quanto à comparação entre deputados.
  2. Linha de base contrafactual: para cada divergência, a probabilidade prevista de votar Sim pelo IRT global estimado **sem** as votações divergentes (para não usar o desfecho para medir a preferência). "Excesso de lealdade ao partido" = observado − previsto. Se o previsto já explica o voto, o líder apenas registra preferências (Krehbiel).
  3. Separar divergências em que o partido orienta "Liberado" (contraste: com liberação, quanto segue o Governo).
  4. Por tipo de votação (procedimental vs. mérito) e por fonte da orientação (própria vs. bloco).
- E (Figueiredo & Limongi; Carey "competing principals"; Zucco): nos partidos da base com ministérios, a maioria segue o partido, mas o Governo atrai uma fração relevante, maior entre suplentes de titulares-ministros e entre deputados à esquerda da mediana do partido; quando a orientação vem do bloco (não do partido), a atração do Governo é maior. ✗: seguir o partido não difere do previsto pelas preferências (excesso ≈ 0) — a orientação seria epifenomenal.

#### 9. Robustez prioritária (ordem de prioridade)

| Prioridade | Checagem | Afeta |
|---|---|---|
| R1 | **Camadas de fonte**: D-própria vs. D-bloco vs. D-inferida; U em paralelo (resolve C1) | P1, P3, P5 |
| R2 | **Excluir blocos heterogêneos** (megabloco 2025) da orientação; e versão "sem fev–out/2025" | P1 (série temporal), P5 |
| R3 | Sem `bloco (inferido)` (≈ 18% dos votos; funções já aceitam `sem_inferidas=True`) | P1, P4, P5 |
| R4 | Reportar cobertura por ano; série temporal em U | P1 |
| R5 | Estrita vs. direcional; abstenção no/fora do denominador | P1, P3 |
| R6 | Limiar de disputa 10% / 20% / ponderado (Carey) e m = 5/10 | Rice |
| R7 | `lam_g`, `lam_d` e células ≥ 5 na validação do IRT | P2, P4 |
| R8 | Ausência como desvio em PEC/PLP | P1 |
| R9 | Fusões vs. trocas individuais; só coorte da janela de 2026 | P3 |
| R10 | Plenário + comissões | P1 |

**Cortes se o tempo for curto (na ordem):** (1) bootstrap do IRT intrapartidário (substituir pela estabilidade entre dobras); (2) M4 2D e modelos por partido na validação (manter M0–M3); (3) R8 ausência e o painel de presença completo (usar presença só para pivôs por data; se nem isso, pivôs com o conjunto de deputados com votos em cada semestre, declarando a aproximação); (4) temas pela API (usar só `proposicoes_temas` e declarar cobertura de 29%); (5) R10 comissões; (6) logit misto. **Não cortar:** U ao lado de D, camadas de fonte, exclusão do megabloco, log-loss com M1 como linha de base, efeitos fixos partido×votação na regressão, EP em duas vias, trocas sem fusões.

**Orçamento de computação estimado (CPU, 4 núcleos):** descritivos + Rice + regressões ≈ 2–4 min; validação cruzada IRT ≈ 30 min; bootstrap global 100 ≈ 12–35 min; intra bootstrap 20 ≈ 10–35 min. Total ≈ 1–1,5 h completo; `--rapido` < 8 min.

**Tools:** Python (pandas, numpy, scipy, statsmodels, scikit-learn, matplotlib); `embeddings_deputados.ajustar_irt` importado, sem modificação; um único `analise.py` com `--secoes` e `--rapido`, semente fixa (`SEMENTE` e `ED.RNG` resemeado), cache de temas versionado.

### Validity Criteria

| Critério | Estratégia |
|---|---|
| Validade de construto (disciplina) | Separar D (liderança) de U (coesão) e de Rice; camadas por fonte; excluir blocos heterogêneos; direcional como principal; cobertura sempre reportada. |
| Validade de construto (dimensões intra) | Cargas interpretadas por tema/tipo; validação convergente com covariáveis externas; validação preditiva (troca futura e sua direção). |
| Validade interna (associações) | Efeitos fixos partido×votação; deputado FE no event study; preferência medida fora do período; EP em duas vias; leads reportados. |
| Validade estatística | Log-loss fora da amostra com linha de base M1 e M2; células ≥ 5; bootstrap de votações; Procrustes nos bootstraps; Holm onde houver famílias de testes. |
| Validade externa | Restrita à 57ª Legislatura, governo Lula 3, presidências Lira/Motta; votações nominais (Carrubba et al. 2006: a seleção de nominais é estratégica) — comparar composição de tipos com o total de votações (`votacoes` inclui simbólicas) e dizer quanto do universo é nominal. |
| Confiabilidade/reprodutibilidade | Um script, sementes, cache de API versionado, `resultados.json` válido (null), tabela de versões dos pacotes; todo número do texto vem de `R`. |
| Objetividade | Expectativas e falsificadores escritos antes da análise (este documento, com hash do commit). |

### Limitations (By Design)
- **Só votações nominais**: seleção estratégica das nominais (Carrubba et al.); mitigação: comparar tipos nominais × total; não generalizar para simbólicas.
- **Ausências**: só parcialmente observáveis via painel de presença (motivo desconhecido); mitigação: análise de ausência seletiva e sensibilidade em PEC/PLP.
- **Orientação registrada ≠ pressão do líder**: orientação é sinal público; negociação e sanções não são observadas. U mitiga a dependência do registro.
- **Orientações de bloco e inferidas**: atribuição mecânica; para o centrão a medida é de disciplina ao bloco. Mitigação: camadas, exclusão de heterogêneos, R3.
- **Retrato estático** do IRT: pontos por período deputado×partido apenas; mitigação: análises por ano em U; pivôs por data.
- **Pós-janela curto (ano eleitoral)**: baixo poder para trocas; reportar IC.
- **Covariáveis ausentes**: sem dados eleitorais (votação nominal, concentração municipal), cargos na liderança e emendas — não testar a tese do voto pessoal (Ames) diretamente; dizer isso.
- **Circularidade**: posições ideais estimadas com os mesmos votos que definem desvio — mitigada por estimação fora do período/fora das votações em análise.

### Ethical Considerations
- Dados públicos de agentes públicos no exercício do mandato; sem sujeitos humanos no sentido de protocolo (por instrução, sem plano IRB).
- Cuidado com rotular deputados nominalmente como "indisciplinados": nomear apenas com IC que excluam o centro do partido e descrever como comportamento de voto, não juízo de valor; lembrar que desvio pode refletir representação da base.
- Ano eleitoral (2026): evitar enquadramentos que funcionem como material de campanha; linguagem descritiva.

### Reporting Standard
- Nenhuma diretriz EQUATOR se aplica bem (não é estudo clínico/epidemiológico). **Recomendado:** princípios de transparência da APSA (DA-RT/JETS: acesso a dados, transparência de produção e analítica) e o *checklist* de reprodutibilidade do periódico-alvo; usar os itens de **STROBE** pertinentes (desenho, fontes, vieses, tamanho, variáveis, dados ausentes) como lista de verificação para as seções de dados e limitações; para a comparação preditiva de modelos, reportar no espírito de TRIPOD (partição, métricas, linha de base, calibração), sem citá-lo como diretriz formal.

### Preregistration
- Recomendado: **parcial / registro de plano de análise após exposição parcial aos dados** (os descritivos de P1 já foram vistos). Rotular P1 como descritivo, P2/P4/P5 e a validação preditiva de §5 como **confirmatórios no sentido de pré-especificados neste documento** (ainda não executados).
- Plataforma: OSF Registries, ou no mínimo commit datado deste blueprint no repositório.
- Status: Planned.
- Completed artifact declaration: not_provided.
- Companion handle: none.
- Sidecar ownership: dispatching layer only; do not populate a digest here.

### Mapa teórico (expectativas e falsificadores, resumo)

| Análise | Referência | Expectativa | Contrariaria |
|---|---|---|---|
| D e U por partido/ano | Figueiredo & Limongi (1999); Cheibub, Figueiredo & Limongi (2009) | ≈ 90% e estável; centro-direita menos disciplinada | U com queda/oscilação forte no tempo |
| Rice disputadas, Desposato | Desposato (2005); Snyder & Groseclose (2000); Carey (2007) | Ranking estável a m e limiar | Ranking que se inverte |
| Desvio individual | Carey (2009); Ames (2001); Krehbiel (1993) | Distância ideológica domina; suplência/UF importam marginalmente | Nada além da preferência (disciplina = preferência) |
| Troca de partido | Desposato (2006); Melo (2004) | Desvio pré-troca alto, cai após | Sem mudança; ou mesma mudança nas fusões |
| Ruído vs. estrutura | Clinton, Jackman & Rivers (2004); McCarty, Poole & Rosenthal (2001) | Ganho pequeno mas positivo de M3 sobre M2 em células disputadas | Ganho nulo (ruído) |
| Dimensões intra | Zucco (2009); Zucco & Lauderdale (2011) | dim1 intra = governismo relativo | Cargas sem padrão; não prevê troca |
| Partido × Governo | Carey (2009); Figueiredo & Limongi | Partido prevalece; Governo atrai suplentes/esquerda do partido | Excesso de lealdade ≈ 0 |

*As referências precisam ser verificadas (ano, título, periódico) na fase bibliográfica; nenhuma foi conferida nesta fase.*

---

## Crítica do v0 (síntese)

1. **Medida de disciplina**: correta na mecânica, mas a "orientação do partido" é majoritariamente de bloco para o centrão (C1) e inclui um megabloco PL+PT (C2); em 2025 a cobertura despenca (C3). Faltam U, camadas de fonte, cobertura e exclusão de blocos heterogêneos.
2. **Rice/Desposato**: implementação adequada (hipergeométrica exata); faltam m alternativo, linha de base aleatória e ponderação por disputa.
3. **Regressão**: unidade agregada sem efeito fixo de votação, suplência fixa, trocas com fusões, R² inválido, EP inadequados; antes/depois confundido com o tempo e com a queda de cobertura.
4. **Ruído vs. estrutura**: sem linha de base que isole x (M1) nem lealdade não espacial (M2); acurácia como métrica; inflação por células pequenas não tratada; premissa de b_j comum não testada; `ndim=0` não é suportado pelo estimador.
5. **Interpretação**: só cargas e uma correlação potencialmente circular; falta validação preditiva.
6. **Pivôs**: calculados sobre 644 deputados em vez dos 513 em exercício.
7. **Incerteza**: bootstrap sem alinhamento de rotação e sem sementes do RNG do módulo; 50 réplicas sem justificativa de tempo.
8. **Governo × partido**: sem tratamento da seleção e com oposição misturada à base.

## Design-Freeze Checkpoint Audit (single-model; cross-model não setado)

```
{
  decision: revise_before_freeze,
  drivers: [
    "A medida central de disciplina mistura orientação própria, de bloco e de um megabloco PL+PT com cobertura que despenca em 2025; precisa de camadas por fonte, exclusão de blocos heterogêneos e da medida de unidade (U), independente de orientação, antes de qualquer série temporal ou regressão.",
    "O teste ruído vs. estrutura do v0 não isola a contribuição da dimensão individual (falta linha de base só com efeitos fixos partido×votação com a mesma penalização, e um modelo de lealdade não espacial), usa acurácia em vez de log-loss e não controla células pequenas.",
    "A regressão do desvio e o antes/depois da troca estão confundidos (tempo, agenda, fusões, suplência fixa, EP inadequados); exigem desenho ao nível do voto com efeitos fixos partido×votação e deputado e erros agrupados em duas vias."
  ],
  confidence: high
}
```

A intenção do desenho (perguntas, dados, família de modelos) se mantém; nenhuma falha é fatal. Primary decision: revise_before_freeze. Cross-model decision: unavailable (flag não setada). Outcome: single-model only.
