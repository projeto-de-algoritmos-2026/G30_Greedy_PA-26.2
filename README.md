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

**Estado atual:** estão implementados a estrutura inicial, a tela de entrada do
Streamlit e os modelos `Trail`, `Item`, `TrailConditions` e `Recommendation`.
O catálogo, o cálculo de prioridades, o algoritmo e as telas de configuração e
resultado ainda serão desenvolvidos.

A [especificação do problema e das regras de otimização](docs/especificacao.md)
detalha o objetivo, o problema real, a distinção entre itens indivisíveis e
recursos divisíveis e a aplicação do Knapsack Fracionário.

## Screenshots

As imagens do fluxo de planejamento e recomendação serão adicionadas conforme
as respectivas telas forem implementadas.

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

O diretório `tests/` está reservado para os testes automatizados. Quando forem
adicionados, poderão ser executados com:

```bash
python -m pytest -q
```

## Uso

Na versão atual, iniciar a aplicação exibe a tela inicial do TrailPack e um
aviso de que o projeto está em desenvolvimento.

O fluxo planejado para as próximas etapas é:

1. Informar os dados da trilha, a quantidade de pessoas e a capacidade da mochila.
2. Selecionar os itens disponíveis e ajustar seus pesos e quantidades.
3. Acionar **Montar minha mochila** para calcular prioridades, reservar os
   essenciais e otimizar os recursos divisíveis.
4. Consultar os itens recomendados, as quantidades, o peso total, a capacidade
   restante e as justificativas de prioridade.

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
│   └── models.py       # Modelos de trilha, condições, itens e recomendação
├── data/               # Catálogo e cenários a serem adicionados
├── tests/              # Testes a serem adicionados
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

Os cenários de uso e os resultados da otimização serão documentados após a
implementação e a validação do fluxo de recomendação.
