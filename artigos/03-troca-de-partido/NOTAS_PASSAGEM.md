# Artigo 3 — Troca de partido e deslocamento do voto: notas de passagem

Sessão anterior encerrada a pedido do usuário, para continuar numa sessão com o plugin
Academic Research Skills (ars). **Ainda não há artigo.md, analise.py, figuras nem referencias.bib.**
Os números abaixo vêm de verificações exploratórias feitas no terminal: precisam ser
reproduzidos pelo `analise.py` antes de entrar no texto.

## Ambiente
- `pip install pyarrow scipy scikit-learn matplotlib statsmodels` (pandas/numpy já existiam).
- `import embeddings_deputados as E` funciona a partir da raiz; `E.preparar_votos` e
  `E.ajustar_irt` podem ser reutilizados sem alterar o arquivo. Um ajuste 2D com períodos
  (λ_d = 4) leva ~15 s em CPU (433.476 votos, 1.470 votações) e converge.

## Já verificado nos dados
- `trajetoria_partidaria.parquet`: 186 deputados com troca (165 com 1, 18 com 2, 3 com 3);
  167 com deslocamento definido; corr(salto, deslocamento) = 0,668 (confere com o enunciado).
- `deputados_partidos`: 210 eventos de troca. Calendário (data de registro na Câmara):
  110 em abr/2026 e 21 em mar/2026 (dias com picos: 25/3, 1/4, 7–8/4, 10/4, 29/4/2026);
  o restante espalhado em 2023–2025. As datas são de registro administrativo e podem
  atrasar em relação à filiação real (vários registros de abril caem depois do prazo de
  filiação para 2026; conferir datas da janela: art. 22-A, III, Lei 9.096/95 [verificar]).
- Mudanças coletivas, que não são decisão do deputado, a separar das individuais:
  PROS→SOLIDARIEDADE (23/03/2023), PSC→PODE (ago/2023 em diante, com registros atrasados
  até 2026), PATRIOTA→PRD (07/02/2024, fusão PTB+Patriota). Gilberto Nascimento (PSC→PSD)
  é individual. Há eventos no início da legislatura (01–02/02/2023, ex.: PTB→PP, PSC→REPUBLICANOS)
  e o estado `S.PART.` (sem partido) como trânsito (Yury do Paredão: PL→S.PART.→MDB).
- O partido do voto (`votos.deputado_siglaPartido`) bate com o período de filiação em
  99,97% dos votos (divergências de 2 a 6 votos no dia da troca).
- Votos válidos (Sim/Não/Obstrução) por evento: mediana ~695 antes e ~57 depois;
  175 eventos com ≥ 20 votos antes e depois. Votações nominais caem muito depois de
  mai/2026 (ano eleitoral) — o pós-troca da janela de 2026 é curto.
- Condição eleitoral: 512 titulares, 114 suplentes, 20 efetivados, 2 não eleitos.

## Desenho planejado (a validar/refinar com o pipeline ars)
1. Classificar os eventos: coletivo / início de legislatura / individual; S.PART. como trânsito.
2. Medida principal, livre de modelo: nas votações em que as maiorias dos não-trocadores
   da origem e do destino divergem, afinidade relativa A = P(vota com destino) − P(vota com origem),
   por mês relativo à troca (estudo de evento, −12…+6 meses).
3. Medida do modelo: fixar (a_j, b_j) do ajuste global, reestimar o ponto do deputado por janela
   relativa com prior fraco e projetar na reta origem→destino (r = 0 origem, 1 destino):
   testa antecipação (r_pré > 0, tendência pré-troca) e ajuste posterior.
4. Placebo/comparação: não-trocadores com datas e destinos fictícios sorteados da distribuição real.
5. Sensibilidade de λ_d ∈ {0,25; 1; 4; 16; 64}: correlação e inclinação deslocamento~salto
   (a penalização encolhe δ).
6. Disciplina antes/depois: regressão com efeitos fixos de deputado e mês, trocadores e
   não-trocadores, erro agrupado por deputado.
7. Tipologia descritiva (formalização / conversão / sem mudança / intrabloco), sem leitura causal.
8. Perfil de quem troca (logit com covariáveis pré-tratamento de 2023–24: distância ao partido
   de origem, disciplina, suplência, UF/região, tamanho do partido, federação).
9. Calendário x janela legal e matriz de fluxos entre partidos/campos.

## Pendências
- Tudo da entrega: `analise.py`, `artigo.md`, `figuras/`, `referencias.bib`.
- Conferir as referências (Desposato 2006; Nokken & Poole 2004; Melo 2004; Freitas 2012;
  Heller & Mershon 2009; McCarty, Poole & Rosenthal 2001; Clinton, Jackman & Rivers 2004;
  Res. TSE 22.610/2007; EC 91/2016; Lei 13.165/2015; EC 111/2021) e as datas legais da janela de 2026
  e das incorporações/fusões no TSE.
- Uma revisão metodológica por agente foi iniciada e interrompida sem resultado: refazer.
