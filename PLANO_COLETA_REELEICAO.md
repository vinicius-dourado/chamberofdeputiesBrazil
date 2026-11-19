# Plano de coleta – replicação de Pereira & Rennó (2001) sem pork barrel

Referência: Pereira, C. & Rennó, L. (2001). *O que é que o reeleito tem? Dinâmicas político-institucionais
locais e nacionais nas eleições de 1998 para a Câmara dos Deputados*. Dados, 44(2).
DOI 10.1590/S0011-52582001000200004.

Fora do escopo (pork barrel): `Emendas`, `Pork`, `MédiaExecução`, `TotalEmendas`.

## 1. Desenho

| Item | Escolha |
|---|---|
| Unidade | deputado (`id` da Câmara) que exerceu mandato na legislatura, titulares e suplentes (como no artigo) |
| Caso principal | 57ª legislatura (2023–2027) → eleição de 2026. `dados/leg57/` já existe |
| Caso de validação | 56ª legislatura (2019–2023) → eleição de 2022 (`python baixar_legislatura.py --legislatura 56`) |
| "Eleição anterior" (Concentração94, MesmaBase) | 2022 para o caso principal; 2018 para a validação |
| Chave Câmara ↔ TSE | CPF (campo `cpf` de `/deputados/{id}`, hoje descartado por `baixar_legislatura.py`) ↔ `NR_CPF_CANDIDATO`; fallback por nome de urna/nome civil + UF + data de nascimento |
| Saída | `dados/leg57/reeleicao_*.parquet` + uma tabela final `reeleicao_painel.parquet` (1 linha por deputado) |

Exclusões a replicar (nota 17 do artigo): quem saiu para prefeito/vereador em 2024, mortos, cassados, e
deputados do DF se a medida de base municipal não fizer sentido (DF tem um único "município").

## 2. O que já está no repositório (só calcular)

| Variável | Fonte no repo | Cálculo |
|---|---|---|
| **Projetos** | `proposicoes` + `proposicoes_autores` | nº de PL/PLP/PEC/PDL com `proponente=1` e `ultimoStatus_descricaoSituacao` = "Transformado em Norma Jurídica" (ou aprovado no Plenário; definir) |
| **Ausência** | `votos` + `votacoes` + `deputados_historico` | nº (e %) de votações nominais do Plenário (`siglaOrgao="PLEN"`, `tem_votos_nominais`) sem voto do deputado, contando só os dias em que ele estava em exercício |
| **Índice** (lealdade ao governo) | `votos.seguiu_orientacao_governo` | % de votos iguais à orientação do Governo, só em votações com orientação Sim/Não |
| **EntrarCoalizão / SairCoalizão** | `deputados_partidos` | troca de partido: destino na base do governo vs. na oposição. Precisa da tabela manual de partidos da base (§4) |
| Partido / UF / sexo / idade | `deputados` | controles |

## 3. Coleta nova – API/arquivos da Câmara (`dadosabertos.camara.leg.br`, host já liberado)

| Variável | Endpoint / arquivo | Observação |
|---|---|---|
| **Mesa** | `GET /legislaturas/{leg}/mesa` (tem `titulo`, `codTitulo`, datas) | escala ordinal: suplente de secretário < secretário < 2º vice < 1º vice < presidente; usar o maior cargo ocupado na legislatura |
| **Permanente / Especial** | arquivo `arquivos/orgaosDeputados/csv/orgaosDeputados-L{leg}.csv` (cargo e datas por órgão) + `GET /orgaos` (tipo do órgão) | separar comissões permanentes (`codTipoOrgao` permanente) e especiais/temporárias; escala: titular < vice-presidente < presidente |
| Relatorias (parte de Permanente/Especial) | arquivo `proposicoesTramitacoes-{ano}.csv` | extrair "Designado Relator, Dep. X" do despacho; **validar** o padrão do texto antes |
| **Partpos** | `GET /legislaturas/{leg}/lideres` (líder/vice-líder de partido, bloco, governo, oposição) | presidência nacional do partido não está na API: fica de fora ou vira coleta manual |
| **Senior** | `GET /deputados?idLegislatura=k` para k = 48 … leg−1 | nº de legislaturas anteriores em que o `id` exerceu mandato |
| **Burocracia / Empresa** | `GET /deputados/{id}/profissoes` e `/ocupacoes` | complementado pela ocupação declarada no TSE (§4); `/ocupacoes` vem quase sempre vazio |
| Licenças para cargo no Executivo (complemento de Burocracia) | `deputados_historico` (já existe) | status de afastamento para Ministro/Secretário durante o mandato |
| CPF | `GET /deputados/{id}` | só acrescentar o campo em `baixar_legislatura.py` |
| *(opcional)* presença em sessões | arquivo `eventosPresencaDeputados-{ano}.csv` | medida alternativa de Ausência |
| *(opcional, endógena)* **Líder** | não existe na Câmara | lista externa (ex.: "Cabeças do Congresso", DIAP). Só para os modelos auxiliares (Tab. 1 do artigo) |

`/deputados/{id}/mandatosExternos` existe, mas veio vazio para todos os deputados testados, então Histleg/Histexec vêm do TSE.

## 4. Coleta nova – TSE (`cdn.tse.jus.br`, `dadosabertos.tse.jus.br`, **hosts ainda bloqueados neste ambiente**)

Arquivos do Portal de Dados Abertos do TSE (`odsele`), por ano/UF:

| Variável | Arquivo TSE | Cálculo |
|---|---|---|
| **VD seleção: concorreu?** | `consulta_cand_2026` (todos os cargos) | categorias: dep. federal / estadual / senador / governador / não concorreu (candidatura deferida) |
| **VD resultado: reeleito?** | `consulta_cand_2026` ou `votacao_candidato_munzona_2026` (`DS_SIT_TOT_TURNO`) | 1 = "ELEITO POR QP" ou "ELEITO POR MÉDIA"; 0 = "SUPLENTE" ou "NÃO ELEITO" |
| **Concentração(t−1), Concentração(t)** | `votacao_candidato_munzona_2022` e `_2026` | somar zonas por município; votos no município de maior votação ÷ votos no estado |
| **Competição** | idem + `detalhe_votacao_munzona` ou `perfil_eleitorado` | no município de maior votação: votos próprios − votos do outro candidato a dep. federal mais votado ali, ÷ eleitorado do município (nota 7) |
| **MesmaBase** | idem 2022 × 2026 | dummy: o município de maior votação é o mesmo nas duas eleições |
| **Gastos(t−1), Gastos(t)** | `prestacao_de_contas_eleitorais_candidatos_2022` / `_2026` (despesas contratadas) | total declarado; versão per capita (÷ eleitorado da UF). Só descritivo, como no artigo |
| **Governador** | `consulta_coligacao_2022` + resultado de governador 2022 | dummy: partido/federação do deputado (na eleição de 2026 e/ou na de 2022) integra a coligação do governador eleito em 2022. Coligações proporcionais acabaram em 2020: comparar partido/federação |
| **Histleg / Histexec** | `consulta_cand_{ano}` para 1994–2024 (gerais e municipais) | contar eleições ganhas para vereador e dep. estadual (Histleg) e para prefeito, vice-prefeito, governador e vice (Histexec), antes da legislatura |
| **Burocracia / Empresa** | `DS_OCUPACAO` em `consulta_cand_2022` | Empresa = "EMPRESÁRIO"; Burocracia = ocupações de servidor público / cargo em comissão (definir a lista) |
| Ligação Câmara ↔ TSE | `consulta_cand_*` (`NR_CPF_CANDIDATO`, `NM_URNA_CANDIDATO`, `DT_NASCIMENTO`) | CPF primeiro; a partir de 2024 o TSE pode mascarar o CPF, e aí usar nome + data de nascimento + UF |

## 5. Tabelas manuais (fora das duas APIs)

| Tabela | Uso | Sugestão de fonte |
|---|---|---|
| Ideologia dos partidos (**Esquerda / Centro / Direita**) | dummies de ideologia | Bolognesi, Ribeiro & Codato (2023), survey de especialistas |
| Partidos da base do governo por período | EntrarCoalizão / SairCoalizão | partidos com ministérios no governo Lula 3 (datas de entrada/saída) |
| Partidos/federações por coligação de governador | Governador | sai do TSE (§4); só conferir federações |

## 6. Ordem de execução

1. Ajustar `baixar_legislatura.py` para gravar o `cpf`. Rodar `--legislatura 56` (caso de validação).
2. Novo `baixar_cargos.py` (Câmara): Mesa, órgãos/comissões, líderes, legislaturas anteriores, profissões. Saídas: `cargos_mesa`, `cargos_orgaos`, `cargos_lideres`, `senioridade`, `profissoes`.
3. Liberar `cdn.tse.jus.br` no ambiente. Novo `baixar_tse.py`: baixa os zips de §4 para `dados/brutos/tse/` (fora do git) e grava só os recortes em Parquet: candidatos que foram deputados federais, mais votos por município/candidato de dep. federal nas UFs.
4. `ligar_camara_tse.py`: tabela `id_camara ↔ sq_candidato/cpf` por eleição, com relatório dos casos não ligados.
5. `montar_painel.py`: calcula todas as variáveis → `reeleicao_painel.parquet`.
6. Conferências: % de deputados ligados ao TSE; nº de reeleitos contra o total oficial; distribuições de Concentração e Competição.

## 7. Riscos e pendências

* **Dados de 2026**: votação por município já deve estar publicada. A prestação de contas final (gastos) pode
  ainda estar incompleta. Se faltar algo, a 56ª/2022 vira o caso principal.
* CPF mascarado em arquivos recentes do TSE → a ligação fica por nome + data de nascimento.
* Relatorias dependem de parsing de texto de tramitação.
* A 57ª legislatura só termina em 31/01/2027. Ausência, Índice e Projetos devem ser cortados na data da eleição (04/10/2026).
* Volume: `votacao_candidato_munzona` e `consulta_cand` do Brasil inteiro passam de 1 GB descompactados. Ficam em `dados/brutos/` (já ignorado pelo `.gitignore`) e só os recortes vão para o git.
