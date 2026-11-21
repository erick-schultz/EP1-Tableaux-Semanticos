import random

import pytest

from src.code_base_EP1 import (
    And,
    ArgumentForm,
    Constant,
    Iff,
    ImpliedBy,
    Implies,
    Not,
    Or,
    Variable,
)
from src.code_base_EP1 import (
    vars as logic_vars,
)
from src.parser import parse_formula, parse_sequente
from src.tableaux import provar_sequente


def _verificar_consistencia(seq: ArgumentForm):
    res = provar_sequente(seq)
    esperado = seq.is_valid_truth_table()
    assert res.valido is esperado

    if res.valido:
        assert res.contra_exemplo is None
    else:
        assert res.contra_exemplo is not None
        assert set(res.contra_exemplo.keys()) == set(seq.variables())
        for premissa in seq.premises:
            assert premissa.evaluate(**res.contra_exemplo) is True
        assert seq.conclusion.evaluate(**res.contra_exemplo) is False

    for item in res.regras_aplicadas:
        assert isinstance(item, tuple) and len(item) == 2
        assert isinstance(item[0], str) and isinstance(item[1], str)

    return res


@pytest.mark.parametrize(
    ("texto", "valido"),
    [
        ("p, p >> q |- q", True),
        ("p >> q, ~q |- ~p", True),
        ("p | q, ~p |- q", True),
        ("p >> q, q >> r |- p >> r", True),
        ("~q >> ~p |- p >> q", True),
        ("~p >> ~q |- p >> q", False),
        ("p >> q |- p >> (q | r)", True),
        ("p >> q |- p >> (q & r)", False),
        ("~(p & q) |- ~p & ~q", False),
        ("~(p | q) |- ~p | ~q", True),
        ("p | q, ~q |- p", True),
        ("p >> q, q |- p", False),
        ("p, (p & q) >> r |- r", False),
        ("p | q, p >> r, q >> (r | s) |- r", False),
        ("p | q, p >> r, q >> r |- r", True),
        ("p |- q", False),
        ("p >> q, ~p |- ~q", False),
        ("p | q, p |- ~q", False),
    ],
)
def test_exercicios_livro_e_demo(texto, valido):
    seq = parse_sequente(texto)
    res = _verificar_consistencia(seq)
    assert res.valido is valido


@pytest.mark.parametrize(
    "teorema",
    [
        "|- p | ~p",
        "|- p >> p",
        "|- (p >> q) >> ((r >> p) >> (r >> q))",
        "|- (p >> (q >> r)) >> (q >> (p >> r))",
        "|- (p >> (p >> q)) >> (p >> q)",
        "|- (p >> (q >> r)) >> ((p >> q) >> (p >> r))",
        "|- p >> (q >> p)",
        "|- ((p >> q) >> p) >> p",
    ],
)
def test_axiomas_implicativos_e_tautologias(teorema):
    seq = parse_sequente(teorema)
    res = _verificar_consistencia(seq)
    assert res.valido is True
    assert len(res.regras_aplicadas) > 0


@pytest.mark.parametrize(
    "equivalencia",
    [
        "|- ~~p <=> p",
        "|- (p >> q) <=> (~p | q)",
        "|- ~(p | q) <=> (~p & ~q)",
        "|- ~(p & q) <=> (~p | ~q)",
        "|- (p & (q | r)) <=> ((p & q) | (p & r))",
        "|- (p | (q & r)) <=> ((p | q) & (p | r))",
    ],
)
def test_equivalencias_bicondicional(equivalencia):
    seq = parse_sequente(equivalencia)
    res = _verificar_consistencia(seq)
    assert res.valido is True


def test_constantes_e_casos_borda():
    P, Q, R = logic_vars("P", "Q", "R")

    casos = [
        ArgumentForm(P, conclusion=P),
        ArgumentForm(P, ~P, conclusion=Q),
        ArgumentForm(conclusion=Constant(True)),
        ArgumentForm(conclusion=Constant(False)),
        ArgumentForm(Constant(False), conclusion=P),
        ArgumentForm(Constant(True), conclusion=Constant(False)),
        ArgumentForm(Constant(True), conclusion=P | ~P),
        ArgumentForm(P & Q & R, conclusion=R),
        ArgumentForm(~(P & Q & R), conclusion=~P | ~Q | ~R),
        ArgumentForm(P | Q | R, ~P, ~Q, conclusion=R),
        ArgumentForm(And(), conclusion=Constant(True)),
        ArgumentForm(Or(), conclusion=P),
        ArgumentForm(And(P), conclusion=P),
        ArgumentForm(Or(P), conclusion=P),
        ArgumentForm(ImpliedBy(Q, P), P, conclusion=Q),
        ArgumentForm(Iff(P, Q), P, conclusion=Q),
    ]

    for seq in casos:
        _verificar_consistencia(seq)


def test_familia_tautologias_hn():
    P, Q, R = logic_vars("P", "Q", "R")
    h1 = P | ~P
    h2 = (P & Q) | (~P & Q) | (P & ~Q) | (~P & ~Q)
    h3 = (
        (P & Q & R)
        | (~P & Q & R)
        | (P & ~Q & R)
        | (~P & ~Q & R)
        | (P & Q & ~R)
        | (~P & Q & ~R)
        | (P & ~Q & ~R)
        | (~P & ~Q & ~R)
    )
    for h in (h1, h2, h3):
        res = _verificar_consistencia(ArgumentForm(conclusion=h))
        assert res.valido is True


def test_sequencia_regras_aplicadas_exemplo_basico():
    res = provar_sequente(parse_sequente("|- p | ~p"))
    assert res.valido is True
    assert res.regras_aplicadas == [
        ("α∨", "F p v ¬p"),
        ("β¬", "F ¬p"),
    ]


def test_formula_muitas_variaveis_sem_tabela_verdade():
    atomos = [Variable(f"P{i}") for i in range(25)]
    premissas = [atomos[0]] + [Implies(atomos[i], atomos[i + 1]) for i in range(24)]
    res = provar_sequente(ArgumentForm(*premissas, conclusion=atomos[-1]))
    assert res.valido is True


def test_parser_erros_e_precedencia():
    f = parse_formula("(((a | b) >> q) & (~s))")
    assert f.variables() == frozenset({"a", "b", "q", "s"})

    assert parse_formula("p >> q >> r").is_identical(parse_formula("p >> (q >> r)"))
    assert parse_formula("p & q >> r").is_identical(parse_formula("(p & q) >> r"))
    assert parse_formula("p | q & r").is_identical(parse_formula("p | (q & r)"))
    assert parse_sequente("p, p >> q ⊢ q").is_valid_truth_table() is True

    for invalido in ("", "(p >> q", "p >> )", "p q", "p $ q"):
        with pytest.raises(ValueError):
            parse_formula(invalido)

    with pytest.raises(ValueError):
        parse_sequente("p >> q")


def test_consistencia_aleatoria_com_tabela_verdade():
    rng = random.Random(42)
    vars_pool = [Variable(c) for c in ("P", "Q", "R", "S")]

    def gerar_formula(prof: int):
        if prof == 0 or rng.random() < 0.3:
            if rng.random() < 0.1:
                return Constant(rng.choice([True, False]))
            return rng.choice(vars_pool)
        op = rng.choice(["~", "&", "|", ">>", "<=>"])
        if op == "~":
            return Not(gerar_formula(prof - 1))
        a = gerar_formula(prof - 1)
        b = gerar_formula(prof - 1)
        if op == "&":
            return a & b
        if op == "|":
            return a | b
        if op == ">>":
            return Implies(a, b)
        return Iff(a, b)

    for _ in range(150):
        n_prem = rng.randint(0, 3)
        premissas = [gerar_formula(3) for _ in range(n_prem)]
        conclusao = gerar_formula(3)
        _verificar_consistencia(ArgumentForm(*premissas, conclusion=conclusao))
