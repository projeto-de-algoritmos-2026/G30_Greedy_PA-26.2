# Cenários de uso e resultados

Resultados simulados reproduzidos em 04/10/2026, com o catálogo de
`data/items.json`, os cenários de `data/scenarios.json` e as regras atuais do
motor de prioridades. Não são medições de trilhas reais nem recomendações
profissionais de segurança.

## Reprodução

Na raiz do projeto, com as dependências instaladas:

```bash
python -m scripts.reproduce_results
python -m pytest -q
```

O script usa a seleção inicial da interface: todos os essenciais e recursos
divisíveis, sem equipamentos opcionais nem itens personalizados. As quantidades
são as do catálogo, para uma pessoa. Os quatro equipamentos reservados são
kit de primeiros socorros (0,4 kg), capa de chuva (0,3 kg), lanterna (0,2 kg)
e apito (0,02 kg): **0,92 kg** em todos os cenários.

Valores são calculados sem arredondamento intermediário. As tabelas apresentam
peso com três casas e pontuação com duas; a interface resume a utilidade da
recomendação em pontos inteiros, enquanto o desafio usa duas casas.

## Condições de entrada

| Cenário | km | Horas | °C | Dificuldade | Chuva | Isolamento | Água no percurso | Capacidade (kg) |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | ---: |
| Rota do sol | 8 | 3 | 32 | Baixa | Baixa | Baixo | Não | 4 |
| Além do horizonte | 20 | 8 | 30 | Alta | Baixa | Alto | Não | 5 |
| Serra gelada | 12 | 5 | 5 | Média | Baixa | Médio | Sim | 6 |
| Caminho das águas | 10 | 4 | 19 | Média | Alta | Médio | Sim | 4,5 |

## Mochilas calculadas

Além dos quatro essenciais, o algoritmo selecionou:

| Cenário | Água (L) | Alimentos (kg) | Isotônico (L) | Mistura energética (kg) | Peso total (kg) | Sobra (kg) | Utilidade total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rota do sol | 3 | 0 | 0,08 | 0 | 4,000 | 0,000 | 984,08 |
| Além do horizonte | 3 | 0 | 1 | 0,08 | 5,000 | 0,000 | 1585,97 |
| Serra gelada | 3 | 1,4 | 0,38 | 0,3 | 6,000 | 0,000 | 932,45 |
| Caminho das águas | 3 | 0,28 | 0 | 0,3 | 4,500 | 0,000 | 820,61 |

No catálogo usado, cada unidade de consumível pesa 1 kg. A utilidade total
inclui os equipamentos reservados e os consumíveis. Não se deve interpretar
uma pontuação maior entre cenários diferentes como uma mochila mais segura:
as condições mudam os valores utilizados no cálculo.

## Caso detalhado: Além do horizonte

Na hidratação, calor, trilha longa e ausência de água multiplicam a utilidade
por `1,4 × 1,3 × 1,5 = 2,73`. A duração e a distância longa ativam uma única
regra, sem contar o fator 1,3 duas vezes. Na alimentação, a trilha longa e a
alta dificuldade produzem `1,3 × 1,3 = 1,69`.

Depois da reserva de 0,92 kg, restam **4,08 kg**. A ordem gulosa é:

| Recurso | Utilidade/unidade | Peso/unidade (kg) | Utilidade/kg | Estoque | Seleção |
| --- | ---: | ---: | ---: | ---: | ---: |
| Água | 273,00 | 1 | 273,00 | 3 | 3 |
| Isotônico | 163,80 | 1 | 163,80 | 1 | 1 |
| Mistura energética | 152,10 | 1 | 152,10 | 0,3 | 0,08 |
| Alimentos fracionáveis | 135,20 | 1 | 135,20 | 1,4 | 0 |

Os equipamentos somam **591,00 pontos**. Os consumíveis somam
`3 × 273 + 1 × 163,8 + 0,08 × 152,1 = 994,968`.
A soma é **1585,968**, exibida como **1585,97** no relatório.

## Desafio: jogador versus algoritmo

No mesmo cenário, mantenha os equipamentos e informe no desafio:

- Água: 2 L;
- Alimentos fracionáveis: 1 kg;
- Isotônico: 0,5 L;
- Mistura energética: 0,3 kg.

| Medida | Jogador | Algoritmo |
| --- | ---: | ---: |
| Peso (kg) | 4,720 | 5,000 |
| Pontos, incluindo equipamentos | 1399,73 | 1585,97 |
| Eficiência relativa | 88,26% | 100% |

A eficiência é `1399,73 / 1585,968 × 100`. As duas soluções usam o mesmo
estoque, a mesma capacidade e os mesmos equipamentos reservados. A estratégia
manual deixa 0,28 kg livres e distribui mais peso a recursos de menor razão.
Copiar as quantidades da solução gulosa permite atingir 100%.

## Casos de limite verificados

Os testes de integração cobrem um ótimo conhecido após a reserva dos
essenciais, inversão de prioridade pelo calor, essencial divisível reservado
uma única vez, capacidade preenchida apenas por essenciais, estoque vazio,
quantidade zero, utilidade zero, capacidade insuficiente, equipamentos opcionais,
justificativas e preservação do catálogo. Quantidades para grupos não são
multiplicadas automaticamente. A suíte completa passou com **124 testes**.

## Limites observados

- A mochila fracionária maximiza uma pontuação linear. Não impõe mínimos por
  categoria: a Rota do sol, por exemplo, não seleciona alimentação. Isso é uma
  limitação explícita do modelo, não uma garantia de preparação adequada.
- A essencialidade vem do estoque selecionado: desmarcar um essencial na
  interface o remove da entrada. O sistema não força sua presença depois disso.
- Os fatores são heurísticos por categoria. Proteção climática, por exemplo,
  compartilha regras de frio, calor e chuva entre os itens dessa categoria.
- Estoque, capacidade e pontuação referem-se ao grupo inteiro. Cabe ao usuário
  informar quantidades adequadas ao número de pessoas.
- Alterações de estoque e itens personalizados vivem na sessão; não há banco
  de dados nem persistência entre sessões.
- Esta avaliação verifica correção funcional nos cenários documentados. Não
  constitui benchmark de desempenho nem validação em campo.
