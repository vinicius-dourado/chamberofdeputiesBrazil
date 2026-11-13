# Estratégias de gerência da coalizão, 1995–2026

Extensão da Tabela 1 de Bertholini & Pereira, *Pagando o preço de governar* (RAP 51(4), 2017), até o governo Lula 3: proporcionalidade, tamanho e heterogeneidade ideológica da coalizão, mais a fatia de cadeiras da Câmara com os partidos do gabinete. A proporcionalidade segue a medida do Ipea (Almeida, NT 53/2021); a medida de Bertholini & Pereira (coalescência) fica como comparação.

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

* **Proporcionalidade (`prop_kd_v1`, medida principal)**: a medida do Ipea (Almeida, NT 53/2021), o índice de Koppel & Diskin (2009). É o cosseno entre o vetor de ministérios e o vetor de cadeiras dos partidos (×100): 100 quando cada partido tem exatamente a mesma fatia de ministérios e de cadeiras.
  * **v1 (`prop_kd_v1`):** os ministros sem partido entram como um grupo com zero cadeiras. É a Prop_v1 da planilha de Almeida.
  * **v2 (`prop_kd_v2`):** cada ministro sem partido entra individualmente, com zero cadeiras. É a Prop_v2 da planilha. Pesa menos os sem partido.
  * Para os 51 gabinetes de Almeida (até Lula 3-4), o cálculo reproduz Prop_v1 e Prop_v2 com diferença de no máximo 0,05.
* **Coalescência (`coalescencia`, para comparação com Bertholini & Pereira)**: índice de Amorim Neto (2006), CABINET = 1 − ½ Σᵢ|Sᵢ − Mᵢ| (×100), somando sobre os partidos do gabinete.
  * Mᵢ é a fração dos cargos de gabinete com o partido i. Os ministros sem partido entram só no total de cargos (Pereira & Bertholini 2017, nota 2).
  * Sᵢ é a fração de cadeiras do partido i no total de cadeiras dos partidos do gabinete.
  * `coalescencia_np_grupo` trata os sem partido como mais um "partido" com zero cadeiras.
* **Tamanho**: número de partidos com pelo menos um ministério.
* **Cadeiras da coalizão**: % das cadeiras da Câmara com os partidos do gabinete (513 desde 1995; 479, 487 e 503 nas legislaturas anteriores). Até 2022, usa as bancadas de Almeida no início de cada gabinete; em Lula 3, os deputados em exercício no mês.
* **Heterogeneidade**: coeficiente de variação (×100, desvio-padrão amostral) da ideologia dos partidos do gabinete, usando a onda do BLS mais recente anterior ao mês.
  * A série do Atlas vai de −1 a 1, centrada em zero, e é uma transformação linear exata da escala de 2012 (r = 0,9998 nas 72 observações comuns). Por isso foi convertida antes do cálculo.
  * União Brasil recebe a média de DEM e PSL em 2021.
* **Medidas alternativas**: a coalescência e as suas variantes, por mandato, estão em `resultados/proporcionalidade_medidas_alternativas.csv`.

## Resultados (`resultados/tabela1_estendida.csv`)

| Mandato | Proporc. (Ipea v1) | DP | Proporc. v2 | DP | Tamanho | DP | Heterog. | DP | Cadeiras da coalizão (%) | DP |
|---|---|---|---|---|---|---|---|---|---|---|
| Sarney | 94,0 | 6,0 | 97,7 | 1,4 | 2,0 | 0,0 | 35,0† | 0,0 | 64,2 | 3,1 |
| Collor | 19,2 | 8,8 | 55,0 | 11,8 | 2,4 | 1,4 | 6,2 | 1,0 | 27,2 | 7,8 |
| Itamar | 37,4 | 19,2 | 71,6 | 13,1 | 4,9 | 0,8 | 34,2 | 9,8 | 57,8 | 3,7 |
| Cardoso 1 | 56,3 | 3,4 | 81,3 | 4,6 | 4,7 | 0,5 | 24,2 | 3,7 | 69,9 | 9,8 |
| Cardoso 2 | 68,3 | 4,2 | 90,4 | 2,3 | 3,9 | 0,5 | 22,1 | 1,7 | 65,0 | 10,2 |
| Lula 1 | 76,7 | 4,5 | 79,5 | 4,3 | 7,5 | 0,5 | 49,4 | 4,7 | 60,1 | 7,8 |
| Lula 2 | 82,0 | 2,3 | 82,6 | 1,7 | 9,2 | 1,0 | 41,2 | 1,8 | 68,5 | 3,1 |
| Rousseff 1 | 80,9 | 1,7 | 83,9 | 1,8 | 7,4 | 0,9 | 42,8 | 3,1 | 60,9 | 5,5 |
| Rousseff 2 | 77,7 | 6,9 | 86,3 | 2,1 | 8,7 | 1,2 | 37,3 | 4,0 | 59,7 | 9,3 |
| Temer | 73,6 | 10,7 | 85,6 | 1,6 | 8,2 | 1,6 | 14,1 | 6,5 | 58,3 | 8,8 |
| Bolsonaro | 8,4 | 6,5 | 30,2 | 22,2 | 1,3 | 1,1 | 1,8* | 0,3 | 9,1 | 7,0 |
| Lula 3 | 64,2 | 18,8 | 83,5 | 5,1 | 8,9 | 1,5 | 53,6 | 1,5 | 51,9 | 11,8 |

\* Heterogeneidade de Bolsonaro: média só dos meses com dois ou mais partidos. A proporcionalidade é baixa porque, na maior parte do mandato, quase todos os ministros eram sem partido (de nov/2019 a fev/2021, nenhum partido tinha ministério).
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
* tamanho, cadeiras da coalizão (nº e % da Câmara) e heterogeneidade;
* proporcionalidade (Prop_v1) e proporcionalidade_v2 (Prop_v2), do Ipea/Almeida. Até Lula 3-4, coincidem com a planilha de Almeida;
* coalescência e coalescência com os sem partido em grupo, para comparação com Bertholini & Pereira.

Lula 3 por subperíodo (`resultados/lula3_subperiodos.csv`):

| Período | Proporc. (Ipea v1) | Proporc. v2 | Tamanho | Cadeiras da coalizão (%) | Ministros sem partido |
|---|---|---|---|---|---|
| jan/2023–ago/2025 | 72,7 | 84,5 | 9,8 | 59,3 | 7,5 |
| set/2025–mar/2026 (saída de União e PP) | 72,0 | 89,5 | 8,0 | 41,2 | 10 |
| abr/2026–nov/2026 (desincompatibilizações) | 23,4 | 74,2 | 6,0 | 31,8 | 23 |

## Comparação com as tabelas publicadas

Esta seção usa a coalescência, a medida dos autores, e não a do Ipea.

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

   A versão alternativa (`resultados/lula3_sensibilidade.csv`) mantém União e PP e atribui os substitutos ao partido da pasta. Ela dá proporcionalidade de 71,1 (DP 5,8; v2 83,5), tamanho de 10,3, heterogeneidade de 52,9 e cadeiras da coalizão de 63,7%.
2. **Linhas com confiança baixa:** no CSV de Lula 3, são os substitutos de Direitos Humanos, Pesca e SRI em 2026. Conferir no DOU.
3. **Ministros sem partido:** na medida do Ipea (v1), eles contam como um grupo sem cadeiras, então muitos sem partido derrubam o índice (Bolsonaro: 8,4; Lula 3 a partir de abr/2026: 23,4). A v2 pesa menos esse efeito. Na coalescência é o contrário: os sem partido ficam fora da soma, e um gabinete de um partido só com quase todos os ministros sem partido ainda pontua cerca de 55.
