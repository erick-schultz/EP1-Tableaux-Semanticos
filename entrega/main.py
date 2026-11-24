import sys

from tableaux import parse_sequente, provar_sequente

SEQUENTES_RELATORIO: list[tuple[str, bool]] = [
    ("p, p -> q |- q", True),
    ("p -> q, ~q |- ~p", True),
    ("p | q, ~p |- q", True),
    ("p -> q, q -> r |- p -> r", True),
    ("~q -> ~p |- p -> q", True),
    ("~p -> ~q |- p -> q", False),
    ("p -> q |- p -> (q | r)", True),
    ("p -> q |- p -> (q & r)", False),
    ("~(p & q) |- ~p & ~q", False),
    ("~(p | q) |- ~p | ~q", True),
    ("p | q, ~q |- p", True),
    ("p -> q, q |- p", False),
    ("p, (p & q) -> r |- r", False),
    ("p | q, p -> r, q -> (r | s) |- r", False),
    ("p | q, p -> r, q -> r |- r", True),
    ("p |- q", False),
    ("p -> q, ~p |- ~q", False),
    ("p | q, p |- ~q", False),
]


def _rotulo_validade(valido: bool) -> str:
    return "Válido" if valido else "Inválido"


def executar_testes() -> bool:
    print("=== Execução dos 18 sequentes do relatório ===\n")
    aprovados = 0
    total = len(SEQUENTES_RELATORIO)

    for indice, (texto, esperado) in enumerate(SEQUENTES_RELATORIO, start=1):
        sequente = parse_sequente(texto)
        resultado = provar_sequente(sequente)
        tabela_verdade = sequente.is_valid_truth_table()

        if resultado.valido:
            contra_exemplo_ok = resultado.contra_exemplo is None
        else:
            contra_exemplo_ok = (
                resultado.contra_exemplo is not None
                and all(p.evaluate(**resultado.contra_exemplo) for p in sequente.premises)
                and not sequente.conclusion.evaluate(**resultado.contra_exemplo)
            )

        ok = (
            resultado.valido is esperado
            and resultado.valido is tabela_verdade
            and contra_exemplo_ok
        )
        if ok:
            aprovados += 1

        status = "OK" if ok else "FALHA"
        print(f"[{indice:02d}] {texto}")
        print(
            f"     Status: {status} "
            f"(esperado: {_rotulo_validade(esperado)} | "
            f"tabela-verdade: {_rotulo_validade(tabela_verdade)})"
        )
        print(f"     Resultado: {_rotulo_validade(resultado.valido)}")
        if not resultado.valido:
            print(f"     Contra-exemplo: {resultado.contra_exemplo}")
        print(f"     Regras aplicadas: {resultado.regras_aplicadas}\n")

    print(
        f"Resumo: {aprovados}/{total} sequentes validados "
        "(esperado e is_valid_truth_table() consistentes)."
    )
    return aprovados == total


def avaliar_sequente(texto: str) -> None:
    sequente = parse_sequente(texto)
    resultado = provar_sequente(sequente)
    print(resultado)


def modo_interativo() -> None:
    print("\n=== Modo interativo ===")
    print("Digite um sequente (ex.: p, p -> q |- q) ou 'sair' para encerrar.")
    print("Operadores: ~ (¬), & (^, ∧), | (∨), -> (=>, >>, →), <-> (<=>, ↔), |- (⊢)\n")
    while True:
        try:
            entrada = input("Sequente> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not entrada or entrada.lower() in {"sair", "exit", "quit"}:
            break
        try:
            avaliar_sequente(entrada)
        except ValueError as exc:
            print(f"Erro: {exc}")
        print()


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if not args:
        ok = executar_testes()
        modo_interativo()
        return 0 if ok else 1

    if args in (["-h"], ["--help"]):
        print("Uso:")
        print("  python3 main.py                Executa os 18 testes e abre o modo interativo")
        print("  python3 main.py --testes       Executa apenas os 18 testes do relatório")
        print('  python3 main.py "<sequente>"   Avalia um sequente diretamente pela CLI')
        return 0

    if args == ["--testes"]:
        return 0 if executar_testes() else 1

    texto = " ".join(args)
    try:
        avaliar_sequente(texto)
    except ValueError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
