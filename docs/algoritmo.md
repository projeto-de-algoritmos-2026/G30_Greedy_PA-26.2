# Knapsack Fracionário e análise de complexidade

## Aplicação no TrailPack

O TrailPack utiliza o algoritmo guloso de **Knapsack Fracionário** para
maximizar a utilidade dos recursos divisíveis dentro do limite de peso da
mochila. A implementação está em
[`fractional_knapsack`](../src/knapsack.py).

Antes da otimização, o serviço de
[`recomendação`](../src/recommendation.py) calcula as prioridades contextuais e
reserva o peso dos itens essenciais. Equipamentos indivisíveis selecionados
explicitamente pelo usuário também têm seu peso reservado. Esses itens não
participam da escolha fracionária.

```text
Capacidade restante = capacidade total - peso dos itens reservados
```

Se os itens reservados excederem a capacidade, o sistema informa um erro.
O algoritmo recebe somente os recursos divisíveis ainda disponíveis e a
capacidade restante, já descontada a reserva.

## Representação do problema

Para cada recurso `i`, os campos do modelo `Item` representam:

- `peso` (`p_i`): peso de uma unidade, em kg, estritamente positivo;
- `valor_base` (`v_i`): utilidade de uma unidade. Nas cópias enviadas pelo
  motor de prioridades, esse campo contém a utilidade contextual;
- `quantidade_padrao` (`q_i`): quantidade disponível, que pode ser fracionária.

Se `x_i` for a quantidade selecionada e `C` a capacidade restante:

```text
Maximizar: soma(v_i × x_i)
Sujeito a: soma(p_i × x_i) <= C
           0 <= x_i <= q_i
```

Peso e utilidade crescem linearmente com a quantidade. A razão utilizada
para ordenar os recursos é:

```text
razão_i = v_i / p_i
```

Ela mede a utilidade por quilograma. A quantidade disponível limita o quanto
pode ser levado, mas não altera essa razão por unidade.

## Etapas do algoritmo

1. Validar a capacidade e os recursos. A capacidade deve ser finita e não
   negativa; os elementos devem ser `Item` divisíveis. O modelo `Item` já
   valida peso positivo e valores e quantidades finitos e não negativos.
2. Ignorar recursos com quantidade disponível ou utilidade igual a zero.
3. Calcular `valor_base / peso` e ordenar os recursos em ordem decrescente.
4. Percorrer essa ordem e selecionar toda a quantidade disponível quando
   seu peso total couber na capacidade restante.
5. Quando um recurso não couber inteiro, selecionar apenas
   `capacidade restante / peso por unidade` e encerrar o preenchimento.

Empates na razão preservam a ordem de entrada. O algoritmo devolve uma tupla
de cópias dos itens, na ordem de seleção, com `quantidade_padrao` representando
a quantidade efetivamente selecionada. O catálogo original não é alterado.

### Pseudocódigo

```text
validar capacidade e recursos
recursos úteis = recursos com quantidade > 0 e valor > 0
ordenar recursos úteis por valor/peso, em ordem decrescente
restante = capacidade
selecionados = lista vazia

para cada recurso na ordem:
    se restante <= 0:
        encerrar
    se peso × quantidade disponível <= restante:
        selecionar toda a quantidade disponível
        restante -= peso × quantidade disponível
    senão:
        selecionar restante / peso unidades
        encerrar

retornar os itens com suas quantidades selecionadas
```

## Por que a escolha gulosa é ótima?

Suponha que uma solução use peso de um recurso de menor razão enquanto
ainda existe quantidade disponível de outro com maior razão. Como os
recursos são divisíveis, é possível trocar uma porção de mesmo peso pelo
recurso de maior razão. A capacidade permanece respeitada e a utilidade
aumenta. Se as razões forem iguais, a troca mantém a utilidade.

Assim, existe uma solução ótima que consome primeiro os recursos de maior
utilidade por kg, exatamente como faz o algoritmo guloso. Quando não há
espaço para o recurso seguinte inteiro, a fração selecionada aproveita a
capacidade restante sem ultrapassá-la.

Essa garantia vale para o **subproblema fracionário**, com utilidade linear,
recursos independentes, limites de estoque e uma restrição de peso. Não
resolve a seleção ótima de equipamentos indivisíveis nem estabelece
quantidades mínimas de hidratação ou alimentação.

## Exemplo de execução

Considere três recursos divisíveis com uma unidade disponível de cada um e
capacidade restante de **50 kg**. São valores didáticos, não um catálogo real.

| Recurso | Valor por unidade | Peso por unidade (kg) | Valor/Peso | Quantidade selecionada |
| --- | --- | --- | --- | --- |
| A | 60 | 10 | 6 | 1 |
| B | 100 | 20 | 5 | 1 |
| C | 120 | 30 | 4 | 2/3 |

A ordenação é `A → B → C`. Após selecionar A e B, restam 20 kg. O recurso C
ocuparia 30 kg; por isso, apenas `20 / 30 = 2/3` de sua unidade é selecionado.

```text
Peso selecionado = 10 + 20 + (2/3 × 30) = 50 kg
Utilidade total = 60 + 100 + (2/3 × 120) = 240 pontos
```

Esse resultado ótimo conhecido é verificado nos
[`testes do Knapsack`](../tests/test_knapsack.py).

## Análise de complexidade

Seja `n` o número de recursos recebidos por `fractional_knapsack`. Considere
operações numéricas e acesso aos campos de `Item` com custo constante.

| Etapa | Tempo no pior caso | Motivo |
| --- | --- | --- |
| Materialização e validação da entrada | O(n) | Cada recurso é lido e validado uma vez |
| Filtragem e cálculo das razões | O(n) | Uma verificação e uma divisão por recurso útil |
| Ordenação | O(n log n) | Ordenação por comparação das razões |
| Seleção | O(n) | Uma passagem, sem revisitar recursos |
| Construção do retorno | O(n) | No máximo uma cópia e uma posição no resultado por recurso |

Portanto, a **ordenação custa O(n log n)** e a **seleção custa O(n)**.
A ordenação domina a soma dos custos:

```text
Tempo total no pior caso = O(n) + O(n log n) + O(n)
                        = O(n log n)
```

A seleção pode terminar antes de visitar todos os recursos, mas isso não
elimina o custo da ordenação, realizada previamente. Mesmo com capacidade
zero, a implementação atual materializa, valida, filtra e ordena a entrada
antes de interromper a seleção.

Se somente `k` dos `n` recursos tiverem quantidade e utilidade positivas,
uma descrição mais precisa é `O(n + k log k)`. Quando não há recursos úteis,
a entrada ainda é percorrida, com custo O(n).

O **espaço adicional é O(n)**: a implementação materializa a entrada,
mantém a lista ordenada e constrói os itens selecionados e a tupla de retorno.

### Custo da recomendação completa

Para `m` itens disponíveis, incluindo equipamentos, calcular prioridades,
separar os essenciais e somar o peso reservado custa O(m). Se `n` desses
itens forem recursos enviados ao Knapsack, a recomendação custa
**O(m + n log n)**, ou **O(m log m)** no pior caso em que `n` cresce com `m`.
Essa análise se refere ao processamento da recomendação, sem contabilizar
renderização da interface ou leitura de arquivos.
