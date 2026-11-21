# EP1 — Tableaux Semânticos

Repositório para o **EP1 (Tableaux Semânticos)** em Lógica Proposicional, construído a partir do código-base fornecido para representação de fórmulas, árvores de subfórmulas e sequentes (`ArgumentForm`).

## Estrutura do Projeto

```text
EP1-Tableaux-Semanticos/
├── code_base_EP1.py       # Biblioteca base (árvores, proposições, tabelas-verdade e sequentes)
├── code_base_EP1_demo.py  # Script de demonstração do código-base
├── tests/
│   └── test_code_base.py  # Testes automatizados de verificação do código-base
├── pyproject.toml         # Metadados do projeto e configuração de pytest/ruff
├── .gitignore
├── .gitattributes
└── README.md
```

## Requisitos

- **Python 3.10+** (o código-base utiliza apenas a biblioteca padrão do Python)
- Opcional para desenvolvimento: `pytest` e `ruff`

## Como Executar

### Demonstração do código-base

```bash
python3 code_base_EP1_demo.py
```

### Testes

```bash
pytest
```

### Lint (opcional)

```bash
ruff check .
```

## Créditos do Código-Base

O arquivo `code_base_EP1.py` foi adaptado originalmente de [Andrew Kay (`dcaa`)](https://bitbucket.org/Andrew-Kay/dcaa/src/master) (com adaptações de `acvm`), conforme indicado nos comentários do arquivo.
