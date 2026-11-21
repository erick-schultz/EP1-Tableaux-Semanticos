from src.code_base_EP1 import (
    ArgumentForm,
    ListTree,
    get_nodes,
    truth_table_rows,
)
from src.code_base_EP1 import (
    vars as logic_vars,
)


def test_formula_tree_and_nodes():
    P, Q, R = logic_vars("P", "Q", "R")
    formula = P >> (Q >> R) | (Q >> (P | R))

    tree = formula.to_tree()
    assert isinstance(tree, ListTree)
    assert formula.variables() == frozenset({"P", "Q", "R"})

    nodes = get_nodes(formula)
    assert len(nodes) > 1
    assert nodes[0].is_identical(formula)


def test_truth_table_rows_count():
    rows = truth_table_rows(["P", "Q", "R"])
    assert len(rows) == 8


def test_valid_arguments_via_truth_table():
    P, Q, R = logic_vars("P", "Q", "R")

    modus_ponens = ArgumentForm(P, P >> Q, conclusion=Q)
    modus_tollens = ArgumentForm(P >> Q, ~Q, conclusion=~P)
    disjunctive_syllogism = ArgumentForm(P | Q, ~P, conclusion=Q)
    hypothetical_syllogism = ArgumentForm(P >> Q, Q >> R, conclusion=P >> R)

    assert modus_ponens.is_valid_truth_table() is True
    assert modus_tollens.is_valid_truth_table() is True
    assert disjunctive_syllogism.is_valid_truth_table() is True
    assert hypothetical_syllogism.is_valid_truth_table() is True


def test_invalid_arguments_via_truth_table():
    P, Q = logic_vars("P", "Q")

    non_sequitur = ArgumentForm(P, conclusion=Q)
    affirming_consequent = ArgumentForm(P >> Q, Q, conclusion=P)
    denying_antecedent = ArgumentForm(P >> Q, ~P, conclusion=~Q)
    fallacy_excluded_middle = ArgumentForm(P | Q, P, conclusion=~Q)

    assert non_sequitur.is_valid_truth_table() is False
    assert affirming_consequent.is_valid_truth_table() is False
    assert denying_antecedent.is_valid_truth_table() is False
    assert fallacy_excluded_middle.is_valid_truth_table() is False
