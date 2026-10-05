# Roteiro de gravação — TrailPack

**Duração: 5 minutos · Euller e Tiago.** Ações e falas estão reunidas neste arquivo.

## Antes de gravar

Na raiz do projeto, prepare o ambiente no Linux/macOS (se já existir, apenas ative):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m scripts.reproduce_results
python -m streamlit run app.py
```

Abra `http://localhost:8501` em uma sessão nova. Deixe a saída dos testes disponível e confira áudio e legibilidade. Mantenha o estoque inicial: essenciais e consumíveis marcados; protetor solar, power bank, mapa e repelente desmarcados.

## 0:00–0:30 · Euller — problema

**Ação:** mostrar a tela inicial e os cenários.

> “O TrailPack ajuda a escolher recursos úteis para uma trilha dentro do limite de peso da mochila. Equipamentos são levados inteiros; consumíveis podem ser fracionados.”

## 0:30–1:15 · Euller — configuração

**Ação:** escolher **Além do horizonte**: 20 km, 8 h, 30 °C, dificuldade e isolamento altos, sem água no percurso, capacidade de 5 kg. Abrir Água e mostrar seleção, quantidade e peso, sem alterar os valores.

> “O usuário informa o percurso e os itens que possui. Pode selecionar itens, alterar quantidade e peso ou adicionar um item próprio. Capacidade e estoque são totais para o grupo.”

## 1:15–2:00 · Euller — recomendação

**Ação:** clicar em **Montar minha mochila** e abrir a justificativa de Água.

> “Os quatro essenciais ocupam 0,92 kg; restam 4,08 kg para consumíveis. A utilidade da água passa de 100 para 273 por litro: 100 × 1,4 pelo calor × 1,3 pela trilha longa × 1,5 pela ausência de água. Distância e duração longas ativam a mesma regra uma única vez.”

## 2:00–3:00 · Tiago — algoritmo e tabela

**Ação:** mostrar **Como a mochila foi otimizada**, com Item, Valor, Peso, Valor/Peso e Quantidade selecionada.

> “Valor e peso são por unidade. O Knapsack Fracionário ordena os consumíveis por valor/peso, seleciona toda a quantidade que cabe e, quando necessário, apenas a fração que completa a mochila. Trocar peso de um recurso de menor razão por outro de maior razão aumenta a utilidade: essa é a justificativa da escolha gulosa.”

> “Aqui entram 3 L de água, 1 L de isotônico e 0,08 kg de mistura energética. Com os equipamentos, são 5 kg e 1585,968 pontos: 1586 no resumo. A ordenação custa O(n log n), a seleção O(n), e o total O(n log n). A solução é ótima para os recursos divisíveis com utilidade linear; equipamentos já foram reservados.”

## 3:00–3:45 · Tiago — jogador versus algoritmo

**Ação:** no **Desafio TrailPack**, informar Água **2**, Alimentos **1**, Isotônico **0,5** e Mistura energética **0,3**. Clicar em **Comparar com o algoritmo**.

> “As duas mochilas usam a mesma trilha, estoque, capacidade e equipamentos. O jogador fez 1399,73 pontos em 4,720 kg; o algoritmo fez 1585,97 em 5 kg. A eficiência é score jogador dividido pelo score greedy, vezes 100: 88,26%. Repetir a composição gulosa permite empatar em 100%.”

## 3:45–4:10 · Euller — item personalizado

**Ação:** em **Adicionar item personalizado**, cadastrar Bússola, categoria Navegação, peso **0,15 kg**, utilidade **50** e quantidade **1**; deixar divisibilidade e essencialidade desmarcadas. Adicionar e mostrar seus controles. Manter a bússola desmarcada e montar novamente para recuperar o resultado principal.

> “Os itens personalizados e ajustes ficam na sessão, sem alterar o catálogo. Equipamentos opcionais entram quando selecionados. Adicionar um item limpa o resultado anterior; montar novamente reinicia o desafio.”

## 4:10–4:30 · Euller — testes

**Ação:** mostrar a saída real de `python -m pytest -q`, usando a contagem exibida.

> “Os testes verificam o algoritmo, prioridades, essenciais, integração, interface e desafio, incluindo seleção parcial, estoque vazio, excesso de peso e preservação do catálogo.”

## 4:30–5:00 · Ambos — encerramento

**Ação:** voltar ao resultado e baixar o checklist.

**Euller:** “A pontuação é heurística: não impõe mínimos por categoria nem garante recursos suficientes para uma trilha real.”

**Tiago:** “O TrailPack aplica o Knapsack Fracionário e mostra as prioridades, as quantidades selecionadas e o efeito das escolhas do jogador.”

Encerrar com os nomes da dupla. Se os números divergirem, restaurar uma sessão nova e a seleção inicial antes de gravar.
