# Stage 4 (REVISE): resposta aos revisores

**Contexto.** Respostas ao Revision Roadmap de `pipeline/stage3_revisao.md`, que tomou a decisão Major Revision. O manuscrito foi reescrito a partir de `artigo_fonte.md`, e todos os números vêm de `resultados.json`, gerado por `analise.py`. Cada item segue o formato R → A → C: comentário do revisor, ação tomada (com o local) e mudança resultante. Para os P0, dizemos se a conclusão mudou.

O usuário autorizou seguir sem parar nos checkpoints ("pode seguir direto"); por isso a decisão do Stage 3 não foi submetida a confirmação explícita. Os cartões dos revisores também não foram aceitos pelo usuário, porque o pedido veio do orquestrador, e a independência entre os revisores é limitada (ver o relatório do Stage 3).

## P0

**P0-1 (registro × comportamento).**
- **R:** a orientação vazia pode ser um limite do registro, e não ausência de orientação; a "D própria" do centro vem de poucas votações.
- **A:** criada `orientacoes_faladas()`, que extrai orientações das transcrições dos discursos ("o PL orienta 'sim'") e as associa à votação nominal seguinte (até 45 min). A validação contra o registro oficial dá 94,3% de concordância em 563 casos. Contei as linhas do registro nas votações do megabloco: nenhuma é própria do PL ou da federação do PT, e há 227 de Oposição. Reescritos o Resumo, o Abstract, a §1, a §3 (orientações faladas), a nova §5.1, a §7, a §8 e a §9. Retirada a afirmação "orientam onde estão unidos". A Figura 2 omite D com cobertura < 20%.
- **C:** **a conclusão sobre 2025 se inverte e se reforça.** Nas votações do megabloco, a disciplina medida pelas falas é de 81,8%; fora dele, nos mesmos votos, é de 87,4% pela fala e de 91,4% pelo registro. A disciplina caiu em 2025, como U já indicava. "Orientação vazia" passa a ser descrita como possível limite do registro.

**P0-2 (comparador M2 desigual).**
- **R:** a lealdade é por deputado e não tem escala por votação; pede-se M2b, um teste com sinais embaralhados e validação temporal.
- **A:**
  - criado M2b (lealdade por período × escala por votação, com a mesma estrutura de parâmetros de M3);
  - criado M3emb (posições permutadas dentro do partido);
  - acrescentados M0c (regra calibrada por partido e fonte) e a subamostra com minoria interna ≥ 10%;
  - a validação cruzada é chamada de imputação;
  - M0→M1 é reinterpretado como uso dos votos dos colegas na mesma votação.

  A validação temporal **não** foi feita, porque o estimador não permite fixar pontos e estimar só os parâmetros das votações novas; isso foi declarado na §7.
- **C:** M2b→M3 = 0,0058 [0,0029; 0,0086]. O efeito é menor que M2→M3 (0,012), mas o IC exclui zero, e E3 se mantém. M3emb piora a log-loss em 0,42. O texto passou a dizer que a direção é pequena perto da propensão a desviar.

**P0-3 (rótulo da dimensão).**
- **R:** "governismo relativo" não se separa de esquerda–direita, e a dimensão é quase o eixo global.
- **A:** o rótulo virou "eixo governo–oposição recortado dentro de cada partido", com a ressalva sobre esquerda–direita sob governo de esquerda; "confirma E4" virou "compatível"; registrado que a correlação com a posição relativa global é de 0,94 e que a estrutura além dela (2ª dimensão) é pequena.
- **C:** a interpretação fica mais modesta; nenhum número muda.

## P1

| Item | Ação | Resultado |
|---|---|---|
| P1-1 extensão | Manuscrito reescrito com cerca de 6,5 mil palavras no corpo, sem tabelas. Comparações com arquivos internos foram para o Apêndice C. Resumo de 209 palavras. Tabelas e figuras renumeradas pela ordem de aparição. | Feito |
| P1-2 E1–E5 | Critérios numéricos de falha (§2). E5 derivada do contraste Figueiredo–Limongi × Carey (principais concorrentes). | Todas se sustentam pelos critérios declarados |
| P1-3 Rice com m comum | m = 3 para todos os 16 partidos; ρ(bruto, m = 3) = 0,99 | E2 testada com os partidos pequenos |
| P1-4 escala da distância | Distância dividida pelo DP da dim1 de cada ajuste; chamada de "distância espacial" | 22,1 p.p. por DP |
| P1-5 estudo de evento | Versão só com a coorte de 2026, com controles que nunca trocaram (Sun–Abraham; Callaway–Sant'Anna); teste conjunto de pré-tendência | Queda de 6,5 p.p. em U na coorte (11,1 na versão completa); pré-tendência com p = 0,10 |
| P1-6 base | Base definida pela composição ministerial (verificada em `stage4_bibliografia.md`); partidos independentes separados; IC e nº de votações por partido; contrafactual (ii) também sem a esquerda | Adesão de 90,8%; excesso entre 4,2 e 17,1 p.p. (sem a esquerda, entre 2,6 e 11,2) |
| P1-7 inferência | Bootstrap em duas vias (votações × deputados) para D e U por partido (Tabela 2); Tabela 8 com EP e viés bootstrap em vez do IC degenerado | Feito |
| P1-8 U por federação | U calculado também por federação; U usado para comparar partidos | PSDB-CIDADANIA 82,1%; PT-PCdoB-PV 98,1% |
| P1-9 literatura | Nove obras verificadas e incorporadas (Amorim Neto et al., Cheibub et al., Pereira–Mueller, Desposato 2006, Nokken, Heller–Mershon, Minozzi–Volden, Sun–Abraham, Callaway–Sant'Anna). O mecanismo de Figueiredo e Limongi foi confirmado em fontes secundárias. A fórmula ponderada de Carey não foi confirmada no artigo de 2007 e foi retirada do texto. | Restam as marcas [verificar] em Nicolau (páginas) e na lista completa de instrumentos de Figueiredo e Limongi |
| P1-10 ausência não ignorável | Limite inferior de D com todas as ausências contadas como desvio | D cai de 90,9% para 73,1%; ρ do ordenamento = 0,91 |

## P2

- **P2-1:** Figura 2 refeita (D omitido com cobertura < 20%).
- **P2-2:** as contagens das Tabelas 1 e 3 diferem porque a Tabela 3 só conta votações com orientação diretiva; dito na nota.
- **P2-3:** Tabela 9 em DP do partido.
- **P2-4:** a §4.3 informa o N das células (64% dos votos); acrescentada a subamostra com minoria ≥ 10%.
- **P2-5:** Tabela 6 (cargas) com "texto mantido/suprimido".
- **P2-6:** "P5" corrigido no Apêndice B; siglas definidas na primeira ocorrência.
- **P2-7:** troca de partido separada em antes e depois na Tabela 7.
- **P2-8:** M5→M4 saiu da Figura 4.
- **P2-9:** validação pelas trocas apresentada como evidência modesta; a §9 foi ajustada.
- **P2-10:** classificador validado em 120 votações (acurácia de 94,1%, com 1 indeterminável).
- **P2-11:** parágrafo sobre usuários dos dados e sobre o registro da Câmara (§8).
- **P2-12:** versões dos pacotes no Apêndice A.
- **P2-13:** o Apêndice B separa análises confirmatórias de exploratórias e marca com † as mudanças posteriores à validação cruzada.

## O que não foi feito

- **Validação temporal** (P0-2): limite do estimador, declarado na §7.
- **Conferência manual de uma amostra de notas taquigráficas** (P0-1): substituída pela validação sistemática das falas contra o registro (563 casos).
- **Composição oficial dos blocos pela Câmara** (P0-1): não está nos Dados Abertos baixados.
- **Páginas de Nicolau (2000):** continuam [verificar], porque o SciELO está bloqueado nesta sessão.
