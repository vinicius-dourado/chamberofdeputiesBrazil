**Tabela 5 – Desempenho fora da amostra (validação cruzada em 5 dobras de células deputado×votação)**

| Amostra | Modelo | Log-loss | Brier | Acurácia | AUC-PR (desvio) |
|---|---|---|---|---|---|
| todas as células | M0 orientação do líder | 0,3627 | 0,1040 | 88,22 | 0,132 |
| todas as células | M1 só partido×votação | 0,2381 | 0,0666 | 91,37 | 0,631 |
| todas as células | M2 + lealdade individual | 0,2218 | 0,0628 | 91,72 | 0,653 |
| todas as células | M3 intra 1D | 0,2083 | 0,0573 | 92,54 | 0,699 |
| todas as células | M4 intra 2D | 0,1999 | 0,0550 | 92,79 | 0,718 |
| todas as células | M5 global 2D (sem partido) | 0,2094 | 0,0606 | 91,87 | 0,681 |
| células com divisão interna | M0 orientação do líder | 0,4475 | 0,1359 | 84,08 | 0,167 |
| células com divisão interna | M1 só partido×votação | 0,2838 | 0,0831 | 88,94 | 0,677 |
| células com divisão interna | M2 + lealdade individual | 0,2641 | 0,0780 | 89,46 | 0,695 |
| células com divisão interna | M3 intra 1D | 0,2525 | 0,0730 | 90,31 | 0,723 |
| células com divisão interna | M4 intra 2D | 0,2447 | 0,0707 | 90,56 | 0,738 |
| células com divisão interna | M5 global 2D (sem partido) | 0,2655 | 0,0792 | 89,21 | 0,695 |

*Células com divisão interna: partido×votação com ≥ 5 colegas no treino e ao menos um voto contra a maioria do partido no treino. AUC-PR: precisão média ao ranquear os votos contra a maioria de treino da célula.*
