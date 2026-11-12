# chamberofdeputiesBrazil

This pool of files are some extractors that access Brazilian PArlament's web services and get all the projects, speechs, transcriptions, deputie's data and so on.

In the file categorizacao_automatica.py, the aim is read all the speechs and classify the deputy with the themes that they are more related with.


## Legislatura atual (57ª, 2023–2027) – `baixar_legislatura.py`

Baixa os dados da legislatura atual da API e dos arquivos em massa de
[Dados Abertos da Câmara](https://dadosabertos.camara.leg.br/swagger/api.html)
e gera tabelas em `dados/leg57/` (Parquet versionado no repositório; CSV `;`/UTF-8 gerado localmente).

```bash
pip install pandas requests pyarrow
python baixar_legislatura.py                  # legislatura atual (~3 min)
python baixar_legislatura.py --legislatura 56 # outra legislatura
```

| Tabela | Conteúdo | Chaves |
|---|---|---|
| `deputados` | todos os deputados que exerceram mandato na legislatura (titulares e suplentes), partido/UF atuais, situação, dados pessoais | `id` |
| `deputados_partidos` | períodos de filiação partidária de cada deputado dentro da legislatura (mudanças de partido) | `id` |
| `deputados_historico` | histórico bruto de status (posse, licença, mudança de partido...) | `id` |
| `partidos` | partidos com representação, nº de membros e líder | `id`, `sigla` |
| `proposicoes` | proposições apresentadas na legislatura com ao menos um deputado como autor | `id` |
| `proposicoes_autores` | autoria (deputado, ordem de assinatura, `proponente`) | `idProposicao`, `idDeputadoAutor` |
| `proposicoes_temas` | temas atribuídos pela Câmara a cada proposição | `idProposicao` |
| `deputados_temas` | resumo: nº de proposições por deputado × tema | `idDeputadoAutor` |
| `frentes` | frentes parlamentares da legislatura | `id` |
| `frentes_deputados` | membros de cada frente e cargo (coordenador, membro...) | `idFrente`, `deputado_id` |
| `votacoes` | todas as votações (plenário e comissões): data, órgão, descrição, resultado, objeto votado e proposição(ões) afetada(s) | `idVotacao` |
| `votacoes_orientacoes` | orientações das lideranças (partidos, federações, blocos, Governo, Maioria, Minoria, Oposição) | `idVotacao` |
| `votos` | voto nominal de cada deputado + proposição + orientação do seu partido/bloco e do Governo | `idVotacao`, `deputado_id` |

### Observações sobre `votos`

* `proposicao_titulo` (ex.: `PL 1604/2022`) é a proposição afetada pela votação; o texto da votação,
  ementas e o objeto votado (requerimento, emenda, destaque...) estão em `votacoes` (join por `idVotacao`).
* `orientacao_partido` é a orientação da bancada que representa o partido do deputado **na data da votação**:
  o próprio partido → a federação que o contém → o bloco que o contém (`orientacao_bancada`/`orientacao_fonte`).
* A Câmara publica nomes de blocos abreviados e truncados (ex.: `Bl UniPpFdrPsdbCid...`). Os partidos que
  votaram sem orientação própria e fora de outra bancada são atribuídos ao bloco truncado
  (`orientacao_fonte = "bloco (inferido)"`).
* Orientação vazia = a liderança não orientou. `seguiu_orientacao_*` só é preenchido quando a orientação foi
  Sim/Não/Obstrução/Abstenção (não para "Liberado").
* Só há votos individuais em votações nominais (`votacoes.tem_votos_nominais`); as demais são simbólicas.

## Discursos – `baixar_discursos.py`

Baixa todos os discursos dos deputados da legislatura (`/deputados/{id}/discursos?idLegislatura=N`),
com sumário, palavras-chave e **transcrição completa**. Roda depois de `baixar_legislatura.py`
(usa `deputados_partidos` para registrar o partido do deputado na data do discurso).

```bash
python baixar_discursos.py                 # ~8 min; retoma de onde parou se interrompido
python baixar_discursos.py --atualizar     # ignora o cache e baixa tudo de novo
```

| Tabela | Conteúdo | Chaves |
|---|---|---|
| `discursos` | um discurso por linha: deputado, partido/UF na data, data/hora, tipo (Pela ordem, Breves comunicações, Como líder...), fase da sessão, `keywords`, `sumario`, `transcricao`, `urlTexto` | `id_discurso`, `deputado_id` |

## Embeddings dos deputados – `embeddings_deputados.py`

Representa cada deputado por vetores, um por **aspecto**, e mede a proximidade entre deputados em cada
aspecto e no conjunto. Saídas em `dados/leg57/embeddings/`.

```bash
pip install scikit-learn scipy sentence-transformers
python embeddings_deputados.py                     # tudo (discursos: ~30 min em CPU na 1ª vez)
python embeddings_deputados.py --aspectos nada --consultar "Tabata" --aspecto media
```

| Arquivo | Aspecto | Técnica |
|---|---|---|
| `emb_votos` | votações nominais | pontos ideais (IRT 2D, família IDEAL/NOMINATE); `dim1` = governo (+) × oposição (−), `dim2` = oposição ideológica (+) × centrão (−) |
| `emb_votos_intra` | votações, **dentro do partido** | mesmo modelo com efeito fixo partido×votação e pontos centrados no partido: só a variação individual |
| `emb_temas` | temas das proposições | perfil temático (autoria fracionada, projetos com peso maior), embedding de Hellinger |
| `emb_frentes` | frentes parlamentares | TF-IDF (coordenador com peso 3) + SVD 16D |
| `emb_discursos_tema` | discursos: assunto | `multilingual-e5-small` sobre sumário + palavras-chave, média por deputado, PCA 32D |
| `emb_discursos_fala` | discursos: palavras do deputado | idem sobre a transcrição (primeiros 256 tokens) |
| `trajetoria_partidaria` | troca de partido | sequência de partidos, deslocamento do ponto ideal entre partidos, "salto" ideológico |
| `alinhamento` | disciplina | taxa de votos seguindo a orientação do partido e do Governo |
| `similaridades` | pares de deputados | `prox_<aspecto>` = percentil de proximidade (1 = par mais próximo), `prox_media`, `prox_snf` (Similarity Network Fusion) |
| `avaliacao.json` | qualidade | acurácia em votos fora da amostra; quanto cada aspecto recupera partido e posição de voto |

Coluna `confiavel` indica deputados com dados suficientes no aspecto (ex.: ≥ 50 votos, ≥ 10 discursos).

**Validação (57ª legislatura):** em 10% dos votos fora do ajuste, o modelo de pontos ideais acerta 91,9%
(seguir a orientação do partido: 84,4%; maioria da votação: 74,8%). O quanto cada aspecto prevê a posição
governo×oposição (R², validação cruzada): frentes 0,85; discursos 0,37–0,39; temas 0,30; votos intrapartidários
0,22 (não recupera o partido: acerto ≈ acaso, como esperado).

## Painel interativo – `gerar_painel.py`

`python gerar_painel.py` lê `dados/leg57/embeddings/` e o modelo `painel/modelo.html` e gera
`painel/painel.html`: página única com o mapa ideológico, ficha de cada deputado (alinhamento, temas,
deputados mais parecidos por aspecto), coesão dos partidos, pivôs e dissidentes, trocas de partido,
temas por lado e pares que falam parecido e votam diferente.
