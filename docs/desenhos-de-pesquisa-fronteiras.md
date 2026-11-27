# Desenhos de pesquisa: fronteiras de avanço selecionadas

Disciplina *A TPC revisitada* (USP, 2026). Este documento detalha as dez propostas do item (c) escolhidas nos arquivos `-bc.md`. Elas estão ancoradas nos dados do repositório `chamberofdeputiesBrazil` (`dados/leg55`–`leg57` e `dados/tse`) e nas fontes de emendas: Portal da Transparência, SIAFI, SIOP e PNCP.

**Como ler.**
- A seção 1 descreve a infraestrutura comum. Ela vem antes porque a maior parte dos desenhos depende das mesmas ligações entre bases e das mesmas correções de lacunas.
- As seções 2 a 5 trazem cada desenho, com: pergunta, hipóteses, unidade e período, operacionalização (com os nomes das colunas existentes), estratégia de identificação, ameaças, dados a coletar e viabilidade.
- A seção 6 mostra como combinar os desenhos em artigos ou capítulos.
- Fatos institucionais citados sem página (datas de ECs, decisões do STF, trocas de ministros) estão **[fora da bibliografia]** e devem ser conferidos em fonte antes de entrar num texto.

---

## 1. Infraestrutura comum

### 1.1 O que o repositório já tem (verificado)

| Tabela | Cobertura | Uso principal |
|---|---|---|
| `votos` | leg55: 308.714 votos em 899 votações nominais; leg56: 800.141 em 2.271; leg57: 473.323 em 1.604 (até 11/11/2026) | VD de disciplina; já traz `orientacao_partido`, `orientacao_governo`, `seguiu_orientacao_*`, `orientacao_fonte` (partido, federação ou bloco) |
| `votacoes` | Plenário **e** comissões (por exemplo, CCJC); `tem_votos_nominais`, `tem_orientacao`, `objeto_*`, `proposicao_*` | Tipo de votação (mérito, requerimento, destaque); arena |
| `votacoes_orientacoes` | Orientação por bancada, incluindo **Governo, Maioria, Minoria e Oposição** | Orientação do governo onde `votos` não a tem |
| `lideres` | Líder e vice-líderes com datas, inclusive "Governo na CD" e "Governo no CN" | Proxy de orientação (1.3); quem controla a bancada |
| `mesa` | Presidência da Câmara com datas (por exemplo, Lira 2023-02-01 a 2025-02-01; Motta desde 2025-02-01) | Alinhamento entre o Executivo e a Presidência da Câmara |
| `proposicoes`, `proposicoes_autores` | Só proposições com **deputado autor** (leg57: 239.509): PL, REQ, EMC, EMP, DTQ, PRL… | Destaques (DTQ), emendas de plenário e de comissão (EMP, EMC), pareceres (PRL → relator) |
| `deputados_partidos`, `deputados_historico` | Filiação e status com datas (licenças, posses) | Trocas de partido; quem estava em exercício em cada data (para medir ausência) |
| `deputados_complemento` | `cpf_hash` | **Chave Câmara ↔ TSE** |
| `tse/depfed_resumo` | 2018, 2022 e 2026; concentração, HHI, reduto e **receitas por fonte (`receita_fefc`, `receita_fundo_partidario`…)** | Base eleitoral; dependência do partido para financiar a campanha |
| `tse/votacao_depfed_municipio` | Votos por candidato e município, 2018/2022/2026 | Peso de cada município na base do deputado |
| `tse/candidatos_municipais` | **Prefeitos 2020 e 2024** (5.601 e 5.568 eleitos), com partido e federação | Alinhamento dos prefeitos da base |
| `tse/candidatos_gerais` | Governadores, senadores e deputados de 2018, 2022 e 2026 | Partido do governador por UF |

### 1.2 Lacunas: situação após o PR #5 (atualizado em 26/11/2026)

| # | Lacuna | Situação | Consequência para os desenhos |
|---|---|---|---|
| L1 | Orientação do governo antes de 2020 | ✅ **Era um bug do script** (a Câmara usa `GOV.` até 2022). Corrigido e regenerado. Votações de plenário com orientação do governo, conferidas no master: 2011 = 78/89, 2014 = 57/72, 2015 = 247/275, 2016 = 149/196, 2018 = 103/135, 2019 = 254/316, 2021 = 623/755 | A VD "seguiu o governo" fica disponível de 2007 a 2026, sob cinco presidentes |
| L2 | Proposições do Executivo | ✅ `dados/executivo/`: 17.588 proposições desde 2007, mais tramitações (pela API, porque o arquivo em massa é incompleto) e relacionadas | O funil (3-c.2) fica executável |
| L3 | TSE municipal de 2016 | ✅ Eleições municipais de 2008 a 2016 e gerais de 2010 e 2014 (com doações de empresas). Nova chave `nome_nasc_hash` para 2024, porque o TSE passou a mascarar o CPF: concorda com o CPF em 97-98% dos casos | 7-c.2 ganha mais choques de posse de prefeitos (jan./2009, 2013, 2017, 2021, 2025) |
| L4 | leg54 (e leg53) | ✅ Baixadas | Há período anterior à EC 86/2015 (4-c.1) |
| L5 | Partido de cada ministério, mês a mês | ✅ (a) base por ministro, de Sarney a Lula 3, completada com o Lula 3 até nov./2026 (`partido_gabinete_ministerio_atualizado.csv`, com fonte por linha); (b) índice de proporcionalidade de Acir Almeida (Ipea, NT 53/2021) estendido de abr./2024 até abr./2026 (gabinetes Lula 3-5 a 3-14). A fórmula, similaridade de cosseno entre o vetor de pastas e o de cadeiras, foi reproduzida nos 52 gabinetes originais com erro < 10⁻¹³ | 6-c.2 e 6-c.3 executáveis. Ressalvas: o CSV e o Ipea codificam de forma diferente as entradas de set./2023 (Fufuca e Sílvio Costa Filho como "ind" ou como PP); cadeiras = deputados em exercício na data, o que muda Prop_v1 em ~0,2 ponto no gabinete-ponte Lula 3-4; partido de vários substitutos de abr./2026 "a verificar" |
| L6 | Emendas por autor e com datas | ⏳ Aguardando os arquivos | Ver 1.4 |
| L7 | Deputados em exercício por data | ✅ `deputados_exercicio`: 512-513 em exercício por data; 99,99% dos votos caem num período de exercício | A ausência estratégica (4-c.3) fica mensurável |

### 1.3 Proxy de orientação do governo (agora só como robustez)

Com a correção da L1, o proxy deixa de ser necessário como fonte principal. Continua útil para preencher as votações sem orientação registrada e como teste de robustez.

Quando a orientação do governo existe, o voto Sim/Não do **Líder do Governo na CD** coincide com ela em:
- **leg56:** 324 de 326 votações (99,4%);
- **leg57:** 833 de 845 votações (98,6%).

Na leg55, o Líder do Governo votou em **539 das 899** votações nominais, o que basta para validar o proxy também nesse período.

Regra proposta:
1. Usar a orientação oficial; se não houver, a de `votacoes_orientacoes` (bancada "Governo").
2. Se não houver nenhuma das duas, usar o voto do Líder.
3. Se o Líder não votou, usar a moda dos vice-líderes do governo.

Registrar a fonte em uma coluna, para testes de robustez sem a imputação.

### 1.4 Arquitetura dos dados de emendas

Cada desenho precisa de algum destes recortes: **autor × emenda × RP × beneficiário (município ou UF) × data de cada documento**.

- **SIOP:** cadastro da emenda (número, autor, RP6, RP7, RP8 ou RP9, ação, localizador, valor aprovado). É a fonte da *alocação*.
- **Portal da Transparência:** emendas parlamentares (autor, código, função, município favorecido, valores empenhado, liquidado e pago por ano) e transferências especiais. A API tem os documentos de despesa por emenda (a verificar).
- **SIAFI e Tesouro Gerencial:** a cadeia **empenho → liquidação → ordem bancária** com **datas**. É a fonte do *momento*, essencial para os desenhos de troca (6-c.1, 4-c.1).
- **PNCP:** contratações financiadas, para seguir o *uso final* (desfecho opcional).
- **Ligação autor ↔ deputado:** nome normalizado e UF, com validação manual dos casos ambíguos. As emendas de bancada (RP7) têm como "autor" a bancada da UF, e as de comissão (RP8), a comissão.

**Painéis-base a construir uma única vez:**
- **P1 deputado × votação:** voto, orientação do partido e do governo (com o proxy), divergência entre as duas orientações, tipo de votação e arena.
- **P2 deputado × dia:** empenhos e pagamentos das emendas de autoria do deputado, por RP.
- **P3 deputado × município × ano:** peso eleitoral do município, prefeito e seu partido, emendas destinadas.
- **P4 partido × mês:** ministérios, cargos, despesa discricionária dos ministérios (RP2), apoio médio ao governo e presidente da Câmara.

### 1.5 Choques institucionais dentro da janela 2015-2026 (agora com dados desde 2007) [fora da bibliografia — conferir]

| Data | Choque | Usado em |
|---|---|---|
| 2015 | EC 86: emendas individuais impositivas | 4-c.1 (com a leg54 como período anterior) |
| 2015-2016 | Presidência da Câmara em conflito aberto com o governo | 6-c.3, 3-c.2 |
| 2020 | EC 100 (bancada impositiva) e EC 105 (transferências especiais) passam a valer | 7-c.3, 6-c.2 |
| 2020-2022 | RP9 (emendas de relator) | 6-c.2, 6-c.3 |
| dez./2022 | STF declara o RP9 inconstitucional; EC 126/2022 redistribui os recursos | 6-c.2 |
| jan./2023 | Troca de presidente da República | Confundidor de muitos choques |
| set./2023 | Entrada de PP e Republicanos no ministério | **6-c.2 (evento limpo)** |
| ago./2024 | STF suspende a execução de emendas até haver regras de transparência | **4-c.1, 6-c.1 (evento limpo, mesmo governo)** |
| fim de 2024 | Nova lei complementar sobre emendas | 4-c.1, 6-c.2 |
| jan./2025 | Posse dos prefeitos eleitos em 2024 | **7-c.2 (evento limpo, mesmo presidente e mesma legislatura)** |
| fev./2025 | Troca da Presidência da Câmara (Lira → Motta) | 3-c.2, 6-c.3; confundidor de 7-c.2 |

**Regra de ouro:** priorizar os choques que ocorrem **dentro do mesmo governo e da mesma legislatura**, marcados como "evento limpo". Choques que coincidem com a troca de governo (dez./2022–jan./2023) só servem com um desenho que separe os dois efeitos.

---

## 2. Aula 3: agenda e política constitucional

### 3-c.2 O funil da agenda do Executivo (seleção antes da votação)

**Pergunta.** Quanto da "cooperação" medida nas votações nominais resulta de filtros anteriores ao voto (o que o Executivo envia, o que a Mesa pauta, o que vai a voto nominal)? Esses filtros variam com o alinhamento entre o Executivo e a Presidência da Câmara?

**Hipóteses.**
- H1: a probabilidade de uma proposição do Executivo chegar ao plenário, e a velocidade com que chega, caem quando a Presidência da Câmara não é aliada.
- H2: nesses períodos, cresce a proporção de MPs que perdem validade sem voto.
- H3: a taxa de sucesso *condicionada* a ir a voto **não** cai, ou cai pouco. É a assinatura da seleção: o filtro age antes do voto.
- H4: a distância entre o texto enviado e o texto aprovado cresce quando o Executivo não controla a pauta.

**Unidade e período.** Proposição do Executivo (PL, PLP, PEC, PLN e MPV), de 2007 a 2026. Há variação entre períodos de conflito (2015-16), de presidência da Câmara autônoma e de alinhamento negociado (2021-25), sob três presidentes da República.

**Operacionalização.**
- *Eventos do funil:* apresentação, despacho, parecer em comissão, requerimento de urgência (entre os REQ de líderes, filtrar a ementa "urgência"), inclusão na ordem do dia, votação simbólica ou nominal, sanção ou promulgação, veto, perda de validade (MPV).
- *Alinhamento:* uma dummy e uma medida contínua. A contínua é o percentual de votos do partido do Presidente da Câmara que seguiram o governo no mês anterior, calculado em P1.
- *Distância textual (H4):* similaridade entre o inteiro teor original (`urlInteiroTeor`) e a norma publicada (LexML ou Planalto), por dispositivo, estendendo Freitas (2016) para a **população** de proposições e não só para as vetadas.

**Identificação.**
- **Modelo de sobrevivência** (Cox, ou riscos competitivos: "votada", "perdeu validade", "arquivada"), com o alinhamento variando no tempo, efeitos fixos de tema e controles de tipo e urgência.
- **Modelo de seleção** (probit bivariado ou de Heckman): o primeiro estágio estima a chance de ir a voto nominal, e o segundo, o resultado condicionado. A exclusão no primeiro estágio pode vir do calendário: semanas com sessões concentradas (esforço concentrado, fim de semestre) afetam a chance de pautar, mas não o mérito. Essa hipótese precisa ser defendida.
- **Placebo:** proposições de deputados da base com tema equivalente não devem reagir ao alinhamento da Presidência da Câmara da mesma forma.

**Ameaças.**
- O Executivo antecipa o filtro e deixa de enviar o que não passaria. Isso é invisível para o funil, mas *o volume enviado por mês* pode ser testado como desfecho.
- A troca de presidente da República confunde. Comparar dentro de cada governo.

**Dados.** L2 resolvida (`dados/executivo/`, desde 2007). Falta só o texto final das normas, para H4.
**Viabilidade:** alta, agora com custo de extração baixo. **Produto:** artigo autônomo; o funil vira infraestrutura para os demais desenhos.

### 3-c.5 Política constitucional e execução orçamentária (componente transversal)

Como você observou, este desenho não se sustenta sozinho: ele é a **moldura** que liga os demais.

**Pergunta.** As emendas constitucionais orçamentárias de 2015 a 2022 redistribuíram poder de agenda do Executivo para o Legislativo, um canal que a TPC não mede?

**Construção.** Um **Índice de Discricionariedade do Executivo (IDE)** por ano e por mês. É a parcela da despesa discricionária (primária, não obrigatória) cuja alocação ou cujo momento de execução o Executivo controla. Na prática:
- RP2 (discricionária do Executivo) dividida por RP2 + RP6 + RP7 + RP8 + RP9.
- Uma versão "momento": a parte do RP6 e do RP7 cuja execução tem data discricionária. A impositividade obriga a executar no exercício, mas o calendário continua com o Executivo. **Essa distinção é central:** a impositividade tirou do Executivo o *se* e a *destinação*, mas não o *quando*.

**Como entra nos outros desenhos.**
- Moderador em 3-c.2: o filtro de agenda importa mais quando o IDE é baixo?
- Moderador em 6-c.1 e 6-c.2: o preço do voto sobe quando o IDE cai?
- Moderador em 4-c.1: separa a dependência do governo da dependência do partido.

**Limitação honesta.** Com cerca de 12 anos de série, o IDE agregado anual só sustenta análise descritiva e série interrompida. O poder estatístico vem de **desagregar o IDE por ministério e por mês**, combinado com a variação entre deputados dos outros desenhos.

---

## 3. Aula 4: disciplina partidária

### 4-c.1 Emendas como moeda: separar a patronagem presidencial (cadeia C) da organização partidária (cadeia D)

**Pergunta.** Quando o Executivo perde o controle sobre as emendas, a disciplina em relação ao **governo** cai mais do que a disciplina em relação ao **partido**?

**Reformulação da VD (de 4-c.5).** Usar P1 restrito às votações em que **a orientação do partido e a do governo divergem**. É ali que está a informação (Aula 4, b.1.1). A VD é binária: seguiu o governo contra o partido, só para deputados de partidos da base.

**Choques utilizáveis (ordem de preferência).**
1. **Suspensão da execução das emendas pelo STF (ago./2024) e retomada após a nova lei (fim de 2024).** Mesmo governo e mesma legislatura, com orientação do governo presente em cerca de 77% das votações de 2024 (347/448). **Este é o choque principal.**
2. **EC 100/2019 e RP9 (2020-2022).** Mesmo governo, com orientação do governo em cerca de 80% das votações de 2019 a 2022 depois da correção da L1.
3. **EC 86/2015.** Agora viável: a leg54 (2011-2014) dá o período anterior, e a orientação do governo está disponível nos dois lados. O choque coincide com o início da leg55 e com a crise de 2015. Por isso a comparação deve ser restrita aos deputados reeleitos de 2010 para 2014 (efeito fixo de deputado), e a Presidência da Câmara em conflito com o governo entra como controle.

**Tratamento contínuo (dose).** A *dependência de emendas* do deputado antes do choque, medida de três formas:
- **(i)** o valor pago das suas emendas no ano anterior, sobre a média da bancada;
- **(ii)** a concentração da votação (`concentracao`, `hhi_municipios` em `depfed_resumo`), na linha de Ames, porque bases concentradas dependem mais de entregar obras;
- **(iii)** o mandato de estreante (`deputados_complemento`).

**Separar a cadeia D.** A *dependência do partido* é medida por `receita_fefc` somada a `receita_fundo_partidario`, sobre `receita_total` da campanha de 2022 (`depfed_resumo`).
- Previsão da cadeia C: deputados com muita dependência de emendas e pouca do partido reagem mais ao choque, seguindo menos o governo enquanto o pagamento está suspenso.
- Previsão da cadeia D: deputados muito financiados pelo partido não reagem.

**Especificação.** Estudo de evento deputado × votação com efeitos fixos de deputado e de votação. O efeito fixo de votação absorve o conteúdo e o placar. Interações: dose × janela pós-choque, e dose × janela × dependência do partido. Erros agrupados por deputado e por votação (*two-way clustering*).

**Ameaças e testes.**
- **Composição da pauta:** o efeito fixo de votação ajuda, e pode-se repetir a análise só com votações de mérito.
- **Antecipação:** a suspensão foi anunciada, então é preciso verificar as tendências anteriores.
- **Placebo:** deputados de oposição não devem reagir.
- **Correção para múltiplos testes** entre as três medidas de dose.

**Dados a coletar.** L6 (emendas por autor com datas de pagamento) e a validação do autor da emenda.
**Viabilidade:** alta, porque o choque principal está todo na leg57 já baixada. **Produto:** é o artigo central para a pesquisa sobre emendas e gestão de coalizão.

### 4-c.3 Dissenso fora do plenário

**Pergunta.** O controle de pauta desloca o dissenso para arenas anteriores ao voto (MPL 1998, p. 127)? A disciplina medida no plenário e o dissenso fora dele são **substitutos**?

**Indicadores de dissenso** (todos com os dados atuais, salvo indicação):

| Indicador | Construção | Fonte no repositório |
|---|---|---|
| Ausência estratégica | Em exercício na data e sem voto registrado, com efeito fixo de deputado para separar da ausência habitual | `votos` + `deputados_historico` (L7) |
| Obstrução e abstenção contra a orientação | `voto` ∈ {Obstrução, Abstenção} quando o partido orientou Sim ou Não | `votos` (obstruções: 18.440 na leg55, 13.666 na leg56, 5.272 na leg57) |
| Destaque contra a orientação | DTQ de bancada sobre matéria em que o partido orientou o voto principal | `proposicoes` (DTQ = 1.666 na leg57) + `votacoes` |
| Emenda contra o relator do próprio partido | EMP ou EMC de um deputado sobre proposição cujo relator (autor do PRL) é do mesmo partido | `proposicoes_autores` (PRL = 41.336 e EMC = 10.660 na leg57) |
| Dissenso em comissão | Votos nominais em comissões (por exemplo, a CCJC) contra a orientação | `votacoes.siglaOrgao` ≠ PLEN |

**Hipóteses.**
- H1: em matérias com urgência e pauta controlada pela Mesa, o dissenso no plenário é baixo e o dissenso fora dele é alto. Há substituição.
- H2: a substituição é maior em partidos com organização descentralizada, ligando aos achados de RLA 2022.
- H3: o dissenso fora do plenário prediz votos contrários em votações *futuras* do mesmo tema, um teste de validade preditiva.

**Identificação.** Painel deputado × proposição, com efeitos fixos de proposição. O desenho é descritivo-explicativo e não depende de choque. A contribuição principal é uma **nova medida**: um índice de dissenso multiarena, validado contra o voto.

**Viabilidade:** muito alta, quase tudo já está no repositório. **Produto:** artigo de mensuração. A medida também serve como controle e desfecho em 4-c.1 e 3-c.2.

---

## 4. Aula 6: formação e performance da coalizão

### 6-c.1 O custo de governo com componentes discricionários e momento de execução

**Pergunta.** O apoio legislativo responde ao **momento** da liberação de recursos discricionários, e não ao seu volume anual?

**Diferença em relação a B&P 2017.** O ICG soma estoques e fluxos, incluindo gastos obrigatórios (Aula 6, b.2.2). Aqui a medida é **por deputado, por dia e por RP**, e o desfecho é o voto.

**Construção.**
- P2: valores empenhados e pagos, por dia, das emendas do deputado, separados por RP6, RP7 (rateado pela bancada), RP8 e RP9.
- **Janelas em torno de votações-chave:** votações em que o governo orientou e o placar foi apertado, isto é, com margem menor que 10% em relação ao quórum exigido, calculada a partir de `votosSim` e `votosNao`.
- **Pivotalidade do deputado:** probabilidade prevista de votar com o governo a partir de pontos ideais estimados com votações *anteriores*. Os "indecisos" ficam entre 0,3 e 0,7.

**Hipóteses.**
- H1: os pagamentos se concentram nos dias anteriores às votações-chave e entre os indecisos.
- H2: receber pagamento na janela aumenta a probabilidade de votar com o governo, sobretudo entre os indecisos.
- H3: o efeito existe **também no RP6 impositivo**, porque o momento continua discricionário (ver 3-c.5).

**Identificação.**
- **Estudo de evento** com efeitos fixos de deputado e de votação. A comparação é entre deputados igualmente pivotais que receberam ou não na janela.
- **Placebo temporal:** pagamentos *depois* da votação não devem "prever" o voto.
- **Placebo de votações:** votações não chave.
- **Endogeneidade:** o governo paga a quem já ia votar a favor. O efeito fixo de deputado e a restrição aos indecisos atenuam o problema, mas não o eliminam. Por isso, explorar também o **choque de ago./2024**, quando o canal foi fechado externamente.

**Dados a coletar.** L6 com datas, a cadeia de documentos do SIAFI. A reconstrução da cadeia empenho → liquidação → ordem bancária já resolve a maior parte do problema. Os cargos (DAS e, depois, CCE e FCE) por partido ficam como extensão, porque a filiação dos nomeados exige cruzar com as listas de filiados do TSE, com erro de classificação.

**Viabilidade:** média-alta, porque o gargalo é ligar emenda, autor e datas. **Produto:** artigo central, junto com 4-c.1.

### 6-c.2 Substituição de moedas depois da impositividade

**Pergunta.** Quando a lei fixa a oferta de uma moeda (emendas impositivas), o governo passa a pagar mais com as moedas que sobram (pastas, RP2, emendas não impositivas)? O preço por voto sobe?

**Dois testes complementares.**

**(a) Evento ministerial limpo: entrada de PP e Republicanos no gabinete em set./2023.**
- É um DiD com deputados de PP e Republicanos (tratados) contra deputados de partidos de centro-direita já no gabinete, como União, PSD e MDB (controles), com mesmo governo e mesma legislatura.
- O desfecho é seguir o governo nas votações com orientação divergente (P1).
- Se a pasta compra apoio, os tratados devem convergir. Se a moeda relevante já eram as emendas, o efeito deve ser pequeno.
- É o teste mais limpo disponível da premissa "pastas como combustível" (Limongi 2006, p. 254).

**(b) Série de choques sobre a oferta de emendas.**
- Os choques são EC 100 (2020), RP9 (2020-2022), STF e EC 126 (dez./2022), suspensão (ago./2024) e nova lei.
- Para cada partido e mês, calcular: o **mix de moedas** (pastas, RP2 dos ministérios do partido, RP6, RP7, RP8 e RP9 dos seus deputados) e o **preço por voto** (recursos discricionários sobre votos a favor do governo nas votações com divergência).
- Série interrompida por partido, com efeitos fixos de partido e de mês.

**Hipóteses.**
- H1: depois de cada redução da discricionariedade sobre emendas, cresce a participação de pastas e RP2 no mix.
- H2: o preço por voto sobe.
- H3: a negociação migra para os canais não impositivos (RP8 e RP9). A migração para o RP8 depois de 2022 é testável.

**Ameaças.** Troca de governo em jan./2023, que faz o teste (a) ter precedência. Inflação e teto de gastos: deflacionar e expressar tudo como parcela da despesa discricionária total.

**Dados.** L5 resolvida (ver 1.2). Falta L6.
**Segundo evento limpo, revelado pela L5:** em 02/09/2025, a federação União Progressista anunciou a saída de União e PP da base, mas seus ministros (Sabino e Fufuca) ficaram; em 18/09 o União deu 24 horas para os filiados deixarem os cargos. O União voltou ao Turismo em 19/12/2025. É o choque inverso do de set./2023: **o partido sai sem perder a pasta**. Se as pastas compram apoio partidário, a disciplina governista de União e PP deve cair em set./2025 mesmo com os ministros no cargo, e voltar no caso do União depois de dez./2025. Na série estendida do Ipea, Prop_v1 cai de 75,9 para 72,7 com o desembarque e sobe para 77,9 com a volta do União.
**Viabilidade:** (a) é **alta**, porque basta P1 e a data do evento; (b) é média. **Produto:** (a) é uma nota de pesquisa rápida, com resultado em semanas; (b) é capítulo.

### 6-c.3 Formação de coalizão com dois formadores (avanço teórico)

**Pergunta.** Quando a Presidência da Câmara controla pauta e recursos orçamentários, o presidente da República deixa de ser o formador único? Como isso muda o custo e a forma da coalizão?

**Modelo (esboço).** São três tipos de jogador:
- o Presidente da República (P), que oferece pastas *m* e posições de política *x*;
- o Presidente da Câmara (H), que oferece acesso à pauta *a* e recursos sob seu controle *b* (RP9 até 2022 e, depois, influência sobre o RP8);
- os partidos *i*, com utilidade *u_i(m, x, a, b)*.

O apoio de *i* a P depende também do alinhamento entre H e P. Com H alinhado, as ofertas são complementares e o custo para P cai. Com H autônomo, P precisa cobrir a oferta de H.

**Predições testáveis.**
- (1) o custo em pastas por cadeira de apoio é maior com H não alinhado;
- (2) a **divergência entre a coalizão ministerial e a legislativa** cresce. Isso testa a crítica b.1.1 da Aula 6;
- (3) partidos próximos de H ganham apoio de "preço" mais alto.

**Operacionalização.**
- *Coalizão legislativa mensal:* partidos com mais de 70% de votos com o governo nas votações com divergência, calculado em P1.
- *Coalizão ministerial:* L5.
- *Índice de divergência:* distância de Jaccard entre os dois conjuntos, ponderada por cadeiras.
- *Alinhamento de H:* tabela `mesa` mais o comportamento da bancada de H.
- *Controle de recursos por H:* volume do RP9 e, depois de 2022, do RP8.

**Casos para traçar o processo.** 2015-16 (conflito aberto), 2019-20 (Presidência da Câmara autônoma diante de um governo sem coalizão formal), 2021-22 (H alinhado e com controle do RP9), 2023-24 (H transacional com o novo governo) e 2025-26 (troca de H).

**Identificação.** É principalmente teórica e comparativa entre períodos (N pequeno de configurações). O peso empírico vem de usar mês × partido como unidade e dos testes (a) de 6-c.2 e de 3-c.2 como evidências convergentes.
**Viabilidade:** média-alta. A L1 e a L5 estão resolvidas, e a coalizão ministerial mensal pode ser lida da base de ministros atualizada. **Produto:** capítulo teórico da dissertação, com o modelo formalizado e as evidências dos outros desenhos.

---

## 5. Aula 7: federalismo

### 7-c.2 Prefeitos da base no lugar de governadores (replicando CFL 2009)

**Pergunta.** O alinhamento entre o presidente e os prefeitos que formam a base eleitoral do deputado afeta seu apoio ao governo, de um modo que CFL não captam ao olhar para governadores?

**Tratamento.** Para cada deputado *d* e mês *t*:

`AlinhaBase_dt = Σ_m (peso_dm × 1[partido do prefeito de m está na coalizão presidencial em t])`

com `peso_dm` = participação do município *m* nos votos de *d* em 2022 (`votacao_depfed_municipio`, ligada por `cpf_hash`).

**Choque principal: a posse dos prefeitos eleitos em 2024 (jan./2025).**
- O presidente e a legislatura continuam os mesmos e só mudam os prefeitos.
- A variação em `AlinhaBase` entre dez./2024 e fev./2025 é **exógena ao comportamento do deputado em plenário**, porque resulta das eleições municipais, ainda que o deputado tenha feito campanha nelas.
- DiD com tratamento contínuo: ΔAlinhaBase × pós-janeiro de 2025, com efeitos fixos de deputado e de votação.

**Choque secundário: troca do presidente em jan./2023.** Os prefeitos de 2020 são os mesmos, mas a coalizão presidencial muda e, com ela, o alinhamento dos mesmos prefeitos. Esse choque coincide com a troca de legislatura, então serve só para os deputados reeleitos de leg56 para leg57.

**Hipóteses.**
- H1: maior alinhamento da base leva a mais apoio ao governo.
- H2: o efeito é maior para deputados com votação concentrada (`hhi_municipios`) e para votações distributivas.
- H3: o efeito é **mediado por emendas**. Depois do choque, as emendas do deputado (RP6 e transferências especiais) migram para os municípios cujo prefeito é aliado do governo, e isso explica parte do efeito sobre o voto. É uma análise de mediação com P3.

**Ameaças.**
- **Troca da Presidência da Câmara em fev./2025, uma semana depois.** É um choque comum, absorvido pelo efeito fixo de votação e de mês, mas pode interagir com o tratamento: deputados de bases que mudaram podem ser os mesmos próximos do novo presidente. Controlar pela proximidade partidária com H.
- **Seleção:** deputados que ajudaram a eleger prefeitos aliados podem já estar se movendo para o governo. Verificar as tendências anteriores em 2024.
- **Medida:** usar o partido do prefeito na posse (TSE 2024) e atualizar as trocas de partido quando houver dados.

**Dados.** Nada essencial falta para o choque de 2025, porque tudo já está em `tse/` e `leg57`. Para os prefeitos de 2024, a ligação usa `nome_nasc_hash`, já que o CPF está mascarado. Para o mediador, falta L6 com o município favorecido. Com a L3 resolvida, **o mesmo desenho pode ser repetido nas posses de 2009, 2013, 2017 e 2021**, todas no meio de uma legislatura. Isso transforma um evento único em **cinco réplicas** sob presidentes diferentes, com estimativa conjunta e análise de heterogeneidade por governo. Atenção: em todas as posses, a eleição da Mesa da Câmara acontece em fevereiro. Ela só troca de presidente em algumas (por exemplo, 2021 e 2025). As réplicas sem troca na Presidência da Câmara servem de teste para a ameaça descrita acima.
**Viabilidade:** **muito alta**, sendo o desenho mais pronto de todos. **Produto:** artigo autônomo. É a contribuição mais original à Aula 7, porque desloca o eixo federativo do governador para o prefeito.

### 7-c.3 A bancada estadual na arena orçamentária

**Pergunta.** A Federação se organiza no Congresso pela **arena orçamentária** (emendas de bancada, RP7) mais do que pela arena de votação, onde Arretche (2013) encontra baixa coesão das bancadas?

**Medidas.**
- *Coesão da bancada estadual no plenário:* índice de Rice por UF e votação (`votos.deputado_siglaUf`), em votações com orientação do governo e em matérias federativas (por classificação temática de `proposicoes_temas` ou da ementa).
- *Coordenação orçamentária da bancada:*
  - (i) concentração das emendas RP7 por ação e destinatário (HHI);
  - (ii) **parcela do RP7 destinada ao governo estadual** (transferências ao estado), em contraste com municípios;
  - (iii) sobreposição entre os municípios contemplados pelo RP7 e os redutos dos deputados da bancada (P3).
- *Alinhamento do governador:* partido do governador eleito em 2018 e 2022 (`candidatos_gerais`) com a coalizão presidencial e com a maioria da bancada.

**Hipóteses.**
- H1: a parcela do RP7 destinada ao governo estadual é maior quando o partido ou a coalizão do governador tem a maioria da bancada. É a **influência do governador pela via orçamentária**.
- H2: a coordenação orçamentária é alta mesmo onde a coesão no plenário é baixa: as duas arenas estão **dissociadas**.
- H3: depois da EC 100 (impositividade do RP7 a partir de 2020), a parcela destinada ao governo estadual cresce em estados de governadores não alinhados com o presidente, porque o RP7 vira o canal de compensação.

**Identificação.** Painel UF × ano (27 × cerca de 10) com efeitos fixos de UF e de ano. A troca de governador em 2019 e em 2023 dá variação dentro da UF. O N é pequeno, então os resultados devem ser lidos como evidência complementar, com inferência por permutação (*randomization inference*).

**Dados a coletar.** L6 restrito ao RP7 (SIOP e Portal, com autor "Bancada de UF", ação, favorecido), uma classificação das votações federativas e a lista dos coordenadores de bancada (opcional).
**Viabilidade:** média. **Produto:** seção de artigo, ou extensão de 7-c.2 num artigo sobre o "canal federativo das emendas".

---

## 6. Combinações e priorização

### 6.1 Como os desenhos se combinam

```
                 Infraestrutura (P1–P4, proxy de orientação, emendas com datas)
                                        │
   ┌───────────────────────────┬────────┴────────────┬─────────────────────────┐
   │ A. Emendas como moeda     │ B. Agenda e seleção │ C. Canal federativo     │
   │  4-c.1  (choque 2024)     │  3-c.2  (funil)     │  7-c.2 (prefeitos 2025) │
   │  6-c.1  (momento)         │  4-c.3  (dissenso)  │  7-c.3 (RP7 bancadas)   │
   │  6-c.2a (pastas set/2023) │                     │                         │
   └─────────────┬─────────────┴─────────┬───────────┴────────────┬────────────┘
                 │                       │                        │
                 └──── 3-c.5 (IDE: moderador transversal) ────────┘
                                         │
                       6-c.3 (teoria dos dois formadores: síntese)
```

- **Programa A** é o núcleo da pesquisa sobre emendas e gestão de coalizão. As três peças usam P1 e P2 e testam a mesma pergunta (qual moeda compra apoio, e quando) com choques diferentes.
- **Programa B** testa a crítica principal de todas as aulas: a evidência ex post mede *se* passou, e não *o que foi filtrado*.
- **Programa C** leva o argumento à Federação usando a mesma infraestrutura (P3).
- **3-c.5** é o moderador comum, e **6-c.3** é o fecho teórico que interpreta os resultados de A e B.

### 6.2 Priorização

| Desenho | Dados já disponíveis | Coleta adicional | Identificação | Ordem sugerida |
|---|---|---|---|---|
| 6-c.2a (pastas, set./2023) | P1 completo na leg57 | Nenhuma, só a data do evento | DiD limpo | **1º: teste rápido** |
| 7-c.2 (prefeitos, jan./2025) | leg57 + TSE | Emendas por município, só para o mediador | DiD contínuo limpo | **2º** |
| 4-c.3 (dissenso multiarena) | Tudo (L7 resolvida) | Nenhuma | Mensuração | **3º**, porque a medida alimenta os demais |
| 4-c.1 (choque de ago./2024) | leg57 + TSE (FEFC, HHI) | L6 por autor | Estudo de evento, dose contínua | **4º: artigo central** |
| 6-c.1 (momento dos pagamentos) | P1 | L6 com datas do SIAFI | Estudo de evento + placebos | 5º, junto com 4-c.1 |
| 3-c.2 (funil) | `dados/executivo/` desde 2007 (L2 resolvida) | Texto final das normas (só para H4) | Sobrevivência + seleção | **4º, em paralelo** (já executável) |
| 7-c.3 (RP7) | Votos por UF, governadores | L6 do RP7 | Painel com N pequeno | 7º |
| 6-c.2b (série de choques) | L5 resolvida (gabinetes e proporcionalidade até abr./2026) | L6 | Séries interrompidas | 8º |
| 3-c.5 (IDE) | — | SIOP/Tesouro agregados | Descritivo | Em paralelo, como insumo |
| 6-c.3 (teoria) | — | Depende dos anteriores | Formal + convergência | Último: síntese |

### 6.3 Cuidados metodológicos comuns
- **Pré-registro** das hipóteses e especificações principais antes de olhar os resultados de 4-c.1, 6-c.1 e 7-c.2. São estudos de evento com muitas escolhas possíveis de janela e de dose.
- **Erros agrupados** em duas dimensões (deputado e votação) em todos os painéis deputado × votação.
- **Restrição às votações com orientação divergente** entre o partido e o governo como especificação principal, e todas as votações orientadas como robustez.
- **Fonte da orientação** (oficial, bancada Governo ou proxy) como variável de controle e de exclusão nos testes de robustez.
- **Deflação** dos valores e normalização pela despesa discricionária total do ano.
- **Ligação autor ↔ deputado das emendas:** relatar a taxa de correspondência e os casos manuais. É a principal fonte de erro de medida.
