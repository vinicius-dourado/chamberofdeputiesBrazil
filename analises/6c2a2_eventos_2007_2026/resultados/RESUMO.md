# 6-c.2a-ii: resultados da estimação pré-registrada

**Rodada:** 27/11/2026, com o pré-registro fechado no commit `ed3f8f1`. Números completos em `resultados.json`.
**Amostra:** 17 eventos (9 entradas e 8 saídas, de 2007 a 2026), 993 mil observações deputado × votação × evento.
**Desfecho:** Y1, o deputado seguiu o governo (1/0). Efeitos em pontos percentuais (pp).
**Critério de leitura:** o do `PREREG.md`. Para confirmar um efeito é preciso:
- p < 0,05 no erro agrupado duplo;
- p < 0,10 no placebo;
- teste de pré-tendência do tipo de evento com p > 0,10.

## Resultado principal

| | β | EP | IC 95% | p (duplo) | Placebo (30 sorteios) | Pré-tendência |
|---|---|---|---|---|---|---|
| Entrada (H1) | **+0,1 pp** | 0,9 | −1,6 a +1,8 | 0,87 | p = 0,97 | p = 0,076 |
| Saída (H2) | **−2,6 pp** | 1,7 | −5,9 a +0,7 | 0,12 | p = 0,55 | **p = 0,004** |
| Soma (H3, simetria) | −2,5 pp | 1,9 | −6,1 a +1,2 | 0,18 | | |

## Veredito pelo pré-registro

- **H1 (entrar aumenta o apoio):** **não identificada**, porque a pré-tendência foi rejeitada no limiar de 10% (p = 0,076). A estimativa é praticamente zero e o intervalo é estreito.
- **H2 (sair diminui o apoio):** **não identificada**, por pré-tendência forte (p = 0,004).
- **H3 (simetria):** não rejeitada (p = 0,18). Com um intervalo de −6 a +1 pp, a falta de rejeição informa pouco.

## O que os dados mostram, além do veredito formal

**1. Nas saídas, o apoio cai antes de a pasta ser perdida.** No estudo de evento das saídas, o apoio dos tratados já está abaixo do dos controles:
- 3 meses antes da saída: −9,2 pp (EP 3,3);
- 2 meses antes: −8,1 pp (EP 3,0).

Depois da saída, a queda continua, mas não se aprofunda de forma clara. **A saída do gabinete registra um afastamento que já tinha acontecido.** É a assinatura da história "a pasta registra o apoio", não da história "a pasta causa o apoio".

Há também uma leitura de **datação**: a ruptura política (anúncio, entrega de cargos, mudança de orientação) vem antes da exoneração formal, que é a data usada aqui. Nas duas leituras, o status ministerial acompanha o apoio, e não o contrário.

**2. Nas entradas, não há efeito médio.** As estimativas por evento são heterogêneas e mudam de sinal:
- de −9,1 pp (PL 2013) a +6,1 pp (PSD 2013);
- em 2021: Republicanos +4,0 (p = 0,018), PL −3,4 (p = 0,009), PP −0,6.

Retirar qualquer evento mantém β_entrada entre −0,7 e +1,5 pp. Nenhum evento sozinho produz o resultado.

**3. A entrada do PP em 2023, vista pela regra geral, fica menor.** No 6-c.2a, com MDB, PSD e União como controles (partidos já na base), o efeito era +4,9 pp. Aqui, com controles fora da base (PL, Novo, Republicanos, PSDB…), é +2,0 pp (p = 0,51). O efeito de 2023 depende do grupo de comparação.

## Robustez

| | Entrada | Saída |
|---|---|---|
| Controles com todos os partidos estáveis | +1,2 (p = 0,15) | −2,7 (p = 0,023) |
| Orientação com proxy do Líder do Governo | −0,4 (p = 0,60) | −3,1 (p = 0,072) |
| Só votações de mérito | −0,2 (p = 0,86) | −2,9 (p = 0,22) |
| Janela de ±3 meses | +1,3 (p = 0,20) | −0,8 (p = 0,73) |

Na saída, a estimativa fica significativa com todos os controles. Ela some na janela curta (±3 meses), coerente com uma queda que já tinha acontecido antes da janela de comparação.

## Leitura em relação ao problema de pesquisa

A pergunta era se a associação clássica entre ter pasta e votar com o governo é causal ou é seleção. Com 17 eventos e cinco governos, **não aparece efeito causal de ganhar pasta**. Nas saídas, o apoio cai **antes** da perda da pasta. Os dois resultados são mais compatíveis com a hipótese de **seleção**: a pasta acompanha o alinhamento do partido em vez de produzi-lo. Pelos critérios pré-registrados, porém, nenhum dos dois efeitos é identificado, então a conclusão fica no nível de padrão consistente, não de teste confirmado.

## Limites

- **Eventos fora da estimação pela regra:** PDT 2007, PTB 2018, PSL 2019 e as 5 saídas do impeachment de 2016, todas por falta de votações ou de controles. O impeachment, o caso mais relevante para a pergunta, não é estimável com esta regra.
- **Placebo:** duas entradas (Republicanos 2007 e União 2025) não tinham datas fictícias possíveis no mesmo governo e ficaram fora dos sorteios.
- **Codificação do Ipea:** os ministros de Bolsonaro de 2019 contam como sem partido. As entradas de 2021 têm controles muito heterogêneos, que incluem a oposição de esquerda.
- **Pacote:** entrar no governo envolve mais que o ministério. O β mede o pacote, não a pasta isolada.

## Notas de implementação (sem mudança de especificação)

- O painel é enxugado (só as colunas usadas, ids como inteiros) para caber na memória da máquina (7 GB).
- Uma rodada de teste com 2 placebos foi feita só para verificar o código, e os coeficientes não foram lidos. Foi sobrescrita pela rodada com 30 placebos.
