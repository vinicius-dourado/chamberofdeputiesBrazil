# Notas de passagem — Artigo 1 (pontos ideais)

Estado em 13/11/2026. Fluxo seguido: `academic-pipeline` do plugin Academic Research Skills (ARS),
executado nesta sessão a partir do repositório do plugin (os agentes rodaram como subagentes com
as definições do ARS como prompt).

## Etapas do pipeline
| estágio | artefato | status |
|---|---|---|
| 1 RESEARCH (metodologia) | `pipeline/fase1_blueprint_metodologico.md` (research_architect_agent) | concluído; hipóteses e critérios fixados sem ver os valores |
| 1 RESEARCH (análise) | `analise.py` → `resultados.json`, `tabelas/`, `figuras/` | concluído (execução completa ~30 min) |
| 2 WRITE (literatura) | `pipeline/fase2_literatura.md` (literature_strategist_agent; Dados, Lua Nova, RBCP) | concluído; 15 refs verificadas, 7 [verificar] não usadas no texto |
| 2 WRITE (redação) | `artigo.md`, `referencias.bib` | versão completa (~11,7 mil palavras com tabelas e referências) |
| 2.5 INTEGRITY | `pipeline/fase2_5_integridade.md` | rodada 1 FAIL (1 SERIOUS, 7 MEDIUM) → corrigido; rodada 2 PASS WITH NOTES; MINOR restantes resolvidos |
| 3 REVIEW em diante | — | pendente (checkpoint obrigatório com o usuário) |

## Achados que divergem de leituras anteriores do projeto
- 2D não é "suficiente" pelo critério fixado: 3D acrescenta +0,41 pp (IC [0,30; 0,51]).
- dim1 é "predominantemente governo × oposição, com componente ideológico" (H1b não sustentada; ver Apêndice A).
- dim2 = dissidência dos polos programáticos (PSOL, NOVO; juntos em 37% das votações) frente a consensos amplos de centrão + PT (+ PL com frequência); não se reproduz nas comissões.

## Linha mestra (decisão do autor, 13/11/2026)
- O artigo se organiza em torno da pergunta "um eixo só explica o voto sob Lula 3?". Resposta: não.
  Governismo e ideologia se fundem na dim1; a dim2 (polos programáticos × acordos amplos) não é ideológica.
- Emendas parlamentares/orçamento impositivo NÃO entram como mecanismo ou choque externo (tema de artigo futuro).
  Pereira & Mueller 2002, Limongi & Figueiredo 2005 e Bonfim et al. 2023 saíram do texto e do .bib.
- As seções reescritas (título, resumo, 1, 2, 7, 9) ainda não passaram pela verificação de integridade.

## Eixo central (decisão do autor): comparação um eixo × dois eixos
- Seções 5.2 (onde o 2º eixo faz diferença: por tipo de votação, partido, posição coletiva, resultado) e
  5.3 (o que o eixo único distorce: PSOL e NOVO) — etapa `etapa_comparacao` no analise.py, tabelas t15–t17, fig9.
- Resultado desfavorável relatado: para prever o vencedor das votações, 1D erra 5 e 2D erra 7.
- PSOL < PT no 1D é só tendência (IC inclui 0); NOVO > PL em oposição no 1D é significativo.
- Comparações exploratórias (declaradas no Apêndice A, item 6). Estas seções ainda não passaram por integridade.

## Equilíbrio quanti/quali (decisão do autor)
- Corpo: resultados quantitativos enxutos (Seção 5), estudos de caso de 4 matérias (Seção 6: PL 709/2023,
  PEC 9/2023, PLP 210/2024, PEC 3/2021; etapa `etapa_casos`, tabela t18), discussão e agenda de pesquisa (Seção 8).
- Apêndices: A desvios; B método/hipóteses/testes de H1; C robustez e incerteza; D terceira dimensão.
- Casos descritos só com o que os registros da Câmara informam; sem reconstituir negociações.
- Seções 5.2, 5.3, 6 e 8 ainda não passaram pela verificação de integridade.

## Decisões e problemas conhecidos
- Escores numéricos do survey BRC não conferidos (scielo.br bloqueado): usamos codificação ordinal `CAMPO`.
- Bootstrap: réplicas reescaladas por fator isotrópico, introduzido ao notar ICs que não continham a estimativa pontual (causa: escala identificada só pelos priors; réplicas ~9% menores); ICs de
  correlações/R² ficam abaixo do ponto (réplicas mais ruidosas) — declarado no texto.
- Bug do 0D na CV: corrigido. Modo `TESTE_RAPIDO=<pasta>` para teste de fumaça.
- Citações em ABNT autor-data (o checkpoint propôs APA 7; trocado por convenção dos periódicos brasileiros).
- Seções a preencher pelos autores: autoria, CRediT, financiamento, conflito de interesses.
- Pendente opcional (Blueprint itens 4–5): IRT com efeito fixo partido×votação; replicação na 56ª Legislatura.
