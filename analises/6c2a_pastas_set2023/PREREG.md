# Pré-registro 6-c.2a: pastas compram apoio? Dois eventos ministeriais no Lula 3

**Situação:** rascunho, ainda não fechado. Fechar = commitar este arquivo sem mudanças pendentes; `estimacao.py` grava o hash do commit nos resultados e se recusa a rodar antes.
**Desenho de origem:** `docs/desenhos-de-pesquisa-fronteiras.md`, seção 6-c.2 (a), mais o segundo evento revelado pela L5.
**Premissa testada:** "pastas como combustível" da coalizão (Limongi 2006, p. 254).

## Eventos

| Evento | Data | Tratados | Controles |
|---|---|---|---|
| **A. Entrada** | 13/09/2023: posse de Fufuca (PP, Esporte) e Sílvio Costa Filho (Republicanos, Portos e Aeroportos) | deputados de PP e REPUBLICANOS | deputados de MDB, PSD e UNIÃO, já no gabinete desde jan./2023 |
| **B. Saída sem perda da pasta** | 18/09/2025: União e PP deixam a base; os ministros ficam | deputados de UNIÃO e PP | deputados de MDB e PSD |
| **B'. Volta do União** | 19/12/2025: Gustavo Feliciano no Turismo | deputados de UNIÃO | deputados de MDB e PSD |

O partido do deputado é o da data da votação. Quem troca de partido dentro da janela é excluído da estimação principal e mantido na robustez.

## Hipóteses

- **H1 (A).** Depois da entrada, a probabilidade de deputados de PP e Republicanos votarem com o governo aumenta em relação aos controles.
- **H1-het (A).** O efeito é maior no PP do que no Republicanos. O Ipea não conta o Republicanos no gabinete (o partido não endossou formalmente o ministro), então o tratamento do Republicanos é mais fraco.
- **H2 (B).** Depois do desembarque, o apoio de União e PP ao governo cai em relação aos controles, mesmo com os ministros no cargo.
- **H3 (B').** Com a volta do União, o apoio do União sobe de novo.
- **Leitura conjunta.** Se H1 e H2 se confirmam, o apoio responde à **filiação formal do partido à base**, mais do que à pasta em si. Se só H1 se confirma, a pasta (o recurso) importa mais que o rótulo. Se nenhuma se confirma, a moeda relevante já não são as pastas (ver 6-c.2b e 4-c.1).

## Amostra

- Votações nominais de **Plenário** da leg57 com orientação do governo Sim ou Não. A orientação vem só dos níveis 1 e 2: oficial e bancada "Governo".
- Votos válidos: Sim, Não, Obstrução (= Não). A Abstenção fica fora da medida direcional.
- **Janelas principais:**
  - A: 6 meses antes e 6 meses depois (14/03/2023 a 12/03/2024). A leg57 só tem votações nominais a partir de 14/03/2023.
  - B: 3 meses antes e 3 depois (18/06/2025 a 18/12/2025). A janela termina antes de B'.
  - B': 19/12/2025 a 30/03/2026. A janela termina antes da desincompatibilização de abr./2026.

## Desfechos

- **Y1 (principal):** seguiu o governo (1/0) em todas as votações da amostra.
- **Y2:** seguiu o governo nas votações em que a orientação do partido **divergia** da do governo. Mede a defecção individual em favor do governo.
- **Y3 (nível do partido):** a orientação do partido coincidiu com a do governo (partido × votação).

**Por que Y1 é o principal e não Y2:** com Y2, a amostra depende da orientação do partido, que é ela mesma afetada pelo tratamento. Depois da entrada, o PP passa a divergir menos do governo, e a amostra de Y2 muda de composição. Por isso Y2 é secundário e interpretado com cautela.

## Especificação principal

```
Y1_ij = β · Tratado_i × Pós_t + α_i + γ_j + ε_ij
```

- Efeitos fixos de deputado (α) e de votação (γ). O γ absorve a pauta e o placar.
- Erros agrupados por deputado e por votação.
- **Inferência adicional, obrigatória, porque o tratamento é atribuído por partido (poucos clusters):**
  - **placebo no tempo:** reestimar com 12 datas fictícias de choque, uma por mês, dentro da leg57 e fora das janelas reais; relatar o p-valor;
  - **placebo de grupo:** trocar os tratados por cada par de partidos de controle.
- **Estudo de evento:** dummies de mês relativo de −6 a +6 (no evento B, de −3 a +3), com referência −1. Tendências pré-choque reportadas e testadas em conjunto (teste F das defasagens).

## Robustez (todas reportadas, nenhuma escolhida pelo resultado)

1. Incluir os níveis 3 e 4 da orientação (proxy do Líder).
2. Sílvio Costa Filho codificado como REPUBLICANOS (`silvio="REPUBLICANOS"`), o que muda os controles de base.
3. Janelas alternativas: A com ±3 e ±9 meses; B com ±2 meses.
4. Só votações de mérito (texto principal, PEC, emendas), sem requerimentos procedimentais.
5. Incluir trocadores de partido com o partido da data.
6. Logit condicional (efeitos fixos de deputado) no lugar do modelo de probabilidade linear.

## Critérios de decisão

- Confirmação de H1/H2/H3: β no sentido previsto, com p < 0,05 no erro agrupado duplo **e** p < 0,10 no placebo no tempo, e sem tendência pré-choque significativa (teste conjunto, p > 0,10).
- Se o pré-choque falhar, o resultado é relatado como **não identificado**, não como nulo.

## Ameaças conhecidas

- **Eleições municipais de out./2024** fora das janelas principais.
- **Ano eleitoral de 2026:** atinge B'. A janela termina em 30/03/2026 e o resultado é tratado como exploratório.
- **Antecipação:** as negociações da entrada foram públicas desde jul./2023. Se a defasagem −2 já for positiva, reestimar com o choque em 01/07/2023 (data a conferir na imprensa antes do fechamento).

## Desvios do pré-registro

(nenhum até agora)
