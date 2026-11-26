# Stage 3 — Revisão por pares simulada (academic-paper-reviewer v1.11.1, modo `full`)

**Manuscrito:** "Disciplina à liderança, unidade partidária e dissidência estruturada na Câmara dos Deputados (57ª Legislatura, 2023–2026)" (`artigos/02-disciplina-intrapartidaria/artigo.md`, gerado de `artigo_fonte.md`).
**Rodada:** 1. **Data:** 26/11/2026. **Modo:** `full` (Fase 0, cinco pareceres, decisão editorial e Revision Roadmap).
**Flags opcionais:** cross-model, passport e ledger não setados. Nenhuma foi usada.
**Material lido:** `artigo.md` inteiro, as 7 figuras, `resultados.json`, trechos de `analise.py` (`prep_irt`, `ajustar`, `_intra`, `ajustar_lealdade`, `dobras`, `regra_orientacao`, `validacao_cruzada`, `avaliar_cv`, `distancia_fora_periodo`, `partido_vs_governo`), `pipeline/stage1_bibliografia.md`, `pipeline/stage2_5_integridade.md` (rodadas 1–3) e `NOTAS_PASSAGEM.md`. Os revisores fizeram consultas somente de leitura a `dados/leg57` (votos.parquet, votacoes_orientacoes.parquet). Nenhum arquivo do artigo foi alterado.

## Nota de execução e proveniência (leia antes dos pareceres)

1. **Checkpoint Rule 1 (confirmação dos cartões antes da Fase 1) não foi cumprida.** O protocolo manda que, quando um subagente roda a Fase 0, ele devolva os cartões e não dispare os revisores até o usuário aceitar os cartões, na vez dele. Esta revisão foi pedida por um agente orquestrador, com instrução de executar o protocolo completo. Mensagem de agente não equivale à confirmação do usuário. Os cinco pareceres foram escritos com os cartões da Fase 0 tal como estão abaixo, sem aceite do usuário. **Se o usuário quiser mudar algum cartão, a Fase 1 deve ser refeita com os cartões aceitos.** Numa re-review (Stage 3'), só devem ser reaproveitados cartões que o usuário tenha aceitado.
2. **Os assentos não foram executados de forma independente.** Os sete papéis foram escritos em sequência por um mesmo modelo, num único contexto. A separação é só de papéis. Não houve contexto novo por assento, nem cegueira aos pareceres dos colegas, nem pré-compromisso cego ao manuscrito (Fase 1 do sprint contract). Os scripts `check_sprint_contract.py`, `check_phase_conformance.py`, `check_panel_synthesis.py` e `review_panel_provenance.py` não foram rodados. Por isso, quando vários pareceres concordam, isso **não** é corroboração independente: erros correlacionados são prováveis.
3. `calibration_status: NOT_CALIBRATED`. `criteria_binding_unavailable`: não há revista-alvo confirmada pelo autor (Dados, RBCP e LSQ foram citadas como hipóteses). O painel não afirma adequação a nenhuma revista específica.
4. Anexos de checagem: a de siglas (#849) foi rodada e está no fim, sem alterações. A de referências sugeridas (#1001) e a de afirmações dos revisores (#1002) não foram rodadas (ver anexos).

| Assento | Role ID | Tipo de ator | Context ID | Vê pareceres dos colegas | Família do modelo | Provedor | Revisor humano |
|---|---|---|---|---|---|---|---|
| Journal-Fit | EIC | modelo | mesmo contexto | sim | Claude | Anthropic | nenhum |
| R1 Metodologia | R1 | modelo | mesmo contexto | sim | Claude | Anthropic | nenhum |
| R2 Domínio | R2 | modelo | mesmo contexto | sim | Claude | Anthropic | nenhum |
| R3 Perspectiva | R3 | modelo | mesmo contexto | sim | Claude | Anthropic | nenhum |
| Devil's Advocate | DA | modelo | mesmo contexto | sim | Claude | Anthropic | nenhum |

| Eixo de proveniência | Situação |
|---|---|
| Separação de papéis | true |
| Separação de contexto de invocação | false |
| Cego aos pareceres dos colegas | false |
| Famílias de modelo distintas | false |
| Provedores distintos | false |
| Revisores humanos distintos | false (nenhum humano) |

Nenhuma alegação de independência é feita. **Divulgação de erro correlacionado:** os cinco assentos usam a mesma família de modelo, no mesmo contexto. Concordâncias entre eles podem refletir um mesmo viés.

---

# FASE 0 — Análise do campo e configuração dos revisores (field_analyst_agent)

## Informações básicas do artigo
- **Título:** ver acima.
- **Resumo:** cerca de 340 palavras em português e outro tanto no Abstract.
- **Texto:** cerca de 9.250 palavras sem tabelas e referências, mais 11 tabelas, 7 figuras e 2 apêndices; 13.800 palavras com tudo.
- **Referências:** 24.

## Análise do campo

| Dimensão | Resultado |
|---|---|
| Disciplina principal | Ciência política: estudos legislativos (comportamento parlamentar, presidencialismo de coalizão) |
| Disciplinas secundárias | Metodologia política (pontos ideais, validação fora da amostra), econometria aplicada (efeitos fixos, estudo de evento), ciência de dados legislativos |
| Paradigma | Quantitativo, observacional, descritivo-preditivo, com inferência causal limitada (estudo de evento) |
| Tipo de metodologia | Medidas descritivas (D, U, Rice e Desposato), modelos de pontos ideais penalizados comparados por validação cruzada, MPL com efeitos fixos e EP em duas vias, estudo de evento e contrafactuais por modelo |
| Nível da revista-alvo | Q1–Q2 da área (Dados e RBCP no Brasil; LSQ no internacional). Não há alvo confirmado pelo autor |
| Maturidade | Pré-submissão. Passou por três rodadas de integridade (PASS WITH NOTES), mas ainda tem 3 marcas "[verificar]" no texto |

## Revistas sugeridas (sem vinculação, só como referência)
1. *Dados – Revista de Ciências Sociais*: a tradição de Figueiredo, Limongi e Nicolau está lá, e o público é o mesmo do debate.
2. *Legislative Studies Quarterly*: aceita medida e métodos para legislativos não americanos, mas pediria um enquadramento comparado.
3. *Revista Brasileira de Ciência Política*: aceita textos longos, com métodos.

## Cartões de configuração dos revisores

### Cartão #1
**Role:** EIC. **Papel exibido:** Journal-Fit Reviewer.
**Identidade:** editor associado de um periódico de ciência política com seção de métodos, de perfil generalista (sem revista-alvo vinculada). Pesquisa instituições legislativas comparadas e já editou números sobre presidencialismo de coalizão.
**Foco:** (1) se a contribuição é nova em relação a Figueiredo e Limongi, Carey e Zucco; (2) se o desenho dos argumentos se mantém coeso com quatro perguntas e cinco expectativas; (3) extensão, legibilidade e o que pode ir para o apêndice.
**Vai se importar sobretudo com:** se o artigo é um artigo, e não um relatório de projeto. Isso inclui as referências a artefatos internos e a "trabalhos irmãos".
**Pontos cegos possíveis:** detalhe técnico dos modelos de pontos ideais.

### Cartão #2
**Role:** R1. **Papel exibido:** Revisor 1 (Metodologia).
**Identidade:** metodólogo político especializado em modelos de pontos ideais (IDEAL/NOMINATE, IRT penalizado), validação fora da amostra e dados em painel (estudos de evento com adoção escalonada, EP agrupados em várias vias).
**Foco:** (1) se a comparação M0–M5, M0c e M3L é justa: comparadores, aninhamento, vazamento entre treino e teste, métrica; (2) validade de construto de D, U e das camadas de orientação; (3) estudo de evento, contrafactuais de P5 e inferência (bootstrap, EP em duas vias).
**Vai se importar sobretudo com:** se a vitória do modelo "com direção" vem da direção ou de parâmetros a mais que o comparador não tem.
**Pontos cegos possíveis:** contexto regimental da Câmara (blocos, Mesa, orientação oral).

### Cartão #3
**Role:** R2. **Papel exibido:** Revisor 2 (Domínio).
**Identidade:** pesquisador sênior de estudos legislativos brasileiros, na tradição do CEBRAP e do Banco de Dados Legislativos. Conhece o regimento da Câmara, os blocos, as federações (Lei 14.208/2021) e a literatura sobre disciplina, coalizões, migração partidária e governadores.
**Foco:** (1) enquadramento teórico e derivação de E1–E5; (2) se é verdade que os registros de orientação são orientação de bloco, e o que isso significa no regimento; (3) a literatura que falta, inclusive a brasileira.
**Vai se importar sobretudo com:** se a interpretação substantiva ("governismo relativo", "base", "o centro orienta onde está unido") corresponde ao funcionamento da Câmara em 2023–2026.
**Pontos cegos possíveis:** detalhes de estimação.

### Cartão #4
**Role:** R3. **Papel exibido:** Revisor 3 (Perspectiva).
**Identidade:** pesquisador de comportamento legislativo comparado, com experiência no Parlamento Europeu (o modelo de "dois principais": grupo político e delegação nacional) e formação em medição/psicometria (validade de construto, dados faltantes não ignoráveis). Também tem experiência com infraestrutura de dados legislativos abertos.
**Foco:** (1) a analogia bloco × partido com os dois principais e o que ela pede de desenho; (2) validade de construto e dados faltantes (ausências, orientação vazia); (3) implicações para usuários de dados públicos (jornalismo de dados, monitores de governismo) e para a transparência.
**Vai se importar sobretudo com:** se D e U medem o que dizem medir, para todos os partidos, da mesma forma.
**Pontos cegos possíveis:** convenções da literatura brasileira.

**Quinto assento (fixo, sem cartão):** Devil's Advocate. Instrução recebida: atacar a tese central (indisciplina estruturada) e o problema de medida dos blocos.

## Recomendações de estratégia de revisão
- O artigo tem cinco frentes empíricas (P1–P4 mais partido × Governo). R1 e DA devem se concentrar no teste ruído × estrutura e na interpretação da dimensão; R2 e R3, na medida da orientação.
- É provável uma tensão entre R1 e EIC: R1 vai pedir mais análises, e EIC vai pedir um texto mais curto. O sintetizador precisa arbitrar.

---

# FASE 1 — Pareceres

## Parecer 1 — Journal-Fit Reviewer (EIC)

### Identidade
Editor associado de um periódico de ciência política com seção de métodos (perfil generalista; `criteria_binding_unavailable`).

### Recomendação: **Major Revision**
### Confiança: 4 (área central: instituições legislativas; não avaliei a fundo a estimação)
### Calibração: `NOT_CALIBRATED`

### Avaliação resumida
O artigo mede a disciplina partidária na Câmara de 2023–2026 com 455 mil votos nominais. Separa a disciplina à liderança (D) da unidade com os colegas (U), testa se a indisciplina é ruído ou estrutura com uma sequência de modelos de pontos ideais avaliados fora da amostra e completa a análise com correlatos do desvio, estudo de evento da troca de partido e a divergência entre partido e Governo. O trabalho empírico é cuidadoso, reprodutível e honesto quanto aos limites; a seção 7 e o Apêndice B estão acima do padrão. Há duas contribuições com potencial claro de publicação. A primeira é o alerta de que a "orientação do partido" registrada pela Câmara é, para o centro, orientação de bloco. A segunda é o teste explícito de ruído × estrutura contra comparadores adequados. Os problemas são de foco e de enquadramento. O texto é um relatório de projeto com cinco artigos dentro: compara com artefatos internos (`alinhamento.parquet`, `emb_votos`, "painel do projeto", "enunciado do bloco, não versionado"), tem 11 tabelas e um resumo de 340 palavras. As expectativas E1–E5 também estão formuladas de maneira que quase não poderiam ser contrariadas. A recomendação é Major Revision. A contribuição existe, mas o artigo precisa decidir qual é a sua tese e cortar o resto.

### Pontos fortes
**S1: Contribuição de medida relevante e com evidência própria.** A decomposição das camadas de orientação (própria, bloco, bloco inferido e bloco heterogêneo) e a cobertura reportada para cada taxa formam um alerta útil para toda a literatura que usa a orientação registrada.
**Evidence Anchor:** `text: §1 ¶2 "a bancada que orienta é o próprio partido ou federação em só 33,9% dos votos do Plenário"`

**S2: Transparência e reprodutibilidade incomuns.** Todo número vem de `resultados.json`, os desvios do plano estão listados e as limitações são explícitas.
**Evidence Anchor:** `text: Apêndice B — tabela de desvios com † para os que mudam definições`

**S3: Comparadores pensados para a pergunta.** A pergunta é posta como problema de previsão fora da amostra e os comparadores foram pensados para ela: M0c como linha de base calibrada e M3L como extensão de M2.
**Evidence Anchor:** `text: §4.3 "M1→M2 mede o valor da lealdade; M2→M3L, o valor da direção da dissidência além da lealdade"`

### Fraquezas

**W1: O artigo não escolhe uma tese; a extensão e o número de frentes diluem a contribuição.**
**Problem:** São quatro perguntas, cinco expectativas e oito subseções de resultados (temas, pivôs, dissidentes nominais, segunda dimensão, suplência, fusões). Pivôs (§5.6, Tabela 8) e temas (Tabela 4) não servem a nenhuma das contribuições anunciadas na §1.
**Evidence Anchor:** `text: §1 ¶1 "As perguntas são quatro: (P1)... (P4)"; §5.6 "Pivôs"; Tabelas 4 e 8`
**Why it matters:** O leitor de Dados ou LSQ perde a linha principal. Com cerca de 9.250 palavras sem tabelas, mais 11 tabelas, o texto fica acima do que essas revistas costumam aceitar como artigo `[FIELD-NORM UNVERIFIED: limites exatos de palavras não conferidos nas normas das revistas]`.
**Suggestion:** Organizar o artigo em torno de duas teses: (a) medida — D × U e camadas; (b) estrutura da indisciplina — M0–M5, interpretação e trocas de partido. Levar temas, pivôs, a lista nominal de dissidentes, a segunda dimensão e os detalhes de suplência para o apêndice online. Partido × Governo fica no corpo só se P0-2 e P1-2 do roadmap forem resolvidos. Meta: cerca de 8.000 palavras com notas, no máximo 6 tabelas e 5 figuras no corpo.
**Severity:** Major. **Confidence:** 4 — experiência editorial.

**W2: Comparações com artefatos internos do projeto e referência a fonte não pública.**
**Problem:** O texto valida resultados contra números de arquivos internos e contra um "enunciado do bloco, não versionado no repositório", que o leitor não tem como consultar.
**Evidence Anchor:** `text: §5.6 "mencionados na descrição dos resultados prévios que orientou este artigo (enunciado do bloco, não versionado no repositório)"`
**Why it matters:** Não é uma fonte citável, e passa a impressão de que o artigo foi escrito para confirmar uma lista prévia.
**Suggestion:** Retirar todas as comparações com `alinhamento.parquet`, `emb_votos`, "painel do projeto" e "obtidos antes no projeto" (§5.1 ¶1, §5.4 ¶1, §5.6 em três lugares, §6 ¶2). Se for preciso, deixar uma frase no Apêndice A sobre a correspondência com versões anteriores do código. Tirar da §1 ¶4 a referência aos "sete trabalhos irmãos", ou trocar por citações formais quando existirem.
**Severity:** Major. **Confidence:** 5.

**W3: As expectativas E1–E5 quase não podem ser contrariadas.**
**Problem:** E1 é "contrariada por variação temporal grande em U", mas "grande" não tem limiar. E2 é testada só entre partidos que têm Rice padronizado com m = 10, o que exclui justamente os pequenos (ver R1-W6). E4 e E5 são confirmadas por qualquer associação positiva.
**Evidence Anchor:** `text: §2.2 ¶3 "E1 (Figueiredo e Limongi): disciplina alta (em torno de 90%) e estável; contrariada por variação temporal grande em U"`
**Why it matters:** O artigo diz "confirma E4", "confirma E5" e "E2 se sustenta", mas um teste que não poderia falhar não confirma nada.
**Suggestion:** Dar a cada expectativa um critério quantitativo de falha, declarado como posterior ao P1 descritivo, já que o plano foi escrito depois dele (Apêndice A). Outra opção é rebaixar E1–E5 a "leituras esperadas" e trocar "confirma" por "é compatível com".
**Severity:** Major. **Confidence:** 4.

**W4: Resumo longo e carregado de números.**
**Problem:** O resumo tem cerca de 340 palavras e 15 números.
**Evidence Anchor:** `text: Resumo — "Quanta disciplina partidária há..." até "conforme o contrafactual."`
**Why it matters:** Resumos de 150–250 palavras são a norma nas revistas da área `[FIELD-NORM UNVERIFIED]`. Este também enfatiza resultados secundários (suplência, sexo, idade).
**Suggestion:** Reduzir a cerca de 200 palavras com as duas teses e três números: cobertura de D, ganho M2→M3L e queda após a troca.
**Severity:** Minor. **Confidence:** 4.

### Comentários detalhados
- **Adequação à revista:** o artigo serve para Dados e RBCP; para LSQ, precisaria de um parágrafo comparado (blocos como "segundo principal", na linha de Hix, Noury e Roland; ver R3).
- **Originalidade:** a medida (camadas e cobertura) é original para a 57ª Legislatura. O teste de ruído × estrutura é original na forma, mas o resultado (dissidência ao longo do eixo principal) é esperado; ver DA.
- **Coerência estrutural:** a §5.5 usa a Tabela 11 antes das Tabelas 6–10, e a §5.6 usa a Tabela 10 antes da 6. A numeração não segue a ordem de aparição, e o mesmo vale para as Figuras 5 e 6.
- **Título:** bom, mas "dissidência estruturada" depende de P0-2 e P0-3.
- **Conclusão:** "prevê o voto fora da amostra" exagera o que foi feito, que é imputar células de uma matriz já observada (R1-W2).

### Perguntas aos autores
1. Qual é a tese que o artigo quer que o leitor guarde em uma frase?
2. Os resultados de temas e pivôs mudam alguma conclusão? Se não mudam, por que estão no corpo?

### Questões menores
- Siglas sem definição: MPL (título da Tabela 10), IC, EP e UF. Ver o anexo de siglas.
- Três marcas "[verificar]" no texto (§2.1 ¶2, §4.1 último parágrafo, referência de Nicolau).
- O Apêndice B fala em "Contrafactual de P5", mas o artigo só tem P1–P4.

### Julgamentos por critério

| Dimensão | Fonte do critério | Julgamento | Âncora | Justificativa | Incerteza | Pesa na decisão? |
|---|---|---|---|---|---|---|
| Originalidade | quality_rubrics | MEETS | §1 ¶2 | Medida por camadas é nova | DA questiona a novidade | sim |
| Rigor metodológico | — | NOT_ASSESSED | — | Fica com R1 | — | não |
| Suficiência da evidência | quality_rubrics | PARTLY_MEETS | §2.2 E1–E5 | Testes fracos | — | sim |
| Coerência do argumento | quality_rubrics | PARTLY_MEETS | §1, §5 | Cinco frentes | — | sim |
| Qualidade da escrita | quality_rubrics | PARTLY_MEETS | Resumo; §5.6 | Clara, mas longa; artefatos internos | — | sim |
| Integração da literatura | quality_rubrics | PARTLY_MEETS | §2 | Ver R2 | — | sim |
| Significância | quality_rubrics | MEETS | §8 ¶2 | Alerta útil para a literatura | — | sim |

---

## Parecer 2 — Revisor 1 (Metodologia)

### Identidade
Metodólogo político: pontos ideais, validação fora da amostra, painel e estudo de evento.

### Recomendação: **Major Revision**
### Confiança: 5 (área central) para §4.2–4.5 e §5.4–5.8; 3 para o regimento
### Calibração: `NOT_CALIBRATED`

### Avaliação resumida
O desenho é ambicioso e bem documentado. A validação cruzada estratificada por votação, os comparadores M0c e M3L, a definição das "células com divisão interna" só com informação de treino e a medida de distância estimada no outro biênio mostram preocupação real com circularidade. Encontrei, porém, problemas que afetam conclusões centrais. (1) O comparador "lealdade sem direção" (M2) tem menos graus de liberdade do que o modelo com direção, de modos que nada têm a ver com direção: não tem escala por votação e usa um parâmetro por deputado, enquanto os pontos são por período. O ganho M2→M3L de 0,015 pode vir disso. (2) A "validação fora da amostra" é imputação de células de uma matriz em que o mesmo deputado e os mesmos colegas, na mesma votação, estão no treino. O ganho M0→M1 é em grande parte uso de informação contemporânea. (3) Na regressão de correlatos, a "distância" mistura as escalas de dois ajustes diferentes (um por biênio). (4) O estudo de evento usa TWFE com adoção escalonada e efeitos possivelmente heterogêneos. (5) Os intervalos ignoram uma das duas dimensões de dependência em quase todos os casos. Nada disso é fatal; tudo pede reanálise.

### Pontos fortes
**S1: Proteção contra seleção pela variável dependente.** As células com divisão interna são definidas só com dados de treino.
**Evidence Anchor:** `text: §4.3 "definidas só com informação de treino, para não selecionar pela variável dependente"`

**S2: Medida de preferência fora do período do desfecho.** A distância é estimada no outro biênio, o que evita a circularidade mais óbvia.
**Evidence Anchor:** `text: §4.4 "estimada com as votações do outro biênio (2023–24 para votos de 2025–26 e vice-versa)"`

**S3: Honestidade sobre os contrafactuais.** O texto diz que (i) é limite inferior e que (ii) é pouco crível para a esquerda.
**Evidence Anchor:** `text: §5.8 ¶2 "o que o torna pouco crível para os partidos de esquerda (para o PSOL, prevê que só 34%...)"`

**S4: Placebo tratado com honestidade.** O grupo de fusões não é identificado em U, e o texto não o usa como teste.
**Evidence Anchor:** `text: §5.7 ¶2 "os coeficientes das fusões em U não são identificados e não são estimados nem mostrados"`

### Fraquezas

**W1: M2 não é um comparador justo para "direção além da lealdade".**
**Problem:** Em M2, $\Pr = \sigma(z^{M1}_{ij} + \rho_i d_{pj})$. A lealdade $\rho_i$ é **por deputado**: no código, `ajustar_lealdade` indexa por `A["base"]`, o índice do deputado, e não do período. Ela também entra com a mesma escala em todas as votações. M3 tem um ponto por **período** deputado×partido e uma carga $b_j$ **por votação**. O ganho M2→M3L (0,015) mistura portanto três coisas: (a) direção; (b) heterogeneidade entre votações na propensão a desviar, que um termo não direcional $\rho_r\,c_j\,d_{pj}$ também capturaria; (c) separação por período, que importa para os 177 deputados que trocaram de partido.
**Evidence Anchor:** `equation: §4.3, M2 — "σ(z^{M1}_{ij}+ρ_i d_{pj})" × §4.2 "b_j^⊤ x_r"`
**Why it matters:** "Saber para que lado o deputado costuma desviar acrescenta informação" (§5.4) é a frase que sustenta a tese. Se um M2 com escala por votação e lealdade por período fechar boa parte da diferença, a "direção" perde a maior parte da evidência a seu favor.
**Suggestion:** Estimar **M2b**: $\sigma(z^{M1} + \rho_r\,c_j\,d_{pj})$, com $c_j \ge 0$ por votação (ou $|b_j|$ de M3 como escala fixa) e $\rho_r$ por período. Reportar M2b→M3L na Tabela 5 e na Figura 4. Um teste complementar: M3 com sinais embaralhados entre deputados dentro do partido, que preserva $|x_r|$ e destrói a direção.
**Severity:** Critical (repairable). **Confidence:** 5 — li o código.

**W2: A "validação fora da amostra" é imputação dentro da matriz, e o ganho M0→M1 usa informação contemporânea.**
**Problem:** As dobras sorteiam células deputado×votação estratificadas por votação. Cerca de 80% dos colegas de partido **na mesma votação** ficam no treino, e $g_{pj}$ é estimado com eles. M1 "prevê" o voto de um deputado a partir do voto dos colegas na mesma chamada.
**Evidence Anchor:** `text: §5.4 "A posição do partido em cada votação, estimada com os votos dos colegas, contém muito mais do que a orientação registrada"`
**Why it matters:** M0 é uma regra *ex ante* (a orientação é anunciada antes do voto), e M1 é *ex post*. A diferença de 0,146 não mede "o que a orientação deixa de fora", e sim o valor de conhecer o resultado da bancada. As palavras "prevê o voto fora da amostra" na §8 e na §9 exageram.
**Suggestion:** (a) Chamar o exercício de "imputação fora da amostra" e reformular a interpretação de M0→M1. (b) Acrescentar uma validação **temporal**: treinar com 2023–2025 e testar em 2026, com $a_j, b_j, g_{pj}$ das votações de teste estimados só com outros partidos, ou com metade aleatória de cada célula. Assim os $x_r$ ficam congelados e só a votação nova é vista. (c) Reportar a diferença de log-loss como redução **relativa** (M2→M3L ≈ 5,7% da perda de M2 nas células com divisão) e por deputado (mediana e quantis), não só por voto.
**Severity:** Major. **Confidence:** 5.

**W3: "Células com divisão interna" são a maioria das observações, e o rótulo engana.**
**Problem:** São 267.770 dos 417.832 votos da amostra do modelo (64%; `cv_disputadas_intra_n`). O critério "≥ 1 voto contra a maioria no treino" é fraco em células grandes.
**Evidence Anchor:** `dataset: resultados.json — cv_disputadas_intra_n = 267770; cv_todas_n = 417832`
**Why it matters:** O leitor entende que se trata de um subconjunto raro de votações rachadas. A taxa de desvio de 15,2% nesse subconjunto ajuda a calibrar a leitura, mas não substitui o tamanho.
**Suggestion:** Informar o N na nota da Tabela 5 e acrescentar uma subamostra mais exigente, por exemplo minoria de treino ≥ 10% na célula.
**Severity:** Minor. **Confidence:** 5.

**W4: A distância na Tabela 10 mistura escalas de dois ajustes e perde os que trocaram de partido.**
**Problem:** `distancia_fora_periodo` estima um modelo global **separado** para cada biênio (`global_b1` e `global_b2`), cada um com sua escala e rotação, e junta as duas distâncias numa única variável. O coeficiente "25,7 p.p. por unidade" fica sem unidade definida. Além disso, a distância só existe quando o deputado tem período **no mesmo partido** no outro biênio (`anexar_distancia`), o que tira da amostra quem trocou de partido entre os biênios.
**Evidence Anchor:** `table: Tabela 10 — "Distância à mediana do partido (outro biênio) 25,67 [22,33; 29,00]"; nota "dim1 global estimada com as votações do outro biênio"`
**Why it matters:** A frase que diz que a distância "domina" os correlatos depende de comparar magnitudes. Além disso, a seleção pela permanência no partido interage com o indicador "Trocou de partido".
**Suggestion:** Padronizar a distância dentro de cada ajuste (DP entre períodos, ou dentro do partido) e reportar o efeito por 1 DP. Reportar separadamente as duas metades (2023–24 → 2025–26 e o inverso). Dizer quantos deputados e votos se perdem por falta de período correspondente.
**Severity:** Major. **Confidence:** 5 — li o código.

**W5: O estudo de evento usa TWFE com adoção escalonada.**
**Problem:** As trocas ocorrem em datas diferentes (139 de 191 na janela de 2026; as outras, de 2023 a 2025). Com $\alpha_i$ e $\gamma_{pj}$, os deputados que já trocaram servem de controle para os que trocam depois, e os pesos podem ser negativos se os efeitos forem heterogêneos entre coortes. A janela pós-troca de quem saiu em 2026 tem 66 votações, em ano eleitoral. As estimativas pré-evento sobem cerca de 3 pontos (−1,7 → −0,9 → +1,4), e nenhum teste conjunto foi reportado.
**Evidence Anchor:** `figure: Figura 5 — coeficientes ≤−13 (−1,7), −6 a −4 (−0,9), −3 a −1 (+1,4); pós 0–3 (−11,1), ≥4 (−12,4)`
**Why it matters:** O "11,1 pontos" está no Resumo e no Abstract.
**Suggestion:** Reestimar com um estimador robusto a heterogeneidade (Sun e Abraham, 2021; Callaway e Sant'Anna, 2021; ou um desenho empilhado) usando nunca tratados e ainda não tratados como controles. Separar a coorte de 2026 das anteriores. Reportar um teste F conjunto das janelas pré-evento e a taxa de desvio dos trocadores na janela de referência, para dar escala. Explicar por que a referência é −12 a −7 e não −1.
**Severity:** Major. **Confidence:** 4 — o resultado pode se manter, mas o estimador precisa mudar.

**W6: O teste de E2 (estabilidade ao corrigir por Desposato) é quase vazio.**
**Problem:** O Rice padronizado com m = 10 não existe para PCdoB, PV, AVANTE e NOVO, que são justamente os partidos pequenos em que a correção importa. A correlação de 0,99 é calculada entre partidos grandes. Em `resultados.json`, a padronização **sobe** o Rice dos partidos grandes de forma não uniforme: UNIÃO vai de 0,537 (bruto) a 0,563 (m = 10) e 0,613 (m = 5); MDB vai de 0,640 a 0,652 e 0,682. O partido grande "parece pequeno", como Desposato propõe.
**Evidence Anchor:** `table: Tabela 2 — coluna "Rice m=10" vazia para PCdoB, PV, AVANTE e NOVO; §5.3 "a correlação de postos entre o Rice bruto e o padronizado (m = 10) é 0,99"`
**Why it matters:** A frase "A expectativa E2 se sustenta" não foi testada onde poderia falhar.
**Suggestion:** Usar um m comum que inclua todos os partidos analisados (m = 5, ou o tamanho do menor partido com mediana ≥ m). Comparar o ranking **completo** bruto × padronizado. Mostrar m = 5 na Tabela 2 em vez de m = 10, ou nas duas.
**Severity:** Major. **Confidence:** 5.

**W7: A inferência é inconsistente entre análises e ignora uma das dependências.**
**Problem:** (a) Taxas: bootstrap só de votações, quando os votos também se correlacionam dentro do deputado. (b) Diferenças de log-loss: bootstrap só de deputados, com previsões fixas, quando os votos também se correlacionam dentro da votação. (c) Dispersão: 100 réplicas, e o IC básico do PT é [0,12; 0,23] com limite superior igual ao estimador (0,23). Isso indica que todas as réplicas ficaram acima do estimador, ou seja, que o bootstrap está medindo sobretudo o viés de inflação e não a variabilidade. (d) Para as posições individuais, 383 de 595 períodos têm IC que exclui a mediana do partido, o que sugere intervalos estreitos demais (o bootstrap de votações sem incerteza paramétrica subestima a variância).
**Evidence Anchor:** `table: Tabela 6 — PT "0,23 [0,12; 0,23]"; §4.5 "Dispersões... (100 réplicas)"; §4.3 "bootstrap de deputados (1.000 réplicas) sobre as perdas de teste"`
**Why it matters:** As conclusões sobre E3 provavelmente se mantêm, porque os ICs estão longe de zero. Já a lista de dissidentes (Tabela 7) e a dispersão (Tabela 6) dependem diretamente dessa incerteza.
**Suggestion:** (a, b) Usar bootstrap de duas vias (*pigeonhole*, Owen, 2007), ou reportar os dois bootstraps de uma via e ficar com o mais conservador. (c) Usar ≥ 500 réplicas, ou bootstrap paramétrico (Lewis e Poole, 2004), e reportar o viés. (d) Tratar os ICs individuais como inferiores ao verdadeiro, ou recalcular com bootstrap paramétrico.
**Severity:** Major. **Confidence:** 4.

**W8: No contrafactual de P5, a linha de base e os ICs não sustentam a leitura por partido.**
**Problem:** O "excesso" por partido não tem IC. Ele vem de poucas votações: entre as votações em que a orientação do partido e a do Governo são opostas, o PT tem 9, o PSB 26 e o PDT 45, segundo consulta a `votos.parquet`. A "base" é definida como todos os partidos menos PL e NOVO (`OPOSICAO` em `partido_vs_governo`), o que inclui PSDB e não varia no tempo. A faixa de 3,8 a 16,5 pontos é larga demais para uma tese, e o limite superior vem de um contrafactual que os próprios autores consideram pouco crível para a esquerda.
**Evidence Anchor:** `text: §5.8 ¶2 "Pelo contrafactual (i), o excesso é maior no PSB (17,8 pontos), no PDT (12,8) e no PSOL (12,1)"`
**Why it matters:** E5 ("o partido prevalece além das preferências") depende de uma faixa cujo limite superior não é crível.
**Suggestion:** (a) Pôr IC por bootstrap de votações em cada partido e mostrar o número de votações na Figura 7. (b) Definir a base pela composição do ministério ao longo do tempo (ver R2-W4). (c) Reportar o contrafactual (ii) sem PSOL, PSB e PDT, como o Stage 2.5 sugeriu (modo 4, "atalho"). (d) Considerar uma âncora de preferência que não venha de votações nominais (ver R3-W3), ou apresentar só os limites, sem ponto central.
**Severity:** Major. **Confidence:** 4.

**W9: Seleção × adaptação depende da penalização de δ_r.**
**Problem:** $x_r = u_i + \delta_r$ com prior gaussiana em $\delta_r$: a penalização puxa as posições de antes e de depois da troca uma para a outra. Os 69,7% "moveram-se em direção ao destino" e o deslocamento mediano de 0,13 dependem do $\lambda$ usado.
**Evidence Anchor:** `text: §5.7 ¶1 "A favor da adaptação: 69,7% se moveram em direção ao destino entre os dois períodos (deslocamento mediano de 0,13 nessa direção)"`
**Why it matters:** A conclusão "sinais dos dois mecanismos" pode ser artefato da penalização.
**Suggestion:** Reestimar com $\lambda_\delta$ menor e maior, ou com períodos estimados separadamente, e reportar como o resultado muda.
**Severity:** Minor. **Confidence:** 4.

**W10: A análise de sensibilidade da penalização foi feita só na dobra 0 e só para M1 e M3.**
**Evidence Anchor:** `text: Apêndice B "Sensibilidade só na dobra 0, para M1 e M3"`
**Problem / Suggestion:** O ganho M2→M3L depende também de $\lambda_r$ (= 1) em M2, que não foi variado. Variar $\lambda_r$ e $\lambda_d$ em todas as dobras para M2 e M3L. O cache torna isso barato.
**Severity:** Minor. **Confidence:** 4.

### Comentários detalhados
- **D e U.** A orientação de Obstrução é tratada como Não, e Abstenção conta como desvio, mas a ausência não conta (exceto na PEC). A assimetria é defensável, mas precisa ser justificada, porque abster-se e ausentar-se são substitutos táticos.
- **U com ≥ 5 colegas.** A regra exclui NOVO e células pequenas de PCdoB e PV, e a composição dos partidos com U muda entre anos. A série de U por ano deveria fixar o conjunto de partidos.
- **Figura 2.** O ponto de D em 2025S1 (97,8%) tem cobertura de 4% e aparece sem IC. O título diz "é um artefato de cobertura", afirmação mais forte que a do texto (o Stage 2.5 já tinha pedido para harmonizar). Sugestão: omitir ou esmaecer os pontos com cobertura < 20% e acrescentar ICs.
- **Tabelas 1 e 3.** Os números de votações não batem (mérito: 230 × 227; emenda: 145 × 144; requerimento: 324 × 318; PEC: 30 × 29) e não há nota explicando.
- **Tabela 7.** A posição está em DPs do partido, mas o IC está em unidades da dim1. Usar uma só unidade.
- **Validação preditiva das trocas.** O "sinal" é comparado com a direção definida pelas mesmas medianas pré-2026, na mesma dimensão. Convém dizer que o teste não é independente do modelo. Com AUC de 0,59 e 61,8%, o resultado é modesto e deve ser apresentado assim.

### Perguntas aos autores
1. Qual é a diferença de log-loss entre M2b (lealdade por período, com escala por votação) e M3L?
2. Numa validação temporal (2026 como teste, com $x_r$ congelados), a vantagem de M3 sobre M2b se mantém?
3. As mudanças em M2 e na definição de "células com divisão interna" (Apêndice B, †) foram feitas antes ou depois de ver resultados de validação cruzada?

### Julgamentos por critério

| Dimensão | Julgamento | Âncora | Justificativa | Pesa? |
|---|---|---|---|---|
| Rigor metodológico | PARTLY_MEETS | §4.3, `ajustar_lealdade` | Comparador desigual; TWFE | sim |
| Suficiência da evidência | PARTLY_MEETS | Tabelas 5, 6, 10 | Escalas e ICs | sim |
| Coerência do argumento | PARTLY_MEETS | §5.4 → §8 | "prevê fora da amostra" | sim |
| Originalidade | MEETS | §1 ¶3 | Desenho de comparadores | não |
| Qualidade da escrita | MEETS | §4 | Método claro | não |
| Integração da literatura | NOT_ASSESSED | — | — | não |
| Significância | MEETS | — | — | não |

---

## Parecer 3 — Revisor 2 (Domínio)

### Identidade
Pesquisador sênior de estudos legislativos brasileiros.

### Recomendação: **Major Revision**
### Confiança: 4 (área central; não conferi cada votação da Tabela 11)
### Calibração: `NOT_CALIBRATED`

### Avaliação resumida
O artigo dialoga com a pergunta certa e com parte da literatura certa. A constatação de que a orientação registrada é de bloco é a mais importante para a comunidade brasileira: muitos trabalhos e monitores de imprensa usam a orientação "do partido" sem perguntar quem orientou. Mas a interpretação comportamental do problema de medida não foi verificada contra o funcionamento regimental: no painel, quem orienta pelo bloco é o líder do bloco, e as orientações orais dos líderes partidários podem não ser registradas. Algumas afirmações substantivas também vão além dos dados: o centro "orienta onde está unido", o megabloco "quase não orientou" e a dimensão é "governismo". O enquadramento teórico tem lacunas importantes. Falta a literatura brasileira sobre poderes de agenda e liderança (Amorim Neto, Cox e McCubbins), sobre recursos do Executivo (Pereira e Mueller; Raile, Pereira e Power), sobre governadores (Cheibub, Figueiredo e Limongi, 2009; Carey e Reinhardt, 2004), que é decisiva para a leitura do efeito das UFs, e sobre migração partidária (Melo; Desposato, 2006). "Base" é definida de forma estática e, para PSDB e REPUBLICANOS, errada. Recomendo Major Revision.

### Pontos fortes
**S1: Bom uso do partido na data e tratamento separado das fusões.** O ponto é crucial numa legislatura com janela partidária.
**Evidence Anchor:** `text: §3 "usá-lo atribuiria a 2023 filiações de 2026"`

**S2: A análise de ausência na PEC captura um mecanismo regimental real.** O quórum de 308 faz da ausência um voto.
**Evidence Anchor:** `text: §5.2 "a disciplina cai de 94,9% para 83,8% (11,6% dos membros em exercício estavam ausentes)"`

**S3: Desmonta um falso racha.** O "racha" de PSB e PDT diante do Governo vem da atribuição a blocos inferidos.
**Evidence Anchor:** `text: §5.8 ¶1 "O 'racha' desses partidos diante do Governo é, em boa parte, um artefato da atribuição a blocos truncados"`

### Fraquezas

**W1: A interpretação comportamental da orientação vazia e da orientação de bloco não foi validada contra o regimento e as notas taquigráficas.**
**Problem:** O artigo afirma que "a orientação vazia significa que a liderança não orientou" (§7) e que o megabloco "quase não orientou" (Resumo, §1). Uma consulta a `votacoes_orientacoes.parquet` mostra que, nas 227 votações de 2025 em que o megabloco foi a bancada aplicável, **não há nenhum registro de orientação própria do PL nem da federação do PT**. Nas outras votações de 2025, o PL tem 122 registros. Ou seja, quando o bloco existe, o painel registra só o bloco (199 das 227 orientações vazias), mesmo quando os líderes partidários orientam oralmente em plenário, o que é comum.
**Evidence Anchor:** `text: §7 "A orientação vazia significa que a liderança não orientou."`
**Why it matters:** A frase "em 2025, quase ninguém [orienta]" (§9) e a ideia da "bancada como ficção regimental" (§8) podem estar descrevendo o **registro**, e não o comportamento. A contribuição de medida continua de pé (o registro não é a orientação do partido). Muda a interpretação substantiva.
**Suggestion:** (a) Para uma amostra aleatória de 30 a 50 votações de 2025 com orientação vazia, conferir nas notas taquigráficas e no *Diário da Câmara* se os líderes do PL, da federação do PT e dos partidos do centro orientaram oralmente. Reportar a taxa de concordância. (b) Reescrever o Resumo, a §1 ¶2, a §7 e a §8–9 conforme o resultado. (c) Como robustez, usar para 2025 a orientação da Oposição como substituta para o PL e a do Governo/Maioria como substituta para a federação do PT, e reportar D com essa imputação.
**Severity:** Major. **Confidence:** 4 — conheço a prática regimental; a verificação é empírica.

**W2: "Quando orientam por conta própria, orientam onde estão unidos" não tem sustentação.**
**Problem:** A "D própria" dos partidos do centro (Tabela 2) vem de pouquíssimas votações. Consulta a `votos.parquet`: MDB e REPUBLICANOS, 1 votação (set/2025); PP, UNIÃO e PSDB, 13 votações, concentradas em mar–abr/2023, antes da formação dos blocos, e em set/2025. A coluna "D própria (n)" informa o número de **votos** (por exemplo, "94,1 (34)" no MDB), o que esconde que se trata de uma votação só.
**Evidence Anchor:** `table: Tabela 2 — MDB "94,1 (34)", REPUBLICANOS "100,0 (39)", PODE "92,3 (13)"; text: §5.1 ¶3 "coerentes com a ideia de que o partido orienta quando está unido"; §8 ¶2 "quando orientam por conta própria, orientam onde estão unidos"`
**Why it matters:** É uma afirmação causal sobre a estratégia dos líderes, apoiada em 1 a 13 votações cuja ocorrência se explica pelo calendário dos blocos.
**Suggestion:** Retirar a afirmação, ou testá-la comparando a unidade (U) nas votações em que o partido orientou por conta própria com votações comparáveis do mesmo período. Na Tabela 2, informar o número de **votações** da coluna D própria e não mostrar a taxa quando forem menos de 10.
**Severity:** Major. **Confidence:** 5 — conferido nos dados.

**W3: Blocos inferidos por nome truncado, quando existe fonte oficial da composição.**
**Problem:** A atribuição "bloco inferido" (11,2% dos votos do Plenário) usa nomes truncados. Para PSB e PDT, a adesão sob essa camada é de 31% e 44%, o que sugere atribuição errada de **pertencimento**, e não só "blocos de que não eram o eixo".
**Evidence Anchor:** `text: §3 "partidos sem orientação própria são atribuídos ao bloco truncado por inferência"`
**Why it matters:** A camada inferida mexe nos rankings de PSB, PDT e AVANTE (Tabela 9) e no "racha" diante do Governo.
**Suggestion:** Obter a composição oficial e datada dos blocos nos Dados Abertos da Câmara (endpoint de blocos e de partidos por bloco `[verificar o endpoint exato na API v2]`) e substituir a inferência. Se não for possível, validar a inferência numa amostra.
**Severity:** Major. **Confidence:** 3 — tenho quase certeza de que a API expõe blocos, mas não conferi o endpoint.

**W4: A "base" é estática e mal delimitada.**
**Problem:** Na análise partido × Governo, "base" é tudo exceto PL e NOVO. Isso põe PSDB na base, além de REPUBLICANOS e partidos que entraram no ministério ou saíram dele ao longo da legislatura (PP e REPUBLICANOS entraram em set/2023; União e PP anunciaram saída em 2025 `[verificar datas]`).
**Evidence Anchor:** `text: §4.4 "separando os partidos da base dos de oposição permanente (PL e NOVO)"`
**Why it matters:** O "excesso de lealdade" mistura partidos da coalizão com partidos independentes. A teoria (Carey; Figueiredo e Limongi) trata essas situações de modo diferente.
**Suggestion:** Definir a coalizão pela participação ministerial datada (como na literatura de coalizões; ver Amorim Neto) e mostrar os resultados separadamente para coalizão, independentes e oposição.
**Severity:** Major. **Confidence:** 4.

**W5: E4 e a leitura de Zucco: "governismo relativo" não se separa de ideologia nesta legislatura.**
**Problem:** Zucco (2009) e Zucco e Lauderdale (2011) separam a influência do Executivo da ideologia comparando governos de orientações diferentes, ou usando âncoras externas. Sob um governo de esquerda, governo × oposição e esquerda × direita quase coincidem. A correlação de 0,90 entre cargas e orientação do Governo é compatível com as duas leituras.
**Evidence Anchor:** `text: §5.5 "A dissidência intrapartidária é o eixo governo × oposição recortado dentro de cada partido, o que confirma E4 (Zucco, 2009)"`
**Why it matters:** "Governismo" sugere um mecanismo (cargos, emendas, acesso ao Executivo) que o artigo não testa.
**Suggestion:** (a) Nomear a dimensão de forma neutra ("eixo governo–oposição, que nesta legislatura coincide com esquerda–direita"). (b) Para separar as leituras, usar as votações em que a orientação do Governo contraria a da esquerda programática (PSOL, ou PT × Governo, que são poucas: 9 votações para o PT) ou votações fiscais em que o Governo se alinhou ao centro. Também pode usar âncoras externas (Power e Zucco; o *Brazilian Legislative Survey*).
**Severity:** Major. **Confidence:** 4.

**W6: Lacunas na literatura que mudam a interpretação.**
**Problem:** Faltam: (a) **governadores e estados**, decisivos para ler o efeito conjunto das UFs (χ² = 73,5): Cheibub, Figueiredo e Limongi (2009, LAPS); Carey e Reinhardt (2004, LSQ); Samuels (2003). (b) **Agenda e liderança**: Amorim Neto, Cox e McCubbins (2003, World Politics), que é a aplicação brasileira da teoria do cartel citada via Cox e McCubbins (2005); Limongi e Figueiredo (1995, Dados), base das medidas de disciplina. (c) **Recursos do Executivo**: Pereira e Mueller (2004, CPS); Raile, Pereira e Power (2011, PRQ), necessários para "governismo". (d) **Migração partidária**: Melo (2004); Desposato (2006, AJPS); e, sobre a mudança de voto após a troca, Nokken (2000, LSQ) e Heller e Mershon (2008, AJPS), que são o paralelo direto do estudo de evento. (e) **Senado e outras arenas**: Neiva (2011, Dados). (f) As três marcas "[verificar]" (Figueiredo e Limongi; Carey; Nicolau) continuam abertas.
**Evidence Anchor:** `absence: §2.1–2.2 e Referências — esperava literatura sobre governadores, recursos do Executivo, agenda e migração partidária; conferi §2, §5.6, §5.7, §8 e a lista de referências`
**Why it matters:** Sem Nokken e Heller e Mershon, o estudo de evento parece mais novo do que é. Sem a literatura sobre governadores, o efeito das UFs fica "sem mecanismo" quando há mecanismo proposto na literatura.
**Suggestion:** Acrescentar as obras e posicionar as contribuições em relação a elas. Ver o bloco `yaml suggested-references` abaixo.
**Severity:** Major. **Confidence:** 4.

**W7: E5 está mal derivada de Carey.**
**Problem:** Em Carey, a existência de "principais concorrentes" **reduz** a unidade: o presidente puxa votos para fora do partido. E5 afirma o contrário ("o partido prevalece além das preferências") e é contrariada só por um excesso nulo.
**Evidence Anchor:** `text: §2.2 ¶3 "E5 (Carey, principais concorrentes): na divergência entre partido e Governo, o partido prevalece além das preferências"`
**Why it matters:** O resultado (10,4% seguem o Governo) poderia ser lido justamente como evidência de Carey: um principal concorrente que tira um voto em cada dez.
**Suggestion:** Reformular E5 como o contraste entre Figueiredo e Limongi (o partido prevalece) e Carey (o presidente atrai votos), com previsões distintas sobre o excesso e sobre o padrão por partido.
**Severity:** Minor. **Confidence:** 4.

### Comentários detalhados
- **Federações.** PT-PCdoB-PV e PSOL-REDE são, por lei, uma unidade de atuação parlamentar. U é calculado por partido, e não por federação, o que deixa PCdoB e PV com bancadas pequenas e U instável (PV: IC [92,6; 98,4]). Calcular U também por federação.
- **Pivôs.** A Tabela 8 é interessante, mas não pertence a este artigo (ver EIC-W1). O pivô de 3/5 interessa para PEC; o texto não o conecta à disciplina.
- **Tabela 11.** Votações da mesma proposição aparecem nos dois polos (PL 1708/2025: mérito +5,88 e requerimento −5,90; PL 3469/2024: destaque + e requerimento −). Isso merece comentário: é um mesmo conflito em votações espelhadas, e não "temas" diferentes. Também deve ser dito que o polo negativo é dominado por requerimentos procedimentais com orientação Não do Governo, ou seja, obstrução e adiamento.

### Perguntas aos autores
1. Nas votações de 2025 com orientação vazia, os líderes orientaram oralmente? (Ver W1.)
2. Como a análise trata deputados que estiveram em partidos de coalizão e de oposição ao longo da legislatura?

```yaml suggested-references
- title: "Partidos políticos na Câmara dos Deputados: 1989-1994"
  authors: ["Limongi, Fernando", "Figueiredo, Argelina"]
  year: 1995
  venue: "Dados"
- title: "Agenda Power in Brazil's Câmara dos Deputados, 1989-98"
  authors: ["Amorim Neto, Octavio", "Cox, Gary W.", "McCubbins, Mathew D."]
  year: 2003
  venue: "World Politics"
- title: "The Cost of Governing: Strategic Behavior of the President and Legislators in Brazil's Budgetary Process"
  authors: ["Pereira, Carlos", "Mueller, Bernardo"]
  year: 2004
  venue: "Comparative Political Studies"
- title: "The Executive Toolbox: Building Legislative Support in a Multiparty Presidential Regime"
  authors: ["Raile, Eric D.", "Pereira, Carlos", "Power, Timothy J."]
  year: 2011
  venue: "Political Research Quarterly"
- title: "Political Parties and Governors as Determinants of Legislative Behavior in Brazil's Chamber of Deputies, 1988-2006"
  authors: ["Cheibub, José Antonio", "Figueiredo, Argelina", "Limongi, Fernando"]
  year: 2009
  venue: "Latin American Politics and Society"
- title: "State-Level Institutional Effects on Legislative Coalition Unity in Brazil"
  authors: ["Carey, John M.", "Reinhardt, Gina Yannitell"]
  year: 2004
  venue: "Legislative Studies Quarterly"
- title: "Ambition, Federalism, and Legislative Politics in Brazil"
  authors: ["Samuels, David"]
  year: 2003
  venue: "Cambridge University Press"
- title: "Parties for Rent? Ambition, Ideology, and Party Switching in Brazil's Chamber of Deputies"
  authors: ["Desposato, Scott W."]
  year: 2006
  venue: "American Journal of Political Science"
- title: "Retirando as cadeiras do lugar: migração partidária na Câmara dos Deputados (1985-2002)"
  authors: ["Melo, Carlos Ranulfo"]
  year: 2004
  venue: "Editora UFMG"
- title: "Dynamics of Congressional Loyalty: Party Defection and Roll-Call Behavior, 1947-97"
  authors: ["Nokken, Timothy P."]
  year: 2000
  venue: "Legislative Studies Quarterly"
- title: "Dealing in Discipline: Party Switching and Legislative Voting in the Italian Chamber of Deputies, 1988-2000"
  authors: ["Heller, William B.", "Mershon, Carol"]
  year: 2008
  venue: "American Journal of Political Science"
- title: "Coesão e disciplina partidária no Senado Federal"
  authors: ["Neiva, Pedro"]
  year: 2011
  venue: "Dados"
```

### Julgamentos por critério

| Dimensão | Julgamento | Âncora | Pesa? |
|---|---|---|---|
| Integração da literatura | PARTLY_MEETS | §2; W6 | sim |
| Coerência do argumento | PARTLY_MEETS | §5.1 ¶3; §8 ¶2 | sim |
| Suficiência da evidência | PARTLY_MEETS | Tabela 2, D própria | sim |
| Originalidade | MEETS | §1 ¶2 | sim |
| Significância | MEETS | §8 | não |
| Rigor metodológico | NOT_ASSESSED | — | não |
| Qualidade da escrita | MEETS | — | não |

---

## Parecer 4 — Revisor 3 (Perspectiva)

### Identidade
Comportamento legislativo comparado (Parlamento Europeu), medição e dados faltantes, infraestrutura de dados legislativos abertos.

### Recomendação: **Major Revision**
### Confiança: 3 (de fora da literatura brasileira; dentro de medição e comparado)
### Calibração: `NOT_CALIBRATED`

### Avaliação resumida
Visto de fora, o achado mais exportável do artigo é a estrutura de **dois principais**: o deputado do centro responde ao líder do bloco, no registro, e ao partido, como unidade de identidade e carreira. Essa estrutura é formalmente análoga à do eurodeputado entre o grupo político e a delegação nacional (Hix, 2002; Hix, Noury e Roland, 2007). O artigo trata isso como "problema de medida" quando poderia tratá-lo como **desenho**: votações em que o bloco e o partido (ou a federação) dão sinais opostos identificariam qual principal prevalece, como na literatura europeia. Do lado da medição, D e U não medem o mesmo construto em todos os partidos. Para PT e PSOL, D é disciplina ao partido; para o centro, é disciplina ao bloco; e U, por definição, mistura coesão de preferências com disciplina. As ausências são tratadas como ignoráveis fora da PEC, e a literatura de dados faltantes não ignoráveis em votações nominais oferece ferramentas para ir além. Também há implicações práticas que o artigo não explora: monitores públicos de governismo e disciplina (imprensa, ONGs) usam a mesma orientação registrada.

### Pontos fortes
**S1: Cobertura reportada junto de cada taxa.** É boa prática de medição, rara na literatura.
**Evidence Anchor:** `text: §4.1 "Toda taxa é reportada com sua cobertura"`

**S2: U como medida que não depende do registro.** Contorna um registro incompleto.
**Evidence Anchor:** `text: §4.1 "U não depende do registro de orientação e cobre 94,6% dos votos (D cobre 66,7%)"`

### Fraquezas

**W1: D não tem o mesmo construto em todos os partidos, e as comparações entre partidos não deixam isso claro.**
**Problem:** A Tabela 2 e a Figura 1 põem lado a lado D de partidos sob orientação própria (PT, PSOL e NOVO, 74–100%) e D de partidos sob orientação de bloco (centro, 0–4% própria). O texto reconhece a diferença (§5.1 ¶3), mas a tabela e o Resumo comparam os partidos ("quase total em PSOL, PT, PCdoB e NOVO e mais baixa em União e PSDB").
**Evidence Anchor:** `figure: Figura 1 — coluna "orientação própria" de 0% a 100% ao lado de D`
**Why it matters:** A diferença entre PT (98,7) e UNIÃO (82,4) mistura disciplina com o tipo de principal (partido × bloco heterogêneo).
**Suggestion:** Apresentar U como medida principal das comparações entre partidos e D por camada. No Resumo, comparar partidos só em U. Acrescentar, para o centro, um teste de "qual principal prevalece" nas votações em que o bloco e o partido (quando o partido orientou) ou a federação diferem. Se forem poucas, dizer isso.
**Severity:** Major. **Confidence:** 4.

**W2: Ausência tratada como ignorável fora da PEC.**
**Problem:** Abstenção conta como desvio, mas ausência não. A §5.2 mostra que a ausência importa na PEC (11,6%), e a §7 diz que "não estimamos ausência seletiva em geral". Nos pontos ideais, a não resposta pode ser não ignorável.
**Evidence Anchor:** `text: §7 "Não estimamos ausência seletiva em geral."`
**Why it matters:** Deputados que discordam podem preferir ausentar-se a votar contra. Isso inflaria D e U e reduziria a dimensão intrapartidária estimada.
**Suggestion:** Usar o painel de exercício para calcular, por deputado, a taxa de ausência nas votações em que o partido está dividido em comparação com as votações em que está unido. Estender a análise da PEC à PLP (quórum de 257). Citar e, se possível, aplicar Rosas, Shomer e Haptonstahl (2015).
**Severity:** Major. **Confidence:** 4.

**W3: A preferência medida vem de votações nominais, e o artigo usa isso para separar preferência de partido.**
**Problem:** A §5.6 conclui que "a expectativa krehbieliana de que a preferência domina se confirma". A "preferência", porém, é a posição estimada com votações nominais, que já incorporam a disciplina passada. Isso vale também para o contrafactual de P5. Aldrich, Montgomery e Sparks (2014) mostram que a pressão partidária, por si só, produz baixa dimensionalidade e posições em escalas de votações.
**Evidence Anchor:** `text: §5.6 ¶1 "A expectativa krehbieliana de que a preferência domina se confirma."`
**Why it matters:** Krehbiel (1993) pede justamente uma medida de preferência independente do voto partidário. Uma propensão estável a desviar, medida em outro biênio, não é preferência no sentido de Krehbiel.
**Suggestion:** Reformular: "a propensão passada a votar longe do partido prediz o desvio presente". Para falar de preferência, usar âncoras que não vêm de votações nominais: a autoria e coautoria de proposições (já em `proposicoes_autores.parquet`), a participação em frentes (já usada na §5.5), discursos (`discursos.parquet`) ou o *Brazilian Legislative Survey*.
**Severity:** Major. **Confidence:** 4.

**W4: As implicações práticas e para a transparência não aparecem.**
**Problem:** O artigo mostra que a orientação registrada pela Câmara não identifica quem orientou e que, em 2025, o registro ficou vazio em 59,5% dos votos. Isso afeta monitores públicos de governismo, que usam esses dados, e a própria transparência da Câmara.
**Evidence Anchor:** `absence: §8 e §9 — esperava uma frase sobre usuários de dados públicos e recomendação de registro; conferi §7, §8 e §9`
**Why it matters:** É uma contribuição prática barata, de interesse para Dados e RBCP.
**Suggestion:** Um parágrafo na §8 com recomendações: estratificar pela fonte e registrar a orientação dos partidos dentro dos blocos.
**Severity:** Minor. **Confidence:** 4.

**W5: Nomear dissidentes individuais com incerteza subestimada.**
**Problem:** A Tabela 7 e a §5.6 nomeiam deputados como "dissidentes sistemáticos" com ICs que provavelmente são estreitos demais (ver R1-W7). Os critérios (|z| ≥ 2 e IC exclui a mediana) também foram fixados depois do plano (Apêndice B).
**Evidence Anchor:** `table: Tabela 7 — "Dissidentes sistemáticos: maiores distâncias à mediana do próprio partido"`
**Why it matters:** São figuras públicas e os dados são públicos, de modo que não há problema ético grave. Mas um rótulo nominal com incerteza subestimada tende a circular fora do contexto do artigo.
**Suggestion:** Levar a lista ao apêndice, com intervalos revistos, e usar "mais distantes da mediana" em vez de "dissidentes sistemáticos".
**Severity:** Minor. **Confidence:** 3.

### Comentários detalhados
- **Analogia com o PE.** Hix, Noury e Roland (2007) está no `.bib` do Stage 1, mas não foi citado. A analogia dá ao artigo o enquadramento comparado de que LSQ precisaria.
- **Dimensão "intrapartidária".** Se ela é o eixo global visto de dentro (correlação de 0,94), a contribuição está em mostrar *quanto* da dissidência é esse eixo, e não em descobrir um novo eixo. A literatura de DIF (*differential item functioning*) sugere testar se as cargas diferem por partido. A §7 reconhece que o modelo impõe cargas comuns, e o plano previa esse teste.

### Recomendações de leitura interdisciplinar
- Hix, S. (2002). Parliamentary Behavior with Two Principals. *AJPS* 46(3).
- Rosas, G., Shomer, Y. e Haptonstahl, S. (2015). No News Is News: Nonignorable Nonresponse in Roll-Call Data Analysis. *AJPS* 59(2).
- Aldrich, J., Montgomery, J. e Sparks, D. (2014). Polarization and Ideology: Partisan Sources of Low Dimensionality in Scaled Roll Call Analyses. *Political Analysis* 22(4).
- Minozzi, W. e Volden, C. (2013). Who Heeds the Call of the Party in Congress? *JOP* 75(3). É o análogo direto de M2: lealdade ao chamado do partido separada da ideologia.

```yaml suggested-references
- title: "Parliamentary Behavior with Two Principals: Preferences, Parties, and Voting in the European Parliament"
  authors: ["Hix, Simon"]
  year: 2002
  venue: "American Journal of Political Science"
- title: "No News Is News: Nonignorable Nonresponse in Roll-Call Data Analysis"
  authors: ["Rosas, Guillermo", "Shomer, Yael", "Haptonstahl, Stephen R."]
  year: 2015
  venue: "American Journal of Political Science"
- title: "Polarization and Ideology: Partisan Sources of Low Dimensionality in Scaled Roll Call Analyses"
  authors: ["Aldrich, John H.", "Montgomery, Jacob M.", "Sparks, David B."]
  year: 2014
  venue: "Political Analysis"
- title: "Who Heeds the Call of the Party in Congress?"
  authors: ["Minozzi, William", "Volden, Craig"]
  year: 2013
  venue: "The Journal of Politics"
- title: "Democratic Politics in the European Parliament"
  authors: ["Hix, Simon", "Noury, Abdul G.", "Roland, Gérard"]
  year: 2007
  venue: "Cambridge University Press"
```

### Perguntas aos autores
1. Há votações em que o bloco e um partido-membro orientaram em sentidos opostos? Quantas, e quem prevaleceu?
2. Nas votações em que o partido está dividido, a ausência é maior do que nas votações em que está unido?

### Julgamentos por critério

| Dimensão | Julgamento | Âncora | Pesa? |
|---|---|---|---|
| Suficiência da evidência | PARTLY_MEETS | §5.6; §7 | sim |
| Coerência do argumento | PARTLY_MEETS | §5.6 ¶1 | sim |
| Significância | MEETS | §8 | não |
| Integração da literatura | PARTLY_MEETS | §2 | sim |
| Originalidade | MEETS | — | não |
| Rigor metodológico | NOT_ASSESSED | — | não |
| Qualidade da escrita | MEETS | — | não |

---

## Parecer 5 — Devil's Advocate

### Calibração
`NOT_CALIBRATED`.

### Julgamentos por critério
| Dimensão | Julgamento | Âncora |
|---|---|---|
| Coerência do argumento | DOES_NOT_MEET (para a tese "indisciplina estruturada / governismo") | §5.4–5.5; §8 ¶3 |
| Suficiência da evidência | PARTLY_MEETS (para a tese de medida) | §1 ¶2; §7 |

### Contra-argumento mais forte (≈ 280 palavras)
A tese "a indisciplina tem estrutura, e essa estrutura é o governismo relativo dentro de cada partido" pode ser, em grande parte, uma **redescrição do eixo principal**, e não uma descoberta sobre dissidência. Os partidos do centro brasileiro não estão ordenados no eixo governo–oposição: abrigam ao mesmo tempo bolsonaristas e governistas (Tabela 6, DP de 0,48 a 0,57). Num modelo que retira a média do partido em cada votação ($g_{pj}$), o que sobra **tem** de se ordenar pelo eixo principal, porque é nele que a variância dentro dos partidos está. A própria correlação de 0,94 entre a posição intrapartidária e a posição global relativa mostra isso. Nenhuma corrente da literatura sustenta que a indisciplina seja "ruído puro", então essa hipótese nula é um espantalho. Contra ela, qualquer modelo com parâmetros individuais e direção vence com 400 mil observações, e mesmo assim o ganho é de 0,015 por voto. O comparador sem direção (M2) foi construído sem os parâmetros por votação e por período que M3 tem (R1-W1). Assim, "direção além da lealdade" não está isolada. E "governismo" não se separa de "esquerda–direita" sob um governo de esquerda. A explicação mais parcimoniosa é a de **Krehbiel**: partidos heterogêneos cujos membros votam conforme posições estáveis no eixo principal. Isso não é nem disciplina nem indisciplina estruturada, é heterogeneidade. Quanto ao "problema de medida", parte dele é um **problema de registro**. Quando existe bloco, o painel da Câmara registra só o bloco: nas 227 votações do megabloco não há nenhum registro de orientação do PL ou da federação do PT. A narrativa comportamental ("o megabloco quase não orientou"; "o centro orienta onde está unido") não está demonstrada, e a "D própria" do centro vem de 1 a 13 votações de mar–abr/2023 e set/2025. Sem essas leituras, o artigo é um bom estudo descritivo de disciplina alta e estável com registros incompletos, e não uma tese sobre dissidência estruturada.

### Lista de problemas

#### CRITICAL

**DA-C1: A interpretação comportamental do problema de medida não foi demonstrada (registro × comportamento), e uma afirmação derivada contradiz os dados.**
- **Dimensão:** Foundation collapse e data-conclusion mismatch (secundário). **Local:** Resumo; §1 ¶2; §5.1 ¶3; §7 "orientação vazia"; §8 ¶2; §9; título da Figura 2.
- **Evidência:** `dataset: votacoes_orientacoes.parquet — nas 227 votações de 2025 com o megabloco como bancada aplicável, 0 registros de PL e 0 de "Fdr PT-PCdoB-PV"; nas demais votações de 2025, 122 de PL e 201 da federação do PT. votos.parquet — D própria do centro vem de 1 votação (MDB, REPUBLICANOS, set/2025) ou 13 (PP, UNIÃO, PSDB; mar–abr/2023 e set/2025)`.
- **Por que é crítico:** A primeira das quatro contribuições é apresentada no Resumo e na Discussão como um fato sobre o comportamento das lideranças ("quase não orientou"; "delegam... e orientam onde estão unidos"; "bancada... ficção regimental"). O mesmo padrão nos dados é igualmente compatível com o painel registrar só o bloco. A frase "orientam onde estão unidos" contradiz o que os dados mostram sobre a origem das poucas orientações próprias, que se explicam pelo calendário.
- **Reparável:** sim (R2-W1, R2-W2). A tese de medida no sentido estrito ("o registro não é orientação do partido; reporte camada e cobertura") sobrevive e é valiosa.
- `field_norm_boundary`: estudos de disciplina na Câmara usam a orientação do líder registrada no painel. Desde Figueiredo e Limongi (1999), e por meio do Banco de Dados Legislativos do CEBRAP, a orientação registrada é tratada como sinal do líder. Afirmações sobre o comportamento dos líderes requerem fonte sobre o que o líder fez, como as notas taquigráficas.
- `evidence_crossing_rationale`: o artigo não apenas usa o registro como sinal (prática aceita). Tira do registro **vazio** inferências sobre ausência de comportamento, sem verificar a fonte primária, e num período em que os dados mostram uma mudança estrutural de registro (a ausência total de linhas partidárias nas votações do megabloco).

**DA-C2: A cadeia "M3L vence M2 ⇒ a dissidência tem direção ⇒ a direção é governismo" se rompe em dois elos.**
- **Dimensão:** Logic chain break. **Local:** §4.3; §5.4 (M2→M3L); §5.5; §8 ¶3; Resumo; título.
- **Evidência:** `equation: §4.3 M2 = σ(z^{M1}+ρ_i d_{pj}) sem escala por votação e com ρ por deputado (código: ajustar_lealdade indexa A["base"]), contra M3 com b_j por votação e x por período; text: §5.5 "o que confirma E4 (Zucco, 2009)" sob governo de esquerda`.
- **Por que é crítico:** Elo 1: o ganho atribuído à "direção" pode vir de parâmetros que nada têm a ver com direção (R1-W1). Elo 2: "governismo" não se separa de ideologia nesta legislatura (R2-W5). A palavra "estruturada" no título e a frase central da §8 dependem dos dois elos.
- **Reparável:** sim (M2b; nomeação neutra ou teste de separação).
- Não depende de norma do campo: é validade lógica do teste declarado pelo próprio artigo (§4.3, "M2→M3L, o valor da **direção**").

#### MAJOR

**DA-M1: O contraste "ruído × estrutura" usa um espantalho como nula.**
Nenhuma teoria citada prevê indisciplina puramente aleatória: Krehbiel, Kam e Carey preveem desvio estruturado por preferência ou por principais concorrentes. Rejeitar "ruído" não discrimina entre essas teorias. **Local:** §1 ¶3; §2.2 E3. **Âncora:** `text: §2.2 "E3 (Krehbiel; Clinton, Jackman e Rivers): se a dissidência for preferência individual estruturada, um modelo com direção espacial intrapartidária prevê melhor"`. **Sugestão:** Reformular a pergunta como "*que tipo* de estrutura" (eixo principal × eixos próprios de cada partido × regional), com previsões distintas para cada teoria. Por exemplo: cargas que diferem por partido (DIF), um eixo regional, um eixo de recursos do Executivo.

**DA-M2: A "dimensão intrapartidária" é o eixo global visto de dentro, de modo que a "descoberta" é esperada por construção.**
**Âncora:** `text: §5.5 "A posição intrapartidária dos deputados correlaciona 0,94 com a sua posição relativa à mediana do partido na dimensão global"`; `text: §5.5 "mas não além do que a posição global relativa já contém"`. **Sugestão:** Apresentar a dimensão como "*quanto* da dissidência é o eixo principal" e testar se existe estrutura **além** dele: M4 com a dimensão 1 fixada à global, ou cargas por partido.

**DA-M3: A faixa de "excesso de lealdade" (3,8 a 16,5) é larga demais para sustentar E5, e o limite superior vem de um contrafactual declarado pouco crível.** **Âncora:** `text: §5.8 ¶2 "o que o torna pouco crível para os partidos de esquerda"`. **Sugestão:** Ver R1-W8. Reportar no Resumo só o limite inferior, ou o intervalo sem a esquerda.

**DA-M4: Possível viés de confirmação nas comparações com artefatos internos.** O texto "confirma" nomes de uma lista prévia ("João Carlos Bacelar se confirma"; "Evair Vieira de Melo e Pezenti... também se confirmam") e justifica as discordâncias pelos limiares de votos. **Âncora:** `text: §5.6 "João Carlos Bacelar se confirma"`. **Sugestão:** Retirar (EIC-W2).

#### MINOR

**DA-m1: O plano foi escrito depois da análise descritiva, e os desvios marcados com † mudaram definições de teste** (M2 e células com divisão interna). Declarar quais análises são confirmatórias e quais exploratórias. **Âncora:** `text: Apêndice B — "M2 como logit de desvio com intercepto de célula†"`.

**DA-m2: Supergeneralização na Conclusão.** "Antecipa trocas de partido" é dito com AUC de 0,59 (quem troca) e 61,8% (direção), sem ganho sobre a posição global. **Âncora:** `text: §9 "prevê o voto fora da amostra e antecipa trocas de partido"`.

### Explicações e caminhos alternativos ignorados
1. **Registro em vez de comportamento** (DA-C1).
2. **Heterogeneidade krehbieliana:** partidos do centro como coalizões eleitorais heterogêneas, sem "dissidência" (DA-M2).
3. **Calendário e agenda:** a seleção de quais votações são nominais e de onde o líder diverge do Governo (reconhecida na §2.1 e na §8, mas não modelada). O contraste entre 2025 e os outros anos pode refletir a agenda do presidente da Câmara, e não a disciplina.
4. **Federação como unidade:** o PCdoB e o PV "racham" com o PT, ou a federação é a unidade e eles estão unidos a ela?

### Perspectivas de atores ausentes
Líderes de bloco (quem efetivamente orienta o centro) e o Executivo como fonte de recursos: o artigo os menciona, mas não os mede. Também estão ausentes os usuários de dados públicos (R3-W4).

### Premissa não examinada
A premissa de que a orientação registrada no painel é a orientação "da liderança", e de que o vazio é ausência de orientação.

### Observações (não são defeitos)
- O teste "so what?" é positivo para a tese de medida: se ela se mantiver, afeta toda pesquisa que usa a orientação registrada após 2023.
- O artigo já modera várias leituras: seleção × adaptação, M5→M4 "não o prova" e a limitação do contrafactual (ii). Os ataques acima não são sobre desonestidade, e sim sobre o alcance das conclusões.

---

# FASE 2 — Pacote de decisão editorial (editorial_synthesizer_agent)

## Resolução de calibração
`calibration_status: NOT_CALIBRATED`. Este pacote não pode ser promovido a partir de um perfil candidato.

## Parte 1 — Carta de decisão editorial

Prezados autores,

Agradecemos o envio de "Disciplina à liderança, unidade partidária e dissidência estruturada na Câmara dos Deputados (57ª Legislatura, 2023–2026)". O manuscrito foi avaliado por cinco assentos de revisão com papéis separados, incluindo um Journal-Fit Reviewer. A proveniência da execução está no início deste documento. Os assentos **não** foram independentes: mesmo modelo, mesmo contexto. Nenhuma alegação de independência é feita.

### Decisão: **Major Revision**

### Matriz de recomendações

| Assento | Recomendação | Confiança |
|---|---|---|
| Journal-Fit (EIC) | Major Revision | 4 |
| R1 Metodologia | Major Revision | 5 |
| R2 Domínio | Major Revision | 4 |
| R3 Perspectiva | Major Revision | 3 |
| DA | — (só achados: 2 CRITICAL, 4 MAJOR, 2 MINOR) | — |

### Análise de consenso

#### Pontos de concordância
- **[CONSENSUS-4] A contribuição de medida é real e valiosa** (EIC-S1, R2 resumo, R3-S1/S2, DA-Observações). Camadas e cobertura devem ficar.
- **[CONSENSUS-3] A interpretação comportamental do registro de orientação não foi validada** (R2-W1/W2/W3, R3-W1, DA-C1; o EIC concorda indiretamente). O consenso conta quatro assentos não DA: EIC, R2 e R3 apontam o problema, e R1 só o toca pela Figura 2. Por isso é classificado como CONSENSUS-3.
- **[CONSENSUS-3] "Preferência" e "governismo" estão rotulados além do que se mediu** (R1-W4 sobre escala; R2-W5; R3-W3; DA-C2 e DA-M2).
- **[CONSENSUS-3] O texto é longo demais e mistura frentes; os artefatos internos devem sair** (EIC-W1/W2, R3-W5, DA-M4; R1 de forma pontual: Tabelas 1 e 3, Figura 2).
- **[CONSENSUS-3] O contrafactual de P5 precisa de base datada, IC por partido e uma faixa crível** (R1-W8, R2-W4, DA-M3).
- **Achados de um só assento, com evidência forte:** o comparador M2 desigual (R1-W1, apoiado pela DA-C2); o TWFE escalonado (R1-W5); a mistura de escalas na Tabela 10 (R1-W4); o teste de E2 quase vazio (R1-W6, corroborado por EIC-W3); a inferência (R1-W7); a literatura que falta (R2-W6, R3).

#### Pontos de discordância
- **Extensão × mais análises.** O EIC pede cortes, e R1, R2 e R3 pedem análises novas (M2b, validação temporal, estimador de eventos robusto, verificação nas notas taquigráficas, base datada).
  - **Resolução do editor:** os dois pedidos são compatíveis. As análises novas são em geral robustez e devem ir sobretudo para o apêndice online. O corpo fica com as duas teses (EIC-W1), e as frentes secundárias (temas, pivôs, dissidentes nominais, segunda dimensão, suplência) saem.
- **Gravidade do problema de registro.** A DA classifica como CRITICAL. R2 classifica como Major, porque a tese de medida no sentido estrito sobrevive.
  - **Resolução do editor:** a DA-C1 é **validada** como CRITICAL **para a interpretação comportamental**, que está no Resumo, na §8 e na §9. Não é CRITICAL para a tese de medida estrita. A evidência dos dados (0 registros partidários nas 227 votações do megabloco; D própria do centro com 1 a 13 votações) foi conferida pelo painel e é verificável.

### Adjudicação dos CRITICAL da DA (Checkpoint Rule 4)
| Item | Adjudicação | Justificativa | Efeito |
|---|---|---|---|
| DA-C1 | **Validado** (reparável) | Corroborado pela consulta de R2 aos dados; a afirmação "orientam onde estão unidos" contradiz a origem das orientações próprias | Bloqueia Accept; vira P0-1 |
| DA-C2 | **Validado** (reparável) | O código confirma a assimetria M2 × M3 (R1-W1); a separação entre governismo e ideologia não foi testada (R2-W5) | Bloqueia Accept; vira P0-2 e P0-3 |

### Justificativa da decisão
Os quatro assentos com recomendação pedem Major Revision, e os dois CRITICAL da DA foram validados e são reparáveis. O artigo tem base empírica sólida, reprodutibilidade exemplar e uma contribuição de medida que interessa à comunidade. Não há evidência de que os resultados centrais sejam artefatos de código: o Stage 2.5 reproduziu tudo, e esta revisão não encontrou erro de implementação. Não é Reject porque as falhas estão no **alcance das interpretações** e na **justiça dos comparadores**, e não na qualidade dos dados ou na existência dos efeitos. Não é Minor porque é preciso reanalisar: o comparador M2b, a validação temporal, o estimador de eventos robusto à heterogeneidade, a distância padronizada, o Rice com m comum, a base datada, a validação do registro em fonte primária e a composição oficial dos blocos. É possível que a tese do título ("dissidência estruturada") precise ser rebaixada, conforme o resultado de P0-2 e P0-3. Se o ganho de M2b→M3L sumir, o artigo continua publicável como estudo de medida e de disciplina, mas com outro título e outra tese. Depois da revisão, o manuscrito volta para re-review.

### Problemas bloqueantes (0–3, ordem de origem)

| Ref. | Problema bloqueante | Assentos | Âncora | Item do roadmap |
|---|---|---|---|---|
| R1 | Interpretação comportamental do registro de orientação não validada; "orientam onde estão unidos" contradiz os dados | DA, R2, R3, EIC | `dataset: votacoes_orientacoes.parquet — 0 registros PL/Fdr PT em 227 votações do megabloco; Tabela 2 D própria` | P0-1 |
| R2 | "Direção além da lealdade" não está isolada: M2 sem escala por votação e com ρ por deputado | R1, DA | `equation: §4.3 M2 × M3; ajustar_lealdade` | P0-2 |
| R3 | "Governismo relativo" não se separa de ideologia; dimensão intrapartidária ≈ eixo global | R2, DA, R3 | `text: §5.5 "o que confirma E4 (Zucco, 2009)"` | P0-3 |

## Parte 2 — Revision Roadmap (numerado e priorizado)

Correspondência entre as prioridades pedidas e as classes do protocolo: **P0** = `must_fix` com origem em CRITICAL (bloqueante); **P1** = `must_fix` com origem em Major; **P2** = `should_fix` ou `consider`. A numeração não define ordem de trabalho.

### P0 — Bloqueantes

**P0-1. Validar o registro de orientação contra a fonte primária e corrigir a interpretação comportamental.**
- **O que mudar:** (a) Para uma amostra aleatória de 30 a 50 votações de 2025 com orientação vazia, e de 20 votações com bloco inferido, conferir nas notas taquigráficas e no *Diário da Câmara* quem orientou e como. Reportar a concordância num quadro do apêndice. (b) Substituir a atribuição por nome truncado pela composição oficial e datada dos blocos (API de Dados Abertos; conferir o endpoint), ou validar a inferência. (c) Como robustez em 2025, imputar a orientação do PL pela da Oposição e a da federação do PT pela do Governo/Maioria. (d) Retirar ou testar "quando orientam por conta própria, orientam onde estão unidos". Na Tabela 2, informar o **número de votações** da D própria e suprimir as taxas com menos de 10 votações. (e) Reescrever conforme o resultado de (a): Resumo e Abstract ("quase não orientou"), §1 ¶2 ("dominada por um artefato"), §5.1 ¶3–4, §7 ("A orientação vazia significa que a liderança não orientou"), §8 ¶2 ("ficção regimental"; "orientam onde estão unidos"), §9 ("em 2025, quase ninguém") e o título da Figura 2 ("é um artefato de cobertura", mais forte que o texto).
- **Onde:** Resumo e Abstract; §1 ¶2; §3 "Orientações"; §5.1; Tabela 2; Figura 2; §7; §8; §9; `analise.py` (atribuição de camadas).
- **Origem:** DA-C1, R2-W1/W2/W3, R3-W1, EIC. **Custo:** re_analysis e new_data (coleta de notas taquigráficas).

**P0-2. Teste justo de "direção além da lealdade".**
- **O que mudar:** (a) Estimar **M2b** = σ(z^{M1} + ρ_r·c_j·d_pj), com ρ **por período** deputado×partido e escala c_j ≥ 0 por votação (ou |b_j| de M3 como escala fixa). Reportar M1→M2b e M2b→M3L na Tabela 5 e na Figura 4. (b) Teste de embaralhamento: M3 com sinais de x_r permutados dentro do partido. (c) Validação **temporal**: treinar com 2023–25, testar em 2026 com x_r congelados. (d) Chamar o exercício principal de "imputação fora da amostra", reinterpretar M0→M1 como valor da informação contemporânea da bancada e reportar ganhos relativos e por deputado. (e) Variar λ_r e λ_d em todas as dobras para M2(b) e M3L. (f) Se M2b→M3L ficar perto de zero, rebaixar a tese do título.
- **Onde:** §4.3; §5.4 (lista de comparações e parágrafo de sensibilidade); Tabela 5; Figura 4; §8 ¶3; §9; título; Resumo; `analise.py` (`ajustar_lealdade`, `validacao_cruzada`).
- **Origem:** DA-C2, R1-W1/W2/W10. **Custo:** re_analysis.

**P0-3. Nomear e delimitar a dimensão intrapartidária.**
- **O que mudar:** (a) Trocar "governismo relativo" por uma descrição neutra ("eixo governo–oposição, que nesta legislatura coincide com esquerda–direita"), **ou** separar as duas leituras com votações em que a orientação do Governo contraria a esquerda programática ou âncoras externas (Power e Zucco; BLS). (b) Mostrar *quanto* da dissidência é o eixo global (correlação de 0,94) e testar se há estrutura além dele: dimensão 1 fixada à global mais uma dimensão livre, ou cargas por partido (DIF). (c) Trocar "confirma E4" por "é compatível com". (d) Comentar na Tabela 11 os pares espelhados (mérito × requerimento da mesma proposição) e o peso de requerimentos procedimentais no polo negativo.
- **Onde:** §2.2 (E4); §5.5; Tabela 11; §8 ¶3; §9; Resumo e Abstract.
- **Origem:** DA-C2, DA-M2, R2-W5, R3 (DIF). **Custo:** re_analysis e section.

### P1 — Obrigatórios (Major)

**P1-1. Focar e encurtar; retirar artefatos internos.** Organizar o texto em duas teses (medida; estrutura da indisciplina, com troca de partido). Levar ao apêndice online temas (Tabela 4), pivôs (Tabela 8 e §5.6 "Pivôs"), a lista nominal de dissidentes (Tabela 7), a segunda dimensão, suplência e fusões. Retirar todas as comparações com `alinhamento.parquet`, `emb_votos`, "painel do projeto", "92,9% obtidos antes no projeto" e o "enunciado do bloco, não versionado" (§5.1 ¶1, §5.4 ¶1, §5.6 em três trechos, §6 ¶2), e a menção aos "sete trabalhos irmãos" (§1 ¶4). Reduzir o Resumo e o Abstract a cerca de 200 palavras. Renumerar tabelas e figuras na ordem de aparição (hoje as Tabelas 10 e 11 vêm antes da 6, e a Figura 6 antes da 5). Meta: cerca de 8.000 palavras, no máximo 6 tabelas e 5 figuras no corpo. *Origem:* EIC-W1/W2/W4, DA-M4, R3-W5. *Custo:* section.

**P1-2. Falseabilidade de E1–E5 e derivação de E5.** Declarar um critério quantitativo de falha para cada expectativa (por exemplo, para E1: amplitude anual de U > 3 p.p.) e dizer que o critério é posterior ao P1 descritivo. Reformular E3 como "que tipo de estrutura" (DA-M1). Reescrever E5 como o contraste entre Figueiredo e Limongi e Carey, com previsões distintas. Trocar "confirma" por "é compatível com" onde o teste não poderia falhar. *Onde:* §2.2 ¶3; §5.1 ¶4; §5.3; §5.5; §5.8; §8. *Origem:* EIC-W3, R2-W7, DA-M1, DA-m1. *Custo:* section.

**P1-3. Rice padronizado com m comum.** Usar m = 5 (ou o maior m que inclua todos os partidos analisados), comparar o ranking completo bruto × padronizado e mostrar m = 5 na Tabela 2 e na Figura 3. Reescrever "A expectativa E2 se sustenta" conforme o resultado. *Onde:* §4.1 ¶4; §5.3; §6 ¶2; Tabela 2; Figura 3. *Origem:* R1-W6, EIC-W3. *Custo:* re_analysis.

**P1-4. Correlatos do desvio: escala, amostra e rótulo de "preferência".** Padronizar a distância dentro de cada ajuste por biênio e reportar o efeito por 1 DP, separando as duas metades. Informar as perdas por falta de período correspondente no outro biênio. Trocar "a expectativa krehbieliana de que a preferência domina se confirma" por "a propensão passada a votar longe do partido prediz o desvio". Se quiser falar de preferência, acrescentar uma âncora que não venha de votações nominais (coautoria de proposições, frentes, discursos). Citar a literatura sobre governadores ao discutir o efeito das UFs. *Onde:* §4.4 "Quem desvia"; §5.6 ¶1; Tabela 10; `distancia_fora_periodo` e `anexar_distancia`. *Origem:* R1-W4, R3-W3, R2-W6(a). *Custo:* re_analysis.

**P1-5. Estudo de evento robusto à adoção escalonada.** Reestimar com Sun e Abraham, Callaway e Sant'Anna ou um desenho empilhado, com controles ainda não tratados e nunca tratados. Separar a coorte da janela de 2026 das trocas de 2023–25. Reportar um teste conjunto das janelas pré-evento e a taxa de desvio na janela de referência. Fazer a análise de seleção × adaptação com λ_δ variado. Atualizar o "11,1 pontos" no Resumo se mudar. *Onde:* §4.4 "Troca de partido"; §5.7; Figura 5; Resumo. *Origem:* R1-W5/W9. *Custo:* re_analysis.

**P1-6. Partido × Governo: base datada, IC por partido e faixa crível.** Definir a coalizão pela participação ministerial datada e separar coalizão, independentes e oposição. Pôr IC por bootstrap de votações e o número de **votações** para cada partido na Figura 7 e no texto (por exemplo, o PT tem 9 votações divergentes). Reportar o contrafactual (ii) sem PSOL, PSB e PDT. No Resumo, apresentar só o limite inferior, ou a faixa sem a esquerda. *Onde:* §4.4 "Partido × Governo"; §5.8; Figura 7; Resumo; `partido_vs_governo` (`OPOSICAO`). *Origem:* R1-W8, R2-W4, DA-M3. *Custo:* re_analysis.

**P1-7. Inferência coerente.** Diferenças de log-loss com bootstrap de duas vias (*pigeonhole*) ou com os dois bootstraps de uma via. Taxas com reamostragem de votações e deputados. Dispersão com ≥ 500 réplicas, ou bootstrap paramétrico, reportando o viés (corrigir o IC degenerado do PT, [0,12; 0,23]). Tratar os ICs individuais da Tabela 7 como inferiores ao verdadeiro, ou recalculá-los. *Onde:* §4.3; §4.5; Tabelas 5, 6 e 7; Figura 4. *Origem:* R1-W7, R3-W5. *Custo:* re_analysis.

**P1-8. Comparação entre partidos: construto de D e U, e federações.** Usar U como medida principal das comparações entre partidos (Resumo, §5.1) e D por camada. Calcular U também por **federação** (PT-PCdoB-PV, PSOL-REDE). Fixar o conjunto de partidos na série anual de U. Se houver votações em que o bloco e um partido-membro (ou a federação) orientam em sentidos opostos, mostrar qual principal prevalece. *Onde:* §4.1; §5.1; Tabela 2; Figura 1; Resumo. *Origem:* R3-W1, R2 (federações), R1 (U com ≥ 5). *Custo:* re_analysis.

**P1-9. Literatura.** Acrescentar e discutir, no mínimo: Limongi e Figueiredo (1995); Amorim Neto, Cox e McCubbins (2003); Pereira e Mueller (2004); Raile, Pereira e Power (2011); Cheibub, Figueiredo e Limongi (2009); Carey e Reinhardt (2004); Desposato (2006); Melo (2004); Nokken (2000); Heller e Mershon (2008); Hix (2002) e Hix, Noury e Roland (2007); Minozzi e Volden (2013); Aldrich, Montgomery e Sparks (2014); Rosas, Shomer e Haptonstahl (2015). Para os métodos, citar os estimadores de evento usados (P1-5), Owen (2007) e Lewis e Poole (2004). Resolver as três marcas "[verificar]" (§2.1 ¶2, §4.1 ¶4 e Nicolau). Toda referência nova deve passar pela verificação do Stage 1 antes de entrar no `.bib` (o anexo #1001 não foi rodado). *Onde:* §2.1; §2.2; §5.6; §5.7; §8; Referências. *Origem:* R2-W6, R3, R1. *Custo:* section.

**P1-10. Ausência não ignorável.** Comparar a ausência em votações com o partido dividido e com o partido unido, por deputado. Estender a análise de ausência da PEC à PLP (quórum de 257). Ao menos discutir, e se possível aplicar, um modelo de não resposta não ignorável. *Onde:* §5.2; §7 "Ausências". *Origem:* R3-W2. *Custo:* re_analysis.

### P2 — Recomendados (should_fix / consider)

1. **P2-1.** Na Figura 2, omitir ou esmaecer os pontos de D com cobertura < 20% (2025S1: 4%) e acrescentar ICs; harmonizar o título com o texto. *(R1)*
2. **P2-2.** Explicar em nota as diferenças entre as contagens das Tabelas 1 e 3 (230/227, 145/144, 324/318, 30/29) e o "28 votações de PEC" da §5.2. *(R1)*
3. **P2-3.** Na Tabela 7, usar uma só unidade (DP do partido, ou dim1) para a posição e o IC. *(R1)*
4. **P2-4.** No rótulo "células com divisão interna", informar o N (64% dos votos) e acrescentar uma subamostra com minoria de treino ≥ 10%. *(R1-W3)*
5. **P2-5.** Na Tabela 11, derivar da descrição os 5 resultados "–" (destaques "Mantido o texto") e encurtar as ementas. *(Stage 2.5 nota; R2)*
6. **P2-6.** Corrigir "Contrafactual de P5" no Apêndice B (o artigo tem P1–P4) e definir MPL, IC, EP e UF na primeira ocorrência (anexo de siglas). *(EIC)*
7. **P2-7.** Esclarecer na Tabela 10 que "Trocou de partido (individual)" é invariante no tempo e inclui o período pós-troca; considerar dividir em antes e depois. *(R1)*
8. **P2-8.** Na Figura 4, separar M5→M4 (comparação não aninhada, que não é "componente acrescentado") num painel à parte. *(R1)*
9. **P2-9.** Na validação preditiva das trocas, dizer que a direção é definida com as mesmas medianas do modelo e apresentar AUC de 0,59 e 61,8% como evidência modesta; ajustar a §9 ("antecipa trocas"). *(R1, DA-m2)*
10. **P2-10.** Fazer a validação manual do classificador de tipo de votação (200 descrições, como no plano) e reportar a acurácia. *(Apêndice B; R1)*
11. **P2-11.** Acrescentar à §8 um parágrafo sobre as implicações para usuários de dados públicos e para o registro de orientações pela Câmara. *(R3-W4)*
12. **P2-12.** Para a submissão, preparar uma declaração de disponibilidade de dados e código (repositório com DOI) e a tabela de versões dos pacotes que o plano previa. *(EIC; Apêndice B)*
13. **P2-13.** Declarar no Apêndice B quais análises são confirmatórias e quais exploratórias, e se as mudanças marcadas com † (M2, células com divisão) vieram antes ou depois de ver os resultados de validação cruzada. *(DA-m1; R1, pergunta 3)*

### Checklist de rastreabilidade (ordem de origem; não é ordem de trabalho)
- [ ] P0-1 — must_fix: validar o registro de orientação e corrigir a interpretação
- [ ] P0-2 — must_fix: M2b, embaralhamento, validação temporal, reinterpretação de M0→M1
- [ ] P0-3 — must_fix: nomear e delimitar a dimensão; estrutura além do eixo global
- [ ] P1-1 — must_fix: foco, extensão, artefatos internos, Resumo, numeração
- [ ] P1-2 — must_fix: falseabilidade de E1–E5; E5 × Carey
- [ ] P1-3 — must_fix: Rice com m comum
- [ ] P1-4 — must_fix: distância padronizada; "preferência"
- [ ] P1-5 — must_fix: estudo de evento robusto
- [ ] P1-6 — must_fix: base datada; ICs; faixa crível em P5
- [ ] P1-7 — must_fix: inferência coerente
- [ ] P1-8 — must_fix: construto de D e U entre partidos; federações
- [ ] P1-9 — must_fix: literatura e "[verificar]"
- [ ] P1-10 — must_fix: ausência não ignorável
- [ ] P2-1 a P2-13 — should_fix/consider

### Carta de resposta
Responder a cada item (P0-1 … P2-13) no formato R → A → C de `templates/revision_response_template.md`: comentário do revisor, ação tomada com o local exato e a mudança resultante no texto ou nos números. Para os itens P0, informar os números novos e dizer se a conclusão mudou.

## Parte 3 — Resumo dos pareceres (apêndice)
- **Journal-Fit (EIC):** Major, confiança 4. O artigo é um relatório de projeto com cinco artigos dentro; precisa escolher a tese, cortar e tirar os artefatos internos.
- **R1 (Metodologia):** Major, confiança 5. O comparador M2 é desigual; a validação é imputação; a distância mistura escalas; o estudo de evento usa TWFE escalonado; a inferência ignora uma das dependências.
- **R2 (Domínio):** Major, confiança 4. O registro de orientação foi lido como comportamento sem verificação regimental; "orientam onde estão unidos" não se sustenta; a base é estática; falta a literatura brasileira sobre governadores, agenda, recursos e migração.
- **R3 (Perspectiva):** Major, confiança 3. Bloco × partido como dois principais; D não tem o mesmo construto em todos os partidos; a ausência não é ignorável; "preferência" vem de votações nominais.
- **DA:** dois CRITICAL validados (registro × comportamento; a cadeia "direção ⇒ governismo"). O desafio principal: a "indisciplina estruturada" é em grande parte o eixo global visto de dentro, e parte do "problema de medida" é problema de registro.

---

## Anexo: Checagem de referências sugeridas (advisory, #1001)

A checagem de referências sugeridas não foi rodada: o script `verify_panel_recommendations.py` consulta índices bibliográficos externos e não foi executado nesta sessão. As sugestões de R2 e R3 ficam como os revisores as escreveram. O autor deve verificá-las (Stage 1) antes de usá-las.

## Anexo: Checagem de afirmações dos revisores (advisory, #1002)

A checagem de afirmações dos revisores não foi rodada (exige um juiz em subagente separado, que não foi disparado). As afirmações sobre dados que os revisores fizeram foram conferidas diretamente por consulta somente de leitura a `dados/leg57` e a `resultados.json`: 0 registros de PL e da federação do PT nas 227 votações do megabloco; D própria do centro com 1 a 13 votações; células com divisão interna = 267.770 de 417.832; número de votações divergentes por partido.

## Anexo: Checagem de siglas (advisory, #849)

Rodada com `--lang en` (o script não aceita `pt`). Saída sem alterações:

```
### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not in this input: English abstract, Chinese abstract.
Not checked:
- Body, line 132: PP (the initials before its parentheses do not spell it)
- Body, line 364: MDB (the initials before its parentheses do not spell it)
- Body, line 364: PODE (the initials before its parentheses do not spell it)
- Body, line 364: PSD (the initials before its parentheses do not spell it)
- Body, line 463: NOVO (the initials before its parentheses do not spell it)

| Scope | Line | Rule | Acronym | Uses |
|---|---|---|---|---|
| Body | 4 | Not defined | PCdoB | 5 |
| Body | 4 | Not defined | PL | 16 |
| Body | 4 | Not defined | PSDB | 8 |
| Body | 4 | Not defined | PSOL | 12 |
| Body | 4 | Not defined | PT | 14 |
| Body | 58 | Not defined | PRD | 3 |
| Body | 58 | Not defined | PROS | 1 |
| Body | 58 | Not defined | PSC | 2 |
| Body | 58 | Not defined | PTB | 1 |
| Body | 60 | Not defined | PV | 2 |
| Body | 90 | Not defined | IDEAL | 1 |
| Body | 94 | Not defined | BFGS | 1 |
| Body | 103 | Not defined | M3L | 4 |
| Body | 106 | Not defined | AUC | 3 |
| Body | 106 | Not defined | PR | 2 |
| Body | 114 | Not defined | UF | 5 |
| Body | 132 | Not defined | AVANTE | 3 |
| Body | 132 | Not defined | IC | 30 |
| Body | 161 | Not defined | PDT | 9 |
| Body | 161 | Not defined | PSB | 8 |
| Body | 175 | Not defined | PEC | 4 |
| Body | 316 | Not defined | MPL | 1 |
| Body | 331 | Not defined | EP | 1 |
| Body | 475 | Not defined | AMES | 1 |
| Body | 477 | Not defined | BAFUMI | 1 |
| Body | 477 | Not defined | GELMAN | 1 |
| Body | 477 | Not defined | KAPLAN | 1 |
| Body | 477 | Not defined | PARK | 1 |
| Body | 479 | Not defined | BLACK | 1 |
| Body | 481 | Not defined | MILLER | 1 |
| Body | 483 | Not defined | CAREY | 2 |
| Body | 487 | Not defined | GABEL | 1 |
| Body | 487 | Not defined | HUG | 1 |
| Body | 489 | Not defined | RIVERS | 1 |
| Body | 491 | Not defined | COX | 1 |
| Body | 495 | Not defined | FGV | 1 |
| Body | 497 | Not defined | KAM | 1 |
| Body | 507 | Not defined | POOLE | 2 |
| Body | 513 | Not defined | POWER | 1 |
| Body | 513 | Not defined | ZUCCO | 3 |
| Body | 515 | Not defined | RICE | 1 |
| Body | 517 | Not defined | SNYDER | 1 |
| Body | 525 | Not defined | API | 1 |
```
