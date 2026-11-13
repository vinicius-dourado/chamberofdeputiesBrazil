# Methodology Blueprint — Presidencialismo de coalizão no Brasil (1985–2026)

> Fase 1 (escopo) do ARS, agente `research-architect-agent`. Entregável único: o desenho metodológico.
> A busca de literatura, a bibliografia anotada, a síntese e a redação são fases posteriores e não estão aqui.

## Pergunta de pesquisa (como formulada pelo autor)

Revisão da literatura sobre o presidencialismo de coalizão e a formação e gestão de coalizões no Brasil, com a replicação dos achados sobre sete indicadores por mandato presidencial: **partidos, ministérios, ministros sem partido, cadeiras da coalizão, proporcionalidade e heterogeneidade**.

Decomposta em três perguntas operacionais (a confirmar pelo autor):

- **PQ1 (síntese):** como a literatura brasileira descreve e explica a formação e a gestão de coalizões desde 1985? Quais conceitos, medidas e achados se consolidaram?
- **PQ2 (replicação):** os valores publicados para os indicadores de gerência da coalizão se reproduzem a partir das fontes primárias declaradas?
- **PQ3 (atualização):** o que os mesmos indicadores mostram quando a série é estendida até Lula 3 (2023–2026)?

Tipo de pergunta, pela árvore de decisão: **descritiva** (PQ1, PQ3) e **comparativa** (entre mandatos e entre medidas, PQ2). Não há pergunta causal. O desenho não deve prometer explicação causal.

## Research Paradigm

**Selecionado:** pragmatista.

**Justificativa:** a pergunta combina dois componentes de natureza diferente.
- A **síntese da literatura** (PQ1) é interpretativa: organiza conceitos e argumentos.
- A **replicação** (PQ2–PQ3) é positivista na mensuração: os indicadores têm definição operacional, e a reprodução é verificável número a número.

O paradigma pragmatista admite os dois sob o critério de responder à pergunta. A ontologia dos indicadores é tratada como convencional: a "proporcionalidade" depende da fórmula escolhida, e o desenho torna essa escolha explícita em vez de escondê-la.

## Method

**Tipo:** métodos mistos, **sequencial convergente**. A síntese da literatura e a replicação correm em paralelo e se encontram na discussão.

**Método específico:**
1. **Revisão integrativa da literatura**, com busca sistematizada e critérios explícitos. A revisão integrativa (e não a sistemática com meta-análise) é adequada porque os estudos usam medidas e recortes heterogêneos, que não se combinam estatisticamente. Ela também permite integrar estudos teóricos, empíricos e de mensuração.
2. **Replicação descritiva e computacional** dos indicadores por gabinete e por mandato. Os resultados publicados funcionam como "evidência a reproduzir", e não só como evidência a resumir.
3. **Extensão da série** (Lula 3), com os mesmos critérios de codificação da fonte original.

**Justificativa:** a PQ2 exige reprodução numérica, e uma revisão narrativa sozinha não verifica números. A PQ1 exige síntese, e a replicação sozinha não organiza o campo. A combinação é o que diferencia o artigo de uma revisão convencional.

**Alternativa mais simples considerada:** só a revisão narrativa. Ela foi descartada porque já diagnosticamos divergências entre tabelas publicadas (ver Data Strategy), e uma revisão que só relatasse esses números os repetiria sem verificar.

## Data Strategy

**Tipo de dado:** secundário (literatura publicada e bases públicas). Nenhum dado primário com pessoas.

### A. Corpus da literatura (PQ1)

| Item | Decisão proposta | Precisa de decisão do autor? |
|---|---|---|
| Bases | SciELO, Portal de Periódicos CAPES, Google Scholar (triagem complementar), Web of Science ou Scopus para a produção internacional sobre o Brasil | Sim: quais bases o autor acessa |
| Período de publicação | 1988 (Abranches) a 2026 | Confirmar |
| Idiomas | português e inglês | Confirmar |
| Tipos de documento | artigos revisados por pares; livros e capítulos centrais; textos para discussão e notas técnicas do Ipea como fonte de dados | Confirmar a inclusão de teses e dissertações |
| Eixos de busca | (1) presidencialismo de coalizão / *coalitional presidentialism*; (2) formação de coalizão, gabinete, ministérios / *portfolio allocation*, *cabinet formation*; (3) gerência e custo da coalizão / *coalition management*, *coalition goods*; (4) proporcionalidade / coalescência / lei de Gamson; (5) heterogeneidade ideológica da coalizão | Ajustar os termos |
| Inclusão | estudos sobre o Brasil pós-1985 que tratem de formação, composição ou gestão de coalizões no Executivo federal | — |
| Exclusão | estudos só subnacionais (a menos que comparem com o nível federal), estudos só eleitorais, textos opinativos | Confirmar se o nível estadual entra |
| Amostragem | busca exaustiva nos eixos 1–3 e bola de neve (*backward* e *forward*) a partir dos trabalhos centrais | — |
| Triagem | dupla e independente em título/resumo e texto completo, com registro do motivo de exclusão; se não houver segundo revisor, uma nova triagem de 20% da amostra após intervalo | Sim: haverá coautor? |

### B. Dados para a replicação (PQ2–PQ3)

| Fonte | Uso | Situação no repositório |
|---|---|---|
| Almeida (Ipea, NT 53/2021), planilha de gabinetes (mar/1985–jun/2024) | composição partidária, ministros e cadeiras por gabinete; Prop_v1 e Prop_v2 publicados | `coalizao/dados_brutos/almeida_ipea_gabinetes.xlsx` (idêntico ao arquivo do Ipea) |
| Codificação própria de Lula 3 (2023–nov/2026), ministro a ministro | extensão de jul/2024 a nov/2026, com fonte e grau de confiança por linha | `coalizao/dados_brutos/lula3_gabinete_2023_2026.csv` |
| Câmara dos Deputados, Dados Abertos | cadeiras em exercício (Lula 3) | `dados/leg57` (e `leg55`, `leg56`) |
| Zucco & Power (2023), via Atlas do Estado Brasileiro (Ipea); Power & Zucco (2012) | ideologia partidária para a heterogeneidade | `coalizao/dados_brutos/` |
| Tabelas publicadas a replicar | Bertholini & Pereira (RAP 2017, Tabela 1); Pereira & Bertholini (2017, tabela revisada); Almeida (2021) | valores já transcritos em `indicadores_coalizao.py` |

**Unidades de análise:** gabinete (60: 51 de Almeida + 9 de Lula 3), mandato-mês (500 observações, no dia 15 de cada mês) e mandato (12).

**Período:** mar/1985 a nov/2026.

### C. Definição operacional das sete colunas

| Coluna | Definição | Situação no código |
|---|---|---|
| Mandato | período presidencial (Sarney a Lula 3; Dilma 2 até 12/05/2016) | `MANDATOS` |
| Partidos | nº de partidos com ao menos um ministério; média mensal | `tamanho` |
| Ministérios | nº de cargos com status de ministro; média mensal | `n_ministerios` no painel; **falta na tabela por mandato** |
| Sem partido | % dos cargos com ministros sem partido; média mensal | derivável (`ministros_np / n_ministerios`); **falta na tabela por mandato** |
| Cadeiras da coalizão | % da Câmara com os partidos do gabinete (513 desde 1995) | `cadeiras_coalizao_pct` |
| Proporcionalidade | Koppel & Diskin, versão Ipea (Prop_v1, sem partido em grupo); Prop_v2 e coalescência como robustez | `prop_kd_v1`, `prop_kd_v2`, `coalescencia` |
| Heterogeneidade | coeficiente de variação (×100) da ideologia dos partidos do gabinete | `heterogeneidade` |

**Tarefa de dados pendente**, a executar fora desta fase: acrescentar "Ministérios" e "Sem partido (%)" a `tabela1_estendida.csv`, para que a tabela do artigo saia inteira de um script.

## Analytical Framework

### PQ1: síntese integrativa
1. **Extração estruturada** por estudo: período, unidade, conceito de coalizão, medida (fórmula, tratamento dos sem partido, fonte de cadeiras e de ministérios), achado principal e mecanismo proposto.
2. **Matriz conceitual**, com duas dimensões a confirmar: **formação** (quem entra e com quantos ministérios) × **gestão** (instrumentos e custos de manutenção).
3. **Mapa de mensuração:** para cada indicador, quais estudos o usam, com que fórmula e com que valores. É a ponte com a PQ2.
4. **Síntese temática:** convergências, divergências e lacunas. As lacunas vêm da matriz, e não de impressão.

### PQ2: replicação em três níveis

| Nível | Pergunta | Critério de sucesso |
|---|---|---|
| R1. Reprodução computacional | Com os mesmos dados e a mesma fórmula, obtenho os números publicados? | diferença ≤ 0,1 ponto por gabinete (Almeida: já obtido, ≤ 0,05) |
| R2. Replicação da tabela por mandato | As médias por mandato publicadas se reproduzem? | diferença ≤ 1 ponto; acima disso, a divergência é diagnosticada e documentada |
| R3. Robustez de mensuração | As conclusões mudam com outra fórmula, outro tratamento dos sem partido ou outra codificação? | a ordenação dos mandatos e os padrões descritos são reportados para as três medidas |

Situação já conhecida, a registrar no artigo e não a "corrigir":
- **Almeida (Prop_v1, Prop_v2):** R1 atendido.
- **Pereira & Bertholini (2017, revisada):** R2 atendido para os governos do PT e Rousseff 2 (≤ 1 ponto). FHC fica 6 a 8 pontos acima, e a hipótese a documentar é a contagem de cargos sem partido.
- **RAP (2017), Tabela 1:** R2 não atendido. A proporcionalidade publicada não se reproduz com os números do próprio texto.

### PQ3: extensão
1. Codificação de Lula 3-5 a 3-9 com os critérios A/B/C de Almeida.
2. Validação: comparar a codificação própria com Almeida nos gabinetes sobrepostos (Lula 3-1 a 3-4; Prop_v1 já confere em Lula 3-1).
3. Sensibilidade: versão base × versão alternativa (União e PP mantidos; substitutos de 2026 atribuídos ao partido da pasta).

### Apresentação
- **Tabela 1:** os sete indicadores por mandato, média e desvio-padrão.
- **Tabela 2:** replicação, publicado × reproduzido × diferença.
- **Figura:** série mensal de 1985 a 2026.
- **Apêndice:** os três índices por gabinete.
- Estatística só descritiva (médias, desvios, ordenações). Com n = 12 mandatos, testes de associação entre mandatos não têm poder e não devem ser apresentados como evidência.

**Ferramentas:** Python (pandas), scripts já existentes em `coalizao/`, gerenciador de referências à escolha do autor.

## Validity Criteria

| Critério | Estratégia |
|---|---|
| Validade de construto (proporcionalidade) | três medidas reportadas lado a lado; o artigo explica o que cada uma penaliza (sobretudo os sem partido) |
| Confiabilidade da codificação de Lula 3 | fonte por linha; conferência no DOU das linhas de confiança baixa; recodificação independente por um segundo codificador, com concordância reportada |
| Reprodutibilidade | código, dados e versão das fontes publicados (repositório e DOI no Zenodo ou OSF); cada número do texto sai de um script |
| Comparabilidade temporal | as mesmas regras de início de gabinete (A/B/C) e o mesmo tamanho da Câmara por legislatura; a quebra de 2024 (Almeida → codificação própria) é sinalizada |
| Comparabilidade da ideologia | série única reescalonada (Zucco & Power 2023 → escala de 2012, r = 0,9998); Sarney usa a onda de 1990, e isso é declarado |
| Credibilidade da síntese (PQ1) | protocolo de busca registrado; fluxograma de triagem; matriz de extração em apêndice |
| Confirmabilidade | divergências com tabelas publicadas apresentadas com o cálculo que as gera, sem atribuir intenção ou erro aos autores |

## Limitations (By Design)

- **Desenho descritivo.** O artigo não identifica causas. Os padrões entre mandatos (ex.: heterogeneidade × proporcionalidade) são hipóteses para estudos futuros. *Mitigação:* linguagem descritiva e n explícito.
- **Ministérios sem peso.** Todas as pastas contam igual. *Mitigação:* declarar a limitação e citar a literatura que pondera por importância, se a revisão a encontrar.
- **Dependência de uma fonte.** Até 2024, a série vem de uma única codificação (Almeida). *Mitigação:* R1 confere os números, mas não a codificação; declarar isso.
- **Codificação recente não revisada externamente.** Lula 3-5 a 3-9 e os eventos C são classificação própria. *Mitigação:* segundo codificador e versão alternativa.
- **Viés de publicação e idioma na revisão.** *Mitigação:* incluir notas técnicas, textos para discussão e produção em inglês sobre o Brasil.
- **Sensibilidade aos ministros sem partido.** Collor, Bolsonaro e Lula 3 em 2026 mudam muito de posição conforme a medida. *Mitigação:* R3 e discussão explícita.

## Ethical Considerations

- Só dados públicos e literatura publicada. Não há participantes humanos nem dados pessoais sensíveis; os nomes de ministros são informação pública sobre agentes no exercício de cargo.
- **Divergências com tabelas publicadas:** relatar de forma verificável e respeitosa. Se possível, consultar os autores antes da submissão (Bertholini & Pereira; Almeida).
- Respeitar as licenças das fontes (Ipea, Câmara) e citar as bases.

### Human-Subjects Administrative Status
- Não se aplica: o desenho não envolve pessoas como participantes nem coleta de dados pessoais.
- Review pathway: institutional determination required (somente se o autor ou a instituição entenderem de outra forma)

> **Human-subjects boundary:** This output does not authorize recruitment, consent, access to identifiable data, intervention, or data collection.

## Reporting Standard
- **Revisão:** PRISMA 2020 adaptado a revisão integrativa. Usar o fluxograma de identificação e triagem e o checklist como guia de transparência, sem alegar revisão sistemática completa.
- **Replicação:** sem guia EQUATOR específico. Seguir as boas práticas de transparência de dados e código (disponibilidade de dados e código, versão das fontes).

## Preregistration
- Recomendado: **sim**, para o protocolo de busca e os critérios de replicação (R1–R3), antes da busca final.
- Plataforma: OSF Registries.
- Status: planejado.
- Completed artifact declaration: not_provided
- Companion handle: none
- Sidecar ownership: dispatching layer only; do not populate a digest here

## Decisões que cabem ao autor antes do congelamento do desenho

1. **Ênfase:** o artigo é principalmente uma *revisão* com replicação de apoio ou uma *replicação e atualização* com revisão de apoio? Isso muda o tamanho de cada seção e a revista adequada.
2. **Revista-alvo** e os seus limites declarados (palavras, resumo, tipo de artigo). Não serão inferidos pelo nome.
3. **Bases, idiomas e tipos de documento** da busca (tabela A).
4. **Segundo revisor ou codificador:** haverá coautor para a triagem dupla e a recodificação de Lula 3?
5. **Medida principal:** manter a Prop_v1 do Ipea como principal, com Prop_v2 e coalescência como robustez (situação atual)?

## Próximo passo (devolvido ao orquestrador)

Depois que o autor responder às decisões acima e congelar este desenho:
- **Fase 2:** montar o protocolo de busca e a bibliografia (agente de bibliografia do `deep-research`).
- **Tarefa de dados:** gerar a Tabela 1 com as sete colunas a partir de um script.
- Voltar ao modo `plan` do `academic-paper` para a negociação capítulo a capítulo.

Este agente não executa essas etapas.
