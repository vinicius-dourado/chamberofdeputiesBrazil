# Pré-registro 3-c.2: o funil da agenda do Executivo

**Situação:** rascunho, ainda não fechado.
**Desenho de origem:** `docs/desenhos-de-pesquisa-fronteiras.md`, seção 3-c.2.

## Pergunta

Quanto da "cooperação" medida nas votações nominais resulta de filtros anteriores ao voto? Esses filtros mudam quando a Presidência da Câmara não é aliada do governo?

## Unidade e período

- **Unidade:** proposição do Executivo dos tipos PL, PLP, PEC e MPV, apresentada de 2007 a 2025 (`dados/executivo/proposicoes_executivo.parquet`).
- **Fora da amostra:**
  - PLN, que tramita no Congresso e não na Câmara;
  - mensagens (MSC), TVR e outros atos sem conteúdo legislativo;
  - proposições apresentadas depois de 30/06/2026 (seguimento curto demais).
- **Painel proposição × mês:** da apresentação até o primeiro evento terminal ou até 24 meses, o que vier antes. Proposições sem evento terminal nesse prazo são censuradas.

## Eventos do funil (fonte: `tramitacoes_executivo`)

| Evento | Definição |
|---|---|
| E1 chegou ao Plenário | primeira tramitação com `siglaOrgao = 'PLEN'` e descrição de discussão ou votação |
| E2 votada nominalmente | `proposicao_id` aparece em `votacoes` de Plenário com `tem_votos_nominais` |
| E3 aprovada na Câmara | tramitação "Aprovação de Proposição em Plenário" ou "(Plenário)" |
| T1 norma jurídica (terminal) | "Transformação em Norma Jurídica" |
| T2 perdeu eficácia (terminal, MPV) | "Perda de eficácia" |
| T3 arquivada ou retirada (terminal) | "Arquivamento" ou "Retirada pelo(a) Autor(a)" |

## Alinhamento da Presidência da Câmara (variável no tempo, mensal)

- **Principal (dummy):** a linhagem do partido do Presidente da Câmara está na base do governo no dia 15 do mês (`comum.gabinetes.base_na_data`).
- **Contínua:** proporção de votos dos deputados do partido do Presidente da Câmara que seguiram o governo no mês anterior (P1, níveis 1 e 2).

## Hipóteses

- **H1:** com Presidente da Câmara não alinhado, cai o risco mensal de E1 (chegar ao Plenário).
- **H2:** para MPV, com Presidente não alinhado, sobe o risco de T2 (perda de eficácia) em relação a T1.
- **H3 (assinatura da seleção):** entre as proposições votadas nominalmente, a taxa de aprovação **não** cai, ou cai menos que a queda de H1.
- **H4 (depende de coleta, fica fora da primeira rodada):** a distância entre o texto enviado e a norma publicada cresce com Presidente não alinhado.

## Especificação principal

Modelo de risco em tempo discreto, estimado como probabilidade linear no painel proposição × mês:

```
1[evento no mês t]_pt = β · alinhado_t + f(meses desde a apresentação) + tipo_p × governo_p + ε_pt
```

- f(·) é um conjunto de dummies de duração.
- Erros agrupados por proposição e por mês.
- Os riscos competitivos são estimados em equações separadas para T1, T2 e T3, com as observações em risco.
- **H3:** probit de seleção (Heckman). Primeiro estágio: chance de ser votada nominalmente. Segundo estágio: aprovação. A variável de exclusão é a atividade do Plenário no mês, medida pelo log do número de votações nominais não relacionadas à proposição.
  - **Fragilidade admitida:** a exclusão é contestável, porque o Plenário pode ser mais ativo justamente quando a pauta do governo avança. Por isso H3 é relatada também na forma descritiva: taxas de aprovação condicionais por alinhamento.

## Robustez

- Só MPV.
- Só PL e PLP.
- Excluir o período da Presidência interina de jul./2016.
- Usar a medida contínua de alinhamento.
- Com efeitos fixos de governo × ano.

## Ameaça central

O Executivo antecipa o filtro e deixa de enviar o que não passaria. Teste: o número de proposições enviadas por mês é o desfecho em uma regressão sobre `alinhado_t` com efeitos fixos de governo.

## Desvios do pré-registro

(nenhum até agora)
