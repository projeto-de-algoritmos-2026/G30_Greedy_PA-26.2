# Especificação do TrailPack

## Objetivo

O **TrailPack** é uma aplicação web proposta para auxiliar no planejamento da
mochila de uma trilha. A recomendação deve considerar os recursos disponíveis,
as condições do percurso e a capacidade máxima de carga, priorizando a
utilidade dos recursos dentro desse limite de peso.

O usuário informa nome, distância, duração, dificuldade, temperatura, nível de
chuva, isolamento, disponibilidade de água no percurso, quantidade de pessoas
e capacidade da mochila. Também seleciona os itens que possui e suas
quantidades. O resultado planejado apresenta os itens e recursos selecionados,
suas quantidades, peso total, capacidade restante e justificativas de prioridade.

## Problema real

Uma pessoa que fará uma trilha precisa equilibrar necessidades e peso carregado.
Levar todos os itens disponíveis pode ultrapassar a capacidade da mochila;
escolher somente os mais leves pode deixar de fora recursos relevantes para
aquele percurso.

Por exemplo, em uma trilha de 18 km, com duração estimada de 7 horas, temperatura
de 30 °C, alta dificuldade e alto isolamento, sem pontos de água, hidratação,
alimentação e segurança têm necessidades diferentes das de uma trilha curta.
Uma mochila com limite de 8 kg exige decidir quais equipamentos levar e quanto
de cada consumível carregar.

O problema é, portanto, selecionar uma composição de mochila que respeite o
peso máximo e a disponibilidade dos itens, reservando os equipamentos essenciais
e maximizando a utilidade dos recursos divisíveis na capacidade restante.
A capacidade representa um limite de **peso em quilogramas**, não de volume.

## Itens indivisíveis e recursos divisíveis

| Tipo | Exemplos | Quantidade selecionada | Tratamento |
| --- | --- | --- | --- |
| Item indivisível | Lanterna, apito, capa de chuva, kit de primeiros socorros, power bank e mapa | Unidades inteiras | Seleção fora do Knapsack Fracionário |
| Recurso divisível | Água, alimentos fracionáveis, isotônico e mistura energética | Pode incluir frações da unidade | Otimização pelo Knapsack Fracionário |

Uma lanterna deve ser levada inteira: selecionar metade de seu peso não
representa um equipamento utilizável. Água pode ser repartida em litros e
alimentos podem ser fracionados quando sua forma de armazenamento permitir.
Um alimento em embalagem que precise permanecer inteira deve ser tratado como
indivisível. A divisibilidade depende do recurso cadastrado.

**Essencialidade e divisibilidade são propriedades distintas.** A marcação de
essencial indica uma seleção obrigatória para o planejamento; a divisibilidade
indica se a quantidade pode ser fracionada. O peso das quantidades essenciais
selecionadas é reservado antes da otimização. Essas quantidades não devem ser
contadas novamente entre os recursos disponíveis para o algoritmo.

Itens indivisíveis recomendados ou opcionais também não entram no algoritmo
fracionário. Caso sejam selecionados fora dele, seu peso deve ser descontado
antes da otimização. A política de seleção desses itens será definida nas
etapas de recomendação; o algoritmo fracionário não resolve essa escolha.

## Regras de otimização

1. Considerar somente itens disponíveis e quantidades que o usuário possui.
2. Reservar o peso dos essenciais e dos demais indivisíveis já selecionados.
3. Calcular a capacidade restante como `capacidade total - peso reservado`.
4. Calcular a utilidade contextual dos recursos divisíveis com base nos dados
   da trilha. Calor e ausência de pontos de água, por exemplo, podem aumentar a
   prioridade da hidratação. Os fatores e seus valores serão definidos pelo
   motor de prioridades.
5. Aplicar o Knapsack Fracionário aos recursos divisíveis disponíveis na
   capacidade restante.
6. Reunir os itens reservados e os recursos otimizados na recomendação, sem
   ultrapassar a capacidade total nem a quantidade disponível de cada recurso.

Se o peso reservado ultrapassar a capacidade, o planejamento é inviável com
essa seleção. O sistema deve informar o conflito, sem fracionar equipamentos
nem remover essenciais silenciosamente. Se a capacidade restante for zero,
nenhum recurso adicional pode ser selecionado. Se não houver recursos
divisíveis disponíveis, a recomendação contém apenas os itens reservados.
Quando todos os recursos úteis couberem, pode sobrar capacidade na mochila.

### Convenções de quantidade, peso e utilidade

Conforme os modelos em `src/models.py`, o peso e o valor base representam **uma
unidade** do item. A unidade pode ser um equipamento, um litro ou um quilograma
de consumível, desde que peso, valor e quantidade usem a mesma referência.

Para cada recurso divisível `i`:

- `q_i`: quantidade disponível, não negativa;
- `p_i`: peso por unidade, positivo e medido em kg;
- `v_i`: utilidade contextual por unidade, não negativa;
- `x_i`: quantidade selecionada, com `0 <= x_i <= q_i`.

O peso selecionado é `p_i × x_i` e a utilidade selecionada é `v_i × x_i`.
Os valores devem ser finitos. A quantidade de um item indivisível deve ser
inteira. A utilidade é uma pontuação de planejamento, não um preço monetário.

## Aplicação do Knapsack Fracionário

Seja `C` a capacidade restante após a reserva dos itens. O subproblema é:

```text
Maximizar: soma(v_i × x_i)
Sujeito a: soma(p_i × x_i) <= C
           0 <= x_i <= q_i
```

A estratégia gulosa calcula `v_i / p_i`, a utilidade por quilograma, e ordena
os recursos por essa razão em ordem decrescente. Para cada recurso, seleciona
a quantidade disponível se ela couber. Caso contrário, seleciona somente
`capacidade restante / p_i` unidades e encerra o preenchimento. Recursos com
quantidade ou utilidade zero não acrescentam benefício e podem ser ignorados.
Empates na razão permitem qualquer ordem entre os recursos empatados, sem
alterar a utilidade ótima desse subproblema.

A estratégia maximiza a utilidade **do subproblema divisível**, pois cada
quilograma recebe a maior utilidade disponível. Essa garantia pressupõe
utilidade linear na quantidade, recursos independentes e somente a restrição
de peso além dos limites de disponibilidade. Não garante a escolha ótima dos
equipamentos indivisíveis nem impõe quantidades mínimas por categoria. Caso
essas restrições sejam necessárias, devem ser tratadas fora dessa formulação.

### Exemplo ilustrativo das regras

Considere uma capacidade total de **8 kg** e **1,3 kg** de equipamentos
essenciais já reservados. Restam **6,7 kg** para recursos divisíveis. Os valores
abaixo são hipotéticos, usados apenas para demonstrar a seleção.

| Recurso | Unidade | Quantidade disponível | Peso por unidade (kg) | Utilidade por unidade | Utilidade/kg | Quantidade selecionada |
| --- | --- | --- | --- | --- | --- | --- |
| Água | L | 4 | 1 | 100 | 100 | 4 L |
| Alimentos fracionáveis | kg | 2 | 1 | 80 | 80 | 2 kg |
| Isotônico | L | 1 | 1 | 60 | 60 | 0,7 L |

O algoritmo seleciona primeiro 4 kg de água, depois 2 kg de alimentos e,
por fim, 0,7 kg de isotônico. O peso dos recursos é **6,7 kg**, sua utilidade
é `4 × 100 + 2 × 80 + 0,7 × 60 = 602` e o peso total da mochila é
`1,3 + 6,7 = 8 kg`. O isotônico é selecionado parcialmente; os equipamentos
essenciais permanecem inteiros.

Esta especificação descreve o comportamento planejado. A implementação do
catálogo, dos fatores de prioridade, da seleção e do algoritmo pertence às
próximas etapas do projeto.
