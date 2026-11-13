# Estratégias de gerência da coalizão, 1995–2026

Extensão da Tabela 1 de Bertholini & Pereira, *Pagando o preço de governar* (RAP 51(4), 2017), até o governo Lula 3. O cálculo segue a versão revisada dessa tabela em Pereira & Bertholini (2017), *Coalition Management in Multiparty Presidential Regimes*.

```bash
pip install pandas openpyxl pyarrow
python coalizao/indicadores_coalizao.py   # painel mensal e médias por mandato
python coalizao/gabinetes.py              # indicadores por gabinete (subgabinetes)
```

## Fontes

| Item | Fonte |
|---|---|
| Gabinetes 1995–2022 | Almeida (Ipea, NT 53/2021), `dados_brutos/almeida_ipea_gabinetes.xlsx`. Traz o número de ministros e as cadeiras de cada partido no início de cada gabinete. |
| Gabinetes 2023–nov/2026 | `dados_brutos/lula3_gabinete_2023_2026.csv`, codificado ministro a ministro com os critérios de Almeida e com fonte e grau de confiança em cada linha |
| Cadeiras 2023–2026 | deputados em exercício, mês a mês (`cadeiras_leg57.py`, a partir de `dados/leg57`) |
| Ideologia | Zucco & Power (2023), ondas do BLS de 1990 a 2021, via Atlas do Estado Brasileiro (Ipea), `dados_brutos/atlas_ipea_ideologia_partidos.xlsx`. Convertida para a escala de 1 a 10 de Power & Zucco (2012), `dados_brutos/ideologia_power_zucco_2012.csv` |

## Medidas (painel mensal, no dia 15)

* **Proporcionalidade (`coalescencia`)**: índice de coalescência de Amorim Neto (2006), CABINET = 1 − ½ Σᵢ|Sᵢ − Mᵢ| (×100). A soma é feita sobre os partidos do gabinete.
  * Mᵢ é a fração dos cargos de gabinete com o partido i. Os ministros sem partido entram só no total de cargos (Pereira & Bertholini 2017, nota 2).
  * Sᵢ é a fração de cadeiras do partido i no total de cadeiras dos partidos do gabinete.
  * `coalescencia_np_grupo` é uma variante que trata os sem partido como mais um "partido" com zero cadeiras. Fica só como sensibilidade.
* **Tamanho**: número de partidos com pelo menos um ministério.
* **Cadeiras da coalizão**: % das cadeiras da Câmara com os partidos do gabinete (513 desde 1995; 479, 487 e 503 nas legislaturas anteriores). Até 2022, usa as bancadas de Almeida no início de cada gabinete; em Lula 3, os deputados em exercício no mês.
* **Heterogeneidade**: coeficiente de variação (×100, desvio-padrão amostral) da ideologia dos partidos do gabinete, usando a onda do BLS mais recente anterior ao mês.
  * A série do Atlas vai de −1 a 1, centrada em zero, e é uma transformação linear exata da escala de 2012 (r = 0,9998 nas 72 observações comuns). Por isso foi convertida antes do cálculo.
  * União Brasil recebe a média de DEM e PSL em 2021.
* **Medidas de conferência**: o cosseno de Koppel & Diskin (`prop_kd_v1` e `prop_kd_v2`), usado por Almeida. Está em `resultados/proporcionalidade_medidas_alternativas.csv`.

## Resultados (`resultados/tabela1_estendida.csv`)

| Mandato | Proporc. | DP | Tamanho | DP | Heterog. | DP | Cadeiras da coalizão (%) | DP | Proporc. em Bertholini 2017 |
|---|---|---|---|---|---|---|---|---|---|
| Sarney | 90,7 | 4,3 | 2,0 | 0,0 | 35,0† | 0,0 | 64,2 | 3,1 | — |
| Collor | 60,5 | 5,4 | 2,4 | 1,4 | 6,2 | 1,0 | 27,2 | 7,8 | — |
| Itamar | 69,9 | 5,5 | 4,9 | 0,8 | 34,2 | 9,8 | 57,8 | 3,7 | — |
| Cardoso 1 | 77,8 | 2,8 | 4,7 | 0,5 | 24,2 | 3,7 | 69,9 | 9,8 | 71,4 |
| Cardoso 2 | 81,8 | 2,0 | 3,9 | 0,5 | 22,1 | 1,7 | 65,0 | 10,2 | 73,8 |
| Lula 1 | 64,9 | 2,2 | 7,5 | 0,5 | 49,4 | 4,7 | 60,1 | 7,8 | 65,5 |
| Lula 2 | 69,3 | 1,7 | 9,2 | 1,0 | 41,2 | 1,8 | 68,5 | 3,1 | 69,1 |
| Rousseff 1 | 69,9 | 1,8 | 7,4 | 0,9 | 42,8 | 3,1 | 60,9 | 5,5 | 68,9 |
| Rousseff 2 | 75,6 | 1,0 | 8,7 | 1,2 | 37,3 | 4,0 | 59,7 | 9,3 | 75,6 |
| Temer | 77,6 | 2,3 | 8,2 | 1,6 | 14,1 | 6,5 | 58,3 | 8,8 | 80,4 (só 2016; nossa série: 76,5) |
| Bolsonaro | 39,2* | 26,8 | 1,3 | 1,1 | 1,8** | 0,3 | 9,1 | 7,0 | — |
| Lula 3 | 75,1 | 5,1 | 8,9 | 1,5 | 53,6 | 1,5 | 51,9 | 11,8 | — |

\* Média entre meses sem nenhum partido no gabinete (índice = 0 por convenção) e meses com um a três partidos.
\*\* Média só dos meses com dois ou mais partidos.
† Até 1989 usa a onda de 1990 do BLS, a primeira disponível.

## Por gabinete (`resultados/gabinetes_1985_2026.csv`)

A unidade básica é o gabinete (subgabinete), como na planilha de Almeida:
* **Regra de início:** um novo gabinete começa com A (inauguração de presidente), B (mudança no conjunto de partidos) ou C (mudança relevante de ministro), conforme a aba leiame e a NT 53/2021.
* **Cadeiras:** são as da data de início de cada gabinete.
* **Médias por mandato:** a média por mandato da tabela acima é a média dos gabinetes ponderada pela duração de cada um, porque o painel mensal pega o gabinete em vigor em cada mês.
* **Sarney-1 a Lula 3-4:** composição e cadeiras de Almeida, sem alteração.
* **Lula 3-5 a Lula 3-9:** identificados aqui com os mesmos critérios. Os eventos C são classificação nossa e devem ser revisados.

| Gabinete | Evento | Início | Motivo |
|---|---|---|---|
| Lula 3-5 | C | 27/09/2024 | Macaé Evaristo (PT) substitui Silvio Almeida (sem partido) nos Direitos Humanos |
| Lula 3-6 | C | 10/03/2025 | Padilha (PT) substitui Nísia Trindade (sem partido) na Saúde; Gleisi assume a SRI |
| Lula 3-7 | B | 02/09/2025 | União Brasil e PP deixam o governo |
| Lula 3-8 | C | 21/10/2025 | Boulos (PSOL) substitui Márcio Macêdo (PT) na Secretaria-Geral |
| Lula 3-9 | B | 01/04/2026 | desincompatibilizações: MDB e Rede ficam sem ministros |

O arquivo traz, para cada gabinete:
* início, fim, duração, número de cargos, ministros sem partido e composição;
* tamanho, cadeiras da coalizão (nº e % da Câmara), proporcionalidade (as duas versões da coalescência) e heterogeneidade;
* Prop_v1 e Prop_v2 (Koppel–Diskin). Até Lula 3-4, esses valores coincidem com os da planilha de Almeida.

Lula 3 por subperíodo (`resultados/lula3_subperiodos.csv`):

| Período | Proporc. | Tamanho | Cadeiras da coalizão (%) | Ministros sem partido |
|---|---|---|---|---|
| jan/2023–ago/2025 | 75,8 | 9,8 | 59,3 | 7,5 |
| set/2025–mar/2026 (saída de União e PP) | 81,8 | 8,0 | 41,2 | 10 |
| abr/2026–nov/2026 (desincompatibilizações) | 66,2 | 6,0 | 31,8 | 23 |

## Comparação com as tabelas publicadas

* **Pereira & Bertholini (2017)**:
  * **Governos do PT e Rousseff 2:** a diferença é de 1 ponto ou menos (`resultados/comparacao_bertholini_2017.csv`).
  * **FHC:** nossa série fica 6 a 8 pontos acima. A explicação mais provável é que Bertholini conte mais cargos com status de ministro ocupados por não partidários na era FHC. Com a sua planilha de ministros mais três cargos sem partido (AGU, BC, Casa Militar), o FHC cai para 76–77.
  * **Tamanho:** bate (FHC 4,7 e 3,9 contra 4,6 e 4,0; Lula 2 9,2 contra 9,1).
* **RAP (2017), Tabela 1**: a proporcionalidade publicada não se reproduz.
  * Com os próprios números do texto (Rousseff 1: 37 cargos, 17 do PT, 6 do PMDB), a coalescência dá cerca de 60 a 70, e não 43,7.
  * A tabela revisada do próprio autor (2017) traz 68,9 para Rousseff 1.
  * Os testes estão em `diagnostico_replicacao_tabela1.py` e `diagnostico_regra_bertholini.py`.
* **Heterogeneidade:** fica próxima da RAP para o PT (Lula 1: 49,4 contra 48,2). Bertholini (2017) dá ao FHC cerca de 31, contra 22 a 24 aqui; a RAP dava 19,6 a 21,5.

## Cautelas

1. **Escolhas de codificação em Lula 3:**
   * os ministros de União e PP passam a não partidários a partir de 02/09/2025;
   * os secretários-executivos que assumiram em abril de 2026 são tratados como não partidários.

   A versão alternativa (`resultados/lula3_sensibilidade.csv`) mantém União e PP e atribui os substitutos ao partido da pasta. Ela dá proporcionalidade de 75,1 (DP 3,9), tamanho de 10,3 e heterogeneidade de 52,9.
2. **Linhas com confiança baixa:** no CSV de Lula 3, são os substitutos de Direitos Humanos, Pesca e SRI em 2026. Conferir no DOU.
3. **Bolsonaro:** com a fórmula literal, um gabinete com um único partido e quase todo não partidário ainda pontua cerca de 55, porque os não partidários não entram na soma. A média do mandato mistura esses meses com meses de índice 0. Leia esse valor com cuidado.
