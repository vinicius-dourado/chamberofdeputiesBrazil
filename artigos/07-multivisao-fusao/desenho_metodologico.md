# Desenho metodológico — Artigo 7: representação multivisão dos deputados (57ª Legislatura)

## Pergunta
Um deputado é a mesma "pessoa política" nas arenas voto, associação (frentes), agenda (temas das proposições que assina) e fala (discursos)?
Sub-perguntas: (Q1) quanto as visões concordam; (Q2) o que cada uma acrescenta; (Q3) onde estão as incoerências e o que significam;
(Q4) a fusão produz tipologia mais informativa que o partido?

## Dados e visões (já calculadas por embeddings_deputados.py)
- votos: pontos ideais IRT 2D (621 deputados com >=50 votos)
- votos_intra: IRT 2D com efeito fixo partido×votação, centrado no partido (mesmos votos)
- temas: perfil temático das proposições (autoria fracionada), embedding de Hellinger, 32 dims (579)
- frentes: TF-IDF de pertença a frentes (coordenador peso 3) + SVD 16D, cosseno (549)
- discursos_tema: e5-small sobre sumário+keywords da Câmara, média por deputado, PCA 32D, cosseno (447)
- discursos_fala: idem sobre transcrição (primeiros 256 tokens) (447)
- 410 deputados em todas as visões.

## Análises planejadas
A. Reprodução: kNN(5) acerto do partido (CV 5 folds), ridge R² para dim1 de votos; nº pares; nº na interseção.
B. Concordância entre visões (N=410):
   - Mantel (Spearman entre triângulos superiores das matrizes de distância, 999 permutações de rótulos);
   - Mantel parcial controlando por "mesmo partido" (resíduos de rank sobre matriz de partido) -> concordância além do partido;
   - CKA linear (= coeficiente RV) sobre features centradas; CKA com kernel gaussiano (mediana) sobre distâncias;
   - sobreposição de vizinhanças k=10 (Jaccard médio), comparado ao acaso k/(n-1).
C. Informação única:
   - prever cada visão (features) a partir da concatenação das demais (ridge CV, R² ponderado pela variância), com e sem a visão "gêmea";
   - ablação: fusão sem cada visão, desempenho nas tarefas externas.
D. Métodos de fusão (N=410): média de percentis; SNF (K=20, t=20, mu=0.5); concatenação padronizada (cada bloco com variância total 1) + PCA;
   GCCA MAXVAR regularizada (autovetores de soma das projeções regularizadas de cada visão). Versões com 6 visões e com 4 arenas
   (sem votos_intra e discursos_tema; e gêmeas fundidas) para testar dupla contagem.
E. Tarefas externas (não usadas na construção):
   1. Votos fora da amostra temporal: reestimar as visões de votos SÓ com votações < 2026-01-01; prever o voto de i em cada votação de 2026
      como voto ponderado dos 10 vizinhos mais próximos (que votaram nela). Acurácia; baseline: orientação do partido; maioria; colegas de partido.
   2. Coautoria: AUC da similaridade para pares que coassinaram >=1 PL/PLP/PEC/PDL com <=10 autores; também só pares de partidos diferentes.
      (Ressalva: visão temas usa autoria -> vazamento parcial; reportar fusão sem temas.)
   3. Troca de partido (janela de 2026): para cada deputado que trocou em 2026, ranquear partidos de destino pela similaridade média
      com a bancada do partido em 2025; top-1 e MRR. Visões de voto pré-2026 (sem vazamento); demais com vazamento leve (anotar).
   4. UF: AUC para pares da mesma UF.
   Incerteza: bootstrap por deputado (200 réplicas).
F. Agrupamento: clusterização espectral sobre a matriz SNF (k por eigengap e k = nº de partidos efetivos); ARI/NMI com partido;
   interpretação dos grupos (composição partidária, dim1, temas, frentes, palavras-chave de discursos distintivas por log-odds).
   Comparar rótulos de grupo vs partido como preditores nas tarefas (mesmo número de grupos).
G. Índice de incoerência por deputado: 1 - Jaccard médio das vizinhanças k=20 entre as 4 arenas; perfil por regressão (volume de dados
   como controle, |dim1|, centrão vs polos, tamanho do partido, troca de partido, sexo, titular/suplente, disciplina); exemplos.
   Também incoerência "direcional": partidarismo da vizinhança de voto vs da vizinhança de fala/frentes.
H. Viés de seleção: 410 vs 211 restantes (com votos): dim1, |dim1|, partido, suplência, sexo, disciplina, nº votos; testes.
I. Sensibilidade SNF: K∈{10,20,30,50}, t∈{5,10,20,40}, mu∈{0.3,0.5,0.8}: estabilidade (Spearman com base), NMI dos clusters, tarefas.
