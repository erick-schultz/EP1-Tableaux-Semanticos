import re

try:
    from .code_base_EP1 import (
        And,
        ArgumentForm,
        Constant,
        Iff,
        ImpliedBy,
        Implies,
        Not,
        Or,
        Proposition,
        Variable,
    )
except ImportError:
    from code_base_EP1 import (
        And,
        ArgumentForm,
        Constant,
        Iff,
        ImpliedBy,
        Implies,
        Not,
        Or,
        Proposition,
        Variable,
    )

_TOKEN_RE = re.compile(r"\s*(<=>|<->|↔|>>|->|=>|→|<<|<=|[~¬&^∧|∨()]|[A-Za-z][A-Za-z0-9_]*)")


def _tokenizar(texto: str) -> list[str]:
    tokens: list[str] = []
    pos = 0
    n = len(texto)
    while pos < n:
        if texto[pos].isspace():
            pos += 1
            continue
        m = _TOKEN_RE.match(texto, pos)
        if not m:
            raise ValueError(f"Símbolo inválido na posição {pos}: {texto[pos:]!r}")
        tokens.append(m.group(1))
        pos = m.end()
    return tokens


class _Parser:
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.pos = 0

    def atual(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consumir(self) -> str:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self) -> Proposition:
        if not self.tokens:
            raise ValueError("Fórmula vazia")
        formula = self._iff()
        if self.atual() is not None:
            raise ValueError(f"Token inesperado: {self.atual()!r}")
        return formula

    def _iff(self) -> Proposition:
        esq = self._implies()
        while self.atual() in ("<=>", "<->", "↔"):
            self.consumir()
            esq = Iff(esq, self._implies())
        return esq

    def _implies(self) -> Proposition:
        esq = self._or()
        if self.atual() in (">>", "->", "=>", "→"):
            self.consumir()
            return Implies(esq, self._implies())
        while self.atual() in ("<<", "<="):
            self.consumir()
            esq = ImpliedBy(esq, self._or())
        return esq

    def _or(self) -> Proposition:
        esq = self._and()
        while self.atual() in ("|", "∨"):
            self.consumir()
            esq = Or(esq, self._and())
        return esq

    def _and(self) -> Proposition:
        esq = self._unary()
        while self.atual() in ("&", "^", "∧"):
            self.consumir()
            esq = And(esq, self._unary())
        return esq

    def _unary(self) -> Proposition:
        if self.atual() in ("~", "¬"):
            self.consumir()
            return Not(self._unary())
        return self._atom()

    def _atom(self) -> Proposition:
        tok = self.atual()
        if tok is None:
            raise ValueError("Fim inesperado da fórmula")
        if tok == "(":
            self.consumir()
            interna = self._iff()
            if self.atual() != ")":
                raise ValueError("Parêntese ')' esperado")
            self.consumir()
            return interna
        if tok == "True":
            self.consumir()
            return Constant(True)
        if tok == "False":
            self.consumir()
            return Constant(False)
        if tok[0].isalpha():
            self.consumir()
            return Variable(tok)
        raise ValueError(f"Token inesperado: {tok!r}")


def parse_formula(texto: str) -> Proposition:
    return _Parser(_tokenizar(texto)).parse()


def parse_sequente(texto: str) -> ArgumentForm:
    for sep in ("|-", "⊢"):
        if sep in texto:
            partes = texto.split(sep)
            if len(partes) != 2:
                raise ValueError("Sequente deve conter apenas um operador '|-'")
            lhs, rhs = partes
            premissas = [parse_formula(p) for p in lhs.split(",") if p.strip()]
            conclusao = parse_formula(rhs)
            return ArgumentForm(*premissas, conclusion=conclusao)
    raise ValueError("Sequente inválido: esperado formato 'A1, A2 |- B'")
