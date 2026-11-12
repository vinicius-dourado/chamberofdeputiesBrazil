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
