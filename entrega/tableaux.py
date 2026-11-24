# This code has been adapted from: https://bitbucket.org/Andrew-Kay/dcaa/src/master
# Refer to the Author whenever the code is used

from collections import deque
from dataclasses import dataclass
import re


# --- Estruturas base (code_base_EP1) ---

class Tree:
    def __init__(self, children=None, value=None, parent=None):
        self.value = value
        self.parent_node = parent
        if children is not None:
            for child in children:
                if isinstance(child, Tree):
                    child = self.__class__(child.children(), child.value, self)
                    self.add_child_node(child)
                elif hasattr(child, "__iter__"):
                    child = self.__class__(children=child, parent=self)
                    self.add_child_node(child)
                else:
                    self.add_child(child)

    def parent(self):
        return self.parent_node

    def children(self):
        raise NotImplementedError()

    def root_node(self):
        a = self
        while a.parent() is not None:
            a = a.parent()
        return a

    def height(self):
        h = 0
        a = self
        while a.parent() is not None:
            a = self.parent()
            h += 1
        return h

    def ancestors(self):
        a = self
        ancestors = [self]
        while a.parent() is not None:
            a = a.parent()
            ancestors.append(a)
        return ancestors

    def descendants(self):
        descendants = [self]
        for c in self.children():
            descendants.extend(c.descendants())
        return descendants

    def values(self):
        return [node.value for node in self.descendants() if node.value is not None]

    def is_leaf_node(self):
        return len(self.children()) == 0

    def leaf_nodes(self):
        if self.is_leaf_node():
            leaf_nodes = [self]
        else:
            leaf_nodes = []
            for c in self.children():
                leaf_nodes.extend(c.leaf_nodes())
        return leaf_nodes

    def filter(self, predicate):
        def find_shallowest_descendants(root, node):
            if node is not root and predicate(node):
                return [node]
            else:
                result = []
                for c in node.children():
                    result.extend(find_shallowest_descendants(root, c))
                return result

        new_root = self.__class__(value=self.value)
        for c in find_shallowest_descendants(self, self):
            new_child = c.filter(predicate)
            new_child.parent_node = new_root
            new_root.add_child_node(new_child)
        return new_root

    def add_child(self, value=None):
        child = self.__class__(value=value, parent=self)
        self.add_child_node(child)
        return child

    def add_child_node(self):
        raise NotImplementedError()

    def delete_child_node(self):
        raise NotImplementedError()

    def __contains__(self, x):
        return any(x == node.value for node in self.descendants())

    def __str__(self):
        def format_node(node):
            first_line = "*" if node.value is None else repr(node.value)
            children = node.children()
            n = len(children)
            if n == 0:
                return [first_line]
            space = " " * len(first_line)
            rows = []
            for i in range(0, n):
                child_rows = format_node(children[i])
                if i == 0:
                    rows.append(first_line + " +-> " + child_rows[0])
                else:
                    rows.append(space + " +-> " + child_rows[0])
                prefix = " |   " if i < n - 1 else "     "
                rows.extend(space + prefix + cr for cr in child_rows[1:])
                if i < n - 1:
                    rows.append(space + " |")
            return rows

        return "\n".join(format_node(self))

    def __repr__(self):
        params = []
        children = self.children()
        if len(children) > 0:
            params.append(repr(children))
        if self.value is not None:
            params.append("value=" + repr(self.value))
        return "{0}({1})".format(self.__class__.__name__, ", ".join(params))

    def to_graph(self):
        from graphs import PredicateGraph

        def edge_relation(x, y):
            return y == x.parent() or x == y.parent()

        return PredicateGraph(self.descendants(), edge_relation)


class ListTree(Tree):
    def __init__(self, children=None, value=None, parent=None):
        self.child_list = []
        Tree.__init__(self, children, value, parent)

    def children(self):
        return self.child_list

    def __getitem__(self, index):
        return self.child_list[index]

    def add_child_node(self, child):
        self.child_list.append(child)

    def remove_child_node(self, child):
        if child not in self.children():
            raise ValueError("child not found")
        self.child_list.remove(child)


def exactly_one(S):
    return len([s for s in S if s]) == 1


def in_order(L):
    return all(L[i] <= L[i + 1] for i in range(0, len(L) - 1))


def set_to_predicate(S):
    return lambda x: x in S


def truth_table_rows(variables):
    if len(variables) == 0:
        return [dict()]
    variables = list(variables)
    P = variables[0]
    R = truth_table_rows(variables[1:])
    add_P = lambda v: [dict([(P, v)] + list(r.items())) for r in R]
    return add_P(True) + add_P(False)


def vars(*var_names):
    return (Variable(name) for name in var_names)


def cast_to_proposition(p):
    if isinstance(p, Proposition):
        return p
    elif isinstance(p, str):
        return Variable(p)
    elif isinstance(p, bool):
        return Constant(p)
    else:
        raise ValueError()


class Proposition:
    symbol = ""
    empty_str = ""

    def __init__(self, *children):
        self.children = [cast_to_proposition(c) for c in children]

    def __str__(self):
        if len(self.children) == 0:
            return self.empty_str
        return self.symbol.join(c.child_str() for c in self.children)

    def evaluate(self, **assignments):
        raise NotImplementedError()

    def variables(self):
        if len(self.children) == 0:
            return frozenset()
        else:
            return frozenset.union(*[c.variables() for c in self.children])

    def __repr__(self):
        return "Proposition( {0} )".format(self)

    def child_str(self):
        return ("{0}" if isinstance(self, (Constant, Variable, Not)) else "({0})").format(self)

    def print_truth_table(self):
        vars = sorted(self.variables())
        rows = truth_table_rows(vars)

        formula_header = str(self)
        formula_len = max(5, len(formula_header))
        header = "{0}  #  {1: ^{2}}".format(
            "  ".join("{0: ^5}".format(v) for v in vars), formula_header, formula_len
        )
        print(header)
        print("#" * len(header))

        for r in rows:
            var_cols = "  ".join(
                "{0: ^{1}}".format(str(r[v]), max(5, len(v))) for v in vars
            )
            result_col = "{0: ^{1}}".format(str(self.evaluate(**r)), formula_len)
            print("{0}  #  {1}".format(var_cols, result_col))
        print()

    def to_tree(self):
        result = ListTree(value=str(self))
        for c in self.children:
            result.add_child_node(c.to_tree())
        return result

    def __and__(self, other):
        v = self.children if isinstance(self, And) else [self]
        w = other.children if isinstance(other, And) else [other]
        return And(*(v + w))

    def __rand__(self, other):
        return cast_to_proposition(other) & self

    def __or__(self, other):
        v = self.children if isinstance(self, Or) else [self]
        w = other.children if isinstance(other, Or) else [other]
        return Or(*(v + w))

    def __ror__(self, other):
        return cast_to_proposition(other) | self

    def __invert__(self):
        return Not(self)

    def __rshift__(self, other):
        return Implies(self, other)

    def __rrshift__(self, other):
        return Implies(other, self)

    def __lshift__(self, other):
        return ImpliedBy(self, other)

    def __rlshift__(self, other):
        return ImpliedBy(other, self)

    def disjunction(self, other):
        return self | other

    def conjunction(self, other):
        return self & other

    def negation(self):
        return ~self

    def implies(self, other):
        return self >> other

    def impliedby(self, other):
        return self << other

    def iff(self, other):
        return Iff(self, other)

    def is_tautology(self):
        return all(self.evaluate(**r) for r in truth_table_rows(self.variables()))

    def is_contradiction(self):
        return all(not self.evaluate(**r) for r in truth_table_rows(self.variables()))

    def is_contingency(self):
        return not self.is_tautology() and not self.is_contradiction()

    def __eq__(self, other):
        return self.is_equivalent(other)

    def is_equivalent(self, other):
        other = cast_to_proposition(other)
        return all(
            self.evaluate(**r) == other.evaluate(**r)
            for r in truth_table_rows(self.variables() | other.variables())
        )

    def is_identical(self, other):
        return (
            self.__class__ == other.__class__
            and len(self.children) == len(other.children)
            and all(c.is_identical(d) for (c, d) in zip(self.children, other.children))
        )

    def substitute(self, e1, e2):
        if self.is_identical(e1):
            return e2
        else:
            return self.__class__(*[c.substitute(e1, e2) for c in self.children])


class Constant(Proposition):
    def __init__(self, value):
        self.children = []
        self.value = bool(value)

    def substitute(self, e1, e2):
        return Constant(self.value)

    def __str__(self):
        return str(self.value)

    def evaluate(self, **assignments):
        return self.value

    def is_identical(self, other):
        return isinstance(other, Constant) and self.value == other.value


class Variable(Proposition):
    def __init__(self, name):
        self.children = []
        self.name = name

    def substitute(self, e1, e2):
        if self.is_identical(e1):
            return e2
        else:
            return Variable(self.name)

    def variables(self):
        return frozenset({self.name})

    def __str__(self):
        return self.name

    def evaluate(self, **assignments):
        return assignments[self.name]

    def is_identical(self, other):
        return isinstance(other, Variable) and self.name == other.name


class Not(Proposition):
    def __init__(self, child):
        Proposition.__init__(self, child)

    def __str__(self):
        return "¬{0}".format(self.children[0].child_str())

    def evaluate(self, **assignments):
        return not self.children[0].evaluate(**assignments)


class And(Proposition):
    symbol = " ^ "
    empty_str = "True"

    def evaluate(self, **assignments):
        return all(child.evaluate(**assignments) for child in self.children)


class Or(Proposition):
    symbol = " v "
    empty_str = "False"

    def evaluate(self, **assignments):
        return any(child.evaluate(**assignments) for child in self.children)


class Implies(Proposition):
    symbol = " => "

    def __init__(self, child1, child2):
        Proposition.__init__(self, child1, child2)

    def evaluate(self, **assignments):
        if self.children[0].evaluate(**assignments):
            return self.children[1].evaluate(**assignments)
        else:
            return True


class ImpliedBy(Proposition):
    symbol = " <= "

    def __init__(self, child1, child2):
        Proposition.__init__(self, child1, child2)

    def evaluate(self, **assignments):
        if self.children[1].evaluate(**assignments):
            return self.children[0].evaluate(**assignments)
        else:
            return True


class Iff(Proposition):
    symbol = " <=> "

    def __init__(self, child1, child2):
        Proposition.__init__(self, child1, child2)

    def evaluate(self, **assignments):
        return self.children[0].evaluate(**assignments) == self.children[1].evaluate(**assignments)


class ArgumentForm:
    def __init__(self, *premises, conclusion):
        self.premises = [cast_to_proposition(c) for c in premises]
        self.conclusion = cast_to_proposition(conclusion)

    def variables(self):
        return frozenset.union(self.conclusion.variables(), *[c.variables() for c in self.premises])

    def __repr__(self):
        return "ArgumentForm( {0} )".format(self)

    def __str__(self):
        return (
            ((", ".join(str(c) for c in self.premises) + ", ") if self.premises else "")
            + "conclusion = "
            + str(self.conclusion)
        )

    def print_truth_table(self):
        vars = sorted(self.variables())
        rows = truth_table_rows(vars)

        var_strings = ["{0: ^5}".format(v) for v in vars]
        premise_strings = ["{0: ^6}".format(str(c)) for c in self.premises]
        conclusion_string = "{0: ^10}".format(str(self.conclusion))
        vars_header = "  ".join(var_strings)
        premises_header = "{0: ^8}".format("   ".join(premise_strings))
        print(
            "{0}  #  {1: ^{2}}  #  {3: ^{4}}".format(
                " " * len(vars_header),
                "premises",
                len(premises_header),
                "conclusion",
                len(conclusion_string),
            )
        )
        header = "{0}  #  {1: ^8}  #  {2}".format(vars_header, premises_header, conclusion_string)
        print(header)
        print("#" * len(header))

        for r in rows:
            premise_values = [c.evaluate(**r) for c in self.premises]
            conclusion_value = self.conclusion.evaluate(**r)
            star = "*" if all(v for v in premise_values) else ""
            var_cols = "  ".join(
                "{0: ^{1}}".format(str(r[v]), len(k)) for (k, v) in zip(var_strings, vars)
            )
            premise_cols = "   ".join(
                "{0: ^{1}}".format(str(v) + star, len(k))
                for (k, v) in zip(premise_strings, premise_values)
            )
            conclusion_col = "{0: ^{1}}".format(str(conclusion_value) + star, len(conclusion_string))
            print("{0}  #  {1: ^8}  #  {2}".format(var_cols, premise_cols, conclusion_col))
        print()

    def is_valid_truth_table(self):  # adapted by acvm
        vars = (
            frozenset.union(*[c.variables() for c in self.premises])
            if self.premises
            else frozenset()
        ) | self.conclusion.variables()
        return all(
            self.conclusion.evaluate(**r)
            for r in truth_table_rows(vars)
            if all(c.evaluate(**r) for c in self.premises)
        )

    def substitute(self, e1, e2):
        return ArgumentForm(
            *[c.substitute(e1, e2) for c in self.premises],
            conclusion=self.conclusion.substitute(e1, e2),
        )


def get_nodes(formula):
    nodes = [formula]
    if len(formula.children) > 0:
        nodes.extend(get_nodes(formula.children[0]))
    if len(formula.children) > 1:
        nodes.extend(get_nodes(formula.children[1]))
    return nodes


# --- Parser de fórmulas e sequentes ---

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


# --- Tableaux semânticos ---

# Proposition.__eq__ usa tabela-verdade; aqui a comparação precisa ser sintática.
def chave_formula(formula: Proposition) -> tuple:
    if isinstance(formula, Variable):
        return ("V", formula.name)
    if isinstance(formula, Constant):
        return ("C", formula.value)
    return (type(formula).__name__, tuple(chave_formula(c) for c in formula.children))


def tamanho_formula(formula: Proposition) -> int:
    if not formula.children:
        return 1
    return 1 + sum(tamanho_formula(c) for c in formula.children)


class FormulaMarcada:
    __slots__ = ("chave", "formula", "marca", "tamanho")

    def __init__(self, marca: bool, formula: Proposition):
        self.marca = marca
        self.formula = formula
        self.chave = chave_formula(formula)
        self.tamanho = tamanho_formula(formula)

    @property
    def id(self) -> tuple[bool, tuple]:
        return (self.marca, self.chave)

    @property
    def id_conjugado(self) -> tuple[bool, tuple]:
        return (not self.marca, self.chave)

    def __str__(self) -> str:
        return f"{'T' if self.marca else 'F'} {self.formula}"

    def __repr__(self) -> str:
        return f"FormulaMarcada({str(self)!r})"


@dataclass
class ResultadoTableau:
    valido: bool
    contra_exemplo: dict[str, bool] | None
    regras_aplicadas: list[tuple[str, str]]

    def __str__(self) -> str:
        linhas = [f"Resultado: {'Válido' if self.valido else 'Inválido'}"]
        if not self.valido:
            linhas.append(f"Contra-exemplo: {self.contra_exemplo}")
        linhas.append(f"Regras aplicadas: {self.regras_aplicadas}")
        return "\n".join(linhas)


def expandir_formula(
    fm: FormulaMarcada,
) -> tuple[str, bool, tuple[FormulaMarcada, ...]] | None:
    f = fm.formula
    if isinstance(f, (Variable, Constant)):
        return None

    if isinstance(f, Not):
        filho = f.children[0]
        if fm.marca:
            return ("α¬", False, (FormulaMarcada(False, filho),))
        # β¬ não bifurca o ramo.
        return ("β¬", False, (FormulaMarcada(True, filho),))

    if isinstance(f, And):
        filhos = f.children
        if not filhos:
            regra = "α∧" if fm.marca else "β∧"
            return (regra, False, (FormulaMarcada(fm.marca, Constant(True)),))
        if len(filhos) == 1:
            regra = "α∧" if fm.marca else "β∧"
            return (regra, False, (FormulaMarcada(fm.marca, filhos[0]),))
        esq = filhos[0]
        dir_ = filhos[1] if len(filhos) == 2 else And(*filhos[1:])
        if fm.marca:
            return ("α∧", False, (FormulaMarcada(True, esq), FormulaMarcada(True, dir_)))
        return ("β∧", True, (FormulaMarcada(False, esq), FormulaMarcada(False, dir_)))

    if isinstance(f, Or):
        filhos = f.children
        if not filhos:
            regra = "β∨" if fm.marca else "α∨"
            return (regra, False, (FormulaMarcada(fm.marca, Constant(False)),))
        if len(filhos) == 1:
            regra = "β∨" if fm.marca else "α∨"
            return (regra, False, (FormulaMarcada(fm.marca, filhos[0]),))
        esq = filhos[0]
        dir_ = filhos[1] if len(filhos) == 2 else Or(*filhos[1:])
        if not fm.marca:
            return ("α∨", False, (FormulaMarcada(False, esq), FormulaMarcada(False, dir_)))
        return ("β∨", True, (FormulaMarcada(True, esq), FormulaMarcada(True, dir_)))

    if isinstance(f, Implies):
        c, b = f.children
        if not fm.marca:
            return ("α→", False, (FormulaMarcada(True, c), FormulaMarcada(False, b)))
        return ("β→", True, (FormulaMarcada(False, c), FormulaMarcada(True, b)))

    if isinstance(f, ImpliedBy):
        c, b = f.children
        if not fm.marca:
            return ("α→", False, (FormulaMarcada(True, b), FormulaMarcada(False, c)))
        return ("β→", True, (FormulaMarcada(False, b), FormulaMarcada(True, c)))

    if isinstance(f, Iff):
        c, b = f.children
        ida, volta = Implies(c, b), Implies(b, c)
        if fm.marca:
            return ("α↔", False, (FormulaMarcada(True, ida), FormulaMarcada(True, volta)))
        return ("β↔", True, (FormulaMarcada(False, ida), FormulaMarcada(False, volta)))

    raise TypeError(f"Fórmula não suportada: {type(f).__name__}")


def _fecha_ramo(fm: FormulaMarcada, presentes: set[tuple[bool, tuple]]) -> bool:
    if isinstance(fm.formula, Constant) and fm.marca != fm.formula.value:
        return True
    return fm.id_conjugado in presentes


def _escolher_beta(
    ramo: list[FormulaMarcada],
    betas: list[int],
    presentes: set[tuple[bool, tuple]],
) -> int:
    melhor_pos = 0
    melhor_score = None
    for pos, idx in enumerate(betas):
        fm = ramo[idx]
        exp = expandir_formula(fm)
        assert exp is not None
        b1, b2 = exp[2]
        fechamentos = int(_fecha_ramo(b1, presentes)) + int(_fecha_ramo(b2, presentes))
        score = (-fechamentos, fm.tamanho, pos)
        if melhor_score is None or score < melhor_score:
            melhor_score = score
            melhor_pos = pos
    return melhor_pos


def provar_sequente(sequente: ArgumentForm) -> ResultadoTableau:
    ramo: list[FormulaMarcada] = []
    presentes: set[tuple[bool, tuple]] = set()
    lineares: deque[int] = deque()
    betas: list[int] = []
    pilha_ramos: list[tuple[FormulaMarcada, int, list[int]]] = []
    regras_aplicadas: list[tuple[str, str]] = []

    def adicionar(fm: FormulaMarcada) -> bool:
        if _fecha_ramo(fm, presentes):
            return True
        if fm.id in presentes:
            return False
        idx = len(ramo)
        ramo.append(fm)
        presentes.add(fm.id)
        exp = expandir_formula(fm)
        if exp is not None:
            if exp[1]:
                betas.append(idx)
            else:
                lineares.append(idx)
        return False

    def retroceder() -> bool:
        while pilha_ramos:
            proxima, tam_salvo, betas_salvos = pilha_ramos.pop()
            for fm in ramo[tam_salvo:]:
                presentes.remove(fm.id)
            del ramo[tam_salvo:]
            lineares.clear()
            betas[:] = betas_salvos
            if not adicionar(proxima):
                return True
        return False

    iniciais = [FormulaMarcada(True, p) for p in sequente.premises]
    iniciais.append(FormulaMarcada(False, sequente.conclusion))
    for fm in iniciais:
        if adicionar(fm):
            return ResultadoTableau(True, None, regras_aplicadas)

    while True:
        fechou = False
        while lineares:
            fm = ramo[lineares.popleft()]
            exp = expandir_formula(fm)
            assert exp is not None
            regra, _, geradas = exp
            regras_aplicadas.append((regra, str(fm)))
            for nova in geradas:
                if adicionar(nova):
                    fechou = True
                    break
            if fechou:
                break

        if fechou:
            if not retroceder():
                return ResultadoTableau(True, None, regras_aplicadas)
            continue

        if not betas:
            contra_exemplo = {v: False for v in sorted(sequente.variables())}
            for fm in ramo:
                if isinstance(fm.formula, Variable):
                    contra_exemplo[fm.formula.name] = fm.marca
            return ResultadoTableau(False, contra_exemplo, regras_aplicadas)

        pos = _escolher_beta(ramo, betas, presentes)
        fm = ramo[betas.pop(pos)]
        exp = expandir_formula(fm)
        assert exp is not None
        regra, _, (b1, b2) = exp
        regras_aplicadas.append((regra, str(fm)))

        if _fecha_ramo(b2, presentes) and not _fecha_ramo(b1, presentes):
            b1, b2 = b2, b1

        pilha_ramos.append((b2, len(ramo), betas.copy()))
        if adicionar(b1) and not retroceder():
            return ResultadoTableau(True, None, regras_aplicadas)
