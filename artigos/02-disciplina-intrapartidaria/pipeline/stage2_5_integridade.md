# Stage 2.5 — Relatório de verificação de integridade (pré-revisão)

**Papel:** `integrity_verification_agent` (ARS), Modo 1 (verificação inicial).
**Objeto:** Artigo 2, *Disciplina à liderança, unidade partidária e dissidência estruturada na Câmara dos Deputados (57ª Legislatura, 2023–2026)*. Arquivos: `artigo.md`, `artigo_fonte.md`, `analise.py`, `resultados.json`, `tabelas/*.md`, `figuras/*.png`, `referencias.bib`, `pipeline/stage1_blueprint.md` e `pipeline/stage1_bibliografia.md`.
**Data:** 13/11/2026. **Flags opcionais:** cross-model, claim audit e passport não setadas. Por isso não houve C3/C4 com passport, registro `claim-registry/1.0` nem linhas de evidência #656. O E1.1 ficou como `not_run`, e a cobertura semântica é `not_machine_detectable`.
**Nenhum arquivo do artigo foi editado.** A reexecução foi feita numa cópia em `scratchpad/`, com links simbólicos para `dados/` e `embeddings_deputados.py` e o mesmo cache de IRT.

---

## Veredito: **FAIL**

Não há referência inventada nem número inventado. Todo número marcado se reproduz byte a byte a partir do código. Mesmo assim, o manuscrito tem **0 problemas P0, 8 P1 e 24 P2**. Os P1 são estes:

- uma afirmação factual falsa sobre o excesso de lealdade no PSOL;
- um grupo placebo cujos coeficientes em U não são identificados, apresentado com uma explicação falsa;
- três afirmações que vão além do que o desenho sustenta: ausência de pré-tendência, a troca como "correção" e a "congruência de preferências" no contrafactual;
- divergências entre o Método e o código;
- a ausência de declaração dos desvios em relação ao blueprint, junto com a afirmação de que o desenho foi registrado antes da execução;
- um marcador "[verificar páginas]" que ficou visível nas referências.

O checklist de modos de falha deu SUSPECTED nos modos 1 e 6, e os dois bloqueiam o pipeline. O modo 4 também deu SUSPECTED, mas só como sinalização.

| Categoria | Total | OK | Problemas |
|---|---|---|---|
| Existência das referências (A1) | 24 na lista do texto; 27 no .bib | 24/24 existem. São 23 com trilha de busca no Stage 1, mais `cameron2011`, verificada agora | 0 NOT_FOUND / 0 MISMATCH |
| Precisão bibliográfica (A2) | 24 | 23 | 1: Nicolau (2000) sem páginas e com "[verificar páginas]" no texto |
| Citações fantasma (A3) | 23 obras citadas × 24 na lista × 27 no .bib | — | 1 órfã na lista (Cameron et al., 2011). 3 órfãs só no .bib (hix2007, cox1993, freitas2016). 0 citações sem entrada |
| Contexto das citações (B1) | 23 de 23 obras (100%) | 20 | 1 MINOR_DISTORTION e 2 contextos não confirmados pelo resumo verificado |
| Números marcados (C1/C2) | 300 marcadores (263 chaves) | 300/300 | 0. A reexecução gerou `artigo.md` idêntico, salvo o tempo de execução, as 11 tabelas idênticas e 1.425 de 1.426 chaves idênticas (só `tempo_execucao_s` muda) |
| Números escritos à mão | 34 conferidos | 26 | 8 (seção 2.2) |
| Texto × tabelas (amostra) | 52 valores conferidos | 50 | 2 |
| Afirmações (E, alto impacto) | 41 afirmações de Resumo, Abstract, Resultados e Discussão | 27 sustentadas | 3 falsas ou não sustentadas e 11 exageradas ou imprecisas |
| Código × Método | 19 elementos | 13 | 6 divergências |
| Modos de falha de IA | 7 | 4 CLEAR | 1 e 6 SUSPECTED (bloqueiam); 4 SUSPECTED (só sinalização) |

---

## 1. Referências (Fases A e B)

### 1.1 Correspondência entre texto, lista e .bib

- **Obras citadas no corpo:** 23. São elas Ames 2001; Bafumi et al. 2005; Black 1948; Carey 2007 e 2009; Carrubba, Gabel e Hug 2008; Clinton, Jackman e Rivers 2004; Cox e McCubbins 2005; Desposato 2005; Figueiredo e Limongi 1999; Kam 2009; Krehbiel 1993 e 1998; Lauderdale 2010; Mainwaring 1999; McCarty, Poole e Rosenthal 2001; Nicolau 2000; Poole e Rosenthal 1997; Power e Zucco 2009; Rice 1925; Snyder e Groseclose 2000; Zucco 2009; Zucco e Lauderdale 2011.
- **Lista de referências do artigo:** 24 entradas, que são as 23 acima mais Cameron, Gelbach e Miller 2011.
- **Órfã na lista:** Cameron et al. (2011) não é citada em lugar nenhum do texto. A seção 4.4 descreve EP em duas vias, V = V_dep + V_vot − V_dep∩vot, sem citar a obra. → P2-1.
- **Órfãs só no .bib:** `hix2007`, `cox1993` e `freitas2016`. Não aparecem no texto nem na lista. → P2-1.
- **Citações sem entrada na lista:** nenhuma.
- **Lista × .bib:** os 24 itens da lista conferem com o .bib em autores, ano, título, periódico, volume, número e páginas.

### 1.2 Lista × `stage1_bibliografia.md`

- 23 das 24 entradas da lista estão na tabela do Stage 1 com status "verificado", e os detalhes conferem.
- **`cameron2011` não está no Stage 1.** O .bib a registra como "acrescentada na redação". Verifiquei agora por WebSearch, com a consulta "Cameron Gelbach Miller 2011 Robust Inference with Multiway Clustering JBES 29 2 238-249". Os primeiros resultados foram o registro do EconPapers/RePEc `RePEc:taf:jnlbes:v:29:y:2011:i:2:p:238-249` e o registro do catálogo da UTB. Ficaram confirmados os três autores, *JBES* 29(2): 238–249, 2011, e o DOI 10.1198/jbes.2010.07136. Veredito: **VERIFIED**. Falta o DOI no .bib → P2-1.
- **Nicolau (2000):** existe. Busquei "Nicolau 2000 Disciplina partidária e base parlamentar ... Dados 43 4 páginas" e encontrei o registro do DOAJ, o dados.iesp.uerj.br e o OAI do SciELO `S0011-52582000000400004`. As páginas continuam sem confirmação: o DOAJ traz "00–00". A lista de referências do manuscrito tem o texto literal "[verificar páginas]". → **P1-8**. É o padrão IH (incompleto), não uma fabricação.
- `carey2007`, `krehbiel1993` e `snyder2000` estão sem DOI e marcados [verificar] no .bib. Isso não afeta a lista do artigo, que não traz DOIs. Fica como observação.
- **Limite de cobertura:** para as 23 entradas que já tinham passado pelo Stage 1, uso a trilha de busca registrada lá (fonte por entrada na tabela do Stage 1). Só refiz a busca para `cameron2011` e `nicolau2000`. A rede da sessão de Stage 1 bloqueou doi.org e Crossref. Recomendo checar os DOIs no Crossref antes da submissão, como o próprio Stage 1 já indica.

### 1.3 Contexto das citações (B1): 23 de 23 obras

Todas as afirmações atribuídas a obras foram comparadas aos resumos verificados do Stage 1. Nenhuma contradiz o resumo. Os pontos a corrigir são estes:

| Local | Afirmação | Situação |
|---|---|---|
| §1, 2º parágrafo de contribuições | "Modelos de pontos ideais com efeitos fixos partido×votação já foram usados ... (Snyder e Groseclose, 2000; McCarty, Poole e Rosenthal, 2001; Zucco e Lauderdale, 2011)" | **MINOR_DISTORTION** (P2-2). Snyder e Groseclose usam regressão nas votações não lopsided; McCarty et al. usam linhas de corte por partido. Nenhum dos dois usa "efeito fixo partido×votação". Sugestão: "modelos que separam preferência e pressão partidária". |
| §2.1 | Figueiredo e Limongi: "a centralização dos trabalhos nos líderes e os poderes de agenda do Executivo produzem disciplina alta ... a orientação do líder é o melhor preditor do voto" | O Stage 1 registra que o mecanismo "é a leitura usual, mas deve ser conferido no texto". Contexto **não confirmado** (nota). |
| §2.1 e §4.1 | Carey "distingue unidade de disciplina" e propõe ponderar pela disputa com w = 1 − \|2q − 1\| | Não está no resumo verificado. Contexto **não confirmado** (nota). Conferir a fórmula exata do *weighted Rice* em Carey (2007). |
| §8 | "A autoridade dos líderes, no sentido de Krehbiel, existe" | Ambíguo. Krehbiel (1993) é o cético da influência partidária. Sugestão: "a influência partidária, no sentido definido por Krehbiel (1993), existe". (P2-2) |

---

## 2. Números (Fase C)

### 2.1 Números gerados (marcadores)

- `artigo_fonte.md` tem 300 marcadores `{{fmt:chave}}`, com 263 chaves distintas, além de 11 tabelas.
- **Reexecução independente:** `analise.py` rodou na cópia em 92 s, saída 0. `artigo.md` ficou idêntico ao do repositório, com a única diferença no tempo de execução do Apêndice (87 s contra 92 s). As 11 `tabelas/*.md` também ficaram idênticas. Das 1.426 chaves de `resultados.json`, 1.425 são iguais; muda só `tempo_execucao_s`.
- Com isso, **100% dos valores renderizados batem com `resultados.json`**. A ressalva é que a reexecução usa o cache de IRT (`dados_aux/cache`, criado entre 11:15 e 11:29). Pelo `git diff` de 26ad291 até HEAD, as mudanças posteriores no código não tocaram as funções de ajuste. Por isso o cache é consistente com o código atual, mas o ajuste do zero não foi reexecutado.
- **Amostra texto × tabela (52 valores):**
  - Tabela 2: D dos 16 partidos, Rice e "% racha" de União, PSDB, MDB, PP, PT e PSOL.
  - Tabela 3: 9 valores.
  - Tabela 4: os 4 temas citados.
  - Tabela 6: os 9 partidos citados.
  - Tabela 7: 11 nomes e partidos.
  - Tabela 8: partidos dos pivôs.
  - Tabela 9: 5 variações e ρ.
  - Tabela 10: 4 coeficientes.

  Batem 50 de 52. As exceções são a lista de partidos dos pivôs na Discussão (P2-12) e o "excesso maior no PSOL" (P1-1).

### 2.2 Números escritos à mão em `artigo_fonte.md` (34 conferidos)

| Local | Texto | Conferência | Veredito |
|---|---|---|---|
| Resumo | "1º semestre de 2025" | Semestre 2025S1: D 97,8%, cobertura 3,7%, U 87,4% (o menor) | OK |
| Resumo/Abstract | "5 dobras", "100 votações" | K = 5; top 100 | OK, mas as 100 são tiradas só das votações com orientação do Governo (P2-6) |
| §2.2 E1 | "em torno de 90%" | D = 90,9% | OK |
| §3 | "coletados até 11/11/2026" | Não rastreável no código; o blueprint fala em 13/11/2026 | Nota |
| §3 | "a no máximo cinco de 513" | `presenca_share_datas_513_mais_menos_5` | OK. O cálculo é por votação, não por data (P2) |
| §3 | "março–abril de 2026" | `n_transicoes_janela2026` usa 1/3 a 1/5 | OK, mas a §5.5 usa "março–maio", com janela de 1/3 a 1/6 (P2-9) |
| §4.1 | "≥ 10%", "≥ 20%", "m = 10", "m = 5", "três votantes", "cinco colegas", "2,5%" | Constantes do código | OK |
| §4.3 | "cinco dobras", "cerca de 20%", "passa de 88%" | K = 5; taxa-base de seguir a maioria 88,8% | OK |
| §4.3 e §4.5 | "1.000 réplicas" (duas vezes) | `B = 1000`, `N_BOOT = 1000` | OK |
| §4.4 | "26 g.l." | `reg_*_uf_gl = 26` | OK |
| §4.4 | janelas de evento | Iguais às do código | OK |
| §5.1 | "entre 88% e 90%" (PP, PSD, MDB, PODE, AVANTE) | 88,3; 89,5; 89,0; 88,3; 88,6 | OK |
| §5.1 | "cerca de 98% em PT, PSOL e NOVO e de 83% a 92% no centrão" | **Não rastreável** a nenhum arquivo do repositório. Vem do "enunciado" segundo `NOTAS_PASSAGEM.md` | P2-10 |
| §5.1 | "menos de 2%" | `share_propria`: máximo de 1,16% (União) entre os 7 partidos | OK |
| §5.1 | "cerca de um ponto percentual" (variação real em U) | U anual vai de 88,7 a 90,3 (**1,6 p.p.**); por semestre, de 87,4 (2025S1) a 92,5 (2026S2), ou **5,0 p.p.** | **Subestimado** (P2-11) |
| §5.2 | "quatro em cada cinco" | U liberado = 79,5% | OK |
| §5.2 | "308 votos Sim" | Quórum constitucional | OK |
| §5.3 | "menos de 75%", "cerca de 1%" (PT e PSOL) | Rice < 0,5; 0,9% e 1,1% | OK |
| §5.4 | "50 ou mais votantes", "menos de cinco" | Faixas por `n_tr`, número de votantes **no treino** | OK. Descrever como "no treino" (P2) |
| §5.4 | λ_d de 1, 4 e 16; λ_g = 1 | Iguais ao código | OK |
| §5.6 | "5%", "mais de um desvio-padrão", "100 votos" | Iguais ao código | OK |
| §5.6 | "cinco deputados" mais próximos da mediana | `nsmallest(5)` | OK |
| §5.7 | "antes de abril de 2023" (datas das fusões de PSC e PATRIOTA) | **Falso nos dados**: PSC→PODE a partir de 22/08/2023; PATRIOTA→PRD a partir de 07/02/2024 | **P1-2** |
| §6 | "oito decisões de medida" | A Tabela 9 tem a principal mais 7 variantes | P2 (dizer "sete variantes") |
| §6 | "menos de meio ponto" | Máximo de 0,33 p.p. (estrita) | OK |
| §7 | "±10 dias" | Igual ao código | OK |
| §9 | "nove de cada dez" | 90,9% | OK |
| Apêndice A | "da ordem de 15 minutos em 4 núcleos" | A docstring de `analise.py` diz "~40–60 min" | P2-19 |
| Legendas das figuras | "≥ 100 votos", "40% e 60%", "−12 a −7", "IC 95%" | Iguais ao código | OK |

### 2.3 Consistência interna (C2)

- **Duas cifras para o bloco inferido.** O texto dá "bloco inferido 11,2% dos votos do Plenário" na §1 e "cerca de 18% de todos os votos" na §3. Os denominadores diferem (camada no Plenário contra fonte bruta em Plenário e comissões), e o megabloco inferido foi reclassificado como heterogêneo. O texto não explica a diferença. (P2-9)
- **Denominadores misturados no excesso de lealdade.** O Resumo e o Abstract juntam "89,4% seguem o partido" (n = 18.116, com abstenções) a "3,9 pontos acima do previsto". O excesso é calculado em n = 18.066, sem abstenções, onde o observado é 89,6% e o previsto 85,8%. (P2-9)
- **Formato numérico do Abstract.** O Abstract em inglês usa o formato brasileiro: "454.829", "90,9%", "14/03/2023". (P2-3)

---

## 3. Afirmações (Fase E; 41 de alto impacto verificadas)

### 3.1 Pontos de atenção pedidos

**Alta de 2025 como "artefato".** Os números sustentam a direção da afirmação:
- D 2025 = 92,9% com cobertura de 32,1%;
- em 2025S1, D = 97,8% com cobertura de 3,7%;
- U em 2025 é o menor valor anual (88,7%);
- sem fevereiro a outubro de 2025, D muda só 0,3 p.p.

O que falta é mostrar o mecanismo. Parte da alta pode vir da **composição**: em 2025 o D cobre sobretudo partidos de orientação própria (PSOL, NOVO, PT fora do megabloco). O texto afirma "é um artefato" na §1 e na §5.1. Sugiro "é compatível com um artefato de cobertura e composição" e reportar o D de 2025 ajustado por partido. (P2-11)

**"E3 se sustenta".** M2→M3 = 0,0117, IC 0,0083–0,0147. A conclusão se mantém, mas o teste descrito não é o que o texto diz:
- M3 não contém M2, porque não tem o ρ_i de lealdade. A frase "saber para que lado ... acrescenta informação **além** de saber quanto ele desvia" (§5.4) não é testada pela diferença M2→M3.
- Fiz o teste correto por conta própria, ajustando M3 + ρ_i nas mesmas dobras e com o mesmo procedimento. Resultado: M2 − (M3+ρ) = **0,0151 [0,0124; 0,0180]** e M3 − (M3+ρ) = 0,0034 [0,0025; 0,0044]. A direção, portanto, acrescenta além da lealdade e a afirmação vale.
- A descrição "seis modelos **aninhados**" está errada: M2 não está aninhado em M3, nem M5 em M4. → P1-6, com o teste acima como correção.

**Dimensão intrapartidária como governismo relativo.** Sustentada:
- correlação entre cargas e orientação do Governo de 0,90;
- correlação de 0,92 com o governismo relativo ao partido;
- correlação de 0,94 com a posição relativa global.

O "100%" é um valor redondo e por isso suspeito. Conferi o código: o sinal do eixo é fixado pela correlação com a taxa de voto com o Governo, e as cargas são então comparadas à orientação do Governo. Isso não é circular no conteúdo, porque o eixo é estimado sem supervisão. Mas a amostra é "as 100 de maior carga **entre as 77% de votações com orientação do Governo**", e não "as 100 votações mais carregadas". (P2-6)

Na §5.5, "a dimensão carrega informação ... mas não muito além do que a posição global relativa já contém" está otimista: o acerto intrapartidário (61,8%) é **menor** que o global (64,6%). (P2-7)

**Estudo de evento: pré-tendência.**
- O texto e o Resumo/Abstract dizem "sem pré-tendência" e "não há sinal de saída anunciada". Mas o coeficiente de **≤ −13 meses**, também uma defasagem pré-evento, é **−1,7 p.p. [−3,5; +0,1]** e não é reportado.
- O coeficiente de −3 a −1 é +1,4 [−1,4; +4,2]. As estimativas pontuais crescem cerca de 3 p.p. até a troca, e o desvio bruto dos trocadores sobe de 16,4% (≤ −13) a 20,6% (referência) e 23,7% (−3 a −1).
- Coeficientes não significativos não equivalem a ausência de efeito, como alerta o próprio blueprint. → **P1-3**.

**Estudo de evento: placebo.**
- Em U, os 5 deputados do grupo de fusão **não têm nenhuma observação antes da fusão**, porque as bancadas de PSC e PATRIOTA não reúnem 5 colegas. Os dois indicadores pós-fusão somam exatamente o efeito fixo de deputado, ou seja, são colineares. `ols_fe` usa `pinv` e devolve uma solução de norma mínima: +0,24 e −0,24 p.p., com ICs espelhados (−2,95; 3,43 e −3,43; 2,95).
- Os coeficientes **não são identificados**, e o texto os descreve como "próximos de zero, mas com intervalos largos".
- A justificativa dada, de que as fusões ocorreram antes de abril de 2023, é falsa nos dados (§2.2).
- Em D, onde há pré-período para 9 deputados, o placebo mostra **aumento** do desvio de +13,4 p.p. [1,9; 25,0] e +13,1 p.p. [3,1; 23,2] depois da fusão, e isso não é relatado. → **P1-2**.

**Estudo de evento: interpretação.** "A troca é sobretudo uma correção da filiação à preferência, não uma mudança de comportamento induzida pelo novo partido" (§5.7) e "A troca reduz o desvio, como correção da filiação" (§9). O desfecho é o desvio em relação aos colegas atuais, e os dois mecanismos (seleção e influência do novo partido) preveem a mesma queda. O desenho não separa os dois. → **P1-4**.

**Excesso de lealdade.**
- "O excesso é maior no PSOL (98,6% contra 86,6%)" é **falso**. O PSOL tem +12,1 p.p., abaixo de **PSB (+17,8; 52,6 contra 34,8)** e **PDT (+12,8; 53,5 contra 40,8)**. → **P1-1**.
- "A maior parte da lealdade nas divergências é congruência de preferências" (§5.8) tem um problema no contrafactual M5. Os pontos x_i e os parâmetros a_j e b_j são estimados com votos já moldados pela disciplina, incluindo 80% dos votos **da mesma votação divergente**. A probabilidade "prevista pelas preferências" absorve, portanto, parte do efeito do partido, e o excesso de 3,9 p.p. é um **limite inferior**.
- O blueprint (§8.2) pedia um IRT sem as votações divergentes, e essa mudança não foi declarada. A Limitação da §7 menciona o problema só de passagem.
- → **P1-5**. A correção é reescrever como "limite inferior" e moderar o Resumo/Abstract ("spatial preferences predict").

**Decomposição de variância.** Os números estão corretos: ruído de 0,8% (U) e 1,2% (D); dentro dos partidos, 80% e 81%. Há duas ressalvas:
- O "sinal" das taxas brutas inclui diferenças de agenda entre deputados (quais votações cada um votou), justamente a crítica (a) do blueprint.
- Entre os commits 26ad291 e d4676ed, o cálculo mudou da versão ajustada por célula, que é a do blueprint, para taxas brutas, sem declaração.

Reexecutei a versão ajustada: o ruído fica em 1,0% (U) e 1,5% (D), e a parte entre partidos cai a cerca de 0, como esperado por construção. A conclusão sobre o ruído é robusta. A cifra de "80% dentro dos partidos" depende da escolha. (P2-13)

**Pivôs.** Na §5.6, "sempre em partidos do centro — REPUBLICANOS, PSD, PP, MDB, PODE, União, PSDB ou SOLIDARIEDADE" confere com a Tabela 8. Na §8, a frase "o mediano e os pivôs de 3/5 estão **sempre nesses partidos**" se refere a União, PP, PSD, MDB e REPUBLICANOS, e é **falsa**: há pivôs do PODE (Igor Timo), do PSDB (Paulo Alexandre Barbosa) e do SOLIDARIEDADE (Aureo Ribeiro). (P2-12)

Há ainda uma inconsistência no bootstrap. José Rocha é o 1º mais próximo da mediana na estimativa pontual, mas não aparece entre os 8 mais frequentes nas réplicas. As réplicas também dão DPs acima da estimativa pontual (PT: 0,23 [0,23; 0,33]). Isso indica viés de reamostragem. O critério "IC exclui a mediana" classifica 383 de 595 períodos (64%) como dissidentes, o que sugere ICs estreitos demais para esse uso. (P2-14)

**Resumo × Abstract.** Dizem a mesma coisa, frase a frase: medida, megabloco, D e U, partidos extremos, validação cruzada, governismo relativo, 62%, correlatos, 11,1 p.p., 89,4% e 3,9 p.p. As divergências são três:
- o formato dos números no Abstract (P2-3);
- "desvio" e "defection" sem dizer que é o desvio de U (P2);
- os dois herdam os exageros de P1-3 ("sem pré-tendência") e P1-5 ("preferências preveem").

### 3.2 Outras afirmações

| # | Afirmação (local) | Veredito |
|---|---|---|
| a | "A correção de Desposato muda pouco os valores e nada o ordenamento" (§5.3) | A evidência citada é ρ(m = 10, m = 5) = 1,00, que compara duas versões corrigidas. Falta o ρ entre o Rice bruto e o padronizado, e os partidos pequenos (PCdoB, PV, AVANTE, NOVO) ficam fora de m = 10. Pela Tabela 2, a ordem bruta e a de m = 10 coincidem entre os 12 partidos. A conclusão provavelmente vale, mas a evidência está mal escolhida. (P2-4) |
| b | "62% das trocas de partido na janela de 2026" (Resumo/Abstract) | São 61,8% de **110** trocas: as de origem igual ao partido de 2025, com \|Δ\| > 0,05. Houve 129 trocadores na amostra de previsão. (P2-7) |
| c | "A disciplina não é só preferência" (§5.6) | É inferida dos efeitos de UF e de troca, que também podem ser preferência. Exagerado. (P2-15) |
| d | P5: só a suplência de ministro é discutida (§5.8) | Não são relatados os coeficientes significativos de "suplente (outro motivo)" (+16,1 p.p. [9,8; 22,4]), mulher (+4,7 [0,6; 8,8]) e log de cadeiras da UF (−2,4 [−4,2; −0,6]). É relato seletivo. (P2-16) |
| e | "M0→M1: a posição do partido contém muito mais do que a orientação registrada" (§5.4) | O M0 é calibrado por uma constante única, a taxa de acerto, e o M1 usa os votos dos colegas na mesma votação. Parte do ganho de 0,16 vem da calibração rudimentar do M0. Sugiro calibrar o M0 por camada e partido. (P2-17) |
| f | Polo negativo da Tabela 11: "requerimentos procedimentais **rejeitados**"; polo positivo: "destaques de projetos **do Executivo**" | O resultado da votação e a autoria não estão na Tabela 11 nem no código. Não verificável. (P2-18) |
| g | Frentes: as correlações na 2ª dimensão (0,11 e −0,13) são chamadas de "fracas", e as da 1ª (−0,13 a −0,23), de substantivas | Enquadramento assimétrico para magnitudes parecidas. (P2-15) |
| h | Discussão: "deputados se ordenam de forma **estável**" | A estabilidade não foi testada; os pontos são estáticos por período. (P2-15) |
| i | Rice, E2, U por liberação (16 de 16 partidos), Obstrução, PEC (94,9 → 83,8), temas, P5 por camada, PSB e PDT inferidos, robustez, regressão do desvio, AUC 0,595, validação cruzada (todas as diferenças com IC acima de 0), M5→M4 com a ressalva sobre g | **Sustentadas** pelos números. |

---

## 4. Código × Método

Elementos conferidos (19):
- D, U, camadas, direcional e estrita;
- Rice e Desposato hipergeométrico, linha de base, disputa, ponderação;
- IRT global e intra, filtro de 2,5%;
- M0, M1, M2, M3, M4 e M5;
- dobras;
- células com divisão interna;
- faixas e sensibilidade;
- bootstrap de deputados;
- regressão MPL com EF e EP em duas vias;
- Wald de UF;
- distância medida no outro biênio;
- estudo de evento;
- contrafactual M5;
- bootstrap global com Procrustes;
- pivôs.

**Correto (13):**
- D, sem o bloco heterogêneo e com Abstenção contada como desvio.
- U, deixando o próprio deputado de fora, com pelo menos 5 colegas e sem empates.
- Rice com m = 10 e m = 5 e mediana menor que m sem valor.
- **Sem vazamento na validação cruzada:**
  - a maioria da célula, `n_tr` e `min_tr` usam só o treino (`stats_celula(A, tr)`);
  - o M0 usa a orientação, que é exógena, e as maiorias e a calibração do treino;
  - o M2 usa como *offset* o M1 da mesma dobra, e a direção d_pj vem do treino;
  - as células sem treino ficam com g = 0;
  - "células com divisão interna" são definidas só com o treino.
- Sinal e rotação: o x intrapartidário é centrado no partido, de modo que a correlação com a taxa bruta de voto com o Governo é efetivamente a correlação dentro do partido. A correlação de 0,92 com o governismo relativo confirma o sinal.
- Os dois `merge_asof` estão ordenados por `dt`, com chave inteira e direção backward, como deve ser.
- EP em duas vias: a fórmula CGM está implementada e a interseção equivale a HC0.
- Wald com 26 g.l.
- Distância medida no outro biênio.
- Contrafactual com as previsões fora da amostra do M5: cada observação está em exatamente uma dobra.

**Divergências (6, reunidas em P1-6):**

1. **Estudo de evento.** O Método diz "Para os deputados com troca individual, estimamos". O código estima com **todos os deputados**: os que não trocaram entram como controle, e fusões e trocas individuais ficam na mesma regressão. Também não está dito que se usa só a 1ª troca individual (13 deputados têm mais de uma).
2. **Temas.** O Método (§4.1) diz que tipo, proposição e **tema** são comparados "em médias brutas e ajustadas por partido×ano". Para tema, `disciplina_temas` só calcula médias brutas. Também não está dito que só a 1ª proposição de cada votação é usada.
3. **Seis modelos "aninhados".** M2 e M3, assim como M5 e M4, não estão aninhados. O Método também diz "ρ_i > 0", mas no código ρ_i não tem restrição de sinal.
4. **Grupo placebo.** É descrito como teste, mas em U não é identificado. Além disso, `ols_fe` usa `pinv` sem alertar para colinearidade, um problema geral (ver o modo 1).
5. **Apêndice.** Diz que o desenho foi "registrado antes da execução". O blueprint foi gravado (6802984, 11:01) **depois** da parte descritiva (079773c, 01:35), como ele próprio declara ("exposição parcial aos dados"). A decisão do blueprint foi `revise_before_freeze`, e não há versão congelada (ver a seção 6).
6. **Tempo de execução.** O Apêndice diz cerca de 15 min; a docstring diz 40–60 min.

**Riscos menores de código (P2-19):**
- O cache `em_cache(nome)` não depende dos dados nem dos hiperparâmetros. Se o filtro ou os dados mudarem e as dimensões continuarem iguais, o cache velho é reaproveitado sem aviso.
- O filtro de minoria ≥ 2,5% usa todas as observações, inclusive as de teste. É um vazamento leve de seleção de votações, igual para todos os modelos.
- Na sensibilidade de ausência em PEC, o presidente da sessão ("Artigo 17", excluído) conta como ausente do próprio partido.
- `presenca_share_datas` é calculado por votação, não por data.

---

## 5. Checklist dos 7 modos de falha de IA (ai_research_failure_modes.md)

| Modo | Resultado | Evidência |
|---|---|---|
| 1. Bug de implementação que passa pela autorrevisão | **SUSPECTED** (bloqueia) | Os coeficientes do placebo em U são colineares com o efeito fixo de deputado. `pinv` produz ±0,0024 com ICs espelhados (valores redondos e simétricos, um sinal clássico), e o texto os interpreta. `ols_fe` não verifica o posto da matriz. O cache não depende dos dados nem dos hiperparâmetros. Não encontrei bugs que mudem os resultados principais (validação cruzada sem vazamento, sinais e merges corretos). |
| 2. Citação alucinada | **CLEAR** | As 24 referências da lista existem: 23 pela trilha do Stage 1 e Cameron (2011) verificada agora. Não há MISMATCH. Restam a falta de páginas no Nicolau (IH), as órfãs e uma MINOR_DISTORTION de contexto. |
| 3. Resultado experimental alucinado | **CLEAR** | A reexecução reproduz `artigo.md`, as tabelas e `resultados.json`. Todo número marcado vem do código. As exceções são números escritos à mão e não rastreáveis ("cerca de 98%", "83% a 92%", nomes de dissidentes e pivôs "apontados antes no projeto"), que vêm do enunciado e não de um arquivo (P2-10). O ajuste de IRT do zero não foi refeito; a reexecução usou o cache. |
| 4. Dependência de atalho | **SUSPECTED** (só sinalização) | (i) O ganho M0→M1 em parte vem da calibração constante do M0 e do uso, pelo M1, dos votos dos colegas na mesma votação. (ii) O "excesso de lealdade" usa um contrafactual (M5) cujas preferências já embutem a disciplina. (iii) Os ICs do bootstrap global ficam acima da estimativa pontual. Preparar ablações antes do Stage 3: M0 calibrado e M5 sem as votações divergentes. |
| 5. Bug reapresentado como achado | **CLEAR** (com nota) | O texto não usa "surpreendentemente" nem "inesperadamente". O "100%" das cargas é coerente com a correlação de 0,90 e com o governismo relativo de 0,92. A única leitura de artefato numérico como resultado é o placebo em U, tratado no modo 1 e em P1-2. Não é um "achado novo". |
| 6. Fabricação de metodologia | **SUSPECTED** (bloqueia) | O Método descreve coisas que o código não faz: estimação só com trocadores, médias ajustadas por tema, modelos "aninhados", ρ_i > 0, o placebo como teste e o registro "antes da execução". Ver P1-6 e P1-7. |
| 7. Frame-lock | **CLEAR** | O blueprint revisou a fundo o rascunho v0 (camadas, U, M1/M2, efeitos fixos). O artigo adota a revisão e reporta resultados que qualificam a tese, como o ganho pequeno e o excesso pequeno. Não há sinais de "em retrospecto". |

**Bloqueio:** os modos 1 e 6 estão SUSPECTED. O usuário precisa confirmar e corrigir, ou registrar uma justificativa (override), antes do Stage 3.

---

## 6. Desvios em relação ao blueprint (`stage1_blueprint.md`)

O artigo **não tem seção de desvios do plano**. A única declaração é a frase do Apêndice, que é imprecisa. → **P1-7**

| # | Blueprint | Artigo/código | Declarado? |
|---|---|---|---|
| 1 | D-própria como medida principal para inferência sobre partidos | D com as três camadas (própria, bloco, inferido) como principal; D-própria entra como recorte e robustez | Não |
| 2 | Bloco heterogêneo definido pela amplitude das medianas dos membros > 2 DP | Regra pelo nome (contém "Pl" e "FdrPT") | Não |
| 3 | Validação manual do classificador (200 descrições) | Cortada | Sim (§7) |
| 4 | Diagnóstico de ausência seletiva; ausência em PEC **e PLP** | Só PEC; sem diagnóstico | Em parte (§7, "não estimamos ausência seletiva") |
| 5 | Recortes em regressão ao nível do voto com EF de partido e ano; tema também só no mérito | Médias com EF partido×ano por *demeaning*; tema só com médias brutas | Não (o Método diz o contrário) |
| 6 | Covariáveis: primeiro mandato, Mesa/liderança, governador; logit condicional ou misto como robustez | Omitidas ou cortadas | Não |
| 7 | Decomposição da variância do desvio ajustado | Taxas brutas, mudança feita depois do primeiro cálculo | Não |
| 8 | Estudo de evento: versão só com a coorte de 2026 e controles nunca tratados | Cortada; acrescentada a janela ≤ −13 | Não |
| 9 | M2 como logit do desvio, σ(κ_pj + r_i) | Forma com *offset* de M1, σ(z_M1 + ρ_i d_pj) | Não |
| 10 | Subamostra (b): ≥ 1 desvio **ou** minoria ≥ 10%; (c) ≥ 5 colegas, separada | (b) e (c) combinadas por "e"; minoria ≥ 10% não usada | Não |
| 11 | λ_g ∈ {0,1; 1} em M1–M4; λ_d ∈ {1, 4, 16} | Só λ_g = 1 em M1 e M3, só λ_d em M3, só na dobra 0 | Em parte ("na dobra 0") |
| 12 | Log-loss restrita aos votos de desvio | Não reportada | Não |
| 13 | Intra 1D por partido (7 maiores) para testar b_j comum | Cortado | Em parte (§7 cita a premissa de b_j comum) |
| 14 | Cargas: top 20 por lado; composição temática com razão de chances e IC; correlatos de temas de autoria, UF e suplência | Top 8 por lado; `compt` calculado mas não reportado; correlatos cortados | Não |
| 15 | Incerteza das cargas (bootstrap intra ou estabilidade entre dobras) | Ausente | Não |
| 16 | Dissidentes: \|x_intra\| e taxa de desvio ajustada | Só a posição relativa global | Não |
| 17 | "Em que votações os partidos racham" (logit) | Cortado | Não |
| 18 | P5: IRT global **sem** as votações divergentes como contrafactual; correlato "troca futura"; divergência por tipo de votação | Previsões fora da amostra do M5 (mesmas votações); sem troca futura; resultado por tipo calculado e não reportado | Não |
| 19 | Dispersão: robustez com todos os deputados ponderados por votos | Cortada | Não |
| 20 | Tabela de versões dos pacotes | Ausente | Não |
| 21 | Pré-registro: decisão `revise_before_freeze`; registro após exposição parcial | O Apêndice diz "registrado antes da execução"; não há versão congelada | Não (afirmação imprecisa) |

Os itens 3 e 4 seguem a lista de "cortes se o tempo for curto" do blueprint. Os itens 1, 7, 9, 10 e 18 mudam definições de medida ou de teste e têm de ser declarados.

---

## 7. Lista de problemas

### P0 (bloqueantes)

Nenhum.

### P1 (importantes; corrigir antes do Stage 3)

| ID | Local | Problema | Correção sugerida |
|---|---|---|---|
| P1-1 | §5.8, 2º parágrafo | "O excesso é maior no PSOL (98,6% contra 86,6%)" é falso: PSB +17,8 p.p. e PDT +12,8 p.p. superam o PSOL (+12,1). | Reescrever: "O excesso é grande no PSB, no PDT e no PSOL (...); no PSOL, cuja orientação é sempre da própria federação, ...". Ou ordenar os partidos pelo excesso. |
| P1-2 | §5.7, 2º parágrafo; Fig. 5; `estudo_evento`/`ols_fe` | Os coeficientes do placebo em U **não são identificados**: não há observações antes da fusão em U, e `pinv` devolve ±0,24 p.p. com ICs espelhados. A justificativa "as fusões de PSC e PATRIOTA ocorreram antes de abril de 2023" é falsa (as datas são 22/08/2023 e 07/02/2024). O placebo em D (+13 p.p., significativo) não é relatado. | Retirar os coeficientes de U ou declará-los não identificados. Explicar que as bancadas pré-fusão têm menos de 5 colegas. Relatar o placebo em D com a ressalva de n = 9. Fazer `ols_fe` detectar o posto e falhar quando houver colinearidade. |
| P1-3 | Resumo, Abstract, §5.7 | "sem pré-tendência" e "não há sinal de saída anunciada" omitem o coeficiente de ≤ −13 meses (−1,7 [−3,5; 0,1]) e a sequência crescente das estimativas pontuais (cerca de +3 p.p. até a troca). | Relatar todos os coeficientes pré-evento. Escrever "sem pré-tendência estatisticamente distinguível; as estimativas pontuais sugerem um aumento modesto (cerca de 3 p.p.) no ano anterior à troca, pequeno diante da queda de 11 p.p.". |
| P1-4 | §5.7, último período do 1º parágrafo; §9 | "A troca é sobretudo uma correção da filiação à preferência, não uma mudança de comportamento induzida pelo novo partido": o desenho, com desfecho relativo aos colegas atuais, não separa seleção de influência. | Apresentar as duas leituras como compatíveis. Para separar, comparar a posição absoluta (x) antes e depois com o modelo global por período, ou usar o desvio em relação aos colegas do partido de origem. |
| P1-5 | §5.8; Resumo ("preferências espaciais preveem"); Abstract; §8 | O contrafactual M5 usa pontos e cargas estimados com votos já disciplinados, incluindo 80% da mesma votação. "A maior parte da lealdade ... é congruência de preferências" está exagerado: o excesso é um limite inferior. É também um desvio não declarado do blueprint §8.2. | Rotular o excesso como limite inferior. Reestimar o M5 sem as votações divergentes (ou com a preferência medida no outro biênio) como robustez. Moderar o Resumo e o Abstract. |
| P1-6 | §1 ("seis modelos aninhados"); §4.3 (M2 "ρ_i > 0"; "M2→M3 mede ... a direção"); §5.4; §4.4 (estudo de evento "para os deputados com troca individual"); §4.1 (temas "ajustadas") | O Método descreve procedimentos diferentes dos do código (seção 4). | (a) Trocar "aninhados" por "hierarquizados" e acrescentar o modelo M3 + ρ (pela minha reexecução: M2 − (M3+ρ) = 0,0151 [0,0124; 0,0180]) para sustentar o "além de". (b) Escrever ρ_i ∈ ℝ. (c) Descrever a amostra completa e os controles do estudo de evento, e o uso da 1ª troca. (d) Calcular médias ajustadas por tema ou retirar "tema" da frase. |
| P1-7 | Apêndice A; não há seção de desvios | O Apêndice diz "registrado antes da execução", mas o blueprint é posterior aos descritivos e não foi congelado (`revise_before_freeze`). Ao menos 15 desvios materiais não são declarados (seção 6). | Acrescentar uma subseção "Desvios do plano de análise" com a tabela da seção 6. Reescrever: "O plano foi escrito após a análise descritiva preliminar (P1) e antes das análises de P2 a P5; os desvios estão listados em ...". |
| P1-8 | Referências: Nicolau (2000) | O marcador "[verificar páginas]" ficou visível no manuscrito, sem páginas nem DOI. | Abrir o SciELO (PID S0011-52582000000400004) e completar as páginas e o DOI. |

### P2 (menores)

| ID | Local | Problema / correção |
|---|---|---|
| P2-1 | Referências; `referencias.bib` | Cameron et al. (2011) está na lista mas não é citada: citar em §4.4 junto da fórmula de EP em duas vias. Acrescentar o DOI 10.1198/jbes.2010.07136 ao .bib e registrá-la no Stage 1. Remover do .bib ou citar `hix2007`, `cox1993` e `freitas2016`. |
| P2-2 | §1 e §8 | MINOR_DISTORTION na caracterização de Snyder e Groseclose, de McCarty et al. e de Zucco e Lauderdale como modelos "com efeitos fixos partido×votação". Ambiguidade em "autoridade ... no sentido de Krehbiel". Conferir Figueiredo e Limongi (mecanismo) e Carey (unidade × disciplina e fórmula de ponderação) no texto original. |
| P2-3 | Abstract | Formato numérico em inglês: 454,829; 1,126; 90.9%; 11.1; 2023-03-14. Basta um formatador por idioma em `montar_artigo`. |
| P2-4 | §5.3 | Para sustentar "nada o ordenamento", reportar ρ(Rice bruto, Rice com m = 10) e dizer que 4 partidos pequenos ficam fora de m = 10. |
| P2-5 | §5.5 e Resumo | O "100%" refere-se às 100 de maior carga entre as votações com orientação do Governo (77% do total): dizer isso. |
| P2-6 | §5.5 | Mesma qualificação do denominador nas cargas (ver P2-5) e menção à fixação do sinal pelo governismo. |
| P2-7 | §5.5, Resumo, Abstract | "62% das trocas": dizer que são 110 trocas classificáveis, de 129 na janela. "Não muito além" deveria ser "não além (61,8% contra 64,6% no modelo global)". |
| P2-8 | §5.4 | As "células com 50 ou mais votantes" e as de "menos de cinco" contam votantes **no treino**. |
| P2-9 | §1, §3, §5.5; Resumo | Duas janelas de 2026 (março–abril na §3, março–maio na §5.5); bloco inferido com 11,2% e 18% sem explicar os denominadores; 89,4% e o excesso de 3,9 p.p. calculados em amostras diferentes (89,6/85,8). Harmonizar. |
| P2-10 | §5.1, §5.6 | "cerca de 98% ... 83% a 92%" e os nomes de dissidentes e pivôs "apontados antes no projeto" não têm fonte rastreável no repositório. Citar a fonte (painel ou outro artigo do projeto) ou retirar. |
| P2-11 | §5.1, §1, Resumo | "Cerca de um ponto percentual" de variação real deveria ser "1,6 p.p. entre anos e até 5 p.p. entre semestres (U)". "É um artefato" deveria ser "é compatível com um artefato de cobertura e composição", reportando o D de 2025 ajustado por partido. |
| P2-12 | §8 | "O mediano e os pivôs de 3/5 estão sempre nesses partidos" é falso para a lista de 5 partidos. Usar a lista de 8 da §5.6. |
| P2-13 | §4.4, §5.6 | A decomposição usa taxas brutas, cujo "sinal" inclui a agenda, e houve mudança não declarada em relação à versão ajustada. Declarar e informar que o ruído fica em cerca de 1% nas duas versões. |
| P2-14 | §5.6, Tabelas 6 e 7 | Os ICs bootstrap ficam deslocados para cima. O critério "IC exclui a mediana" classifica 64% dos períodos. Usar ICs corrigidos de viés ou um limiar mais exigente para chamar alguém de "dissidente". |
| P2-15 | §5.5, §5.6, §8 | Enunciados exagerados: "a disciplina não é só preferência"; "ordenam de forma estável"; leitura assimétrica das frentes nas duas dimensões. |
| P2-16 | §5.8 | Relatar os coeficientes significativos omitidos: suplente (outro motivo) +16,1 p.p.; mulher +4,7; log de cadeiras da UF −2,4. |
| P2-17 | §5.4 | O ganho M0→M1 está inflado pela calibração constante do M0. Acrescentar um M0 calibrado por camada e partido. |
| P2-18 | §5.5 | "Rejeitados" e "do Executivo" não são verificáveis na Tabela 11: acrescentar as colunas de resultado e autor, ou retirar. |
| P2-19 | Apêndice A; `analise.py` | Tempo de execução de 15 min contra 40–60 min. Cache sem chave de dados e hiperparâmetros. Filtro de 2,5% calculado com dados de teste. Presidente da sessão contado como ausente em PEC. `presenca` por votação, não por data. "Oito decisões" deveria ser sete variantes. |
| P2-20 | Resumo/Abstract | Dizer que a queda de 11,1 p.p. é no desvio de U (da maioria dos colegas). |
| P2-21 | Tabela 2 / Resumo | "Mais baixa em União, PSDB e PP": PP (88,32) e PODE (88,33) estão empatados em D. Em U, o 3º menor é o MDB. Escrever "União e PSDB" ou explicitar a medida. |
| P2-22 | §4.1, U | A fórmula de U não define s(v) para Abstenção, que conta como desvio no código. Acrescentar. |
| P2-23 | §6 | A Tabela 9 não traz cobertura nem n por partido para "só orientação própria", com amostras muito pequenas nos partidos de centro (REPUBLICANOS 100,0%). Acrescentar o n. |
| P2-24 | Figuras | O C3 com `figure_table_trace[]` não pôde ser aplicado, porque não há Figure Package. As legendas das figuras 1, 2, 4, 5, 6 e 7 conferem com o código. A legenda da Fig. 5 herda P1-3. Nota de "trace indisponível". |

---

## 8. O que fazer a seguir

- Corrigir P1-1 a P1-8 no `artigo_fonte.md`. P1-2 também exige mexer em `analise.py`; P1-5 e P1-6, opcionalmente, também.
- Rodar `analise.py` de novo.
- Reverificar os itens corrigidos e refazer o C2 (consistência interna), porque o Resumo e o Abstract mudam.
- Os modos 1 e 6 precisam ser resolvidos ou receber override justificado antes do Stage 3. O modo 4 vai para o Stage 3, com sugestão de ablações (M0 calibrado; M5 sem as votações divergentes).

Fontes da verificação na web: [EconPapers – Cameron, Gelbach e Miller (2011)](https://econpapers.repec.org/RePEc:taf:jnlbes:v:29:y:2011:i:2:p:238-249); [registro da UTB](https://vufind-test.katalog.k.utb.cz/SummonRecord/FETCH-LOGICAL-c446t-6d9ae3b2dfe1cf37623a25a8be7e7017ae67fdbe9e349ddb7ec6564032463d7a3); [DOAJ – Nicolau (2000)](https://doaj.org/article/bf0c3d3b746a4658aea869e30e8fd742); [Dados/IESP – Nicolau (2000)](https://dados.iesp.uerj.br/artigos/?id=601); [OAI SciELO S0011-52582000000400004](https://sidalc.net/search/Record/oai:scielo:S0011-52582000000400004).


---

# Rodada 2 — reverificação depois das correções (commit 25ab720)

**Data:** 26/11/2026. **Modo:** 1, reverificação. Seguindo o anti-padrão 6 do pipeline, esta rodada não se limita aos itens corrigidos. Reli o Resumo, o Abstract e as seções 1 a 9, os Apêndices A e B, o diff completo de `analise.py` (c78105d → HEAD), as tabelas e as figuras 4 e 5.

**Execução.**
- *Com o cache.* Uma cópia em `scratchpad/repo2` reproduz `artigo.md` e as 11 tabelas byte a byte. Das 1.590 chaves de `resultados.json`, 1.589 são idênticas (só muda o tempo de execução).
- *Do zero.* Uma segunda cópia, `scratchpad/repo3`, rodou sem cache: levou 668 s em 4 núcleos e reproduz tudo do mesmo jeito: `artigo.md` muda só na linha do tempo de execução, as 11 tabelas são idênticas e 1.589 das 1.590 chaves são iguais. Os ajustes de IRT, portanto, se reproduzem a partir do código, e não só a partir do cache.

Nenhum arquivo do artigo foi editado. Só esta seção foi acrescentada.

## Veredito da rodada 2: **FAIL**

São **0 P0, 3 P1 novos ou remanescentes e 18 P2**. Seis dos oito P1 da rodada 1 foram resolvidos, e um sétimo (o marcador de Nicolau) passou a nota aberta. Restam três problemas:
- o placebo, corrigido no texto mas não na Figura 5;
- a nova leitura da troca de partido ("adaptação"), que troca um exagero pelo exagero oposto;
- uma afirmação falsa nova, a de que "a alta de 2025 não vem da composição".

No checklist dos 7 modos, o **modo 1 continua SUSPECTED** e bloqueia. O modo 6 passou a CLEAR.

## R2.1 Situação dos P1 da rodada 1

| ID | Situação | Evidência |
|---|---|---|
| P1-1 (excesso no PSOL) | **Resolvido** | A §5.8 ordena PSB (17,8), PDT (12,8) e PSOL (12,0), o que confere com `div_cf_*_excesso`. |
| P1-2 (placebo) | **Resolvido no texto, não na figura** → ver R2-P1-A | A §5.7 traz as datas corretas (22/08/2023 e 07/02/2024), diz que os coeficientes em U não são identificados e relata o placebo em D (+13,4 [1,9; 25,0]). A Figura 5, porém, ainda plota o placebo em U. |
| P1-3 (pré-tendência) | **Resolvido** | Todas as defasagens são relatadas: −1,7 [−3,5; 0,1], −0,9 e +1,4. O texto diz "sem pré-tendência estatisticamente distinguível" e menciona o sinal fraco de cerca de 3 pontos. |
| P1-4 (troca como "correção") | **Substituído por um exagero no sentido oposto** → ver R2-P1-B | |
| P1-5 (contrafactual M5) | **Resolvido**, com uma nota P2 | Dois contrafactuais, rotulados como limite inferior (3,9 [3,0; 4,9]) e como estimativa que tende a superestimar (16,5 [14,3; 19,0]). Conferi o código: `global_sem_divergentes` é treinado sem as células divergentes da base e prevê exatamente essas células, sem vazamento. |
| P1-6 (Método × código) | **Resolvido**, com uma nota P2 | M3L implementado (M2→M3L = 0,0151 [0,0124; 0,0180], igual ao que eu tinha estimado na rodada 1). ρ_i ∈ ℝ. A amostra completa do estudo de evento e a 1ª troca estão descritas. Tema usa só médias brutas. Resta o título da §4.3, que ainda diz "seis modelos" (R2-P2-9). |
| P1-7 (desvios e pré-registro) | **Resolvido**, com uma nota P2 | O Apêndice B traz 17 linhas, coerentes com a seção 6 da rodada 1, e o Apêndice A foi reescrito. O Apêndice B diz que o plano foi "revisado antes das análises de P2 a P4", mas `stage1_blueprint.md` tem um único commit (6802984), e o Apêndice A diz que ele "não foi congelado formalmente" (R2-P2-10). |
| P1-8 (Nicolau "[verificar páginas]") | **Mantido de propósito** → nota aberta (R2-P2-16) | Refiz a busca na web. A existência está confirmada (DOAJ, IESP/Dados id 601, SciELO S0011-52582000000400004), mas as páginas não: o DOAJ traz "00–00". Marcar o que não foi conferido, em vez de inventar, é a conduta certa, e não é fabricação. Fica como nota que não bloqueia no Stage 2.5. No Stage 4.5, que exige zero problemas, vai bloquear se continuar aberta. |

## R2.2 Problemas P1 desta rodada

| ID | Local | Problema | Correção sugerida |
|---|---|---|---|
| **R2-P1-A** | Figura 5; `ols_fe`/`estudo_evento`; `resultados.json` (`ev_U_fus:0 a 3_identificado = true`) | A nova verificação de posto em `ols_fe` remove `fus:≥4` por colinearidade e **mantém** `fus:0 a 3`. Para os 5 deputados de fusão sem observações antes da fusão, o coeficiente que sobra não mede a diferença em relação à janela de referência. Mede o contraste entre "0 a 3" e "≥ 4" (+0,48 p.p.). A Figura 5 o desenha como efeito relativo a −12 a −7 meses e ainda desenha um quadrado de placebo na referência, onde não há observação de fusão. O texto diz o contrário ("não são identificados"). O problema geral é que remover uma coluna colinear muda o significado das outras sem aviso. | Quando um grupo de indicadores de evento não tem observações na janela de referência, retirar o grupo inteiro em U. Desenhar na Figura 5 só o placebo em D, com a observação n = 9. Na verificação de posto, registrar como "não identificados em relação à referência" todos os coeficientes do grupo afetado, não só a coluna removida. |
| **R2-P1-B** | Resumo, Abstract, §5.7 (2º parágrafo de "Há duas leituras"), §8, §9 | A afirmação "A comparação de posições favorece a segunda [adaptação]", com o destino que "não estava, em regra, mais perto", se apoia em duas coisas. A primeira é que o destino estava mais perto em só 44,8% dos casos. A segunda é uma mudança **absoluta, sem direção**, de 0,21, comparada à distância entre as medianas (0,22). Reproduzi o cálculo com os mesmos pontos e o bootstrap de 100 réplicas. Resultados: **(i)** 67,6% dos trocadores já estavam, antes da troca, do lado da mediana de origem voltado para o destino. Isso é seleção na direção, coerente com os 61,8% a 64,5% da validação preditiva do próprio artigo, que o argumento omite. **(ii)** 69,7% se moveram em direção ao destino, com mediana de +0,13. É evidência de adaptação, mas menor que os 0,21 citados. **(iii)** O EP bootstrap mediano da mudança é 0,13, e só 43% das mudanças passam de 1,96 EP. Os períodos depois da troca têm mediana de 49 votos. "A mudança é, se algo, subestimada" não está demonstrado, porque o ruído infla \|Δx\| na mesma medida em que o encolhimento o reduz. "Mais perto do destino do que da origem" é um critério rígido demais para medir seleção quando as medianas dos partidos ficam longe umas das outras. | Apresentar as duas evidências: seleção na direção (68% do lado do destino; 62% a 65% na validação preditiva) e ajuste posterior (70% se movem em direção ao destino, mediana de +0,13, EP de cerca de 0,13). Concluir que os dados são compatíveis com as duas coisas e não as separam. Retirar do Resumo e do Abstract "o destino não estava, em regra, mais perto" e "favorece a adaptação". Retirar da §9 "sem que o destino estivesse...". Na §8, trocar "sugere que os deputados se ajustam" por "não sustenta que a troca seja só seleção". Reportar a mudança com sinal e com IC. |
| **R2-P1-C** | §5.1, 3º parágrafo | A frase "Mesmo fixando a composição partidária, D em 2025 fica em 92,0%, contra 90,5% em 2023: **a alta não vem da composição**" é desmentida pelos próprios números. A diferença bruta entre 2023 e 2025 é 2,8 p.p. (92,9 − 90,1). Com a composição fixa, é 1,5 p.p. (92,0 − 90,5). Cerca de **metade** da alta vem, portanto, da composição. | Escrever: "fixando a composição partidária, a diferença cai de 2,8 para 1,5 ponto; cerca de metade da alta vem da composição dos votos orientados, e o restante, de quais votações tiveram orientação". |

## R2.3 Problemas P2 desta rodada

| ID | Local | Problema / correção |
|---|---|---|
| R2-P2-1 | §5.1; Tabela 2 | **Arredondamento duplo.** `num()` arredonda para 4 casas e o formatador arredonda de novo. Por isso o texto e a tabela divergem: União tem D de 82,5% no texto e 82,4 na Tabela 2 (0,82449…); PP tem D própria de 95,0% no texto e 94,9 na tabela. Guardar o valor sem arredondar, ou formatar texto e tabelas a partir da mesma chave arredondada. |
| R2-P2-2 | §5.8 | "Nos partidos do centro, o excesso é de 2 a 4 pontos, e no PODE é nulo (−1,4)". Os valores são União 1,9, AVANTE 1,0, MDB 3,7, PSD 3,9, PP 4,3, PSDB 4,3, **REPUBLICANOS −1,2** e PODE −1,4. Corrigir o intervalo para "de 1 a 4 pontos" e citar REPUBLICANOS ao lado do PODE. |
| R2-P2-3 | §5.8; Resumo e Abstract ("até 16,5") | O contrafactual (ii) não é crível para partidos que divergem do Governo pela esquerda. Ele prevê que o PSOL seguiria o partido em só 34,1% das divergências (o observado é 98,6%), o PSB em 25,6% e o PDT em 29,4%. Esses partidos puxam o limite superior para cima. Reportar o (ii) também sem PSOL, PSB e PDT, ou por partido, e dizer que ele não representa bem a oposição pela esquerda. |
| R2-P2-4 | Tabela 11; `interpretar_intra`/`tabela_cargas` | A nova coluna "Resultado" sai toda como "–". `votacoes.aprovacao` é texto ('1'/'0') e o dicionário espera números inteiros ou booleanos. Converter com `pd.to_numeric`. (O texto já não diz "rejeitados", então não há afirmação errada; a coluna é que não funciona.) |
| R2-P2-5 | Tabela 6; §4.5 e §5.6 | O IC bootstrap básico corrige o deslocamento, mas dá limite inferior **negativo** para o DP do NOVO (−0,03) e limite superior igual ao ponto para o PT (0,23 [0,12; 0,23]). O "viés mediano de 0,008" esconde vieses grandes nos partidos pequenos e de esquerda. Truncar em 0, mostrar o viés por partido e avisar que o IC não é confiável com 5 a 14 períodos. A nota da Tabela 6 não diz que o IC é "básico". |
| R2-P2-6 | Tabela 7 (nota) | Agora a tabela também filtra por \|z\| ≥ 2, mas a nota ainda diz só "IC exclui a mediana". Atualizar. |
| R2-P2-7 | §5.6 | "O painel do projeto destacava no PL João Carlos Bacelar, Henrique Júnior, Bosco Costa" é rastreável (`prev_diss_pl`). Já "assim como Evair Vieira de Melo e Pezenti no sentido oposto" e a menção a Daniel José não correspondem a nenhuma chave calculada a partir do painel. Calcular os oposicionistas relativos de `emb_votos` ou retirar. |
| R2-P2-8 | §1, 2º parágrafo | Ficou "a série temporal da disciplina 'à orientação' é, em 2025, um artefato de cobertura", afirmação categórica que a §5.1 já moderou ("compatível com"). Harmonizar. |
| R2-P2-9 | Título da §4.3 | Diz "seis modelos", mas o texto diz "oito modelos hierarquizados". |
| R2-P2-10 | Apêndice B, 1ª frase | "Revisado antes das análises de P2 a P4" não tem evidência no repositório (um só commit do blueprint) e contradiz o "não foi congelado formalmente" do Apêndice A. Escrever "e não foi revisado nem congelado formalmente". |
| R2-P2-11 | Abstract | "year-to-year change in U is 1.6 point" deveria ser "1.6 percentage points". |
| R2-P2-12 | §3, "Partido na data" | Frase truncada: "reflete a janela partidária de março–abril de 2026, e nos meses seguintes (março–maio), quando ocorreram 139...". Reescrever, por exemplo: "reflete as trocas de março–maio de 2026 (139 das 191 trocas individuais), concentradas na janela partidária". |
| R2-P2-13 | §5.3 | "Nada o ordenamento" ainda cita como evidência o ρ entre m = 10 e m = 5. O ρ entre o Rice bruto e o de m = 10 (0,99, com 4 partidos sem índice) está na §6. Mover para a §5.3. |
| R2-P2-14 | `resultados.json` | `ev_*_identificado = true` para `fus:0 a 3` em U é enganoso (ver R2-P1-A). |
| R2-P2-15 | Docstring de `analise.py` × Apêndice A | A docstring ainda diz "~40-60 min" e o Apêndice diz "20 a 30 minutos". Medido do zero nesta máquina: 668 s, ou cerca de 11 min, em 4 núcleos. Corrigir os dois. |
| R2-P2-16 | Referências e §2.1/§4.1 | Ficaram de propósito três marcadores "[verificar]": as páginas de Nicolau, o mecanismo de Figueiredo e Limongi e a fórmula de Carey. É nota aberta, sem fabricação. Tentei confirmar a fórmula do *weighted Rice* de Carey e as páginas de Nicolau na web, sem sucesso. Precisam ser resolvidos com o texto original antes do Stage 4.5, que bloqueia notas desse tipo como problemas MEDIUM. |
| R2-P2-17 | `referencias.bib` (`cameron2011`) | O campo `note` ainda diz "conferir DOI [verificar]". O DOI foi verificado na rodada 1 (10.1198/jbes.2010.07136, via EconPapers/RePEc): acrescentar e tirar o marcador. |
| R2-P2-18 | §5.4 | M3L "contém M3 e, na prática, M2". O segundo encaixe não é exato, porque a penalização de g e de x difere entre M1 e M3. Escrever "contém M3; M2→M3L compara lealdade com lealdade mais direção". |

## R2.4 Conferências que passaram (denominadores)

- **Código novo, 14 itens.**
  - M0c usa só o treino, com suavização de Laplace e estratos de partido × fonte.
  - M3L usa como *offset* o M3 da mesma dobra.
  - `global_sem_divergentes` prevê fora da amostra.
  - A verificação de posto em `ols_fe` funciona; só falha na interpretação (R2-P1-A).
  - D com composição fixa: os pesos são a participação de cada partido em D.
  - Amplitude de U: 1,6 p.p. entre anos e 5,0 p.p. entre semestres. Confere com o texto.
  - Variância ajustada: ruído de 0,99% (U) e 1,47% (D). Confere com o que eu tinha calculado na rodada 1.
  - Presença por data: 242 datas, 99,2% delas a até 5 de 513.
  - PEC: presidente da sessão excluído das ausências (83,9%).
  - Números prévios a partir de `alinhamento.parquet` e `emb_votos`: PT 98,4, PSOL 97,2, NOVO 97,0, PP 86,3, REPUBLICANOS 89,7. Os pivôs prévios conferem.
  - Formatos em inglês no Abstract (454,829; 90.9%; datas por extenso).
  - Impressão digital do cache.
  - `selecao_troca` reproduzida (n = 145; 44,8%; 0,207; 0,219).
  - Datas das fusões: PSC 2023-08-22, PATRIOTA 2024-02-07.
- **Números renderizados.** A reexecução bate em 100% dos marcadores. Conferi à mão 46 valores do texto novo contra `resultados.json` e as tabelas. Divergem os dois casos de arredondamento duplo (R2-P2-1) e o intervalo "2 a 4" (R2-P2-2).
- **Referências.** Lista com 24 entradas, 24 citadas no texto e 24 no .bib. Não há órfãs nem citações sem entrada. Cameron (2011) agora é citada na §4.4. As novas formulações de contexto (§1 sobre Snyder e Groseclose, McCarty et al. e Zucco e Lauderdale; §8 sobre Krehbiel) conferem com os resumos verificados no Stage 1.
- **Resumo × Abstract.** Equivalentes, frase a frase. Os dois herdam R2-P1-B.

## R2.5 Checklist dos 7 modos (rodada 2)

| Modo | Rodada 1 → Rodada 2 | Evidência |
|---|---|---|
| 1. Bug de implementação | SUSPECTED → **SUSPECTED** (bloqueia) | Placebo em U desenhado com um coeficiente cujo significado mudou depois da remoção por colinearidade (R2-P1-A). Coluna "Resultado" inoperante (R2-P2-4). Arredondamento duplo (R2-P2-1). IC básico negativo (R2-P2-5). Nenhum desses muda os resultados principais. |
| 2. Citação alucinada | CLEAR → **CLEAR** | As 24 obras existem. Restam três "[verificar]" declarados, que não são fabricação. |
| 3. Resultado alucinado | CLEAR → **CLEAR** | 100% reproduzido com o cache. Também 100% reproduzido do zero, sem cache (668 s). Os números prévios agora são rastreáveis, exceto dois nomes (R2-P2-7). |
| 4. Atalho | SUSPECTED → **SUSPECTED** (só sinalização) | M0c e o contrafactual (ii) foram acrescentados. Resta o (ii) para a esquerda (R2-P2-3). Para o Stage 3, sugiro também a comparação M2→M3L por partido. |
| 5. Bug reapresentado como achado | CLEAR → **CLEAR** (com nota) | Não há bug por trás da nova leitura "adaptação, não seleção". Mas ela se apoia numa medida sem direção e ruidosa e inverte, no mesmo ciclo de revisão, a conclusão anterior, quando o P1-4 pedia moderação e não inversão. É deriva de força da afirmação, tratada como R2-P1-B. Se não for corrigida, reclassificar como SUSPECTED no Stage 4.5. |
| 6. Fabricação de metodologia | SUSPECTED → **CLEAR** | O Método agora corresponde ao código (estudo de evento, M2/M3L, temas, ρ_i, contrafactuais). Restam erros de redação (título "seis modelos"; "revisado" no Apêndice B), que não descrevem procedimentos inexistentes. |
| 7. Frame-lock | CLEAR → **CLEAR** | — |

**Bloqueio:** o modo 1 está SUSPECTED; a correção é a de R2-P1-A. O modo 4 é só sinalização.

## R2.6 Desvios do blueprint

O Apêndice B cobre 17 dos 21 desvios listados na seção 6 da rodada 1. Os quatro que faltam são:
- os correlatos da troca futura e a divergência por tipo de votação em P5 (calculada, mas não reportada);
- a robustez com todos os λ_g e λ_d em todas as dobras (só aparece "dobra 0", sem dizer que λ_g = 0,1 foi omitido);
- a incerteza das cargas (mencionada como "sem IC", aceitável);
- a análise nova de seleção nas trocas (`selecao_troca`), que não estava no plano. Ela deveria ser marcada como exploratória/pós-hoc, tanto mais porque sustenta uma conclusão que vai para o Resumo. → incorporar em R2-P1-B.

## R2.7 O que fazer a seguir

- Corrigir R2-P1-A, R2-P1-B e R2-P1-C.
- Rodar `analise.py` de novo.
- Reverificar a Figura 5, a §5.7, a §5.1, o Resumo, o Abstract, a §8 e a §9.
- Os P2 podem seguir para o Stage 3, se o usuário preferir. As três notas "[verificar]" precisam estar resolvidas até o Stage 4.5.
