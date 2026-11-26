# Stage 4.5: verificação final de integridade (Artigo 02, disciplina intrapartidária)

**Agente:** `integrity_verification_agent` (ARS, academic-pipeline), Modo 2 (final-check).
**Data:** 26/11/2026. **Commit verificado:** `3b4a7a4` (o manuscrito é o mesmo de `0467017`).
**Arquivos (SHA-256, 16 primeiros caracteres):** `artigo.md` 439014106db7cfd4; `artigo_fonte.md` d665d882bf663d2b; `resultados.json` baedc7e517211ad7; `analise.py` 109043936c4b0f15.
**Flags opcionais:** cross-model, claim audit e passport **não** setados. Por isso não há passport, `experiment_provenance[]`, `figure_table_trace[]` nem Claim Registry em formato de máquina. As seções C3, C4, E1.1 e E3.1 do protocolo ficam `[NÃO APLICÁVEL: sem passport/Figure Package]`, e a extração de afirmações (E1) é manual, com cobertura semântica `not_machine_detectable`.
**Independência:** é uma verificação nova, do zero. Li `stage2_5_integridade.md` só no fim, para conferir se os problemas antigos foram resolvidos. O verificador é do mesmo modelo que escreveu o artigo, então os erros não são independentes.

---

## Veredito: **FAIL** (correção leve, só de texto)

Pela regra do Stage 4.5, qualquer problema bloqueia, inclusive os MINOR. Foram encontrados **2 P1 e 13 P2**. Nenhum é numérico: o código reproduz byte a byte todos os números, tabelas e figuras, e não achei bug que altere resultados. Os problemas são de descrição do método, de atribuição a fontes e de forma. Com eles corrigidos e as três notas `[verificar]` mantidas como notas abertas, o veredito esperado é **PASS WITH NOTES**.

O checklist de modos de falha tem o **Modo 6 SUSPECTED**: a codificação dita "manual" foi feita por um assistente de IA, e o texto não diz isso (P1-1). Pelo protocolo, isso bloqueia até a correção ou até uma decisão registrada do usuário.

## Resumo da verificação (denominadores)

| Categoria | Total | Passou | Problemas |
|---|---|---|---|
| Existência das referências (A1) | 32 na lista; 33 no .bib | 32/32 existem | 0 NOT_FOUND, 0 MISMATCH |
| Exatidão bibliográfica (A2) | 32 | 31 | 1 nota: Nicolau (2000), páginas na lista × .bib (nota aberta) |
| Citações fantasma (A3) | 31 obras citadas × 32 na lista × 33 no .bib | — | 1 órfã na lista e no .bib (Poole e Rosenthal, 1997); 1 órfã só no .bib (Kam, 2009); 0 citações sem entrada |
| Contexto das citações (B1) | 31 obras citadas, 100% | 27 | 4 que vão além do verificado (Carey 2007, duas; Nokken 2000; F&L 1999 já marcada) |
| Números com marcador (C1) | 315 marcadores | 315/315 | 0 |
| Reexecução de `analise.py` | 2.146 chaves; 11 tabelas; 7 figuras | 2.145 chaves; 11/11; 7/7 | só `tempo_execucao_s` muda (180 → 184 s), como esperado |
| Números escritos à mão (C2) | 24 | 22 | 1 não verificável aqui ("11 minutos sem cache"); 1 com referência errada ("< 2%… (Tabela 2)") |
| Consistência interna (C2) | Resumo × Abstract × corpo | Resumo = Abstract | 3 generalizações (P2-8) |
| Originalidade (D1) | 6 frases-teste em 6 parágrafos (cerca de 10% dos parágrafos) | 6 ORIGINAL | 0; amostra abaixo dos 50% do protocolo (nota) |
| Afirmações (E) | 62 registradas (Resumo, Abstract, §5, §8, §9) | 55 VERIFIED | 6 MINOR_DISTORTION; 1 sem suporte (interpretação não testada); 0 MAJOR_DISTORTION |
| Tabelas e figuras: numeração e legendas | 8 + 3 tabelas; 7 figuras | 11/11 tabelas; 5/7 figuras | Fig. 1 antes da Fig. 2 na ordem do texto; legenda da Fig. 1 |

---

## 1. Referências (Fases A e B)

### 1.1 Correspondência texto × lista × .bib

- **Obras citadas no texto:** 31. São elas Ames; Amorim Neto, Cox e McCubbins; Bafumi et al.; Black; Callaway e Sant'Anna; Cameron, Gelbach e Miller; Carey 2007; Carey 2009; Carrubba, Gabel e Hug; Cheibub, Figueiredo e Limongi; Clinton, Jackman e Rivers; Cox e McCubbins; Desposato 2005; Desposato 2006; Figueiredo e Limongi; Heller e Mershon; Krehbiel 1993; Krehbiel 1998; Lauderdale; Mainwaring; McCarty, Poole e Rosenthal; Minozzi e Volden; Nicolau; Nokken; Pereira e Mueller; Power e Zucco; Rice; Snyder e Groseclose; Sun e Abraham; Zucco 2009; Zucco e Lauderdale.
- **Lista de referências:** 32 entradas, as 31 acima mais **Poole e Rosenthal (1997)**, que **não é citada** em lugar nenhum. "Poole" só aparece em "McCarty, Poole e Rosenthal (2001)".
- **`referencias.bib`:** 33 entradas, as 32 da lista mais **`kam2009`**, que não é citada nem listada.
- **Citações sem entrada:** 0.
- Autores, ano, título, periódico, volume, número, páginas e DOI conferem entre a lista e o .bib nas 31 entradas comuns. A exceção é Nicolau (2000): o .bib tem `pages = {709--735}`, com nota `[verificar]`, e a lista traz "[verificar páginas]" sem páginas (ver P2-5).

### 1.2 Existência e metadados (A1/A2)

| Grupo | Referências | Fonte do veredito |
|---|---|---|
| Busca nova nesta sessão (WebSearch) | Nicolau 2000; Nokken 2000; Carey 2007; Cheibub et al. 2009; Heller e Mershon 2005 | Ver a trilha de auditoria (seção 8). Todas VERIFIED, exceto as páginas de Nicolau, que continuam sem confirmação primária (o DOAJ traz "00–00") |
| Trilha registrada no Stage 1 | Rice, Desposato 2005, Carey 2009, Carrubba et al., Krehbiel 1993 e 1998, Snyder e Groseclose, McCarty et al., Cox e McCubbins 2005, Poole e Rosenthal, Black, Clinton et al., Bafumi et al., Lauderdale, Figueiredo e Limongi, Mainwaring, Ames, Power e Zucco, Zucco 2009, Zucco e Lauderdale, Kam | `pipeline/stage1_bibliografia.md`: fonte por entrada; todas "verificado" |
| Trilha registrada no Stage 2.5 | Cameron, Gelbach e Miller 2011 | EconPapers/RePEc; DOI 10.1198/jbes.2010.07136 |
| Trilha registrada no Stage 4 | Amorim Neto et al., Pereira e Mueller, Desposato 2006, Minozzi e Volden, Sun e Abraham, Callaway e Sant'Anna | `pipeline/stage4_bibliografia.md` |

**Limite de cobertura (nota):** pelo protocolo, toda referência deveria ter busca nova no Stage 4.5. Refiz a busca de 5 das 32. Para as outras 27, usei as trilhas registradas, que trazem consulta, fonte e campos confirmados por entrada. Não achei nenhum indício de TF, PAC, PH ou SH. Os padrões IH (falta de DOI) continuam em Krehbiel 1993, Snyder e Groseclose, Cheibub et al., Nokken e Heller e Mershon, todos com `[verificar]` no .bib. São DOIs omitidos, não errados.

### 1.3 Contexto das citações (B1, 100% das 31 obras citadas)

| Obra | O que o artigo atribui | Situação |
|---|---|---|
| Carey (2007; 2009) | "o que leva a restringir a análise a votações disputadas **ou a ponderar pela disputa** (Carey, 2007; 2009)" | **Vai além do verificado.** O Stage 4 confirmou a ponderação por proximidade só em *working papers* (Carey 2000/2002) e recomendou não atribuí-la ao AJPS 2007. A resposta aos revisores diz que a fórmula "foi retirada do texto", mas a atribuição continua no §2 (P1-2) |
| Carey (2007; 2009) | "Carey distingue *unidade* de *disciplina*" | Não confirmada em fonte lida (o Stage 2.5 já pedia a conferência, em P2-2). Risco baixo (P1-2) |
| Carey (2007) | unidade menor onde há "principais concorrentes" | VERIFIED (resumo AJPS; eScholarship) |
| Nokken (2000) | "Os dados são compatíveis com os dois mecanismos [seleção e ajuste], **como em Nokken (2000)**" | **Vai além do verificado.** A fonte confirmada (tese de 1999 e citações) diz que quem troca de partido muda o voto no momento da troca, rumo ao novo partido, o que é ajuste. Não está confirmado que Nokken encontre também seleção (P1-2) |
| Nokken (2000), §2 | "estuda a dinâmica da lealdade e da defecção..., inclusive dos que trocam de partido" | VERIFIED |
| Figueiredo e Limongi (1999) | Colégio de Líderes + poderes de agenda do Executivo (MPs, urgência) | VERIFIED em fontes secundárias. A "lista completa dos instrumentos" já está marcada `[verificar]`: nota aberta, mantida por instrução do usuário |
| Nicolau (2000) | "documenta a disciplina no primeiro governo FHC" | VERIFIED (título; resumo no repositório) |
| Desposato (2005) | inflação do Rice em grupos pequenos; subamostra de m membros | VERIFIED |
| Cheibub, Figueiredo e Limongi (2009) | "discutem partidos e governadores como determinantes" | VERIFIED (título e resumo; o artigo não atribui conclusão) |
| Amorim Neto et al.; Pereira e Mueller; Desposato 2006; Heller e Mershon; Minozzi e Volden; Sun e Abraham; Callaway e Sant'Anna | conforme o Stage 4 | VERIFIED |
| Rice; Krehbiel 1993 e 1998; Black; Snyder e Groseclose; McCarty et al.; Clinton et al.; Bafumi et al.; Lauderdale; Zucco; Zucco e Lauderdale; Power e Zucco; Cox e McCubbins; Carrubba et al.; Mainwaring; Ames; Cameron et al. | atribuições genéricas e coerentes com os resumos do Stage 1 | VERIFIED |

---

## 2. Números (Fase C)

### 2.1 Reexecução

Copiei `dados/leg57/`, `embeddings_deputados.py` e a pasta do artigo, com o cache de IRT, para o scratchpad e rodei `python artigos/02-disciplina-intrapartidaria/analise.py` da raiz da cópia. Terminou com código 0 em 184 s. Resultado:

- `resultados.json`: 2.146 chaves, 2.145 idênticas. Só `tempo_execucao_s` difere (180 → 184).
- `tabelas/*.md`: 11/11 idênticas byte a byte.
- `figuras/*.png`: 7/7 idênticas byte a byte.
- `artigo.md`: idêntico, exceto o "180 segundos" do Apêndice A, que é o tempo de execução.

**Não verificado:** a execução sem cache, que o texto estima em "cerca de 11 minutos em 4 núcleos". O cache não está no git, então a reprodução a frio não foi testada aqui (nota).

### 2.2 Marcadores (todos, não só uma amostra)

Reimplementei `montar_artigo()` de forma independente: os mesmos formatadores, aplicados ao `resultados.json` versionado. Os **315 marcadores** (89 linhas de `artigo_fonte.md`) produzem um texto **idêntico** ao `artigo.md` versionado, sem chave ausente. Além disso, conferi a semântica da chave usada (se o marcador aponta para a grandeza que a frase descreve) em 74 marcadores. Alguns deles:

- `unid_ano_*` e a amplitude de 1,6 p.p.;
- `U_queda2025_*` (PSD 4,9; MDB 4,7; PP 3,1; União 2,7) e PL/PT/REPUBLICANOS estáveis;
- `reg_mb_vazias` 199/227 e `reg_mb_linhas_partido_PL_PT` = 0;
- `fala_mb_votacoes` 138/227;
- `cvdif_M2b_M3` 0,0058 [0,0029; 0,0086], e por votações [0,0043; 0,0072];
- `ev_c26_U_ind:0 a 3` −6,5 [−10,5; −2,4];
- `div_cf_excesso` 4,2 [3,2; 5,3] e `div_cf_excesso_sd` 17,1;
- `pred_dir_acerto` 68/110 = 61,8%, p = 0,017;
- `sel_*` 98, 101 e 65 de 145;
- `diss_n_z2` 32 de 595;
- `pivos_boot_max` = 0,20, o que torna verdadeira a frase "nenhum… em mais de 20%";
- `intra1_tipo_*`: 38% contra 30,5%, arredondado para 31%.

Todos conferem.

**Aritmética derivada no texto:**

- M0c→M1 = 0,4298 − 0,2838 = 0,146 ✓
- M1→M2b = 0,0255 ✓
- M2b→M3 = 0,0058 ✓
- M2→M3L = 0,015 ✓
- M3→M4 = 0,0078 ✓
- M5−M4 = 0,0208 ✓
- 210 − 19 = 191 trocas ✓
- D sob ausência: 0,909 × (1 − 0,196) ≈ 0,731 ✓
- "cerca de metade": alta de 2,8 p.p. bruta e de 1,5 p.p. com composição fixa ✓
- pré-tendência de 3,1 = 1,4 − (−1,7) ✓
- 1 − 94,1% ≈ 6% de discordância ✓

### 2.3 Números escritos à mão em `artigo_fonte.md`

| Número | Local | Conferência |
|---|---|---|
| 120 votações codificadas | §3 | ✓ (`validacao_tipo_votacao.csv` tem 120 linhas, 1 "indeterminado") |
| 45 minutos | §3 | ✓ (`orientacoes_faladas`: `tolerance=45min`) |
| 513; ± 5 | §3 | ✓ (código) |
| 2,5% (minoria mínima no IRT) | §4.2 | ✓ (`prep_irt(min_minoria=0.025)`) |
| 10% (disputa); m = 3 e m = 10 | §4.1 | ✓ |
| janelas ≤ −13 … ≥ 4 | §4.4 | ✓ (`estudo_evento`) |
| "menos de 2% dos votos" (7 partidos) | §5.1 | ✓ nos dados (máximo de 1,16%, no União), mas a referência "(Tabela 2)" está errada: a Tabela 2 mostra o nº de votações, e a % está na Fig. 1 (P2-6) |
| 20% (limiar de cobertura da Fig. 2) | legenda | ✓ (`fig_serie`) |
| 308 votos (PEC) | §5.2; Tab. A3 | ✓ (constitucional) |
| 50 (células grandes); 10% (minoria interna); λ = 1 e 16 | §5.4 | ✓ |
| 100 votações de maior carga | §5.5 | ✓ |
| 26 g.l. | §5.6 | ✓ (27 UFs − 1) |
| 100 votos (dissidentes); 40% e 60% | §5.6; legendas | ✓ |
| 13/09/2023; 02/09/2025 | §5.8 | ✓ no código (`partido_vs_governo`) e no Stage 4 (datas finas `[verificar]`) |
| 10 dias (pareamento de suplentes) | §7 | ✓ (`motivo_suplencia`) |
| 11/11/2026 (coleta) | §3 | não conferível pelo código (metadado da coleta) |
| "cerca de 11 minutos" sem cache | Apêndice A | **não verificado** (nota) |
| 1/1/2023; 13/09/2023 | Apêndice C | ✓ (Stage 4) |
| 100 votos; 67, 86 e 57 votos | Apêndice C | marcadores ✓ |

---

## 3. Afirmações (Fase E)

**Registro manual: 62 afirmações substantivas.** São 9 no Resumo, 9 no Abstract (espelho), 33 em §5.1–§5.8 e §6, 7 na §8 e 4 na §9. O registro é feito à mão e não pode ser dado como completo.

**Resultado: 55 VERIFIED, 6 MINOR_DISTORTION, 1 sem suporte (interpretação não testada), 0 MAJOR_DISTORTION.**

**Resumo × Abstract:** dizem o mesmo, frase a frase: números, direção, "o ganho é pequeno, mas o intervalo exclui zero", artefato de 2025, U em queda no centro, eixo governo–oposição, distância espacial dominante, ajuste após a troca e excesso de lealdade. Os formatos numéricos em inglês estão corretos (454,829; 90.9%).

| # | Afirmação (local) | Verificação | Veredito |
|---|---|---|---|
| 1 | D = 90,9% [90,4; 91,3]; U = 89,5% (Resumo, §5.2) | `disc_geral`, `unidade_geral` | VERIFIED |
| 2 | D sobe em 2025 "por artefato"; U cai (Resumo, §5.1, §8) | D 2025 = 92,9 × 90,1, com cobertura de 32% × 89%; composição fixa 92,0 × 90,5; U 2025 = 88,7, a menor de todas | VERIFIED. "Por artefato" é inferência, mas o §5.1 a sustenta com U e cobertura |
| 3 | "a unidade… cai **nos partidos de centro**" (Resumo, Abstract, §8 "a unidade dos partidos de centro cai") | Cai em PSD, MDB, PP, União e PSDB. REPUBLICANOS (92,5 × 92,3) e PODE (88,1 × ≈ 87,8) ficam estáveis. O §5.1 diz, com mais cuidado, "a queda **se concentra**" | MINOR_DISTORTION (P2-8) |
| 4 | Registro do megabloco "quase sempre vazio"; 0 linhas de PL/PT; 227 de Oposição | `reg_mb_*` | VERIFIED |
| 5 | Falas cobrem 138/227; concordância de 94,1% em 563 casos; viés de −4,1 p.p. | `fala_*` | VERIFIED |
| 6 | M2b→M3 > 0, IC exclui zero nas duas vias de bootstrap | `cvdif_M2b_M3_*` | VERIFIED |
| 7 | A dimensão é o eixo governo–oposição: correlação de 0,90; 100% nas 100 de maior carga; correlação de 0,94 com a posição global | `intra1_*` | VERIFIED, com a ressalva sobre esquerda–direita no §5.5 |
| 8 | Distância espacial: 22,1 p.p./DP [19,2; 25,0] | `reg_D_dist_fora_*` | VERIFIED |
| 9 | Depois da troca, vota mais com os novos colegas: coorte −6,5 [−10,5; −2,4] | `ev_c26_U_*` | VERIFIED (em U; em D não se distingue de zero, o que o §5.7 diz) |
| 10 | Excesso de lealdade > 0 nos dois contrafactuais | `div_cf_excesso*` | VERIFIED |
| 11 | "PT, PSOL, PCdoB e NOVO votam quase sempre com a liderança **e com os colegas**" (§5.2) | O NOVO não tem U (Tabela 2: "–") | MINOR_DISTORTION (P2-7) |
| 12 | "menos de 2% dos votos… (Tabela 2)" (§5.1) | Valor correto; a referência aponta para a tabela errada | MINOR_DISTORTION (P2-6) |
| 13 | "As estimativas pontuais sobem 3,1 pontos **ao longo do ano anterior à troca**" (§5.7) | A diferença é entre a janela ≤ −13 meses (mais de um ano antes) e −3 a −1 | MINOR_DISTORTION (P2-12) |
| 14 | "para o centro, o bloco; **em 2025, quase nada**" (§9) | A cobertura de D em 2025 é de 32%. O registro "quase vazio" vale para o megabloco (199/227) | MINOR_DISTORTION (P2-8) |
| 15 | "Os dados são compatíveis com os dois mecanismos, **como em Nokken (2000)**" (§5.7) | O lado dos dados confere: 67,6%, 69,7% e 44,8%. O lado de Nokken não foi verificado | MINOR_DISTORTION de citação (P1-2) |
| 16 | "a heterogeneidade interna **permite** ao Governo construir maiorias votação a votação com parte de suas bancadas" (§8) | Mecanismo causal não testado no artigo | Sem suporte (interpretação; P2-9) |
| 17–62 | As demais afirmações de §5.1–§6, §8 e §9: tipos de votação, temas, Rice e E2, liberação (16/16), obstrução, ausências (73,1%, ρ = 0,91; PEC 94,9 → 83,8), validação cruzada (células grandes, minoria ≥ 10%, λ), validação externa (AUC 0,59; 61,8% × 64,5%), correlatos (troca antes/depois; UF χ² = 73,2), variância (1%; 80%), dispersão, dissidentes, pivôs "sempre no centro" (8 partidos na Tab. A3, todos de centro), seleção × ajuste, PSB/PDT sob orientação própria, PT com 9 votações, robustez (7 variantes; "menos de meio ponto" vale para as variantes além de "sem inferidas" e "só própria") | Conferidas contra `resultados.json` e tabelas reexecutadas | VERIFIED |

**E4/E5 (advisórios):** sem RQ Brief em formato de máquina `[E4-SKIPPED: no scope context]`. Não há afirmação de primazia ("o primeiro a…"); as afirmações de contribuição de medida são delimitadas à 57ª Legislatura. **E6:** `[E6-SKIPPED: sem Revision-Evidence Bundle]`. A comparação qualitativa com a versão anterior não mostrou endurecimento de afirmações. As afirmações sobre 2025 e as falas ficaram **mais** fracas, como pedia a re-revisão.

---

## 4. Código × Método

| Elemento do Método | Código | Situação |
|---|---|---|
| D: direção; Não = Obstrução; Abstenção = desvio; camadas própria, bloco e inferido; cobertura | `amostra_D`, `disciplina` | ✓ |
| U: maioria dos demais colegas (≥ 5), sem empates, abstenção do deputado = desvio | `amostra_U` (abstenção vira `vd = NaN`, logo `unido = 0`; colegas que se abstêm saem de n) | ✓ |
| Rice em células com ≥ 3; hipergeométrica exata para m = 3 e m = 10; base de votantes independentes; disputadas ≥ 10% | `rice`, `rice_esperado_sub`, `rice_aleatorio` | ✓ |
| Bootstrap em duas vias para taxas por partido (500 réplicas) | `boot_duas_vias` (pesos multinomiais de votações × deputados) | ✓. O IC **geral** de D (90,4–91,3) vem só de votações (`boot_razao`), o que não está dito (P2-11) |
| IRT global e intra; g partido×votação; centrado no partido; minoria < 2,5% fora | `prep_irt`, `ajustar`, `_intra` | ✓. λ_d = 4 (padrão) não é informado (P2-11) |
| CV em 5 dobras estratificada por votação | `dobras` | ✓ |
| M0 / M0c | `regra_orientacao` (M0c com suavização (s+1)/(n+2) por fonte × partido) | ✓ |
| M1 (`fe`); M2 (ρ por deputado, *offset* M1); M2b (ρ por período × s_j, *offset* M1); M3L (ρ por deputado sobre M3); M4; M5 | `MODELOS_CV`, `ajustar_lealdade`, `ajustar_lealdade_b` | ✓. M2b é estimado em duas etapas (*offset* fixo de M1; λ_r = 1, λ_s = 0,04), enquanto M3 reestima a e g em conjunto (λ_d = 4). "Mesma estrutura de parâmetros" é correto quanto à forma, mas a diferença de estimação e de penalização não é dita (P2-11) |
| **M3emb** | calculado em `validacao_cruzada`, fora da Tabela 4 | **Definido no §4.3, sem resultado no texto.** O Apêndice B diz que foi retirado (P2-4) |
| Células com divisão interna: ≥ 5 colegas e ≥ 1 desvio no treino (64%) | `avaliar_cv` | ✓ |
| Bootstrap de deputados e de votações nas diferenças | `avaliar_cv` | ✓ |
| MPL com EF partido×votação; EP em duas vias (Cameron et al.) | `ols_fe` (V = V₁ + V₂ − V₁₂) | ✓ |
| Distância no outro biênio, em DP da dim1 | `distancia_fora_periodo`, `anexar_distancia` | ✓ |
| Estudo de evento: EF de deputado e de partido×votação; janelas; teste conjunto | `estudo_evento` | ✓ |
| Coorte de 2026 com controles que nunca trocaram | `excl26 = (ind − ind26) ∪ fus` (precedência de operadores correta) | ✓, com uma ressalva: 4 deputados cuja única troca foi antes de 01/04/2023 ficam entre os "nunca trocaram". O efeito é desprezível (P2-14) |
| Contrafactuais (i), previsões de CV do M5, e (ii), M5 sem as células divergentes | `partido_vs_governo` (sem vazamento; abstenções fora por construção) | ✓ |
| Base ministerial e base datada | `BASE_MINISTERIAL`; filtro de datas | ✓ |
| Orientações faladas: regex nos primeiros 600 caracteres; `merge_asof` para frente com 45 min; validação contra o registro | `orientacoes_faladas` | ✓ (o corte de 600 caracteres não é descrito; irrelevante) |
| Limites com ausência (geral e PEC; presidente da sessão fora) | `ausencia_geral`, `ausencia_pec` | ✓ |
| Validações "manuais" (120 tipos; 50 falas) | CSVs com a coluna `codificador` = "leitura manual… (**assistente de IA**, Stage 4)" em 120/120 e 50/50 | **O Método diz "codificadas manualmente" e "conferência manual", sem dizer que o codificador foi um assistente de IA** (P1-1) |

**Procura de bugs que alterem resultados:** revisei vazamento entre treino e teste na CV, chaves de junção (votação|deputado), sinais de orientação (`orientar`), precedência de conjuntos no estudo de evento, divisão por zero no bootstrap, identificação no `ols_fe` (colunas colineares removidas com aviso) e o cache (chave pela impressão digital dos dados). **Nenhum bug que altere resultados foi encontrado.**

---

## 5. Checklist dos 7 modos de falha de IA

| Modo | Resultado | Evidência | Bloqueia? |
|---|---|---|---|
| 1. Bug de implementação | **CLEAR** | Reexecução idêntica (JSON, 11 tabelas, 7 figuras) e revisão de código (seção 4). Ressalva: só com cache; a execução a frio não foi testada | não |
| 2. Citação alucinada | **INSUFFICIENT EVIDENCE** | As 32 obras existem, sem MISMATCH. Duas atribuições de conteúdo (ponderação a Carey 2007; "dois mecanismos" a Nokken 2000) não foram confirmadas em fonte lida e não têm `[verificar]` (P1-2) | não (pode seguir com aviso; corrigir o texto resolve) |
| 3. Resultado experimental alucinado | **CLEAR** | 315/315 marcadores reproduzidos a partir de uma reexecução; os números escritos à mão foram conferidos | não |
| 4. Atalho (*shortcut*) | **CLEAR** | Comparador M2b com a mesma forma de M3, M3L, células ≥ 50, minoria ≥ 10%, bootstrap em duas vias, contrafactual em dois limites; ressalva de esquerda–direita declarada | não |
| 5. Bug apresentado como achado | **CLEAR** | O achado "surpreendente" (D sobe em 2025) foi rastreado até o dado bruto: 0 linhas de PL/PT e 199/227 linhas de bloco vazias em `votacoes_orientacoes.parquet`. Ele é tratado como artefato, não como achado de comportamento | não |
| 6. Fabricação de metodologia | **SUSPECTED** | O §3 e o Apêndice A descrevem a validação do classificador e a conferência das falas como "manuais". Os CSVs mostram que ambas foram feitas por um assistente de IA (a mesma família de modelo que gerou as regras e as associações), sem codificador humano. Secundário: M3emb é descrito no Método sem resultado; a legenda da Fig. 1 descreve um bootstrap diferente do usado | **sim**, até corrigir o texto (P1-1) ou o usuário registrar um *override* com justificativa |
| 7. Frame-lock | **CLEAR** | O enquadramento de 2025 foi revisto duas vezes conforme a evidência (as falas passaram de medida de nível a evidência de orientação). Os critérios de falha posteriores aos resultados estão declarados (§2, Apêndice B) | não |

---

## 6. Numeração de tabelas e figuras e legendas

- **Tabelas:** 1 → 8 aparecem e são citadas em ordem (1 §3; 2 §5.1/§5.2; 3 §5.3; 4 §5.4; 5 §5.5; 6 e 7 §5.6; 8 §6). As tabelas A1–A3 estão no Apêndice D e são citadas em §5.3 e §5.6. As legendas e notas das tabelas conferem com o código. As 11 tabelas são reproduzidas.
- **Figuras:** a **Figura 2** é citada (§5.1) e mostrada **antes** da Figura 1 (§5.2). A resposta aos revisores (P1-1) diz que tabelas e figuras foram "renumeradas pela ordem de aparição" (P2-3). As Figuras 3–7 estão em ordem.
- **Legenda da Fig. 1:** diz "IC 95% por bootstrap de votações", mas o eixo da figura e o código (`fig_disciplina` usa `D_lo2`/`U_lo2`) usam o bootstrap **em duas vias**. No PSDB, o limite inferior de D (75,8) fica cortado pelo `xlim` de 76 (P2-2).
- **Fig. 2, 3, 4, 5, 6 e 7:** as legendas conferem com o código. Na Fig. 6, só a troca individual é plotada, o que é coerente com o texto ("fusões… coeficientes não são identificados").
- Os nomes de arquivo internos (`tab4_temas` = Tabela A1, `tab5_validacao` = Tabela 4 etc.) não seguem a numeração. É cosmético e não aparece para o leitor.

---

## 7. Marcas `[verificar]` e afirmações não verificadas sem marca

**Notas abertas, mantidas por instrução do usuário** (marcar em vez de inventar; não contam como problema):

1. Nicolau (2000), páginas e DOI: a lista diz "[verificar páginas]"; o .bib tem 709–735 com `[verificar]`. Fontes secundárias divergem (709–735 × 709–734), e o DOAJ dá "00–00".
2. Figueiredo e Limongi (1999), "a lista completa dos instrumentos no original fica [verificar]" (§2).
3. Base ministerial, "datas finas [verificar]" (Apêndice C).

**Afirmações não verificadas que estão SEM a marca `[verificar]`** (resposta à pergunta do usuário: **sim, há**):

- (a) Carey (2007) como fonte de "ponderar pela disputa" (§2). O Stage 4 recomendou não atribuir (P1-2).
- (b) "Carey distingue *unidade* de *disciplina*" (§2): não conferido em fonte lida (P1-2).
- (c) "como em Nokken (2000)" para os dois mecanismos (§5.7) (P1-2).
- (d) "um megabloco formado para a eleição da Mesa" (§1): a finalidade do bloco não tem fonte (P2-13).
- (e) "Sem cache, a execução leva cerca de 11 minutos em 4 núcleos" (Apêndice A): não reexecutado a frio (P2-10).
- (f) A validação descrita como "manual" (§3), que de fato foi feita por IA (P1-1). Os números estão certos; o que falta é dizer quem codificou.

---

## 8. Lista de problemas

### P1

| ID | Local | Problema | Correção sugerida |
|---|---|---|---|
| P1-1 (IL-MEDIUM-1; Modo 6) | §3 ("numa amostra estratificada de 120 votações codificadas manualmente"; "Numa conferência manual de 50 associações"); Apêndice A ("a codificação manual dos tipos de votação"); Apêndice B ("Validação manual do classificador") | A coluna `codificador` dos dois CSVs diz "assistente de IA, Stage 4" em 170/170 linhas. Chamar isso de codificação manual descreve mal o procedimento, e a validação não é independente do sistema que gerou as regras e as associações | Escrever, por exemplo, "codificadas por leitura da descrição, feita por um assistente de IA (sem codificador humano independente)" nos três lugares, e acrescentar a limitação no §7. Melhor ainda: recodificar uma amostra por uma pessoa e informar a concordância |
| P1-2 (IL-MINOR-1..3; citação) | §2 "(Carey, 2007; 2009)" depois de "ponderar pela disputa"; §2 "Carey distingue *unidade* de *disciplina*"; §5.7 "como em Nokken (2000)" | O conteúdo atribuído vai além do que foi verificado (Stage 4, item 11; resumo de Nokken). A resposta aos revisores diz que a fórmula de Carey "foi retirada do texto", mas a atribuição continua | Carey: citar "(Carey, 2009)" para a ponderação, ou "Carey (2000)" como *working paper* (não listado), ou marcar `[verificar]`. Unidade × disciplina: conferir no texto de Carey (2007, intro) ou marcar `[verificar]`. Nokken: "Nokken (2000) documenta mudança de voto no momento da troca", ou retirar "como em Nokken (2000)" |

### P2

| ID | Local | Problema | Correção sugerida |
|---|---|---|---|
| P2-1 | Referências; `referencias.bib` | Órfãs: Poole e Rosenthal (1997) na lista e no .bib, sem citação; `kam2009` só no .bib | Citar (por exemplo, Poole e Rosenthal no §2, junto de McCarty et al.) ou retirar das duas listas |
| P2-2 | Legenda da Fig. 1 | Diz "bootstrap de votações"; a figura usa o bootstrap em duas vias. O IC de D do PSDB é cortado em 76 | "IC 95% por bootstrap em duas vias (votações e deputados)"; `set_xlim(74, 100.5)` em `fig_disciplina` |
| P2-3 | §5.1 e §5.2 | A Figura 2 é citada e mostrada antes da Figura 1 | Renumerar (a série semestral vira a Fig. 1) ou citar a Fig. 1 antes no §5.1 |
| P2-4 | §4.3 ("**M3emb** é M3 com as posições embaralhadas…"); Apêndice B, tabela ("M3emb acrescentados") | Modelo definido sem resultado; o próprio Apêndice B diz que foi retirado | Retirar a definição do §4.3 e o item da tabela, ou reportar o resultado |
| P2-5 | Referências: Nicolau (2000) | A lista não tem páginas; o .bib tem 709–735 | Harmonizar: remover `pages` do .bib (critério estrito do Stage 4) ou pôr "p. 709–735 [verificar]" na lista |
| P2-6 | §5.1 "menos de 2% dos votos… (Tabela 2)" | A Tabela 2 não mostra essa %; ela está na Fig. 1 | "(Figura 1)" |
| P2-7 | §5.2 "PT, PSOL, PCdoB e NOVO votam quase sempre com a liderança e com os colegas" | O NOVO não tem U | "PT, PSOL e PCdoB…; o NOVO, com a liderança (99,4%)" |
| P2-8 | Resumo, Abstract, §8 ("a unidade dos partidos de centro cai"); §9 ("em 2025, quase nada") | Generalizações: REPUBLICANOS e PODE ficam estáveis; a cobertura de D em 2025 é de 32% | "cai na maior parte dos partidos de centro (PSD, MDB, PP, União)" / "falls in most centrist parties"; §9: "em 2025, para o megabloco, quase nada" |
| P2-9 | §8 "a heterogeneidade interna permite ao Governo construir maiorias votação a votação" | Mecanismo não testado | "o que é compatível com um Governo que constrói maiorias…" |
| P2-10 | Apêndice A | "cada número do texto é uma referência a `resultados.json`" (há números escritos à mão; ver 2.3); "cerca de 11 minutos" sem cache não verificado; a lista de entradas omite `discursos.parquet` e `dados_aux/validacao_falas.csv` | "cada resultado do texto…; parâmetros de desenho estão fixos no código"; acrescentar as duas entradas; reconferir o tempo a frio ou escrever "dezenas de minutos" |
| P2-11 | §4.1–§4.3 | O IC geral de D é só por votações, sem dizer; λ_d = 4 e as penalizações de M2b (λ_r = 1, λ_s = 0,04) não aparecem; M2b é estimado em duas etapas sobre o *offset* de M1 | Uma frase em cada ponto |
| P2-12 | §5.7 "sobem 3,1 pontos ao longo do ano anterior à troca" | A diferença é entre ≤ −13 meses e −3 a −1 | "entre a janela de 13 meses ou mais antes da troca e os três meses anteriores, as estimativas pontuais sobem 3,1 pontos" |
| P2-13 | §1 "um megabloco formado para a eleição da Mesa" | Finalidade sem fonte | Citar fonte (notícia ou ato da Mesa) ou marcar `[verificar]` |
| P2-14 | §4.4 / §5.7 (coorte de 2026) | 4 deputados com troca só antes de 01/04/2023 contam como "nunca trocaram" | Excluí-los ou dizer "que não trocaram desde abril de 2023"; o efeito é desprezível |

---

## 9. Comparação com o Stage 2.5 (conferência suplementar)

- Os P1 da rodada 2 do Stage 2.5 estão resolvidos no texto atual: excesso por partido, placebo, pré-tendência, contrafactual como limite inferior, Método × código (M3L, ρ_i ∈ ℝ) e desvios do plano.
- O P2-1 antigo (Cameron órfão) foi resolvido; Cameron agora é citada no §4.4. Mas surgiram duas órfãs novas (P2-1 atual).
- O P2-2 antigo pedia conferir Figueiredo e Limongi e Carey. Figueiredo e Limongi ganhou marca `[verificar]`. Carey continua sem conferência (P1-2 atual).
- A pendência de Nicolau (P1-8 antigo) está mantida como nota, por instrução do usuário.

---

## 10. Trilha de auditoria (buscas desta sessão)

| Consulta | Principais resultados | Determinação |
|---|---|---|
| Nicolau 2000 "Disciplina partidária e base parlamentar…" Dados 43 4 páginas | [DOAJ](https://doaj.org/article/bf0c3d3b746a4658aea869e30e8fd742) (v. 43, n. 4, p. "00–00"); [OAI SciELO S0011-52582000000400004](https://sidalc.net/search/Record/oai:scielo:S0011-52582000000400004) | Existe; páginas não confirmadas (nota) |
| Nokken 2000 "Dynamics of Congressional Loyalty"… LSQ 25 417-444 | [Tese, IDEALS/Illinois](https://www.ideals.illinois.edu/items/83886); [Shor 2026](https://bshor.github.io/files/papers/shor_switchers_2026.pdf) | Existe, LSQ 25: 417–444. O achado confirmado é a mudança de voto na troca, rumo ao novo partido |
| Carey 2007 "Competing Principals…" abstract | [IDEAS/RePEc](https://ideas.repec.org/a/wly/amposc/v51y2007i1p92-107.html); [eScholarship](https://escholarship.org/uc/item/7zq7k5w8) | Existe, AJPS 51(1): 92–107. Principais concorrentes confirmados; ponderação e unidade × disciplina não aparecem no resumo |
| Cheibub, Figueiredo e Limongi 2009 LAPS 51 1 | [Cambridge Core](https://www.cambridge.org/core/journals/latin-american-politics-and-society/article/political-parties-and-governors-as-determinants-of-legislative-behavior-in-brazils-chamber-of-deputies-19882006/04177956C7296AD9A5F16C114664200D) | Existe; título com "1988–2006" |
| Heller e Mershon 2005 JOP 67 2 536 | [Página da autora](https://uva.theopenscholar.com/carol-mershon/publications/party-switching-italian-chamber-deputies-1996-2001); [SUNY](https://researchconnect.suny.edu/en/publications/party-switching-in-the-italian-chamber-of-deputies-1996-2001/) | Existe, JOP 67(2): 536–559 |
| Originalidade: frases do §1 e do §2 entre aspas (4 buscas; 6 frases-teste) | nenhuma correspondência literal | ORIGINAL |

**Aviso sobre ferramentas:** a checagem de originalidade (Fase D) usa buscas na web, é heurística e cobriu cerca de 10% dos parágrafos, abaixo dos 50% do protocolo. Ela não substitui Turnitin ou iThenticate. O risco é baixo porque o texto descreve análises originais de dados de 2023–2026, mas recomenda-se um verificador profissional antes da submissão. As referências sem busca nova nesta sessão (27/32) se apoiam nas trilhas registradas nos Stages 1, 2.5 e 4.

**Arquivos da reexecução:** `/tmp/claude-0/-home-user-chamberofdeputiesBrazil/f52fda40-72cc-5ee2-acb5-2b134774c1a2/scratchpad/rep/` (cópia; nenhum arquivo do artigo foi editado).

---
---

# Rodada 2 (commit `1da626c`)

**Data:** 26/11/2026. **Escopo:** reverificar as correções da rodada 1 e procurar problemas introduzidos por elas (diff `3b4a7a4..1da626c` em `artigo_fonte.md`, `artigo.md`, `analise.py`, `referencias.bib` e `resultados.json`). Também refiz os pontos da rodada 1 que não estavam na lista de correções do coordenador. As marcas `[verificar]` continuam como notas abertas, por instrução do usuário.

## Veredito da rodada 2: **FAIL** (0 P1; 10 P2, todos de texto ou forma)

Os dois P1 foram resolvidos. O Modo 6 passa a CLEAR e o Modo 2 a CLEAR. Restam 10 P2. Dois deles foram **introduzidos pela correção**: a referência à figura errada no §5.1 e uma definição de "disciplina" que a medida D não satisfaz. Os outros oito são P2 da rodada 1 que não estavam na lista de correções. Como o Stage 4.5 exige zero problemas, o veredito formal continua FAIL. Nenhum P2 afeta número, direção ou conclusão. Com os 10 corrigidos, o esperado é **PASS WITH NOTES**, com as três notas `[verificar]`.

## R2.1 Reprodução

Reexecutei `analise.py` numa cópia nova, com o cache e sem figuras pré-existentes (173 s, código 0). Resultado:

- `resultados.json`: 2.145/2.146 chaves idênticas; só `tempo_execucao_s` muda.
- `tabelas/*.md`: 11/11 idênticas.
- Figuras: 7/7 idênticas byte a byte, com os novos nomes (`fig1_serie_semestral.png`, `fig2_disciplina_unidade.png`). A pasta não tem arquivos antigos órfãos.
- `artigo.md`: idêntico, exceto o tempo do Apêndice A.

A mudança em `analise.py` está restrita aos dois nomes de arquivo em `savefig`.

O novo texto do Apêndice A ("cerca de 11 minutos… numa reexecução de verificação (Stage 2.5)") confere com `stage2_5_integridade.md` (R2-P2-15: "668 s, ou cerca de 11 min, em 4 núcleos").

## R2.2 Situação dos problemas da rodada 1

| Rodada 1 | Situação | Evidência (`artigo.md` em `1da626c`) |
|---|---|---|
| P1-1 codificação por IA | **Resolvido no §3**; resíduo no Apêndice A → R2-2 | §3: "…codificadas pelo assistente de IA que conduziu a análise, a partir da leitura das descrições, sem segundo codificador"; nas falas: "feita pelo mesmo assistente de IA…, sem segundo codificador". O Apêndice A (l. 514) ainda diz "a codificação manual dos tipos de votação" |
| P1-2 Carey / Nokken | **Resolvido** | "ponderar pela disputa" ficou sem atribuição. "Carey (2007; 2009) mostra que a unidade de voto é menor onde 'principais concorrentes'…" está dentro do verificado (resumo AJPS; eScholarship). "Como em Nokken (2000)" foi retirado. A atribuição da distinção a Krehbiel (1993) confere com o argumento verificado no Stage 1 ("só há efeito partidário quando o legislador vota com o partido apesar de discordar"). Ver, porém, R2-3 |
| P2-1 órfãs | **Resolvido** | Lista com 31 entradas e .bib com 31 entradas; as 31 obras citadas batem 1:1; 0 órfãs, 0 citações sem entrada |
| P2-2 legenda da Fig. 1 (agora Fig. 2) | **Resolvido**; resíduo do corte do PSDB → R2-6 | Legenda: "bootstrap em duas vias (votações e deputados)". `fig_disciplina` mantém `set_xlim(76, …)`, e o limite inferior de D do PSDB (75,8) continua cortado |
| P2-3 ordem das figuras | **Resolvido** | Fig. 1 (série) é citada no §5.1 e mostrada antes da Fig. 2 (§5.2). As Figuras 1–7 aparecem em ordem; cada `![Figura n]` aponta para o arquivo certo |
| P2-4 M3emb no Método | **Resolvido** | O §4.3 não menciona mais M3emb. O Apêndice B o explica ao dizer que foi retirado; a linha da tabela "M3emb acrescentados" é aceitável nesse contexto |
| P2-5 Nicolau, páginas na lista × .bib | **Não tratado** → R2-7 | A lista diz "[verificar páginas]"; o .bib tem `pages = {709--735}` |
| P2-6 "menos de 2%" | **Corrigido de forma errada** → R2-1 | O texto diz "(Figura 1, coluna à direita)". A coluna com a % de orientação própria está na **Figura 2** (por partido); a Figura 1 é a série semestral |
| P2-7 NOVO sem U | **Resolvido** | "…NOVO votam quase sempre com a liderança, e os três primeiros, também com os colegas (NOVO não tem U)" |
| P2-8 generalizações | **Resolvido no Resumo, no Abstract e no §9; resíduo no §8** → R2-4 | Resumo: "cai em quatro partidos de centro (PSD, MDB, PP e União)", e o Abstract diz o mesmo (os dois continuam equivalentes). §9: "no período do megabloco de 2025, quase sempre nada" (199/227 ✓). O §8 ainda diz "uma disciplina 'medida' que sobe justamente quando **a unidade dos partidos de centro cai**" |
| P2-9 heterogeneidade | **Resolvido** | "uma hipótese, que não testamos, é que essa heterogeneidade permita…" |
| P2-10 Apêndice A | **Parcial** → R2-8 | O tempo a frio agora tem fonte. Continuam "cada número do texto é uma referência a `resultados.json`" e a lista de entradas sem `discursos.parquet` e `validacao_falas.csv` |
| P2-11 detalhes do Método | **Não tratado** → R2-9 | IC geral de D só por votações; λ_d = 4; penalizações e estimação em duas etapas de M2b |
| P2-12 "ao longo do ano anterior" | **Não tratado** → R2-5 | §5.7 sem alteração |
| P2-13 megabloco "para a eleição da Mesa" | **Resolvido** | "formado em fevereiro de 2025, no início do biênio da nova Mesa": a data é coerente com os dados (`megabloco_data_ini` = 2025-02-11), e a frase não afirma mais a finalidade do bloco |
| P2-14 controles da coorte | **Não tratado** → R2-10 | 4 deputados com troca só antes de 01/04/2023 continuam entre os "nunca trocaram" (efeito desprezível) |

## R2.3 Procura de problemas introduzidos pelas mudanças

- **Referências cruzadas de figuras:** conferi as 13 menções "Figura n" e os 7 blocos de imagem. Há um erro: §5.1, "(Figura 1, coluna à direita)" (R2-1). Os demais estão certos: §5.1 → Fig. 1 (cobertura de D); §5.2 → Tabela 2 e Fig. 2; Figs. 3–7.
- **Definição nova de disciplina (§2):** "distinguimos *unidade* (votar junto) de *disciplina* (votar com o líder contra a própria preferência)". A medida D, chamada "disciplina à liderança" em todo o artigo, é a adesão à orientação **independentemente** da preferência (§4.1). Com a nova definição, D passa a medir algo diferente do conceito que leva o mesmo nome. Só o excesso de lealdade da §5.8 se aproxima do componente "contra a preferência" (R2-3).
- **Resumo × Abstract:** continuam equivalentes frase a frase, inclusive a nova lista de quatro partidos.
- **Números:** nenhum marcador foi acrescentado ou retirado de forma que mude valores. Renderizei de novo os marcadores com o `resultados.json` de `1da626c`, e o resultado é idêntico ao `artigo.md` versionado.
- **Bibliografia:** a remoção de `poole1997` e `kam2009` não deixou citação pendente: "McCarty, Poole e Rosenthal (2001)" aponta para `mccarty2001`.

## R2.4 Checklist dos 7 modos (rodada 2)

| Modo | Resultado | Evidência | Bloqueia? |
|---|---|---|---|
| 1 | CLEAR | Reprodução idêntica (R2.1); o diff do código só troca nomes de arquivos | não |
| 2 | CLEAR | As 31 obras existem; as atribuições a Carey e a Krehbiel estão dentro do verificado; Nokken retirado | não |
| 3 | CLEAR | Marcadores e reexecução idênticos | não |
| 4 | CLEAR | Sem mudança | não |
| 5 | CLEAR | Sem mudança | não |
| 6 | **CLEAR** (antes SUSPECTED) | O §3 declara que as duas codificações foram feitas pelo assistente de IA, sem segundo codificador. O "codificação manual" que sobra no Apêndice A é um resíduo de redação (R2-2), não uma descrição falsa do procedimento no Método | não |
| 7 | CLEAR | Sem mudança | não |

## R2.5 Lista de problemas (rodada 2)

| ID | Origem | Local | Problema | Correção sugerida |
|---|---|---|---|---|
| R2-1 | **novo** | §5.1, 1º parágrafo | "menos de 2%… (Figura 1, coluna à direita)": a coluna está na Figura 2 | "(Figura 2, coluna à direita)" |
| R2-2 | resíduo de P1-1 | Apêndice A, lista de entradas | "a codificação manual dos tipos de votação" | "a codificação dos tipos de votação pelo assistente de IA (`dados_aux/validacao_tipo_votacao.csv`) e a conferência das falas (`dados_aux/validacao_falas.csv`)" |
| R2-3 | **novo** | §2, "Disciplina, coesão e agenda" | A definição de disciplina como "votar com o líder contra a própria preferência" não é o que D mede | Acrescentar: "D mede a adesão à orientação, sem separar disciplina de concordância; o componente contra a preferência só é aproximado pelo excesso de lealdade (§5.8)". Ou definir disciplina como adesão à orientação e atribuir a Krehbiel apenas a ressalva |
| R2-4 | resíduo de P2-8 | §8, 1º parágrafo | "a unidade dos partidos de centro cai" | "a unidade de quatro partidos de centro cai" |
| R2-5 | P2-12 | §5.7, "Antes da troca" | "sobem 3,1 pontos ao longo do ano anterior à troca" | "entre a janela de 13 meses ou mais antes da troca e os três meses anteriores, as estimativas pontuais sobem 3,1 pontos" |
| R2-6 | resíduo de P2-2 | Fig. 2; `fig_disciplina` | IC de D do PSDB cortado em 76 | `ax.set_xlim(74, 100.5)` |
| R2-7 | P2-5 | Referências: Nicolau (2000) | A lista não tem páginas; o .bib tem 709–735 | Harmonizar (remover `pages` do .bib, ou "p. 709–735 [verificar]" na lista) |
| R2-8 | P2-10 | Apêndice A | "cada número do texto é uma referência a `resultados.json`" (há números escritos à mão); entradas omitidas | "cada resultado do texto…"; acrescentar `discursos.parquet` e `validacao_falas.csv` |
| R2-9 | P2-11 | §4.1–§4.3 | O IC geral de D é só por votações, sem dizer; λ_d = 4; M2b estimado em duas etapas (λ_r = 1, λ_s = 0,04) | Uma frase em cada ponto |
| R2-10 | P2-14 | §4.4 (coorte de 2026) | 4 deputados com troca antes de 01/04/2023 entre os "nunca trocaram" | "que não trocaram desde abril de 2023", ou excluí-los |

## R2.6 Marcas `[verificar]` e afirmações sem marca

- **Notas abertas, mantidas por instrução do usuário:** páginas e DOI de Nicolau (2000); lista completa dos instrumentos em Figueiredo e Limongi (1999); datas finas da base ministerial.
- **Afirmações não verificadas sem marca:** as da rodada 1 foram resolvidas (Carey, Nokken, finalidade do megabloco, tempo a frio). Não encontrei outra afirmação não verificada sem marca no texto alterado. A nova frase sobre Krehbiel está dentro do argumento verificado, mas tem o problema conceitual de R2-3.
