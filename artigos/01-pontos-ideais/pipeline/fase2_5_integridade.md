# Academic Integrity Verification Report

Artigo 1, "Governo, oposição e os dois polos" (`artigo.md`, versão de 13/11/2026, commit `e7131ae`).
Papel: `integrity_verification_agent` (ARS, `academic-pipeline/agents/integrity_verification_agent.md`).
Data: 13/11/2026.

## Verification Mode

Initial Verification (Mode 1, Stage 2.5, pré-revisão).

**Fases aplicadas:** A (referências), B (contexto das citações), C (dados: C1 e C2), E (afirmações, com seleção de alto impacto feita à mão).

**Fases e partes não aplicadas, por dependerem de scripts, sidecars, flags ou modelos cruzados que não estão disponíveis nesta execução:**
- Phase D (originalidade, D1 e D2).
- A0 (lote na API do Semantic Scholar) e A0.5 (cache, #541).
- C3 (`figure_table_trace[]`, #261) e C4 (proveniência dos experimentos, #260): não há Figure Package nem passport. As legendas das tabelas foram conferidas por leitura direta, dentro de C2.
- E1 em formato `claim-registry/1.0`, E1.1 (`claim_registry_coverage.py`, #737), E3.1 (`evidence_rows.py`, #656), E4–E6 (#547, #548, #569), o aviso de economia de tokens (#570) e a verificação com outro modelo.

O registro de afirmações abaixo é uma tabela feita à mão e não um artefato validado pelo schema. Por isso, a cobertura semântica da extração é `not_machine_detectable` e o estado da cobertura é **`E1-COVERAGE-UNRESOLVED`**.

**Fontes de verdade usadas:**
- `resultados.json` e `tabelas/*.md|csv`, gerados por `analise.py`. Não reexecutei a análise.
- `tabelas/votacoes_cargas.csv`, para contagens derivadas dos votos de cada votação.
- `referencias.bib` e `pipeline/fase2_literatura.md`.
- `pipeline/fase1_blueprint_metodologico.md` (commit `7c95579`). Pelo `git log`, o arquivo não mudou depois desse commit.
- WebSearch, para os metadados e resumos das obras citadas. A busca vem dos EUA. scielo.br, doi.org, crossref, redalyc, ideas.repec.org e bibliotecadigital.tse.jus.br estavam bloqueados nesta sessão, então nenhum texto integral foi lido.

## Verdict

**FAIL**: 1 SERIOUS e 7 MEDIUM, além de 16 MINOR.

Os números estão, em quase tudo, exatos. Das cerca de 580 verificações numéricas, só uma diverge da fonte, e é relevante: "a mais de 1,2 unidade". O bloqueio vem de outras três coisas:
1. Uma citação de Hix e Noury (2016) na Discussão diz o contrário do que a obra conclui.
2. Três conclusões se afastam das regras de decisão fixadas no Blueprint, sem que o texto declare o desvio: a resposta à RQ1, o rótulo "misto" de H1b e a assinatura de E1(b).
3. Duas generalizações sobre a segunda dimensão vão além dos dados: a "coalizão ampla contra os dois polos" e o "desaparece nas comissões". Um dos exemplos citados para a dim2, a PEC 3/2021, também está descrito de forma errada.

## Verification Summary

| Category | Total | Passed | Issues |
|----------|-------|--------|--------|
| Reference Existence (A1) | 24 | 24 | 0 |
| Bibliographic Accuracy (A2) | 24 | 21 | 3 MINOR: Zucco 2009 e Clinton et al. 2004 sem DOI; prenome de Argelina Figueiredo inconsistente |
| Ghost Citations (A3) | 24 citadas / 24 listadas | -- | 0 órfãs / 0 pendentes |
| Citation Context Accuracy (B1) | 24 de 24 (100%; obras do Brasil e Hix e Noury lidas pelo resumo ou pela fonte secundária) | 22 | 1 SERIOUS (Hix e Noury no §7), 1 MINOR (Zucco e Power 2024) |
| Statistical Data Accuracy (C1/C2) | ≈150 valores no texto (resumo, abstract e corpo) + ≈430 células nas Tabelas 1–9 | todos menos 1 | 1 MEDIUM ("mais de 1,2"), 5 MINOR (rótulos e fonte) |
| Internal Consistency (C2) | -- | Fail | 3 (transparência entre resumo, nota e Blueprint; 0,998 contra 0,999; 77/60 contra 78/59) |
| Originality Check (D1) | não aplicado | -- | -- |
| Self-Plagiarism (D2) | não aplicado | -- | -- |
| Claim Verification (E) | 22 de 22 registradas (Mode 1: HIGH-IMPACT 22, RANDOM 0, TOP-UP 0, NOT-SELECTED 0; cobertura da extração semântica `not_machine_detectable`; lacunas candidatas: não medidas, E1.1 não executado) | 14 | 1 MAJOR_DISTORTION, 5 com desvio em relação ao Blueprint ou generalização (MEDIUM), 2 MINOR_DISTORTION |

## Phase C: Data Verification (resumo)

**Conferidos e corretos.** Os itens abaixo batem com a fonte, inclusive no arredondamento:
- Resumo e abstract: 644, 433.476, 1.470, 91,9%, 84,3%, 88,5%, 83%, 60%, 9 pontos de R², 3,4 pp.
- §3: 43.631, 1.604 (3,7%), 1.128, 473.323, 1.039/431/276, 35,5%, 56,7%, 66,7%/6,4%/26,8%, 1.072.
- §4: 171, 831, 707, 621, 664, o fator de escala 1,09 (1,06–1,11) e 31.229.
- §5.1: 74,8%→91,0%, APRE de 64%, +0,90 pp [0,72; 1,09], log-loss 0,241→0,209, +0,41 pp [0,30; 0,51], 46%, +0,28, APRE dentro da amostra 0,650/0,693/0,717/0,737, SVD 38,5/9,1/1,9%.
- §5.2: 74%, autovalores 0,81/0,29, todas as médias partidárias, ângulos de 26° [21; 31] e 36° [29; 39], +33 e +9 pontos de R², r de 0,91 e −0,24 nas metades, e a Tabela 5.
- §5.3: 200 de 200 réplicas, 4,2°/1,0°/2,7°, confiabilidade 0,92/0,99, 0,96, razão 2,8, mínimo 0,97, as diferenças com IC, R² 0,29, −0,01 [−0,11; 0,16], 0,90 [0,73; 1,08], 372 (25%), a Tabela 6, 8,5%, 42% e 43%, 213 proposições, 22%. Na PEC 9/2023 em 2º turno: PSOL 0, NOVO 0, PT 95,0%, centrão 88,7%.
- §5.4: 0,997/0,984, autovalores 0,14/0,83/0,31, 12%, 47/77/60% (do modelo 3D), as faixas de médias, dp de 0,41.
- §5.5: 78%/59%, 3,4 [2,9; 3,9], 3,9 [3,4; 4,3], 7,6 [6,7; 8,6], a Tabela 7, 90,2%, 28.256, 55,0/50,3/17,1, 14,3 e 7,3 pp e os limites de 2 e 0,5 pp.
- §6: EP de 0,09/0,12 (p90 0,16/0,22), dp de 0,90/0,54, 65 de 621, 19% e 46%, a Tabela 8 inteira, a Tabela 9, 107, 0,95, 0,72, 0,29, 92,6 contra 93,9, as faixas anuais (0,97–0,98; 0,84–0,92; 0,2–1,5 pp), a orientação em 87%/79% e a SVD (91,0/89,4/91,9; r de 0,97/0,75).

**Discrepâncias:**

| Local | Texto | Fonte | Chave/arquivo |
|---|---|---|---|
| Resumo, abstract, §5.2 §3 | "a mais de 1,2 unidade do PL" (vale para os três) | União − PL = **1,199** (< 1,2); PP − PL = 1,266; Republicanos − PL = 1,295 | `bootstrap.dif_UNIÃO_PL_dim1.dif` |
| §6 "Plenário × comissões" | correlações "de 0,999 e 0,998" | a Tabela 9, cuja nota diz "após Procrustes", traz 0,999/0,999; 0,998 é o valor em eixos próprios | `orgaos.tabela[0]["r dim2 (eixos próprios)"]` = 0,99796; `"r dim2 (Procrustes)"` = 0,99882 |
| §6 "Incerteza individual" | EP "cerca do dobro para os deputados com menos votos" | dim1: 0,168 contra 0,086 (1,96×); dim2: 0,168 contra 0,119 (**1,41×**) | `bootstrap.ep_mediano_dim*_nao_conf` |
| §3 §4 e Limitação 4 | "18,0% dos registros de voto" | a proporção é sobre os **433.476 votos analisados** e não sobre os 473.323 registros brutos | `dados.orientacao_fonte["bloco (inferido)"]`, calculada sobre `P.v` (analise.py, `etapa_dados`) |
| §5.4 e §5.5 | partido explica "77%… e 60%" (§5.4) e "78% e 59%" (§5.5) | os dois estão certos, mas o §5.4 usa o modelo 3D e o §5.5 o 2D, sem dizer isso | `dim3.eta2_partido_d*` e `estrutura.eta2_partido_d*` |
| Limitação 7 | "Missão (1)" período | nenhuma saída de `analise.py` traz o número de períodos do Missão | não rastreável em `resultados.json`/`tabelas` |

## Phase E: Claim Verification Results

Coverage: `E1-COVERAGE-UNRESOLVED`. O registro foi feito à mão e E1.1 não foi executado. Cobertura semântica: `not_machine_detectable`.

| ID | Afirmação (local) | Fonte ou critério | Veredito |
|---|---|---|---|
| C01 | 2D acerta 91,9%, contra 84,3% e 88,5% (resumo e abstract) | `cv` | VERIFIED |
| C02 | H2, necessidade sustentada (§5.1) | Blueprint H2a: 0,90 pp ≥ 0,3; mínimo > 0; IC exclui 0; log-loss menor | VERIFIED |
| C03 | H2, suficiência não sustentada (§5.1) | H2b: 0,41 pp ≥ 0,3 e 46% ≥ 1/3 | VERIFIED |
| C04 | "A resposta à RQ1 é que o espaço tem duas dimensões principais" (§5.1, resumo, §9) | o Blueprint (H2b) diz: "Caso contrário, a resposta à RQ1 passa a ser 3D" | Desvio não declarado → **MEDIUM** (IL-MEDIUM-3) |
| C05 | "PP, Republicanos e União… a mais de 1,2 unidade do PL" (resumo, abstract, §5.2) | União − PL = 1,199 | **MEDIUM** (IL-MEDIUM-1) |
| C06 | H1a sustentada (Tabela 4) | IC > 0 para os três; fração 0,42 ≥ 0,33 | VERIFIED |
| C07 | H1b "misto" (Tabela 4, §5.2) | O Blueprint só define "Sustentada"; uma das três condições falha (+0,092 > 0,05). Não existe categoria "misto" para H1b nem critério de refutação | Rótulo fora do Blueprint → **MEDIUM** (IL-MEDIUM-2) |
| C08 | H1c e H1d sustentadas | 0,908 ≥ 0,80 e \|−0,235\| ≤ 0,30; 0,999 ≥ 0,95 | VERIFIED |
| C09 | "o primeiro eixo é predominantemente governo × oposição, com um componente ideológico residual" (§5.2) | A formulação atenuada é adequada aos R² parciais, mas depende de C07 | VERIFIED com ressalva (ver IL-MEDIUM-2) |
| C10 | H3 sustentada (§5.3) | 2,7° ≤ 15°; 0,92 ≥ 0,70; 0,96 ≥ 0,90; min r(t10) 0,974 ≥ 0,90; 200 de 200 | VERIFIED |
| C11 | "Não é uma ferradura" (§5.3) | E1(a): a CV do 1D quadrático contra o 2D difere em 0,90 pp, acima do limite de 0,1. Mas a assinatura descritiva do Blueprint (R² ≥ 0,25, coef. > 0) **é satisfeita** (0,286), e o texto a chama de "parcial" | VERIFIED; MINOR_DISTORTION na palavra "parcial" (IL-MINOR-8) |
| C12 | dim2 dominante: "são votações vencidas por uma coalizão ampla contra os dois polos" (§5.3); "opõe os dois polos… ao núcleo" (resumo, abstract, §9) | Tabela 6: \|PSOL − NOVO\| = **51,4 pp** nas votações de dim2 dominante. O Blueprint, em E1(b), exige que esse valor seja pequeno, e o texto não discute o número. Pelo `votacoes_cargas.csv` (343 votações de dim2 dominante com dados para os 4 grupos): os dois polos ficam juntos contra o centrão em **36,7%**, só o PSOL em 21,6% e só o NOVO em 28,9%. Nas votações de dim1 dominante a proporção é 0,7%. | Generalização além dos dados → **MEDIUM** (IL-MEDIUM-4) |
| C13 | Exemplos de matérias "em que o núcleo… (PT e centrão…) se une contra os dois partidos", entre eles a PEC 3/2021 (§5.3) | Na PEC 3/2021, nas 11 votações de dim2 dominante, o PT vota **com** PSOL e NOVO: 11,7–19,0% de "Sim" ao lado da PEC, contra centrão 79–92% e PL 94–100%, ou 86–100% do lado oposto. O núcleo, ali, é centrão + PL. | MAJOR para o exemplo → **MEDIUM** (IL-MEDIUM-5) |
| C14 | dim2 "desaparece nas comissões"; "fenômeno de plenário" (abstract, resumo, §6) | t9: r = 0,29 (n = 107) e 2D < 1D numa única partição de teste de 10% (≈1.557 votos, sem IC). Mas t9a (CV do modelo conjunto por órgão): CCJC 2D 0,924 > 1D 0,921 e demais comissões 0,925 = 0,925, sem relato no texto | Generalização além dos dados → **MEDIUM** (IL-MEDIUM-6) |
| C15 | 3ª dimensão "sobretudo intrapartidária"; "pouca estrutura partidária" (resumo, abstract, §5.1, §9) | η² = 0,47: 53% dentro dos partidos, mas 47% partidário não é "pouca" | MINOR_DISTORTION (IL-MINOR-1) |
| C16 | RQ4: +3,4 pp [2,9; 3,9]; 7,6 é limite superior (§5.5) | `cv.ic_*`; a ressalva da interpolação está presente | VERIFIED |
| C17 | "mais de 45% dos votos contra a bancada continuam imprevisíveis" | 1 − 0,5498 = 45,0% | VERIFIED (no limite) |
| C18 | Discussão: os resultados "sustentam a tese… de que o voto nominal num presidencialismo de coalizão se organiza primeiro pela relação com o Executivo (Zucco, 2009; Hix; Noury, 2016)" | Hix e Noury concluem que o padrão governo × oposição domina na maioria dos legislativos, **exceto** em presidencialismos com governos de coalizão e em parlamentarismos com governo minoritário, onde aparecem coalizões esquerda–direita caso a caso. O próprio §2.2 do artigo diz isso. | **MAJOR_DISTORTION → SERIOUS** (IL-SERIOUS-1) |
| C19 | Scheeffer (2018): a ideologia prevalece, exceto nas matérias com recursos financeiros (§2.2, §7) | Resumo: "A exceção são os casos em que estão em jogo recursos financeiros…" | VERIFIED |
| C20 | Leoni (2002), ordenação esquerda–direita, PT e PFL nos extremos; Izumi (2016), uma dimensão governo × oposição no Senado | Resumos (DOAJ/OASIS; FAPESP/NECI-USP) | VERIFIED |
| C21 | Testa et al. (2024): os especialistas incluem o PL no centrão | Cobertura do próprio estudo (Congresso em Foco): PP, Republicanos, PL, PTB, Patriota, MDB, União, Podemos e PSD, com corte de 5% | VERIFIED (por fonte secundária) |
| C22 | Nota de transparência e resumo: critérios "redigidos antes da leitura dos resultados completos" | O resumo e o abstract dizem "antes"; a nota diz que o autor "já conhecia… uma primeira execução completa do script"; o Blueprint fala só em "tabelas parciais de uma execução abortada" (commit `e53f967`, que contém só `t1`) e na acurácia de 91,94% | Inconsistência → **MEDIUM** (IL-MEDIUM-7) |

| Verdict | Claim Count | Proportion |
|---------|------------|-----------|
| VERIFIED | 14 | 64% |
| MINOR_DISTORTION | 2 | 9% |
| MAJOR_DISTORTION | 1 | 5% |
| UNVERIFIABLE | 0 | 0% |
| UNVERIFIABLE_ACCESS | 0 (as fontes externas foram lidas pelo resumo ou por fonte secundária, sem texto integral; ver o aviso) | — |
| Desvio do Blueprint ou generalização (classificado como MEDIUM) | 5 | 23% |

## Issue List (Sorted by Severity)

### SERIOUS (Must Fix)

| ID | # | Category | Location | Issue Description | Correct Information | Source |
|----|---|----------|----------|------------------|--------------------|----|
| IL-SERIOUS-1 | 1 | Citation context (B1/E) | §7, 2º parágrafo: "Os resultados sustentam a tese, consolidada na literatura brasileira e comparada, de que o voto nominal num presidencialismo de coalizão se organiza primeiro pela relação com o Executivo (Zucco, 2009; Hix; Noury, 2016)." | Hix e Noury concluem o contrário para os presidencialismos com governos de coalizão: neles aparecem coalizões esquerda–direita caso a caso. O §2.2 do próprio artigo resume a obra corretamente, e o §7 contradiz o §2.2. | Reescrever: "Os resultados convergem com Zucco (2009) e com o padrão que Hix e Noury (2016) encontram na maioria dos legislativos, mas **contrariam** a expectativa desses autores para presidencialismos com governo de coalizão, em que previam coalizões caso a caso ao longo de uma dimensão de políticas." Retirar "consolidada… e comparada". | Hix e Noury, PSRM 4(2):249–273, 2016, resumo (Cambridge Core; RePEc `cup:pscirm:v:4:y:2016:i:02:p:249-273_00`) |

### MEDIUM (Must Fix)

| ID | # | Category | Location | Issue Description | Correct Information | Source |
|----|---|----------|----------|------------------|--------------------|----|
| IL-MEDIUM-1 | 1 | Data (C2) | Resumo ("a mais de 1,2 unidade do PL"), abstract ("more than 1.2 units away from PL"), §5.2 §3 ("ficam a mais de 1,2 unidade do PL") | União − PL = 1,199, abaixo de 1,2 | "a 1,2 unidade ou mais do PL (1,20 a 1,30)" / "1.2 to 1.3 units away from PL" | `bootstrap.dif_UNIÃO_PL_dim1` |
| IL-MEDIUM-2 | 2 | Claim vs Blueprint (E) | Tabela 4 (linha H1b, "misto"); §5.2 ("H1b é misto (um dos três critérios falha)") | O Blueprint só define a condição "Sustentada" para H1b. "Misto" só existe para H1a, e H1b não tem critério de refutação. Pelo critério fixado, H1b **não é sustentada**. Tratá-la como "não refutada" na regra agregada é uma decisão de interpretação que o texto não declara. | Na Tabela 4: "não sustentada (critério 2 falha: +0,09 > 0,05)". No §5.2: "Pelo critério fixado, H1b não se sustenta. Como o desenho não definiu limiar de refutação para H1b, aplicamos a regra agregada tratando-a como não refutada e, por isso, adotamos a formulação atenuada…". Registrar o ponto numa seção de desvios. | Blueprint, H1b e "Regra agregada para H1" |
| IL-MEDIUM-3 | 3 | Claim vs Blueprint (E) | §5.1, último parágrafo ("A resposta à RQ1, portanto, é que o espaço de votação tem duas dimensões principais"); resumo e abstract (estrutura 2D); §9, 1º parágrafo | A regra fixada em H2b diz: se 2D não for suficiente, "a resposta à RQ1 passa a ser 3D, e a dim3 entra como exploratória". O texto mantém "duas dimensões principais" e o modelo 2D sem declarar o desvio. | "Pelo critério fixado, a resposta à RQ1 é três dimensões. Mantemos o modelo 2D como especificação de trabalho porque [razões: autovalor 0,14, η² etc.]; trata-se de um desvio do desenho." Reproduzir isso no resumo, no abstract e no §9, e criar a seção "Desvios em relação ao desenho" que o Blueprint pede. | Blueprint, H2b; `cv.ganho_2D_3D` |
| IL-MEDIUM-4 | 4 | Claim overgeneralization (E) | §5.3, "O padrão é claro…" ("são votações vencidas por uma coalizão ampla contra os dois polos"); resposta à RQ3; resumo, abstract e §9 | A Tabela 6 mostra \|PSOL − NOVO\| = 51,4 pp nas votações de dim2 dominante, e o texto não discute esse valor. A assinatura E1(b) do Blueprint (\|PSOL − NOVO\| pequeno) não é satisfeita. Só em 36,7% dessas votações os dois polos votam juntos contra o centrão; nas demais, só um dos polos se separa (21,6% PSOL, 28,9% NOVO). O padrão é muito mais frequente que nas votações de dim1 (0,7%), mas não é a regra. | Relatar o 51,4 e o resultado da assinatura E1(b). Reformular: "a dim2 capta votações em que um ou ambos os polos programáticos se separam de seus vizinhos de campo contra um núcleo PT + centrão; em cerca de um terço delas (37%), os dois polos votam juntos contra esse núcleo." Ajustar o resumo e o abstract ("opõe os polos, separada ou conjuntamente, ao núcleo…"). | `tabelas/t8a_perfil_dim2`; contagem derivada de `tabelas/votacoes_cargas.csv` (`dim2_dominante`, maioria > 50% de "Sim" por grupo; n = 343) |
| IL-MEDIUM-5 | 5 | Data/claim (C2/E) | §5.3, parágrafo "As matérias com as maiores cargas…" (a PEC 3/2021 listada entre as matérias em que "o núcleo de governabilidade (PT e centrão…) se une contra os dois partidos") | Na PEC 3/2021 (prerrogativas), o PT vota com PSOL e NOVO contra centrão + PL: PT com 11,7–19,0% de "Sim" ao lado da PEC, centrão 79–92% e PL 94–100%. O exemplo contradiz a frase. | Tirar a PEC 3/2021 da lista de exemplos ou descrevê-la como caso em que o "núcleo" é centrão + PL e o PT fica do lado dos polos. Acrescentar que a composição do núcleo varia de matéria para matéria (nas fiscais, o PL fica em parte com os polos). | `tabelas/votacoes_cargas.csv`, `proposição` = PEC 3/2021 e `dim2_dominante` |
| IL-MEDIUM-6 | 6 | Claim overgeneralization (E) | Abstract ("it vanishes in committee votes"); resumo ("desaparece nas comissões"); §6, "Plenário × comissões" ("O conflito 'polos × núcleo' é um fenômeno de plenário"); §7 e §9 | A evidência é r = 0,29 entre 107 deputados e 2D < 1D numa partição única de 10% (cerca de 1.557 votos, sem IC). A Tabela t9a, que não aparece no texto, mostra no modelo conjunto a CCJC com 2D 0,924 > 1D 0,921 e as demais comissões empatadas. A explicação causal ("onde se votam as PECs…") não é testada. | "não se reproduz nas comissões, onde o modelo estimado só com essas votações não ganha com a 2ª dimensão (amostra pequena; partição única)". Relatar a t9a. Marcar a explicação como conjectura. | `orgaos.tabela`, `orgaos.r_dim2`; `tabelas/t9a_cv_por_orgao`; analise.py, `_orgao_tarefa` (`rng(7) < 0.10`) |
| IL-MEDIUM-7 | 7 | Internal consistency (C2) / transparência | Resumo e abstract ("critérios… fixados num documento de desenho redigido antes da leitura dos resultados completos"); §1, Nota de transparência ("já conhecia… uma primeira execução completa do script"); §8, item 10; §9 ("pelo critério que fixamos antes de ver os resultados finais") | As três versões não batem entre si. O Blueprint registra só a acurácia de 91,94%, os rótulos, o modelo e "tabelas parciais de uma execução abortada" (`e53f967`, que contém só `t1`). Também diz que as hipóteses foram fixadas por um revisor cego aos valores, e não pelo autor. O Blueprint recomenda ainda citar o *hash*, o que o texto não faz. | Harmonizar: "Os critérios foram fixados por um revisor metodológico que não consultou os valores (documento versionado no commit `7c95579`). O autor da análise conhecia resultados preliminares (acurácia 2D de 91,9%, ordem dos partidos na dim1) [e, se for o caso, a execução completa]." Usar a mesma formulação no resumo, no abstract, no §8 e no §9. Se a execução completa tiver sido vista pelo autor antes do commit, dizer isso no resumo. | `pipeline/fase1_blueprint_metodologico.md` (linhas 5, 86, 235–237); `git log` |

### MINOR (Recommended Fix at Stage 2.5; Must Fix at Stage 4.5)

| ID | # | Category | Location | Issue Description | Suggestion |
|----|---|----------|----------|------------------|----|
| IL-MINOR-1 | 1 | Claim (E) | Resumo e abstract ("sobretudo intrapartidária"/"mostly intra-party"); §5.1 e §5.4 ("pouca estrutura partidária"); §9 | η² do partido na dim3 = 0,47: 53% da variância fica dentro dos partidos. "Pouca" exagera. | "menos estruturada por partido que as duas primeiras (o partido explica 47% da sua variância, contra 77% e 60%)" |
| IL-MINOR-2 | 2 | Data (C2) | §6, "Incerteza individual" | "cerca do dobro" vale para a dim1 (1,96×), mas não para a dim2 (1,41×) | "cerca do dobro na dimensão 1 e 40% maior na dimensão 2" |
| IL-MINOR-3 | 3 | Data (C2) | §6, "Plenário × comissões", 1ª frase | 0,998 está em eixos próprios; a Tabela 9 (Procrustes) traz 0,999 | Usar 0,999 e 0,999 ou declarar a métrica |
| IL-MINOR-4 | 4 | Data (C2) | §5.4 contra §5.5 | η² de 77/60 no modelo 3D contra 78/59 no 2D, sem indicação do modelo | Acrescentar "no modelo 3D" no §5.4 |
| IL-MINOR-5 | 5 | Data (C2) | §3, 4º parágrafo; Limitação 4 | "18,0% dos registros de voto" é uma proporção dos 433.476 votos analisados | "18,0% dos votos analisados" |
| IL-MINOR-6 | 6 | Data traceability (C1) | Limitação 7 ("Missão (1)") | nenhuma saída de `analise.py` traz esse número | Gerar o número no script (`t5` com todos os partidos) ou retirá-lo |
| IL-MINOR-7 | 7 | Blueprint fidelity | §4.5 (H1a, H1c) | H1a acrescenta a União ao critério (é mais estrito, e tudo passa); H1c omite a condição \|r dim2\| ≤ 0,30, que passa com −0,24 | Reproduzir os critérios exatamente e registrar o acréscimo da União como desvio |
| IL-MINOR-8 | 8 | Blueprint fidelity (E) | §5.3, "Não é uma ferradura" ("assinatura parcial") | Pelo Blueprint, a assinatura descritiva de (a) é satisfeita (R² 0,286 ≥ 0,25, coef. > 0), mas o teste preditivo decisivo a rejeita | "A assinatura descritiva prevista no desenho está presente (R² 0,29 ≥ 0,25), mas o teste preditivo decisivo a rejeita" |
| IL-MINOR-9 | 9 | Reporting completeness | §4.5 e §5 | H2c (ganho > 0 em todas as especificações, anos e no plenário) e H2d (2D > maioria do partido, IC exclui 0) foram fixadas, mas não aparecem como hipóteses. As duas se sustentam. Não há seção "Desvios", nem o *hash* do Blueprint. | Relatar H2c e H2d, criar o apêndice "Desvios" e citar o commit `7c95579` |
| IL-MINOR-10 | 10 | Claim (E) | §7, 3º parágrafo ("menor dependência de recursos de governo") | Afirmação empírica sobre PSOL e NOVO sem dado nem citação | Citar uma fonte ou retirar |
| IL-MINOR-11 | 11 | Claim (E) | §7, 4º parágrafo ("e não por moderação ideológica") | Atribuição causal não testada | "o que é compatível com governismo, e não necessariamente com moderação ideológica" |
| IL-MINOR-12 | 12 | Claim (E) | §6, "Método alternativo" ("As conclusões substantivas não dependem da forma logística do modelo") | Com r = 0,75 na dim2, a frase vale bem para a dim1 e só razoavelmente para a dim2 | "As conclusões sobre a dimensão 1 não dependem…; a dimensão 2 é recuperada de forma aproximada" |
| IL-MINOR-13 | 13 | Wording | §5.2, final ("o de esquerda tende a ficar mais à direita do eixo (no sentido positivo)") | "À direita" confunde a posição no gráfico com o campo ideológico. O sinal condicional não foi verificado: `resultados.json` não guarda os coeficientes da regressão conjunta. | "o de esquerda tende a ter valor maior (mais governista) na dimensão 1"; gravar os coeficientes no JSON |
| IL-MINOR-14 | 14 | Bibliographic (A2) | Referências: Zucco 2009 e Clinton, Jackman e Rivers 2004 | Faltam os DOIs, embora as demais entradas os tragam | Acrescentar o DOI depois de conferir no Cambridge Core (de memória, não confirmado nesta sessão: 10.1017/S0022381609090896 e 10.1017/S0003055404001194) |
| IL-MINOR-15 | 15 | Format (B2) | Referências: Figueiredo e Limongi 1999 ("Argelina Cheibub") contra 1998, 2005 e 2009 ("Argelina") | Nome da autora inconsistente | Uniformizar |
| IL-MINOR-16 | 16 | Citation context (B1) | §2.2, último parágrafo (Zucco; Power, 2024: "a maior distância ideológica já registrada entre o presidente e o Congresso") | O resumo diz que os presidentes "se afastaram do Congresso" e fala em estresse inédito no início de Lula 3. O superlativo literal não foi confirmado no texto integral. | Conferir no texto integral (acesso aberto) ou atenuar para "distância ideológica inédita" |

## Phase A/B: Audit Trail das referências

Todas as 24 referências estão citadas no texto e todas as citações têm entrada na lista: 0 órfãs e 0 pendentes. As notas de A2 e B1 de cada referência estão na tabela.

| Referência | Consulta (WebSearch) | Melhor resultado | A1 | A2 | B1 (uso no texto) |
|---|---|---|---|---|---|
| Assis & Silva 2026 | "Informal Coalitions in Action" BPSR 2026 | brazilianpoliticalsciencereview.org (artigo e XML), v. 20 n. 1 e0001, DOI 10.1590/1981-3821202600010001, 05/01/2026 | VERIFIED | ok | Ok: 2.030 votações (1995–2016); coalizões formais e informais moldam os resultados |
| Bafumi et al. 2005 | título + PA 13 | Cambridge Core / RePEc `polals:v:13:y:2005:i:02:p:171-187`, DOI 10.1093/pan/mpi010 | VERIFIED | ok | Ok (identificação e invariâncias) |
| Bolognesi, Ribeiro, Codato 2023 | título + Dados 2023 | SciELO PDF ("DADOS, Rio de Janeiro, vol.66 (2): e20210164, 2023"), DOI 10.1590/dados.2023.66.2.303 | VERIFIED | ok | Ok (survey de especialistas, 2018) |
| Bolognesi et al. 2025 | título + Opinião Pública 2025 | Revista CESOP/Unicamp, v. 31, e31120, DOI 10.1590/1807-0191202531120 | VERIFIED | ok | Ok (desaparecimento do centro, 2018 contra 2022) |
| Bonfim, Luz, Vasquez 2023 | título + BPSR 17 | BPSR / SciELO v17n2, DOI 10.1590/1981-3821202300020001 | VERIFIED | ok | Ok (EC 86/2015 reduziu a dominância do Executivo) |
| Cheibub, Figueiredo, Limongi 2009 | título + Dados 52 | DOAJ (jun. 2009), v. 52 n. 2 p. 263–299, DOI 10.1590/s0011-52582009000200001; versão LAPS em inglês | VERIFIED | ok | Ok: os partidos, e não os governadores, explicam o voto (por citação de Arretche no mesmo volume) |
| Clinton, Jackman, Rivers 2004 | título + APSR 98 | Cambridge Core / RePEc `apsrev:v:98:y:2004:i:02:p:355-370` | VERIFIED | MINOR (sem DOI) | Ok |
| Figueiredo & Limongi 1999 | título + Editora FGV | programa de curso da FFLCH-USP; core.ac.uk | VERIFIED | MINOR (nome) | Ok |
| Hix & Noury 2016 | título + PSRM | Cambridge Core; RePEc `pscirm:v:4:y:2016:i:02:p:249-273`; LSE Research Online | VERIFIED (DOI conforme o padrão Cambridge; o resolvedor estava bloqueado) | ok | §2.2 ok; **§7 MAJOR_DISTORTION** (IL-SERIOUS-1) |
| Imai, Lo, Olmsted 2016 | título + APSR 110 | RePEc `apsrev:v:110:y:2016:i:04:p:631-656`; Cambridge; DOI 10.1017/S000305541600037X | VERIFIED | ok | Ok (algoritmos EM) |
| Izumi 2016 | título + Dados 2016 | FAPESP BV; NECI-USP; v. 59 n. 1 p. 91–138 | VERIFIED | ok (DOI 10.1590/00115258201672 aceito pela matriz da Fase 2, que o tirou da 1ª página do PDF; doi.org estava bloqueado) | Ok: "uma única dimensão… governo e oposição é suficiente" |
| Jackman 2001 | título + PA 9 | Cambridge PDF; RePEc `polals:v:9:y:2001:i:03:p:227-241`; DOI 10.1093/polana/9.3.227 | VERIFIED | ok | Ok |
| Koren, Bell, Volinsky 2009 | título + Computer 42 | BibSonomy / bibbase: v. 42 n. 8 p. 30–37, DOI 10.1109/MC.2009.263 | VERIFIED | ok | Ok |
| Leoni 2002 | título + Dados 2002 | DOAJ / OASIS-IBICT: v. 45 n. 3 p. 361–386 | VERIFIED | ok | Ok: um contínuo esquerda–direita, PT e PFL nos extremos, dimensões extras acrescentam pouco |
| Limongi & Figueiredo 1998 | título + Lua Nova 44 | DOAJ; SciELO; n. 44 p. 81–106; DOI 10.1590/S0102-64451998000200005 | VERIFIED | ok | Ok |
| Limongi & Figueiredo 2005 | título + Dados 48 | DOAJ (dez. 2005); dados.iesp.uerj.br; v. 48 n. 4 p. 737–776 | VERIFIED | ok | Ok (contesta as emendas como moeda de troca) |
| Pereira & Mueller 2002 | título + Dados 45 | redalyc / typeset; v. 45 n. 2 p. 265–301 | VERIFIED | ok | Ok |
| Poole & Rosenthal 1985 | título + AJPS 29 | Caltech authors; JSTOR (maio 1985) p. 357–384 | VERIFIED | ok | Ok |
| Poole & Rosenthal 1997 | título + Oxford | catálogo UP (Oxford University Press, New York, 1997) | VERIFIED | ok | Ok |
| Scheeffer 2018 | título + Teoria & Pesquisa; DOI | teoriaepesquisa.ufscar.br; TSE BDTSE; v. 27 n. 2 p. 167–188; DOI 10.31068/tp.27208 | VERIFIED | ok | Ok: "a ideologia prevalece… A exceção são os casos em que estão em jogo recursos financeiros" |
| Testa, Mesquita, Bolognesi 2024 | título + Caderno CRH | SciELO ccrh; OASIS-UFBA; v. 37, e024003, DOI 10.9771/ccrh.v37i0.55537 | VERIFIED | ok | Ok: centrão unido por demandas clientelistas; a inclusão do PL vem da cobertura do estudo pelos autores (Congresso em Foco) |
| Zucco 2009 | título + JOP 71 | Pollux-FID: JOP 71(3):1076–1092 | VERIFIED | MINOR (sem DOI) | Ok: os votos divergem da ideologia na direção do presidente, via *pork* e cargos |
| Zucco & Lauderdale 2011 | título + LSQ | LSE Research Online (título exato); poliscidata (DOI 10.1111/j.1939-9162.2011.00019.x) | VERIFIED | ok | Ok |
| Zucco & Power 2024 | título + LAPS 66 | Cambridge (acesso aberto, CC BY), DOI 10.1017/lap.2023.24, 24/01/2024 | VERIFIED | ok | MINOR (superlativo; IL-MINOR-16) |

Nenhum padrão de citação alucinada foi detectado: nenhuma obra inexistente, nenhuma mistura de duas obras e nenhum DOI apontando para outra obra.

## AI Research Failure Mode Checklist

| Mode | Outcome | Evidence | Blocks? |
|------|---------|----------|---------|
| Afirmações acima do suporte dos dados | SUSPECTED | IL-MEDIUM-4, IL-MEDIUM-6 | sim (via MEDIUM) |
| Descumprimento silencioso de regra de decisão pré-fixada | SUSPECTED | IL-MEDIUM-2, IL-MEDIUM-3 | sim (via MEDIUM) |
| Citação que inverte o achado da fonte | SUSPECTED | IL-SERIOUS-1 | sim |
| Números fabricados ou não rastreáveis | CLEAR, com 1 exceção MINOR | todos os números rastreados até `resultados.json`/`tabelas`, exceto "Missão (1)" | não |
| Referências fabricadas | CLEAR | 24 de 24 verificadas | não |
| Proveniência do desenho ou pré-registro exagerada | SUSPECTED | IL-MEDIUM-7 | sim (via MEDIUM) |
| Resultados de experimento sem execução | NOT APPLICABLE | análise observacional; `resultados.json` e o commit `52c17fc` existem | não |

## Tool Limitation Disclaimer

> A Phase D (originalidade) **não foi executada** nesta verificação. Não houve comparação por WebSearch nem software de detecção de plágio, e a taxa de amostragem é de 0%. Antes da submissão formal, recomenda-se uma checagem completa com ferramenta profissional, como Turnitin ou iThenticate.
>
> As obras citadas foram verificadas por WebSearch: metadados, resumos e fontes secundárias. scielo.br, doi.org, crossref, redalyc, ideas.repec.org e bibliotecadigital.tse.jus.br estavam bloqueados, e nenhum texto integral foi lido. Por isso, os veredictos de B1 se apoiam nos resumos. Em particular, a inclusão do PL no centrão (Testa et al.) e o achado de Cheibub et al. vêm de fonte secundária.
>
> Os números foram conferidos contra as saídas de `analise.py`, sem reexecutar o script. A verificação, portanto, não atesta que as saídas estejam corretas, só que o texto as reproduz.
>
> As partes do protocolo que dependem de scripts, sidecars ou flags (A0, A0.5, C3, C4, E1 em schema, E1.1, E3.1, E4–E6, #570, verificação com outro modelo) não foram aplicadas. A cobertura de afirmações é `E1-COVERAGE-UNRESOLVED`.

## Verification Audit Trail (dados)

- Valores lidos por scripts Python curtos sobre `resultados.json`, `tabelas/t1–t14b` e `tabelas/votacoes_cargas.csv`.
- Contagens derivadas para IL-MEDIUM-4: votações com `dim2_dominante == True` e sem dados faltantes em PSOL, NOVO, centrão e PT (n = 343). O lado de cada grupo é dado por "% Sim > 50". Os dois polos ficam do mesmo lado e contra o centrão em 36,7% das votações, só o PSOL contra o centrão em 21,6%, só o NOVO em 28,9% e nenhum dos dois em 12,8%. Nas votações de dim1 dominante (n = 825), os dois polos ficam juntos contra o centrão em 0,7%.
- IL-MEDIUM-5: as 11 votações da PEC 3/2021 com dim2 dominante, em `votacoes_cargas.csv`.
- IL-MEDIUM-6: `analise.py`, `_orgao_tarefa`, partição de teste `np.random.default_rng(7).random(n) < 0.10`; `tabelas/t9a_cv_por_orgao`.
- IL-MEDIUM-7: `git log`. O Blueprint (`7c95579`) e a execução completa (`52c17fc`) têm o mesmo horário (10:52:07). O Blueprint não mudou depois disso. `e53f967` contém só `t1_dados_por_ano`.

---

## Rodada 2 (re-verificação dos itens corrigidos)

Data: 13/11/2026. Alvo: `artigo.md` no commit `e8d94db`.

**Escopo.** Reverifiquei só os itens IL-SERIOUS-1, IL-MEDIUM-1 a 7 e IL-MINOR-1 a 16. Também conferi se as correções trouxeram números ou afirmações novas sem fonte. Para isso comparei o texto com o commit `e7131ae` (`git diff --word-diff`) e li as chaves novas de `resultados.json`: `dim2.coalizoes_dim2`, `dim2.coalizoes_dim1`, `dim2.pec3_2021`, `estrutura.coef_dim1_conjunta` e `estrutura.periodos_por_partido`. Li também o trecho de código que gera essas chaves em `analise.py` (`etapa_estrutura`, `etapa_dim2`).

### Verdict (Rodada 2)

**PASS WITH NOTES.** Não restam problemas SERIOUS nem MEDIUM, nem nenhum MAJOR_DISTORTION ou UNVERIFIABLE. Ficam 4 MINOR e 1 nota, nenhum deles bloqueia a passagem ao Stage 3. Na Stage 4.5, os MINOR terão de estar resolvidos.

### Status dos itens da Rodada 1

| ID | Status | Evidência |
|---|---|---|
| IL-SERIOUS-1 (Hix e Noury, §7) | **Resolvido** | O §7 agora diz que os resultados "convergem com Zucco (2009) e com o padrão que Hix e Noury (2016) encontram na maioria dos legislativos" e que "contrariam… a expectativa desses autores para os presidencialismos com governos de coalizão". Isso confere com o resumo da obra. |
| IL-MEDIUM-1 (1,2 unidade) | **Resolvido** | Resumo, abstract e §5.2 dizem "entre 1,2 e 1,3", e os valores são 1,199, 1,266 e 1,295. |
| IL-MEDIUM-2 (H1b "misto") | **Resolvido** | A Tabela 4 diz "não sustentado (ganho do campo = 0,09)". O §5.2 declara que o desenho não tem limiar de refutação e que a decisão é de interpretação, registrada no Apêndice A, item 2. |
| IL-MEDIUM-3 (RQ1) | **Resolvido** | O §5.1 diz que a resposta à RQ1 é "três dimensões". O abstract e o resumo dizem que "duas dimensões não bastam". A manutenção do modelo 2D está no Apêndice A, item 1, com razões rastreáveis: autovalores 0,14/0,83/0,31 e correlações 0,997/0,984 (`dim3.*`). |
| IL-MEDIUM-4 (coalizão contra os polos) | **Resolvido** | O texto relata 51 pp, 37%, 22%, 29% e 0,7%, e também PT com o centrão em 89% contra 70% e PL com o centrão em 78% contra 36%. Os números conferem com `dim2.coalizoes_dim2/dim1` (0,367, 0,216, 0,289, 0,0073, 0,886, 0,702, 0,776, 0,356; n = 343 e 825) e com a minha contagem da Rodada 1. A assinatura E1(b) não cumprida está declarada no §5.3 e no Apêndice A, item 6. A RQ3 foi reformulada ("dissidência dos polos, juntos ou separadamente"). |
| IL-MEDIUM-5 (PEC 3/2021) | **Resolvido** | O PT aparece "do lado dos polos (entre 12% e 18% de 'Sim' nas votações de maior carga, contra 79% a 92% do centrão e 94% a 100% do PL)". Os valores conferem com as linhas da PEC 3/2021 em `t8_top_dim2`, com \|b2\| ≥ 5: PT 11,7, 12,3, 13,6 e 17,5; centrão 79,0–92,2; PL 94,0–100. A chave nova `dim2.pec3_2021` guarda o mínimo e o máximo de **todas** as votações, nos dois sentidos (PT de 11,5 a 100), e não sustenta sozinha o intervalo do texto. A fonte certa é `t8_top_dim2`, citada no parágrafo. |
| IL-MEDIUM-6 (comissões) | **Resolvido** | O texto diz "não se reproduz…", cita a partição única de 10% sem intervalo, traz a t9a (CCJC: 92,4 contra 92,1, +0,30 pp; demais comissões: 92,5 nos dois modelos, valores 0,92547 e 0,92544) e marca a explicação como não testada. Os números conferem com `cv_por_orgao`. |
| IL-MEDIUM-7 (transparência) | **Resolvido, com 1 MINOR novo (R2-MINOR-2)** | A nota cita o commit `7c95579` e declara que o autor "havia lido os resultados de uma primeira execução completa do script antes do commit do documento". O §8, item 10, diz o mesmo. Resumo e abstract não dizem mais "antes da leitura dos resultados completos", mas só falam em "resultados preliminares". |
| IL-MINOR-1 a 13, 15, 16 | **Resolvidos** | Dim3 descrita como "menos estruturada por partido"; "40% maior" na dim2; 0,999 nas duas após Procrustes; "no modelo 3D" no §5.4; "votos analisados" no §3 e na Limitação 4; Missão = 1 em `estrutura.periodos_por_partido`; H1a com critério de refutação e a União declarada como acréscimo; H1c com \|r\| ≤ 0,30; R² 0,29 descrito como "acima do limiar de 0,25"; H2c e H2d relatadas; Apêndice A e *hash* presentes; "menor dependência de recursos" e "cartel" retirados; "não necessariamente com moderação ideológica"; SVD restrita à dim1; coeficientes +0,74 e −0,04 conferem com `estrutura.coef_dim1_conjunta` (0,7368 e −0,0365); "Argelina Cheibub" uniformizado; Zucco e Power com "distância ideológica inédita". |
| IL-MINOR-14 (DOIs de Zucco 2009 e Clinton 2004) | **Aberto, por decisão declarada** | Os DOIs seguem omitidos porque não foram conferidos. A omissão é aceitável na Stage 2.5. Na Stage 4.5, é preciso acrescentá-los depois de conferir ou declarar a omissão na nota das referências. |

### Novos números e afirmações introduzidos pelas correções

Todos os números novos foram rastreados até `resultados.json` ou `tabelas`: 89/78/70/36%, 37/22/29/0,7%, 51 pp, 12–18/79–92/94–100%, +0,74 e −0,04, 0,3 pp e 92,4/92,1/92,5%, Missão = 1, e 0,14/0,83/0,31 com 0,997/0,984. As análises novas (coalizões e regressão conjunta) estão marcadas como exploratórias no Apêndice A, item 5. Achei 3 pontos menores e 1 nota.

### Pendências (MINOR, não bloqueiam a Stage 3)

| ID | Location | Issue | Suggestion |
|---|---|---|---|
| R2-MINOR-1 | §2.3, 2º período ("uma segunda dimensão estável que oponha os dois extremos programáticos ao núcleo de governabilidade") | Ficou a formulação antiga, que não bate com a nova RQ3 | "…que capte a dissidência dos dois extremos programáticos em relação a consensos amplos…" |
| R2-MINOR-2 | Resumo e abstract (frase sobre os critérios) contra a Nota de transparência e o §8, item 10 | Resumo e abstract falam só em "resultados preliminares"; nota e limitação dizem que o autor leu "uma primeira execução completa" antes do commit do desenho. O resumo informa menos que o corpo. | No resumo e no abstract: "o autor da análise já conhecia resultados preliminares e os de uma primeira execução completa" |
| R2-MINOR-3 | §5.3 ("O que define a dimensão é a existência de um consenso amplo… e a dissidência de um ou dos dois polos") e RQ3 | A dissidência de pelo menos um polo contra o centrão **não** distingue a dim2: ocorre em 87% das votações de dim2 dominante e em 91% das de dim1 dominante (`coalizoes_*.algum_polo_contra_centrao`). O que distingue a dim2 é a amplitude do consenso (PT com o centrão em 89% contra 70%; PL em 78% contra 36%) e a dissidência conjunta (37% contra 0,7%). | Reescrever a frase com esses contrastes e relatar `algum_polo_contra_centrao` |
| IL-MINOR-14 | Referências | DOIs omitidos (ver acima) | Resolver até a Stage 4.5 |

**Nota (não é um problema).** O Apêndice A, item 4, diz que o reescalonamento isotrópico do bootstrap foi introduzido "depois de observar que os intervalos de algumas médias partidárias não continham a estimativa pontual". É uma declaração de processo e não há saída que a documente. `NOTAS_PASSAGEM.md` dá outra justificativa: a escala é identificada só pelos priors. Recomenda-se citar o commit em que o reescalonamento entrou (`52c17fc`, "bootstrap reescalado") ou harmonizar as duas justificativas.

### Aviso de limitação (Rodada 2)

Valem as limitações da Rodada 1:
- Phase D não aplicada.
- Fontes externas lidas só pelo resumo.
- Cobertura E1 `E1-COVERAGE-UNRESOLVED`.
- Não reexecutei `analise.py`. As chaves novas foram conferidas contra o código que as gera e contra a minha contagem independente sobre `votacoes_cargas.csv`, e as duas bateram.
