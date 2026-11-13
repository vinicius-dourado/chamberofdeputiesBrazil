# Notas de passagem — Artigo 2 (sessão anterior, sem o plugin ars)

## Pronto
- `analise.py` (parte 1, roda em ~5 s): descritivo; disciplina estrita e direcional por partido, ano, fonte da orientação, tipo de orientação, tipo de votação (classificador por `votacoes.descricao`) e tipo de proposição; Rice e Rice padronizado por subamostragem hipergeométrica (m = 10) em votações disputadas (minoria ≥ 10%); Governo × partido divergentes; GLM binomial da defecção por deputado (suplente, troca, log cadeiras da UF, sexo, idade, efeitos fixos de partido, EP HC1); disciplina antes/depois da troca de partido.
- `tabelas/tab1_votacoes_tipo_ano.md`, `tabelas/tab2_disciplina_partidos.md`, `resultados.json`.
- Reproduzido do enunciado: dispersões na dim1 global (PDT 0,17 … PODE 0,55), pivôs e dissidentes batem com `emb_votos`; validação do README (92,9% intra) vem de `avaliacao.json`, ainda não refeita no script. Ajuste IRT global ≈ 20 s, intrapartidário ≈ 106 s (importando `ajustar_irt` de embeddings_deputados.py).

## Problemas conhecidos (corrigir)
- `r2_defeccao_partido` = 0,998: implausível (provável problema do R² em WLS ponderado); refazer.
- `resultados.json` grava NaN (JSON inválido): converter para null.
- Temas: `proposicoes_temas` cobre só 29% das proposições votadas; `temas_proposicoes()` completa pela API com cache em `dados_aux/` (ainda não chamada no main).
- Achado a interpretar com cuidado: disciplina sobe de 82,8% (partido antigo) para 90,8% (novo) entre 141 trocadores — confundido com a tendência temporal (disciplina geral 2023: 89,5% → 2025: 92,4%); controlar por ano.

## Falta
- Pontos ideais: teste "ruído vs. estrutura" fora da amostra (orientação; só efeito fixo partido×votação; intra 1D; intra 2D), interpretação das dimensões pelas votações com maior carga, dispersão, pivôs (mediana e 3/5 para PEC), bootstrap.
- Disciplina por tema; sensibilidade sem `bloco (inferido)` (as funções já aceitam `sem_inferidas=True`); só Plenário vs. com comissões.
- Figuras, `artigo.md`, `referencias.bib` (referências do enunciado ainda não verificadas).

## Desenho metodológico (rascunho v0, enviado ao revisor; o parecer não chegou a ser concluído)
# Desenho metodológico (rascunho v0) — Artigo 2: disciplina partidária e variação intrapartidária na 57ª Legislatura

## Pergunta
Quanta disciplina partidária há na 57ª Legislatura da Câmara (2023–nov/2026), onde ela falha, e a indisciplina é ruído ou tem estrutura (uma dimensão intrapartidária interpretável)? O que o voto individual acrescenta à orientação do líder?

## Dados (já disponíveis, repo /home/user/chamberofdeputiesBrazil, dados/leg57)
- votos.parquet: 473.323 votos nominais, 1.604 votações (1.128 de Plenário, ~456 mil votos; o resto em comissões), 644 deputados. Colunas: voto (Sim 277k, Não 188k, Obstrução 5,3k, Abstenção 1,1k, Artigo 17 1k), deputado_siglaPartido (partido na data), orientacao_partido (orientação da bancada aplicável: partido > federação > bloco > "bloco (inferido)"), orientacao_fonte, orientacao_governo/maioria/minoria/oposicao, seguiu_orientacao_partido/governo (só para Sim/Não/Obstrução/Abstenção; NA para Liberado/vazio).
- Distribuição de orientacao_partido: Sim 199k, vazio 122k, Não 117k, Liberado 28k, Obstrução 7k. orientacao_fonte: bloco 217k, partido 88k, bloco (inferido) 85k (≈18%), federação 78k.
- Não há registro de ausência: só sabemos quem votou. Não há dados eleitorais (votos/municípios) no repositório.
- votacoes.parquet: descrição, objeto_titulo (REQ 824, PRL 389, RPD 134, EMP, DTQ...), proposicao_titulo (PL, PLP, PEC, MPV, PDL...). proposicoes_temas: temas da Câmara por proposição.
- deputados (condicaoEleitoral: Titular/Suplente/Efetivado), deputados_partidos (períodos de filiação; 215 alterações de partido no histórico).
- Modelo existente (embeddings_deputados.py, não pode ser alterado, mas pode ser importado): IRT 2D penalizado (MAP com priors normais, L-BFGS), P(Sim)=σ(a_j + g_{p,j} + b_j·x_i), x_i = u_dep + δ_período (período = deputado×partido). Obstrução codificada como Não; votações com minoria < 2,5% removidas. Versão intrapartidária: efeito fixo g para cada partido×votação e x centrado no partido; ajuste em ~106 s. Global ~20 s.

## Medidas propostas
1. Taxa de disciplina: entre votos Sim/Não/Obstrução/Abstenção com orientação de bancada em {Sim, Não, Obstrução}, proporção voto == orientação. Variante "direcional": Obstrução e Não tratados como equivalentes (ambos contra a matéria). Por partido, por ano, por fonte de orientação, por tipo de orientação, por tipo de proposição (PEC, PL, PLP, MPV, PDL), por tipo de objeto (requerimento procedimental vs. mérito), por tema.
2. Índice de Rice por partido×votação: |S−N|/(S+N), com Obstrução = Não; média por partido; correção de Desposato (2005) para tamanho pequeno de bancada; restrito a votações disputadas (minoria ≥ 10%) para evitar inflar coesão com votações consensuais.
3. Votações com orientação "Liberado": distribuição do voto (o partido racha?), como contraste.
4. Partido × Governo divergentes: votos em que a orientação do partido e a do Governo são ambas Sim/Não e diferem; proporção que segue o partido vs. o Governo, por partido.
5. Desvio individual: taxa de defecção por deputado (1 − disciplina). Regressão binomial (GLM, logit, com efeitos fixos de partido e erros agrupados por deputado ou quase-binomial no nível do deputado) em: suplente (condicaoEleitoral), número de trocas de partido, UF (efeitos ou tamanho da bancada da UF), sexo, idade; ou modelo de voto com efeito aleatório de deputado (se viável).
6. Pontos ideais intrapartidários (reuso de ajustar_irt): comparação, fora da amostra (10% ou validação cruzada em 5 partes), de: (i) orientação do partido; (ii) só efeito fixo partido×votação (0 dimensões individuais); (iii) intra 1D; (iv) intra 2D. Se (iii)/(iv) > (ii), a indisciplina tem estrutura de baixa dimensão; se não, é ruído. Também log-loss.
7. Interpretação das dimensões intrapartidárias: votações com maior |b_j| (cargas) e o conteúdo delas (proposição, tema); correlação da dim1 intra com o desvio do deputado em relação à mediana do partido na dim1 global (já ≈ 0,76).
8. Dispersão por partido na dim1 global (desvio-padrão), pivôs (mediana do plenário; pivô de 3/5 para PEC: 308º deputado), dissidentes sistemáticos (maior desvio em relação à mediana do partido). Incerteza via bootstrap das votações (reajustar o IRT global ~50 vezes).
9. Robustez: refazer 1, 2, 4, 6 sem votos com orientacao_fonte = "bloco (inferido)"; só Plenário vs. com comissões; codificação alternativa de Obstrução; limiar de votações disputadas.

## Riscos conhecidos
- Só votações nominais (viés de seleção: as nominais são pedidas estrategicamente; Carrubba et al.).
- Ausências não observadas (a abstenção estratégica por ausência não aparece).
- Retrato estático; partido na data da votação.
- Orientações inferidas de blocos truncados; orientação vazia = não orientou.
- O IRT intrapartidário com efeito fixo partido×votação: identificação, bancadas pequenas (efeito fixo saturado por 1–2 deputados), penalização.
