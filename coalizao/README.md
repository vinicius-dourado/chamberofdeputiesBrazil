# Estratégias de gerência da coalizão, 1995–2026

Extensão da Tabela 1 de *Pagando o preço de governar* (RAP 51(4), 2017) até o governo Lula 3.

```bash
pip install pandas openpyxl pyarrow
python coalizao/indicadores_coalizao.py
```

## Fontes

| Período | Composição do gabinete | Cadeiras na Câmara |
|---|---|---|
| 1995–2022 | Almeida (Ipea, NT 53/2021), `dados_brutos/almeida_ipea_gabinetes.xlsx` | idem (na data de início de cada gabinete) |
| 2023–nov/2026 | `dados_brutos/lula3_gabinete_2023_2026.csv`: codificação ministro a ministro com os critérios de Almeida (ministro partidário se o partido apoia o governo e o indicou ou o reconhece) | mensal, deputados em exercício (`cadeiras_leg57.py`, a partir de `dados/leg57`) |
| Ideologia | `dados_brutos/ideologia_partidos.csv` (**pendente**: Power & Zucco/BLS, colunas `partido;ano;ideologia`) | — |

O gabinete exclui GSI, CGU, AGU, Secom e Banco Central (critério de Almeida). A codificação própria de Lula 3 reproduz os gabinetes Lula 3-2 e 3-4 de Almeida (Koppel–Diskin v1 com diferença de ±0,3 ponto). Veja `resultados/validacao_lula3_almeida.csv`.

## Medidas (painel mensal, dia 15)

* **Proporcionalidade (`coalescencia`)**: índice de coalescência de Amorim Neto, a medida do artigo. Os ministros não partidários entram como um grupo sem cadeiras.
* **`prop_kd_v1` / `prop_kd_v2`**: cosseno de Koppel & Diskin, a medida de Almeida. Reproduz exatamente Prop_v1 e Prop_v2 da planilha.
* **Tamanho**: número de partidos com pelo menos um ministério.
* **Heterogeneidade**: coeficiente de variação (×100) da ideologia dos partidos do gabinete. É calculada quando o arquivo de ideologia existir.

## Resultados (`resultados/tabela1_estendida.csv`)

| Mandato | Proporc. média | DP | Tamanho médio | DP |
|---|---|---|---|---|
| Cardoso 1 | 58,7 | 3,0 | 4,7 | 0,5 |
| Cardoso 2 | 64,0 | 3,9 | 3,9 | 0,5 |
| Lula 1 | 56,5 | 2,2 | 7,5 | 0,5 |
| Lula 2 | 65,6 | 2,8 | 9,2 | 1,0 |
| Rousseff 1 | 61,9 | 1,7 | 7,4 | 0,9 |
| Rousseff 2 | 64,6 | 3,8 | 8,7 | 1,2 |
| Temer | 65,9 | 6,6 | 8,2 | 1,6 |
| Bolsonaro | 9,7 | 7,5 | 1,3 | 1,1 |
| Lula 3 | 59,5 | 12,6 | 8,9 | 1,5 |

Lula 3 por subperíodo (`resultados/lula3_subperiodos.csv`):

| Período | Proporc. | Tamanho | Ministros np |
|---|---|---|---|
| jan/2023–ago/2025 | 64,6 | 9,8 | 7,5 |
| set/2025–mar/2026 (saída de União e PP) | 67,1 | 8,0 | 10 |
| abr/2026–nov/2026 (desincompatibilizações) | 32,4 | 6,0 | 23 |

## Cautelas

1. **Os números não emendam com a Tabela 1 original.** A base Ipea/FGV (2015) do artigo não é pública. Com as composições de Almeida, FHC bate (58,7 contra 59,6; 64,0 contra 61,7), mas os governos petistas saem mais altos (Lula 1: 56,5 contra 49,3; Rousseff 1: 61,9 contra 43,7). Para comparar mandatos, use a série recalculada de 1995 a 2026, não a tabela original misturada com a extensão.
2. **Lula 3 depende de duas escolhas de codificação.**
   * A saída da federação União Progressista do governo, em 02/09/2025, torna não partidários os ministros de União e PP.
   * Os secretários-executivos que assumiram em abril de 2026 são tratados como não partidários.

   A versão alternativa (`partido_alt`: mantém União e PP na base e atribui os substitutos técnicos ao partido da pasta) dá proporcionalidade média de 64,1 (DP 1,7) e tamanho médio de 10,3. Veja `resultados/lula3_sensibilidade.csv`.
3. **Linhas com `confianca` = baixa no CSV de Lula 3** são os substitutos de Direitos Humanos, Pesca e SRI em 2026. Conferir no DOU.
4. **Bolsonaro**: nos gabinetes sem nenhum partido, a proporcionalidade vale 0 por convenção, como em Almeida.
