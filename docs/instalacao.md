# Instalação e execução do TrailPack

## Pré-requisitos

- Python 3.10 ou superior, com suporte a `pip` e `venv`;
- Git para clonar o repositório;
- acesso à internet para obter o projeto e as dependências;
- navegador para acessar a interface local;
- permissão de acesso ao repositório, caso esteja privado.

As dependências estão em [`requirements.txt`](../requirements.txt): Streamlit,
Pandas e Pytest. O projeto usa arquivos JSON locais para catálogo e cenários;
não exige banco de dados, credenciais de serviços externos ou arquivo `.env`.

## Obter o projeto

```bash
git clone https://github.com/projeto-de-algoritmos-2026/TrailPack.git
cd TrailPack
```

Se o projeto já estiver no computador, entre no diretório existente. Execute
os comandos seguintes na **raiz do repositório**, onde estão `app.py` e
`requirements.txt`. Mantenha também os diretórios `data/`, `assets/`, `src/`
e `.streamlit/`, utilizados pela aplicação.

## Criar o ambiente virtual

O ambiente virtual isola as dependências do projeto. Escolha os comandos
correspondentes ao seu sistema operacional.

### Linux e macOS

Confira a versão do Python e crie o ambiente:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
```

### Windows — PowerShell

Confira se a versão exibida é 3.10 ou superior:

```powershell
py -3 --version
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Se o lançador `py` não estiver disponível, use `python` nos dois primeiros
comandos, verificando antes a versão. No Prompt de Comando (CMD), a ativação é:

```bat
.venv\Scripts\activate.bat
```

## Instalar as dependências

Com o ambiente ativo, execute:

```bash
python -m pip install -r requirements.txt
```

Usar `python -m pip` instala as dependências no mesmo interpretador que será
usado para executar a aplicação e os testes. Em novos terminais, ative
novamente o ambiente existente; não é necessário recriá-lo.

## Iniciar e encerrar a aplicação

Na raiz do projeto, com o ambiente ativo:

```bash
python -m streamlit run app.py
```

Abra o endereço indicado no terminal, normalmente **http://localhost:8501**.
Mantenha esse terminal aberto enquanto utiliza o TrailPack. Execute a aplicação
pelo Streamlit para que os formulários e o estado da sessão funcionem.

Para encerrar o servidor, pressione **Ctrl+C** no terminal. Se desejar sair
do ambiente virtual depois disso, execute:

```bash
deactivate
```

## Fluxo de uso

1. Escolha um cenário ou informe as características da trilha e a capacidade.
2. Marque os itens disponíveis, ajuste quantidade e peso por unidade e,
   se desejar, adicione itens personalizados.
3. Clique em **Montar minha mochila** para calcular a recomendação.
4. Consulte os itens reservados, consumíveis otimizados, justificativas e a
   tabela com valor, peso, valor/peso e quantidade selecionada.
5. Baixe o checklist ou monte uma escolha manual de consumíveis no
   **Desafio TrailPack** e clique em **Comparar com o algoritmo**.

Ao modificar a trilha ou o estoque, monte novamente a mochila. O desafio usa
os dados da última montagem. Os dois participantes usam a mesma capacidade,
estoque e itens reservados. Os itens personalizados e ajustes ficam na sessão,
sem gravar alterações em `data/items.json`; uma nova sessão começa com o catálogo.

## Executar os testes

Execute os comandos na raiz do repositório, com o ambiente virtual ativo.

Suíte completa, incluindo lógica e interface:

```bash
python -m pytest -q
```

Apenas o Knapsack Fracionário:

```bash
python -m pytest -q tests/test_knapsack.py
```

Apenas os fluxos da interface:

```bash
python -m pytest -q tests/test_app.py
```

Os testes de interface usam `streamlit.testing.v1.AppTest`. Eles executam a
aplicação automaticamente, sem exigir servidor iniciado ou navegador aberto.

## Problemas comuns

| Problema | Como resolver |
| --- | --- |
| Python abaixo de 3.10 | Instale uma versão compatível e crie o ambiente com esse interpretador |
| Falha ao criar o ambiente por ausência de `venv` ou `ensurepip` | Instale o suporte a ambientes virtuais correspondente à sua instalação de Python e repita a criação |
| `No module named streamlit` ou `No module named pytest` | Ative o ambiente e execute `python -m pip install -r requirements.txt` |
| `app.py` ou `requirements.txt` não encontrado | Entre na raiz do repositório antes de executar o comando |
| Porta 8501 ocupada | Use uma porta livre, como no comando abaixo |
| PowerShell bloqueia `Activate.ps1` | Execute diretamente o Python do ambiente, conforme os comandos abaixo |
| Essenciais ou equipamentos selecionados excedem a capacidade | Ajuste a capacidade ou a seleção e monte novamente a mochila |

Para usar outra porta:

```bash
python -m streamlit run app.py --server.port 8502
```

Nesse caso, acesse o endereço indicado pelo terminal, normalmente
`http://localhost:8502`.

No Windows, é possível instalar, executar e testar sem ativar o ambiente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
.\.venv\Scripts\python.exe -m pytest -q
```

Para confirmar qual interpretador está sendo usado:

```bash
python -c "import sys; print(sys.executable)"
```

Com o ambiente do projeto ativo, o caminho deve apontar para `.venv`.
