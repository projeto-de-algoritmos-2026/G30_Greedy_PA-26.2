# TrailPack

**Conteúdo da Disciplina:** Algoritmos Gulosos

## Alunos

| Matrícula | Aluno |
| -- | -- |
| 23/1011838 | Tiago Antunes Balieiro |
| 23/1026714 | Euller Júlio da Silva |

## Apresentação do trabalho

O link para o vídeo de apresentação será adicionado após a gravação.

## Sobre

O **TrailPack** é um projeto de aplicação web para auxiliar no planejamento de
mochilas para trilhas. A proposta é considerar as características do percurso,
os itens disponíveis e a capacidade máxima de carga para sugerir uma composição
de mochila adequada ao cenário informado.

O planejamento levará em conta distância, duração, dificuldade, temperatura,
chuva, isolamento, disponibilidade de água durante o trajeto e quantidade de
pessoas. Essas condições serão utilizadas para calcular a utilidade contextual
dos recursos: por exemplo, uma trilha longa e quente, sem pontos de água,
aumentará a prioridade da hidratação.

A solução distinguirá **itens indivisíveis**, como lanterna, apito e kit de
primeiros socorros, de **recursos divisíveis**, como água, alimentos e isotônico.
Os itens essenciais selecionados terão seu peso reservado antes da otimização.
Na capacidade restante, será aplicada uma implementação manual do algoritmo
guloso de **Knapsack Fracionário** (problema da mochila fracionária).

O algoritmo ordenará os recursos pela razão entre utilidade e peso, selecionando
primeiro os de maior razão. Quando um recurso não couber integralmente, apenas
a fração que cabe será selecionada. Essa estratégia maximiza a utilidade no
subproblema fracionário, considerando valores lineares e a capacidade restante
após a reserva dos essenciais. A ordenação terá complexidade de tempo
**O(n log n)**, seguida de uma seleção **O(n)**, para `n` recursos divisíveis.

**Estado atual:** o catálogo, o perfil da trilha, as prioridades contextuais,
a reserva de essenciais e o Knapsack Fracionário estão integrados à interface.
É possível configurar o percurso, montar a mochila, consultar o resultado e
baixar um checklist. Quatro cenários simulados preenchem o formulário: Rota do
sol, Além do horizonte, Serra gelada e Caminho das águas. Também estão disponíveis seleção e edição do
estoque, itens personalizados, justificativas, tabela Valor/Peso e desafio
jogador × algoritmo.

## Screenshots

![Expedições e visual do TrailPack](docs/interface-expedicoes.png)

*Ilustração de trilha e seleção de cenários simulados.*

![Resumo da mochila](docs/interface-mochila.png)

*Peso, espaço restante e pontos de utilidade da última montagem.*

## Instalação

**Linguagem:** Python 3.10+<br>
**Framework:** Streamlit<br>
**Bibliotecas previstas:** Pandas para tabelas e Pytest para testes

Pré-requisitos:

- Python 3.10 ou superior;
- Git;
- acesso ao repositório no GitHub, enquanto ele estiver privado.

Clone o projeto e entre no diretório:

```bash
git clone https://github.com/projeto-de-algoritmos-2026/TrailPack.git
cd TrailPack
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows, ative o ambiente pelo PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências e execute a aplicação:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

O Streamlit informará o endereço local da aplicação, normalmente
`http://localhost:8501`.

Para executar os testes automatizados:

```bash
python -m pytest -q
```

## Uso

1. Escolha uma das quatro expedições ou preencha seu próprio percurso.
2. Ajuste distância, duração, clima, dificuldade, isolamento, água disponível,
   número de pessoas e capacidade total de carga.
3. Selecione os itens disponíveis, ajuste pesos e quantidades ou adicione um
   item personalizado. Clique em **Montar minha mochila** para reservar os
   equipamentos selecionados e otimizar os consumíveis na carga restante.
4. Confira peso, capacidade restante, utilidade, justificativas e a tabela
   Valor/Peso. No desafio, monte seus consumíveis e compare com o algoritmo.
5. Baixe o checklist para revisar a seleção. Após editar o percurso, clique
   novamente em **Montar minha mochila** para atualizar o resultado.

A capacidade e o estoque são totais para o grupo. Os equipamentos indivisíveis
opcionais começam desmarcados; se selecionados, têm seu peso reservado. Se os
itens essenciais não couberem, a interface informa o conflito. Os pontos são
heurísticos: não garantem suficiência dos recursos para uma trilha real.

## Outros

### Organização do projeto

```text
TrailPack/
├── app.py              # Entrada da interface Streamlit
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── models.py       # Contratos de domínio
│   ├── trail_profile.py
│   ├── priority_engine.py
│   ├── essential_items.py
│   ├── knapsack.py
│   ├── recommendation.py
│   ├── scenarios.py
│   ├── explanations.py
│   ├── item_editor.py
│   ├── game.py
│   ├── game_ui.py
│   └── ui.py
├── assets/             # Ilustração vetorial local da paisagem
├── data/               # Catálogo e quatro cenários simulados
├── scripts/            # Reprodução dos resultados
├── tests/              # Testes automatizados
└── docs/               # Documentação complementar
```

### Convenções dos modelos

- Pesos e capacidade em quilogramas, distância em quilômetros, duração em horas
  e temperatura em graus Celsius.
- O peso e o valor base de um item representam uma unidade do recurso.
- Itens indivisíveis exigem quantidades inteiras; recursos divisíveis aceitam
  quantidades fracionárias.
- O modelo de recomendação calcula o peso total e a capacidade restante e
  rejeita uma seleção que exceda a capacidade da mochila.

### Resultados

Veja os [cenários e resultados reproduzíveis](docs/resultados.md), incluindo
quatro mochilas calculadas e um desafio com eficiência de 88,26%.

```bash
python -m scripts.reproduce_results
```
