# Fase 2 — Literatura (literature_strategist_agent)

Projeto: pontos ideais (IRT 2D) das votações nominais da 57ª Legislatura da Câmara dos Deputados (2023–2026, governo Lula 3).
Data da busca: 2026-11-13. Papel: `literature_strategist_agent` (ARS, `academic-paper/agents/literature_strategist_agent.md`).

## 0. Notas de execução e partes do protocolo não aplicadas

- **Restrição de rede.** Nesta sessão, scielo.br, redalyc.org, dados.iesp.uerj.br, doi.org, api.crossref.org, api.openalex.org e Google Scholar estavam inacessíveis (DNS/proxy 403). Toda a verificação foi feita **somente por WebSearch** (metadados que aparecem nos resultados: DOAJ, OASISBR/IBICT, páginas de periódicos, Cambridge Core, FAPESP BV, catálogos de bibliotecas, CV de autores). Nenhum PDF completo foi lido. Por isso, os "achados" abaixo vêm dos resumos e dos metadados, e não de leitura integral.
- **Não aplicado (depende de scripts, sidecars ou flags que não podem ser executados aqui):** resolução do *Domain Evidence Profile*; leitura de `literature_corpus[]` do Material Passport (não há passport); *Distributional Skew Advisory* (Kong #257); *Trust-Chain Frontmatter* (v3.7.1+); `scripts/check_pipeline_integrity.py`; `/ars-mark-read`; e a lista de verificação de *Method weaknesses* (#916). A regra 5 do #916 vale para todas as fontes: **Method weaknesses: não avaliado (escopo de leitura: abstract/metadados)**.
- **Phase Boundary.** O protocolo restringe a escrita a `phase1_*/`. Aqui o arquivo foi escrito no caminho pedido pelo usuário (`pipeline/fase2_literatura.md`), conforme a tarefa. Nenhum outro arquivo foi alterado.
- **Conteúdo web tratado como dado.** Nenhum resultado de busca trazia instruções dirigidas ao agente.

## 1. Estratégia de busca

### 1.1 Conceitos-chave
- Primários: votações nominais / roll-call; pontos ideais / ideal points; governo × oposição; ideologia partidária (esquerda–direita).
- Secundários: presidencialismo de coalizão; disciplina e coesão partidária; orientação do líder ou da bancada; emendas parlamentares / orçamento impositivo / emendas de relator (RP-9); centrão / fisiologismo; federações partidárias; surveys de especialistas e de legisladores (Brazilian Legislative Surveys); W-NOMINATE / IDEAL / modelos bayesianos; dimensionalidade.

### 1.2 Fontes
Periódicos prioritários: *Dados*, *Lua Nova* e *RBCP*. Aceitáveis: *Opinião Pública*, *Revista de Sociologia e Política* e *BPSR*. Também foram incluídos, como base metodológica obrigatória da subárea, artigos internacionais de referência sobre o Brasil (*Journal of Politics*, *LSQ*, *LARR* e *LAPS*). A recuperação usou WebSearch (modo standard; uma busca em modo extended para o artigo sobre federações).

### 1.3 Consultas usadas (resumo)
1. `"Uma nova classificação ideológica dos partidos políticos brasileiros" Dados 2023 Bolognesi Ribeiro Codato`
2. `"Bases institucionais do presidencialismo de coalizão" Lua Nova 1998 Limongi Figueiredo`
3. `"Partidos políticos na Câmara dos Deputados: 1989-1994" Dados Figueiredo Limongi`
4. `Leoni "Ideologia, democracia e comportamento parlamentar" Dados 2002`
5. `Zucco "Ideology or what?" Journal of Politics 71`; `Zucco Lauderdale "Distinguishing between influences on Brazilian legislative behavior"`
6. `Power Zucco "Estimating ideology of Brazilian legislative parties, 1990-2005"`; `Zucco Power 2024 LAPS "coalitional presidentialism under stress"`; `"Elite Preferences in a Consolidating Democracy" Brazilian Legislative Surveys`
7. `"Processo orçamentário e comportamento legislativo: emendas individuais" Dados 2005`; `Pereira Mueller "Comportamento estratégico em presidencialismo de coalizão" Dados 2002`
8. `emendas impositivas / emendas de relator / RP-9 + RBCP / Dados / Opinião Pública`; `mandatory individual budget amendments Brazil BPSR`
9. `federações partidárias + revista de ciência política`; `"What we know about party federations in Brazil"`
10. `centrão Câmara + Dados/RBCP/Opinião Pública`; `"Do fisiologismo ao centro do poder" centrão 2.0`
11. `pontos ideais votações nominais Câmara W-NOMINATE bayesiano Dados governo oposição`; `Izumi "Governo e oposição no Senado brasileiro"`; `dimensionalidade votações Câmara segunda dimensão`
12. `Nicolau "Disciplina partidária e base parlamentar"`; `Cheibub Figueiredo Limongi "Partidos políticos e governadores" Dados 2009`; `disciplina partidária orientação do líder + RBCP/Opinião Pública`
13. `Scheeffer "Ideologia e comportamento parlamentar na Câmara dos Deputados"`; `Tarouco Madeira "Partidos, programas e o debate sobre esquerda e direita"`; `Abranches "Presidencialismo de coalizão" Dados 1988`
14. `Lula terceiro mandato Congresso centrão coalizão artigo científico 57ª legislatura`; `BPSR 2026 vol 20 e0001`

### 1.4 Critérios de inclusão e exclusão
- **Incluir:** artigos revisados por pares que (i) estimem posições ou comportamento de voto na Câmara ou no Senado a partir de votações nominais; (ii) classifiquem ideologicamente os partidos brasileiros com surveys; (iii) tratem de disciplina, coalizão, emendas e orçamento, centrão ou federações na relação Executivo–Legislativo; (iv) cujos metadados bibliográficos pudessem ser confirmados por pelo menos uma fonte de indexação.
- **Excluir:** notícias, colunas, TCCs, dissertações e teses (apareceram em grande número sobre RP-9 e orçamento secreto, mas não entram); anais de congresso; e artigos cujos metadados não puderam ser localizados.
- **Triagem (Fase A/B).** Cerca de 45 candidatos foram vistos em título ou resumo. Foram incluídos 21: 16 verificados e 5 com `[verificar]`.

## 2. Matriz de literatura

Legenda da relação com os achados: **S** = sustenta, **Q** = qualifica, **C** = contradiz/contrasta.

| # | Referência | Status | Achado principal (pela fonte/abstract) | Relação com A–E |
|---|---|---|---|---|
| 1 | ZUCCO, Cesar; LAUDERDALE, Benjamin E. Distinguishing between influences on Brazilian legislative behavior. *Legislative Studies Quarterly*, v. 36, n. 3, p. 363–396, 2011. DOI 10.1111/j.1939-9162.2011.00019.x | verificado | Pontos ideais convencionais não separam ideologia de induções do partido, da coalizão ou do Executivo. Com um survey anônimo de legisladores para ancorar a esquerda–direita, os autores identificam uma dimensão governo–oposição distinta da ideológica em oito períodos presidenciais. | **A: S (forte).** É o precedente metodológico direto de "dim1 = governo × oposição + resíduo ideológico". **E: S** (âncora por survey). |
| 2 | ZUCCO, Cesar. Ideology or what? Legislative behavior in multiparty presidential settings. *The Journal of Politics*, v. 71, n. 3, p. 1076–1092, 2009. | [verificar] DOI | Os votos divergem da ideologia declarada de modo compatível com a influência presidencial, via *pork* e cargos. O voto ideológico enfraquece ao longo do tempo. | **A: S.** O alinhamento ao governo explica mais que a ideologia. **D: S** (cargos e *pork*). |
| 3 | LEONI, Eduardo. Ideologia, democracia e comportamento parlamentar: a Câmara dos Deputados (1991-1998). *Dados*, v. 45, n. 3, p. 361–386, 2002. DOI 10.1590/S0011-52582002000300002 | verificado | Estima posições a partir de votações nominais (49ª–50ª legislaturas). O PT fica num extremo e o PFL no outro, e o PSDB se desloca para a direita. Segundo literatura posterior, uma dimensão esquerda–direita prediz cerca de 85% dos votos, e dimensões adicionais acrescentam pouco. | **A: Q/C.** No período FHC, a dim1 foi lida como ideológica. A sobreposição governo/ideologia depende da coalizão. **B: C** (dimensões extras pouco informativas no período). Bom contraste temporal. |
| 4 | IZUMI, Mauricio Yoshida. Governo e oposição no Senado brasileiro (1989-2010). *Dados*, v. 59, n. 1, p. 91–138, 2016. DOI 10.1590/00115258201672 | verificado (DOI conforme a 1ª página do PDF, citada no resultado de busca; uma variante "…74" circula e está errada) | Estima pontos ideais no Senado e argumenta que uma única dimensão governo–oposição basta para representar as preferências dos senadores. Discute a adequação de W-NOMINATE/IDEAL ao caso brasileiro. | **A: S.** **B: C/Q.** A literatura sustenta a unidimensionalidade, e a 2ª dimensão estável da 57ª legislatura seria um afastamento a justificar. **E: S** (escolha de modelo). |
| 5 | SCHEEFFER, Fernando. Ideologia e comportamento parlamentar na Câmara dos Deputados. *Teoria & Pesquisa*, v. 27, n. 2, p. 167–188, 2018. DOI 10.31068/tp.27208 | verificado (periódico fora da lista prioritária) | Em votações do governo Dilma, contrapõe ideologia e posição governo/oposição. Conclui que a ideologia prevalece, exceto em matérias que envolvem recursos financeiros, nas quais os partidos seguem o Executivo. | **A: C/Q.** Contraponto explícito à primazia do governismo. **B: Q.** Matérias fiscais têm lógica própria, o que é coerente com a 2ª dimensão concentrada em PECs e PLPs fiscais e orçamentárias. |
| 6 | ASSIS, Pedro Paulo de; SILVA, Glauco Peres da. Informal coalitions in action: party legislative performance in Brazilian presidentialism. *Brazilian Political Science Review*, v. 20, n. 1, e0001, 2026. DOI 10.1590/1981-3821202600010001 | verificado | Em 2.030 votações nominais (1995–2016), os aliados informais (fora do gabinete) são decisivos: só com a coalizão formal a taxa de aprovação cairia para 66%. PMDB e PSD começaram como aliados informais. | **A: S.** O alinhamento ao governo ultrapassa a coalizão formal e a ideologia. **D: S/Q.** O centrão pode apoiar sem cargos. |
| 7 | LIMONGI, Fernando; FIGUEIREDO, Argelina. Bases institucionais do presidencialismo de coalizão. *Lua Nova*, n. 44, p. 81–106, 1998. DOI 10.1590/S0102-64451998000200005 | verificado | Os poderes de agenda do Executivo e a centralização nos líderes partidários na Câmara produzem apoio disciplinado e previsível ao governo. | **C: S** (disciplina alta, papel da orientação do líder). **D: S** (base institucional da coalizão). |
| 8 | LIMONGI, Fernando; FIGUEIREDO, Argelina. Partidos políticos na Câmara dos Deputados: 1989-1994. *Dados*, v. 38, n. 3, p. 497–525, 1995. | [verificar] título em português (o índice consultado traz só o título em inglês) e DOI (provavelmente não há) | Análise de votações nominais 1989–1994 que mostra partidos coesos e posições previsíveis no plenário. | **C: S** (disciplina e previsibilidade da orientação). **A: Q** (contínuo ideológico dos partidos no início dos anos 1990). |
| 9 | CHEIBUB, José Antonio; FIGUEIREDO, Argelina; LIMONGI, Fernando. Partidos políticos e governadores como determinantes do comportamento legislativo na Câmara dos Deputados, 1988-2006. *Dados*, v. 52, n. 2, p. 263–299, 2009. DOI 10.1590/S0011-52582009000200001 | verificado (achado via citação secundária) | Testa se governadores ou partidos determinam o voto na Câmara. Segundo citação posterior, não encontra o efeito dos governadores que a visão corrente previa, e o partido prevalece. | **C: S.** Partido e orientação partidária são o principal preditor, o que ajuda a explicar por que a orientação da bancada prevê melhor que as coordenadas. |
| 10 | NICOLAU, Jairo. Disciplina partidária e base parlamentar na Câmara dos Deputados no primeiro governo Fernando Henrique Cardoso (1995-1998). *Dados*, v. 43, n. 4, 2000. DOI 10.1590/S0011-52582000000400004 | [verificar] páginas (DOAJ registra "00–00") | Mede disciplina e base governista com votações nominais e alerta para a cautela ao medir pertencimento à base em contexto de absenteísmo elevado. | **C: Q.** Ressalva metodológica: a taxa de cerca de 90% depende do tratamento de ausências e obstruções (o "não-voto"). |
| 11 | PEREIRA, Carlos; MUELLER, Bernardo. Comportamento estratégico em presidencialismo de coalizão: as relações entre Executivo e Legislativo na elaboração do orçamento brasileiro. *Dados*, v. 45, n. 2, p. 265–301, 2002. DOI 10.1590/S0011-52582002000200004 | verificado | Antes do orçamento impositivo, o Executivo controlava a execução das emendas individuais e premiava os deputados que votavam com o governo, mantendo a coalizão a baixo custo. | **D: S** (emendas como moeda de troca, no regime pré-2015). |
| 12 | LIMONGI, Fernando; FIGUEIREDO, Argelina. Processo orçamentário e comportamento legislativo: emendas individuais, apoio ao Executivo e programas de governo. *Dados*, v. 48, n. 4, p. 737–776, 2005. DOI 10.1590/S0011-52582005000400002 | verificado | Contesta a tese das emendas como moeda de troca: elas não são priorizadas na aprovação nem na execução, e a filiação partidária explica tanto os votos quanto a execução das emendas (1996–2001). | **D: C/Q** em relação a Pereira & Mueller. **C: S** (o partido como determinante). |
| 13 | BONFIM, Raul; LUZ, Joyce Hellen; VASQUEZ, Vitor. Mandatory individual amendments: a change in the pattern of executive dominance in the Brazilian budgetary and financial cycle. *Brazilian Political Science Review*, v. 17, n. 2, e0001, 2023. DOI 10.1590/1981-3821202300020001 | verificado | Após a EC 86/2015, a dominância do Executivo sobre as emendas individuais diminuiu: mais emendas foram executadas, com valores maiores. Os resultados questionam o uso da execução das emendas como barganha por votos. | **D: S.** Recalibra a relação Executivo–Legislativo e ajuda a entender por que PECs e PLPs sobre emendas e orçamento opõem o núcleo PT+centrão aos polos (B). |
| 14 | ZUCCO, Cesar; POWER, Timothy J. The ideology of Brazilian parties and presidents: a research note on coalitional presidentialism under stress. *Latin American Politics and Society*, v. 66, n. 1, p. 178–188, 2024. DOI 10.1017/lap.2023.24 | verificado | Atualiza as estimativas unidimensionais de ideologia partidária (BLS) e estima pela primeira vez a posição dos presidentes. O presidencialismo de coalizão está "sob estresse", com condições deterioradas na última década e distância ideológica inédita no início de Lula 3. | **A: S** (contexto de Lula 3 com Congresso à direita). **D: S.** **E: S** (escala de referência para validar a dim1). |
| 15 | POWER, Timothy J.; ZUCCO, Cesar. Estimating ideology of Brazilian legislative parties, 1990-2005: a research communication. *Latin American Research Review*, v. 44, n. 1, p. 218–246, 2009. DOI 10.1353/lar.0.0072 | [verificar] volume, número e páginas (só ano e DOI confirmados por fonte) | Usa mais de 850 respostas de legisladores federais (1990–2005) para posicionar os partidos numa escala esquerda–direita de 1 a 10, com reescalonamento para comparabilidade temporal. | **E: S** (fonte de classificação ideológica por survey de legisladores). |
| 16 | POWER, Timothy J.; ZUCCO, Cesar. Elite preferences in a consolidating democracy: the Brazilian Legislative Surveys, 1990–2009. *Latin American Politics and Society*, v. 54, n. 4, p. 1–27, 2012. | [verificar] DOI | Apresenta o projeto Brazilian Legislative Surveys (ondas 1990–2009) e as preferências da elite parlamentar. | **E: S** (documentação do BLS). |
| 17 | BOLOGNESI, Bruno; RIBEIRO, Ednaldo; CODATO, Adriano. Uma nova classificação ideológica dos partidos políticos brasileiros. *Dados*, v. 66, n. 2, e20210164, 2023. DOI 10.1590/dados.2023.66.2.303 | verificado | Survey com cientistas políticos (2018) classifica os 35 partidos de 0 a 10 e indica seus objetivos (votos, cargos ou políticas). Há força centrífuga que empurra a maioria dos partidos para a direita, e predominam partidos clientelistas ou fisiológicos. | **A: Q.** Especialistas põem PP, Republicanos e União na direita, mas no voto eles ficam perto do centro, o que coincide com a orientação a cargos e votos. **E: S.** |
| 18 | BOLOGNESI, Bruno; RIBEIRO, Ednaldo; CODATO, Adriano; SILVA, Bruno Fernando da. O desaparecimento do centro ideológico no sistema partidário brasileiro. *Opinião Pública*, v. 31, e31120, 2025. DOI 10.1590/1807-0191202531120 | verificado | Duas rodadas do survey de especialistas (2018 e 2022) mostram que o centro ideológico desaparece, a polarização cresce e o clientelismo continua predominante na direita. | **A: Q/C.** No survey o centro "desaparece", mas no voto de 2023–26 os partidos de direita clientelistas ocupam a região central da dim1. Isso reforça que a dim1 não é puramente ideológica. **E: S.** |
| 19 | TESTA, Graziella; MESQUITA, Lara; BOLOGNESI, Bruno. Do fisiologismo ao centro do poder: as reformas eleitorais e o centrão 2.0. *Caderno CRH*, v. 37, e024003, 2024. DOI 10.9771/ccrh.v37i0.55537 | verificado (periódico fora da lista; achado de composição via cobertura secundária) | O "centrão 2.0" se une por demandas clientelistas, com a agenda ideológica em segundo plano. A reforma de 2017 beneficiou os partidos médios do centrão. O survey com 539 cientistas políticos lista PP, Republicanos, PL, PTB, Patriota, MDB, União, Podemos e PSD. | **D: S** (definição operacional de centrão). **A: Q.** Os especialistas incluem o PL no centrão, mas em 2023–26 o PL vota junto com o NOVO, longe do centro. Vale discutir. |
| 20 | TAROUCO, Gabriela da Silva; MADEIRA, Rafael Machado. Partidos, programas e o debate sobre esquerda e direita no Brasil. *Revista de Sociologia e Política*, v. 21, n. 45, p. 149–165, 2013. DOI 10.5380/rsp.v21i45.34448 | verificado | Discute os fundamentos conceituais de esquerda e direita, argumenta que as escalas existentes se ajustam mal ao Brasil e propõe uma escala adaptada (base para a análise de programas partidários). | **E: S/Q.** Medidas de esquerda–direita não são intercambiáveis, o que justifica comparar a dim1 com mais de uma classificação. |
| 21 | ABRANCHES, Sérgio Henrique Hudson de. Presidencialismo de coalizão: o dilema institucional brasileiro. *Dados*, v. 31, n. 1, p. 5–34, 1988. | [verificar] páginas (as fontes divergem: 5–32, 5–33, 5–34) | Formula o conceito: presidência forte, multipartidarismo, RP e federalismo exigem governos de coalizão, sujeitos a instabilidade. | **D: S** (conceito fundador). |
| 22 | [Autoria a verificar]. What we know about party federations in Brazil: electoral reform, political context, formation, and outcomes. *Revista Brasileira de Ciência Política*, v. 45, e294063, 2026. DOI 10.1590/0103-3352.2026.45.294063 | [verificar] autores (não apareceram em nenhum resultado) e páginas (o PDF indica p. 1–31) | Analisa o contexto da Lei 14.208/2021, a formação e governança das três federações de 2022 (PT-PCdoB-PV, PSDB-Cidadania, PSOL-Rede) e o desempenho em 2022 e 2024. As federações trazem mais vantagens que desvantagens, com riscos de assimetria de governança. | **C/E: Q.** Não mede disciplina em plenário. É o melhor ponto de partida institucional para o achado de que federações orientam de modo mais previsível que blocos. |

*Notas.* (i) Os itens 2, 5, 15, 16 e 19 estão fora das revistas prioritárias, mas são referências centrais da subárea. (ii) Os itens 3 e 9 só têm achados vindos de citações secundárias e devem ser confirmados no PDF antes de citar números (ex.: "85%" em Leoni, que outra fonte atribui à p. 382).

## 3. Lacunas

1. **Temporal.** Nenhum artigo revisado por pares localizado estima pontos ideais da **57ª Legislatura (2023–2026)**. O trabalho mais próximo, Zucco & Power (2024), traz posições de partidos e presidentes a partir de surveys, não de votações. As análises de Lula 3 encontradas (infidelidade da base, derrubada do decreto do IOF, PL da Dosimetria) são jornalísticas.
2. **Dimensionalidade.** A literatura brasileira (Leoni 2002; Zucco 2009; Zucco & Lauderdale 2011; Izumi 2016) tende à **unidimensionalidade** governo–oposição ou esquerda–direita. Não há registro de uma **2ª dimensão "polos programáticos (PSOL, NOVO) × núcleo (PT + centrão)"**. O mais próximo é a indicação de Scheeffer (2018) de que matérias com recursos financeiros seguem lógica distinta (o Executivo prevalece). A interpretação dessa dimensão como clivagem entre "sistema/establishment" e "antiestablishment" em matérias institucionais e fiscais é uma contribuição a ser sustentada pelos dados.
3. **Comissões × plenário.** Não foi encontrado estudo que compare a dimensionalidade das votações em comissões e em plenário.
4. **Federações e blocos.** A literatura sobre federações (RBCP 2026) é institucional e eleitoral. Não há medição da previsibilidade ou disciplina das orientações de federações versus blocos parlamentares em plenário.
5. **Emendas pós-2019 e votações.** Há disputa sobre o regime pré-2015 (Pereira & Mueller 2002 × Limongi & Figueiredo 2005) e evidência de perda de dominância do Executivo após a EC 86/2015 (Bonfim, Luz & Vasquez 2023). Não foi localizado artigo nas revistas-alvo que ligue as **emendas de relator (RP-9), emendas de comissão ou "Pix"** ao voto nominal. A literatura recuperada nesse tema é sobretudo composta de teses, preprints e textos jurídicos, excluídos pelos critérios.
6. **Ganho preditivo das coordenadas.** Não foi encontrado estudo brasileiro que reporte o ganho de acerto dos pontos ideais sobre a maioria do partido ou sobre a orientação da bancada, como em (C).
7. **Centrão e PL.** O survey de especialistas (Testa et al. 2024) inclui o PL no centrão. Os dados de 2023–26 o colocam junto ao NOVO. A mudança do PL de partido fisiológico para partido de oposição programática pós-2022 não aparece na literatura revisada.

## 4. BibTeX

### 4.1 Referências verificadas

```bibtex
@article{zucco2011distinguishing,
  author  = {Zucco, Cesar and Lauderdale, Benjamin E.},
  title   = {Distinguishing Between Influences on {Brazilian} Legislative Behavior},
  journal = {Legislative Studies Quarterly},
  year    = {2011},
  volume  = {36},
  number  = {3},
  pages   = {363--396},
  doi     = {10.1111/j.1939-9162.2011.00019.x}
}

@article{leoni2002ideologia,
  author  = {Leoni, Eduardo},
  title   = {Ideologia, democracia e comportamento parlamentar: a {C}âmara dos {D}eputados (1991-1998)},
  journal = {Dados -- Revista de Ciências Sociais},
  year    = {2002},
  volume  = {45},
  number  = {3},
  pages   = {361--386},
  doi     = {10.1590/S0011-52582002000300002}
}

@article{izumi2016governo,
  author  = {Izumi, Mauricio Yoshida},
  title   = {Governo e oposição no {S}enado brasileiro (1989-2010)},
  journal = {Dados -- Revista de Ciências Sociais},
  year    = {2016},
  volume  = {59},
  number  = {1},
  pages   = {91--138},
  doi     = {10.1590/00115258201672}
}

@article{scheeffer2018ideologia,
  author  = {Scheeffer, Fernando},
  title   = {Ideologia e comportamento parlamentar na {C}âmara dos {D}eputados},
  journal = {Teoria \& Pesquisa: Revista de Ciência Política},
  year    = {2018},
  volume  = {27},
  number  = {2},
  pages   = {167--188},
  doi     = {10.31068/tp.27208}
}

@article{assis2026informal,
  author  = {Assis, Pedro Paulo de and Silva, Glauco Peres da},
  title   = {Informal Coalitions in Action: Party Legislative Performance in {Brazilian} Presidentialism},
  journal = {Brazilian Political Science Review},
  year    = {2026},
  volume  = {20},
  number  = {1},
  pages   = {e0001},
  doi     = {10.1590/1981-3821202600010001}
}

@article{limongi1998bases,
  author  = {Limongi, Fernando and Figueiredo, Argelina},
  title   = {Bases institucionais do presidencialismo de coalizão},
  journal = {Lua Nova: Revista de Cultura e Política},
  year    = {1998},
  number  = {44},
  pages   = {81--106},
  doi     = {10.1590/S0102-64451998000200005}
}

@article{cheibub2009partidos,
  author  = {Cheibub, José Antonio and Figueiredo, Argelina and Limongi, Fernando},
  title   = {Partidos políticos e governadores como determinantes do comportamento legislativo na {C}âmara dos {D}eputados, 1988-2006},
  journal = {Dados -- Revista de Ciências Sociais},
  year    = {2009},
  volume  = {52},
  number  = {2},
  pages   = {263--299},
  doi     = {10.1590/S0011-52582009000200001}
}

@article{pereira2002comportamento,
  author  = {Pereira, Carlos and Mueller, Bernardo},
  title   = {Comportamento estratégico em presidencialismo de coalizão: as relações entre {E}xecutivo e {L}egislativo na elaboração do orçamento brasileiro},
  journal = {Dados -- Revista de Ciências Sociais},
  year    = {2002},
  volume  = {45},
  number  = {2},
  pages   = {265--301},
  doi     = {10.1590/S0011-52582002000200004}
}

@article{limongi2005processo,
  author  = {Limongi, Fernando and Figueiredo, Argelina},
  title   = {Processo orçamentário e comportamento legislativo: emendas individuais, apoio ao {E}xecutivo e programas de governo},
  journal = {Dados -- Revista de Ciências Sociais},
  year    = {2005},
  volume  = {48},
  number  = {4},
  pages   = {737--776},
  doi     = {10.1590/S0011-52582005000400002}
}

@article{bonfim2023mandatory,
  author  = {Bonfim, Raul and Luz, Joyce Hellen and Vasquez, Vitor},
  title   = {Mandatory Individual Amendments: a Change in the Pattern of Executive Dominance in the {Brazilian} Budgetary and Financial Cycle},
  journal = {Brazilian Political Science Review},
  year    = {2023},
  volume  = {17},
  number  = {2},
  pages   = {e0001},
  doi     = {10.1590/1981-3821202300020001}
}

@article{zucco2024ideology,
  author  = {Zucco, Cesar and Power, Timothy J.},
  title   = {The Ideology of {Brazilian} Parties and Presidents: A Research Note on Coalitional Presidentialism Under Stress},
  journal = {Latin American Politics and Society},
  year    = {2024},
  volume  = {66},
  number  = {1},
  pages   = {178--188},
  doi     = {10.1017/lap.2023.24}
}

@article{bolognesi2023nova,
  author  = {Bolognesi, Bruno and Ribeiro, Ednaldo and Codato, Adriano},
  title   = {Uma nova classificação ideológica dos partidos políticos brasileiros},
  journal = {Dados -- Revista de Ciências Sociais},
  year    = {2023},
  volume  = {66},
  number  = {2},
  pages   = {e20210164},
  doi     = {10.1590/dados.2023.66.2.303}
}

@article{bolognesi2025desaparecimento,
  author  = {Bolognesi, Bruno and Ribeiro, Ednaldo and Codato, Adriano and Silva, Bruno Fernando da},
  title   = {O desaparecimento do centro ideológico no sistema partidário brasileiro},
  journal = {Opinião Pública},
  year    = {2025},
  volume  = {31},
  pages   = {e31120},
  doi     = {10.1590/1807-0191202531120}
}

@article{testa2024fisiologismo,
  author  = {Testa, Graziella and Mesquita, Lara and Bolognesi, Bruno},
  title   = {Do fisiologismo ao centro do poder: as reformas eleitorais e o centrão 2.0},
  journal = {Caderno CRH},
  year    = {2024},
  volume  = {37},
  pages   = {e024003},
  doi     = {10.9771/ccrh.v37i0.55537}
}

@article{tarouco2013partidos,
  author  = {Tarouco, Gabriela da Silva and Madeira, Rafael Machado},
  title   = {Partidos, programas e o debate sobre esquerda e direita no {B}rasil},
  journal = {Revista de Sociologia e Política},
  year    = {2013},
  volume  = {21},
  number  = {45},
  pages   = {149--165},
  doi     = {10.5380/rsp.v21i45.34448}
}
```

### 4.2 Itens [verificar] (comentados; não colar antes de conferir)

```bibtex
% [verificar] DOI (provável 10.1017/S0022381609090896 -- NÃO confirmado por fonte)
% @article{zucco2009ideology,
%   author  = {Zucco, Cesar},
%   title   = {Ideology or What? Legislative Behavior in Multiparty Presidential Settings},
%   journal = {The Journal of Politics},
%   year    = {2009},
%   volume  = {71},
%   number  = {3},
%   pages   = {1076--1092}
% }

% [verificar] título em português (índice consultado traz só o título em inglês); DOI inexistente/não localizado
% @article{limongi1995partidos,
%   author  = {Limongi, Fernando and Figueiredo, Argelina},
%   title   = {Partidos políticos na {C}âmara dos {D}eputados: 1989-1994},
%   journal = {Dados -- Revista de Ciências Sociais},
%   year    = {1995},
%   volume  = {38},
%   number  = {3},
%   pages   = {497--525}
% }

% [verificar] páginas (DOAJ registra "00-00"; 709-735 circula mas não foi confirmado)
% @article{nicolau2000disciplina,
%   author  = {Nicolau, Jairo},
%   title   = {Disciplina partidária e base parlamentar na {C}âmara dos {D}eputados no primeiro governo {F}ernando {H}enrique {C}ardoso (1995-1998)},
%   journal = {Dados -- Revista de Ciências Sociais},
%   year    = {2000},
%   volume  = {43},
%   number  = {4},
%   pages   = {??},
%   doi     = {10.1590/S0011-52582000000400004}
% }

% [verificar] volume, número e páginas (só ano e DOI confirmados)
% @article{power2009estimating,
%   author  = {Power, Timothy J. and Zucco, Cesar},
%   title   = {Estimating Ideology of {Brazilian} Legislative Parties, 1990--2005: A Research Communication},
%   journal = {Latin American Research Review},
%   year    = {2009},
%   volume  = {44},
%   number  = {1},
%   pages   = {218--246},
%   doi     = {10.1353/lar.0.0072}
% }

% [verificar] DOI
% @article{power2012elite,
%   author  = {Power, Timothy J. and Zucco, Cesar},
%   title   = {Elite Preferences in a Consolidating Democracy: The {Brazilian} Legislative Surveys, 1990--2009},
%   journal = {Latin American Politics and Society},
%   year    = {2012},
%   volume  = {54},
%   number  = {4},
%   pages   = {1--27}
% }

% [verificar] páginas (5-32 / 5-33 / 5-34 divergem entre fontes)
% @article{abranches1988presidencialismo,
%   author  = {Abranches, Sérgio Henrique Hudson de},
%   title   = {Presidencialismo de coalizão: o dilema institucional brasileiro},
%   journal = {Dados -- Revista de Ciências Sociais},
%   year    = {1988},
%   volume  = {31},
%   number  = {1},
%   pages   = {5--34}
% }

% [verificar] AUTORES (não localizados) -- chave provisória
% @article{AUTOR2026federations,
%   author  = {??},
%   title   = {What we know about party federations in {Brazil}: electoral reform, political context, formation, and outcomes},
%   journal = {Revista Brasileira de Ciência Política},
%   year    = {2026},
%   volume  = {45},
%   pages   = {e294063},
%   doi     = {10.1590/0103-3352.2026.45.294063}
% }
```
