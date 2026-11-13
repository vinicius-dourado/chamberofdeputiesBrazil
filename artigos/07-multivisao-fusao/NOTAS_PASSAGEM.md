# Notas de passagem — Artigo 7 (multivisão e fusão)

Estado em 13/11/2026. O trabalho foi interrompido a pedido do usuário (repassado pela sessão do Artigo 2) para continuar numa sessão com o plugin Academic Research Skills (ars).

## O que está pronto
- `desenho_metodologico.md`: desenho das análises A–I (reprodução, concordância, informação única, fusões, tarefas externas, agrupamento, incoerência, viés de seleção, sensibilidade do SNF). É a versão anterior à revisão abaixo e precisa ser atualizado com ela.
- `codificar_discursos.py`: recodifica os discursos com texto corrigido. Remove os cabeçalhos "O SR./A SRA. NOME (PARTIDO - UF...)" e "DISCURSO NA ÍNTEGRA ENCAMINHADO PELO/PELA SR(A). DEPUTADO(A) ..." e neutraliza as marcas de gênero do sumário e das palavras-chave ("A Deputada", "oradora", "Ela"). Grava um vetor por discurso em `cache/` (não versionado).
  - A limpeza foi conferida: restam cerca de 0,7% de cabeçalhos e 0% de marcas de gênero no sumário.
  - A codificação **não foi concluída**, porque foi interrompida. Rode `python artigos/07-multivisao-fusao/codificar_discursos.py`. Leva cerca de 30–40 min em CPU e precisa de `torch` (CPU) e `sentence-transformers`.
- `.gitignore`: ignora `cache/` e `*.npy`.
- Ambiente: `pyarrow`, `scipy`, `scikit-learn`, `matplotlib`, `torch` (CPU) e `sentence-transformers` instalados nesta sessão. Reinstale na sessão nova.

## Falta fazer
Nada abaixo foi feito; nenhum número do artigo foi calculado ainda.
- `analise.py`: script reprodutível com todas as análises do desenho, já incorporadas as correções da revisão.
- `artigo.md` completo, `figuras/` e `referencias.bib`. As referências do enunciado ainda não foram conferidas.
- A reprodução dos resultados prévios.

## Fatos verificados nesta sessão
- Reestimar os pontos ideais (IRT 2D) só com as votações anteriores a 2026-01-01 leva cerca de 15 s e converge. São 385.333 votos em 1.323 votações. As votações de 2026 somam 48.143 votos em 147 votações e 567 deputados. Isso viabiliza a tarefa de prever votos fora da amostra temporal e o split-half das visões de voto.
- Há 140 trocas de partido em 2026, a maioria em março e abril, na janela partidária. Isso viabiliza a tarefa de prever o partido de destino com visões construídas antes da janela.
- Os arquivos `.npy` com os vetores por discurso não estão no git.

## Problemas conhecidos no código existente (`embeddings_deputados.py`, que não deve ser alterado)
Encontrados por revisão metodológica independente. O item 1 foi conferido nesta sessão.

1. **Vazamento de sexo e de partido nos discursos.** A regex de `embeddings_deputados.py:291` (`^O SR?A?\.`) não remove "A SRA. NOME (PARTIDO - UF ...)". Além disso, os sumários dizem "A Deputada".
   - Conferido: o kNN5 acerta o sexo em 99,6% (`discursos_tema`) e 99,8% (`discursos_fala`). A taxa base é 80%. As outras visões ficam perto do acaso (votos 79%, temas 76%, frentes 79%).
   - Consequência: os resultados prévios dos discursos (acerto de partido de 31–32%, R² de 0,37–0,39) e tudo o que os usa (SNF, `prox_media`, exemplos de consulta) estão contaminados.
   - Correção: `codificar_discursos.py`. Depois de reagregar, medir de novo o acerto de sexo. Se continuar alto (flexões como "obrigada"), remover linearmente a direção que separa os sexos (estilo LEACE) e relatar as duas versões.
2. **Partido pós-janela.** `salvar_emb` usa o partido atual de `deputados.parquet`, que já é posterior às trocas de 2026: 93 dos 410 deputados da interseção estão com o partido errado.
   - Correção: usar o partido em 2025-12-31 (de `deputados_partidos.parquet`) e guardar o partido atual só como desfecho da tarefa de troca.
3. **`votos_intra`: média de períodos sem peso.** A média não pondera pelo número de votos de cada período (linhas 173–174). Partidos com um só membro e "S.PART." ficam com x = 0 por construção.
   - Correção: ponderar pelo número de votos e descartar períodos de partidos com menos de 3 membros ou menos de 50 votos.
4. **Percentis de `fusao` em populações diferentes.** Cada `prox_v` é ranqueado sobre os deputados daquela visão. Correção: recalcular tudo só sobre os 410.
5. **PCA dos discursos.** É ajustado com deputados que têm 1 ou 2 discursos. Correção: ajustar só com quem tem 10 ou mais e projetar os demais.
6. **Validação cruzada de `avaliar` sem embaralhamento.** Correção: `StratifiedKFold(shuffle=True, random_state=0)`.

## Recomendações da revisão para o desenho
- **Versão principal.** A principal deve ter 4 arenas: votos, temas, frentes e um dos discursos. As 6 visões ficam como sensibilidade (dupla contagem).
- **Vazamento temporal.** Construir as visões com dados anteriores a 2026 para as tarefas de voto e de troca. As frentes não têm data de adesão: usar `dataCriacao < 2026`. Para a coautoria, construir os temas com 2023–24 e medir a coautoria em 2025–26.
- **AUC de pares.** Estratificar por mesmo partido e mesma UF, ou relatar o ganho sobre uma logística com `mesmo_partido` e `mesma_UF`.
- **Incerteza.** Usar subamostragem de 80% sem reposição, não bootstrap com reposição: as duplicatas quebram o kNN e o SNF.
- **Mantel.** Permutação restrita dentro do partido, em vez de Mantel parcial. Repetir a concordância só entre colegas de partido.
- **CKA.** Usar o estimador não viesado (HSIC-U de Song et al., 2012). Dispensar o CKA gaussiano.
- **Incoerência.**
  - Confiabilidade split-half por visão: discursos, proposições e frentes divididos ao acaso; votações divididas com o IRT reajustado.
  - Índice desatenuado, J_ab / sqrt(rel_a·rel_b).
  - Nulo por permutação dentro do partido.
  - Preferir o Spearman de linha ao Jaccard.
- **Baselines.**
  - Votos: orientação do partido, log-loss, votações disputadas e o IRT pré-2026.
  - Troca de partido: popularidade do destino, distância em dim1 e federação.
  - Grupos: k-means em votos com o mesmo k e ARI nulo.
- **Cortes.**
  - Incoerência direcional.
  - Grade do SNF reduzida a mu = 0,5, K ∈ {10, 20, 40} e t ∈ {10, 20}.
  - GCCA opcional: a concatenação padronizada fica como fusão linear de referência.
- **Acréscimo.** Pesos IPW de inclusão nos 410 para as regressões do índice de incoerência.
