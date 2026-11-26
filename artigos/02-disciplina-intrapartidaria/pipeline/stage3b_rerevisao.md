# Stage 3' — Re-revisão (academic-paper-reviewer, modo `re-review`)

**Manuscrito revisado:** `artigos/02-disciplina-intrapartidaria/artigo.md` (commit 4370c4e, branch `claude/artigo-2-disciplina-intrapartidaria`), com `artigo_fonte.md`, `resultados.json` e `analise.py`.
**Versão anterior:** `git show 93b03d6:artigos/02-disciplina-intrapartidaria/artigo.md`.
**Roadmap de referência:** `pipeline/stage3_revisao.md` (Rodada 1, Major Revision).
**Resposta aos revisores:** `pipeline/stage4_resposta.md`, lida só na Fase 2B.
**Bibliografia nova:** `pipeline/stage4_bibliografia.md`.
**Rodada:** 2. **Data:** 26/11/2026.

## Registro do juiz e desvios do protocolo

- **O contrato de três portões não foi executado como especificado.** Não houve `input_manifest` 1.1, nem `revision-roadmap/1.0` em formato de máquina, nem sidecar `author-adjudication/1.0`, nem `revision-evidence-bundle`, nem patch/apply-report 1.3. Os scripts `check_re_review_synthesis.py` e `review_panel_provenance.py` não rodaram. Pela regra G0, uma execução estrita terminaria em `[RE-REVIEW-ABORT: manifest_incomplete]`. O que segue é a aplicação manual da lógica do protocolo e **não equivale** a uma decisão validada pelo checker.
- **Ordem das fases.** A ordem foi respeitada:
  1. Fase 1: os critérios de cada item foram escritos e gravados num arquivo de rascunho antes de abrir o manuscrito revisado e a resposta.
  2. Fase 2A: veredictos pela evidência no manuscrito, no código e nos dados, sem a carta de resposta.
  3. Fase 2B: comparação com a carta.

  Os três portões rodaram no mesmo contexto e com o mesmo modelo, e não houve isolamento técnico entre eles. O mesmo modelo escreveu o roadmap da Rodada 1, de modo que juiz e autor dos critérios são correlacionados.
- **Configuração dos revisores.** Os cartões da Rodada 1 foram reaproveitados (continuidade da régua), mas **o usuário nunca os aceitou** (ver `stage3_revisao.md`, Nota de execução). A carta de resposta diz que o usuário autorizou "seguir sem parar nos checkpoints". Isso é afirmação do autor, tratada como dado, e não muda a situação dos cartões. `[ROUTING: card_mapped; cards não confirmados pelo usuário]`.
- **Status.** `calibration_status: NOT_CALIBRATED`. Cross-model desligado. Não há alegação de independência.

---

## Fase 1 — Critérios comprometidos (antes de ver a revisão)

Os critérios abaixo operacionalizam o que o roadmap da Rodada 1 pediu e não acrescentam exigências. O texto completo está em `scratchpad/fase1_criterios.md` e foi copiado aqui sem alteração de conteúdo.

| Item | Totalmente atendido se… | Parcialmente atendido se… | Piorou se… |
|---|---|---|---|
| P0-1 | (a) Orientações verificadas numa fonte primária para uma amostra de votações de 2025 com orientação vazia, com taxa de concordância. (b) Composição oficial dos blocos usada, ou inferência validada. (c) Resumo, §1, §7, §8, §9 e título da Fig. 2 sem afirmações comportamentais sem evidência. (d) Tab. 2 com o nº de votações da D própria, suprimindo taxas com < 10 | Só reescrita sem verificação, ou verificação sem correção do texto | Novas afirmações comportamentais sem base, ou nova fonte de orientação sem validação nem viés reportado |
| P0-2 | M2b estimado. M2b→M3(L) com IC. Teste de embaralhamento ou equivalente. Validação temporal ou reinterpretação explícita como imputação. M0→M1 reinterpretado. Tese rebaixada se o ganho sumir | Falta um dos elementos ou o texto não foi ajustado | Comparador ainda desigual, com linguagem mais forte |
| P0-3 | Nome neutro ou teste que separe governo de esquerda–direita. Quantificado quanto é eixo global, com teste de estrutura além dele. "Confirma E4" retirado. Pares espelhados da Tab. 11 comentados | Renomeia sem teste (resíduo should_fix) ou testa sem renomear | Afirma governismo com mais força |
| P1-1 | Corpo com cerca de 8–9 mil palavras, até 6 tabelas e 5 figuras no corpo, sem artefatos internos, Resumo de 200–250 palavras, numeração em ordem | Parte disso | — |
| P1-2 | Critério de falha quantitativo para E1–E5, declarado como posterior ao P1. E5 como contraste FL × Carey. "Confirma" trocado por "compatível" | Parte disso | — |
| P1-3 | Rice com m comum para todos os partidos, ranking completo, texto de E2 coerente | — | — |
| P1-4 | Distância padronizada por ajuste, efeito por DP, metades separadas, perdas informadas, "preferência" reformulada | Parte disso | — |
| P1-5 | Estimador robusto à adoção escalonada, coortes separadas, teste conjunto da pré-tendência, taxa de referência, sensibilidade a λ_δ | Parte disso | — |
| P1-6 | Base ministerial datada, IC e nº de votações por partido, contrafactual (ii) sem a esquerda, Resumo com limite crível | Parte disso | — |
| P1-7 | Log-loss com bootstrap de duas vias (ou ambos os de uma via). Dispersão com ≥ 500 réplicas ou paramétrica, sem IC degenerado. ICs individuais recalculados ou ressalvados | Parte disso | — |
| P1-8 | U como medida principal entre partidos, U por federação, conjunto fixo de partidos na série, teste bloco × partido ou declaração de que é inviável | Parte disso | — |
| P1-9 | Literatura listada incorporada e discutida, três "[verificar]" resolvidos, novas referências verificadas | Parte disso | — |
| P1-10 | Ausência em votações divididas × unidas, PLP, discussão ou aplicação de não resposta não ignorável | Parte disso | — |
| P2-1 a P2-13 | Forma leve (should_fix): o que o roadmap pediu foi feito no manuscrito | — | Degradação em relação ao original |

`[CONTRACT-ACKNOWLEDGED]`

---

## Fase 2A — Veredictos pela evidência (sem a carta)

### P0 (must_fix)

**P0-1 — Registro × comportamento: PARTIALLY_ADDRESSED** (resíduo **must_fix**)
- **O que mudou:** foi criada uma reconstrução das orientações faladas a partir das transcrições (`orientacoes_faladas`). A §5.1 e o Resumo agora dizem que o registro do megabloco não tem linhas do PL nem da federação do PT (0 de 227). "Orientam onde estão unidos" foi retirado. A §7 e a §8 tratam a orientação vazia como possível limite do registro. A Fig. 2 omite D com cobertura < 20%, e o título deixou de dizer "é um artefato". Há um parágrafo para usuários dos dados (§8).
- **Evidência:** `text: §5.1 ¶2 "nenhuma linha própria do PL ou da federação do PT. Nas transcrições, porém, esses partidos aparecem orientando"`; `text: §5.1 ¶4 "Orientação vazia, portanto, nem sempre quer dizer que a liderança não orientou"`; `figure: Fig. 2 — 2025S1 omitido`.
- **O que falta:**
  - **(a) A medida pelas falas não foi validada onde é usada, e há evidência de erro grande justamente ali.** A concordância de 94,3% foi medida fora do megabloco, contra o registro. Dentro do megabloco, a D pela fala do PT é de 91,2% (`fala_mb_D_PT`, 16 votações). Consultei a U nas mesmas votações do megabloco (`votos.parquet`, cálculo aproximado do revisor): o PT tem 98,1%. Para o PL, a D pela fala é de 80,5%, contra U de 89,0%. Fora do megabloco, D e U desses dois partidos quase coincidem (PT 98,7 × 98,3; PL 90,5 × 89,3). Uma diferença de 7 a 9 pontos entre D pela fala e U, em partidos de bancada quase unânime, indica erro de associação fala→votação, não indisciplina. A "correção" de 4,1 pontos, chamada de "ruído" mas que é um viés sistemático, vem de outro contexto e subestima esse erro. A frase do Resumo "medida pelas orientações faladas, [a disciplina] cai" e a da §8 "pelas falas e pela unidade, ela cai" ficam, portanto, sem base no que diz respeito às falas. **U** sustenta uma queda, mas concentrada no centro: MDB 80,1 × 86,1, PSD 83,2 × 88,3 e União 75,8 × 81,7 nas votações do megabloco × fora dele, enquanto PL e PT ficam estáveis.
  - **(b)** A composição oficial dos blocos não foi usada nem validada.
  - **(c)** A Tab. 2 continua mostrando "D própria (n = votos)", com MDB 94,1 (34) e REPUBLICANOS 100,0 (39), que vêm de uma única votação cada. O pedido de mostrar o número de votações e suprimir as taxas com < 10 não foi atendido.
- **Por que o resíduo é must_fix:** o item (a) é o que P0-1 pedia (verificar a orientação no contexto do megabloco), e a solução introduziu uma afirmação quantitativa no Resumo que os próprios dados contradizem.

**P0-2 — Comparador M2 desigual: PARTIALLY_ADDRESSED** (resíduo should_fix)
- **O que mudou:** M2b foi implementado (`ajustar_lealdade_b`) como σ(z^{M1} + s_j·ρ_r·d_pj), com ρ por período e escala por votação. É o que foi pedido. M2b→M3 = 0,0058 [0,0029; 0,0086] (Tab. 5, Fig. 4). A validação passou a ser chamada de imputação (§4.3, §7), e M0→M1 foi reinterpretado (§5.4 ¶1). O texto rebaixa a tese: "a indisciplina tem estrutura, mas pouca" (§8).
- **Evidência:** `table: Tab. 5 — M2b 0,2583; M3 0,2525`; `text: §5.4 "Direção da dissidência além da propensão, com a mesma estrutura de parâmetros (M2b→M3): 0,006"`.
- **O que falta:**
  - O teste de embaralhamento (M3emb) foi implementado **sem reajuste**: os vetores x de M3 são permutados entre colegas, e as cargas e os g estimados com as posições verdadeiras são mantidos (`validacao_cruzada`, linhas 1026–1034). O resultado (log-loss 0,67) é muito pior que o de M1 (0,28), ou seja, pior do que não ter posição individual nenhuma. O teste mostra que posições erradas com cargas calibradas para as certas dão previsões confiantes e erradas, e **não** que a direção acrescente algo além da propensão. O pedido era trocar o sinal preservando |x_r|, ou reajustar o modelo. A frase da §8 "não é intercambiável entre colegas" depende desse teste e deveria sair, ou o teste deveria ser refeito.
  - A validação temporal não foi feita, o que está declarado (§7). Pelo critério, a reinterpretação como imputação basta.
  - O título mantém "dissidência estruturada" para um ganho de 0,006 por voto. É aceitável porque o IC exclui zero, mas a §8 ("é estável… prevê o voto fora da amostra") vai um pouco além do que foi testado (ver NI-1).

**P0-3 — Rótulo da dimensão: PARTIALLY_ADDRESSED** (resíduo should_fix)
- **O que mudou:** o rótulo é agora "eixo governo–oposição recortado dentro de cada partido", com a ressalva sobre esquerda–direita (§5.5 ¶1). A correlação de 0,94 com a posição global relativa está reportada, assim como "o que vai além dele é pequeno" (§5.5 ¶2). "Confirma" virou "se sustenta, no sentido de compatibilidade".
- **Evidência:** `text: §5.5 "Sob um governo de esquerda, porém, o eixo governo–oposição não se separa de um eixo esquerda–direita"`.
- **O que falta:** nenhum teste separa governo de esquerda–direita, nem há teste de cargas por partido (DIF). Os pares espelhados da Tab. 6 (PL 1708/2025 e PL 3469/2024 aparecem nos dois polos, como mérito/destaque e requerimento) continuam sem comentário. Pelo critério da Fase 1, renomear sem testar equivale a resíduo should_fix.

### P1 (must_fix)

| Item | Veredicto | Evidência (manuscrito revisado) | O que falta (classe) |
|---|---|---|---|
| P1-1 Extensão e foco | PARTIALLY | Corpo com cerca de 6.400 palavras sem tabelas; Resumo com 205; artefatos internos levados ao Apêndice C; numeração em ordem | Ainda há 11 tabelas e 7 figuras no corpo: temas (Tab. 4), lista nominal de dissidentes (Tab. 9) e pivôs (Tab. 10) continuam no corpo. "Um de sete trabalhos" continua na §1 ¶3 (should_fix) |
| P1-2 E1–E5 | PARTIALLY | §2: critérios numéricos de falha; E5 como FL × Carey | Os limiares (U > 3 p.p.; ρ < 0,8; correlação < 0,5) foram fixados **na revisão, já conhecidos os resultados** (1,6; 0,99; 0,90), mas o texto diz que "E3 a E5 foram especificadas antes das análises que as testam". As expectativas, sim; os limiares, não. Declarar que são posteriores (should_fix) |
| P1-3 Rice com m comum | FULLY | §4.1 e §5.3: m = 3 para os 16 partidos, ρ = 0,99; Tab. 2 com coluna m = 3 | A Fig. 3 ainda mostra só m = 10 (consider) |
| P1-4 Distância | PARTIALLY | `distancia_fora_periodo` divide pelo DP da dim1 de cada ajuste; 22,1 p.p. por DP; "distância espacial, e não preferência" (§5.6) | Metades não reportadas separadamente; perdas por falta de período no outro biênio não informadas (consider) |
| P1-5 Estudo de evento | PARTIALLY | §5.7: coorte de 2026 com controles que nunca trocaram (6,5 p.p.; IC 2,4–10,5); teste conjunto da pré-tendência | p = 0,096 (completo) e 0,103 (coorte), descritos como "nenhum coeficiente se distingue" e "sem pré-tendência conjunta", o que é limítrofe a 10%. A estimativa completa (11,1) vem antes, embora o TWFE seja justamente a especificação problemática; a da coorte é cerca de 40% menor, e em D é nula. Coortes anteriores não foram separadas; não há sensibilidade a λ_δ nem taxa da janela de referência (should_fix) |
| P1-6 Partido × Governo | PARTIALLY | §4.4 e Apêndice C: base pelos partidos com ministério; independentes separados; (ii) sem a esquerda: 2,6–11,2; Resumo sem número | A base **não é datada**: "filiação em qualquer momento do período" (`BASE_MINISTERIAL` fixo), o que mantém União e PP após a saída anunciada em set/2025 (datas ainda "[verificar]" no Apêndice C). IC por partido existe em `resultados.json` (`div_*_lo`), mas não aparece na Fig. 7 nem no texto. O nº de votações por partido só aparece para o PT (should_fix) |
| P1-7 Inferência | PARTIALLY | Tab. 2 com bootstrap de duas vias (500); Tab. 8 com EP e viés, sem IC degenerado; Tab. 9 em DP | Diferenças de log-loss ainda só com bootstrap de deputados (§4.3, Fig. 4). ICs da Tab. 9 ainda com 100 réplicas de votações. Legenda da Fig. 1 diz "bootstrap de votações" (should_fix) |
| P1-8 Construto D/U | PARTIALLY | §5.2: comparação entre partidos em U; U por federação (98,1; 97,5; 82,1) | Não há teste bloco × partido nem declaração de inviabilidade; série de U sem conjunto fixo de partidos (consider) |
| P1-9 Literatura | PARTIALLY | Nove obras novas, verificadas em `stage4_bibliografia.md` | A maioria é citada numa frase. Não entraram: Limongi e Figueiredo (1995), Raile–Pereira–Power, Carey–Reinhardt, Melo, Hix (2002) e Hix–Noury–Roland, Aldrich–Montgomery–Sparks, Rosas–Shomer–Haptonstahl, Lewis–Poole e Owen. Continuam 2 "[verificar]" no texto, mais 1 no Apêndice C. A §2 afirma que Cheibub, Figueiredo e Limongi (2009) "mostram que partidos, e não governadores, organizam o comportamento legislativo", mas a verificação bibliográfica diz que "a conclusão substantiva não foi confirmada… [verificar]" (should_fix; ver NI-3) |
| P1-10 Ausência | PARTIALLY | §5.2: limite inferior de D (73,1%; ρ = 0,91) e PEC | Faltam a comparação de ausência em votações divididas × unidas e a PLP (consider) |

### P2 (should_fix, forma leve)

| Item | Veredicto | Evidência |
|---|---|---|
| P2-1 Fig. 2 | FULLY | D omitido < 20%; título neutro |
| P2-2 Contagens Tab. 1 × 3 | FULLY | Nota da Tab. 3 |
| P2-3 Unidades da Tab. 9 | FULLY | IC em DP do partido |
| P2-4 N das células e minoria ≥ 10% | FULLY | §4.3 (64%), §5.4 |
| P2-5 Resultados na Tab. 6 | FULLY | "texto mantido" |
| P2-6 "P5" e siglas | FULLY | Apêndice B; MPL, EP e UF definidos |
| P2-7 Troca antes × depois | FULLY | Tab. 7 |
| P2-8 M5→M4 fora da Fig. 4 | FULLY | Fig. 4 |
| P2-9 Trocas como evidência modesta | FULLY | §5.5, último parágrafo |
| P2-10 Validação do classificador | FULLY | §3: 94,1%. O texto diz "119 votações" e o Apêndice B diz "120" (NI-2) |
| P2-11 Usuários dos dados | FULLY | §8 ¶1 |
| P2-12 Disponibilidade e versões | PARTIALLY | Versões no Apêndice A; não há DOI nem depósito |
| P2-13 Confirmatório × exploratório | FULLY | Apêndice B |

`should_fix_addressed_rate` = 13/13 (100%).

### Problemas novos (congelados aqui)

O guarda de metas foi aplicado. Problemas que derivam de um item do roadmap foram tratados no próprio item: o erro da medida pelas falas está em P0-1(a), o M3emb sem reajuste em P0-2, os limiares posteriores em P1-2 e a pré-tendência limítrofe em P1-5. Abaixo ficam só os que não correspondem a nenhum item.

| ID | Atribuição | Gravidade | Problema | Âncora |
|---|---|---|---|---|
| NI-1 | regressão | Minor | A §8 diz que a direção individual "é estável". A estabilidade não foi testada: os pontos são fixos por período, e a validação temporal não foi feita (§7) | `text: §8 ¶2 "A direção, porém, conta: é estável, não é intercambiável entre colegas e prevê o voto fora da amostra"` |
| NI-2 | regressão | Minor | Inconsistências pequenas: 119 (§3) × 120 (Apêndice B) votações codificadas; legenda da Fig. 1 ("bootstrap de votações") × nota da Tab. 2 (duas vias); a §5.3 centra em m = 3, mas a Fig. 3 mostra m = 10 | `text: §3 "numa amostra estratificada de 119 votações"` × `text: Apêndice B "Amostra estratificada de 120"` |
| NI-3 | regressão | Minor | Conteúdo de citação afirmado sem confirmação: Cheibub, Figueiredo e Limongi (2009) e Nokken (2000), este último resumido a partir da tese segundo `stage4_bibliografia.md` | `text: §2 "Cheibub, Figueiredo e Limongi (2009) mostram que partidos, e não governadores, organizam o comportamento legislativo"` |
| NI-4 | regressão | Minor | O método de associação fala→votação tem vieses previsíveis que não foram discutidos (§3): a regex aceita "vota"/"encaminha", que também aparecem em falas de debate, e lê só os 600 primeiros caracteres; a fala é ligada à **primeira votação nominal** em até 45 min, de modo que orientações dadas antes de votações simbólicas caem na nominal seguinte, que pode ser de outro item; e, quando há duplicatas, fica a última. O efeito quantitativo é o de P0-1(a); aqui o problema é a falta de descrição e discussão desses vieses | `text: §3 "associamos cada uma à primeira votação nominal registrada até 45 minutos depois"` |

Nenhum dos problemas novos é Critical ou Major, e nenhum pede escalonamento.

`[EVIDENCE-COMMITTED]`

---

## Fase 2B — Comparação com a carta de resposta

| Item | O que a carta afirma | O manuscrito confirma? | Ajuste do veredicto |
|---|---|---|---|
| P0-1 | "A conclusão sobre 2025 se inverte e se reforça… A disciplina caiu em 2025" | Em parte. U confirma uma queda no centro; a D pela fala, como medida, não confirma (ver o resíduo) | Nenhum |
| P0-1 | Conferência manual "substituída pela validação sistemática das falas contra o registro (563 casos)" | A validação existe, mas fora do contexto em que a medida é usada. A substituição não atende o critério (a) | Nenhum |
| P0-1 | Composição oficial dos blocos "não está nos Dados Abertos baixados" | É uma justificativa, não uma refutação; não traz evidência no manuscrito | Nenhum |
| P0-2 | "M3emb piora a log-loss em 0,42" | Correto, mas o teste é pouco informativo (sem reajuste) | Nenhum |
| P0-2 | Validação temporal impossível porque "o estimador não permite fixar pontos" | Explicação plausível e declarada na §7; o critério já aceitava a reinterpretação como imputação | Nenhum |
| P1-6 | "IC e nº de votações por partido" | **Não está no manuscrito**: os ICs estão só em `resultados.json`, e o nº de votações aparece só para o PT | Nenhum; divergência entre a carta e o manuscrito |
| P1-6 | "Base definida pela composição ministerial" | Sim, mas é estática ("em qualquer momento do período") | Nenhum |
| P1-9 | "Nove obras verificadas e incorporadas" | Verificadas quanto à existência; o conteúdo de duas está com "[verificar]" no relatório bibliográfico | Nenhum |
| Demais | Correspondem ao manuscrito | — | Nenhum |

Nenhuma justificação válida nem indicação de evidência que a Fase 2A não tivesse visto. **Nenhum veredicto mudou entre 2A e 2B** (sem registros de ajuste; G1 não dispara).

`[MATRIX-COMMITTED]`

---

## Decisão

### **Major Revision** (de escopo restrito; volta ao Stage 4')

**Derivação, aplicada manualmente, sem o checker:**
- G0: na execução estrita, abortaria por falta de manifesto. Declarado como desvio.
- G1 e G2: não disparam.
- B1 a B3: não disparam. Nenhum must_fix está NOT_ADDRESSED, MADE_WORSE ou CANNOT_VERIFY, e não há regressão Major.
- **B4 dispara:** P0-1 está PARTIALLY_ADDRESSED com resíduo **must_fix**.
- Sem B4, valeria B5 (Minor): os demais must_fix estão parciais com resíduo should_fix ou consider, e a taxa de should_fix é de 100%.

**Justificativa.** A revisão foi séria e resolveu a maior parte do roadmap:
- M2b com a estrutura de M3;
- reinterpretação da validação como imputação;
- Rice com m = 3;
- distância padronizada;
- coorte de 2026;
- U por federação;
- limite inferior com ausências;
- texto encurtado.

O artigo está muito mais perto de submeter do que na Rodada 1. O bloqueio que resta vem da própria correção de P0-1. A nova medida, por orientações faladas, sustenta no Resumo e na §8 que a disciplina "cai" em 2025, mas nas mesmas votações ela dá ao PT 91,2% de D contra 98,1% de U. É um sinal de erro de associação de 7 a 9 pontos, que a calibração de 4,1 pontos não capta. A conclusão qualitativa sobrevive, porque U mostra queda no centro, mas a evidência atribuída às falas não. Corrigir isso é barato. Se o resíduo R-1 abaixo for resolvido e os demais forem tratados ou justificados, a decisão esperada na próxima rodada é Minor ou Accept.

### Roadmap residual (curto)

**must_fix**
- **R-1 (P0-1a).** Validar a medida pelas falas **no megabloco**.
  - Comparar, partido a partido e nas mesmas votações, a D pela fala com U.
  - Conferir à mão uma amostra de cerca de 50 associações fala→votação (texto da fala, horário, votação associada, item em pauta) e informar a taxa de erro.
  - Restringir a extração a "orienta", ou reportar a medida com e sem "vota/encaminha".
  - Reescrever o Resumo, a §1 ¶2, a §5.1 ¶2–3 e a §8 ¶1 de modo que a queda de 2025 se apoie em **U**: no centro, MDB, PSD e União caem 5 a 6 pontos; PL e PT ficam estáveis. A D pela fala deve aparecer como evidência ruidosa, de que os partidos orientaram, e não como medida de nível.
  - Trocar "ruído de 4,1 pontos" por "viés de −4,1 pontos fora do megabloco".
  - Descrever na §3 os vieses do método de associação (NI-4).

**should_fix**
- **R-2 (P0-1c).** Tab. 2: informar o nº de **votações** da D própria e suprimir as taxas com < 10.
- **R-3 (P0-2).** Refazer o M3emb com troca de sinal que preserve |x|, ou com reajuste; se não for refeito, retirar "não é intercambiável entre colegas" e "é estável" da §8 (NI-1).
- **R-4 (P1-2).** Declarar na §2 que os limiares de falha foram fixados na revisão, depois de conhecidos os resultados.
- **R-5 (P1-5).** Dar destaque à estimativa da coorte (6,5) ou mostrar as duas lado a lado. Descrever p ≈ 0,10 como pré-tendência limítrofe. Informar a taxa de desvio na janela de referência.
- **R-6 (P1-6).** Base ministerial datada, com saídas e entradas pela data, ou ao menos a robustez sem União e PP a partir de set/2025. ICs e nº de votações por partido na Fig. 7 ou no texto, como a carta diz que foi feito.
- **R-7 (P1-7).** Bootstrap de votações (ou de duas vias) também para as diferenças de log-loss. Corrigir a legenda da Fig. 1.
- **R-8 (P1-9, NI-3).** Confirmar no texto original o conteúdo atribuído a Cheibub, Figueiredo e Limongi (2009) e a Nokken (2000), ou suavizar. Resolver os "[verificar]" restantes. Considerar Limongi e Figueiredo (1995), Hix (2002), Aldrich, Montgomery e Sparks (2014) e Rosas, Shomer e Haptonstahl (2015).
- **R-9 (P1-1).** Levar as Tabs. 4, 9 e 10 ao apêndice e retirar "um de sete trabalhos".

**consider**
- Fig. 3 com m = 3.
- Coerência de 119 × 120 (NI-2).
- Metades da distância separadas.
- PLP e ausência em votações divididas × unidas.
- Comentar os pares espelhados da Tab. 6.
- DOI e depósito do código.
