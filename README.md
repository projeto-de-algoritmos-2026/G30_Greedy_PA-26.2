# TrailPack

Planejador inteligente de mochila para trilhas, desenvolvido para Projeto de Algoritmos por Euller e Tiago.

A proposta é usar as condições da trilha para priorizar recursos dentro da capacidade da mochila. Itens essenciais indivisíveis terão seu peso reservado antes da seleção de recursos divisíveis pelo Knapsack Fracionário.

## Estado do projeto

Estrutura inicial em desenvolvimento. O algoritmo e o fluxo de recomendação serão implementados nas próximas etapas.

## Ambiente

Python 3.10 ou superior.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Organização

```text
app.py          Entrada da interface Streamlit
src/            Modelos e lógica da aplicação
data/           Catálogo e cenários
tests/          Testes automatizados
docs/           Documentação do projeto
```
