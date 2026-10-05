# Roteiro da apresentação — TrailPack

Roteiro proposto para **Euller e Tiago**, com duração de **5 minutos**.
Preparado como parte do commit compartilhado 23; revisar e ensaiar em dupla
antes da gravação. A divisão abaixo é uma proposta, não uma confirmação de
revisão pelo Tiago.

## Preparação

1. Instalar as dependências e iniciar `streamlit run app.py`.
2. Abrir uma sessão nova, sem itens personalizados ou alterações de estoque.
3. Ter abertos `src/trail_profile.py`, `src/priority_engine.py`,
   `src/essential_items.py`, `src/knapsack.py` e `src/game.py`.
4. Executar `python -m scripts.reproduce_results` e `python -m pytest -q`.
5. Usar o cenário **Além do horizonte**, com o estoque inicial: essenciais e
   recursos divisíveis marcados; protetor solar, power bank, mapa e repelente
   desmarcados. Não alterar pesos ou quantidades durante o caso principal.
6. Conferir áudio, legibilidade da interface e captura do código antes de gravar.

## Sequência de cinco minutos

| Tempo | Pessoa | Tela e ação | Mensagem central |
| --- | --- | --- | --- |
| 0:00–0:30 | Euller | Tela inicial e cartões de expedição | Apresentar o problema de escolher recursos úteis com peso limitado. |
| 0:30–1:15 | Euller | Selecionar Além do horizonte; mostrar formulário e estoque | 20 km, 8 h, 30 °C, alta dificuldade e isolamento, sem água, 5 kg de capacidade. |
| 1:15–2:00 | Euller | Montar mochila; mostrar resumo e justificativa da água | Reservar equipamentos e calcular utilidade conforme o contexto. |
| 2:00–3:00 | Tiago | Tabela Valor/Peso e `fractional_knapsack` | Ordenação decrescente, seleção integral e fração do último recurso; complexidade. |
| 3:00–3:50 | Tiago | Desafio; informar quantidades e comparar | Mesmos itens fixos e estoque para jogador e algoritmo; 88,26% no exemplo. |
| 3:50–4:20 | Euller | Resultado dos testes e documentação | Testes de limites, integração e resultados reproduzíveis. |
| 4:20–5:00 | Ambos | Retomar mochila e checklist | Limites do modelo, contribuições e conclusão. |

## Falas sugeridas e números de referência

### Euller — problema e contexto

> “O TrailPack ajuda a explorar como montar uma mochila dentro de um limite de
> peso. Nesta simulação, temos uma trilha de 20 quilômetros, oito horas, calor,
> alto isolamento e nenhum ponto de água. A mochila suporta cinco quilos.”

Mostrar que pesos e quantidades podem ser editados. Explicar que equipamentos
indivisíveis são levados inteiros e consumíveis podem ser fracionados. O estoque
é informado pelo usuário, não estimado automaticamente pelo número de pessoas.

> “Os quatro essenciais ocupam 0,92 kg, deixando 4,08 kg para os consumíveis.
> A utilidade da água passa de 100 para 273 por litro, pelo calor, pela duração
> longa e pela ausência de água. As justificativas mostram essas condições.”

A multiplicação é `100 × 1,4 × 1,3 × 1,5 = 273`. Distância e duração longas
ativam a mesma regra uma única vez. Abrir a justificativa de Água no resultado.

### Tiago — algoritmo guloso

Mostrar `fractional_knapsack` em `src/knapsack.py`: validação, ordenação por
`valor_base / peso`, atualização da capacidade restante e quantidade fracionária.
O motor entrega cópias cujo campo `valor_base` contém a utilidade contextual;
o catálogo original não é modificado.

> “A cada passo escolhemos a maior utilidade por quilo. Selecionamos três litros
> de água, um de isotônico e 0,08 kg de mistura energética. Assim completamos os
> cinco quilos. Não dividimos equipamentos: eles foram reservados antes.”

> “Ordenar os recursos custa O(n log n), e percorrer a lista custa O(n).
> A estratégia é ótima para o subproblema divisível com utilidade linear e
> restrição de peso; ela não resolve a escolha ótima de todos os equipamentos.”

Os 591 pontos dos itens fixos mais 994,968 dos recursos resultam em **1585,968**.
O resumo mostra **1586**; o desafio apresenta **1585,97** por arredondamento.

### Tiago — desafio

Preencher os quatro campos de consumíveis:

| Campo | Quantidade manual |
| --- | ---: |
| Água | 2 |
| Alimentos fracionáveis | 1 |
| Isotônico | 0,5 |
| Mistura energética | 0,3 |

Clicar em **Comparar com o algoritmo**. A mochila manual pesa **4,720 kg** e
soma **1399,73 pontos**. A eficiência é **88,26%**, calculada sobre a pontuação
total, incluindo equipamentos idênticos nos dois lados.

> “A comparação usa as mesmas condições. Nossa mochila deixou espaço livre e
> levou mais recursos de menor utilidade por quilo. Copiar a composição gulosa
> permite empatar em 100%.”

### Euller — validação

> “A suíte atual passou com 124 testes. Os testes de integração verificam o
> caminho completo, da trilha à recomendação: reserva de essenciais, fração do
> último recurso, capacidade insuficiente, estoque vazio e catálogo preservado.”

Mostrar a execução real, sem simular saída. Em `docs/resultados.md`, apontar a
tabela dos quatro cenários e o comando para reproduzir os números.

### Ambos — limites e encerramento

Euller:

> “A ferramenta maximiza uma pontuação heurística. Ela não impõe mínimos por
> categoria nem garante que a mochila seja suficiente para uma trilha real.”

Tiago:

> “O projeto aplica o Knapsack Fracionário com implementação manual e torna
> visíveis as prioridades, a seleção e o efeito das escolhas do jogador.”

Mostrar o botão de checklist e encerrar com os nomes da dupla.

## Plano de contingência

- Se o estado da sessão tiver sido alterado, abrir uma sessão nova e repetir a
  seleção padrão antes de apresentar os números.
- Se a interface falhar durante a gravação, parar e corrigir; usar o script de
  reprodução para diagnosticar os dados, sem apresentar uma execução antiga
  como se fosse a atual.
- Se houver pouco tempo, reduzir a exploração do estoque e manter caso real,
  código do algoritmo, resultado e limite do modelo.

## Pendências para entrega

- **Tiago — commit 20:** documentar o algoritmo, sua justificativa de correção,
  hipóteses e análise de complexidade em `docs/algoritmo.md`. Há um resumo no
  README, mas o documento previsto ainda não existe.
- **Tiago — commit 22:** revisar e finalizar as instruções de instalação e
  execução. O README já contém comandos; falta a revisão final prevista na
  divisão, incluindo verificação em ambiente limpo.
- **Ambos — commit 23:** revisar este roteiro em dupla, ensaiar, gravar e
  publicar a apresentação. O texto está preparado; a gravação não foi feita.
- Adicionar o link real do vídeo em **Apresentação do trabalho** no README.
- Atualizar as capturas do README para incluir seleção de itens, justificativas
  e desafio; as imagens atuais retratam a versão anterior a essas funcionalidades.
- Conferir o acesso do professor ao repositório e os requisitos de entrega da
  disciplina. Não há exigência de hospedagem identificada no planejamento;
  disponibilizar uma aplicação pública é opcional, salvo regra externa do curso.

O MVP e o modo de comparação estão implementados. Persistência de trilhas,
comparação entre capacidades e demais extras do planejamento são opcionais.
