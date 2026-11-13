# Notas de passagem: Artigo 5, Frentes parlamentares como assinatura política

Sessão interrompida a pedido do usuário para continuar numa sessão com o plugin Academic Research Skills (ars).
Branch: `claude/artigo-5-frentes-parlamentares` (criado a partir de `claude/zen-mayer-hkvhwi`).

## O que está pronto

Ainda não há `artigo.md`, `analise.py`, `figuras/` nem `referencias.bib`. Esta nota é o único arquivo da pasta.
Tudo o que segue foi apurado em sondagens exploratórias, não em script versionado. **Precisa ser refeito no `analise.py`** antes de ir para o texto.

### Ambiente
- `pip install pyarrow networkx scikit-learn scipy matplotlib` (pyarrow e networkx não vinham instalados).
  `python-louvain` não compila; use `networkx.community.louvain_communities` (networkx 3.x).
- Não há rede para revistas.ufpr.br, revistas.usp.br e portaldeperiodicos.idp.edu.br (WebFetch bloqueado); a busca web funciona.

### Números já reproduzidos (exploratório)
- `frentes`: 320 frentes; `frentes_deputados`: 65.318 adesões, 5 linhas sem `deputado_id` (descartar), sem duplicatas.
- Cargo: 64.994 Membro, 319 "Coordenador" e 5 "Coordernador" (erro de grafia na fonte; `str.startswith("Coord")` cobre os dois).
  314 frentes têm 1 coordenador e 5 têm 2; há 209 coordenadores distintos.
- `dataInicio` e `dataFim` estão 100% vazias. `dataCriacao` da frente: 263 em 2023, 19 em 2024, 28 em 2025, 10 em 2026.
- Tamanho das frentes: mín. 180, mediana 202, média 204, máx. 342 (FPA); "Mista" no título em 51%.
  O piso de cerca de 180 a 200 reflete a exigência de assinaturas de 1/3 dos membros (Ato da Mesa 69/2005).
  Logo, *não aderir* é o que varia; a seletividade quase não varia.
- Frentes por deputado: 606 deputados; mín. 1, Q1 48, mediana 99,5, Q3 168, máx. 307.
- Embedding (TF-IDF + SVD 16, coord. peso 3): variância explicada 0,372.
- Alvo `emb_votos.dim1` (governo +, oposição −). Amostra com ≥5 frentes e voto válido: n = 548.
  - Ridge CV R² = 0,852 (KFold com shuffle: 0,854); matriz binária bruta: 0,852.
  - Nº de frentes sozinho: R² ≈ −0,03 (correlação com dim1 −0,03). A informação está em *quais* frentes, não em quantas.
  - Dummies de partido sozinhas: R² 0,831; partido + frentes: 0,895. **Ponto crítico:** o ganho sobre o partido é modesto.
  - Dentro do partido (dim1 menos a média do partido): R² 0,11 (embedding) e 0,09 (binária).
    Contra `emb_votos_intra.dim1`: 0,19 (embedding) e 0,26 (binária).
- `avaliacao.json` (já versionado): kNN5 acerta partido 41% nas frentes (acaso 18,8%); R² dim1: temas 0,297, discursos 0,372 e 0,391, votos_intra 0,22.
- Amostras das outras visões (confiáveis): temas 579, discursos 447, votos 621.
- 166 deputados com 2 partidos na legislatura, 18 com 3 e 2 com 4: definir o partido (atual vs. majoritário nos votos).
- Votos por ano: 2023 com 128.679; 2024 com 116.400; 2025 com 175.067; 2026 com 53.177.

### Referências verificadas (busca web)
- Coradini, O. L. (2010). Frentes parlamentares, representação de interesses e alinhamentos políticos. *Rev. Sociol. Polít.* 18(36): 241–256. doi:10.5380/rsp.v18i36.31641
- Cascione, S. & Araújo, S. M. V. G. (2019). Obstáculos para protagonismo das frentes parlamentares em coalizões presidenciais no Brasil. *Rev. Sociol. Polít.* 27(72): e005. doi:10.1590/1678-987319277205.
  Achado: frentes reais são muito menores que as listas de assinatura (survey de 2017). **Essencial** para "adesão formal não é atuação".
- Araújo e Silva: Silva, V. A. A. (2012), "Grupos suprapartidários no congresso brasileiro: uma análise da Frente Parlamentar Evangélica", *Revista Três Pontos* 9(2): 27–36.
  Também há "Representações Políticas Alternativas no Congresso Nacional: uma Proposta Conceitual para Compreender as Frentes Parlamentares", *Direito Público* 16(88): 232–256, 2019.
  Os autores desse último **não foram confirmados** (Silva & Araújo? Silveira e Silva?): marcar [verificar].
  "Araújo e Silva (2016)" é citado como tipologia de frentes [verificar].
- Nery, P. F. & Mueller, B. (2022). Co-sponsorship networks in the Brazilian congress: an exploratory analysis of caucus influence. *Estudos Econômicos* 52(1): 83–111. doi:10.1590/1980-53575213pnbm
- Ringe, N. & Victor, J. N., with C. J. Carman (2013). *Bridging the Information Gap: Legislative Member Organizations as Social Networks in the United States and the European Union*. University of Michigan Press.
- Fowler, J. H. (2006). Connecting the Congress: A Study of Cosponsorship Networks. *Political Analysis* 14(4): 456–487. doi:10.1093/pan/mpl002
- Zucco, C. & Lauderdale, B. (2011). Distinguishing between influences on Brazilian legislative behavior. *LSQ* 36(3): 363–396. doi:10.1111/j.1939-9162.2011.00019.x
- Neal, Z. P. (2014). The backbone of bipartite projections: Inferring relationships from co-authorship, co-sponsorship, co-attendance and other co-behaviors. *Social Networks* 39: 84–97.
- Newman, M. E. J. (2006). Modularity and community structure in networks. *PNAS* 103(23): 8577–8582.
- Blondel, V. D., Guillaume, J.-L., Lambiotte, R. & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *J. Stat. Mech.* P10008.
- Não buscadas, mas canônicas (conferir páginas):
  - Spärck Jones (1972), *J. Documentation* 28(1): 11–21.
  - Salton & Buckley (1988), *Inf. Process. Manag.* 24(5): 513–523.
  - Deerwester et al. (1990), *JASIS* 41(6): 391–407.
- Sugestões de referências a acrescentar:
  - Ojala & Garriga (2010), JMLR 11, testes de permutação de classificadores.
  - Strona et al. (2014), Nat. Commun. 5:4114, algoritmo curveball.
  - Traag, Waltman & van Eck (2019), Sci. Rep. 9:5233, Leiden.
  - Hubert & Arabie (1985), ARI.

## O que falta (plano de análise desenhado)
1. `analise.py` reprodutível, com saídas em `figuras/` e `resultados/` (json e tabelas md), cobrindo:
   - Descritivos.
   - Reprodução: R² com 5 dobras repetidas e kNN de partido.
   - Testes de permutação: y permutado; y permutado dentro do partido; nulo curveball que preserva os graus da bipartida, refazendo TF-IDF e SVD.
   - Controle por partido: ΔR² e R² parcial em CV; alvo `emb_votos_intra`.
   - Informação por frente: correlação ponto-bisserial com dim1, entropia partidária, diferença de médias entre membros e não membros.
   - Curva R² × k frentes, com seleção *dentro* da dobra, comparando top-k e k aleatórias; Lasso com seleção por estabilidade.
   - Homofilia de recrutamento: taxa de adesão do mesmo lado do coordenador vs. do lado oposto (teste de "rede" vs. "posição").
   - Coordenadores.
   - Comunidades: projeção deputado–deputado, backbone SDSM/BiCM com aproximação normal da Poisson-binomial e Bonferroni; Louvain com várias sementes; ARI/NMI com partido e com grupos do mapa de votos; frentes com maior *lift* em cada comunidade para nomeá-las.
   - "Bancadas" nomeadas: FPA, Evangélica, Segurança Pública, Ambientalista, Serviço Público, Trabalhadores.
   - Sensibilidade: TF-IDF ligado/desligado, peso do coordenador 1/2/3/5, dimensões de 2 a 128.
   - Estabilidade temporal: frentes de 2023 vs. posteriores; alinhamento ao governo por ano a partir de `votos`.
   - Trocadores de partido.
2. `artigo.md` completo, `referencias.bib`, figuras com legenda.
3. Revisão metodológica independente: o subagente "arquiteto de pesquisa" foi lançado mas perdeu-se no reinício, sem parecer.
   As questões enviadas a ele valem como checklist:
   - vazamento na seleção de frentes;
   - R² inflado pelo partido e pela bimodalidade;
   - endogeneidade temporal;
   - suplentes;
   - senadores nas frentes mistas;
   - desenho dos nulos;
   - como distinguir posição, rede e troca de assinaturas.

## Problemas conhecidos e alertas para o texto
- O R² de 0,85 é quase igual ao do partido sozinho (0,83). A tese "frentes preveem o voto" precisa ser reformulada:
  as frentes recuperam sobretudo o alinhamento partidário e de bloco, e acrescentam pouco dentro do partido (R² ≈ 0,1–0,26).
  Relatar com honestidade.
- TF-IDF e SVD são ajustados em todos os deputados (transdutivo, sem uso de y). Declarar no texto.
- Não alterar `embeddings_deputados.py` nem os dados versionados.
