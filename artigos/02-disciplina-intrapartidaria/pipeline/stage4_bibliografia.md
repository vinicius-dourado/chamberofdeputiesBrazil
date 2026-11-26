# Stage 4 — Verificação bibliográfica (agente de bibliografia)

Data: 2026-11-26.

**Restrição de rede.** Nesta sessão só funcionou a WebSearch. O acesso direto (curl ou WebFetch) a api.crossref.org, scielo.br (desafio anti-bot), dados.iesp.uerj.br, doaj.org, redalyc.org, ideas.repec.org e doras.dcu.ie foi recusado pelo proxy ou não resolveu DNS. Por isso a verificação se apoia nos metadados que as buscas devolveram: páginas de editoras (Cambridge Core, SAGE, Wiley), registros RePEc/EconPapers, eScholarship, CVs de autores e listas de referências. Nenhum PDF foi lido por completo.

## 1. Tabela de verificação

| # | Chave | Status | Campos confirmados | Fonte(s) |
|---|---|---|---|---|
| 1 | amorimneto2003 | Confirmada | autores, título, WP 55(4), 550–578, jul/2003, DOI 10.1353/wp.2003.0023 | Cambridge Core (resumo); Scilit; repositório FGV; core.ac.uk |
| 2 | cheibub2009 | Confirmada, sem DOI | autores, LAPS 51(1): 1–30, 2009; título com "1988–2006" no Cambridge Core | Cambridge Core; CV em polisci.pitt.edu; versão em português na Dados 52(2), 2009 (DOI 10.1590/S0011-52582009000200001, outra publicação) |
| 3 | pereira2004 | Confirmada | título completo, CPS 37(7): 781–815, set/2004, DOI 10.1177/0010414004266866 | SAGE (journals.sagepub.com/doi/10.1177/0010414004266866) |
| 4 | desposato2006 | Confirmada | AJPS 50(1): 62–80, DOI 10.1111/j.1540-5907.2006.00170.x | EconPapers/IDEAS (RePEc:wly:amposc:v:50:y:2006:i:1:p:62-80); eScholarship |
| 5 | nokken2000 | Confirmada, sem DOI | LSQ 25(3): 417–444 | CV do autor (Texas Tech); listas de referências (APSR) |
| 6 | heller2005 | Confirmada, sem DOI | JOP 67(2): 536–559 | Página da autora (uva.theopenscholar.com/carol-mershon); researchconnect.suny.edu; listas de referências |
| 7 | minozzi2013 | Confirmada | JOP 75(3): 787–802, jul/2013, DOI 10.1017/S0022381613000480 | PDF hospedado pela Batten School/UVA (folha de rosto) |
| 8 | sun2021 | Confirmada | JoE 225(2): 175–199, DOI 10.1016/j.jeconom.2020.09.006; ordem Sun e Abraham na versão publicada (o arXiv 1804.05785 traz Abraham e Sun) | EconPapers (RePEc:eee:econom:v:225:y:2021:i:2:p:175-199); doi.org |
| 9 | callaway2021 | Confirmada | JoE 225(2): 200–230, DOI 10.1016/j.jeconom.2020.12.001 | EconPapers (RePEc:eee:econom:v:225:y:2021:i:2:p:200-230); arXiv 1803.09015 |
| 10 | nicolau2000 | Parcial | Dados 43(4), 2000. Páginas 709–735 só em fonte secundária (ResearchGate e listas de referências); uma citação em artigo SciELO de 2009 dá 709–734. **DOI não confirmado** | ResearchGate; DOAJ (registro, sem páginas); sidalc (oai:scielo:S0011-52582000000400004) |
| 11 | carey2007 | DOI confirmado | DOI 10.1111/j.1540-5907.2007.00239.x | Wiley Online Library (URL onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-5907.2007.00239.x); IDEAS (v51y2007i1p92-107) |

Notas sobre o .bib:
- Os DOIs ausentes de cheibub2009, nokken2000 e heller2005 ficaram de fora, com `note = {... [verificar]}`.
- Em nicolau2000 as páginas 709--735 entraram, mas a nota marca a fonte secundária e a divergência com `[verificar]`. Se o critério for estrito, remova o campo `pages`. O DOI provável, 10.1590/S0011-52582000000400004, não foi incluído porque não foi confirmado.
- O título de cheibub2009 segue o Cambridge Core. O CV de Pittsburgh traz uma variante: "...determinants of the behavior of Brazilian legislators".

## 2. Argumento central das obras novas (só o que foi confirmado)

- **Amorim Neto, Cox & McCubbins (2003).** O artigo pergunta quando surge, na Câmara pós-1988, um controle de agenda consistente por uma única coalizão majoritária, em vez de maiorias cambiantes. A resposta é que isso só ocorre se o presidente escolhe se aliar a uma coalizão majoritária. O artigo dialoga criticamente com a tese de Figueiredo e Limongi de um modo "parlamentar" de governar constante. (Fonte: resumo no Cambridge Core.)
- **Cheibub, Figueiredo & Limongi (2009).** O artigo usa todas as votações nominais da Câmara de 1989 a 2006 para testar se pressões subnacionais, em especial dos governadores sobre suas bancadas, afetam o voto. A conclusão substantiva não foi confirmada nesta sessão, porque nem o PDF nem o resumo completo foram lidos `[verificar]`. (Fonte: Cambridge Core.)
- **Pereira & Mueller (2004).** O Executivo usa a execução das emendas orçamentárias individuais dos parlamentares como moeda de baixo custo para obter apoio legislativo. (Fonte: resumo SAGE e citações posteriores.)
- **Desposato (2006).** Mais de um terço dos deputados troca de partido durante o mandato, alguns até sete vezes. O artigo testa um modelo de troca partidária movido por ambição, ideologia e fatores de base eleitoral. (Fonte: resumo via RePEc/eScholarship.)
- **Nokken (2000).** O artigo usa troca de partido no Congresso dos EUA, 1947–97, como experimento natural: se o comportamento de voto muda com a troca de partido, há influência partidária independente das preferências. O resumo vem da tese de 1999 que deu origem ao artigo. Trate como indicação e confirme no texto do artigo.
- **Heller & Mershon (2005).** Quase um quarto dos deputados italianos (cerca de 23%) trocou de partido na legislatura 1996–2001. O artigo analisa os determinantes dessas trocas. (Fonte: citações secundárias; o texto não foi lido.)
- **Minozzi & Volden (2013).** O estudo usa dados da Câmara dos EUA de 1973 a 2006. A resposta aos "party calls" é máxima entre os extremistas ideológicos dos dois partidos e cai entre os moderados, mesmo controlando pelo voto partidário de base. Um modelo de utilidade aleatória fundamenta o resultado. (Fonte: página da Batten School/UVA.)
- **Sun & Abraham (2021).** Em event studies com tratamento escalonado e efeitos heterogêneos, o coeficiente de cada lead ou lag em TWFE pode ser contaminado por efeitos de outros períodos, e "pré-tendências" espúrias podem surgir só da heterogeneidade. Os autores propõem um estimador livre de contaminação, de efeitos médios por coorte de entrada (interaction-weighted).
- **Callaway & Sant'Anna (2021).** Os autores desenvolvem identificação, estimação e inferência para efeitos de tratamento em DiD com múltiplos períodos e variação no momento do tratamento, via ATT por grupo e período agregáveis. O método admite tendências paralelas condicionais a covariáveis.

## 3. Respostas às perguntas 11–13

### 11. Carey (2007): índice de unidade ponderado pela proximidade da votação

**Confirmado:**
- O DOI é 10.1111/j.1540-5907.2007.00239.x.
- O artigo testa, com votações de 19 países, a hipótese de que a unidade de voto é menor onde as regras eleitorais geram competição intrapartidária do que sob lista fechada. Também testa o efeito de principais concorrentes (competing principals), como presidentes e governos federais.
- O artigo usa índices de UNITY, uma modificação do Rice.

**Não confirmado:** o texto do artigo de 2007 não foi lido, então não está confirmado se ele próprio usa a versão ponderada nem a fórmula exata que aplica.

**O que existe em fontes secundárias e em working papers do mesmo autor:**
- No working paper "Party Unity in Legislative Voting" (Carey, 2000/2002; seção "Indexes of voting unity: weighting votes by CLOSEness"; tabela "Weighted unity indexes in 10 countries, 12 chambers", ResearchGate 2412757) e no paper de Carey sobre o Chile (LASA 1998, bibliotecavirtual.clacso.org.ar), o índice ponderado é:
  - Weighted UNITY = Σ (UNITY_i × ATTEND_i × CLOSE_i) / Σ (ATTEND_i × CLOSE_i)
  - CLOSE_i = 1 − 2·|0,5 − %AYE_i|, com %AYE medido no plenário inteiro.
  - ATTEND_i é a proporção de presentes ou votantes.
- A justificativa é que votações esvaziadas ou desequilibradas importam menos para medir unidade.
- Uma fonte secundária (cohesion.pdf, DCU) atribui a Carey a ponderação por presença e proximidade.

**Recomendação:** cite a fórmula como "Carey (2000; 2009)" ou confirme no artigo de 2007 ou no livro Carey (2009) antes de atribuí-la ao AJPS 2007.

### 12. Figueiredo & Limongi (1999): mecanismo

**Confirmado por fontes secundárias.** Na síntese da literatura, a disciplina na Câmara decorre de dois fatores combinados:
- os poderes legislativos do presidente;
- a forma centralizada como as decisões são tomadas em plenário, em torno do Colégio de Líderes.

Elementos que as fontes associam ao argumento:
- O Colégio de Líderes, com o presidente da Câmara, monta a pauta do plenário.
- Os pedidos de urgência neutralizam as comissões.
- Os líderes indicam membros de comissões.
- Nas votações nominais de 1989–1994, a posição dos líderes basta para prever o resultado.
- Os poderes de agenda do Executivo são a peça que explica por que a paralisia temida não ocorreu. O sumário do livro inclui os capítulos "Poder de agenda, disciplina e apoio partidário na Câmara dos Deputados" e "O Congresso e as medidas provisórias: abdicação ou delegação?".

Fontes:
- "Coesão e disciplina partidária no Senado Federal", Dados (SciELO, scielo.br/j/dados/a/TQDyL7BfNpsmdg3VrDyY5xH).
- "A importância dos líderes partidários na Câmara dos Deputados" (sdpscp.fflch.usp.br).
- Revista de Sociologia e Política nº 15 (2000), pp. 31–47 (SciELO).
- "Disciplina partidária no Congresso brasileiro", Intratextos/UERJ.
- Anotação HLAS/Library of Congress (loc.gov/item/hlas-bi2001007744): uma "aggressively argued attack on the weak-institutions thesis".
- Editora FGV, página do livro.

**Não confirmado por fonte lida nesta sessão:** que o livro liste explicitamente a "iniciativa exclusiva em matéria orçamentária" como um dos poderes de agenda. É consistente com a literatura posterior dos mesmos autores (por exemplo, sobre o orçamento), mas fica `[verificar]`. Medidas provisórias e urgência estão confirmadas pelo sumário e pelas sínteses.

Nota de edição: o livro saiu pela Editora FGV em coedição com a FAPESP (Rio de Janeiro, 1999).

### 13. Composição partidária dos ministérios — Lula 3 (2023–2026)

| Partido | Ministros/pastas (exemplos confirmados) | Período confirmado | Fonte |
|---|---|---|---|
| PT, PSB, MDB, PSD, União Brasil, PDT, PCdoB, PSOL, REDE | os 9 partidos com ministérios na formação inicial; 37 ministérios | desde 01/01/2023 | Gazeta do Povo ("lula-16-ministros-centro-aliados"); Politize; Correio Braziliense, jan/2023 |
| PT | 8–10 pastas na formação (as contagens divergem: Politize dá 8, O POVO dá 10) | 2023– | Politize; O POVO |
| PSB | 3 pastas na formação (inclui Alckmin no MDIC) | 2023–; Alckmin exonerado em abr/2026 | Politize; SBT News |
| MDB | 3 pastas na formação (inclui Tebet no Planejamento) | 2023–; Tebet saiu em abr/2026 | O POVO; CartaCapital |
| PSD | 3 pastas na formação (inclui André de Paula) | 2023–; André de Paula saiu em abr/2026 | O POVO; Itatiaia |
| PCdoB | 1 pasta | 2023– | Politize |
| PSOL | 1 pasta (Sônia Guajajara, Povos Indígenas) | 01/2023 – abr/2026 (desincompatibilização) | Politize; A Crítica (lista de abr/2026) |
| REDE | 1 pasta (Marina Silva, Meio Ambiente) | 01/2023 – abr/2026 (desincompatibilização) | Politize; CartaCapital, abr/2026 |
| PDT | Carlos Lupi (Previdência), sucedido por Wolney Queiroz (PDT), que manteve a pasta com o partido | Lupi: 01/2023 – 02/05/2025 | Jornal Opção; IstoÉ Dinheiro (DOU extra de 02/05/2025); SBT News |
| União Brasil | Juscelino Filho (Comunicações) até 08/04/2025, exoneração no DOU em 09/04/2025; Celso Sabino (Turismo) | formação 2023 – set/2025, quando a federação rompeu; Sabino permaneceu no cargo | CNN Brasil; Congresso em Foco; Gazeta do Povo; Portal Norte (18/09/2025) |
| PP | André Fufuca (Esporte) | posse 13/09/2023; o PP anunciou a saída em 02/09/2025; Fufuca ficou e foi afastado da direção do partido em 08/10/2025; acordo PP–Planalto de ~22/10/2025 para mantê-lo | Correio Braziliense, 09/2023; Agência Gov; Agência Brasil (10/2025); CNN Brasil; DGABC |
| Republicanos | Silvio Costa Filho (Portos e Aeroportos) | posse 13/09/2023 – abr/2026 (desincompatibilização) | Correio Braziliense; O Povo (06/09/2023); A Crítica (abr/2026) |

Outros fatos confirmados:
- **Federação União Progressista (União Brasil e PP).** Anunciou em 02/09/2025 o rompimento com o governo e a entrega de cargos em até 30 dias. Em 18/09/2025, o União Brasil deu 24 horas para filiados deixarem cargos (Gazeta do Povo; Metrópoles; Portal Norte). Algumas reportagens falam em ruptura "institucional", com preservação de nomes ligados a Alcolumbre.
- **Desincompatibilização de 2026.** Entre 16 e 18 ministros deixaram o governo até 03–04/04/2026 para disputar eleições; as fontes divergem no número. A maioria foi substituída por secretários-executivos (Band; IstoÉ; Itatiaia; TMC; CartaCapital).

**Não confirmado** (marcar `[verificar]`):
- data exata da troca Daniela Carneiro → Celso Sabino no Turismo (2023) e filiação partidária de Daniela na saída;
- partido e status de Waldez Góes (Integração);
- sucessor de Juscelino Filho (Pedro Lucas Fernandes era citado como provável);
- situação de Fufuca e Sabino após abril de 2026;
- contagem exata de pastas por partido em cada data.

Para codificar a variável de "partido no ministério" por mês, recomenda-se cruzar com uma base sistemática, como os dados de gabinetes de Amorim Neto ou o DOU.
