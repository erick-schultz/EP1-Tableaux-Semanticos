# EP1 — Tableaux Semânticos

Implementação de um provador de teoremas para o Cálculo Proposicional usando o método dos **Tableaux Semânticos** (Analíticos), desenvolvido para a disciplina **MAC0239 — Métodos Formais em Programação** (IME-USP).

Dado um sequente $A_1, A_2, \dots, A_n \vdash B$, o programa decide se ele é válido ou não:
- **Se for válido**, retorna `valido=True` e a sequência de regras aplicadas até o fechamento de todos os ramos.
- **Se não for válido**, retorna `valido=False`, um **contra-exemplo** (valoração dos átomos que satisfaz todas as premissas e falsifica a conclusão) e a sequência de regras aplicadas.

## Estrutura do Repositório

```text
EP1-Tableaux-Semanticos/
├── docs/
│   ├── ep.tableaux.pdf           # Enunciado do EP1
│   └── livro.partes.tableaux.pdf # Material de apoio (regras e estratégias)
├── src/
│   ├── __init__.py
│   ├── code_base_EP1.py          # Código-base fornecido (fórmulas, árvores e sequentes)
│   ├── parser.py                 # Parser de fórmulas e sequentes em texto
│   └── tableaux.py               # Provador de tableaux semânticos
├── examples/
│   └── code_base_EP1_demo.py     # Demonstração original do código-base
├── pyproject.toml
├── .gitignore
├── .gitattributes
└── README.md
```

## Como Funciona

- **Estratégia de busca:** busca em profundidade (DFS) mantendo um único ramo ativo e uma pilha de ramificações (`pilha_ramos`) para backtracking.
- **Ordem das regras:** estratégia **α-primeiro** (expande todas as regras lineares $\alpha\wedge$, $\alpha\vee$, $\alpha\rightarrow$, $\alpha\neg$ e $\beta\neg$ antes de bifurcar).
- **Escolha de fórmulas β:** prioriza fórmulas que fecham algum ramo imediatamente e, em caso de empate, escolhe a de menor tamanho sintático.

### Linguagem Suportada no Parser

- **Átomos:** letras/identificadores (`P`, `q`, `a`, `b`, etc.) e constantes (`True`, `False`)
- **Conectivos:** negação (`~`, `¬`), conjunção (`&`, `^`, `∧`), disjunção (`|`, `∨`), implicação (`>>`, `->`, `=>`, `→`), implicação reversa (`<<`, `<=`) e bicondicional (`<=>`, `<->`, `↔`)
- **Sequentes:** `A1, A2, ... |- B` (ou usando `⊢`; o lado esquerdo pode ficar vazio para teoremas como `|- P | ~P`)

## Requisitos

- **Python 3.10+** (usa apenas a biblioteca padrão)

## Exemplos de Uso

### Usando o parser de texto

```python
from src import parse_sequente, provar_sequente

resultado = provar_sequente(parse_sequente("P, P >> Q |- Q"))
print(resultado)
# Resultado: Válido
# Regras aplicadas: [('β→', 'T P => Q')]
```

Exemplo de sequente inválido (gera contra-exemplo):

```python
from src import parse_sequente, provar_sequente

resultado = provar_sequente(parse_sequente("P, (P & Q) >> R |- R"))
print(resultado)
# Resultado: Inválido
# Contra-exemplo: {'P': True, 'Q': False, 'R': False}
# Regras aplicadas: [('β→', 'T (P ^ Q) => R'), ('β∧', 'F P ^ Q')]
```

### Usando diretamente as classes do código-base

```python
from src.code_base_EP1 import ArgumentForm, vars
from src.tableaux import provar_sequente

P, Q = vars("P", "Q")
sequente = ArgumentForm(P, P >> Q, conclusion=Q)
resultado = provar_sequente(sequente)
print(resultado.valido, resultado.regras_aplicadas)
```

## Créditos do Código-Base

O arquivo [src/code_base_EP1.py](src/code_base_EP1.py) foi adaptado originalmente de [Andrew Kay (`dcaa`)](https://bitbucket.org/Andrew-Kay/dcaa/src/master) (com adaptações de `acvm`), conforme indicado no cabeçalho do arquivo.
