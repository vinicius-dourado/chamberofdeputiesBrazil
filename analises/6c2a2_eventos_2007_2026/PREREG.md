# Pré-registro 6-c.2a-ii: ganhar ou perder pasta muda o voto? Todas as entradas e saídas de 2007 a 2026

**Situação:** fechado em 27/11/2026, antes de qualquer estimação com dados reais. Aprovado por Vinicius ("vou seguir suas sugestões. Pode rodar o 6-c.2a-ii", 27/11/2026, 14h04). Mudanças daqui em diante vão para "Desvios do pré-registro".
**Antecedente:** 6-c.2a (`analises/6c2a_pastas_set2023`), com dois eventos do Lula 3. Lá, o efeito foi na direção prevista, mas o desenho tinha pouco poder, e nenhuma hipótese passou em todos os critérios.

## Problema de pesquisa

A teoria do presidencialismo de coalizão afirma que o presidente compra apoio legislativo distribuindo pastas: elas são o "combustível" da coalizão (Limongi 2006, p. 254; Cheibub, Przeworski e Saiegh 2002). A evidência usual define a coalizão como os partidos com pasta e mostra que eles votam com o governo. Essa correspondência é **em parte construída pela definição**, porque as pastas tendem a ir para quem já apoia (crítica b.1.1 da Aula 6). A correlação não distingue duas histórias:
- **a pasta causa o apoio;**
- **a pasta registra um apoio que já existia** (seleção).

**Pergunta:** quando um partido **ganha** ou **perde** pasta no meio de um governo, o voto dos seus deputados com o governo muda, em relação a partidos que não mudaram de situação na mesma janela?

## Eventos (regra fixada antes de olhar desfechos; código em `eventos.py`)

**Fonte:** L5 (`dados/gabinetes/ministros.parquet`), com a codificação do Ipea. "Base" é a linhagem com ao menos um ministro filiado e indicado pelo partido. Sob essa codificação, no início do governo Bolsonaro quase nenhum partido conta como base, porque os ministros não eram indicações partidárias.

**Regras de exclusão, aplicadas nesta ordem:**
1. Eventos a até 30 dias do início ou do fim de um governo (trocas de presidente). Exceção: as saídas de mar. a mai./2016, que vão para o grupo do impeachment.
2. Saída seguida de reentrada do mesmo partido em até 30 dias: é troca de ministro, não de partido.
3. Saídas entre 1º/03 e 10/04 de anos de eleição geral: desincompatibilização (o ministro sai para concorrer, o partido não sai).
4. Saídas entre 01/03/2016 e 11/05/2016: grupo **impeachment_2016**, analisado à parte.

**Janela de cada evento:** ±6 meses, cortada no início e no fim do governo e da legislatura e em qualquer outro evento real do mesmo partido.

**Inclusão:** ao menos 20 votações com orientação do governo antes **e** depois, e ao menos um deputado tratado e um de controle.

**Resultado da regra.** São 20 eventos principais (10 entradas e 10 saídas) e 5 do impeachment. Desses, entram na estimação:

| Tipo | Evento | Governo | Votações antes/depois |
|---|---|---|---|
| Entrada | Republicanos (PRB) 18/06/2007 | Lula 2 | 52/37 |
| Entrada | Republicanos (PRB) 02/03/2012 | Dilma 1 | 36/25 |
| Entrada | PL (PR) 03/04/2013 | Dilma 1 | 23/51 |
| Entrada | PSD 08/05/2013 | Dilma 1 | 23/60 |
| Entrada | Republicanos 12/02/2021 | Bolsonaro | 177/350 |
| Entrada | PL 06/04/2021 | Bolsonaro | 223/388 |
| Entrada | PP 04/08/2021 | Bolsonaro | 337/261 |
| Entrada | PP 13/09/2023 | Lula 3 | 110/147 |
| Entrada | União 19/12/2025 | Lula 3 | 145/81 |
| Saída | PTB 28/09/2009 | Lula 2 | 54/62 |
| Saída | PL (PR) 06/07/2011 | Dilma 1 | 33/43 |
| Saída | PSB 03/10/2013 | Dilma 1 | 51/31 |
| Saída | PSB 21/05/2017 | Temer | 84/71 |
| Saída | Cidadania (PPS) 22/05/2017 | Temer | 84/72 |
| Saída | PSDB 14/12/2017 | Temer | 84/59 |
| Saída | PP 02/09/2025 | Lula 3 | 163/164 |
| Saída | União 02/09/2025 | Lula 3 | 163/145 |

**Eventos que ficam fora pela regra de inclusão (decisão tomada só com contagens de votações):**
- entrada do PDT em 29/03/2007: só 17 votações antes, porque a leg53 começa em fev./2007;
- saída do PTB em 05/07/2018: só 16 votações depois, em período eleitoral;
- saída do PSL em 11/11/2019: nenhum partido de controle com o mesmo status. Pela codificação do Ipea, o PSL era o único partido da base;
- **as 5 saídas do impeachment (2016):** de 4 a 10 votações entre a saída e o afastamento de Dilma. O grupo previsto para análise à parte **não é estimável**, e isso é registrado como achado de desenho.

## Grupos de comparação

**Principal:** partidos com o **mesmo status do tratado antes do choque** e sem nenhuma mudança real de status na janela:
- nas entradas, partidos fora da base durante toda a janela;
- nas saídas, partidos dentro da base durante toda a janela.

Deputados que votaram por mais de uma linhagem na janela saem.

**Robustez:** todos os partidos sem mudança de status na janela, qualquer que seja o status. Esta versão permite incluir a saída do PSL.

## Desfecho e amostra

- **Y1:** o deputado seguiu a orientação do governo (1/0).
- Votações nominais de Plenário com orientação do governo Sim ou Não, níveis 1 e 2 (oficial e bancada "Governo").
- Votos Sim, Não e Obstrução (= Não). A Abstenção fica fora.

## Hipóteses

- **H1:** ganhar pasta aumenta o apoio ao governo (β_entrada > 0).
- **H2:** perder pasta diminui o apoio (β_saída < 0).
- **H3 (simetria, sem direção prevista):** |β_entrada| = |β_saída|. Teste: β_entrada + β_saída = 0.
- **Leitura em relação ao problema:**
  - H1 e H2 confirmadas: a pasta tem efeito causal sobre o voto, e a associação não é só seleção.
  - Ambas nulas, com intervalos estreitos: a associação clássica é sobretudo seleção.
  - Assimetria (por exemplo, entrar aumenta e sair não diminui): o apoio cresce com o recurso, mas não se desfaz quando o rótulo de base é perdido.

## Especificação principal (painel empilhado)

```
Y1_ijs = β_E · Entrada_s × Tratado_is × Pós_js + β_S · Saída_s × Tratado_is × Pós_js + α_is + γ_js + ε_ijs
```

- *s* indexa o evento (a "pilha"). α são efeitos fixos de deputado × evento e γ de votação × evento.
- Erros agrupados por deputado e por votação (ids originais, porque a mesma votação pode aparecer em mais de uma pilha).
- **Estudo de evento:** meses relativos de −6 a +6, com referência −1, separados para entradas e saídas. Teste conjunto das defasagens pré-choque para cada tipo.

**Inferência por placebo, obrigatória:** 30 sorteios. Em cada sorteio, cada evento recebe uma data fictícia (dia 15 de um mês) que atende a três condições:
- está no mesmo governo do evento real;
- o partido tem nela o mesmo status de antes do evento real;
- não há mudança real de status do partido a menos de 6 meses dela.

A janela e os controles seguem as mesmas regras. O p-valor é calculado separadamente para β_E e β_S. Com 30 sorteios, o menor p possível é 1/31 ≈ 0,032.

## Robustez (todas reportadas)

1. Controles com todos os partidos de status estável (inclui a saída do PSL).
2. Orientação com os níveis 3 e 4 (proxy do Líder do Governo).
3. Só votações de mérito (texto principal, PEC, emendas e destaques).
4. Janela de ±3 meses (meses relativos de −3 a +2).
5. **Retirar um evento por vez:** amplitude dos β_E e β_S.
6. **Estimativas por evento (exploratório):** um DiD por evento, para mostrar a heterogeneidade entre governos.

## Critérios de decisão

- H1 ou H2 confirmada: sinal previsto, p < 0,05 no erro agrupado duplo, p < 0,10 no placebo e teste de pré-tendência do tipo correspondente com p > 0,10.
- H3: simetria "não rejeitada" se p ≥ 0,10. Não rejeitar não prova simetria, e o intervalo de β_E + β_S é relatado.
- Pré-tendência rejeitada: o efeito daquele tipo é **não identificado**, não nulo.

## Ameaças

- **Seleção na decisão de entrar ou sair:** partidos entram quando já se aproximam do governo. As defasagens pré-choque mostram isso. Se a antecipação aparecer, o β estimado é um limite inferior do efeito "anúncio + posse".
- **Pacote:** a entrada traz junto cargos de segundo escalão e acordos de pauta. O tratamento é "entrar ou sair do governo", não o ministério isolado.
- **Controles heterogêneos:** nas entradas sob Bolsonaro, os controles incluem a oposição de esquerda e o centro sem pasta. O efeito fixo de votação × evento absorve choques comuns, mas não tendências diferentes por grupo. A robustez 6 permite ver se um evento domina.
- **Codificação do Ipea:** os ministros de Bolsonaro de 2019 contam como sem partido. Isso tira eventos de 2019–2020 e faz a entrada de 2021 parecer a "primeira" entrada.

## Desvios do pré-registro

(nenhum até agora)
