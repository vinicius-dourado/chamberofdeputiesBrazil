# Stage 6 — Registro do processo de criação do artigo (pipeline ARS)

**Artigo:** "Disciplina à liderança, unidade partidária e dissidência estruturada na Câmara dos Deputados (57ª Legislatura, 2023–2026)". O manuscrito é `artigo.md`, gerado por `analise.py` a partir de `artigo_fonte.md`.

## 1. Como o pipeline foi executado

O plugin Academic Research Skills (ARS) não estava instalado na sessão. O usuário indicou o repositório `imbad0202/academic-research-skills`, que foi clonado; a partir daí, os papéis dos agentes foram executados por subagentes que liam os arquivos `SKILL.md` e `agents/*.md` do repositório. Uma sessão anterior, ainda sem o plugin, havia deixado uma primeira versão de `analise.py` e um desenho v0.

| Stage | Papel ARS | Resultado | Registro |
|---|---|---|---|
| 1 RESEARCH | research_architect_agent; agente de bibliografia | Blueprint, com decisão `revise_before_freeze` sobre o v0; 26 referências verificadas | `stage1_blueprint.md`, `stage1_bibliografia.md` |
| 2 WRITE | orquestrador (análise e redação) | `analise.py` reescrito; manuscrito gerado a partir de marcadores | commits de c78105d em diante |
| 2.5 INTEGRITY | integrity_verification_agent | FAIL → FAIL → PASS WITH NOTES (3 rodadas) | `stage2_5_integridade.md` |
| 3 REVIEW | academic-paper-reviewer (EIC, 3 revisores, devil's advocate, síntese) | Major Revision (3 P0, 10 P1, 13 P2) | `stage3_revisao.md` |
| 4 REVISE | orquestrador; agente de bibliografia | Novas análises; texto reescrito e encurtado; resposta R→A→C | `stage4_resposta.md`, `stage4_bibliografia.md` |
| 3' RE-REVIEW | academic-paper-reviewer (re-review) | Major, com um único item obrigatório (R-1) | `stage3b_rerevisao.md` |
| 4' RE-REVISE | orquestrador | R-1 a R-9 tratados | commit 0467017 |
| 4.5 FINAL INTEGRITY | integrity_verification_agent (agente novo) | FAIL → FAIL → PASS WITH NOTES (3 rodadas) | `stage4_5_integridade_final.md` |
| 5 FINALIZE | — | Manuscrito final em Markdown (formato pedido no enunciado); não foram pedidos DOCX, PDF nem LaTeX | `artigo.md` |
| 6 PROCESS SUMMARY | orquestrador | Este documento | — |

## 2. Decisões do usuário

- **Pediu que o artigo fosse conduzido com o plugin ARS** e indicou o repositório quando o plugin não estava disponível.
- **Confirmou o Stage 1** ("1: sim") **e autorizou seguir sem parar nos checkpoints** ("2: pode seguir direto"). Por isso:
  - os checkpoints MANDATORY (decisões dos Stages 3 e 3', entrada do Stage 5) não foram submetidos a confirmação explícita;
  - os cartões dos revisores não foram aceitos pelo usuário, o que fica registrado como desvio do protocolo.
- **Pediu a retomada das tarefas** depois de interrupções por limite de uso ("Retomar as tarefas em segundo plano"; "Tente novamente"; "tentar novamente. coloquei credito").
- **A instrução original manda marcar com [verificar]** o que não puder ser conferido, em vez de inventar. As três marcas restantes (páginas de Nicolau, lista de instrumentos de Figueiredo e Limongi, datas finas da base ministerial) foram mantidas como notas abertas, e a verificação final as aceitou nesses termos.

## 3. Trajetória das conclusões (o que mudou e por quê)

| Afirmação | Versão inicial | Versão final | O que provocou a mudança |
|---|---|---|---|
| Disciplina em 2025 | "Sobe" (89,5% → 92,4%) | A alta é artefato do registro; U cai em PSD, MDB, PP e União | Blueprint (cobertura), revisão (P0-1) e re-revisão (R-1): falas e U |
| "8% de disciplina do PT no megabloco" | Afirmado ao research architect | Erro do orquestrador: 8% era a cobertura, e a taxa era 94,9% | Correção do research architect |
| Indisciplina estruturada | M2→M3 = 0,012 | M2b→M3 = 0,006 [0,003; 0,009] (comparador com a mesma estrutura) | Revisão (P0-2) |
| Rótulo da dimensão | "Governismo relativo" | "Eixo governo–oposição dentro do partido", com a ressalva sobre esquerda–direita | Revisão (P0-3) |
| Troca de partido | "Correção da filiação à preferência" → "adaptação" | Compatível com seleção e com ajuste; 6,5 p.p. na coorte de 2026 | Stage 2.5 (R2-P1-B) e revisão (P1-5) |
| Excesso de lealdade partido × Governo | 3,9 p.p.; "a maior parte é congruência de preferências" | Entre 4,2 e 17,1 p.p., conforme o contrafactual; base ministerial | Stage 2.5 (P1-5) e revisão (P1-6) |
| Placebo das fusões | Interpretado como teste | Não identificado em U; retirado | Stage 2.5 (P1-2) |
| Teste de posições embaralhadas (M3emb) | Citado na Discussão | Retirado: sem reajuste do modelo, não informa | Re-revisão (R-3) |
| Codificações de validação | "Codificadas manualmente" | Declaradas como feitas pelo assistente de IA, sem segundo codificador | Stage 4.5 (P1-1) |

## 4. Autoavaliação do processo (AI Self-Reflection)

- **Erros do orquestrador apanhados pelos agentes:**
  - o "8%" do PT, que era cobertura e não taxa;
  - o R² de 0,998, sem sentido;
  - a decomposição da variância nula por construção;
  - a atribuição do "racha" de PSB e PDT;
  - o "excesso maior no PSOL";
  - a datação das fusões;
  - a afirmação "a alta não vem da composição";
  - o placebo não identificado;
  - a descrição da codificação como "manual".

  Todos foram corrigidos e estão registrados nos relatórios. Dois padrões se repetem: confiança excessiva em leituras interpretativas, como seleção, adaptação e congruência de preferências, e números ou atribuições escritos à mão sem rastreio. O esquema de marcadores ligados a `resultados.json` resolveu o segundo; o primeiro dependeu dos revisores.
- **Modos de falha do checklist do ARS:**
  - Modo 1 (bug de implementação): SUSPECTED em duas rodadas, por colinearidade no estudo de evento e pelo cache sem impressão digital dos dados; ficou CLEAR na rodada final.
  - Modo 6 (fabricação de metodologia): SUSPECTED, porque o Método descrevia procedimentos que o código não fazia e a codificação foi apresentada como manual; ficou CLEAR.
- **Independência limitada:**
  - os pareceres do Stage 3 foram escritos por um mesmo modelo num único contexto;
  - a codificação de validação foi feita pelo mesmo assistente que fez a análise.

  Concordâncias entre esses papéis não valem como corroboração independente.
- **Itens não feitos (declarados no artigo):**
  - validação temporal dos pontos ideais;
  - composição oficial dos blocos;
  - segundo codificador humano;
  - depósito com DOI.

## 5. Avaliação da colaboração (6 dimensões, 1–100)

| Dimensão | Nota | Evidência |
|---|---|---|
| Clareza do pedido | 85 | Enunciado detalhado, com perguntas, análises esperadas, referências de partida e limitações a tratar |
| Engajamento nos checkpoints | 40 | Confirmou o Stage 1 e delegou o resto ("pode seguir direto"); não revisou os cartões de revisores nem as decisões editoriais |
| Vigilância crítica | 50 | Instrução explícita de honestidade ("relate com honestidade o que não se sustenta") e de marcar o não verificado; não houve leitura própria dos rascunhos durante a sessão |
| Delegação | 30 (alta delegação) | Quase todo o trabalho substantivo ficou com o assistente e os subagentes |
| Contribuição de domínio | 60 | Avisos técnicos herdados (partido atual × na data; vazamento de sexo nos discursos) e escolha do plugin |
| Resolução de impasses | 70 | Retomou as tarefas depois das interrupções por limite de uso |

**Recomendação ao usuário.** Antes de qualquer submissão, leia o artigo e os relatórios dos Stages 3 e 3'. Faça uma segunda codificação humana das amostras de validação e confira as três marcas [verificar].
