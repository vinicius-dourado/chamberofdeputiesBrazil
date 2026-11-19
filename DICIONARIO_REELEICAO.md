# Painel de reeleição – `dados/leg57/reeleicao_painel.parquet`

Uma linha por deputado que exerceu mandato na 57ª legislatura (648, titulares e suplentes).
Eleição analisada: 04/10/2026. Eleição anterior: 2022. Medidas de atuação na Câmara vão até a véspera da eleição.
Gerado por `python montar_painel.py` (depois de `baixar_legislatura.py`, `baixar_cargos.py` e `baixar_tse.py`).

Fora do escopo (pork barrel): `Emendas`, `Pork`, `MédiaExecução`, `TotalEmendas`.

## Variáveis do artigo → colunas

| Artigo | Coluna(s) | Definição | Fonte |
|---|---|---|---|
| VD seleção | `concorreu_reeleicao`, `cargo_disputado_2026`, `situacao_candidatura_2026` | 1 = candidato a dep. federal em 2026; senão o cargo mais alto disputado ou "NÃO CONCORREU" | TSE `consulta_cand_2026`, via CPF |
| VD resultado | `reeleito` | 1 = eleito (QP ou média) em 2026; NA para quem não concorreu. AP: ver `fonte_situacao_2026` | TSE `consulta_cand_2026` / `dados/manual` |
| Concentração94 / 98 | `concentracao_2022`, `concentracao_2026` | votos no município de maior votação ÷ votos no estado | TSE `votacao_candidato_munzona` |
| Competição | `competicao_2022`, `competicao_2026` (e `competicao_bruta_*`) | votos próprios − votos do outro dep. federal mais votado no município-base, ÷ eleitorado apto do município (nota 7) | TSE munzona + `detalhe_votacao_munzona` |
| MesmaBase | `mesma_base` | município de maior votação igual em 2022 e 2026 | TSE |
| Gastos94 / 98 | `gastos_2022`, `gastos_2026`, `gastos_por_eleitor_*`, `gastos_pagos_*`, `receitas_*` | despesas contratadas declaradas; per capita = ÷ eleitorado apto da UF | TSE prestação de contas |
| Governador | `governador` | partido do deputado na eleição de 2022 integra a coligação do governador eleito em 2022 na UF | TSE `consulta_cand_2022` |
| Projetos | `projetos` (aprovados na Câmara: virou norma, foi ao Senado, à sanção ou à promulgação), `projetos_norma`, `projetos_apresentados` | PL/PLP/PEC/PDL de que o deputado é 1º autor | Câmara (proposições) |
| Ausência | `ausencia`, `ausencia_pct`, `votacoes_em_exercicio` | votações nominais do Plenário, nos dias em exercício, sem registro de voto | Câmara (votações, histórico) |
| Mesa | `mesa` | maior cargo: 5 presidente, 4 1º vice, 3 2º vice, 2 secretário, 1 suplente de secretário, 0 nenhum | Câmara `/legislaturas/57/mesa` |
| Permanente / Especial | `permanente`, `especial` (e `cpi`, `*_n_titular`) | maior cargo em comissão permanente / especial: 4 presidente, 3 relator ou 1º vice, 2 2º vice, 1 3º vice ou relator parcial, 0 membro | Câmara `orgaosDeputados-L57` |
| Líder | **não coletado** | listas externas de "mais influentes" (ex.: DIAP); no artigo é endógena e fica fora do modelo principal | – |
| Senior | `senior` | nº de legislaturas anteriores (1–56) em que exerceu mandato de dep. federal | Câmara `/deputados?idLegislatura=` |
| Histleg | `histleg` | nº de mandatos anteriores de vereador, dep. estadual ou distrital | Câmara `/mandatosExternos` |
| Histexec | `histexec` | nº de mandatos anteriores de prefeito, vice-prefeito, governador ou vice | Câmara `/mandatosExternos` |
| Burocracia | `burocracia` (e `afastou_para_executivo`) | ocupação anterior em órgão público (`/ocupacoes`), profissão "servidor público" ou ocupação TSE 2022 "servidor público" | Câmara + TSE |
| Empresa | `empresa` | profissão "empresário" (Câmara) ou ocupação TSE 2022 "empresário" | Câmara + TSE |
| Partpos | `partpos` (e `lideranca_governo`, `lideranca_oposicao`) | maior cargo de liderança de partido/bloco: 3 líder ou presidente, 2 1º vice-líder, 1 vice-líder ou representante | Câmara `/legislaturas/57/lideres` |
| Esquerda / Centro / Direita | `esquerda`, `centro`, `direita`, `ideologia` | partido na eleição de 2026 → `dados/manual/ideologia_partidos.csv` (**classificação provisória**) | manual |
| EntrarCoalizão / SairCoalizão | `entrar_coalizao`, `sair_coalizao`, `trocas_partido` | troca de partido na legislatura (fusões não contam) para partido da base / da base para a oposição. Base = partido cujos deputados seguem a orientação do Governo em ≥ 50% das votações nominais do Plenário (`reeleicao_alinhamento_partidos.parquet`: NOVO, PL e MISSÃO ficam na oposição) | Câmara (votos) |
| Índice | `indice` | % de votos iguais à orientação do Governo (Plenário, orientação Sim/Não) | Câmara (votos) |

## Controles e filtros

`siglaUf`, `sexo`, `idade_eleicao`, `partido_eleicao`, `partido_base_governo`, `condicao_2022` (eleito/suplente em 2022),
`dias_exercicio`, `saida_definitiva` (+ data: renúncia, cassação, morte), `eleito_prefeito_2024`,
`sq_2022`/`sq_2026` (chave do TSE), `votos_2022`/`votos_2026`, `municipio_base_*`.

Para replicar a amostra do artigo (nota 17), excluir quem foi eleito prefeito em 2024, quem morreu ou foi cassado e,
se for o caso, o DF (um só "município").

## Limitações

* **AP 2026**: o TSE ainda não publicou a totalização proporcional do AP. Eleito/suplente vêm da página de resultados do TSE (`dados/manual/tse_situacao_ap_depfed_2026.csv`).
* `mandatosExternos` é declarado ao cadastro da Câmara e pode estar incompleto (329 dos 648 deputados têm registros).
* Ideologia é provisória; a regra de coalizão é empírica (alinhamento ≥ 50%) e pode ser trocada por uma lista de partidos com ministérios.
* As escalas ordinais de Mesa, comissões e liderança seguem a lógica do artigo, mas os pesos são escolhas nossas.
