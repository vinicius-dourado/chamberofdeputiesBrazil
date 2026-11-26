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

## Dados para modelos de reeleição (Pereira & Rennó 2007) – legislaturas 55, 56, 57 + TSE

Para replicar análises de sucesso eleitoral de deputados federais candidatos à reeleição
(eleições de 2018, 2022 e 2026), o repositório também traz as legislaturas 55 (2015–2019) e
56 (2019–2023), complementos da API da Câmara e dados do TSE.

```bash
python baixar_legislatura.py --legislatura 56      # idem 55; a 57 já está no repositório
python baixar_camara_complementar.py               # legislaturas 55, 56, 57 (~5 min cada)
python baixar_tse.py                               # TSE: gerais 2018/2022/2026, municipais 2020/2024 (~3 GB de ZIPs em cache)
```

### `baixar_camara_complementar.py` → `dados/leg<N>/`

| Tabela | Conteúdo | Uso no modelo |
|---|---|---|
| `deputados_complemento` | `cpf_hash` (chave para o TSE), nome civil, nascimento, legislaturas anteriores em exercício | Sênior; ligação Câmara↔TSE |
| `deputados_orgaos` | participação em órgãos na legislatura (cargo, tipo: Mesa, comissão permanente, especial, CPI...) | Mesa Diretora, C. Permanente, C. Especial |
| `deputados_mandatos_externos` | mandatos fora da Câmara (vereador, prefeito, dep. estadual, governador...) | Hist. Legislativo / Executivo |
| `deputados_ocupacoes`, `deputados_profissoes` | ocupações e profissões declaradas | Empresário |
| `lideres` | líderes/vice-líderes de partidos, blocos, Governo, Maioria, Minoria, Oposição, com período | Posição no partido |
| `mesa` | composição da Mesa Diretora com período | Mesa Diretora |

### `baixar_tse.py` → `dados/tse/`

| Tabela | Conteúdo |
|---|---|
| `candidatos_gerais` | todas as candidaturas de 2018, 2022 e 2026 (todos os cargos), situação final (`eleito`), ocupação, partido |
| `candidatos_municipais` | candidatos a prefeito/vice em 2020 e 2024 (variável Prefeito) |
| `votacao_depfed_municipio` | votos de cada candidato a dep. federal por município |
| `depfed_resumo` | um candidato a dep. federal por linha: votação, município-reduto, `concentracao` (votos no reduto / total), `dominancia_reduto`, `dominancia_media` (Ames), HHI, nº de candidatos na UF, receitas por fonte (FEFC, fundo partidário, próprios, pessoas físicas...) e despesas contratadas/pagas |

**Ligação Câmara↔TSE:** `deputados_complemento.cpf_hash` = `candidatos_gerais.cpf_hash`
(cobertura de 100% dos deputados). Para não republicar CPFs de candidatos, as tabelas guardam
apenas o SHA-256 do CPF (16 primeiros hex); título de eleitor não é mantido.

Exemplo – variável dependente para 2022 (deputados da leg. 56):
```python
import pandas as pd
dep = pd.read_parquet("dados/leg56/deputados_complemento.parquet")
cand = pd.read_parquet("dados/tse/candidatos_gerais.parquet").query("ANO_ELEICAO == '2022'")
base = dep.merge(cand, on="cpf_hash", how="left")
reeleicao = base[base["DS_CARGO"].str.upper() == "DEPUTADO FEDERAL"]   # 503 tentaram; 298 reeleitos
```
