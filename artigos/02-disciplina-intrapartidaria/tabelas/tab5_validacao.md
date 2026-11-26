**Tabela 5 – Desempenho fora da amostra nas células com divisão interna (validação cruzada em 5 dobras de células deputado×votação)**

| Modelo | Log-loss | Brier | Acurácia | AUC-PR (desvio) |
|---|---|---|---|---|
| M0 orientação do líder | 0,4475 | 0,1359 | 84,08 | 0,167 |
| M0c orientação, calibrada por partido e fonte | 0,4298 | 0,1312 | 84,05 | 0,228 |
| M1 só partido×votação | 0,2838 | 0,0831 | 88,94 | 0,677 |
| M2 = M1 + lealdade individual | 0,2641 | 0,0780 | 89,46 | 0,695 |
| M2b = M1 + lealdade por período × escala por votação | 0,2583 | 0,0765 | 89,68 | 0,703 |
| M3 intra 1D | 0,2525 | 0,0730 | 90,31 | 0,723 |
| M3L = M3 + lealdade individual | 0,2491 | 0,0727 | 90,24 | 0,725 |
| M3 com posições embaralhadas no partido | 0,6736 | 0,1696 | 78,96 | 0,212 |
| M4 intra 2D | 0,2447 | 0,0707 | 90,56 | 0,738 |
| M5 global 2D (sem partido) | 0,2655 | 0,0792 | 89,21 | 0,695 |

*Células com divisão interna: partido×votação com ≥ 5 colegas no treino e ao menos um voto contra a maioria do partido no treino. AUC-PR: precisão média ao ranquear os votos contra a maioria de treino da célula.*
