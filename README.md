# EP1 — Tableaux Semânticos (MAC0239)

Implementação de um provador de teoremas para Lógica Proposicional utilizando **Tableaux Semânticos** (busca em profundidade com estratégia α-primeiro e heurística de seleção β por fechamento imediato e menor tamanho).

## Estrutura do Projeto

```text
EP1-Tableaux-Semanticos/
├── docs/
│   ├── ep.tableaux.pdf           # Enunciado do EP1
│   └── livro.partes.tableaux.pdf # Material complementar de referência
├── src/
│   ├── __init__.py
│   ├── code_base_EP1.py          # Código-base fornecido (fórmulas, árvores e sequentes)
│   ├── parser.py                 # Parser de fórmulas e sequentes em texto
│   └── tableaux.py               # Implementação do provador de tableaux semânticos
├── examples/
│   └── code_base_EP1_demo.py     # Demonstração original do código-base
├── tests/
│   ├── test_code_base.py         # Testes do código-base
│   └── test_tableaux.py          # Testes do provador e do parser
├── main.py                       # Script de utilização (bateria de exemplos, CLI e interativo)
├── pyproject.toml
├── .gitignore
├── .gitattributes
└── README.md
```

## Requisitos

- **Python 3.10+** (sem dependências externas para execução)
- Opcional para desenvolvimento: `pytest` e `ruff`

## Como Executar

### Rodar a bateria de exemplos

```bash
python3 main.py
```

### Provar um sequente via linha de comando

```bash
python3 main.py "P, P >> Q |- Q"
python3 main.py "|- ((P >> Q) >> P) >> P"
python3 main.py "P, (P & Q) >> R |- R"
```

### Modo interativo

```bash
python3 main.py -i
```

### Demonstração do código-base

```bash
python3 examples/code_base_EP1_demo.py
```

### Testes e lint

```bash
pytest -v
ruff check .
```

## Créditos do Código-Base

O arquivo `src/code_base_EP1.py` foi adaptado originalmente de [Andrew Kay (`dcaa`)](https://bitbucket.org/Andrew-Kay/dcaa/src/master) (com adaptações de `acvm`), conforme indicado no cabeçalho do arquivo.
