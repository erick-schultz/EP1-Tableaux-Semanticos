# EP1 — Tableaux Semânticos (MAC0239)

Implementação de um provador de teoremas para Lógica Proposicional utilizando **Tableaux Semânticos** (busca em profundidade com estratégia α-primeiro e escolha de β por fechamento imediato e menor tamanho).

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
├── pyproject.toml
├── .gitignore
├── .gitattributes
└── README.md
```

## Requisitos

- **Python 3.10+** (sem dependências externas)

## Uso da Implementação

```python
from src import parse_sequente, provar_sequente

resultado = provar_sequente(parse_sequente("P, P >> Q |- Q"))
print(resultado)
```

Também é possível passar um `ArgumentForm` criado diretamente com `src/code_base_EP1.py`:

```python
from src.code_base_EP1 import ArgumentForm, vars
from src.tableaux import provar_sequente

P, Q = vars("P", "Q")
resultado = provar_sequente(ArgumentForm(P, P >> Q, conclusion=Q))
print(resultado)
```

## Créditos do Código-Base

O arquivo `src/code_base_EP1.py` foi adaptado originalmente de [Andrew Kay (`dcaa`)](https://bitbucket.org/Andrew-Kay/dcaa/src/master) (com adaptações de `acvm`), conforme indicado no cabeçalho do arquivo.
