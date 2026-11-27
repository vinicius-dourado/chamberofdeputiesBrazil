# Pré-registro 4-c.3: dissenso fora do Plenário e índice de dissenso multiarena

**Situação:** rascunho, ainda não fechado.
**Desenho de origem:** `docs/desenhos-de-pesquisa-fronteiras.md`, seção 4-c.3.
**Origem teórica:** o controle de pauta desloca o dissenso para arenas anteriores ao voto (MPL 1998, p. 127).

## Pergunta

Disciplina no Plenário e dissenso fora dele são substitutos? Um índice que junte as arenas prediz defecções futuras melhor do que a disciplina passada no Plenário?

## Indicadores (deputado × votação ou deputado × proposição; leg57 principal, leg55–56 réplica)

| # | Indicador | Definição operacional | Dados |
|---|---|---|---|
| I1 | Ausência estratégica | Em exercício na data, votação nominal de Plenário com orientação do partido Sim ou Não, sem voto registrado | `comum.p1.ausencias` |
| I2 | Obstrução ou abstenção contra a orientação | Voto Obstrução ou Abstenção quando o partido orientou Sim; Abstenção quando orientou Não | P1 |
| I3 | Destaque da base contra o governo | DTQ de autoria de deputado de partido da base, sobre proposição em que o governo orientou Sim no texto principal | `proposicoes` (DTQ) + ementa → proposição + `votacoes` |
| I4 | Emenda ao relator do próprio partido | EMP ou EMC do deputado sobre proposição relatada (PRL) por deputado do mesmo partido | **Precisa da proposição principal das acessórias (lacuna L8, ver abaixo)** |
| I5 | Dissenso em comissão | Voto nominal em comissão contrário à orientação do partido | P1 com `so_plenario=False` |

**Lacuna L8 (nova):** PRL, EMC e muitas EMP não trazem na ementa a proposição a que se referem. A API da Câmara traz esse dado em `/proposicoes/{id}` (`uriPropPrincipal`). Enquanto essa coleta não existir, I4 fica fora. I3 usa o título da proposição citado na ementa do DTQ, que cobre a maior parte dos casos; a taxa de ligação é relatada.

## Hipóteses

- **H1 (substituição):** dentro do mesmo deputado, nas proposições com requerimento de urgência aprovado, a defecção no Plenário é menor e o dissenso fora dele (I1, I2, I5) é maior do que nas proposições sem urgência.
- **H2:** a substituição é maior nos partidos de organização descentralizada, ligando aos achados de RLA 2022. Classificação dos partidos a fixar **antes** do fechamento, a partir de RLA 2022.
- **H3 (validade preditiva):** o índice de dissenso fora do Plenário no semestre *s* prediz a defecção no Plenário no semestre *s+1*, controlando pela defecção no Plenário em *s*.

## Construção do índice

- Taxas por deputado e semestre: I1, I2 e I5, mais I3 e I4 quando disponíveis.
- Padronização (z) dentro da legislatura.
- **Índice principal:** a média simples dos z. **Alternativa:** o primeiro componente principal. As cargas são relatadas.

## Especificações

- **H1:** `fora_ip ~ urgencia_p | deputado + partido×mês`, em painel deputado × proposição com ao menos uma votação nominal de mérito. `fora_ip` é a taxa de I1, I2 e I5 nas votações da proposição. Erros agrupados por deputado e por proposição.
- **H3:** `defeccao_{i,s+1} ~ indice_{i,s} + defeccao_{i,s} | partido×semestre`. A comparação de ajuste (AUC e log-loss) com e sem o índice é feita fora da amostra, por legislatura.

## Robustez

- Excluir deputados licenciados no semestre.
- Excluir requerimentos procedimentais.
- Usar só a orientação do partido sem os blocos inferidos (`orientacao_fonte` ≠ "bloco (inferido)").

## Desvios do pré-registro

(nenhum até agora)
