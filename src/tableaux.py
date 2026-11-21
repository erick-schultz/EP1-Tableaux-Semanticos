from collections import deque
from dataclasses import dataclass

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
