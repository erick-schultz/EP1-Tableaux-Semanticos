import sys

from src.code_base_EP1 import ArgumentForm
from src.code_base_EP1 import vars as logic_vars
from src.parser import parse_sequente
from src.tableaux import provar_sequente


def montar_exemplos() -> list[tuple[str, ArgumentForm]]:
    P, Q, R, S = logic_vars("P", "Q", "R", "S")
    return [
        ("Modus Ponens", ArgumentForm(P, P >> Q, conclusion=Q)),
        ("Modus Tollens", ArgumentForm(P >> Q, ~Q, conclusion=~P)),
        ("Silogismo Disjuntivo", ArgumentForm(P | Q, ~P, conclusion=Q)),
        ("Silogismo Hipotético", ArgumentForm(P >> Q, Q >> R, conclusion=P >> R)),
        ("Terceiro Excluído", ArgumentForm(conclusion=P | ~P)),
        ("Lei de Peirce", ArgumentForm(conclusion=((P >> Q) >> P) >> P)),
        ("De Morgan", ArgumentForm(~(P | Q), conclusion=~P & ~Q)),
        ("Eliminação de Disjunção", ArgumentForm(P | Q, P >> R, Q >> R, conclusion=R)),
        ("Non Sequitur", ArgumentForm(P, conclusion=Q)),
        ("Afirmação do Consequente", ArgumentForm(P >> Q, Q, conclusion=P)),
        ("Negação do Antecedente", ArgumentForm(P >> Q, ~P, conclusion=~Q)),
        ("Falácia do Meio Excluído", ArgumentForm(P | Q, P, conclusion=~Q)),
        ("Contra-exemplo do livro 1", ArgumentForm(P, (P & Q) >> R, conclusion=R)),
        (
            "Contra-exemplo do livro 2",
            ArgumentForm(P | Q, P >> R, Q >> (R | S), conclusion=R),
        ),
    ]


def executar_bateria() -> None:
    for nome, seq in montar_exemplos():
        res = provar_sequente(seq)
        tv = seq.is_valid_truth_table()
        assert res.valido == tv, f"Divergência em {nome}: tableau={res.valido}, tv={tv}"
        premissas = ", ".join(str(p) for p in seq.premises)
        seq_str = f"{premissas} |- {seq.conclusion}" if premissas else f"|- {seq.conclusion}"
        print(f"=== {nome} ===")
        print(f"Sequente: {seq_str}")
        print(res)
        print()


def modo_interativo() -> None:
    print("Digite um sequente no formato 'A1, A2 |- B' (ou 'sair'):")
    while True:
        try:
            linha = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not linha or linha.lower() in ("sair", "exit", "quit"):
            break
        try:
            seq = parse_sequente(linha)
            print(provar_sequente(seq))
        except ValueError as err:
            print(f"Erro: {err}")
        print()


def main() -> None:
    args = sys.argv[1:]
    if not args:
        executar_bateria()
    elif args[0] in ("-i", "--interativo"):
        modo_interativo()
    else:
        seq = parse_sequente(" ".join(args))
        print(provar_sequente(seq))


if __name__ == "__main__":
    main()
