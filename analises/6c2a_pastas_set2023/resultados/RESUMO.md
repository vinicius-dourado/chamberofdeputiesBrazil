# 6-c.2a: resultados da estimação pré-registrada

**Rodada:** 27/11/2026, sobre o pré-registro fechado no commit `6fe6b9c`. Números completos em `resultados.json`.
**Leitura:** pelos critérios de decisão do `PREREG.md`. Um efeito só é "confirmado" com:
- p < 0,05 no erro agrupado duplo;
- p < 0,10 no placebo no tempo;
- teste conjunto de pré-tendência com p > 0,10.

Y1 = o deputado seguiu o governo (1/0). Os efeitos estão em pontos percentuais (pp) de probabilidade.

## Evento A: entrada de PP e Republicanos (13/09/2023)

| | β | EP | p (duplo) | Placebo no tempo | Pré-tendência |
|---|---|---|---|---|---|
| Y1 (PP + Republicanos) | **+4,9 pp** | 2,0 | 0,015 | p = 0,15 | p = 0,28 |
| Y1 só PP | +5,9 pp | 2,4 | 0,015 | | |
| Y1 só Republicanos | +3,6 pp | 2,8 | 0,20 | | |
| Y2 (votações em que bloco e governo divergem) | +4,5 pp | 3,2 | 0,17 | | |
| Y3 (orientação do partido/bloco) | +0,9 pp | 0,9 | 0,33 | | |

**Veredito pelo pré-registro: H1 não confirmada formalmente.**
- O efeito vai na direção prevista, é significativo no erro convencional e não há pré-tendência.
- Falha só no placebo no tempo: 1 das 12 datas fictícias (+6,4 pp) supera o efeito real.
- Com 12 placebos, o menor p-valor possível é 1/13 ≈ 0,077. O critério exige que **nenhum** placebo supere o efeito real.

**H1-het, coerente com a previsão:** o efeito é maior no PP (+5,9 pp, p = 0,015) do que no Republicanos (+3,6 pp, p = 0,20), cujo ministro não teve endosso formal do partido.

**Robustez de Y1:**
- Mantêm sinal e significância:
  - janela de ±9 meses (+4,8; p = 0,010);
  - com trocadores de partido (+4,6; p = 0,023);
  - choque no anúncio de 04/08/2023 (+5,5; p = 0,019);
  - orientação com proxy do Líder do Governo (+4,1; p = 0,018);
  - logit (p < 0,001).
- Ficam mais fracas:
  - só votações de mérito (+4,6; p = 0,058);
  - janela de ±3 meses (+2,9; p = 0,19).
- O placebo de grupo é próximo de zero: os controles não diferem entre si (−0,8 a +0,9 pp).

## Evento B: saída de União e PP sem perder a pasta (02/09/2025)

| | β | EP | p (duplo) | Placebo no tempo | Pré-tendência |
|---|---|---|---|---|---|
| Y1 | **−2,5 pp** | 1,9 | 0,19 | p = 0,54 | p = 0,18 |
| Y2 | não identificado | | | | |
| Y3 | degenerado (β = 0, EP = 0) | | | | |

**Veredito pelo pré-registro: H2 não confirmada.** O IC 95% de Y1 vai de cerca de −6,2 a +1,2 pp.

**Padrão no tempo (exploratório, não pré-registrado como teste):**
- A queda se concentra no primeiro mês depois do anúncio: −7,0 pp (EP 3,3). Depois some (meses +1 e +2: −0,9 e +3,5).
- Por isso a janela de ±2 meses dá −6,0 pp (p = 0,025).
- Com a orientação via proxy do Líder do Governo, o efeito é −3,7 pp (p = 0,047).
- Sem as votações da Blindagem e da anistia: −2,3 pp (p = 0,23). A queda não é só a agenda de setembro.
- O ultimato do União em 18/09 não acrescenta nada (−0,3 pp, p = 0,91).

**Por que Y2 e Y3 não funcionaram:**
- **Y2:** nas janelas, só houve votações com divergência entre bloco e governo **depois** do anúncio (16 votações). Sem um "antes", o efeito não é identificado.
- **Y3:** cada partido orientou por conta própria em uma única votação. A orientação é a do bloco e se repete entre tratados e controles, como o pré-registro previa.

## Evento B': volta do União (19/12/2025)

- **Y1:** +1,5 pp, p = 0,59.
- **Pré-tendência rejeitada** (p < 0,001).
- **Veredito pelo pré-registro: não identificado.**
- Só há 47 votações depois do choque, até o fim de março de 2026, já perto do período eleitoral.

## Leitura conjunta (pelo pré-registro)

Nenhuma hipótese passa em todos os critérios. A evidência é **sugestiva** e assimétrica:
- a **entrada** com pasta está associada a cerca de +5 pp de apoio governista, concentrados no PP;
- o **anúncio formal de saída**, sem perda da pasta, produziu no máximo uma queda passageira, de um mês.

O padrão é mais compatível com "a pasta (o recurso) pesa mais que o rótulo de base" do que com o contrário. A afirmação fica no nível de sugestão até haver mais poder estatístico.

## Notas de implementação (não são desvios de especificação)

- O teste de Wald da pré-tendência passou a usar só as defasagens que o pyfixest mantém. Dummies sem variação são descartadas automaticamente.
- Desfechos secundários não identificados (colinearidade com os efeitos fixos) são registrados como `nao_identificado`, em vez de interromper a estimação.

## Lições para os próximos pré-registros

- O placebo no tempo com 12 datas é muito exigente, porque o menor p possível é 0,077. Nos próximos desenhos, usar 25 ou mais datas, ou declarar o limiar em função do número de placebos.
- Desfechos baseados em orientação partidária precisam checar **antes** do fechamento se tratados e controles estão em blocos diferentes e se há votações divergentes dos dois lados do choque.
