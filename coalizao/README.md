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
* **Heterogeneidade**: coeficiente de variação (×100, desvio-padrão amostral) da ideologia dos partidos do gabinete, usando a onda do BLS mais recente anterior ao mês.
  * A série do Atlas vai de −1 a 1, centrada em zero, e é uma transformação linear exata da escala de 2012 (r = 0,9998 nas 72 observações comuns). Por isso foi convertida antes do cálculo.
  * União Brasil recebe a média de DEM e PSL em 2021.
* **Medidas de conferência**: o cosseno de Koppel & Diskin (`prop_kd_v1` e `prop_kd_v2`), usado por Almeida. Está em `resultados/proporcionalidade_medidas_alternativas.csv`.

## Resultados (`resultados/tabela1_estendida.csv`)

| Mandato | Proporc. | DP | Tamanho | DP | Heterog. | DP | Proporc. em Bertholini 2017 |
|---|---|---|---|---|---|---|---|
| Sarney | 90,7 | 4,3 | 2,0 | 0,0 | 35,0† | 0,0 | — |
| Collor | 60,5 | 5,4 | 2,4 | 1,4 | 6,2 | 1,0 | — |
| Itamar | 69,9 | 5,5 | 4,9 | 0,8 | 34,2 | 9,8 | — |
| Cardoso 1 | 77,8 | 2,8 | 4,7 | 0,5 | 24,2 | 3,7 | 71,4 |
| Cardoso 2 | 81,8 | 2,0 | 3,9 | 0,5 | 22,1 | 1,7 | 73,8 |
| Lula 1 | 64,9 | 2,2 | 7,5 | 0,5 | 49,4 | 4,7 | 65,5 |
| Lula 2 | 69,3 | 1,7 | 9,2 | 1,0 | 41,2 | 1,8 | 69,1 |
| Rousseff 1 | 69,9 | 1,8 | 7,4 | 0,9 | 42,8 | 3,1 | 68,9 |
| Rousseff 2 | 75,6 | 1,0 | 8,7 | 1,2 | 37,3 | 4,0 | 75,6 |
| Temer | 77,6 | 2,3 | 8,2 | 1,6 | 14,1 | 6,5 | 80,4 (só 2016; nossa série: 76,5) |
| Bolsonaro | 39,2* | 26,8 | 1,3 | 1,1 | 1,8** | 0,3 | — |
| Lula 3 | 75,1 | 5,1 | 8,9 | 1,5 | 53,6 | 1,5 | — |

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
* tamanho, proporcionalidade (as duas versões da coalescência) e heterogeneidade;
* Prop_v1 e Prop_v2 (Koppel–Diskin). Até Lula 3-4, esses valores coincidem com os da planilha de Almeida.

Lula 3 por subperíodo (`resultados/lula3_subperiodos.csv`):

| Período | Proporc. | Tamanho | Ministros sem partido |
|---|---|---|---|
| jan/2023–ago/2025 | 75,8 | 9,8 | 7,5 |
| set/2025–mar/2026 (saída de União e PP) | 81,8 | 8,0 | 10 |
| abr/2026–nov/2026 (desincompatibilizações) | 66,2 | 6,0 | 23 |

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

## Proporcionalidade "entregue": cadeiras × votos efetivamente entregues (`proporcionalidade_entregue.py`)

```bash
python coalizao/proporcionalidade_entregue.py
```

### Ideia

A coalescência compara a fatia de ministérios de cada partido (Mᵢ) com a sua fatia de **cadeiras** na coalizão (Sᵢ). Pela lei de Gamson, isso mede a proporcionalidade em relação ao **potencial** de votos: supõe que cada deputado de um partido do gabinete é um voto do governo. Mas os partidos entregam esse potencial de forma muito desigual. Um partido com 59 deputados que apoia o governo em 60% das votações rende menos votos que um de 45 deputados que apoia em 90%.

A versão "entregue" troca só o Sᵢ e mantém Mᵢ, os gabinetes e os ministros sem partido:

  Sᵢᵉ = cadeirasᵢ × governismoᵢ / Σⱼ (cadeirasⱼ × governismoⱼ)  (j = partidos do gabinete)

  CABINETᵉ = 1 − ½ Σᵢ |Sᵢᵉ − Mᵢ| (×100)

Se Sᵢᵉ estiver mais perto de Mᵢ do que Sᵢ, o presidente distribui ministérios em proporção aos votos que **recebe**, mais do que aos votos que **poderia receber**.

### Governismo (taxa de apoio ao governo)

A partir de `dados/leg<N>/votos.parquet` (votos nominais com a orientação do líder do Governo):

* **Universo:** só o plenário (`siglaOrgao == 'PLEN'`) e só as votações em que o Governo orientou **Sim** ou **Não**. Ficam fora "Liberado", a orientação de obstrução do próprio governo e as votações sem orientação do governo.
* **Voto válido:** Sim, Não, Obstrução ou Abstenção. Só o voto igual à orientação conta como apoio. **Obstrução e abstenção contam como não apoio**, porque, com orientação Sim/Não, obstruir nega quórum e abster-se nega o voto. "Artigo 17" (presidente da Casa) e ausências ficam fora. `taxa_estrita_*` (só Sim/Não no denominador) fica como sensibilidade.
* **Taxa do partido:** votos alinhados ÷ votos válidos, somados sobre todos os deputados e votações. É uma taxa agregada, e não a média dos deputados. Por isso pesa mais o deputado que vota mais.
* **Janelas:** taxa no mês (`taxa_mes`), móvel de 3 e de 6 meses (`taxa_3m` e `taxa_6m`, sem atravessar a troca de mandato) e do mandato inteiro. O painel mensal usa a janela de 6 meses. Os meses sem votações na janela (jan–fev/2023) recebem o primeiro valor observado.
* **Gabinetes:** taxa de todas as votações entre o início e o fim do gabinete.
* **Variante com ausência (`*_presenca`):** entrega = votos alinhados ÷ (cadeiras em exercício × nº de votações) = taxa entre os presentes × fração de presença. Assim, quem não aparece também deixa de entregar.
* **Variante "disputadas" (por gabinete):** só as votações em que a Oposição (ou, na falta, a Minoria) orientou diferente do governo. Ela retira as votações consensuais, em que até o PL acompanha o governo (o PL tem taxa de 31% em Lula 3).
* **Siglas:** harmonizadas com `NORM` (UNIÃO→UNIAO, REPUBLICANOS→REP, PMDB→MDB, PR→PL, PRB→REP…), mais SOLIDARIEDADE→SD e PTN/PODEMOS→PODE.

### Retorno ministerial por voto entregue

Para cada partido do gabinete, retorno = (fração dos ministérios **partidários**) ÷ (fração dos votos entregues da coalizão).
* 1 = proporcional;
* > 1 = sobrerrepresentado, com mais ministérios por voto entregue;
* < 1 = sub-representado.

`retorno_potencial` faz o mesmo com as cadeiras. Usamos os ministérios partidários no numerador para que a média da coalizão seja 1. A coalescência, por sua vez, usa todos os cargos.

### Resultados de Lula 3 (`resultados/proporcionalidade_entregue_gabinetes.csv`)

| Gabinete | Período | Votações | Cadeiras | Entregue | Dif. | Entregue c/ ausência | Só disputadas |
|---|---|---|---|---|---|---|---|
| Lula 3-1 | jan–set/2023 | 110 | 79,7 | 82,0 | +2,3 | 82,4 | 82,2 |
| Lula 3-2 | set–dez/2023 | 128 | 75,6 | 78,9 | +3,3 | 80,9 | 80,3 |
| Lula 3-3 | jan–abr/2024 | 36 | 77,1 | 80,4 | +3,3 | 82,0 | 82,1 |
| Lula 3-4 | abr–set/2024 | 109 | 75,6 | 82,1 | +6,5 | 83,9 | 85,4 |
| Lula 3-5 | set/2024–mar/2025 | 90 | 73,8 | 78,7 | +4,9 | 81,0 | 80,6 |
| Lula 3-6 | mar–set/2025 | 163 | 72,6 | 79,2 | +6,5 | 81,3 | 81,1 |
| Lula 3-7 | set–out/2025 | 40 | 79,4 | 82,8 | +3,3 | 82,9 | 82,9 |
| Lula 3-8 | out/2025–mar/2026 | 149 | 82,4 | 82,8 | +0,5 | 82,9 | 82,9 |
| Lula 3-9 | abr–nov/2026 | 49 | 66,2 | 66,2 | 0,0 | 66,2 | 66,2 |

Painel mensal (`proporcionalidade_entregue_mensal.csv` e `proporcionalidade_entregue_resumo.csv`):

| Período | Cadeiras (DP) | Entregue (DP) | Dif. | Entregue c/ ausência |
|---|---|---|---|---|
| Lula 3, todo o mandato | 75,1 (5,1) | 78,3 (5,9) | +3,2 | 79,4 |
| jan/2023–ago/2025 | 75,8 (2,6) | 80,2 (1,9) | +4,3 | 81,7 |
| set/2025–mar/2026 | 81,8 (1,6) | 83,6 (0,5) | +1,8 | 83,8 |
| abr/2026–nov/2026 | 66,2 (0,0) | 66,2 (0,0) | 0,0 | 66,2 |

Partidos de Lula 3, com médias ponderadas pela duração dos gabinetes em que tiveram ministério (`proporcionalidade_entregue_partidos.csv`):

| Partido | Governismo | Só disputadas | Peso potencial | Peso entregue | Dif. (p.p.) | Retorno potencial | Retorno entregue |
|---|---|---|---|---|---|---|---|
| União | 0,68 | 0,59 | 19,5% | 16,1% | −3,5 | 0,59 | 0,72 |
| PSD | 0,78 | 0,70 | 17,9% | 16,2% | −1,6 | 0,74 | 0,80 |
| MDB | 0,76 | 0,69 | 15,3% | 13,8% | −1,5 | 0,78 | 0,85 |
| PP | 0,76 | 0,68 | 15,8% | 14,6% | −1,2 | 0,24 | 0,26 |
| PSB | 0,92 | 0,92 | 6,0% | 6,5% | +0,5 | 1,62 | 1,46 |
| PCdoB | 0,97 | 0,99 | 3,3% | 3,8% | +0,5 | 1,49 | 1,29 |
| PDT | 0,90 | 0,89 | 6,4% | 6,9% | +0,5 | 0,73 | 0,69 |
| PT | 0,98 | 0,99 | 26,6% | 30,9% | +4,3 | 1,60 | 1,36 |

### Governos anteriores (legislaturas 55 e 56)

Os votos de 2015 a 2022 vêm de `python baixar_legislatura.py --legislatura 55` (e `56`), que gera os parquets em `dados/leg55` e `dados/leg56`. São cerca de 56 MB de parquet e alguns minutos de download. Os CSVs brutos ficam em `dados/brutos`, fora do git.
* **Correção no download:** de 2019 a 2022, a bancada do Governo aparece como "GOV." nos arquivos da Câmara, e o parser não a reconhecia. Sem a correção em `baixar_legislatura.norm`, a orientação do governo só existia em 2020–2021. Com ela, há orientação Sim/Não em 70% a 88% das votações do plenário em todos os anos de 2015 a 2022.
* **Composições:** os gabinetes de Almeida (`comp_almeida()`), com as cadeiras da data de início.

| Mandato | Cadeiras (DP) | Entregue (DP) | Dif. | Entregue c/ ausência | Governismo médio da base |
|---|---|---|---|---|---|
| Rousseff 2 (fev/2015–mai/2016) | 75,6 (1,0) | 79,1 (2,1) | +3,6 | 80,4 | 0,79 |
| Temer | 77,6 (2,3) | 78,2 (2,4) | +0,6 | 79,1 | 0,93 |
| Bolsonaro | 39,2 (26,8) | 39,2 (26,8) | 0,0 | 39,2 | — |
| Lula 3 | 75,1 (5,1) | 78,3 (5,9) | +3,2 | 79,4 | 0,84 |

* **Rousseff 2:** tem o mesmo padrão de Lula 3. O PT é sobrerrepresentado (retorno de 1,92 por cadeira e de 1,64 por voto) e entrega 93%. PP (64%), PSD e PTB (71–73%) entregam menos. A diferença é de +5,0 em Dilma 2-1. Dilma 2-3 (abr–mai/2016) tem só 4 votações e não deve ser interpretado.
* **Temer:** a base vota com o governo em cerca de 93% das vezes e de modo homogêneo, com o PSB como exceção (80%). Por isso as duas réguas quase coincidem (+0,6). A proporcionalidade de Temer não depende da escolha entre potencial e entregue.
* **Bolsonaro:** a diferença é zero por construção. Com 1 a 3 partidos e 16 a 18 ministros sem partido, Sᵢ > Mᵢ para todo partido, e o índice não depende de S (ver o item 4 abaixo).

### O que muda na interpretação

1. **A coalizão de Lula 3 é mais proporcional em votos entregues do que em cadeiras** (cerca de 3 pontos no mandato e até 6,5 pontos em alguns gabinetes). A desproporção medida pela lei de Gamson vem, em boa parte, de o PT ter mais ministérios do que as suas cadeiras justificam e de o "centrão" do gabinete (União, PSD, MDB, PP) ter menos. Como o PT entrega quase 100% e esses partidos entregam de 68% a 78%, o peso real do PT cresce e o dos aliados de centro-direita encolhe. Os dois pesos se aproximam da distribuição de ministérios. Parte do que parecia "pagamento abaixo do preço" ao centrão reflete o fato de esse apoio ser parcial.
2. **O centrão continua sub-representado mesmo em votos entregues** (retorno de 0,7 a 0,85). O PP é o caso extremo (0,26): um ministério para cerca de 15% dos votos entregues da coalizão. O sobrepreço do PT cai de 1,60 para 1,36, mas não some.
3. **A diferença é maior quando o apoio dos aliados cai** (Lula 3-4 e 3-6, com governismo médio da coalizão abaixo de 0,8). Ela praticamente desaparece depois da saída de União e PP (Lula 3-8), quando sobra uma base mais homogênea.
4. **Os gabinetes com muitos ministros sem partido ficam insensíveis à mudança.** Quando ΣMᵢ dos partidos é pequeno e Sᵢ > Mᵢ para todos eles (Lula 3-9, com 23 sem partido), Σ|Sᵢ − Mᵢ| = 1 − ΣMᵢ, qualquer que seja a distribuição de S. O índice então só mede quantos cargos foram para partidos, e não para quais. É uma propriedade da operacionalização de Pereira & Bertholini, e não dos dados.

### Limitações

* **Endogeneidade:** o governismo é, em parte, consequência dos ministérios. A versão "entregue" mede quanto do apoio recebido é recompensado, e não quanto o presidente "deveria" pagar ex ante.
* **Votações consensuais:** elas inflam a taxa de todos os partidos, até da oposição. A variante "disputadas" corrige isso e dá resultados muito parecidos, com União, MDB, PSD e PP de 7 a 10 pontos mais baixos.
* **Agenda:** o governo escolhe o que orienta. Partidos com pauta própria podem ter taxas diferentes sem que isso signifique menos apoio nas votações decisivas. Não há ponderação pela importância da votação (MPs, PECs, LDO).
* **Unidade partidária:** a taxa é do partido inteiro. O aliado que "entrega" pode ser só a ala que tem o ministro. Aqui não se mede a entrega por ministro.
* **Cobertura temporal:** em Dilma 2-3 há só 4 votações. As votações nominais de 2023 começam em 14/03/2023. O 2º semestre de 2026 (eleições) tem poucas votações (49 no Lula 3-9).
* **Presença:** a variante usa as cadeiras em exercício no dia 15 de cada mês como denominador, o que é uma aproximação. Com mudanças de partido no meio do mês, a presença pode passar de 1 e é truncada.
