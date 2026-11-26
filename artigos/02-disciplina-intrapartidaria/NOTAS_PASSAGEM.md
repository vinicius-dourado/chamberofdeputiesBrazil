# Notas de passagem — Artigo 2 (disciplina partidária e variação intrapartidária)

## Estado
- O manuscrito está em `artigo.md`, **gerado** por `analise.py` a partir de `artigo_fonte.md`. Edite sempre `artigo_fonte.md`: cada número é um marcador `{{fmt:chave}}` que vem de `resultados.json`.
- `python artigos/02-disciplina-intrapartidaria/analise.py` (da raiz do repositório) leva cerca de 11 min sem cache e cerca de 3 min com o cache de IRT em `dados_aux/cache/` (fora do git). O script gera `resultados.json`, `tabelas/`, `figuras/` e `artigo.md`.
- O pipeline ARS (plugin Academic Research Skills, executado a partir dos arquivos do repositório `imbad0202/academic-research-skills`, porque o plugin não estava instalado na sessão) tem os registros em `pipeline/`:
  - Stage 1: `stage1_blueprint.md` (research_architect) e `stage1_bibliografia.md`.
  - Stage 2.5: `stage2_5_integridade.md`, três rodadas, a última PASS WITH NOTES.
  - Stage 3: `stage3_revisao.md`, Major.
  - Stage 4: `stage4_resposta.md` e `stage4_bibliografia.md`.
  - Stage 3': `stage3b_rerevisao.md`, Major com um único item obrigatório, R-1.
  - Stage 4': commit 0467017.
  - Stage 4.5: `stage4_5_integridade_final.md`.
- O usuário autorizou seguir sem parar nos checkpoints ("pode seguir direto").

## Achados principais
- O registro de orientações é de bloco para o centro. Em 2025, o megabloco PL + federação do PT deixou o registro quase vazio, mas as transcrições mostram que os partidos orientaram. D sobe em 2025 por artefato; U cai no centro (PSD, MDB, PP, União).
- D = 90,9% e U = 89,5%. A indisciplina tem estrutura pequena: M2b→M3 = 0,006, com IC acima de zero. A dimensão é o eixo governo–oposição dentro do partido.
- A distância espacial ao partido (medida no outro biênio) domina os correlatos do desvio. Depois da troca de partido, o desvio em relação aos novos colegas cai (6,5 p.p. na coorte de 2026); os dados são compatíveis com seleção e com ajuste.
- Partido × Governo: o excesso de lealdade ao partido fica entre 4,2 e 17,1 p.p., conforme o contrafactual.

## Pendências
- Marcas [verificar]: páginas de Nicolau (2000), porque o SciELO está bloqueado; lista completa de instrumentos em Figueiredo e Limongi (1999); datas finas da base ministerial.
- Validação temporal dos pontos ideais: o estimador do projeto não permite fixar pontos.
- Composição oficial dos blocos: não está nos Dados Abertos baixados.
- Reconstrução sistemática das orientações faladas: a extração atual capta só a fórmula "o X orienta/vota 'y'".
- Para submissão: DOI do repositório de código e dados.

## Avisos herdados
- `deputados.parquet/siglaPartido` é o partido atual (pós-janela de 2026). Use o partido na data.
- As visões de discursos em `embeddings_deputados.py` vazam o sexo do deputado; este artigo não as usa.
