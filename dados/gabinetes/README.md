# dados/gabinetes: partidos no ministério (lacuna L5)

| Arquivo | Conteúdo |
|---|---|
| `ministros.parquet` | Um registro por ministro e pasta, de Sarney a Lula 3 (738 linhas). Colunas: `governante`, `gov_inicio`, `gov_fim`, `classificacao`, `ministerio`, `partido_pasta`, `ministro`, `min_inicio`, `min_fim`, `partido_ministro`, `fonte`, `obs`. |
| `proporcionalidade.parquet` | Índice de proporcionalidade ministérios × cadeiras por gabinete (`prop_v1`, `prop_v2`), com a composição (`partido(ministros,cadeiras)`), a série alternativa sem o desembarque de União/PP (`prop_*_alt`) e `fonte_serie` ∈ {`ipea_original`, `ponte`, `extensao`}. |
| `proporcionalidade_ministerios_cadeiras_atualizado.xlsx` | A planilha original de Acir Almeida (Ipea, NT 53/2021) com a extensão e as notas na aba `leiame`. |

## Proveniência

- **Até abr./2024:** base de Acir Almeida (Ipea, Nota Técnica nº 53/2021), enviada pelo usuário.
- **Lula 3 de abr./2024 a nov./2026:** completada por pesquisa na web (26/11/2026). Cada linha nova traz a fonte em `fonte`. Datas de exoneração entre 31/03 e 03/04/2026 são aproximadas, e o partido de vários substitutos está marcado "a verificar" em `obs`.
- **Fórmula do índice:** similaridade de cosseno (×100) entre o vetor de pastas e o de cadeiras por partido. A v1 trata os ministros sem partido como um só "partido" com zero cadeiras; a v2 conta cada um separadamente. Reproduz os gabinetes originais do Ipea (teste em `analises/comum/tests/test_gabinetes.py`).
- **Cadeiras na extensão:** deputados em exercício na data (`dados/leg57/deputados_exercicio.parquet`), não a fonte do Ipea. O gabinete `Lula 3-4 (ponte)` mede o efeito dessa troca (cerca de 0,2 ponto em `prop_v1`).

## Convenções de codificação (usadas em `analises/comum/gabinetes.py`)

- `sfp`, `ind` e vazio no partido da pasta = sem partido (`np`).
- Fufuca (Esporte) conta como PP desde set./2023, como no Ipea.
- Anielle Franco (Igualdade Racial) conta como PT a partir de 02/04/2024, inferido do gabinete Lula 3-4 do Ipea.
- **Desembarque (anúncio da federação em 02/09/2025):** as pastas de União (Turismo, Comunicações, Integração) e PP (Esporte) contam como `np` até a volta do União em 19/12/2025. O PP não voltou. A série `*_alt` ignora essa regra.
- Siglas são convertidas para as da Câmara: União → UNIÃO, Rede → REDE, REP → REPUBLICANOS.

## Histórico

- 27/11/2026: a data do desembarque passou de 18/09/2025 (ultimato do União) para 02/09/2025 (anúncio da federação União Progressista). Os valores do índice não mudam, só a data de início do gabinete Lula 3-9.
