# Pré-registro 6-c.2a: pastas compram apoio? Dois eventos ministeriais no Lula 3

**Situação:** rascunho, ainda não fechado. Fechar = commitar este arquivo sem mudanças pendentes; `estimacao.py` grava o hash do commit nos resultados e se recusa a rodar antes.
**Desenho de origem:** `docs/desenhos-de-pesquisa-fronteiras.md`, seção 6-c.2 (a), mais o segundo evento revelado pela L5.
**Premissa testada:** "pastas como combustível" da coalizão (Limongi 2006, p. 254).
**Papel na pesquisa:** isolado, o desenho não testa a impositividade das emendas. Ele mede quanto o apoio responde às pastas e à filiação formal à base, e esse número serve de referência para 6-c.2b e 4-c.1.

## Eventos (datas conferidas em 27/11/2026; fontes em `analises/comum/config.py`)

| Evento | Data do choque | Tratados | Controles | Janela principal |
|---|---|---|---|---|
| **A. Entrada** | 13/09/2023: posse de Fufuca (PP, Esporte) e Sílvio Costa Filho (Republicanos, Portos e Aeroportos) | PP e REPUBLICANOS | MDB, PSD e UNIÃO, no gabinete desde jan./2023 | 14/03/2023 a 12/03/2024 (±6 meses) |
| **B. Saída sem perda da pasta** | 02/09/2025: a federação União Progressista anuncia a saída de União e PP da base; os ministros ficam | UNIÃO e PP | MDB e PSD | 02/06/2025 a 01/12/2025 (±3 meses) |
| **B'. Volta do União** | 19/12/2025: Gustavo Feliciano (indicação do União) assume o Turismo | UNIÃO | MDB e PSD | 19/09/2025 a 30/03/2026 |

**Sobre as datas:**
- **A:** a negociação foi pública desde jul./2023. Padilha confirmou os dois nomes em 04/08/2023, e a minirreforma foi oficializada em 06/09/2023. O estudo de evento mostra se houve antecipação.
- **B:** em 18/09/2025, a executiva do União deu 24 horas para os filiados deixarem os cargos (Resolução CEN 19/2025). É uma escalada só do União, usada como segundo degrau do evento.
- **B':** a janela começa em 19/09, depois do ultimato, e termina antes da desincompatibilização de abr./2026. A federação União Progressista só foi registrada no TSE em 26/03/2026. Até out./2026, a orientação desses partidos nos dados continua vindo do bloco.

O partido do deputado é o da data da votação. Quem troca de partido dentro da janela é excluído da estimação principal e mantido na robustez.

## Hipóteses

- **H1 (A).** Depois da entrada, a probabilidade de deputados de PP e Republicanos votarem com o governo aumenta em relação aos controles.
- **H1-het (A).** O efeito é maior no PP do que no Republicanos. A executiva do Republicanos declarou que o partido "não fará parte da base" mesmo com Costa Filho no ministério, que foi tratado como cota pessoal de Lula. O Ipea também não conta o Republicanos no gabinete.
- **H2 (B).** Depois do anúncio da saída, o apoio de União e PP ao governo cai em relação aos controles, mesmo com os ministros no cargo.
- **H3 (B').** Com a volta do União ao Turismo, o apoio do União sobe de novo.
- **Leitura conjunta.**
  - Se H1 e H2 se confirmam, o apoio responde à **filiação formal do partido à base**, mais do que à pasta em si.
  - Se só H1 se confirma, a pasta (o recurso) importa mais que o rótulo.
  - Se nenhuma se confirma, a moeda relevante já não são as pastas (ver 6-c.2b e 4-c.1).

## Amostra

- Votações nominais de **Plenário** da leg57 com orientação do governo Sim ou Não. A orientação vem só dos níveis 1 e 2: oficial e bancada "Governo".
- Votos válidos: Sim, Não, Obstrução (= Não). A Abstenção fica fora da medida direcional.

## Desfechos

- **Y1 (principal):** o deputado seguiu o governo (1/0) em todas as votações da amostra.
- **Y2 (secundário):** seguiu o governo nas votações em que a orientação do partido **divergia** da do governo. Na leg57, a orientação "do partido" de PP, União, Republicanos, MDB e PSD vem do **bloco** em mais de 95% dos votos. Por isso Y2 mede o deputado que abandona a orientação do bloco para seguir o governo. A amostra de Y2 depende da orientação do bloco, que pode ser afetada pelo tratamento, então Y2 é interpretado com cautela.
- **Y3 (nível do partido):** a orientação que vale para o partido coincidiu com a do governo (partido × votação). Regra: a orientação **do próprio partido**, quando ele orientou; se não orientou, a **do bloco** a que pertence. É a coluna `orientacao_partido`, cuja fonte está em `orientacao_fonte`. O voto individual do líder não entra.

**O que esperar do Y3 (contagem de votações, sem olhar desfechos):**
- Na janela A, PP e União orientaram por conta própria em 11 e 12 votações; nas demais (cerca de 260), a orientação veio do bloco.
- Republicanos, MDB e PSD orientaram sempre pelo bloco.
- Na janela B, cada partido orientou por conta própria em uma votação. A orientação do MDB (e parte da do PSD) é "bloco (inferido)", atribuída pelo script de coleta a partir do nome do bloco.

Quando tratado e controle estão no mesmo bloco e nenhum dos dois orienta à parte, o Y3 dos dois é idêntico naquela votação. Em 2023, PP e União estavam no mesmo bloco, assim como Republicanos, MDB e PSD. Nessas votações, a diferença tratado − controle é zero por construção. O β do Y3 é identificado sobretudo:
- pelas votações em que o partido se descolou do bloco e orientou à parte;
- pelas diferenças entre blocos, que misturam tratados e controles.

Por isso o Y3 é **descritivo e complementar**, e o Y1 continua como o teste principal.

## Especificação principal

```
Y1_ij = β · Tratado_i × Pós_t + α_i + γ_j + ε_ij
```

- Efeitos fixos de deputado (α) e de votação (γ). O γ absorve a pauta e o placar.
- Erros agrupados por deputado e por votação.
- **Y3:** `Y3_pj = β · Tratado_p × Pós_t + α_p + γ_j`, com erros agrupados por votação. Relatar também quantas votações tiveram orientação própria de cada partido antes e depois do choque.

**Inferência adicional, obrigatória, porque o tratamento é atribuído por partido (poucos clusters):**
- **placebo no tempo:** reestimar com 12 datas fictícias de choque, uma por mês, dentro da leg57 e fora da janela real; relatar o p-valor;
- **placebo de grupo:** trocar os tratados por combinações dos partidos de controle.

**Estudo de evento:** dummies de mês relativo de −6 a +6 (no evento B, de −3 a +3), com referência −1. As tendências pré-choque são reportadas e testadas em conjunto (teste de Wald das defasagens).

## Robustez (todas reportadas, nenhuma escolhida pelo resultado)

1. Incluir os níveis 3 e 4 da orientação (proxy do Líder do Governo).
2. Janelas alternativas: A com ±3 e ±9 meses; B com ±2 meses.
3. Só votações de mérito (texto principal, PEC, emendas e destaques), sem requerimentos procedimentais.
4. Incluir trocadores de partido com o partido da data.
5. Logit com efeitos fixos no lugar do modelo de probabilidade linear.
6. **Antecipação (A):** choque em 04/08/2023, quando Padilha confirmou os nomes, em vez da posse.
7. **B sem a agenda de setembro de 2025:** excluir as votações da PEC 3/2021 (Blindagem) e do PL 2162/2023 (anistia). O anúncio de 02/09 veio junto com o apoio declarado à anistia. Sem essas votações, β mede a mudança de comportamento fora do tema que motivou a saída. Com elas, mede o "pacote" da saída.
8. **Y3 sem orientações inferidas:** excluir `orientacao_fonte = 'bloco (inferido)'`. Na janela B, isso retira o MDB.
9. **B em dois degraus:** dummies separadas para depois de 02/09 e depois de 18/09, esta interagida só com UNIÃO.

## Critérios de decisão

- Confirmação de H1, H2 ou H3: β no sentido previsto, com p < 0,05 no erro agrupado duplo **e** p < 0,10 no placebo no tempo, e sem tendência pré-choque significativa (teste conjunto, p > 0,10).
- Se o pré-choque falhar, o resultado é relatado como **não identificado**, não como nulo.

## Ameaças conhecidas

- **Eleições municipais de out./2024:** ficam fora das janelas principais.
- **Ano eleitoral de 2026:** atinge B'. A janela termina em 30/03/2026 e o resultado é tratado como exploratório.
- **Ala governista:** a imprensa relatou que parte das bancadas de União e PP seguiria com o governo apesar do anúncio. Isso atenua H2 e é exatamente o que o desenho mede: o anúncio formal mudou o voto?

## Desvios do pré-registro

(nenhum até agora)
