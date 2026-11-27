# Pré-registro 7-c.2: prefeitos da base eleitoral e apoio ao governo (replicando CFL 2009 no nível municipal)

**Situação:** rascunho, ainda não fechado.
**Desenho de origem:** `docs/desenhos-de-pesquisa-fronteiras.md`, seção 7-c.2.

## Pergunta

Quando muda o alinhamento político dos prefeitos que formam a base eleitoral de um deputado, muda também o apoio desse deputado ao governo federal?

## Tratamento

Para o deputado *d* e a réplica *r*:

```
AlinhaBase_d(prefeitos, B) = Σ_m peso_dm × 1[linhagem do prefeito de m ∈ B]
ΔAlinhaBase_dr = AlinhaBase_d(prefeitos novos, B_r) − AlinhaBase_d(prefeitos antigos, B_r)
```

- `peso_dm`: participação do município *m* nos votos de *d* na eleição que o elegeu. Ligação por `cpf_hash` (ou `nome_nasc_hash`).
- **B_r:** base do governo **na data da posse**, mantida fixa. Assim, Δ varia só porque os prefeitos mudam, não porque a coalizão muda.
- Deputados sem ligação ao TSE saem da amostra. Suplentes de outras eleições, por exemplo, não têm peso municipal. A taxa de ligação é relatada.

## Réplicas

| Réplica | Posse | Legislatura | Pesos (eleição do deputado) | Prefeitos antigos → novos | Troca na Presidência da Câmara em fevereiro? |
|---|---|---|---|---|---|
| 2013 | 01/01/2013 | 54 | 2010 | 2008 → 2012 | sim (Marco Maia → Henrique Alves) |
| 2017 | 01/01/2017 | 55 | 2014 | 2012 → 2016 | não (Rodrigo Maia reconduzido) |
| 2021 | 01/01/2021 | 56 | 2018 | 2016 → 2020 | sim (Maia → Lira) |
| **2025 (principal)** | 01/01/2025 | 57 | 2022 | 2020 → 2024 | sim (Lira → Motta) |

A posse de 2009 não entra: não há votação por município do deputado eleito em 2006 e só 65% dos prefeitos eleitos em 2008 estão na base do TSE. Ela pesa apenas como "prefeitos antigos" da réplica de 2013. Por isso, nessa réplica, os municípios sem prefeito de 2008 conhecido saem do cálculo do Δ.

## Hipóteses

- **H1:** β > 0. Mais prefeitos aliados na base aumentam o apoio ao governo.
- **H2:** o efeito é maior para deputados com votação concentrada (`hhi_municipios` acima da mediana).
- **H3 (mecanismo, depende da L6):** depois da posse, as emendas do deputado migram para municípios de prefeitos aliados, e essa migração explica parte de β.
- **H4 (sinal eleitoral × prefeito no cargo):** se o efeito aparece já entre outubro e dezembro, antes da posse, o mecanismo é o sinal da eleição. Se aparece só a partir de janeiro, o mecanismo é o prefeito no cargo.

## Amostra e janelas

- Votações nominais de Plenário com orientação do governo Sim ou Não (níveis 1 e 2), votos Sim, Não e Obstrução.
- **Período anterior:** 1º de março a 30 de setembro do ano anterior à posse. **Período posterior:** 1º de janeiro a 30 de junho do ano da posse.
- **Excluídos da estimação principal:** outubro a dezembro (eleição e transição). Esse período entra no estudo de evento.

## Especificação principal

```
seguiu_gov_ij = β · ΔAlinhaBase_d × Pós_t + α_i + γ_j + ε_ij
```

- Estimada para a réplica de 2025 e para as quatro réplicas empilhadas. No empilhamento, os efeitos fixos de deputado e de votação são definidos dentro de cada réplica.
- Erros agrupados por deputado e por votação.
- **Estudo de evento:** meses de −9 a +5 em relação à posse, com referência −4 (setembro), ΔAlinhaBase interagido com cada mês.
- **Heterogeneidade por governo:** um β por réplica, para testar se o efeito depende do presidente.

## Robustez

1. Incluir outubro a dezembro no período anterior.
2. Usar as réplicas sem troca na Presidência da Câmara (2017) contra as réplicas com troca, para testar a ameaça da Mesa.
3. Controlar pela proximidade do deputado com o novo Presidente da Câmara: partido do deputado = partido do presidente eleito × Pós.
4. Base B_r = partido do presidente da República apenas, uma definição mais estrita de "aliado".
5. Pesos pela eleição seguinte (para quem foi reeleito), como teste de sensibilidade da medida.

## Critérios de decisão

H1 é confirmada com β > 0, p < 0,05 na réplica principal **e** estimativa empilhada com o mesmo sinal, sem tendência pré-choque significativa (teste conjunto dos meses −9 a −5, p > 0,10).

## Desvios do pré-registro

(nenhum até agora)
