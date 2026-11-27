# CLAUDE.md: convenções do repositório chamberofdeputiesBrazil

Dados da Câmara dos Deputados (legislaturas 53–57, 2007–2026) e do TSE, usados na pesquisa de mestrado de Vinicius (PPGCP/UnB) sobre **emendas parlamentares e gestão de coalizão**. Escreva código, comentários, commits e documentos em **português**.

## Estrutura

| Caminho | O quê |
|---|---|
| `baixar_*.py`, `obter_*.py` (raiz) | Coleta. Geram `dados/legNN/*.parquet`, `dados/tse/`, `dados/executivo/`. Não edite os parquets à mão: corrija o script e regenere. |
| `dados/legNN/` | Votos, votações, orientações, líderes, Mesa, deputados (com `deputados_exercicio`), proposições e autores. |
| `dados/tse/` | Candidatos (gerais e municipais), votação por município, resumo do deputado federal (concentração, HHI, receitas). |
| `dados/executivo/` | Proposições do Executivo desde 2007, com tramitações e relacionadas. |
| `dados/gabinetes/` | Ministros por partido de Sarney a Lula 3 e índice de proporcionalidade (L5). Ver o README da pasta. |
| `dados/emendas/` | **Lacuna L6, ainda vazia.** Esquema esperado em `analises/comum/emendas.py`. |
| `docs/desenhos-de-pesquisa-fronteiras.md` | Os dez desenhos de pesquisa. É a referência conceitual de `analises/`. |
| `analises/comum/` | Painéis e funções compartilhadas (P1–P4, gabinetes, TSE, emendas, estimação). |
| `analises/<desenho>/` | Uma pasta por desenho: `PREREG.md`, `paineis.py`, `estimacao.py`, `test_validacao.py`. |
| `artigos/` | Artigos já em andamento (por exemplo, `02-disciplina-intrapartidaria`). |

Rode tudo **da raiz**: `python -m analises.6c2a_pastas_set2023.paineis` não funciona porque o nome começa com dígito. Use `python analises/6c2a_pastas_set2023/paineis.py`. Testes: `pytest analises`.

## Regras de pesquisa (obrigatórias)

1. **Pré-registro antes do resultado.** Antes de rodar `estimacao.py` com dados reais, o `PREREG.md` do desenho precisa estar fechado e commitado. O hash do commit vai no cabeçalho de `resultados/`. Mudança posterior na especificação principal vira seção "Desvios do pré-registro" no `PREREG.md`, com data e motivo. Nunca apague um desvio.
2. **Testes não olham o resultado.** `test_validacao.py` testa a integridade dos painéis e se o estimador recupera um efeito conhecido em **dados sintéticos**. Nenhum teste pode imprimir ou afirmar coeficientes estimados com dados reais.
3. **Fatos institucionais** (datas de ECs, decisões do STF, posses) ficam em `analises/comum/config.py`, com a fonte. Datas marcadas `verificar=True` não entram em especificação principal até serem conferidas.
4. Toda escolha de codificação que afete resultados (classificação de partido, janela, limiar) é uma **constante nomeada** em `config.py` ou no topo do script, nunca um número solto.

## Convenções de medida

**Votos.** Valores válidos: Sim, Não, Obstrução, Abstenção. "Artigo 17" (o presidente da sessão não vota) e voto vazio saem. Na medida direcional, Obstrução = Não.

**Orientação do governo** (`comum.p1.orientacao_governo`), nesta ordem:
1. `votos.orientacao_governo` (oficial; a Câmara usou `GOV.` até 2022 e `Governo` depois);
2. `votacoes_orientacoes` com `siglaBancada` ∈ {Governo, GOV.};
3. voto do Líder do Governo na CD (`lideres`, `bancada_nome == 'Governo na CD'`, `titulo == 'Líder'`, vigente na data);
4. moda dos vice-líderes do governo que votaram.

A coluna `fonte_orient_gov` guarda o nível usado. A especificação principal usa só os níveis 1 e 2; os níveis 3 e 4 entram como robustez. Validação: concordância do Líder com a orientação oficial de 99,4% (leg56) e 98,6% (leg57).

**Votação com orientação divergente:** o partido do deputado e o governo orientaram ambos Sim ou Não, e em sentidos opostos. É a amostra principal de todo desenho sobre disciplina governista.

**Base do governo na data** (`comum.gabinetes.base_na_data`): linhagens partidárias com ao menos uma pasta, depois das convenções de `dados/gabinetes/README.md`. A oposição declarada (PL e NOVO no Lula 3) nunca entra como controle de "base".

**Siglas.** `comum.siglas.normalizar` converte grafias (União → UNIÃO, REP → REPUBLICANOS…). `comum.siglas.linhagem` dá continuidade a renomeações (PMDB → MDB, PR → PL, PRB → REPUBLICANOS, PPS → CIDADANIA…). Fusões (DEM + PSL → UNIÃO) **não** são linhagem: trate-as explicitamente.

**Cadeiras e presença:** `deputados_exercicio` (em exercício na data). Ausência = em exercício e sem voto registrado.

**Ligação Câmara ↔ TSE:** `cpf_hash`. Para candidaturas de 2024, o TSE mascarou o CPF; use `nome_nasc_hash`, que concorda com o CPF em 97–98% dos casos anteriores. Sempre relate a taxa de ligação.

**Emendas (L6):** autor ↔ deputado por nome normalizado e UF, com os ambíguos validados à mão (lista em `dados/emendas/ligacao_manual.csv`). Valores deflacionados pelo IPCA e normalizados pela despesa discricionária do ano.

## Estimação

- `pyfixest` para efeitos fixos de alta dimensão. Painel deputado × votação: efeitos fixos de deputado e de votação, erros agrupados **por deputado e por votação** (`vcov={"CRV1": "deputado_id+idVotacao"}`).
- Estudos de evento: tendências pré-choque sempre reportadas; janelas fixadas no `PREREG.md`.
- Sementes fixas (`config.SEMENTE`). Resultados em `analises/<desenho>/resultados/` (JSON com NaN → null, tabelas em Markdown).

## Git

- Trabalhe em branch; nunca commite direto no `master`.
- Não versione dados brutos nem CSVs grandes (`.gitignore` já exclui `dados/**/*.csv`). Painéis derivados vão para `analises/**/cache/`, também ignorado.
